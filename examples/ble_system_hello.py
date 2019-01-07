import time

try:
    # standard library installation
    import perilib
    print("Detected standard perilib-python installation")
except ImportError as e:
    # local development installation
    import sys
    sys.path.insert(0, "../../../..") # submodule upwards to perilib root
    sys.path.insert(0, ".") # submodule root
    try:
        import perilib
        print("Detected development perilib-python installation run from submodule root")
    except ImportError as e:
        sys.path.insert(0, "../../../../..") # submodule/examples upwards to perilib root
        sys.path.insert(0, "..") # submodule/examples upwards to submodule root
        try:
            import perilib
            print("Detected development perilib-python installation run from submodule/example folder")
        except ImportError as e:
            print("Unable to find perilib-python installation, cannot continue")
            sys.exit(1)

from perilib.protocol.stream.silabs_bgapi import SilabsBGAPIProtocol

class App():

    def __init__(self):
        # set up protocol parser (handles imcoming data and builds outgoing data)
        #self.parser_generator = perilib.protocol.stream.core.ParserGenerator(protocol=SilabsBGAPIProtocol())

        # set up data stream (detects incoming serial data as well as USB removal)
        #self.data_stream = perilib.hal.serial.SerialStream(parser_generator=self.parser_generator)

        # set up manager (detects USB insertion/removal, creates data stream and parser/generator instances as needed)
        self.manager = perilib.hal.serial.SerialManager(
            stream_class=perilib.hal.serial.SerialStream,
            protocol_class=perilib.protocol.stream.silabs_bgapi.SilabsBGAPIProtocol)
        self.manager.port_filter = lambda port_info: port_info.vid == 0x2458 and port_info.pid == 0x0001
        self.manager.on_connect_device = self.on_connect_device         # triggered by manager when running
        self.manager.on_disconnect_device = self.on_disconnect_device   # triggered by manager when running (if stream is closed) or stream (if stream is open)
        self.manager.on_open_stream = self.on_open_stream               # triggered by stream
        self.manager.on_close_stream = self.on_close_stream             # triggered by stream
        self.manager.on_rx_packet = self.on_rx_packet                   # triggered by parser/generator
        self.manager.on_tx_packet = self.on_tx_packet                   # triggered by parser/generator
        self.manager.on_rx_error = self.on_rx_error                     # triggered by parser/generator
        self.manager.auto_open = perilib.hal.serial.SerialManager.AUTO_OPEN_ALL

        # start monitoring for devices
        self.manager.start()

    def on_connect_device(self, metadata):
        print("[%.03f] CONNECTED: %s" % (time.time(), metadata["port_info"]))

    def on_disconnect_device(self, metadata):
        print("[%.03f] DISCONNECTED: %s" % (time.time(), metadata["port_info"]))

    def on_open_stream(self, sender):
        print("[%.03f] OPENED: %s" % (time.time(), sender.port_info))

    def on_close_stream(self, sender):
        print("[%.03f] CLOSED: %s" % (time.time(), sender.port_info))

    def on_rx_packet(self, packet):
        print("[%.03f] RX: [%s] (%s)" % (time.time(), ' '.join(["%02X" % b for b in packet.buffer]), packet))

    def on_tx_packet(self, packet):
        print("[%.03f] TX: [%s] (%s)" % (time.time(), ' '.join(["%02X" % b for b in packet.buffer]), packet))

    def on_rx_error(self, e, rx_buffer, sender):
        print("[%.03f] ERROR: %s (raw data: [%s] from %s)" % (time.time(), e, ' '.join(["%02X" % b for b in rx_buffer]), sender.port_info.device if sender.port_info is not None else "unidentified port"))

def main():
    app = App()
    while True:
        for stream_id in app.manager.streams:
            if app.manager.streams[stream_id].is_open:
                app.manager.streams[stream_id].send("ble_cmd_system_hello")
        time.sleep(1)

if __name__ == '__main__':
    main()
