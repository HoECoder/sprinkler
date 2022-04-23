"""Program Manager Class"""
from typing import List, Union
from abc import ABC, abstractmethod

from sprinkler.program.abc.program import SprinklerProgram

class ProgramManager(ABC): # pylint: disable=too-few-public-methods
    """Manages programs

The idea behind managers is that they provide the interface between the
controller and the outside world managing the storage, scheduling and retrieval
of a program.

All the controller then has to care about is servicing the current program and
looking for the next program. In this way, a ProgramManager handles the storage
aspects, but also if a user somewhere requests that a program be run ad-hoc.
This simplified feature can also be used to handle when a user somewhere
requests that a single station be run on demand.

All that a Controller cares about is that it can call get_program with the
current time in UTC and get the next program it should run (if any).

Currently, the code calling get_program expects a single Program in return, so
it is expected that other portions of the implementation prevent multiple
programs from running at once. This is partially a limitation of the HW too, as
it can only realisitcally have a single valve on for any serious length of time
as there's a physical limit on the current it can have.
"""
    @abstractmethod
    def get_program(self, now: float) -> Union[SprinklerProgram, None]:
        """Gets the program for the given now, in UTC"""
    @abstractmethod
    def update_programs(self,
                        additions: List[SprinklerProgram],
                        deletes: List[SprinklerProgram]):
        """Updates the internal list of programs"""
