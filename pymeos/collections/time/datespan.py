from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING, Union, Optional, overload

from _meos_cffi.lib import distance_datespanset_datespan
from dateutil.parser import parse
from pymeos_cffi import (
    adjacent_span_date,
    datespan_in,
    date_to_date_adt,
    pg_date_in,
    datespan_make,
    datespan_out,
    datespan_to_tstzspan,
    date_adt_to_date,
    interval_to_timedelta,
    datespan_duration,
    datespan_upper,
    datespan_lower,
    datespan_shift_scale,
    union_span_date,
    minus_span_date,
    minus_span_span,
    minus_span_spanset,
    intersection_span_date,
    intersection_span_span,
    intersection_spanset_span,
    distance_span_date,
    overafter_span_date,
    after_span_date,
    overbefore_span_date,
    before_span_date,
    contains_span_date,
)

from .timecollection import TimeCollection
from ..base import Span

if TYPE_CHECKING:
    from .dateset import DateSet
    from .datespanset import DateSpanSet
    from .tstzspan import TsTzSpan
    from .time import TimeDate


class DateSpan(Span[date], TimeCollection[date]):
    """
    Class for representing sets of contiguous dates between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``DateSpan`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> DateSpan('(2019-09-08, 2019-09-10)')

    Another possibility is to provide the ``lower`` and ``upper`` named
    parameters (of type str or date), and optionally indicate whether the
    bounds are inclusive or exclusive (by default, the lower bound is inclusive
    and the upper is exclusive):

        >>> DateSpan(lower='2019-09-08', upper='2019-09-10')
        >>> DateSpan(lower='2019-09-08', upper='2019-09-10', lower_inc=False, upper_inc=True)
        >>> DateSpan(lower=parse('2019-09-08'), upper=parse('2019-09-10'), upper_inc=True)
    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "datespan"

    _parse_function = datespan_in
    _parse_value_function = lambda x: (
        pg_date_in(x) if isinstance(x, str) else date_to_date_adt(x)
    )
    _make_function = datespan_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            datespan_out
        """
        return datespan_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> DateSpanSet:
        """
        Returns a :class:`DateSpanSet` set containing ``self``.

        Returns:
            A new :class:`DateSpanSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .datespanset import DateSpanSet

        return DateSpanSet(_inner=super().to_spanset())

    def to_tstzspan(self) -> TsTzSpan:
        """
        Returns a :class:`TsTzSpan equivalent to ``self``.

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            datespan_to_tstzspan
        """
        from .tstzspan import TsTzSpan

        return TsTzSpan(_inner=datespan_to_tstzspan(self._inner))

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> date:
        """
        Returns the lower bound of ``self``.

        Returns:
            The lower bound of the :class:`DateSpan` as a :class:`datetime.datetime`

        MEOS Functions:
            datespan_lower
        """

        return date_adt_to_date(datespan_lower(self._inner))

    def upper(self) -> date:
        """
        Returns the upper bound of ``self``.

        Returns:
            The upper bound of the :class:`DateSpan` as a :class:`datetime.date`

        MEOS Functions:
            datespan_upper
        """
        return date_adt_to_date(datespan_upper(self._inner))

    def duration(self) -> timedelta:
        """
        Returns the duration of ``self``.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the :class:`DateSpan`

        MEOS Functions:
            datespan_duration
        """
        return interval_to_timedelta(datespan_duration(self._inner))

    def duration_in_days(self) -> float:
        """
        Returns the duration of ``self``.

        Returns:
            Returns a `float` representing the duration of the :class:`DateSpan` in
            days

        MEOS Functions:
            span_width
        """
        return self.width()

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: Union[timedelta, int]) -> DateSpan:
        """
        Returns a new :class:`DateSpan` that is the result of shifting ``self`` by
        ``delta``.

        Examples:
            >>> DateSpan('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'DateSpan([2000-01-03, 2000-01-12])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`DateSpan` instance

        MEOS Functions:
            datespan_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: Union[timedelta, int]) -> DateSpan:
        """
        Returns a new :class:`DateSpan` that starts as ``self`` but has
        duration ``duration``.

        Examples:
            >>> DateSpan('[2000-01-01, 2000-01-10]').scale(timedelta(days=2))
            >>> 'DateSpan([2000-01-01, 2000-01-03])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new dateSpan

        Returns:
            A new :class:`DateSpan` instance

        MEOS Functions:
            datespan_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self,
        shift: Union[int, timedelta, None] = None,
        duration: Union[int, timedelta, None] = None,
    ) -> DateSpan:
        """
        Returns a new :class:`DateSpan` that starts at ``self`` shifted by ``shift`` and
        has duration ``duration``

        Examples:
            >>> DateSpan('[2000-01-01, 2000-01-10]').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'DateSpan([2000-01-03, 2000-01-07])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new dateSpan

        Returns:
            A new :class:`DateSpan` instance

        MEOS Functions:
            datespan_shift_scale
        """
        assert (
            shift is not None or duration is not None
        ), "shift and scale deltas must not be both None"

        shift = (
            shift.days
            if isinstance(shift, timedelta)
            else int(shift) if shift is not None else 0
        )
        duration = (
            duration.days
            if isinstance(duration, timedelta)
            else int(duration) if duration is not None else 0
        )

        modified = datespan_shift_scale(
            self._inner, shift, duration, shift != 0, duration != 0
        )
        return DateSpan(_inner=modified)

    # ------------------------- Topological Operations ------------------------

    def is_adjacent(self, other: Union[date, DateSpan, DateSpanSet]) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share
        a bound but only one of them contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_span_date
        """
        if isinstance(other, date):
            return adjacent_span_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_adjacent(other)

    def contains(self, content: TimeDate) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> DateSpan('[2012-01-01, 2012-01-04]').contains(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-01, 2012-01-02]').contains(DateSpan('(2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSpan('(2012-01-01, 2012-01-02)').contains(DateSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_span_date
        """

        if isinstance(content, date):
            return contains_span_date(self._inner, date_to_date_adt(content))
        else:
            return super().contains(content)

    def overlaps(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> DateSpan('[2012-01-01, 2012-01-02]').overlaps(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-01, 2012-01-02)').overlaps(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> False
            >>> DateSpan('[2012-01-01, 2012-01-02)').overlaps(DateSpan('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_span_span, overlaps_span_spanset
        """

        if isinstance(other, date):
            return self.contains(other)
        else:
            return super().overlaps(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> DateSpan('[2012-01-01, 2012-01-02)').is_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-01, 2012-01-02)').is_left(DateSpan('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-01, 2012-01-02]').is_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, before_span_date,
        """

        if isinstance(other, date):
            return before_span_date(date_to_date_adt(other), self._inner)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> DateSpan('[2012-01-01, 2012-01-02)').is_over_or_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-01, 2012-01-02]').is_over_or_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSpan('[2012-01-03, 2012-01-05]').is_over_or_left(DateSpan('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overbefore_span_date,
        """

        if isinstance(other, date):
            return overbefore_span_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self``
        starts after ``other`` ends.

        Examples:
            >>> DateSpan('[2012-01-02, 2012-01-03]').is_right(DateSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSpan('(2012-01-02, 2012-01-03]').is_right(DateSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSpan('[2012-01-02, 2012-01-03]').is_right(DateSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, after_span_date,
        """
        if isinstance(other, date):
            return after_span_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> DateSpan('[2012-01-02, 2012-01-03]').is_over_or_right(DateSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSpan('[2012-01-02, 2012-01-03]').is_over_or_right(DateSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> DateSpan('[2012-01-02, 2012-01-03]').is_over_or_right(DateSpan('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overafter_span_date,
        """

        if isinstance(other, date):
            return overafter_span_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: TimeDate) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_span_date, distance_datespanset_datespan,
            distance_datespanset_datespan
        """
        from .dateset import DateSet
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return timedelta(
                days=distance_span_date(self._inner, date_to_date_adt(other))
            )
        elif isinstance(other, DateSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, DateSpan):
            return timedelta(
                days=distance_datespanset_datespan(self._inner, other._inner)
            )
        elif isinstance(other, DateSpanSet):
            return timedelta(
                days=distance_datespanset_datespan(self._inner, other._inner)
            )
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: date) -> Optional[date]: ...

    @overload
    def intersection(self, other: DateSpan) -> Optional[DateSpan]: ...

    @overload
    def intersection(
        self, other: Union[DateSet, DateSpanSet]
    ) -> Optional[DateSpanSet]: ...

    def intersection(self, other: TimeDate) -> Optional[TimeDate]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`TimeDate` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_span_date
        """
        from .datespanset import DateSpanSet
        from .dateset import DateSet

        if isinstance(other, date):
            result = intersection_span_date(self._inner, date_to_date_adt(other))
            return date_adt_to_date(result) if result is not None else None
        elif isinstance(other, DateSet):
            return self.intersection(other.to_spanset())
        elif isinstance(other, DateSpan):
            result = intersection_span_span(self._inner, other._inner)
            return DateSpan(_inner=result) if result is not None else None
        elif isinstance(other, DateSpanSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return DateSpanSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: TimeDate) -> DateSpanSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`DateSpanSet` instance.

        MEOS Functions:
            minus_span_date, minus_span_spanset, minus_span_span
        """
        from .datespanset import DateSpanSet
        from .dateset import DateSet

        if isinstance(other, date):
            result = minus_span_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSet):
            return self.minus(other.to_spanset())
        elif isinstance(other, DateSpan):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, DateSpanSet):
            result = minus_span_spanset(self._inner, other._inner)
        else:
            result = super().minus(other)
        return DateSpanSet(_inner=result) if result is not None else None

    def union(self, other: TimeDate) -> DateSpanSet:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`DateSpanSet` instance.

        MEOS Functions:
            union_span_date, union_spanset_span, union_span_span
        """
        from .datespanset import DateSpanSet
        from .dateset import DateSet

        if isinstance(other, date):
            result = union_span_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSet):
            result = super().union(other.to_spanset())
        elif isinstance(other, DateSpan):
            result = super().union(other)
        elif isinstance(other, DateSpanSet):
            result = super().union(other)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return DateSpanSet(_inner=result) if result is not None else None

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzspan(self.to_tstzspan(), *args, **kwargs)
