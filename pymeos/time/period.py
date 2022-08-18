from __future__ import annotations

import warnings
from datetime import datetime, timedelta
from typing import Optional, Union
from typing import TYPE_CHECKING

from dateutil.parser import parse

from pymeos_cffi.functions import datetime_to_timestamptz, period_in, pg_timestamptz_in, period_make, \
    overlaps_span_span, \
    span_ge, contains_period_timestamp, span_eq, span_cmp, span_lt, span_le, span_gt, period_shift_tscale, \
    timedelta_to_interval, timestamptz_to_datetime, period_lower, period_upper, span_hash, \
    period_out, span_copy, \
    period_to_periodset, adjacent_period_periodset, adjacent_period_timestamp, \
    adjacent_period_timestampset, adjacent_span_span

if TYPE_CHECKING:
    # Import here to use in type hints
    from .periodset import PeriodSet
    from .timestampset import TimestampSet

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class Period:
    """
    Class for representing sets of contiguous timestamps between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``Period`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> Period(string='(2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01)')

    Another possibility is to give a tuple of arguments as follows:

    * ``lower`` and ``upper`` are instances of ``str`` or ``datetime``
      specifying the bounds,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default, ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.

    Some examples are given next.

        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01')
        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01', lower_inc=False, upper_inc=True)
        >>> Period(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'))
        >>> Period(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'), lower_inc=False, upper_inc=True)

    """

    __slots__ = ['_inner']

    def __init__(self, *, string: Optional[str] = None, lower: Optional[Union[str, datetime]] = None,
                 upper: Optional[Union[str, datetime]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (lower is not None and upper is not None)), \
            "Either string must be not None or both lower and upper must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = period_in(string)
        else:
            lower_ts = pg_timestamptz_in(lower, -1) if isinstance(lower, str) else datetime_to_timestamptz(lower)
            upper_ts = pg_timestamptz_in(upper, -1) if isinstance(upper, str) else datetime_to_timestamptz(upper)
            self._inner = period_make(lower_ts, upper_ts, lower_inc, upper_inc)

    @property
    def lower(self) -> datetime:
        """
        Lower bound
        """
        return timestamptz_to_datetime(period_lower(self._inner))

    @property
    def upper(self) -> datetime:
        """
        Upper bound
        """
        return timestamptz_to_datetime(period_upper(self._inner))

    @property
    def lower_inc(self) -> bool:
        """
        Is the lower bound inclusive?
        """
        return self._inner.lower_inc

    @property
    def upper_inc(self) -> bool:
        """
        Is the upper bound inclusive?
        """
        return self._inner.upper_inc

    @property
    def duration(self) -> timedelta:
        """
        Time interval on which the period is defined
        """
        return self.upper - self.lower

    def shift(self, time_delta) -> Period:
        """
        Shift the period by a time interval
        """
        interval = timedelta_to_interval(time_delta)
        inner = period_shift_tscale(interval, None, self._inner)
        return Period(_inner=inner)

    def overlap(self, other) -> bool:
        """
        Do the periods share a timestamp?
        """
        return overlaps_span_span(self._inner, other._inner)

    def contains_timestamp(self, date_time: datetime) -> bool:
        """
        Does the period contain the timestamp?
        """
        ts = datetime_to_timestamptz(date_time)
        return contains_period_timestamp(self._inner, ts)

    def to_periodset(self) -> PeriodSet:
        from .periodset import PeriodSet
        return PeriodSet(_inner=period_to_periodset(self._inner))

    def is_adjacent(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return adjacent_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_period_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return span_eq(self._inner, other._inner)
        return False

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return span_cmp(self._inner, other._inner)
        return 0

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return span_lt(self._inner, other._inner)
        return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return span_le(self._inner, other._inner)
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return span_gt(self._inner, other._inner)
        return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return span_ge(self._inner, other._inner)
        return False

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "{}".format(self.__str__())

    # End Psycopg2 interface.

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return Period(string=value)

    def __copy__(self):
        inner_copy = span_copy(self._inner)
        return Period(_inner=inner_copy)

    def __str__(self):
        return period_out(self._inner)

    def __hash__(self) -> int:
        return span_hash(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')
