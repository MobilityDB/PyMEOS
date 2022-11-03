from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Union, overload
from typing import TYPE_CHECKING

from dateutil.parser import parse
from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from .periodset import PeriodSet
    from .timestampset import TimestampSet
    from .time import Time


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

    Some pymeos_examples are given next.

        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01')
        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01', lower_inc=False, upper_inc=True)
        >>> Period(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'))
        >>> Period(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'), lower_inc=False, upper_inc=True)

    """

    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *, lower: Optional[Union[str, datetime]] = None,
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

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Period:
        result = span_from_hexwkb(hexwkb)
        return Period(_inner=result)

    def as_hexwkb(self) -> str:
        return span_as_hexwkb(self._inner, -1)[0]

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

    @property
    def width(self) -> float:
        return span_width(self._inner)

    def shift_tscale(self, shift_delta: Optional[timedelta] = None, scale_delta: Optional[timedelta] = None) -> Period:
        """
        Shift the period by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        p = period_shift_tscale(
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None,
            self._inner
        )
        return Period(_inner=p)

    def expand(self, other: Period) -> Period:
        copy = span_copy(self._inner)
        span_expand(other._inner, copy)
        return Period(_inner=copy)

    def to_periodset(self) -> PeriodSet:
        from .periodset import PeriodSet
        return PeriodSet(_inner=period_to_periodset(self._inner))

    def is_adjacent(self, other: Union[Time, Temporal]) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return adjacent_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, Temporal]) -> bool:
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(container, Period):
            return contained_span_span(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_period_periodset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_period_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Time, Temporal]) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(content, Period):
            return contains_span_span(self._inner, content._inner)
        elif isinstance(content, PeriodSet):
            return contains_period_periodset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_period_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_period_timestampset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_period_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return overlaps_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_period_periodset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Time) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return right_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return after_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return after_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Time) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return left_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return before_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return before_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Time) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overright_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overafter_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overafter_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Time) -> bool:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overleft_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overbefore_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overbefore_period_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Temporal) -> bool:
        from ..temporal import Temporal
        if isinstance(other, Temporal):
            return same_period_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def distance(self, other: Time) -> float:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return distance_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return distance_period_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return distance_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return distance_period_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def intersection(self, other: Period) -> Period:
        ...

    @overload
    def intersection(self, other: PeriodSet) -> PeriodSet:
        ...

    @overload
    def intersection(self, other: datetime) -> datetime:
        ...

    @overload
    def intersection(self, other: TimestampSet) -> TimestampSet:
        ...

    def intersection(self, other: Time) -> Time:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return Period(_inner=intersection_span_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=intersection_period_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timestamptz_to_datetime(intersection_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=intersection_period_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def minus(self, other: Time) -> PeriodSet:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return PeriodSet(_inner=minus_period_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=minus_period_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return PeriodSet(_inner=minus_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=minus_period_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def union(self, other: Time) -> PeriodSet:
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return PeriodSet(_inner=union_period_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_period_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return PeriodSet(_inner=union_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=union_period_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def __mul__(self, other):
        return self.intersection(other)

    def __add__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return self.minus(other)

    def __contains__(self, item):
        return self.contains(item)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return span_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return span_ne(self._inner, other._inner)
        return True

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return span_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return span_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return span_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return span_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return span_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, _):
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

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_period(self, *args, **kwargs)
