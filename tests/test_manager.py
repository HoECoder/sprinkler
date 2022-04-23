"""Test DictProgramManager"""

import time
from copy import deepcopy
from typing import List, Mapping
from unittest import TestCase

import pendulum

from sprinkler.program.abc.program import SprinklerProgram
from sprinkler.program.dictionary.helpers import turn_dict_into_dict_program
from sprinkler.program.dictionary.manager import DictProgramManager
from sprinkler.program.dictionary.manager import remove_dup_starts_for_even_odd
from sprinkler.program.dictionary.manager import turn_dicts_to_programs
from sprinkler.program.dictionary.program import LOCAL_TZ, DictSprinklerProgram
from sprinkler.program.time_utilities import local_dt_for_utc_now, utc_for_local_midnight
from sprinkler.station.station import Station
from tests.sample_prog_data import SAMPLE_ODD_DAY, SAMPLE_PROGRAM_DICT, SAMPLE_DOW_DAY

DUPLICATES = 3

class TestRemoveDuplicatePrograms(TestCase):
    """Tests program de-duplication"""
    def setUp(self):
        """Setup the programs"""
        now = time.time()
        self.all_st = [Station(_i+1, True, True) for _i in range(8)]
        multi_even: List[SprinklerProgram] = []
        multi_odd: List[SprinklerProgram] = []
        for _x in range(DUPLICATES):
            e_prog = turn_dict_into_dict_program(deepcopy(SAMPLE_PROGRAM_DICT))
            o_prog = turn_dict_into_dict_program(deepcopy(SAMPLE_ODD_DAY))
            de_prog = DictSprinklerProgram.factory(e_prog,
                                                   self.all_st,
                                                   now=now)
            do_prog = DictSprinklerProgram.factory(o_prog,
                                                   self.all_st,
                                                   now=now)
            multi_even.append(de_prog)
            multi_odd.append(do_prog)
        self.multi_even = multi_even
        self.multi_odd = multi_odd
        _dow_prog = turn_dict_into_dict_program(deepcopy(SAMPLE_DOW_DAY))
        self.dow_programs = [
            DictSprinklerProgram.factory(_dow_prog, self.all_st, now=now)
        ]
        self.single_prog = [
            multi_even[0]
        ]
        self.all_programs: List[SprinklerProgram] = []
        self.all_programs.extend(self.multi_even)
        self.all_programs.extend(self.multi_odd)
    def test_even_dedup(self):
        """Test remove_dup_starts_for_even_odd on evens"""
        new_list = remove_dup_starts_for_even_odd(self.multi_even)
        self.assertEqual(len(new_list), 1)
    def test_odd_dedup(self):
        """Test remove_dup_starts_for_even_odd on odds"""
        new_list = remove_dup_starts_for_even_odd(self.multi_odd)
        self.assertEqual(len(new_list), 1)
    def test_even_odd_dedup(self):
        """Test remove_dup_starts_for_even_odd for a mix"""
        new_list = remove_dup_starts_for_even_odd(self.all_programs)
        self.assertEqual(len(new_list), 2)
    def test_even_odd_dedup_ignores_dow(self):
        """Test remove_dup_starts_for_even_odd on DOW"""
        new_list = remove_dup_starts_for_even_odd(self.dow_programs)
        self.assertListEqual(new_list, self.dow_programs)
    def test_even_odd_dedup_single_prog(self):
        """Test remove_dup_starts_for_even_odd on DOW"""
        new_list = remove_dup_starts_for_even_odd(self.single_prog)
        self.assertListEqual(new_list, self.single_prog)

class TestDictProgramManager(TestCase):
    """Test DictProgramManager"""
    def setUp(self):
        """Setup"""
        self.all_st = [Station(_i+1, True, True) for _i in range(8)]
        multi_even: List[SprinklerProgram] = []
        multi_odd: List[SprinklerProgram] = []
        for _x in range(DUPLICATES):
            e_prog = deepcopy(SAMPLE_PROGRAM_DICT)
            o_prog = deepcopy(SAMPLE_ODD_DAY)
            multi_even.append(e_prog)
            multi_odd.append(o_prog)
        self.multi_even = multi_even
        self.multi_odd = multi_odd
        self.dow_programs = [
            deepcopy(SAMPLE_DOW_DAY)
        ]
        self.all_programs: List[Mapping] = []
        self.all_programs.extend(self.multi_even)
        self.all_programs.extend(self.multi_odd)
        self.all_programs.extend(self.dow_programs)
        self.all_st = [Station(_i, True, True) for _i in range(8)]
        self.local_dt = local_dt_for_utc_now(time.time(), LOCAL_TZ)
    def all_progs_mgr(self) -> DictProgramManager:
        """Makes a DictProgramManager"""
        return DictProgramManager(self.all_programs, self.all_st, LOCAL_TZ)
    def dow_only_mgr(self) -> DictProgramManager:
        """Make a DictProgramManager with only DOW programs"""
        return DictProgramManager(self.dow_programs, self.all_st, LOCAL_TZ)
    def test_init(self):
        """Tests initilization of DictProgramManager"""
        all_progs = turn_dicts_to_programs(self.all_programs)
        mgr = self.all_progs_mgr()
        self.assertSequenceEqual(all_progs, mgr.programs)
    def test_search_prog_by_time(self):
        """Test DictProgramManager.search_prog_by_time"""
        mgr = self.all_progs_mgr()
        expected_progs = [
            DictSprinklerProgram.factory(turn_dict_into_dict_program(_progc),
                                         self.all_st,
                                         now=self.local_dt.timestamp())
            for _progc in self.all_programs
        ]
        midnight = utc_for_local_midnight(self.local_dt.timestamp(), LOCAL_TZ)
        start = SAMPLE_PROGRAM_DICT["start_time_of_day"]
        now = midnight + start
        res = mgr.search_progs_by_time(now)
        self.assertListEqual(expected_progs, res)
    def test_get_program(self):
        """Test DictProgramManager.get_program"""
        # all the programs start at 6 am Local time
        expected = {
            pendulum.datetime(2022, 4, 1, 6, tz = LOCAL_TZ): deepcopy(SAMPLE_ODD_DAY),
            pendulum.datetime(2022, 4, 2, 6, tz = LOCAL_TZ): deepcopy(SAMPLE_PROGRAM_DICT),
            pendulum.datetime(2022, 4, 2, 16, tz = LOCAL_TZ): None,
        }
        mgr = self.all_progs_mgr()
        for date_t, conf in expected.items():
            if conf is not None:
                prog = DictSprinklerProgram.factory(turn_dict_into_dict_program(conf),
                                                    self.all_st,
                                                    now=date_t.float_timestamp)
            else:
                prog = None
            result = mgr.get_program(date_t.float_timestamp)
            with self.subTest(prog=prog, result=result):
                self.assertEqual(prog, result)
    def test_get_program_dow(self):
        """Test DictProgramManager.get_program for DOW program"""
        # all the programs start at 6 am Local time
        expected = {
            pendulum.datetime(2022, 4, 1, 6, tz = LOCAL_TZ): deepcopy(SAMPLE_DOW_DAY),
            pendulum.datetime(2022, 4, 2, 6, tz = LOCAL_TZ): None,
            pendulum.datetime(2022, 4, 2, 16, tz = LOCAL_TZ): None,
            pendulum.datetime(2022, 4, 4, 6, tz = LOCAL_TZ): deepcopy(SAMPLE_DOW_DAY),
            pendulum.datetime(2022, 4, 6, 6, tz = LOCAL_TZ): deepcopy(SAMPLE_DOW_DAY),
            pendulum.datetime(2022, 4, 17, 6, tz = LOCAL_TZ): None,
        }
        mgr = self.dow_only_mgr()
        for date_t, conf in expected.items():
            if conf is not None:
                prog = DictSprinklerProgram.factory(turn_dict_into_dict_program(conf),
                                                    self.all_st,
                                                    now=date_t.float_timestamp)
            else:
                prog = None
            result = mgr.get_program(date_t.float_timestamp)
            msg = f"Wrong for ts: {repr(date_t)}"
            with self.subTest(prog=prog, result=result, msg=msg):
                self.assertEqual(prog, result)
