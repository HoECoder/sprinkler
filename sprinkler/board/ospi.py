"""Open Sprinkler Pi Board"""

from typing import List
from sprinkler.board.pins import SRPins
from sprinkler.board.board import Board
from sprinkler.station.station import Station

# pin_sr_dat = 27 # Shift Register Data Pin
# pin_sr_clk = 4  # Shift Register Clock Pin
# pin_sr_oe = 17  # Shift Register Output Enable Pin
# pin_sr_lat = 22 # Shift Register Latch Pin

# We will attempt to import pigpio
# If we can't, we've got a mock that will pretend for the
# core pieces we care about
try:
    import pigpio # type: ignore
except ImportError:
    import mockpigio as pigpio

def get_pigpio_pi(host: str = 'localhost',
                  port: int = 8888,
                  show_errors: bool = True) -> pigpio.pi: # pragma: no cover
    """Wrapper to get the pigpio"""
    return pigpio.pi(host=host, port=port, show_errors=show_errors)

class PiGPIOConnFailure(Exception):
    """Raised for connection failures"""

class OSPIBoard(Board):
    """Represents the physical hardware of a Open Sprinkler Pi Board"""
    def __init__(self,
                 gpio_connector: pigpio.pi,
                 stations: List[Station],
                 use_rain_sensor: bool = False):
        super().__init__()
        self.stations = stations
        self.use_rain_sensor = use_rain_sensor
        self.gpio: pigpio.pi = gpio_connector
        if not self.gpio.connected:
            raise PiGPIOConnFailure("Failed to connect to pigpiod")
        self.setup_pins()
        self._previous_pattern = None
    def setup_pins(self):
        """Setup the pins for the board"""
        if not self.gpio:
            return # pragma: no cover
        self.gpio.set_mode(SRPins.OUTPUT_EN, pigpio.OUTPUT)
        self.gpio.set_mode(SRPins.CLOCK, pigpio.OUTPUT)
        self.gpio.set_mode(SRPins.DATA, pigpio.OUTPUT)
        self.gpio.set_mode(SRPins.LATCH, pigpio.OUTPUT)
        if self.use_rain_sensor:
            self.gpio.set_pull_up_down(SRPins.RAIN, pigpio.PUD_UP)
        # Force the levels the first time, they are in a random state
        self.gpio.write(SRPins.OUTPUT_EN, pigpio.ON)
        self.gpio.write(SRPins.CLOCK, pigpio.OFF)
        self.gpio.write(SRPins.DATA, pigpio.OFF)
        self.gpio.write(SRPins.LATCH, pigpio.OFF)
    def enable_disable_register(self, enable: bool) -> int:
        """Enables or Disables the Shift Register the shift register"""
        bit_val = pigpio.HIGH
        if enable:
            bit_val = pigpio.LOW
        return self.gpio.write(SRPins.OUTPUT_EN, bit_val)
    def enable_shift_register(self) -> int:
        """Enables the shift register"""
        return self.enable_disable_register(True)
    def disable_shift_register(self) -> int:
        """Diable the shift register"""
        return self.enable_disable_register(False)
    def set_clock(self, bit: int) -> int:
        """Set the clock pin"""
        return self.gpio.write(SRPins.CLOCK, bit)
    def clock_up(self) -> int:
        """Set the clock high"""
        return self.set_clock(pigpio.HIGH)
    def clock_down(self) -> int:
        """Set the clock low"""
        return self.set_clock(pigpio.LOW)
    def set_latch(self, bit: int) -> int:
        """Set the latch pin"""
        return self.gpio.write(SRPins.LATCH, bit)
    def latch(self) -> int:
        """Latch the shift register"""
        return self.set_latch(pigpio.HIGH)
    def unlatch(self) -> int:
        """Unlatch the shift register"""
        return self.set_latch(pigpio.LOW)
    def set_data_pin(self, bit: int) -> int:
        """Sets the data pin"""
        return self.gpio.write(SRPins.DATA, bit)
    def write_bits_to_register(self, bits: List[int]):
        """Writes the pattern to the register in the order given"""
        self.clock_down()
        self.unlatch()
        # loop through the bits and clock them into the register
        for bit in bits:
            self.clock_down()
            self.set_data_pin(bit)
            self.clock_up()
        self.latch()
    def send_pattern(self):
        """Applies the current pattern to the underlying hardware"""
        pattern = self.get_bit_pattern()
        if self._previous_pattern is not None and self._previous_pattern == pattern:
            # We don't excessively bang on the shift-register
            return
        self._previous_pattern = pattern
        # pattern goes out in MSB order
        pattern.reverse()
        self.disable_shift_register()
        self.write_bits_to_register(pattern)
        self.enable_shift_register()
