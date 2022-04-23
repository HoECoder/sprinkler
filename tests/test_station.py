"""Test out the Station class"""

from typing import List, Tuple
from unittest import TestCase

from sprinkler.station.station import Station

class TestStation(TestCase):
    """Test station basics"""
    def setUp(self):
        """Do some basic steup"""
        self.enabled_st = Station(1, True, True)
        self.disabled_st = Station(2, False, True)
    def test_on_off(self):
        """Test Enabled Station"""
        tests: List[Tuple[Station, bool, bool]] = [
            (
                self.enabled_st,
                True,
                True
            ),
            (
                self.enabled_st,
                False,
                False
            ),
            (
                self.disabled_st,
                True,
                False
            ),
            (
                self.disabled_st,
                False,
                False
            ),
        ]
        for station, new_state, exp_state in tests:
            with self.subTest(station=station,
                              new_state=new_state,
                              exp_state=exp_state):
                station.on = new_state
                result = station.on
                self.assertEqual(result, exp_state)
