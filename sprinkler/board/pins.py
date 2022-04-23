"""Broadcom OSPI Pin Definitions"""

from enum import IntEnum

class SRPins(IntEnum):
    """Enumation of the Pins used by the Board for sending controls

Definition of pins per the OSPi Manual for HW Rev 1.42+
These are the Broadcom numbers as understood by pigpio
"""
    DATA = 27
    CLOCK = 4
    OUTPUT_EN = 17
    LATCH = 22
    RAIN = 14
    EXTERNAL_RELAY = 15
