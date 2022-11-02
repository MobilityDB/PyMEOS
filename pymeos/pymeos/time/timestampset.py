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

from datetime import datetime, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload

from dateutil.parser import parse
from pymeos_cffi.functions import pg_timestamp_in, datetime_to_timestamptz, timestampset_end_timestamp, \
    timestampset_start_timestamp, timestampset_num_timestamps, timestampset_timestamps, timestampset_timestamp_n, \
    timestampset_out, timestamptz_to_datetime, pg_timestamptz_out, timestampset_shift_tscale, timedelta_to_interval, \
    timestampset_eq, timestampset_ne, timestampset_cmp, timestampset_lt, timestampset_le, timestampset_ge, \
    timestampset_gt, timestampset_make, timestampset_in, timestampset_hash, timestampset_copy, \
    timestampset_to_periodset, adjacent_timestampset_period, adjacent_timestampset_periodset, \
    contained_timestampset_period, contained_timestampset_periodset, contained_timestampset_timestampset, \
    contains_timestampset_timestamp, contains_timestampset_timestampset, overlaps_timestampset_period, \
    overlaps_timestampset_periodset, overlaps_timestampset_timestampset, after_timestampset_period, \
    after_timestampset_periodset, after_timestampset_timestamp, after_timestampset_timestampset, \
    before_timestampset_period, before_timestampset_periodset, before_timestampset_timestamp, \
    before_timestampset_timestampset, overbefore_timestampset_timestampset, overbefore_timestampset_timestamp, \
    overbefore_timestampset_periodset, overbefore_timestampset_period, overafter_timestampset_timestampset, \
    overafter_timestampset_timestamp, overafter_timestampset_periodset, overafter_timestampset_period, \
    intersection_timestampset_period, intersection_timestampset_periodset, intersection_timestampset_timestamp, \
    intersection_timestampset_timestampset, minus_timestampset_period, minus_timestampset_periodset, \
    minus_timestampset_timestamp, minus_timestampset_timestampset, union_timestampset_period, \
    union_timestampset_periodset, union_timestampset_timestamp, union_timestampset_timestampset, \
    distance_timestampset_period, distance_timestampset_periodset, distance_timestampset_timestamp, \
    distance_timestampset_timestampset, timestampset_timespan, interval_to_timedelta, timestampset_from_hexwkb, \
    timestampset_as_hexwkb, adjacent_timestampset_temporal, contained_timestampset_temporal, \
    contains_timestampset_temporal, overlaps_timestampset_temporal, same_timestampset_temporal, \
    after_timestampset_temporal, before_timestampset_temporal, overafter_timestampset_temporal, \
    overbefore_timestampset_temporal

if TYPE_CHECKING:
    from ..temporal import Temporal
    from .period import Period
    from .periodset import PeriodSet
    from .time import Time


class TimestampSet:
    """
    Class for representing lists of distinct timestamp values.

    ``TimestampSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TimestampSet(string='{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TimestampSet(timestamp_list=['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TimestampSet(timestamp_list=[parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])

    """

    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *, timestamp_list: Optional[List[Union[str, datetime]]] = None,
                 _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (timestamp_list is not None)), \
            "Either string must be not None or timestamp_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = timestampset_in(string)
        else:
            times = [pg_timestamp_in(ts, -1) if isinstance(ts, str) else datetime_to_timestamptz(ts)
                     for ts in timestamp_list]
            self._inner = timestampset_make(times, len(times))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> TimestampSet:
        result = timestampset_from_hexwkb(hexwkb)
        return TimestampSet(_inner=result)

    def as_hexwkb(self) -> str:
        return timestampset_as_hexwkb(self._inner, -1)[0]

    @property
    def timespan(self) -> timedelta:
        """
        Interval on which the timestamp set is defined ignoring the potential time gaps
        """
        return interval_to_timedelta(timestampset_timespan(self._inner))

    @property
    def period(self) -> Period:
        """
        Period on which the timestamp set is defined ignoring the potential time gaps
        """
        from .period import Period
        return Period(lower=pg_timestamptz_out(timestampset_start_timestamp(self._inner)),
                      upper=pg_timestamptz_out(timestampset_end_timestamp(self._inner)),
                      lower_inc=True, upper_inc=True)

    @property
    def num_timestamps(self) -> int:
        """
        Number of timestamps
        """
        return timestampset_num_timestamps(self._inner)

    @property
    def start_timestamp(self) -> datetime:
        """
        Start timestamp
        """
        return timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    @property
    def end_timestamp(self) -> datetime:
        """
        End timestamp
        """
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        N-th timestamp
        """
        # 1-based
        return timestamptz_to_datetime(timestampset_timestamp_n(self._inner, n))

    @property
    def timestamps(self) -> List[datetime]:
        """
        Distinct timestamps
        """
        tss = timestampset_timestamps(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_timestamps)]

    def shift_tscale(self, shift_delta: Optional[timedelta] = None,
                     scale_delta: Optional[timedelta] = None) -> TimestampSet:
        """
        Shift the timestamp set by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        tss = timestampset_shift_tscale(
            self._inner,
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None
        )
        return TimestampSet(_inner=tss)

    def to_periodset(self) -> PeriodSet:
        from .periodset import PeriodSet
        return PeriodSet(_inner=timestampset_to_periodset(self._inner))

    def is_adjacent(self, other: Union[Period, PeriodSet, Temporal]) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return adjacent_timestampset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(container, Period):
            return contained_timestampset_period(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_timestampset_periodset(self._inner, container._inner)
        elif isinstance(container, TimestampSet):
            return contained_timestampset_timestampset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_timestampset_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[datetime, TimestampSet, Temporal]) -> bool:
        from ..temporal import Temporal
        if isinstance(content, datetime):
            return contains_timestampset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_timestampset_timestampset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_timestampset_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return overlaps_timestampset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Time) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return after_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return after_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return after_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Time) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return before_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return before_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return before_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Time) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return overafter_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overafter_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overafter_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Time) -> bool:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return overbefore_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overbefore_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overbefore_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Temporal) -> bool:
        from ..temporal import Temporal
        if isinstance(other, Temporal):
            return same_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def distance(self, other: Time) -> float:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return distance_timestampset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return distance_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return distance_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return distance_timestampset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def intersection(self, other: datetime) -> datetime:
        ...

    @overload
    def intersection(self, other: Union[Period, PeriodSet, TimestampSet]) -> TimestampSet:
        ...

    def intersection(self, other: Time) -> Union[datetime, TimestampSet]:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return TimestampSet(_inner=intersection_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return TimestampSet(_inner=intersection_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timestamptz_to_datetime(
                intersection_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=intersection_timestampset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def minus(self, other: Time) -> TimestampSet:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return TimestampSet(_inner=minus_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return TimestampSet(_inner=minus_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return TimestampSet(_inner=minus_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=minus_timestampset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def union(self, other: Union[Period, PeriodSet]) -> PeriodSet:
        ...

    @overload
    def union(self, other: Union[datetime, TimestampSet]) -> TimestampSet:
        ...

    def union(self, other: Time) -> Union[PeriodSet, TimestampSet]:
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return PeriodSet(_inner=union_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return TimestampSet(_inner=union_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=union_timestampset_timestampset(self._inner, other._inner))
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
            return timestampset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_ne(self._inner, other._inner)
        return True

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return TimestampSet(string=value)

    def __copy__(self):
        inner_copy = timestampset_copy(self._inner)
        return TimestampSet(_inner=inner_copy)

    def __str__(self):
        return timestampset_out(self._inner)

    def __hash__(self) -> int:
        return timestampset_hash(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_timestampset(self, *args, **kwargs)
