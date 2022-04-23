"""Program Types"""

from enum import IntEnum

class ProgramType(IntEnum):
    """Represents the kind of Programs that exist"""
    DAYOFTHEWEEK = 1
    EVENDAYSONLY = 2
    ODDDAYSONLY = 3
