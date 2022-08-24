from datetime import datetime
from typing import TYPE_CHECKING

from pymeos_cffi.functions import timestamp_to_period, datetime_to_timestamptz, timestamp_to_periodset, \
    timestamp_to_timestampset

if TYPE_CHECKING:
    from .period import Period
    from .periodset import PeriodSet
    from .timestampset import TimestampSet


def datetime_to_period(self: datetime) -> Period:
    from .period import Period
    return Period(_inner=timestamp_to_period(datetime_to_timestamptz(self)))


def datetime_to_periodset(self: datetime) -> PeriodSet:
    from .period import PeriodSet
    return PeriodSet(_inner=timestamp_to_periodset(datetime_to_timestamptz(self)))


def datetime_to_timestampset(self: datetime) -> TimestampSet:
    from .timestampset import TimestampSet
    return TimestampSet(_inner=timestamp_to_timestampset(datetime_to_timestamptz(self)))


datetime.to_period = datetime_to_period
datetime.to_periodset = datetime_to_periodset
datetime.to_timestampset = datetime_to_timestampset
