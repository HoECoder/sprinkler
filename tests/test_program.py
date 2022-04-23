"""Tests out SprinklerPrograms"""
from copy import deepcopy
from datetime import datetime
from typing import Callable, List, Tuple
from unittest import TestCase

from marshmallow import ValidationError
import pendulum

from sprinkler.program.dictionary.program import LOCAL_TZ, DictSprinklerProgram
from sprinkler.program.dictionary.helpers import ProgramDictSchema, ProgramEntry
from sprinkler.program.dictionary.helpers import turn_dict_into_dict_program
from sprinkler.program.program_types import ProgramType
from sprinkler.station.station import Station

from tests.sample_prog_data import SAMPLE_PROGRAM_DICT, SAMPLE_ODD_DAY, SAMPLE_DOW_DAY
from tests.sample_prog_data import SAMPLE_NO_ADJ_PROGRAM_DICT, SAMPLE_RUN_TIME
from tests.sample_prog_data import SAMPLE_BAD_PROGRAM_DICT

class TestDictProgramHelpers(TestCase):
    """Tests the dictionary program helpers"""
    def setUp(self):
        """Setup the tests"""
        self.schema = ProgramDictSchema()

    def test_working_dict_from_schema(self):
        """Test that a meaningful dict comes out of the schema"""
        data = self.schema.load(SAMPLE_PROGRAM_DICT)
        with self.subTest(data=data):
            all_pes = all(isinstance(_i, ProgramEntry) for _i in data["station_durations"])
            self.assertTrue(all_pes)
        with self.subTest(data=data):
            self.assertTrue(isinstance(data["program_type"], ProgramType))
    def test_non_working_dict_through_schema(self):
        """Tests that we get a validation error for a malformed schema"""
        with self.assertRaises(ValidationError):
            self.schema.load(SAMPLE_BAD_PROGRAM_DICT)
    def test_getting_a_dict_program_from_a_dict(self):
        """Tests that we can get a DictProgram from a good dict"""
        program = turn_dict_into_dict_program(SAMPLE_PROGRAM_DICT)
        with self.subTest(program=program):
            all_pes = all(isinstance(_i, ProgramEntry) for _i in program.station_durations)
            self.assertTrue(all_pes)
        with self.subTest(program=program):
            self.assertTrue(isinstance(program.program_type, ProgramType))
            self.assertEqual(program.program_type, ProgramType.EVENDAYSONLY)
    def test_getting_a_dict_program_from_a_bad_dict(self):
        """Tests that we get a validation error"""
        with self.assertRaises(ValidationError):
            turn_dict_into_dict_program(SAMPLE_BAD_PROGRAM_DICT)


class TestSprinklerProgram(TestCase):
    """Tests SprinklerProgram"""
    def setUp(self) -> None:
        self.sample_dict_program = turn_dict_into_dict_program(SAMPLE_PROGRAM_DICT)
        self.sample_odd_program = turn_dict_into_dict_program(SAMPLE_ODD_DAY)
        self.sample_dow_program = turn_dict_into_dict_program(SAMPLE_DOW_DAY)
        self.sample_no_adj_program = turn_dict_into_dict_program(SAMPLE_NO_ADJ_PROGRAM_DICT)
        self.all_stations = {
            1: Station(1, True, True),
            2: Station(2, True, True),
            3: Station(3, True, True),
            4: Station(4, True, True),
            5: Station(5, True, True),
            6: Station(6, True, True),
            7: Station(7, True, True),
            8: Station(8, True, True),
        }
    def test_valid_on_even_day(self):
        """Tests the classmethod DictSprinklerProgram.valid_on_day for even days"""
        # Program is for even days
        test_days_results: List[Tuple[datetime, bool]] = [
            (datetime(year=2022, month=4, day=1), False),
            (datetime(year=2022, month=4, day=2), True),
            (datetime(year=2022, month=4, day=21), False),
            (datetime(year=2022, month=4, day=30), True),
        ]
        for test_date, expected_res in test_days_results:
            with self.subTest(test_date=test_date, expected_res=expected_res):
                valid = DictSprinklerProgram.valid_on_day(test_date, self.sample_dict_program)
                self.assertEqual(valid, expected_res)
    def test_valid_on_odd_day(self):
        """Tests the classmethod DictSprinklerProgram.valid_on_day for odd days"""
        # Program is for odd days
        test_days_results: List[Tuple[datetime, bool]] = [
            (datetime(year=2022, month=4, day=1), True),
            (datetime(year=2022, month=4, day=2), False),
            (datetime(year=2022, month=4, day=21), True),
            (datetime(year=2022, month=4, day=30), False),
        ]
        for test_date, expected_res in test_days_results:
            with self.subTest(test_date=test_date, expected_res=expected_res):
                valid = DictSprinklerProgram.valid_on_day(test_date, self.sample_odd_program)
                self.assertEqual(valid, expected_res)
    def test_valid_on_dow_day(self):
        """Tests the classmethod DictSprinklerProgram.valid_on_day for DOW schedule"""
        # Program is for M, W, F
        test_days_results: List[Tuple[datetime, bool]] = [
            (datetime(year=2022, month=4, day=1), True),
            (datetime(year=2022, month=4, day=4), True),
            (datetime(year=2022, month=4, day=7), False),
            (datetime(year=2022, month=4, day=27), True),
            (datetime(year=2022, month=4, day=30), False),
        ]
        print("")
        for test_date, expected_res in test_days_results:
            with self.subTest(test_date=test_date, expected_res=expected_res):
                valid = DictSprinklerProgram.valid_on_day(test_date, self.sample_dow_program)
                self.assertEqual(valid, expected_res)
    def test_should_run_now(self):
        """Tests the classmethod DictSprinklerProgram.should_run_now"""
        # Program is for even days
        # It starts at 6 am local time
        expected_results: List[Tuple[float, bool]] = [
            (pendulum.datetime(2022, 4, 1, hour = 6, tz = LOCAL_TZ).float_timestamp, False),
            (pendulum.datetime(2022, 4, 2, hour = 6, tz = LOCAL_TZ).float_timestamp, True),
            (pendulum.datetime(2022, 4, 2, hour = 5, tz = LOCAL_TZ).float_timestamp, False),
            (pendulum.datetime(2022, 4, 2, hour = 7, tz = LOCAL_TZ).float_timestamp, False),
            (pendulum.datetime(2022, 4, 1, hour = 18, tz = LOCAL_TZ).float_timestamp, False),
        ]
        for test_now, expected_res in expected_results:
            with self.subTest(test_now=test_now, expected_res=expected_res):
                should = DictSprinklerProgram.should_run_now(test_now, self.sample_dict_program)
                self.assertEqual(should, expected_res)
    def test_program_creation(self):
        """Test the instantiation of a program"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        self.assertEqual(program.program_run_time, SAMPLE_RUN_TIME)
    def test_program_runtime(self):
        """Test SprinklerProgram.program_run_time"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        self.assertEqual(program.program_run_time, SAMPLE_RUN_TIME)
    def test_program_stations(self):
        """Test SprinklerProgram.stations"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        expected_stations = [
            self.all_stations[1],
            self.all_stations[2],
            self.all_stations[3],
            self.all_stations[4],
            self.all_stations[5],
        ]
        self.assertListEqual(program.stations, expected_stations)
    def test_program_end_time(self):
        """Test SprinklerProgram.program_end_time"""
        now = pendulum.datetime(2022, 4, 1, hour=6, tz = LOCAL_TZ)
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations,
                                               now = now.float_timestamp)
        expected = now.float_timestamp + SAMPLE_RUN_TIME
        self.assertEqual(expected, program.program_end_time)
    def test_program_type(self):
        """Test SprinklerProgram.program_type"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        self.assertEqual(ProgramType.EVENDAYSONLY, program.program_type)
    def test_respects_water_adjustment(self):
        """Test SprinklerProgram.respects_water_adjustment"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        self.assertTrue(program.respects_water_adjustment)
    def test_respect_rain_delay(self):
        """Test SprinklerProgram.respect_rain_delay"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        self.assertTrue(program.respect_rain_delay)
    def test_days_of_the_week(self):
        """Tests the SprinklerProgram.days_of_the_week property"""
        prog1 = DictSprinklerProgram.factory(self.sample_dow_program,
                                             self.all_stations)
        prog2 = DictSprinklerProgram.factory(self.sample_dict_program,
                                             self.all_stations)
        expected_dows: List[Tuple[DictSprinklerProgram, List[int]]] = [
            (prog1, [0, 2, 4]),
            (prog2, [])
        ]
        for prog, expected_dow in expected_dows:
            with self.subTest(prog=prog, expected_dow=expected_dow):
                self.assertListEqual(expected_dow, prog.days_of_the_week)
    def test_adjust_watering(self):
        """Test SprinklerProgram.adjust_watering"""
        program = DictSprinklerProgram.factory(self.sample_dict_program,
                                               self.all_stations)
        percentage = 75
        expected_run = percentage * SAMPLE_RUN_TIME
        program.adjust_watering(percentage)
        self.assertAlmostEqual(expected_run, program.program_run_time, 0)
    def test_adjust_watering_no_adj(self):
        """Test SprinklerProgram.adjust_watering if the program doesn't adjust"""
        program = DictSprinklerProgram.factory(self.sample_no_adj_program,
                                               self.all_stations)
        percentage = 75
        expected_run = SAMPLE_RUN_TIME
        program.adjust_watering(percentage)
        self.assertAlmostEqual(expected_run, program.program_run_time, 0)
    def test_program_over(self):
        """Tests SprinklerProgram.program_over"""
        runtime_hrs = int(SAMPLE_RUN_TIME // 3600)
        runtime_min = int((SAMPLE_RUN_TIME - (runtime_hrs * 3600)) / 60)
        test_prog_now = pendulum.datetime(2022, 4, 2, hour=6, tz=LOCAL_TZ).float_timestamp
        test_prog = DictSprinklerProgram.factory(self.sample_dict_program,
                                                 self.all_stations,
                                                 now=test_prog_now)
        expected_results: List[Tuple[float, bool]] = [
            (
                pendulum.datetime(2022, 4, 2, hour=5, tz=LOCAL_TZ).float_timestamp,
                False
            ),
            (
                pendulum.datetime(2022, 4, 2, hour=6, tz=LOCAL_TZ).float_timestamp,
                False
            ),
            (
                pendulum.datetime(2022, 4, 2, hour=6+runtime_hrs, tz=LOCAL_TZ).float_timestamp,
                False
            ),
            (
                pendulum.datetime(2022,
                                  4,
                                  2,
                                  hour=6+runtime_hrs,
                                  minute=runtime_min,
                                  tz=LOCAL_TZ).float_timestamp,
                False
            ),
            (
                pendulum.datetime(2022,
                                  4,
                                  2,
                                  hour=6+runtime_hrs,
                                  minute=runtime_min+1,
                                  tz=LOCAL_TZ).float_timestamp,
                True
            ),
        ]
        for test_now, expected_res in expected_results:
            with self.subTest(test_now=test_now, expected_res=expected_res):
                res = test_prog.program_over(test_now)
                self.assertEqual(expected_res, res)
    def test_update_program(self):
        """Tests SprinklerProgram.update_program"""
        test_prog_now = pendulum.datetime(2022, 4, 2, hour=6, tz=LOCAL_TZ)
        test_prog = DictSprinklerProgram.factory(self.sample_dict_program,
                                                 self.all_stations,
                                                 now=test_prog_now.float_timestamp)
        # Program runs 5 stations, for 55, 40, 45, 30, and 50 minutes
        expected_results = [
            (
                test_prog_now.float_timestamp,
                [True, False, False, False, False]
            ),
            (
                test_prog_now.add(seconds=35).float_timestamp,
                [True, False, False, False, False]
            ),
            (
                test_prog_now.add(minutes=54, seconds=59).float_timestamp,
                [True, False, False, False, False]
            ),
            (
                test_prog_now.add(minutes=55).float_timestamp,
                [False, True, False, False, False]
            ),
            (
                test_prog_now.add(minutes=95).float_timestamp,
                [False, False, True, False, False]
            ),
            (
                test_prog_now.add(minutes=140).float_timestamp,
                [False, False, False, True, False]
            ),
            (
                test_prog_now.add(minutes=170).float_timestamp,
                [False, False, False, False, True]
            ),
            (
                test_prog_now.add(minutes=220).float_timestamp,
                [False, False, False, False, False]
            ),
        ]
        for test_now, expect_res in expected_results:
            with self.subTest(test_now=test_now, expect_res=expect_res):
                test_prog.update_program(test_now)
                res = [st.on for st in test_prog.stations]
                self.assertListEqual(expect_res, res)
    def test_prog_equal(self):
        """Test DictSprinklerProgram.__eq__"""
        test_prog_now = pendulum.datetime(2022, 4, 2, hour=6, tz=LOCAL_TZ)
        prog_a = DictSprinklerProgram.factory(self.sample_dict_program,
                                              self.all_stations,
                                              now=test_prog_now.float_timestamp)
        prog_b = DictSprinklerProgram.factory(deepcopy(self.sample_dict_program),
                                              self.all_stations,
                                              now=test_prog_now.float_timestamp)
        prog_c = DictSprinklerProgram.factory(self.sample_odd_program,
                                              self.all_stations,
                                              now=test_prog_now.float_timestamp)
        tests: List[Tuple[object, object, Callable]] = [
            (prog_a, prog_b, self.assertTrue),
            (prog_a, prog_c, self.assertFalse),
            (prog_c, prog_b, self.assertFalse),
            (prog_c, prog_c, self.assertTrue),
        ]
        for obj_a, obj_b, asserter in tests:
            with self.subTest(obj_a=obj_a, obj_b=obj_b):
                asserter(obj_a == obj_b)
