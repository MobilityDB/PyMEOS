from __future__ import annotations

from datetime import timedelta, datetime
from typing import Optional, Union, List, overload, get_args
from typing import TYPE_CHECKING

from pymeos_cffi import *

from .time_collection import TimeCollection

if TYPE_CHECKING:
    from ...temporal import Temporal
    from ...boxes import Box
    from .period import Period
    from .timestampset import TimestampSet
    from .time import Time

from ..base.spanset import SpanSet


class PeriodSet(SpanSet[datetime], TimeCollection):
    """
    Class for representing lists of disjoint periods.

    ``PeriodSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> PeriodSet(string='{[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01], [2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]}')

    Another possibility is to give a list specifying the composing
    periods, which can be instances  of ``str`` or ``Period``. The composing
    periods must be given in increasing order.

        >>> PeriodSet(period_list=['[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'])
        >>> PeriodSet(period_list=[Period('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), Period('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')])

    """

    __slots__ = ['_inner']

    _parse_function = periodset_in
    _parse_value_function = lambda period: period_in(period)[0] if isinstance(period, str) else period._inner[0]

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            periodset_out
        """
        return periodset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_span(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            spanset_span
        """
        from .period import Period
        return Period(_inner=super().to_span())

    def to_period(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            spanset_span
        """
        return self.to_span()

    # ------------------------- Accessors -------------------------------------
    def duration(self, ignore_gaps: Optional[bool] = False) -> timedelta:
        """
        Returns the duration of the periodset. By default, i.e., when the
        second argument is False, the function takes into account the gaps within,
        i.e., returns the sum of the durations of the periods within.
        Otherwise, the function returns the duration of the periodset ignoring
        any gap, i.e., the duration from the lower bound of the first period to
        the upper bound of the last period.

        Parameters:
            ignore_gaps: Whether to take into account potential time gaps in the periodset.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the periodset

        MEOS Functions:
            periodset_duration
        """
        return interval_to_timedelta(periodset_duration(self._inner, ignore_gaps))

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            periodset_num_timestamps
        """
        return periodset_num_timestamps(self._inner)

    def start_element(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_start_timestamp
        """
        return timestamptz_to_datetime(periodset_start_timestamp(self._inner))

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_start_timestamp
        """
        return self.start_element()

    def end_element(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_end_timestamp
        """
        return timestamptz_to_datetime(periodset_end_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_end_timestamp
        """
        return self.end_element()

    def element_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_timestamp_n
        """
        return timestamptz_to_datetime(periodset_timestamp_n(self._inner, n + 1))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_timestamp_n
        """
        return self.element_n(n)

    def elements(self) -> List[datetime]:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            periodset_timestamps
        """
        ts, count = periodset_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    def timestamps(self) -> List[datetime]:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            periodset_timestamps
        """
        return self.elements()

    def num_spans(self) -> int:
        """
        Returns the number of periods in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            spanset_num_spans
        """
        return spanset_num_spans(self._inner)

    def num_periods(self) -> int:
        """
        Returns the number of periods in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            spanset_num_spans
        """
        return self.num_spans()

    def start_span(self) -> Period:
        """
        Returns the first period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_start_span
        """
        from .period import Period
        return Period(_inner=super().start_span())

    def start_period(self) -> Period:
        """
        Returns the first period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_start_span
        """
        return self.start_span()

    def end_span(self) -> Period:
        """
        Returns the last period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_end_span
        """
        from .period import Period
        return Period(_inner=super().end_span())

    def end_period(self) -> Period:
        """
        Returns the last period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_end_span
        """
        return self.end_span()

    def span_n(self, n: int) -> Period:
        """
        Returns the n-th period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_span_n
        """
        from .period import Period
        return Period(_inner=super().span_n(n))

    def period_n(self, n: int) -> Period:
        """
        Returns the n-th period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_span_n
        """
        return self.span_n(n)

    def spans(self) -> List[Period]:
        """
        Returns the list of periods in ``self``.
        Returns:
            A :class:`list[Period]` instance

        MEOS Functions:
            spanset_spans
        """
        from .period import Period
        ps = super().spans()
        return [Period(_inner=ps[i]) for i in range(self.num_spans())]

    def periods(self) -> List[Period]:
        """
        Returns the list of periods in ``self``.
        Returns:
            A :class:`list[Period]` instance

        MEOS Functions:
            spanset_spans
        """
        return self.spans()

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> PeriodSet:
        """
        Returns a new periodset that is the result of shifting ``self`` by ``delta``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            periodset_shift_tscale
        """
        return self.shift_tscale(shift=delta)

    def tscale(self, duration: timedelta) -> PeriodSet:
        """
        Returns a new periodset that starts as ``self`` but has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').tscale(timedelta(days=2))
            >>> 'Period([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            periodset_shift_tscale
        """
        return self.shift_tscale(duration=duration)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> PeriodSet:
        """
        Returns a new periodset that starts at ``self`` shifted by ``shift`` and has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift_tscale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            periodset_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        ps = periodset_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return PeriodSet(_inner=ps)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_adjacent(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_adjacent(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> False  # Both contain bound
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_adjacent(PeriodSet('{[(2012-01-02, 2012-01-03]]}'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_spanset_span, adjacent_spanset_spanset, adjacent_periodset_timestamp,
            adjacent_periodset_timestampset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return adjacent_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_adjacent(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_adjacent(other.to_period())
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_contained_in(Period('{[2012-01-01, 2012-01-04]}'))
            >>> True
            >>> PeriodSet('{(2012-01-01, 2012-01-02)}').is_contained_in(Period('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_contained_in(Period('{(2012-01-01, 2012-01-02)}'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_spanset_span, contained_spanset_spanset, contained_periodset_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(container, datetime):
            return contained_spanset_span(self._inner, timestamp_to_period(datetime_to_timestamptz(container)))
        elif isinstance(container, Temporal):
            return self.is_contained_in(container.period())
        elif isinstance(container, get_args(Box)):
            return self.is_contained_in(container.to_period())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-04]}').contains(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').contains(PeriodSet('{(2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{(2012-01-01, 2012-01-02)}').contains(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
        contains_spanset_span, contains_spanset_spanset, contains_periodset_timestamp
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(content, datetime):
            return contains_periodset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, Temporal):
            return self.contains(content.period())
        elif isinstance(content, get_args(Box)):
            return self.contains(content.to_period())
        else:
            return super().contains(content)

    def __contains__(self, item):
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-04]}').contains(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').contains(PeriodSet('{(2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{(2012-01-01, 2012-01-02)}').contains(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset, contains_periodset_timestamp,
            contains_periodset_timestampset, contains_periodset_temporal
        """
        return self.contains(item)

    def overlaps(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both share at least an instant

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').overlaps(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').overlaps(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> False
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').overlaps(PeriodSet('{(2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_spanset_span, overlaps_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overlaps_spanset_span(self._inner, timestamp_to_period(datetime_to_timestamptz(other)))
        elif isinstance(other, Temporal):
            return self.overlaps(other.period())
        elif isinstance(other, get_args(Box)):
            return self.overlaps(other.to_period())
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether the bounding period of `self` is the same as the bounding period of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if same, False otherwise.

        See Also:
            :meth:`Period.is_same`
        """
        return self.to_period().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_left(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_left(PeriodSet('{(2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_left(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
        before_periodset_timestamp, left_spanset_span, left_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return before_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_left(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_left(other.to_period())
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_over_or_left(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_over_or_left(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-03, 2012-01-05]}').is_over_or_left(PeriodSet('{[2012-01-01, 2012-01-04]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_spanset_span, overleft_spanset_spanset, overbefore_periodset_timestamp,
            overbefore_periodset_timestampset, overbefore_periodset_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overbefore_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_over_or_left(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_left(other.to_period())
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(PeriodSet('{[2012-01-01, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset, overafter_periodset_timestamp,
            overafter_periodset_timestampset,
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overafter_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_over_or_right(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_right(other.to_period())
        else:
            return super().is_over_or_right(other)

    def is_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``.That is, ``self`` starts after ``other`` ends.

        Examples:
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_right(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{(2012-01-02, 2012-01-03]}').is_right(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_right(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_spanset_span, right_spanset_spanset, overbefore_timestamp_periodset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overbefore_timestamp_periodset(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, Temporal):
            return self.is_right(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_right(other.to_period())
        else:
            return super().is_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[Time, Box, Temporal]) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_periodset_period, distance_periodset_periodset, distance_periodset_timestamp,
            distance_periodset_timestampset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return timedelta(seconds=distance_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        if isinstance(other, Temporal):
            return self.distance(other.period())
        elif isinstance(other, get_args(Box)):
            return self.distance(other.to_period())
        else:
            return timedelta(seconds=super().distance(other))

    # ------------------------- Set Operations --------------------------------
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
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
        intersection_periodset_timestamp, intersection_spanset_spanset, intersection_spanset_span
        """
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            result = intersection_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = super().intersection(other)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = super().intersection(other)
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = super().intersection(other)
            return PeriodSet(_inner=result) if result is not None else None
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
        intersection_periodset_timestamp, intersection_spanset_spanset, intersection_spanset_span
        """
        return self.intersection(other)

    def minus(self, other: Time) -> PeriodSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        minus_spanset_span, minus_spanset_spanset, minus_periodset_timestamp
        """
        if isinstance(other, datetime):
            result = minus_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        else:
            result = super().minus(other)
        return PeriodSet(_inner=result) if result is not None else None

    def __sub__(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        minus_spanset_span, minus_spanset_spanset, minus_periodset_timestamp
        """
        return self.minus(other)

    def union(self, other: Time) -> PeriodSet:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        union_periodset_timestamp, union_spanset_spanset, union_spanset_span
        """
        if isinstance(other, datetime):
            result = union_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        else:
            result = super().union(other)
        return PeriodSet(_inner=result) if result is not None else None

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        union_periodset_timestamp, union_spanset_spanset, union_spanset_span
        """
        return self.union(other)

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter
        return TimePlotter.plot_periodset(self, *args, **kwargs)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`PeriodSet` from a database cursor. Used when automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return PeriodSet(string=value)
