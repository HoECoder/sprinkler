"""Program that can be configured from a dictionary"""

import time
import datetime
from typing import List, Mapping
from sprinkler.program.abc.program import SprinklerProgram, ProgramTime
from sprinkler.program.program_types import ProgramType
from sprinkler.program.time_utilities import local_dt_for_utc_now
from sprinkler.program.time_utilities import utc_for_local_midnight
from sprinkler.station.station import Station

from sprinkler.program.dictionary.helpers import DictProgram

LOCAL_TZ = "US/Central"

class DictSprinklerProgram(SprinklerProgram):
    """A SprinklerProgram initialized via a dictionary"""
    def __init__(self,
                 start_time: float,
                 all_stations: Mapping[int, Station],
                 program_conf: DictProgram):
        super().__init__(start_time)
        self._prog_conf: DictProgram = program_conf
        self._stations_used: Mapping[int, Station] = {}
        self.update_with_config(all_stations)
    def __repr__(self) -> str: #pragma: no cover
        cls = self.__class__.__name__
        return f"{cls}({self.start_time}, {repr(self._stations_used)}, {repr(self._prog_conf)})"
    def __eq__(self, __o: "DictSprinklerProgram") -> bool:
        if not isinstance(__o, DictSprinklerProgram):
            return super().__eq__(__o) # pragma: no cover
        time_eq = self.start_time == __o.start_time
        used_st = self.stations == __o.stations
        prog_c = self._prog_conf == __o._prog_conf
        return all([time_eq, used_st, prog_c])
    @property
    def days_of_the_week(self) -> List[int]:
        """The days of the week this program runs on if it is a DOW program"""
        return self._prog_conf.days_of_the_week
    @property
    def respect_rain_delay(self) -> bool:
        """True if this program will respect the rain delay"""
        return self._prog_conf.respect_rain
    @property
    def respects_water_adjustment(self) -> bool:
        """True if this program respects water adjustments"""
        return self._prog_conf.respect_water_adjustment
    @property
    def program_type(self):
        """The type of program this is"""
        return self._prog_conf.program_type
    def update_with_config(self,
                           all_stations: Mapping[str, Station]):
        """Update the stations with the config"""
        # Start time is the UTC time we start the program
        running_time = self.start_time
        for entry in self._prog_conf.station_durations:
            start = running_time
            end = start + entry.duration
            running_time = end
            prog_t = ProgramTime(start, end, entry.duration)
            self._stations[prog_t] = all_stations[entry.station_id]
            self._stations_used[entry.station_id] = all_stations[entry.station_id]
    def adjust_watering(self, percentage: float):
        """Adjust the watering by the given percentage"""
        if not self.respects_water_adjustment:
            return
        running_time = self.start_time
        new_stations: Mapping[ProgramTime, Station] = {}
        for entry in self._prog_conf.station_durations:
            start = running_time
            duration = int(round(entry.duration * percentage, 0))
            end = start + duration
            running_time = end
            prog_t = ProgramTime(start, end, duration)
            new_stations[prog_t] = self._stations_used[entry.station_id]
        self._stations = new_stations

    @classmethod
    def valid_on_day(cls: "DictSprinklerProgram",
                     day: datetime.datetime,
                     conf: DictProgram) -> bool:
        """Returns if this program can run today"""
        program_type: ProgramType = conf.program_type
        if program_type == ProgramType.DAYOFTHEWEEK:
            return day.weekday() in conf.days_of_the_week
        remainder = 0
        if program_type == ProgramType.ODDDAYSONLY:
            remainder = 1
        return day.day % 2 == remainder

    @classmethod
    def should_run_now(cls: "DictSprinklerProgram",
                       now: float,
                       conf: DictProgram,
                       jitter: int = 60) -> bool:
        """Returns true if this program should run now"""
        local_dt = local_dt_for_utc_now(now, LOCAL_TZ)
        if not cls.valid_on_day(local_dt, conf):
            return False
        local_midnight_utc = utc_for_local_midnight(now, LOCAL_TZ)
        program_start = local_midnight_utc + conf.start_time_of_day
        return (program_start - jitter) <= now <= (program_start + jitter)

    @classmethod
    def factory(cls: "DictSprinklerProgram",
                program_conf: DictProgram,
                all_stations: Mapping[int, Station],
                now: float = 0) -> "DictSprinklerProgram":
        """Properly create the class"""
        if now <= 0:
            now = time.time()
        utc_midnight = utc_for_local_midnight(now, LOCAL_TZ)
        start_time = utc_midnight + program_conf.start_time_of_day
        return DictSprinklerProgram(start_time, all_stations, program_conf)
