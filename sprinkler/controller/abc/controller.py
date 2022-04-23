"""Controller that provides what is essentially the mainloop for the controller"""

from abc import ABC, abstractmethod

from sprinkler.board.board import Board
from sprinkler.program.abc import ProgramManager
from sprinkler.program.abc import SprinklerProgram


class SprinklerController(ABC):
    """Sprinkler Controller

This is the core class of the sprinkler package. It is the class that is keeping
time (UTC) and advancing the state of the running programs, asking helpers for
weather updates, and so on.

The controller utilizes UTC time as a close proxy for a monotonically increasing
clock. As such, it doesn't need to care about DST, time zones, etc. It just
needs to know about one second to the next. Admittedly, UTC does have positive
and negative leap seconds in its specification, but a few seconds here or there
are not nearly as critical as running mostly consistently throughout the year.

To facilitate this, it interfaces to a ProgramManager in UTC which returns
programs that are defined in UTC. This removes the controller from the need to
understand local time and just handle the forward progressing clock and ask
programs to advance their progress using the shared state of the station. Then,
once a program is updated, to ask the interface to the hardward to update the
state of the valves.

The core function is on_tick, which is called with the current clock in UTC. It
checks for weather, rain delays, watering adjustments, services existing
programs, checks for programs to run, and asks the HW to update its state.
"""
    def __init__(self):
        """Initialize the controller"""
        self.current_program: SprinklerProgram = None
        self.board: Board = None
        self.manager: ProgramManager = None
        self.last_tick: float = 0
        self.water_adjust_percent: float = 100

    def get_next_program(self, now: float) -> SprinklerProgram:
        """Get the next program"""
        program = self.manager.get_program(now)
        if program.respects_water_adjustment:
            program.adjust_watering(self.water_adjust_percent)
        return program

    @abstractmethod
    def cold_weather_lockout(self) -> bool:
        """Returns true if there is a lockout for cold weather"""
    @abstractmethod
    def rain_delay(self) -> bool:
        """Returns true if we should rain-delay"""
    @abstractmethod
    def update_watering_percentage(self):
        """Updates the watering percentage"""

    def on_tick(self, now: float):
        """Called on every tick of the clock"""
        # Everything respects the cold weather lockout
        if self.cold_weather_lockout():
            if self.current_program:
                self.current_program = None
            self.full_stop()
            return
        # Update the watering adjustment
        self.update_watering_percentage()
        if self.current_program:
            if self.rain_delay() and self.current_program.respect_rain_delay():
                self.full_stop()
                return
            self.current_program.update_program(now)
        else:
            next_program = self.get_next_program(now)
            if next_program:
                self.current_program = next_program
                if self.rain_delay() and self.current_program.respect_rain_delay():
                    self.full_stop()
                    return
                self.current_program.update_program(now)
        self.board.send_pattern()
        if self.current_program:
            if self.current_program.program_over(now):
                self.current_program = None
    def full_stop(self):
        """Force a full stop"""
        self.board.stop_all_stations()
