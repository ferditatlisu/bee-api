from enum import Enum


class OffsetType(Enum):
    BEGINNING = 0
    END = 1,
    SHIFTBY = 2,
    DATE = 3