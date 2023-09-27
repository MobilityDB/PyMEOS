from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Union, overload, TYPE_CHECKING, get_args

from dateutil.parser import parse
from pymeos_cffi import *

from .time_collection import TimeCollection
from ..base.span import Span

if TYPE_CHECKING:
    from ...temporal import Temporal
    from ...boxes import Box
    from .periodset import PeriodSet
    from .time import Time
    from .timestampset import TimestampSet


class Period(Span[datetime], TimeCollection):
    """
    Class for representing sets of contiguous timestamps between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``Period`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> Period('(2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01)')

    Another possibility is to provide the ``lower`` and ``upper`` named parameters (of type str or datetime), and
    optionally indicate whether the bounds are inclusive or exclusive (by default, the lower bound is inclusive and the
    upper is exclusive):

        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01')
        >>> Period(lower='2019-09-08 00:00:00+01', upper='2019-09-10 00:00:00+01', lower_inc=False, upper_inc=True)
        >>> Period(lower=parse('2019-09-08 00:00:00+01'), upper=parse('2019-09-10 00:00:00+01'), upper_inc=True)
    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'tstzspan'

    _parse_function = period_in
    _parse_value_function = lambda x: pg_timestamptz_in(x, -1) if isinstance(x, str) else datetime_to_timestamptz(x)
    _make_function = period_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            period_out
        """
        return period_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> PeriodSet:
        """
        Returns a period set containing ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .periodset import PeriodSet
        return PeriodSet(_inner=super().to_spanset())

    def to_periodset(self) -> PeriodSet:
        """
        Returns a period set containing ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            span_to_spanset
        """
        return self.to_spanset()

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> datetime:
        """
        Returns the lower bound of a period

        Returns:
            The lower bound of the period as a :class:`datetime.datetime`

        MEOS Functions:
            period_lower
        """

        return timestamptz_to_datetime(period_lower(self._inner))

    def upper(self) -> datetime:
        """
        Returns the upper bound of a period

        Returns:
            The upper bound of the period as a :class:`datetime.datetime`

        MEOS Functions:
            period_upper
        """
        return timestamptz_to_datetime(period_upper(self._inner))

    def duration(self) -> timedelta:
        """
        Returns the duration of the period.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the period

        MEOS Functions:
            period_duration
        """
        return interval_to_timedelta(period_duration(self._inner))

    def duration_in_seconds(self) -> float:
        """
        Returns the duration of the period.

        Returns:
            Returns a `float` representing the duration of the period in seconds

        MEOS Functions:
            span_width
        """
        return self.width()

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> Period:
        """
        Returns a new period that is the result of shifting ``self`` by ``delta``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            period_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: timedelta) -> Period:
        """
        Returns a new period that starts as ``self`` but has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').scale(timedelta(days=2))
            >>> 'Period([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            period_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> Period:
        """
        Returns a new period that starts at ``self`` shifted by ``shift`` and has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            period_shift_scale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        modified = period_shift_scale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return Period(_inner=modified)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

        Examples:
            >>> Period('[2012-01-01, 2012-01-02)').is_adjacent(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_adjacent(Period('[2012-01-02, 2012-01-03]'))
            >>> False  # Both contain bound
            >>> Period('[2012-01-01, 2012-01-02)').is_adjacent(Period('(2012-01-02, 2012-01-03]'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_period_timestamp,
            adjacent_period_timestampset, adjacent_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return adjacent_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return adjacent_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return adjacent_span_span(self._inner, other.to_period()._inner)
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[Period, PeriodSet, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]').is_contained_in(Period('[2012-01-01, 2012-01-04]'))
            >>> True
            >>> Period('(2012-01-01, 2012-01-02)').is_contained_in(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_contained_in(Period('(2012-01-01, 2012-01-02)'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_span_span, contained_span_spanset, contained_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(container, Temporal):
            return self.is_contained_in(container.period())
        elif isinstance(container, Box):
            return self.is_contained_in(container.to_period())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> Period('[2012-01-01, 2012-01-04]').contains(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').contains(Period('(2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('(2012-01-01, 2012-01-02)').contains(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_period_timestamp,
            contains_period_timestampset, contains_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(content, datetime):
            return contains_period_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, Temporal):
            return self.contains(content.period())
        elif isinstance(content, get_args(Box)):
            return self.contains(content.to_period())
        else:
            return super().contains(content)

    def overlaps(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both share at least an instant

        Examples:
            >>> Period('[2012-01-01, 2012-01-02]').overlaps(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02)').overlaps(Period('[2012-01-02, 2012-01-03]'))
            >>> False
            >>> Period('[2012-01-01, 2012-01-02)').overlaps(Period('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_span_span, overlaps_span_spanset, overlaps_period_timestampset,
            overlaps_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overlaps_span_span(self._inner, timestamp_to_period(datetime_to_timestamptz(other)))
        elif isinstance(other, Temporal):
            return self.overlaps(other.period())
        elif isinstance(other, get_args(Box)):
            return self.overlaps(other.to_period())
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` and the bounding period of ``other`` is the same.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, Temporal):
            return self.is_same(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_same(other.to_period())
        elif isinstance(other, datetime):
            return span_eq(self._inner, timestamp_to_period(datetime_to_timestamptz(other)))
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> Period('[2012-01-01, 2012-01-02)').is_left(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02)').is_left(Period('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_left(Period('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, before_period_timestamp,
            before_period_timestampset, before_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overafter_timestamp_period(datetime_to_timestamptz(other), self._inner)
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
            >>> Period('[2012-01-01, 2012-01-02)').is_over_or_left(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_over_or_left(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-03, 2012-01-05]').is_over_or_left(Period('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overbefore_period_timestamp,
            overbefore_period_timestampset, overbefore_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overbefore_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_over_or_left(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_left(other.to_period())
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self`` starts after ``other`` ends.

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]').is_right(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('(2012-01-02, 2012-01-03]').is_right(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_right(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, after_period_timestamp,
            after_period_timestampset, after_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overbefore_timestamp_period(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, Temporal):
            return self.is_right(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_right(other.to_period())
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[Time, Box, Temporal]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_right(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_right(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_right(Period('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overafter_period_timestamp,
            overafter_period_timestampset, overafter_period_temporal
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overafter_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.is_over_or_right(other.period())
        elif isinstance(other, get_args(Box)):
            return self.is_over_or_right(other.to_period())
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
            distance_span_span, distance_spanset_span, distance_period_timestamp
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return timedelta(seconds=distance_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, Temporal):
            return self.distance(other.period())
        elif isinstance(other, get_args(Box)):
            return self.distance(other.to_period())
        else:
            return timedelta(seconds=super().distance(other))

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: datetime) -> Optional[datetime]:
        ...

    @overload
    def intersection(self, other: Period) -> Optional[Period]:
        ...

    @overload
    def intersection(self, other: Union[TimestampSet, PeriodSet]) -> Optional[PeriodSet]:
        ...

    def intersection(self, other: Time) -> Optional[Time]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
        intersection_span_span, intersection_spanset_span, intersection_period_timestamp
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            result = intersection_period_timestamp(self._inner, datetime_to_timestamptz(other))
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TimestampSet):
            return self.intersection(other.to_periodset())
        elif isinstance(other, Period):
            result = intersection_span_span(self._inner, other._inner)
            return Period(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return PeriodSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: Time) -> PeriodSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            minus_period_timestamp, minus_span_spanset, minus_span_span
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            result = minus_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return self.minus(other.to_periodset())
        elif isinstance(other, Period):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = minus_span_spanset(self._inner, other._inner)
        else:
            super().minus(other)
        return PeriodSet(_inner=result) if result is not None else None

    def union(self, other: Time) -> PeriodSet:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        union_period_timestamp, union_spanset_span, union_span_span
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            result = union_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = super().union(other)
        elif isinstance(other, Period):
            result = super().union(other)
        elif isinstance(other, PeriodSet):
            result = super().union(other)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return PeriodSet(_inner=result) if result is not None else None

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter
        return TimePlotter.plot_period(self, *args, **kwargs)
