"""Tests the OSPIBoard class using mocks"""

from typing import Mapping
from unittest import TestCase
from unittest.mock import patch, MagicMock

import mockpigio
import sprinkler.board.ospi
from sprinkler.board import OSPIBoard
from sprinkler.board.ospi import PiGPIOConnFailure
from sprinkler.board.pins import SRPins
from sprinkler.station import Station

class TestOSPIBoard(TestCase):
    """Test out the functionality of the OSPIBoard"""
    @patch("sprinkler.board.ospi.get_pigpio_pi")
    def setUp(self, mock_res: MagicMock): # pylint: disable=arguments-differ
        """Setup the test"""
        mock_res.return_value = mockpigio.pi()
        gpio = sprinkler.board.ospi.get_pigpio_pi()
        self.all_st = [
            Station(1, True, True),
            Station(2, True, True),
            Station(3, True, True),
            Station(4, True, True),
            Station(5, True, True),
            Station(6, True, True),
            Station(7, True, True),
            Station(8, True, True),
        ]
        rainless = OSPIBoard(gpio, self.all_st)
        rainful = OSPIBoard(gpio,
                            self.all_st,
                            use_rain_sensor=True)
        self.rainless = rainless
        self.rainful = rainful
    def check_gpio_pins(self, gpio: mockpigio.pi, expect: Mapping[SRPins, int]):
        """Checkout the pins"""
        for pin, expected_mode in expect.items():
            with self.subTest(gpio=gpio, pin=pin, expected_mode=expected_mode):
                self.assertEqual(expected_mode, gpio.pin_modes[pin])
    def test_setup_pins_no_rain(self):
        """Tests that setup pins was called right for no rain sensor"""
        gpio: mockpigio.pi = self.rainless.gpio
        expected_pin_modes = {
            SRPins.OUTPUT_EN: mockpigio.OUTPUT,
            SRPins.CLOCK: mockpigio.OUTPUT,
            SRPins.DATA: mockpigio.OUTPUT,
            SRPins.LATCH: mockpigio.OUTPUT
        }
        self.check_gpio_pins(gpio, expected_pin_modes)
    def test_setup_pins_with_rain(self):
        """Tests that setup pins was called right for a rain sensor"""
        gpio: mockpigio.pi = self.rainful.gpio
        expected_pin_modes = {
            SRPins.OUTPUT_EN: mockpigio.OUTPUT,
            SRPins.CLOCK: mockpigio.OUTPUT,
            SRPins.DATA: mockpigio.OUTPUT,
            SRPins.LATCH: mockpigio.OUTPUT,
        }
        self.check_gpio_pins(gpio, expected_pin_modes)
        with self.subTest(gpio=gpio):
            self.assertEqual(gpio.pin_up_downs[SRPins.RAIN], mockpigio.PUD_UP)
    def test_get_bit_pattern(self):
        """Test Board.get_bit_pattern"""
        expected_states = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
        ]
        for expected_state in expected_states:
            for state, station in zip(expected_state, self.all_st):
                if state == 1:
                    station.on = True
                else:
                    station.on = False
            with self.subTest(expected_state=expected_state):
                self.assertListEqual(expected_state,
                                     self.rainless.get_bit_pattern())
    def test_stop_all_stations(self):
        """Tests Board.stop_all_stations"""
        test_states = [
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1],
        ]
        all_zeros = [0, 0, 0, 0, 0, 0, 0, 0]
        for test_state in test_states:
            for state, station in zip(test_state, self.all_st):
                if state == 1:
                    station.on = True
                else:
                    station.on = False
            self.rainless.stop_all_stations()
            with self.subTest(test_state=test_state):
                self.assertListEqual(all_zeros,
                                     self.rainless.get_bit_pattern())
    @patch("sprinkler.board.ospi.get_pigpio_pi")
    def test_conn_failure_exception(self, mock_res: MagicMock): # pylint: disable=arguments-differ
        """Test that we get a PiGPIOConnFailure on a conn failure"""
        mock_res.return_value = mockpigio.pi()
        gpio = sprinkler.board.ospi.get_pigpio_pi()
        gpio.connected = False
        with self.assertRaises(PiGPIOConnFailure):
            OSPIBoard(gpio, self.all_st)
