"""Board Definition"""

from abc import ABC, abstractmethod
from typing import List

from sprinkler.station.station import Station

class Board(ABC):
    """Represents a controller board

While this code is specifically designed to run the OpenSprinkler Pi board.
However, we split the implementation into multiple classes with a common
abstract base class that provides the interface between the Controller and the
given Board. This allows for managing a single board physically connected to
the device connected, as well as for a Mock Board that only exists in software
for testing purposes.
"""
    def __init__(self):
        """Setup the board"""
        self.stations: List[Station] = []
    def get_bit_pattern(self) -> List[int]:
        """Get the bit pattern"""
        pattern = []
        for station in self.stations:
            state = 0
            if station.on:
                state = 1
            pattern.append(state)
        return pattern
    @abstractmethod
    def send_pattern(self):
        """Applies the current pattern to the underlying hardware"""
    def stop_all_stations(self):
        """Stops all stations"""
        for station in self.stations:
            station.on = False
        self.send_pattern()
