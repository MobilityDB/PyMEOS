from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload, get_args

from dateutil.parser import parse
from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from .period import Period
    from .periodset import PeriodSet
    from .time import Time
    from ..boxes import Box


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
            self._inner = tstzset_in(string)
        else:
            times = [pg_timestamp_in(ts, -1) if isinstance(ts, str) else datetime_to_timestamptz(ts)
                     for ts in timestamp_list]
            self._inner = tstzset_make(times, len(times))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> TimestampSet:
        """
        Returns a `TimestampSet` from its WKB representation in hex-encoded ASCII.
        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`TimestampSet` instance

        MEOS Functions:
            set_from_hexwkb
        """
        return TimestampSet(_inner=(set_from_hexwkb(hexwkb)))

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.
        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            set_as_hexwkb
        """
        return set_as_hexwkb(self._inner, -1)[0]

    def timespan(self) -> timedelta:
        """
        Returns the duration of the time ignoring gaps, i.e. the duration from the
        first timestamp to the last one.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the period

        MEOS Functions:
            period_duration
        """
        return interval_to_timedelta(period_duration(set_to_span(self._inner)))

    def period(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            set_to_span
        """
        from .period import Period
        return Period(_inner=set_to_span(self._inner))

    def to_periodset(self) -> PeriodSet:
        """
        Returns a PeriodSet that contains a Period for each Timestamp in ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            set_to_spanset
        """
        from .periodset import PeriodSet
        return PeriodSet(_inner=set_to_spanset(self._inner))

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            set_num_values
        """
        return set_num_values(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzset_start_timestamp
        """
        return timestamptz_to_datetime(tstzset_start_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzset_end_timestamp
        """
        return timestamptz_to_datetime(tstzset_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzset_timestamp_n
        """
        result = tstzset_timestamp_n(self._inner, n + 1)
        if result is None:
            raise IndexError(f"Index {n} out of range 0 - {self.num_timestamps() - 1}")
        return timestamptz_to_datetime(result)

    def timestamps(self) -> List[datetime]:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            tstzset_timestamps
        """
        tss = tstzset_values(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_timestamps())]

    def shift(self, delta: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that is the result of shifting ``self`` by ``delta``

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift(timedelta(days=2))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            tstzset_shift_tscale
        """
        return self.shift_tscale(shift=delta)

    def tscale(self, duration: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that with the scaled so that the span of ``self`` is ``duration``.

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').tscale(timedelta(days=2))
            >>> 'TimestampSet({2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the span of the new set

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            tstzset_shift_tscale
        """
        return self.shift_tscale(duration=duration)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> TimestampSet:
        """
        Returns a new TimestampSet that is the result of shifting and scaling ``self``.

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift_tscale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the span of the new set

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            tstzset_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        tss = tstzset_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return TimestampSet(_inner=tss)

    def is_adjacent(self, other: Union[Period, PeriodSet, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_adjacent(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_adjacent(Period('[2012-01-02, 2012-01-03]'))
            >>> False  # Both contain bound
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_adjacent(Period('(2012-01-02, 2012-01-03]'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
        adjacent_span_span, adjacent_spanset_span
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return adjacent_span_span(set_to_span(self._inner), other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_spanset_spanset(other._inner, set_to_spanset(self._inner))
        elif isinstance(other, Temporal):
            return adjacent_span_span(set_to_span(self._inner), temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return adjacent_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, TimestampSet, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_contained_in(Period('[2012-01-01, 2012-01-04]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_contained_in(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_contained_in(Period('(2012-01-01, 2012-01-02)'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
        contained_span_span, contained_span_spanset, contained_set_set, contained_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(container, Period):
            return contained_span_span(set_to_span(self._inner), container._inner)
        elif isinstance(container, PeriodSet):
            return contained_span_spanset(set_to_span(self._inner), container._inner)
        elif isinstance(container, TimestampSet):
            return contained_set_set(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_spanset_spanset(set_to_spanset(self._inner), temporal_time(container._inner))
        elif isinstance(container, Box):
            return contained_span_span(set_to_span(self._inner), container.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[datetime, TimestampSet, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').contains(TimestampSet('{2012-01-01}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').contains(TimestampSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_timestampset_timestamp, contains_set_set, contains_spanset_spanset
        """
        from ..temporal import Temporal
        if isinstance(content, datetime):
            return contains_timestampset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_set_set(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_spanset_spanset(set_to_spanset(self._inner), temporal_time(content._inner))
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both share at least an instant

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').overlaps(TimestampSet('{2012-01-02, 2012-01-03}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').overlaps(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').overlaps(Period('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
        overlaps_set_set, overlaps_span_span, overlaps_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return contains_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overlaps_set_set(self._inner, other._inner)
        elif isinstance(other, Period):
            return overlaps_span_span(set_to_span(self._inner), other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_spanset_spanset(set_to_spanset(self._inner), other._inner)
        elif isinstance(other, Temporal):
            return overlaps_spanset_spanset(set_to_spanset(self._inner), temporal_time(other._inner))
        elif isinstance(other, Box):
            return overlaps_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, the first timestamp in ``self``
        is after ``other``.

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(TimestampSet('{2012-01-01}'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
        overbefore_timestamp_timestampset, right_set_set, right_span_span, right_span_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overbefore_timestamp_timestampset(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, TimestampSet):
            return right_set_set(self._inner, other._inner)
        elif isinstance(other, Period):
            return right_span_span(set_to_span(self._inner), other._inner)
        elif isinstance(other, PeriodSet):
            return right_span_spanset(set_to_span(self._inner), other._inner)
        elif isinstance(other, Temporal):
            return right_span_span(set_to_span(self._inner), temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return right_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(TimestampSet('{2012-01-03}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(Period('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(Period('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overafter_timestamp_period, left_span_span, left_span_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overafter_timestamp_period(datetime_to_timestamptz(other), set_to_span(self._inner))
        elif isinstance(other, TimestampSet):
            return left_set_set(self._inner, other._inner)
        elif isinstance(other, Period):
            return left_span_span(set_to_span(self._inner), other._inner)
        elif isinstance(other, PeriodSet):
            return left_span_spanset(set_to_span(self._inner), other._inner)
        elif isinstance(other, Temporal):
            return left_span_span(set_to_span(self._inner), temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return left_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
        overafter_period_timestamp, overright_span_span, overright_span_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overafter_period_timestamp(set_to_span(self._inner), datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overright_set_set(self._inner, other._inner)
        elif isinstance(other, Period):
            return overright_span_span(set_to_span(self._inner), other._inner)
        elif isinstance(other, PeriodSet):
            return overright_span_spanset(set_to_span(self._inner), other._inner)
        elif isinstance(other, Temporal):
            return overright_span_span(set_to_span(self._inner), temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overright_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-03, 2012-01-05}').is_over_or_before(Period('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overbefore_period_timestamp, overleft_span_span, overleft_span_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overbefore_period_timestamp(set_to_span(self._inner), datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overleft_set_set(self._inner, other._inner)
        if isinstance(other, Period):
            return overleft_span_span(set_to_span(self._inner), other._inner)
        if isinstance(other, PeriodSet):
            return overleft_span_spanset(set_to_span(self._inner), other._inner)
        elif isinstance(other, Temporal):
            return overleft_span_span(set_to_span(self._inner), temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overleft_span_span(set_to_span(self._inner), other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def distance(self, other: Union[Time, Temporal, Box]) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_timestampset_timestamp, distance_set_set, distance_span_span, distance_spanset_span
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return timedelta(seconds=distance_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return timedelta(seconds=distance_set_set(self._inner, other._inner))
        elif isinstance(other, Period):
            return timedelta(seconds=distance_span_span(set_to_span(self._inner), other._inner))
        elif isinstance(other, PeriodSet):
            return timedelta(seconds=distance_spanset_span(other._inner, set_to_span(self._inner)))
        elif isinstance(other, Temporal):
            return timedelta(seconds=distance_span_span(set_to_span(self._inner), temporal_to_period(other._inner)))
        elif isinstance(other, get_args(Box)):
            return timedelta(seconds=distance_span_span(set_to_span(self._inner), other.to_period()._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def intersection(self, other: datetime) -> Optional[datetime]:
        ...

    @overload
    def intersection(self, other: TimestampSet) -> Optional[TimestampSet]:
        ...

    @overload
    def intersection(self, other: Union[Period, PeriodSet, Temporal]) -> Optional[PeriodSet]:
        ...

    def intersection(self, other: Union[Time, Temporal]) -> Optional[Time]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
        intersection_set_set, intersection_spanset_span, intersection_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            result = intersection_set_set(self._inner, timestamp_to_tstzset(datetime_to_timestamptz(other)))
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = intersection_set_set(self._inner, other._inner)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = intersection_spanset_span(set_to_spanset(self._inner), other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = intersection_spanset_spanset(set_to_spanset(self._inner), other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def minus(self, other: Union[datetime, TimestampSet]) -> Optional[TimestampSet]:
        ...

    @overload
    def minus(self, other: Union[Period, PeriodSet]) -> Optional[PeriodSet]:
        ...

    def minus(self, other: Time) -> Optional[Time]:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            minus_timestampset_timestamp, minus_set_set, minus_spanset_span, minus_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            result = minus_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = minus_set_set(self._inner, other._inner)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = minus_spanset_span(set_to_spanset(self._inner), other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = minus_spanset_spanset(set_to_spanset(self._inner), other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def union(self, other: Union[datetime, TimestampSet]) -> TimestampSet:
        ...

    @overload
    def union(self, other: Union[Period, PeriodSet]) -> PeriodSet:
        ...

    def union(self, other: Time) -> Union[PeriodSet, TimestampSet]:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            union_timestampset_timestamp, union_set_set, union_spanset_span, union_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            return TimestampSet(_inner=union_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=union_set_set(self._inner, other._inner))
        elif isinstance(other, Period):
            return PeriodSet(_inner=union_spanset_span(set_to_spanset(self._inner), other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_spanset_spanset(set_to_spanset(self._inner), other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def __mul__(self, other):
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
        intersection_set_set, intersection_spanset_span, intersection_spanset_spanset
        """
        return self.intersection(other)

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            union_timestampset_timestamp, union_set_set, union_spanset_span, union_spanset_spanset
        """
        return self.union(other)

    def __sub__(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            minus_timestampset_timestamp, minus_set_set, minus_spanset_span, minus_spanset_spanset
        """
        return self.minus(other)

    def __contains__(self, item):
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').contains(TimestampSet('{2012-01-01}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').contains(TimestampSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_timestampset_timestamp, contains_set_set, contains_spanset_spanset
        """
        return self.contains(item)

    def __eq__(self, other):
        """
        Returns whether ``self`` and ``other`` are equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            set_eq
        """
        if isinstance(other, self.__class__):
            return set_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            set_ne
        """
        if isinstance(other, self.__class__):
            return set_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            set_lt
        """
        if isinstance(other, self.__class__):
            return set_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            set_le
        """
        if isinstance(other, self.__class__):
            return set_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            set_gt
        """
        if isinstance(other, self.__class__):
            return set_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            set_ge
        """
        if isinstance(other, self.__class__):
            return set_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TimestampSet` from a database cursor. Used when automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return TimestampSet(string=value)

    def __copy__(self):
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            set_copy
        """
        inner_copy = set_copy(self._inner)
        return TimestampSet(_inner=inner_copy)

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            set_out
        """
        return set_out(self._inner, 15)

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            set_hash
        """
        return set_hash(self._inner)

    def __repr__(self):
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            set_out
        """
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_timestampset(self, *args, **kwargs)
