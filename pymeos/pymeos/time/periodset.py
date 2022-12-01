###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################

from __future__ import annotations

from datetime import timedelta, datetime
from typing import Optional, Union, List, overload
from typing import TYPE_CHECKING

from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from .period import Period
    from .timestampset import TimestampSet
    from .time import Time


class PeriodSet:
    """
    Class for representing lists of disjoint periods.

    ``PeriodSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> PeriodSet(string='{[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01], [2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]}')

    Another possibility is to give a list or tuple specifying the composing
    periods, which can be instances  of ``str`` or ``Period``. The composing
    periods must be given in increasing order.

        >>> PeriodSet(period_list=['[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'])
        >>> PeriodSet(period_list=[Period('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), Period('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')])

    """

    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *, period_list: Optional[List[Union[str, Period]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (period_list is not None)), \
            "Either string must be not None or period_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = periodset_in(string)
        else:
            periods = [period_in(period) if isinstance(period, str) else period._inner for period in period_list]
            self._inner = spanset_make(periods, len(periods), normalize)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> PeriodSet:
        result = periodset_from_hexwkb(hexwkb)
        return PeriodSet(_inner=result)

    def as_hexwkb(self) -> str:
        return periodset_as_hexwkb(self._inner, -1)[0]

    @property
    def duration(self) -> timedelta:
        """
        Time interval on which the period set is defined
        """
        return interval_to_timedelta(periodset_duration(self._inner))

    @property
    def timespan(self) -> timedelta:
        """
        Time interval on which the period set is defined
        """
        return self.end_timestamp - self.start_timestamp

    def to_period(self) -> Period:
        """
        Period on which the period set is defined ignoring the potential time gaps
        """
        from .period import Period
        return Period(_inner=spanset_to_span(self._inner))

    @property
    def num_timestamps(self) -> int:
        """
        Number of distinct timestamps
        """
        return periodset_num_timestamps(self._inner)

    @property
    def start_timestamp(self) -> datetime:
        """
        Start timestamp
        """
        return timestamptz_to_datetime(periodset_start_timestamp(self._inner))

    @property
    def end_timestamp(self) -> datetime:
        """
        End timestamp
        """
        return timestamptz_to_datetime(periodset_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        N-th distinct timestamp
        """
        # 1-based
        return timestamptz_to_datetime(periodset_timestamp_n(self._inner, n))

    @property
    def timestamps(self) -> List[datetime]:
        """
        Distinct timestamps
        """
        ts, count = periodset_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    @property
    def num_periods(self) -> int:
        """
        Number of periods
        """
        return spanset_num_spans(self._inner)

    @property
    def start_period(self) -> Period:
        """
        Start period
        """
        from .period import Period
        return Period(_inner=periodset_lower(self._inner))

    @property
    def end_period(self) -> Period:
        """
        End period
        """
        from .period import Period
        return Period(_inner=periodset_upper(self._inner))

    def period_n(self, n: int) -> Period:
        """
        N-th period
        """
        # 1-based
        from .period import Period
        return Period(_inner=spanset_span_n(self._inner, n))

    @property
    def periods(self) -> List[Period]:
        """
        Periods
        """
        from .period import Period
        ps, count = spanset_spans(self._inner)
        return [Period(_inner=ps[i]) for i in range(count)]

    def shift_tscale(self, shift_delta: Optional[timedelta] = None,
                     scale_delta: Optional[timedelta] = None) -> PeriodSet:
        """
        Shift the period set by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        ps = periodset_shift_tscale(
            self._inner,
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None
        )
        return PeriodSet(_inner=ps)

    def is_adjacent(self, other: Union[Time, Temporal]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return adjacent_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return adjacent_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, Temporal]) -> bool:
        from .period import Period
        from ..temporal import Temporal
        if isinstance(container, Period):
            return contained_spanset_span(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_spanset_spanset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_periodset_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Time, Temporal]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(content, Period):
            return contains_spanset_span(self._inner, content._inner)
        if isinstance(content, PeriodSet):
            return contains_spanset_spanset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_periodset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_periodset_timestampset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_periodset_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return overlaps_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overlaps_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Time) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return right_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return right_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return after_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Time) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return left_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return left_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return before_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Time) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overright_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overright_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overafter_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Time) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overleft_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overleft_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overbefore_periodset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Temporal) -> bool:
        from ..temporal import Temporal
        if isinstance(other, Temporal):
            return same_periodset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def distance(self, other: Time) -> float:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return distance_periodset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return distance_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return distance_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return distance_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def intersection(self, other: Period) -> PeriodSet:
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

    def intersection(self, other: Time) -> Union[PeriodSet, datetime, TimestampSet]:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return PeriodSet(_inner=intersection_spanset_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=intersection_spanset_spanset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timestamptz_to_datetime(
                intersection_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=intersection_periodset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def minus(self, other: Time) -> PeriodSet:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return PeriodSet(_inner=minus_spanset_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=minus_spanset_spanset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return PeriodSet(_inner=minus_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=minus_periodset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def union(self, other: Time) -> PeriodSet:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return PeriodSet(_inner=union_spanset_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_spanset_spanset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return PeriodSet(_inner=union_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=union_periodset_timestampset(self._inner, other._inner))
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
            return spanset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return spanset_ne(self._inner, other._inner)
        return True

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return spanset_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return spanset_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return spanset_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return spanset_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return spanset_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        if not value:
            return None
        return PeriodSet(string=value)

    def __copy__(self):
        inner_copy = spanset_copy(self._inner)
        return PeriodSet(_inner=inner_copy)

    def __str__(self):
        return periodset_out(self._inner)

    def __hash__(self) -> int:
        return spanset_hash(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_periodset(self, *args, **kwargs)
