import perilib
import struct

class SilabsBGAPIPacket(perilib.StreamPacket):
    """BGAPI packet class.
    
    This class provides the structure for all BGAPI packets. It is identical to
    the parent StreamPacket class except that it provides three types instead of
    just one, and it overrides the buffer preparation method so that the header
    data in the binary buffer is properly filled based on packet metadata when
    creating a packet from a name and argument list."""

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
                | (self.metadata["technology_type"] << 3) \
                | (payload_length >> 8),
            (payload_length & 0xFF),
            self.metadata["group_id"],
            self.metadata["method_id"])

        # insert the header at the beginning of the buffer
        self.buffer = header + self.buffer
