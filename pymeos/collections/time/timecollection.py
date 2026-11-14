from abc import ABC
from datetime import date, timedelta
from typing import TypeVar

from ..base.collection import Collection

TimeClass = TypeVar("TimeClass", bound=date)

_DAY = timedelta(days=1)


def whole_days(delta: timedelta | int) -> int:
    """
    Returns the days of a shift or a width of dates, which MEOS takes as a whole number of days.

    The collections of timestamps pass a :class:`datetime.timedelta` through the cast
    #timedelta_to_interval of pymeos_cffi; MEOS has no cast of an interval to a number of days,
    so the collections of dates read the days of the :class:`datetime.timedelta` here.

    Args:
        delta: :class:`int` number of days or :class:`datetime.timedelta` of whole days

    Returns:
        The number of days as an :class:`int`

    Raises:
        ValueError: when ``delta`` is a :class:`datetime.timedelta` with a part below a day
    """
    if isinstance(delta, timedelta):
        days, rest = divmod(delta, _DAY)
        if rest:
            raise ValueError(f"A shift or a width of dates is a whole number of days: {delta!r}")
        return days
    return int(delta)


class TimeCollection(Collection[TimeClass], ABC):
    def is_before(self, other) -> bool:
        return self.is_left(other)

    def is_over_or_before(self, other) -> bool:
        return self.is_over_or_left(other)

    def is_over_or_after(self, other) -> bool:
        return self.is_over_or_right(other)

    def is_after(self, other) -> bool:
        return self.is_right(other)
