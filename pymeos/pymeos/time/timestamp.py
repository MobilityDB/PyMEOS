from datetime import datetime
from typing import TYPE_CHECKING, Union

from pymeos_cffi.functions import timestamp_to_period, datetime_to_timestamptz, timestamp_to_periodset, \
    timestamp_to_timestampset, adjacent_timestamp_period, adjacent_timestamp_periodset, contained_timestamp_period, \
    contained_timestamp_periodset, contained_timestamp_timestampset

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


def datetime_is_adjacent(self: datetime, other: Union[Period, PeriodSet]) -> bool:
    from .period import Period
    from .periodset import PeriodSet
    if isinstance(other, Period):
        return adjacent_timestamp_period(datetime_to_timestamptz(self), other._inner)
    elif isinstance(other, PeriodSet):
        return adjacent_timestamp_periodset(datetime_to_timestamptz(self), other._inner)
    else:
        raise TypeError(f'Operation not supported with type {other.__class__}')


def datetime_is_contained_in(self: datetime, container: Union[Period, PeriodSet, TimestampSet]) -> bool:
    from .period import Period
    from .periodset import PeriodSet
    from .timestampset import TimestampSet
    if isinstance(container, Period):
        return contained_timestamp_period(datetime_to_timestamptz(self), container._inner)
    elif isinstance(container, PeriodSet):
        return contained_timestamp_periodset(datetime_to_timestamptz(self), container._inner)
    elif isinstance(container, TimestampSet):
        return contained_timestamp_timestampset(datetime_to_timestamptz(self), container._inner)
    else:
        raise TypeError(f'Operation not supported with type {container.__class__}')


datetime.to_period = datetime_to_period
datetime.to_periodset = datetime_to_periodset
datetime.to_timestampset = datetime_to_timestampset
datetime.is_adjacent = datetime_is_adjacent
datetime.is_contained_in = datetime_is_contained_in
