import perilib
import struct

class SilabsBGAPIProtocol(perilib.protocol.stream.StreamProtocol):

    header_args = [
        { "name": "type", "type": "uint8" },
        { "name": "length", "type": "uint8" },
        { "name": "group", "type": "uint8" },
        { "name": "method", "type": "uint8" }
    ]

    response_packet_timeout = 0.5
    incoming_packet_timeout = 1.2

    commands = {
        0: { # technology_type = 0x0 (BLE)
            "name": "ble",
            0: { # group_id = 0x00 (system)
                "name": "system",
                1: { # method_id = 0x01 (system_hello)
                    "name": "hello",
                    "command_args": [],
                    "response_args": [],
                },
            },
        },

        1: { # technology_type = 0x1 (Wifi)
            "name": "wifi",
        },

        4: { # technology_type = 0x4 (Dumo)
            "name": "dumo",
        }
    }

    events = {
        0: { # technology_type = 0x0 (BLE)
            "name": "ble",
        },

        1: { # technology_type = 0x1 (Wifi)
            "name": "wifi",
        },

        2: { # technology_type = 0x4 (Dumo)
            "name": "dumo",
        }
    }

    @classmethod
    def test_packet_complete(cls, buffer, is_tx=False):
        # make sure we have at least the header
        if len(buffer) > 3:
            # check 11-bit "length" field in 4-byte header
            (payload_length,) = struct.unpack(">H", buffer[0:2])
            payload_length = payload_length & 0x3FF
            if len(buffer) == payload_length + 4:
                return perilib.protocol.stream.StreamParserGenerator.STATUS_COMPLETE

        # not finished if we made it here
        return perilib.protocol.stream.StreamParserGenerator.STATUS_IN_PROGRESS

    @classmethod
    def get_packet_from_buffer(cls, buffer, parser_generator=None, is_tx=False):
        (type_data, payload_length, group_id, method_id) = struct.unpack("4B", buffer[0:4])
        message_type = (type_data & 0x80) >> 7
        technology_type = (type_data & 0x78) >> 3
        payload_length += (type_data & 0x07)
        try:
            if message_type == 0:
                # command (TX) or response (RX) packet (or command, but for RX this is only response)
                if is_tx:
                    packet_type = SilabsBGAPIPacket.TYPE_COMMAND
                    token = "cmd"
                else:
                    packet_type = SilabsBGAPIPacket.TYPE_RESPONSE
                    token = "rsp"
                packet_definition = SilabsBGAPIProtocol.commands[technology_type][group_id][method_id]
                packet_name = "%s_%s_%s_%s" % ( \
                    SilabsBGAPIProtocol.commands[technology_type]["name"], \
                    token, \
                    SilabsBGAPIProtocol.commands[technology_type][group_id]["name"], \
                    SilabsBGAPIProtocol.commands[technology_type][group_id][method_id]["name"])
            else:
                # event packet (message_type == 1)
                packet_type = SilabsBGAPIPacket.TYPE_EVENT
                packet_definition = SilabsBGAPIProtocol.events[technology_type][group_id][method_id]
                packet_name = "%s_evt_%s_%s" % ( \
                    SilabsBGAPIProtocol.events[technology_type]["name"], \
                    SilabsBGAPIProtocol.events[technology_type][group_id]["name"], \
                    SilabsBGAPIProtocol.events[technology_type][group_id][method_id]["name"])
        except KeyError as e:
            raise perilib.PerilibProtocolException(
                            "Could not find packet definition for "
                            "technology type %d, group %d, and method %d" \
                            % (technology_type, group_id, method_id))

        packet_definition["header_args"] = SilabsBGAPIProtocol.header_args

        packet_metadata = {
            "message_type": message_type,
            "technology_type": technology_type,
            "group_id": group_id,
            "method_id": method_id,
        }

        if technology_type == 0x0:
            # Bluetooth Low Energy (ble_...)
            return SilabsBGAPIBLEPacket(type=packet_type, name=packet_name, definition=packet_definition, buffer=buffer, metadata=packet_metadata, parser_generator=parser_generator)
        elif technology_type == 0x1:
            # Wi-Fi (wifi_...)
            return SilabsBGAPIWifiPacket(type=packet_type, name=packet_name, definition=packet_definition, buffer=buffer, metadata=packet_metadata, parser_generator=parser_generator)
        elif technology_type == 0x4:
            # Bluetooth dual-mode BR/EDR+LE (dumo_...)
            return SilabsBGAPIDumoPacket(type=packet_type, name=packet_name, definition=packet_definition, buffer=buffer, metadata=packet_metadata, parser_generator=parser_generator)

        # unable to find correct packet
        raise perilib.PerilibProtocolException("Unable to identify packet from buffer [%s]" % ' '.join(["%02X" % b for b in buffer]))

    @classmethod
    def get_packet_from_name_and_args(cls, _packet_name, _parser_generator=None, **kwargs):
        # split "ble_cmd_system_hello" into relevant parts
        parts = _packet_name.split('_', maxsplit=3)
        if len(parts) != 4:
            raise perilib.PerilibProtocolException("Invalid packet name '%s' specified" % _packet_name)

        # find the entry in the protocol definition table
        (technology_type_str, message_type_str, group_name, method_name) = parts
        packet_definition = None
        if message_type_str == "evt":
            search = SilabsBGAPIProtocol.events
            message_type = 1
            packet_type = SilabsBGAPIPacket.TYPE_EVENT
        else:
            search = SilabsBGAPIProtocol.commands
            message_type = 0
            if message_type_str == "rsp":
                packet_type = SilabsBGAPIPacket.TYPE_RESPONSE
            else:
                packet_type = SilabsBGAPIPacket.TYPE_COMMAND
        for technology_type in search:
            if search[technology_type]["name"] == technology_type_str:
                for group_id in search[technology_type]:
                    if type(group_id) == str:
                        continue
                    if search[technology_type][group_id]["name"] == group_name:
                        for method_id in search[technology_type][group_id]:
                            if type(method_id) == str:
                                continue
                            if search[technology_type][group_id][method_id]["name"] == method_name:
                                packet_definition = search[technology_type][group_id][method_id]
                                packet_definition["header_args"] = SilabsBGAPIProtocol.header_args

                                packet_metadata = {
                                    "message_type": message_type,
                                    "technology_type": technology_type,
                                    "group_id": group_id,
                                    "method_id": method_id,
                                }

                                # create technology-specific packet type
                                if technology_type == 0x0:
                                    # Bluetooth Low Energy (ble_...)
                                    return SilabsBGAPIBLEPacket(type=packet_type, name=_packet_name, definition=packet_definition, payload=kwargs, metadata=packet_metadata, parser_generator=_parser_generator)
                                elif technology_type == 0x1:
                                    # Wi-Fi (wifi_...)
                                    return SilabsBGAPIWifiPacket(type=packet_type, name=_packet_name, definition=packet_definition, payload=kwargs, metadata=packet_metadata, parser_generator=_parser_generator)
                                elif technology_type == 0x4:
                                    # Bluetooth dual-mode BR/EDR+LE (dumo_...)
                                    return SilabsBGAPIDumoPacket(type=packet_type, name=_packet_name, definition=packet_definition, payload=kwargs, metadata=packet_metadata, parser_generator=_parser_generator)

        # unable to find correct packet
        raise perilib.PerilibProtocolException("Unable to locate packet definition for '%s'" % _packet_name)

class SilabsBGAPIPacket(perilib.protocol.stream.StreamPacket):

    TYPE_COMMAND = 0
    TYPE_RESPONSE = 1
    TYPE_EVENT = 2

    TYPE_STR = ["command", "response", "event"]
    TYPE_ARG_CONTEXT = ["command_args", "response_args", "event_args"]

    def prepare_buffer_after_building(self):
        # determine header length based on current buffer
        payload_length = len(self.buffer)
        header = struct.pack("4B", \
            (self.metadata["message_type"] << 7) \
                | (self.metadata["technology_type"] << 6) \
                | ((payload_length >> 8) << 3), \
            (payload_length & 0xFF), \
            self.metadata["group_id"],
            self.metadata["method_id"])

        # insert the header at the beginning of the buffer
        self.buffer = header + self.buffer

class SilabsBGAPIBLEPacket(SilabsBGAPIPacket):

    pass

class SilabsBGAPIWifiPacket(SilabsBGAPIPacket):

    pass

class SilabsBGAPIDumoPacket(SilabsBGAPIPacket):

    pass
