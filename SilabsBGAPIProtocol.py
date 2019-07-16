import perilib
import struct

from .SilabsBGAPIPacket import *

class SilabsBGAPIProtocol(perilib.StreamProtocol):
    """Silicon Labs BGAPI protocol definition.
    
    This class describes the binary BGAPI protocol used to communicate with
    some of the modules from Bluegiga (now Silicon Labs), specifically BLE112,
    BLE113, BLE121LR, WF121, WGM110, and BT121. This protocol follows a basic
    command-response pattern, and also includes events sent from the module to
    the host at unpredictable times when certain activities occur, such as a
    new connection from a remote device, or incoming data.
    
    Command/response pairs are defined together, each with their own set of
    arguments. Events are defined in a separate dictionary and have only one
    argument set. The protocol is divided by technology type (`ble`, `wifi`, and
    `dumo` to match the definitions in the original BGAPI host implementations),
    then subdivided into group and method names. Packet names are generated
    using these categories along with the packet type, yielding names such as
    `ble_cmd_system_hello` and `wifi_evt_endpoint_data`."""

    header_args = [
        { "name": "type", "type": "uint8" },
        { "name": "length", "type": "uint8" },
        { "name": "group", "type": "uint8" },
        { "name": "method", "type": "uint8" }
    ]

    response_packet_timeout = 0.5
    incoming_packet_timeout = 1.2

    commands = {
        0x0: { # technology_type = 0x0 (BLE)
            "name": "ble",
            0x00: { # group_id = 0x00 (system)
                "name": "system",
                0x01: { # method_id = 0x01 (system_hello)
                    "name": "hello",
                    "response_required": "ble_rsp_system_hello",
                    "command_args": [],
                    "response_args": [],
                },
            },
        },

        0x1: { # technology_type = 0x1 (Wifi)
            "name": "wifi",
        },

        0x4: { # technology_type = 0x4 (Dumo)
            "name": "dumo",
            0x01: { # group_id = 0x01 (system)
                "name": "system",
                0x00: { # method_id = 0x00 (system_hello)
                    "name": "hello",
                    "response_required": "dumo_rsp_system_hello",
                    "command_args": [],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
                0x08: { # method_id = 0x08 (system_set_local_name)
                    "name": "set_local_name",
                    "response_required": "dumo_rsp_system_set_local_name",
                    "command_args": [
                        { "name": "name", "type": "uint8a-l8v" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
            0x02: { # group_id = 0x02 (bt_gap)
                "name": "bt_gap",
                0x03: { # method_id = 0x03 (bt_gap_set_mode)
                    "name": "set_mode",
                    "response_required": "dumo_rsp_bt_gap_set_mode",
                    "command_args": [
                        { "name": "connectable", "type": "uint8" },
                        { "name": "discoverable", "type": "uint8" },
                        { "name": "limited", "type": "uint8" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
            0x04: { # group_id = 0x04 (bt_rfcomm)
                "name": "bt_rfcomm",
                0x01: { # method_id = 0x01 (bt_rfcomm_start_server)
                    "name": "start_server",
                    "response_required": "dumo_rsp_bt_rfcomm_start_server",
                    "command_args": [
                        { "name": "sdp_id", "type": "uint8" },
                        { "name": "streaming_destination", "type": "uint8" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
            0x0B: { # group_id = 0x0B (endpoint)
                "name": "endpoint",
                0x00: { # method_id = 0x00 (endpoint_send)
                    "name": "send",
                    "response_required": "dumo_rsp_endpoint_send",
                    "command_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "data", "type": "uint8a-l8v" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
            0x0C: { # group_id = 0x0C (hardware)
                "name": "hardware",
                0x08: { # method_id = 0x08 (hardware_set_uart_configuration)
                    "name": "set_uart_configuration",
                    "response_required": "dumo_rsp_hardware_set_uart_configuration",
                    "command_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "rate", "type": "uint32" },
                        { "name": "data_bits", "type": "uint8" },
                        { "name": "stop_bits", "type": "uint8" },
                        { "name": "parity", "type": "uint8" },
                        { "name": "flow_ctrl", "type": "uint8" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
            0x0F: { # group_id = 0x0F (sm)
                "name": "sm",
                0x00: { # method_id = 0x00 (sm_set_bondable_mode)
                    "name": "set_bondable_mode",
                    "response_required": "dumo_rsp_sm_set_bondable_mode",
                    "command_args": [
                        { "name": "bondable", "type": "uint8" },
                    ],
                    "response_args": [
                        { "name": "result", "type": "uint16" },
                    ],
                },
            },
        }
    }

    events = {
        0x0: { # technology_type = 0x0 (BLE)
            "name": "ble",
        },

        0x1: { # technology_type = 0x1 (Wifi)
            "name": "wifi",
        },

        0x4: { # technology_type = 0x4 (Dumo)
            "name": "dumo",
            0x01: { # group_id = 0x01 (system)
                "name": "system",
                0x00: { # method_id = 0x00 (system_boot)
                    "name": "boot",
                    "event_args": [
                        { "name": "major", "type": "uint16" },
                        { "name": "minor", "type": "uint16" },
                        { "name": "patch", "type": "uint16" },
                        { "name": "build", "type": "uint16" },
                        { "name": "bootloader", "type": "uint16" },
                        { "name": "hw", "type": "uint16" },
                    ],
                },
                0x01: { # method_id = 0x01 (system_initialized)
                    "name": "initialized",
                    "event_args": [
                        { "name": "address", "type": "macaddr" },
                    ],
                },
                0x02: { # method_id = 0x01 (system_recovery)
                    "name": "recovery",
                    "event_args": [
                        { "name": "id1", "type": "uint32" },
                        { "name": "id2", "type": "uint32" },
                        { "name": "data", "type": "uint8a-l8v" },
                    ],
                },
            },
            0x04: { # group_id = 0x04 (bt_rfcomm)
                "name": "bt_rfcomm",
                0x01: { # method_id = 0x01 (bt_rfcomm_modem_status)
                    "name": "modem_status",
                    "event_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "modem", "type": "uint8" },
                    ],
                },
            },
            0x07: { # group_id = 0x07 (bt_connection)
                "name": "bt_connection",
                0x00: { # method_id = 0x00 (bt_connection_opened)
                    "name": "opened",
                    "event_args": [
                        { "name": "address", "type": "macaddr" },
                        { "name": "master", "type": "uint8" },
                        { "name": "connection", "type": "uint8" },
                        { "name": "bonding", "type": "uint8" },
                    ],
                },
                0x01: { # method_id = 0x01 (bt_connection_closed)
                    "name": "closed",
                    "event_args": [
                        { "name": "reason", "type": "uint16" },
                        { "name": "endpoint", "type": "uint8" },
                    ],
                },
                0x02: { # method_id = 0x02 (bt_connection_parameters)
                    "name": "parameters",
                    "event_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "block_size", "type": "uint32" },
                        { "name": "msc", "type": "uint8" },
                        { "name": "address", "type": "macaddr" },
                        { "name": "direction", "type": "uint8" },
                        { "name": "powermode", "type": "uint8" },
                        { "name": "role", "type": "uint8" },
                        { "name": "encryption", "type": "uint8" },
                        { "name": "input_buffer", "type": "uint32" },
                        { "name": "port", "type": "uint8" },
                    ],
                },
            },
            0x0B: { # group_id = 0x0B (endpoint)
                "name": "endpoint",
                0x00: { # method_id = 0x00 (endpoint_syntax_error)
                    "name": "syntax_error",
                    "event_args": [
                        { "name": "result", "type": "uint16" },
                        { "name": "endpoint", "type": "uint8" },
                    ],
                },
                0x01: { # method_id = 0x01 (endpoint_data)
                    "name": "data",
                    "event_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "data", "type": "uint8a-l8v" },
                    ],
                },
                0x02: { # method_id = 0x02 (endpoint_status)
                    "name": "status",
                    "event_args": [
                        { "name": "endpoint", "type": "uint8" },
                        { "name": "type", "type": "uint32" },
                        { "name": "destination_endpoint", "type": "int8" },
                        { "name": "flags", "type": "uint8" },
                    ],
                },
                0x03: { # method_id = 0x03 (endpoint_closing)
                    "name": "closing",
                    "event_args": [
                        { "name": "reason", "type": "uint16" },
                        { "name": "endpoint", "type": "uint8" },
                    ],
                },
                0x04: { # method_id = 0x04 (endpoint_closed)
                    "name": "closed",
                    "event_args": [
                        { "name": "endpoint", "type": "uint8" },
                    ],
                },
            },
            0x0F: { # group_id = 0x0F (sm)
                "name": "sm",
                0x03: { # method_id = 0x03 (sm_bonded)
                    "name": "bonded",
                    "event_args": [
                        { "name": "connection", "type": "uint8" },
                        { "name": "bonding", "type": "uint8" },
                    ],
                },
            },
        }
    }

    @classmethod
    def test_packet_complete(cls, buffer, is_tx=False):
        # make sure we have at least the header (4 bytes)
        if len(buffer) > 3:
            # check 11-bit "length" field in 4-byte header
            (payload_length,) = struct.unpack(">H", buffer[0:2])
            payload_length = payload_length & 0x3FF
            if len(buffer) == payload_length + 4:
                return perilib.ParseStatus.COMPLETE if buffer != "\x00\x00\x00\x00" else perilib.ParseStatus.IDLE

        # not finished if we made it here
        return perilib.ParseStatus.IN_PROGRESS

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
                            "Could not find packet definition for %s with "
                            "technology type %d, group %d, and method %d" \
                            % (SilabsBGAPIPacket.TYPE_STR[packet_type], technology_type, group_id, method_id))

        packet_definition["header_args"] = SilabsBGAPIProtocol.header_args

        packet_metadata = {
            "message_type": message_type,
            "technology_type": technology_type,
            "group_id": group_id,
            "method_id": method_id,
        }

        # create packet instance
        return SilabsBGAPIPacket(type=packet_type, name=packet_name, definition=packet_definition, buffer=buffer, metadata=packet_metadata, parser_generator=parser_generator)

    @classmethod
    def get_packet_from_name_and_args(cls, _packet_name, _parser_generator=None, **kwargs):
        # split "ble_cmd_system_hello" into relevant parts
        parts = _packet_name.split('_', maxsplit=2)
        if len(parts) != 3:
            raise perilib.PerilibProtocolException("Invalid packet name '%s' specified" % _packet_name)

        # find the entry in the protocol definition table
        (technology_type_str, message_type_str, short_name) = parts
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
                    if search[technology_type][group_id]["name"] == short_name[:len(search[technology_type][group_id]["name"])]:
                        method_name = short_name[len(search[technology_type][group_id]["name"]) + 1:]
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

                                # create packet instance
                                return SilabsBGAPIPacket(type=packet_type, name=_packet_name, definition=packet_definition, payload=kwargs, metadata=packet_metadata, parser_generator=_parser_generator)

        # unable to find correct packet
        raise perilib.PerilibProtocolException("Unable to locate packet definition for '%s'" % _packet_name)
