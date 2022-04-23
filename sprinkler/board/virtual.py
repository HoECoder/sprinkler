"""Represents a virtual board for testing"""

from typing import List, TextIO
from sprinkler.board.board import Board
from sprinkler.station.station import Station

class VirtualStreamBoard(Board): # pragma: no cover
    """A virtual board that isn't connected to any device"""
    def __init__(self,
                 stations: List[Station],
                 stream: TextIO):
        super().__init__()
        self.stations = stations
        self.stream = stream
    def send_pattern(self):
        """Sends the pattern out"""
        msg = f"{repr(self.get_bit_pattern)}\n"
        self.stream.write(msg)
