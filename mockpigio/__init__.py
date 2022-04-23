"""Mock pipgio library

This library exists to handle cases where the pigpio library is not installed
or we want to fake out the existence of the library for unit testing purposes.
"""
#pylint: disable=invalid-name
# pragma: no cover

# GPIO modes

import time
from collections import namedtuple
from typing import List, Mapping


INPUT  = 0
OUTPUT = 1
ALT0   = 4
ALT1   = 5
ALT2   = 6
ALT3   = 7
ALT4   = 3
ALT5   = 2

OFF   = 0
LOW   = 0
CLEAR = 0

ON   = 1
HIGH = 1
SET  = 1

PUD_OFF  = 0
PUD_DOWN = 1
PUD_UP   = 2

WriteLogEntry = namedtuple("WriteLogEntry", ["pin", "value", "time"])

class pi: # pragma: no cover
    """Mock pipgio pi class for testing purposes"""
    def __init__(self,
                 host: str = "localhost",
                 port: int = 8888,
                 show_errors: bool = True):
        """Setup the mock"""
        self.host = host
        self.port = port
        self.show_errors = show_errors
        self.pin_modes: Mapping[int, int] = {}
        self.pin_up_downs: Mapping[int, int] = {}
        self.write_log: List[WriteLogEntry] = []
        self.connected = True
    def set_mode(self, pin: int, mode: int) -> int:
        """Sets the mode"""
        self.pin_modes[pin] = mode
        return mode
    def get_mode(self, pin: int) -> int:
        """Gets the mode for the pin"""
        return self.pin_modes[pin]
    def set_pull_up_down(self, pin: int, mode: int) -> int:
        """Sets or clears the internal GPIO pull-up/down resistor."""
        self.pin_up_downs[pin] = mode
        return mode
    def write(self, pin: int, value: int) -> int:
        """Writes a value to the pin"""
        entry = WriteLogEntry(pin, value, time.time())
        self.write_log.append(entry)
        return 0
    def read(self, pin: int) -> int:
        """Reads a value from a pin"""
        return 0
