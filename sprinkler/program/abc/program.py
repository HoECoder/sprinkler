"""Represents a program"""
import datetime
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Any, List, Mapping
from sprinkler.program.program_types import ProgramType

from sprinkler.station.station import Station

# In this tuple, start is a time in UTC, stop is a time in UTC
ProgramTime = namedtuple("ProgramTime", ["start", "end", "duration"])

def program_time_start_key(idx: ProgramTime) -> int:
    """Return the start key"""
    return idx.start
def program_time_end_key(idx: ProgramTime) -> int:
    """Return the end key"""
    return idx.end

class SprinklerProgram(ABC):
    """Representation of a Program

Programs live in two worlds: 1) realtime/UTC-time, 2) relative

For the controller to start/stop programs, it asks for programs in realtime/UTC-
time. That is, it only thinks of things in terms of a UTC clock. This allows for
seamless transition across DST boundaries; the '23' hour day doesn't result in a
possibly shortened program, the '25' hour day does result in an overly long
program. This is per the convetion that UTC is monotonically** moving forward
regardless of what the local human/political clock does.

For the scheduling aspects, the program lives in a relative time. That is in
terms of start the program at specific time of day, run each station for their
respective durations, only on the days specified.

This abstract class really only implements the functionality needed by the
controller itself. These are the operations it needs to work. It is up to
subclasses to figure out the starting time in seconds of UTC given the
scheduling nature and to sort the program's stations and durations into a
dictionary with proper ProgramTime namedtuples setup in seconds of UTC. This
separates out the concerns of handling local-time conversions (and DST
headaches) from the concerns of getting a valve to open reliably on time and
pour out some water.

Moving on, the design here is that the Stations themselves are objects that are
shared between a specific Board and the program itself. This way, the program
will flip the state of the station, and the Board can worry itself on how to
apply out the pattern to the actual physical hardware. So, when update_program
is called with a now value in UTC, it will figure out which stations need to
be on and off based on the start and stop time of the station within the
program. It doesn't care if the start/stop times of two stations overlap or if
a station is repeated, or even what order the stations are run in beyond the
implicit start and stop times. As for overlapping start/stop times, this can
actually be advantageous to have two stations overlap as it can lower the water
pressure temporarily and prevent water hammer for at least part of the cycle.

** Yes, this does not account for leap seconds or negative leap seconds.
If a program is short or long by a couple seconds, no one will really care.
People will care if the program is short an hour or runs an hour too long. If
you do care, probably don't use this program for such a sensitive application.
"""
    def __init__(self, start_time: float):
        """Setup the program"""
        self._stations: Mapping[ProgramTime, Station] = {}
        self._start_time: float = start_time
    @property
    def start_time(self) -> float:
        """Start time of the station in UTC"""
        return self._start_time
    @property
    def stations(self) -> List[Station]:
        """List of stations involved, in run order"""
        return [self._stations[idx]
                for idx in sorted(self._stations.keys(), key = program_time_start_key)]
    @property
    def stations_indexed(self) -> Mapping[ProgramTime, Station]: # pragma: no cover
        """Get the stations indexed to their program times"""
        return self._stations
    @property
    def program_run_time(self) -> int:
        """Length of the program, essentially the sum of durations of the stations"""
        #pylint: disable=consider-iterating-dictionary
        return sum(time_idx.duration for time_idx in self._stations.keys())
    @property
    def program_end_time(self) -> float:
        """Returns the time at which the program ends in UTC"""
        return max(self._stations.keys(), key=program_time_end_key).end

    @property
    @abstractmethod
    def days_of_the_week(self) -> List[int]:
        """The days of the week this program runs on if it is a DOW program"""

    @property
    @abstractmethod
    def program_type(self) -> ProgramType:
        """The type of program this is"""

    @property
    @abstractmethod
    def respects_water_adjustment(self) -> bool:
        """True if this program respects water adjustments"""

    @property
    @abstractmethod
    def respect_rain_delay(self) -> bool:
        """True if this program will respect the rain delay"""

    @classmethod
    @abstractmethod
    def valid_on_day(cls, day: datetime.datetime, conf: Any) -> bool:
        """Returns if this program can run today"""

    @classmethod
    @abstractmethod
    def should_run_now(cls,
                       now: float,
                       conf: Any,
                       jitter: int = 0) -> bool:
        """Returns true if this program should run now"""

    @abstractmethod
    def adjust_watering(self, percentage: float):
        """Adjust the watering by the given percentage"""

    def update_program(self, now: float):
        """Updates the state of the stations based on the given now"""
        for time_idx, station in self._stations.items():
            if time_idx.start <= now < time_idx.end:
                station.on = True
            else:
                station.on = False

    def program_over(self, now: float) -> bool:
        """Returns true if the program is over"""
        return now > self.program_end_time
