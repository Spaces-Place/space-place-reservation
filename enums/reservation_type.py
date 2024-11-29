

from enum import Enum, auto


class ReservationStatus(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELED = auto
