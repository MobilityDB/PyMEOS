from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Union, overload, TYPE_CHECKING, get_args

from dateutil.parser import parse
from pymeos_cffi import *

from .timecollection import TimeCollection
from ..base.span import Span

if TYPE_CHECKING:
    from ...temporal import Temporal
    from ...boxes import Box
    from .tstzspanset import TsTzSpanSet
    from .time import Time
    from .tstzset import TsTzSet


class TsTzSpan(Span[datetime], TimeCollection[datetime]):
    """
    Class for representing sets of contiguous timestamps between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``TsTzSpan`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TsTzSpan('(2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01)')

    Another possibility is to provide the ``lower`` and ``upper`` named
    parameters (of type str or datetime), and optionally indicate whether the
    bounds are inclusive or exclusive (by default, the lower bound is inclusive
    and the upper is exclusive):

        >>> TsTzSpan(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01')
        >>> TsTzSpan(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01', lower_inc=False, upper_inc=True)
        >>> TsTzSpan(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'), upper_inc=True)
    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "tstzspan"

    _parse_function = tstzspan_in
    _parse_value_function = lambda x: (
        pg_timestamptz_in(x, -1) if isinstance(x, str) else datetime_to_timestamptz(x)
    )
    _make_function = tstzspan_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            tstzspan_out
        """
        return tstzspan_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> TsTzSpanSet:
        """
        Returns a tstzspan set containing ``self``.

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .tstzspanset import TsTzSpanSet

        return TsTzSpanSet(_inner=super().to_spanset())

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> datetime:
        """
        Returns the lower bound of a tstzspan

        Returns:
            The lower bound of the tstzspan as a :class:`datetime.datetime`

        MEOS Functions:
            tstzspan_lower
        """

        return timestamptz_to_datetime(tstzspan_lower(self._inner))

    def upper(self) -> datetime:
        """
        Returns the upper bound of a tstzspan

        Returns:
            The upper bound of the tstzspan as a :class:`datetime.datetime`

        MEOS Functions:
            tstzspan_upper
        """
        return timestamptz_to_datetime(tstzspan_upper(self._inner))

    def duration(self) -> timedelta:
        """
        Returns the duration of the tstzspan.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the tstzspan

        MEOS Functions:
            tstzspan_duration
        """
        return interval_to_timedelta(tstzspan_duration(self._inner))

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> TsTzSpan:
        """
        Returns a new tstzspan that is the result of shifting ``self`` by ``delta``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'TsTzSpan([2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            tstzspan_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: timedelta) -> TsTzSpan:
        """
        Returns a new tstzspan that starts as ``self`` but has duration ``duration``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').scale(timedelta(days=2))
            >>> 'TsTzSpan([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            tstzspan_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None
    ) -> TsTzSpan:
        """
        Returns a new tstzspan that starts at ``self`` shifted by ``shift`` and
        has duration ``duration``

        Examples:
            >>> TsTzSpan('[2000-01-01, 2000-01-10]').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TsTzSpan([2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            tstzspan_shift_scale
        """
        assert (
            shift is not None or duration is not None
        ), "shift and scale deltas must not be both None"
        modified = tstzspan_shift_scale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return TsTzSpan(_inner=modified)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is,
        they share a bound but only one of them contains it.

        Examples:
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').is_adjacent(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').is_adjacent(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> False  # Both contain bound
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').is_adjacent(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_span_timestamptz,
            adjacent_span_tstzset, adjacent_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return adjacent_span_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return adjacent_span_span(self._inner, temporal_to_tstzspan(other._inner))
        elif isinstance(other, get_args(Box)):
            return adjacent_span_span(self._inner, other.to_tstzspan()._inner)
        else:
            return super().is_adjacent(other)

    def is_contained_in(
        self, container: Union[TsTzSpan, TsTzSpanSet, Box, Temporal]
    ) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_contained_in(TsTzSpan('[2012-01-01, 2012-01-04]'))
            >>> True
            >>> TsTzSpan('(2012-01-01, 2012-01-02)').is_contained_in(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').is_contained_in(TsTzSpan('(2012-01-01, 2012-01-02)'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_span_span, contained_span_spanset, contained_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(container, Temporal):
            return self.is_contained_in(container.tstzspan())
        elif isinstance(container, get_args(Box)):
            return self.is_contained_in(container.to_tstzspan())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TsTzSpan('[2012-01-01, 2012-01-04]').contains(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').contains(TsTzSpan('(2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSpan('(2012-01-01, 2012-01-02)').contains(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_span_timestamptz,
            contains_span_tstzset, contains_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(content, datetime):
            return contains_span_timestamptz(
                self._inner, datetime_to_timestamptz(content)
            )
        elif isinstance(content, Temporal):
            return self.contains(content.tstzspan())
        elif isinstance(content, get_args(Box)):
            return self.contains(content.to_tstzspan())
        else:
            return super().contains(content)

    def overlaps(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').overlaps(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').overlaps(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> False
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').overlaps(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_span_span, overlaps_span_spanset,
            overlaps_span_tstzset, overlaps_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overlaps_span_span(
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
        Returns whether ``self`` and the bounding tstzspan of ``other`` is the same.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, Temporal):
            return self.is_same(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_same(other.to_tstzspan())
        elif isinstance(other, datetime):
            return span_eq(
                self._inner, timestamptz_to_span(datetime_to_timestamptz(other))
            )
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').is_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').is_left(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').is_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, before_span_timestamptz,
            before_span_tstzset, before_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overafter_timestamptz_span(
                datetime_to_timestamptz(other), self._inner
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
            >>> TsTzSpan('[2012-01-01, 2012-01-02)').is_over_or_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-01, 2012-01-02]').is_over_or_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSpan('[2012-01-03, 2012-01-05]').is_over_or_left(TsTzSpan('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overbefore_span_timestamptz,
            overbefore_span_tstzset, overbefore_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overbefore_span_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_over_or_left(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_left(other.to_tstzspan())
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self``
        starts after ``other`` ends.

        Examples:
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_right(TsTzSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSpan('(2012-01-02, 2012-01-03]').is_right(TsTzSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_right(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, after_span_timestamptz,
            after_span_tstzset, after_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overbefore_timestamptz_span(
                datetime_to_timestamptz(other), self._inner
            )
        elif isinstance(other, Temporal):
            return self.is_right(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_right(other.to_tstzspan())
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TsTzSpan('[2012-01-02, 2012-01-03]').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overafter_span_timestamptz,
            overafter_span_tstzset, overafter_span_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overafter_span_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
        elif isinstance(other, Temporal):
            return self.is_over_or_right(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_right(other.to_tstzspan())
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[Time, Box, Temporal]) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_span_timestamptz, distance_tstzspan_tstzspan,
            distance_tstzspanset_tstzspan
        """
        from .tstzset import TsTzSet
        from .tstzspanset import TsTzSpanSet
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return timedelta(
                seconds=distance_span_timestamptz(
                    self._inner, datetime_to_timestamptz(other)
                )
            )
        elif isinstance(other, TsTzSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, TsTzSpan):
            return timedelta(
                seconds=distance_tstzspan_tstzspan(self._inner, other._inner)
            )
        elif isinstance(other, TsTzSpanSet):
            return timedelta(
                seconds=distance_tstzspanset_tstzspan(other._inner, self._inner)
            )
        elif isinstance(other, Temporal):
            return self.distance(other.tstzspan())
        elif isinstance(other, get_args(Box)):
            return self.distance(other.to_tstzspan())
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: datetime) -> Optional[datetime]: ...

    @overload
    def intersection(self, other: TsTzSpan) -> Optional[TsTzSpan]: ...

    @overload
    def intersection(
        self, other: Union[TsTzSet, TsTzSpanSet]
    ) -> Optional[TsTzSpanSet]: ...

    def intersection(self, other: Time) -> Optional[Time]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_span_timestamptz
        """
        from .tstzspanset import TsTzSpanSet
        from .tstzset import TsTzSet

        if isinstance(other, datetime):
            result = intersection_span_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TsTzSet):
            return self.intersection(other.to_tstzspanset())
        elif isinstance(other, TsTzSpan):
            result = intersection_span_span(self._inner, other._inner)
            return TsTzSpan(_inner=result) if result is not None else None
        elif isinstance(other, TsTzSpanSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return TsTzSpanSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: Time) -> TsTzSpanSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`TsTzSpanSet` instance.

        MEOS Functions:
            minus_span_timestamptz, minus_span_spanset, minus_span_span
        """
        from .tstzspanset import TsTzSpanSet
        from .tstzset import TsTzSet

        if isinstance(other, datetime):
            result = minus_span_timestamptz(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TsTzSet):
            return self.minus(other.to_tstzspanset())
        elif isinstance(other, TsTzSpan):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, TsTzSpanSet):
            result = minus_span_spanset(self._inner, other._inner)
        else:
            result = super().minus(other)
        return TsTzSpanSet(_inner=result) if result is not None else None

    def union(self, other: Time) -> TsTzSpanSet:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_span_timestamptz, union_spanset_span, union_span_span
        """
        from .tstzspanset import TsTzSpanSet
        from .tstzset import TsTzSet

        if isinstance(other, datetime):
            result = union_span_timestamptz(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TsTzSet):
            result = super().union(other)
        elif isinstance(other, TsTzSpan):
            result = super().union(other)
        elif isinstance(other, TsTzSpanSet):
            result = super().union(other)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return TsTzSpanSet(_inner=result) if result is not None else None

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzspan(self, *args, **kwargs)
