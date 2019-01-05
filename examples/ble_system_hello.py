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
        self.parser_generator = perilib.protocol.stream.core.ParserGenerator(protocol=SilabsBGAPIProtocol())
        self.parser_generator.on_rx_packet = self.on_rx_packet
        self.parser_generator.on_rx_error = self.on_rx_error

        # set up data stream (detects incoming serial data as well as USB removal)
        self.data_stream = perilib.protocol.stream.serial.SerialStream(parser_generator=self.parser_generator)
        self.data_stream.on_open_stream = self.on_open_stream
        self.data_stream.on_close_stream = self.on_close_stream
        self.data_stream.on_tx_packet = self.on_tx_packet

        # set up device monitor (detects USB insertion/removal)
        self.devices_monitor = perilib.monitor.serial.SerialMonitor(data_stream=self.data_stream)
        self.devices_monitor.port_filter = lambda port_info: port_info.vid == 0x2458 and port_info.pid == 0x0001
        self.devices_monitor.on_connect_device = self.on_connect_device
        self.devices_monitor.on_disconnect_device = self.on_disconnect_device
        self.devices_monitor.auto_open = True

        # start monitoring for devices
        self.devices_monitor.start()

    def on_connect_device(self, port_info):
        print("[%.03f] CONNECTED: %s" % (time.time(), port_info))

    def on_disconnect_device(self, port_info):
        print("[%.03f] DISCONNECTED: %s" % (time.time(), port_info))

    def on_open_stream(self, port_info):
        print("[%.03f] OPENED: %s" % (time.time(), port_info))

    def on_close_stream(self, port_info):
        print("[%.03f] CLOSED: %s" % (time.time(), port_info))

    def on_rx_packet(self, packet):
        print("[%.03f] RX: [%s] (%s)" % (time.time(), ' '.join(["%02X" % b for b in packet.buffer]), packet))

    def on_tx_packet(self, packet):
        print("[%.03f] TX: [%s] (%s)" % (time.time(), ' '.join(["%02X" % b for b in packet.buffer]), packet))

    def on_rx_error(self, e, rx_buffer, port_info):
        print("[%.03f] ERROR: %s (raw data: [%s] from %s)" % (time.time(), e, ' '.join(["%02X" % b for b in rx_buffer]), port_info.device if port_info is not None else "unidentified port"))

def main():
    app = App()
    while True:
        if app.data_stream.is_open:
            app.data_stream.send("ble_cmd_system_hello")
        time.sleep(1)

if __name__ == '__main__':
    main()
