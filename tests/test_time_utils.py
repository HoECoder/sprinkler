"""Test out the time utilities"""

from typing import List, Tuple
from unittest import TestCase
import pendulum

from sprinkler.program.time_utilities import after_now, seconds_from_midnight, utc_for_local_midnight

class TestTimeUtils(TestCase):
    """Test out the time utilities"""
    def setUp(self) -> None:
        self.tz = "US/Central" # pylint: disable=invalid-name
    def test_utc_for_local_midnight(self):
        """Tests the utc_for_local_midnight function"""
        tests = [
            (
                pendulum.datetime(2022, 4, 1, hour = 6, tz = self.tz).float_timestamp,
                pendulum.datetime(2022, 4, 1, hour = 0, tz = self.tz).float_timestamp
            ),
            (
                pendulum.datetime(2022, 4, 2, hour = 23, tz = self.tz).float_timestamp,
                pendulum.datetime(2022, 4, 2, hour = 0, tz = self.tz).float_timestamp
            ),
            (
                pendulum.datetime(2022, 4, 2, hour = 0, tz = self.tz).float_timestamp,
                pendulum.datetime(2022, 4, 2, hour = 0, tz = self.tz).float_timestamp
            ),
        ]
        for test_now, expected_mid in tests:
            test_val = utc_for_local_midnight(test_now, self.tz)
            self.assertEqual(expected_mid, test_val)
    def test_seconds_from_midnight(self):
        """Tests seconds_from_midnight"""
        tests: List[Tuple[int, int, int]] = [
            (6, 0, 6*3600),
            (6, 44, 6*3600 + 44*60)
        ]
        for hour, minute, expected_s in tests:
            with self.subTest(hour=hour,
                              minute=minute,
                              expected_s=expected_s):
                result = seconds_from_midnight(hour, minute)
                self.assertEqual(result, expected_s)
    def test_seconds_from_midnight_val_errors(self):
        """Test the cases where seconds_from_midnight raises ValueError"""
        tests: List[Tuple[int, int]] = [
            (-1, 0),
            (24, 0),
            (6, -1),
            (6, 60)
        ]
        for args in tests:
            with self.subTest(args=args):
                self.assertRaises(ValueError,
                                  seconds_from_midnight,
                                  *args)
    def test_after_now(self):
        """Tests the after_now utility"""
        tests: List[Tuple[Tuple[float, float, float], bool]] = [
            ((10, 10, 60), True),
            ((15, 10, 10), True),
            ((15, 10, 1), False),
            ((10, 15, 5), False)
        ]
        for test_args, expected_res in tests:
            with self.subTest(test_args=test_args, expected_res=expected_res):
                res = after_now(*test_args)
                self.assertEqual(res, expected_res)
