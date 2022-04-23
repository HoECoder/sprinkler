"""Test out key dates

There are some key dates I would like to use to ensure the programs do the right
thing in terms of running the station.

Primarily, we want to check the Winter -> Summer Time and Summer -> Winter transitions.
These are unfortunately US based.
"""

from typing import List, Mapping
from unittest import TestCase
import pendulum
from pendulum.datetime import DateTime
from sprinkler.program.abc.program import ProgramTime
from sprinkler.station.station import Station
from sprinkler.program.dictionary.program import LOCAL_TZ, DictSprinklerProgram
from sprinkler.program.dictionary.helpers import DictProgram, turn_dict_into_dict_program
from tests.sample_prog_data import SAMPLE_EVEN_DST_START_DICT, SAMPLE_ODD_DST_START_DICT
from tests.sample_prog_data import SAMPLE_EVEN_DST_END_DICT, SAMPLE_ODD_DST_END_DICT

DST_START_TIME = {
    "hour": 1,
    "minute": 59,
    "second": 59,
    "tz": LOCAL_TZ
}

DST_END_TIME = {
    "hour": 0,
    "minute": 59,
    "second": 59,
    "tz": LOCAL_TZ
}

DST_STARTS = [
    pendulum.datetime(2023, 3, 12, **DST_START_TIME),
    pendulum.datetime(2024, 3, 10, **DST_START_TIME),
]

DST_ENDS = [
    pendulum.datetime(2022, 11, 6, **DST_END_TIME),
    pendulum.datetime(2023, 11, 5, **DST_END_TIME),
    pendulum.datetime(2024, 11, 3, **DST_END_TIME),
]

class TestKeyDatesOnProgram(TestCase):
    """Tests the transition of key time changes"""
    def setUp(self):
        self.even_start_prog = turn_dict_into_dict_program(SAMPLE_EVEN_DST_START_DICT)
        self.odd_start_prog = turn_dict_into_dict_program(SAMPLE_ODD_DST_START_DICT)
        self.even_end_prog = turn_dict_into_dict_program(SAMPLE_EVEN_DST_END_DICT)
        self.odd_end_prog = turn_dict_into_dict_program(SAMPLE_ODD_DST_END_DICT)
        self.all_sts = {
            1: Station(1, True, True),
            2: Station(2, True, True),
            3: Station(3, True, True),
            4: Station(4, True, True),
            5: Station(5, True, True),
            6: Station(6, True, True),
            7: Station(7, True, True),
            8: Station(8, True, True),
        }
    def do_overage(self,
                   times: List[DateTime],
                   even_odd_progs: Mapping[int, DictProgram],
                   expected: Mapping[int, List[bool]]):
        """Test starts and end"""
        for start in times:
            # prog_conf = self.even_start_prog
            prog_conf = even_odd_progs[start.day % 2]
            prog = DictSprinklerProgram.factory(prog_conf,
                                                self.all_sts,
                                                now=start.float_timestamp)
            for offset, exp_res in expected.items():
                with self.subTest(dst_start=start, offset=offset, exp_res=exp_res):
                    prog.update_program(start.float_timestamp + offset)
                    res = [st.on for st in prog.stations]
                    self.assertListEqual(res, exp_res)
    def test_dst_start(self):
        """Test DST starts"""
        expected = {
            0: [False, True, False, False, False], # Middle of St 2, before DST
            1: [False, True, False, False, False], # Middle of St 2, at DST
            2: [False, True, False, False, False], # Middle of St 2, after DST
            2101: [False, False, True, False, False] # After St 2
        }
        even_odds = {
            0: self.even_start_prog,
            1: self.odd_start_prog
        }
        self.do_overage(DST_STARTS, even_odds, expected)
    def test_dst_end(self):
        """Tests end of DST"""
        expected = {
            0: [False, True, False, False, False], # Middle of St 2, before DST
            1: [False, True, False, False, False], # Middle of St 2, at DST
            2: [False, True, False, False, False], # Middle of St 2, after DST
            2101: [False, False, True, False, False] # After St 2
        }
        print("")
        even_odds = {
            0: self.even_end_prog,
            1: self.odd_end_prog
        }
        self.do_overage(DST_ENDS, even_odds, expected)

def _pretty_prog_time(prog_t: ProgramTime) -> str: #pragma: no cover
    """Makes a pretty program time"""
    start = str(pendulum.from_timestamp(prog_t.start, LOCAL_TZ))
    end = str(pendulum.from_timestamp(prog_t.end, LOCAL_TZ))
    return f"Start: {start}, End: {end}, Duration: {prog_t.duration}"
