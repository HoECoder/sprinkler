"""Define a station"""

class Station:
    """Represents a Station"""
    def __init__(self,
                 number: int,
                 enabled: bool,
                 weather_aware: bool):
        """Setup a station"""
        self.number = number
        self.enabled = enabled
        self.weather_aware = weather_aware
        self._on = False #pylint: disable=invalid-name
    @property
    def on(self) -> bool: #pylint: disable=invalid-name
        """Returns if this station is on or not"""
        return self._on
    @on.setter
    def on(self, state: bool) -> bool: #pylint: disable=invalid-name
        if not self.enabled:
            self._on = False
            return self._on
        self._on = state
        return self._on
    def __repr__(self) -> str: # pragma: no cover
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.number}, {self.enabled}, {self.weather_aware})"
