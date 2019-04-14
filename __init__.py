"""
This module provides protocol and packet definitions for communicating with
Bluegiga (now Silicon Labs) modules that implement the BGAPI protocol. This set
of devices includes the BLE112, BLED112, BLE113, and BLE121LR Bluetooth Low
Energy modules, WF121 and WGM110 Wifi modules, and BT121 Bluetooth Smart Ready
(dual-mode) module.
"""

# .py files
from .SilabsBGAPIProtocol import *
from .SilabsBGAPIPacket import *
