"""Helper classes for the dict program"""
# import datetime
from collections import namedtuple
from typing import List, Mapping
from dataclasses import dataclass, field

from marshmallow import Schema, fields, post_load
from sprinkler.program.program_types import ProgramType

ProgramEntry = namedtuple("ProgramEntry", ["station_id", "duration"])

class ProgramDictSchema(Schema):
    """Schema defining Programs"""
    start_time_of_day = fields.Int(required=True)
    station_durations = fields.List(fields.Dict, required=True)
    program_type = fields.Int(required=True)
    respect_rain = fields.Bool(required=True)
    respect_water_adjustment = fields.Bool(required=True)
    days_of_the_week = fields.List(fields.Int)
    name = fields.Str()

    @post_load
    def tupleize_durations(self, input_data: Mapping, **kwargs): #pylint: disable=unused-argument, no-self-use, line-too-long
        """Turn station_durations into a list of ProgramEntry"""
        new_dur = []
        for duration in input_data["station_durations"]:
            new_dur.append(ProgramEntry(**duration))
        input_data["station_durations"] =  new_dur
        return input_data
    @post_load
    def enum_program_type(self, input_data: Mapping, **kwargs): #pylint: disable=unused-argument, no-self-use, line-too-long
        """Turn the program_type into Enum"""
        input_data["program_type"] = ProgramType(input_data["program_type"])
        return input_data

@dataclass
class DictProgram:
    """Dataclass representing a program config from a dictionary"""
    start_time_of_day: float
    station_durations: List[ProgramEntry]
    program_type: ProgramType
    respect_rain: bool
    respect_water_adjustment: bool
    days_of_the_week: List[int] = field(default_factory=list)
    name: str = field(default="")
    def __post_init__(self):
        """Fix up names"""
        if self.name:
            return #pragma: no cover
        if self.program_type == ProgramType.DAYOFTHEWEEK:
            dow = ",".join(str(_i) for _i in self.days_of_the_week)
            self.name = f"{self.program_type}_{self.start_time_of_day}_{dow}"
        else:
            self.name = f"{self.program_type}_{self.start_time_of_day}"

def turn_dict_into_dict_program(conf: Mapping) -> DictProgram:
    """Takes a raw schema and turn it into a program"""
    data = ProgramDictSchema().load(conf)
    return DictProgram(**data)
