"""A ProgramManager that can produce DictSprinklerProgram"""

from collections import defaultdict
from typing import Any, List, Mapping, Sequence, Union
from sprinkler.program.dictionary.helpers import DictProgram, turn_dict_into_dict_program
from sprinkler.program.dictionary.program import DictSprinklerProgram

from sprinkler.program.program_types import ProgramType
from sprinkler.program.abc import ProgramManager, SprinklerProgram
from sprinkler.program.time_utilities import after_now, local_dt_for_utc_now
from sprinkler.station.station import Station

def turn_dicts_to_programs(programs: List[Mapping[str, Any]]) -> List[DictProgram]:
    """Takes dicts of programs and turns them into DictSprinklerProgram"""
    return [turn_dict_into_dict_program(program) for program in programs] # pragma: no cover

def remove_dup_starts_for_even_odd(programs: List[SprinklerProgram]) -> List[SprinklerProgram]:
    """Remove duplicate programs based on start times.

Only the first program at a given time on an even/odd day will survive.
"""
    even_days: Mapping[float, List[SprinklerProgram]] = defaultdict(list)
    odd_days: Mapping[float, List[SprinklerProgram]] = defaultdict(list)
    even_odds = {
        ProgramType.EVENDAYSONLY: even_days,
        ProgramType.ODDDAYSONLY: odd_days
    }
    for program in programs:
        e_o = even_odds.get(program.program_type, None)
        if e_o is None:
            continue
        e_o[program.start_time].append(program)
    programs_to_remove: List[SprinklerProgram] = []

    for e_o in even_odds.values():
        for dupes in e_o.values():
            if len(dupes) <= 1:
                continue
            programs_to_remove.extend(dupes[1:])

    new_programs = list(programs)
    for program in programs_to_remove:
        new_programs.remove(program)

    return new_programs


class DictProgramManager(ProgramManager):
    """Program manager"""
    def __init__(self,
                 programs: List[Mapping[str, Any]],
                 all_stations: List[Station],
                 local_tz: str,
                 jitter: int = 5):
        """Initialize the manager

programs is a list of Mappings that can be validated by ProgramDictSchema.
all_stations is List of stations from a board that will be coupled to the
programs.
local_tz is the local timezone this Manager, and consequently programs, will be
operating in.
jitter is a parameter used to handle the imprecision of clocks when trying to
select a program.
"""
        self.jitter = jitter
        self.local_tz: str = local_tz
        self.all_stations = all_stations
        self._programs: List[DictProgram] = turn_dicts_to_programs(programs)
    @property
    def programs(self) -> Sequence[DictProgram]:
        """Programs managed by this manager"""
        return tuple(self._programs)
    def search_progs_by_time(self,
                             now: float) -> List[SprinklerProgram]:
        """Returns a program from the even or odd programs"""
        programs: List[DictSprinklerProgram] = []
        for _search in self._programs:
            prog = DictSprinklerProgram.factory(_search,
                                                self.all_stations,
                                                now=now)
            if after_now(now, prog.start_time, self.jitter):
                programs.append(prog)
        return programs
    def get_program(self, now: float) -> Union[SprinklerProgram, None]:
        """Gets the program for the given now, in UTC.

The search is greedy, in that the very first program found is the one that is
returned if there are many programs at the same time.
"""
        local_dt = local_dt_for_utc_now(now, self.local_tz)
        programs = self.search_progs_by_time(now)
        if not programs:
            return None
        for program in programs:
            if program.program_type in [ProgramType.EVENDAYSONLY, ProgramType.ODDDAYSONLY]:
                remainder = 0
                if program.program_type == ProgramType.ODDDAYSONLY:
                    remainder = 1
                if local_dt.day % 2 == remainder:
                    return program
            if program.program_type == ProgramType.DAYOFTHEWEEK:
                if local_dt.weekday() in program.days_of_the_week:
                    return program
        return None
    def update_programs(self,
                        additions: List[Mapping[str, Any]],
                        deletes: List[Mapping[str, Any]]):
        """Updates the internal list of programs"""
        # Remove programs first
        for _del in turn_dicts_to_programs(deletes):
            self._programs.remove(_del)
        # Add programs
        for _add in turn_dicts_to_programs(additions):
            self._programs.append(_add)
