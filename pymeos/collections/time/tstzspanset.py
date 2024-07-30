from __future__ import annotations

from datetime import timedelta, datetime
from typing import Optional, Union, List, overload, get_args
from typing import TYPE_CHECKING

from pymeos_cffi import *

from .timecollection import TimeCollection

if TYPE_CHECKING:
    from ...temporal import Temporal
    from ...boxes import Box
    from .tstzspan import TsTzSpan
    from .tstzset import TsTzSet
    from .time import Time

from ..base.spanset import SpanSet


class TsTzSpanSet(SpanSet[datetime], TimeCollection[datetime]):
    """
    Class for representing lists of disjoint tstzspans.

    :class:``TsTzSpanSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TsTzSpanSet(string='{[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01], [2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]}')

    Another possibility is to give a list specifying the composing
    tstzspans, which can be instances  of ``str`` or ``TsTzSpan``. The composing
    tstzspans must be given in increasing order.

        >>> TsTzSpanSet(span_list=['[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'])
        >>> TsTzSpanSet(span_list=[TsTzSpan('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), TsTzSpan('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "tstzspanset"

    _parse_function = tstzspanset_in
    _parse_value_function = lambda tstzspan: (
        tstzspan_in(tstzspan)[0] if isinstance(tstzspan, str) else tstzspan._inner[0]
    )

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            tstzspanset_out
        """
        return tstzspanset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_span(self) -> TsTzSpan:
        """
        Returns a tstzspan that encompasses ``self``.

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            spanset_span
        """
        from .tstzspan import TsTzSpan

        return TsTzSpan(_inner=super().to_span())

    def to_tstzspan(self) -> TsTzSpan:
        """
        Returns a tstzspan that encompasses ``self``.

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            spanset_span
        """
        return self.to_span()

    # ------------------------- Accessors -------------------------------------
    def duration(self, ignore_gaps: Optional[bool] = False) -> timedelta:
        """
        Returns the duration of the tstzspanset. By default, i.e., when the
        second argument is False, the function takes into account the gaps within,
        i.e., returns the sum of the durations of the tstzspans within.
        Otherwise, the function returns the duration of the tstzspanset ignoring
        any gap, i.e., the duration from the lower bound of the first tstzspan to
        the upper bound of the last tstzspan.

        Parameters:
            ignore_gaps: Whether to take into account potential time gaps in
            the tstzspanset.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the tstzspanset

        MEOS Functions:
            tstzspanset_duration
        """
        return interval_to_timedelta(tstzspanset_duration(self._inner, ignore_gaps))

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            tstzspanset_num_timestamps
        """
        return tstzspanset_num_timestamps(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzspanset_start_timestamptz
        """
        return timestamptz_to_datetime(tstzspanset_start_timestamptz(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzspanset_end_timestamptz
        """
        return timestamptz_to_datetime(tstzspanset_end_timestamptz(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzspanset_timestamptz_n
        """
        if n < 0 or n >= self.num_timestamps():
            raise IndexError(f"Index {n} out of bounds")
        return timestamptz_to_datetime(tstzspanset_timestamptz_n(self._inner, n + 1))

    def timestamps(self) -> TsTzSet:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            spanset_timestamptzs
        """
        from .tstzset import TsTzSet

        return TsTzSet(_inner=tstzspanset_timestamps(self._inner))

    def start_span(self) -> TsTzSpan:
        """
        Returns the first tstzspan in ``self``.
        Returns:
            A :class:`TsTzSpan` instance

        MEOS Functions:
            spanset_start_span
        """
        from .tstzspan import TsTzSpan

        return TsTzSpan(_inner=super().start_span())

    def end_span(self) -> TsTzSpan:
        """
        Returns the last tstzspan in ``self``.
        Returns:
            A :class:`TsTzSpan` instance

        MEOS Functions:
            spanset_end_span
        """
        from .tstzspan import TsTzSpan

        return TsTzSpan(_inner=super().end_span())

    def span_n(self, n: int) -> TsTzSpan:
        """
        Returns the n-th tstzspan in ``self``.
        Returns:
            A :class:`TsTzSpan` instance

        MEOS Functions:
            spanset_span_n
        """
        from .tstzspan import TsTzSpan

        return TsTzSpan(_inner=super().span_n(n))

    def spans(self) -> List[TsTzSpan]:
        """
        Returns the list of tstzspans in ``self``.
        Returns:
            A :class:`list[TsTzSpan]` instance

        MEOS Functions:
            spanset_spans
        """
        from .tstzspan import TsTzSpan

        ps = super().spans()
        return [TsTzSpan(_inner=ps[i]) for i in range(self.num_spans())]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> TsTzSpanSet:
        """
        Returns a new :class:`TsTzSpanSet` that is the result of shifting ``self`` by
        ``delta``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'TsTzSpan([2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            tstzspanset_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: timedelta) -> TsTzSpanSet:
        """
        Returns a new tstzspanset that starts as ``self`` but has duration
        ``duration``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').scale(timedelta(days=2))
            >>> 'TsTzSpan([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            tstzspanset_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None
    ) -> TsTzSpanSet:
        """
        Returns a new tstzspanset that starts at ``self`` shifted by ``shift``
        and has duration ``duration``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TsTzSpan([2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            tstzspanset_shift_scale
        """
        assert (
            shift is not None or duration is not None
        ), "shift and scale deltas must not be both None"
        ps = tstzspanset_shift_scale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return TsTzSpanSet(_inner=ps)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is,
        they share a bound but only one of them contains it.

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').is_adjacent(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').is_adjacent(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> False  # Both contain bound
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').is_adjacent(TsTzSpanSet('{[(2012-01-02, 2012-01-03]]}'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_spanset_span, adjacent_spanset_spanset,
            adjacent_spanset_timestamptz, adjacent_tstzspanset_tstzset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return adjacent_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_adjacent(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_adjacent(other.to_tstzspan())
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_contained_in(TsTzSpan('{[2012-01-01, 2012-01-04]}'))
            >>> True
            >>> TsTzSpanSet('{(2012-01-01, 2012-01-02)}').is_contained_in(TsTzSpan('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').is_contained_in(TsTzSpan('{(2012-01-01, 2012-01-02)}'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_spanset_span, contained_spanset_spanset,
            contained_tstzspanset_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(container, datetime):
            return contained_spanset_span(
                self._inner, timestamptz_to_span(datetime_to_timestamptz(container))
            )
        elif isinstance(container, Temporal):
            return self.is_contained_in(container.tstzspan())
        elif isinstance(container, get_args(Box)):
            return self.is_contained_in(container.to_tstzspan())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-04]}').contains(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').contains(TsTzSpanSet('{(2012-01-01, 2012-01-02)}'))
            >>> True
            >>> TsTzSpanSet('{(2012-01-01, 2012-01-02)}').contains(TsTzSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset,
            contains_spanset_timestamptz
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(content, datetime):
            return contains_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(content)
            )
        elif isinstance(content, Temporal):
            return self.contains(content.tstzspan())
        elif isinstance(content, get_args(Box)):
            return self.contains(content.to_tstzspan())
        else:
            return super().contains(content)

    def __contains__(self, item):
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-04]}').contains(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').contains(TsTzSpanSet('{(2012-01-01, 2012-01-02)}'))
            >>> True
            >>> TsTzSpanSet('{(2012-01-01, 2012-01-02)}').contains(TsTzSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset,
            contains_spanset_timestamptz, contains_tstzspanset_tstzset,
            contains_tstzspanset_temporal
        """
        return self.contains(item)

    def overlaps(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').overlaps(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').overlaps(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> False
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').overlaps(TsTzSpanSet('{(2012-01-02, 2012-01-03]}'))
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
            return overlaps_spanset_span(
                self._inner, timestamptz_to_span(datetime_to_timestamptz(other))
            )
        elif isinstance(other, Temporal):
            return self.overlaps(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.overlaps(other.to_tstzspan())
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether the bounding tstzspan of `self` is the same as the
        bounding tstzspan of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if same, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_same`
        """
        return self.to_tstzspan().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').is_left(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').is_left(TsTzSpanSet('{(2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').is_left(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
        before_spanset_timestamptz, left_spanset_span, left_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return before_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_left(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_left(other.to_tstzspan())
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02)}').is_over_or_left(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-01, 2012-01-02]}').is_over_or_left(TsTzSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-03, 2012-01-05]}').is_over_or_left(TsTzSpanSet('{[2012-01-01, 2012-01-04]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_spanset_span, overleft_spanset_spanset,
            overbefore_spanset_timestamptz, overbefore_tstzspanset_tstzset,
            overbefore_tstzspanset_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overbefore_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_over_or_left(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_left(other.to_tstzspan())
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(TsTzSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(TsTzSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(TsTzSpanSet('{[2012-01-01, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset,
            overafter_spanset_timestamptz, overafter_tstzspanset_tstzset,
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overafter_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_over_or_right(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_right(other.to_tstzspan())
        else:
            return super().is_over_or_right(other)

    def is_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``.That is, ``self``
        starts after ``other`` ends.

        Examples:
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_right(TsTzSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> TsTzSpanSet('{(2012-01-02, 2012-01-03]}').is_right(TsTzSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> TsTzSpanSet('{[2012-01-02, 2012-01-03]}').is_right(TsTzSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_spanset_span, right_spanset_spanset,
            overbefore_timestamp_tstzspanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overbefore_timestamptz_spanset(
                datetime_to_timestamptz(other), self._inner
            )
        elif isinstance(other, Temporal):
            return self.is_right(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_right(other.to_tstzspan())
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
            distance_tstzspanset_tstzspan, distance_tstzspanset_tstzspanset,
            distance_spanset_timestamptz, distance_tstzspanset_tstzset
        """
        from .tstzset import TsTzSet
        from .tstzspan import TsTzSpan
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return timedelta(
                seconds=distance_spanset_timestamptz(
                    self._inner, datetime_to_timestamptz(other)
                )
            )
        elif isinstance(other, TsTzSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, TsTzSpan):
            return timedelta(
                seconds=distance_tstzspanset_tstzspan(self._inner, other._inner)
            )
        elif isinstance(other, TsTzSpanSet):
            return timedelta(
                seconds=distance_tstzspanset_tstzspanset(self._inner, other._inner)
            )
        if isinstance(other, Temporal):
            return self.distance(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.distance(other.to_tstzspan())
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: TsTzSpan) -> TsTzSpanSet: ...

    @overload
    def intersection(self, other: TsTzSpanSet) -> TsTzSpanSet: ...

    @overload
    def intersection(self, other: datetime) -> datetime: ...

    def intersection(self, other: Time) -> Union[TsTzSpanSet, datetime, TsTzSet]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_spanset_timestamptz, intersection_spanset_spanset,
            intersection_spanset_span
        """
        if isinstance(other, datetime):
            result = intersection_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
            return timestamptz_to_datetime(result) if result is not None else None
        else:
            result = super().intersection(other)
        return TsTzSpanSet(_inner=result) if result is not None else None

    def __mul__(self, other):
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_spanset_timestamptz, intersection_spanset_spanset,
            intersection_spanset_span
        """
        return self.intersection(other)

    def minus(self, other: Time) -> TsTzSpanSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset, minus_spanset_timestamptz
        """
        if isinstance(other, datetime):
            result = minus_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        else:
            result = super().minus(other)
        return TsTzSpanSet(_inner=result) if result is not None else None

    def __sub__(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset,
            minus_spanset_timestamptz
        """
        return self.minus(other)

    def union(self, other: Time) -> TsTzSpanSet:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_spanset_timestamptz, union_spanset_spanset,
            union_spanset_span
        """
        if isinstance(other, datetime):
            result = union_spanset_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        else:
            result = super().union(other)
        return TsTzSpanSet(_inner=result) if result is not None else None

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_spanset_timestamptz, union_spanset_spanset,
            union_spanset_span
        """
        return self.union(other)

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzspanset(self, *args, **kwargs)
