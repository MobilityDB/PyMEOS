from __future__ import annotations

from datetime import timedelta, date
from typing import Optional, Union, List, overload
from typing import TYPE_CHECKING

from _meos_cffi.lib import (
    distance_datespanset_datespan,
    distance_datespanset_datespanset,
)
from pymeos_cffi import (
    datespanset_in,
    datespan_in,
    datespanset_out,
    datespanset_to_tstzspanset,
    interval_to_timedelta,
    datespanset_duration,
    datespanset_num_dates,
    date_adt_to_date,
    datespanset_start_date,
    datespanset_end_date,
    datespanset_date_n,
    datespanset_dates,
    datespanset_shift_scale,
    date_to_date_adt,
    contains_spanset_date,
    before_spanset_date,
    overbefore_spanset_date,
    overafter_spanset_date,
    after_spanset_date,
    distance_spanset_date,
    intersection_spanset_date,
    minus_spanset_date,
    union_spanset_date,
)

from .timecollection import TimeCollection
from ..base.spanset import SpanSet

if TYPE_CHECKING:
    from .tstzspan import TsTzSpan
    from .tstzspanset import TsTzSpanSet
    from .datespan import DateSpan
    from .time import TimeDate


class DateSpanSet(SpanSet[date], TimeCollection[date]):
    """
    Class for representing lists of disjoint tstzspans.

    :class:``DateSpanSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> DateSpanSet(string='{[2019-09-08, 2019-09-10], [2019-09-11, 2019-09-12]}')

    Another possibility is to give a list specifying the composing
    tstzspans, which can be instances  of :class:``str`` or :class:``DateSpan``.
    The composing datespans must be given in increasing order.

        >>> DateSpanSet(span_list=['[2019-09-08, 2019-09-10]', '[2019-09-11, 2019-09-12'])
        >>> DateSpanSet(span_list=[TsTzSpan('[2019-09-08, 2019-09-10]'), TsTzSpan('[2019-09-11, 2019-09-12]')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "dateSpanSet"

    _parse_function = datespanset_in
    _parse_value_function = lambda tstzspan: (
        datespan_in(tstzspan)[0] if isinstance(tstzspan, str) else tstzspan._inner[0]
    )

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            datespanset_out
        """
        return datespanset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_span(self) -> DateSpan:
        """
        Returns a :class:`DateSpan` that encompasses ``self``.

        Returns:
            A new :class:`DateSpan` instance

        MEOS Functions:
            spanset_span
        """
        from .dateset import DateSpan

        return DateSpan(_inner=super().to_span())

    def to_tstzspanset(self) -> TsTzSpanSet:
        """
        Returns a :class:`TsTzSpanSet` equivalent to ``self``.

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            datespanset_to_tstzspanset
        """
        from .tstzspanset import TsTzSpanSet

        return TsTzSpanSet(_inner=datespanset_to_tstzspanset(self._inner))

    # ------------------------- Accessors -------------------------------------
    def duration(self, ignore_gaps: Optional[bool] = False) -> timedelta:
        """
        Returns the duration of ``self``. By default, i.e., when ``ignore_gaps`` is
        ``False``, the function takes into account the gaps between the
        spans, i.e., returns the sum of the durations of the composing datespans.
        Otherwise, the function returns the duration of ``self`` ignoring
        any gap, i.e., the duration from the lower bound of the first datespan to
        the upper bound of the last datespan.

        Parameters:
            ignore_gaps: Whether to take into account potential time gaps in
            ``self``.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the datespanset

        MEOS Functions:
            datespanset_duration
        """
        return interval_to_timedelta(datespanset_duration(self._inner, ignore_gaps))

    def num_dates(self) -> int:
        """
        Returns the number of dates in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            datespanset_num_dates
        """
        return datespanset_num_dates(self._inner)

    def start_date(self) -> date:
        """
        Returns the first date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            datespanset_start_date
        """
        return date_adt_to_date(datespanset_start_date(self._inner))

    def end_date(self) -> date:
        """
        Returns the last date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            datespanset_end_date
        """
        return date_adt_to_date(datespanset_end_date(self._inner))

    def date_n(self, n: int) -> date:
        """
        Returns the n-th date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            datespanset_date_n
        """
        if n < 0 or n >= self.num_dates():
            raise IndexError(f"Index {n} out of bounds")
        return date_adt_to_date(datespanset_date_n(self._inner, n + 1))

    def dates(self) -> List[date]:
        """
        Returns the list of distinct dates in ``self``.
        Returns:
            A :class:`list[date]` instance

        MEOS Functions:
            datespanset_dates
        """
        ds, count = datespanset_dates(self._inner)
        return [date_adt_to_date(ds[i]) for i in range(count)]

    def start_span(self) -> DateSpan:
        """
        Returns the first :class:`DateSpan` in ``self``.
        Returns:
            A :class:`DateSpan` instance

        MEOS Functions:
            spanset_start_span
        """
        from .datespan import DateSpan

        return DateSpan(_inner=super().start_span())

    def end_span(self) -> DateSpan:
        """
        Returns the last :class:`DateSpan` in ``self``.
        Returns:
            A :class:`DateSpan` instance

        MEOS Functions:
            spanset_end_span
        """
        from .datespan import DateSpan

        return DateSpan(_inner=super().end_span())

    def span_n(self, n: int) -> DateSpan:
        """
        Returns the n-th :class:`DateSpan` in ``self``.
        Returns:
            A :class:`DateSpan` instance

        MEOS Functions:
            spanset_span_n
        """
        from .datespan import DateSpan

        return DateSpan(_inner=super().span_n(n))

    def spans(self) -> List[DateSpan]:
        """
        Returns the list of :class:`DateSpan` in ``self``.
        Returns:
            A :class:`list[DateSpan]` instance

        MEOS Functions:
            spanset_spans
        """
        from .datespan import DateSpan

        ps = super().spans()
        return [DateSpan(_inner=ps[i]) for i in range(self.num_spans())]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: Union[timedelta, int]) -> DateSpanSet:
        """
        Returns a new :class:`DateSpanSet` that is the result of shifting ``self`` by
        ``delta``

        Examples:
            >>> DateSpanSet('{[2000-01-01, 2000-01-10]}').shift(timedelta(days=2))
            >>> 'DateSpanSet({[2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01]})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`DateSpanSet` instance

        MEOS Functions:
            datespanset_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: Union[timedelta, int]) -> DateSpanSet:
        """
        Returns a new :class:`DateSpanSet` that starts as ``self`` but has duration
        ``duration``

        Examples:
            >>> DateSpanSet('{[2000-01-01, 2000-01-10]}').scale(timedelta(days=2))
            >>> 'DateSpanSet({[2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01]})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`DateSpanSet` instance

        MEOS Functions:
            datespanset_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self,
        shift: Union[timedelta, int, None] = None,
        duration: Union[timedelta, int, None] = None,
    ) -> DateSpanSet:
        """
        Returns a new :class:`DateSpanSet` that starts at ``self`` shifted by ``shift``
        and has duration ``duration``

        Examples:
            >>> DateSpanSet('{[2000-01-01, 2000-01-10]}').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'DateSpanSet({[2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01]})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            duration of the new tstzspan

        Returns:
            A new :class:`DateSpanSet` instance

        MEOS Functions:
            datespanset_shift_scale
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

        modified = datespanset_shift_scale(
            self._inner, shift, duration, shift != 0, duration != 0
        )
        return DateSpanSet(_inner=modified)

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> DateSpanSet('{[2012-01-01, 2012-01-04]}').contains(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-01, 2012-01-02]}').contains(DateSpanSet('{(2012-01-01, 2012-01-02)}'))
            >>> True
            >>> DateSpanSet('{(2012-01-01, 2012-01-02)}').contains(DateSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset,
            contains_spanset_date
        """

        if isinstance(content, date):
            return contains_spanset_date(self._inner, date_to_date_adt(content))
        else:
            return super().contains(content)

    def overlaps(self, other: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> DateSpanSet('{[2012-01-01, 2012-01-02]}').overlaps(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-01, 2012-01-02)}').overlaps(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> False
            >>> DateSpanSet('{[2012-01-01, 2012-01-02)}').overlaps(DateSpanSet('{(2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_spanset_span, overlaps_spanset_spanset
        """
        if isinstance(other, date):
            return self.contains(other)
        else:
            return super().overlaps(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> DateSpanSet('{[2012-01-01, 2012-01-02)}').is_left(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-01, 2012-01-02)}').is_left(DateSpanSet('{(2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-01, 2012-01-02]}').is_left(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
        before_spanset_date, left_spanset_span, left_spanset_spanset
        """
        if isinstance(other, date):
            return before_spanset_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> DateSpanSet('{[2012-01-01, 2012-01-02)}').is_over_or_left(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-01, 2012-01-02]}').is_over_or_left(DateSpanSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-03, 2012-01-05]}').is_over_or_left(DateSpanSet('{[2012-01-01, 2012-01-04]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_spanset_span, overleft_spanset_spanset,
            overbefore_spanset_date
        """
        if isinstance(other, date):
            return overbefore_spanset_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> DateSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(DateSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> DateSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(DateSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> DateSpanSet('{[2012-01-02, 2012-01-03]}').is_over_or_right(DateSpanSet('{[2012-01-01, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset,
            overafter_spanset_date
        """
        if isinstance(other, date):
            return overafter_spanset_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_over_or_right(other)

    def is_right(self, other: Union[TimeDate]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``.That is, ``self``
        starts after ``other`` ends.

        Examples:
            >>> DateSpanSet('{[2012-01-02, 2012-01-03]}').is_right(DateSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> DateSpanSet('{(2012-01-02, 2012-01-03]}').is_right(DateSpanSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> DateSpanSet('{[2012-01-02, 2012-01-03]}').is_right(DateSpanSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_spanset_span, right_spanset_spanset,
            overbefore_timestamp_tstzspanset
        """
        if isinstance(other, date):
            return after_spanset_date(self._inner, date_to_date_adt(other))
        else:
            return super().is_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: TimeDate) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_spanset_date, distance_datespanset_datespan,
            distance_datespanset_datespanset
        """
        from .dateset import DateSet
        from .datespan import DateSpan

        if isinstance(other, date):
            return timedelta(
                days=distance_spanset_date(self._inner, date_to_date_adt(other))
            )
        elif isinstance(other, DateSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, DateSpan):
            return timedelta(
                days=distance_datespanset_datespan(self._inner, other._inner)
            )
        elif isinstance(other, DateSpanSet):
            return timedelta(
                days=distance_datespanset_datespanset(self._inner, other._inner)
            )
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: date) -> date: ...

    @overload
    def intersection(self, other: Union[DateSpan, DateSpanSet]) -> DateSpanSet: ...

    def intersection(self, other: TimeDate) -> Union[date, DateSpanSet]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`TimeDate` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_spanset_timestamptz, intersection_spanset_spanset,
            intersection_spanset_span
        """
        if isinstance(other, date):
            result = intersection_spanset_date(self._inner, date_to_date_adt(other))
            return date_adt_to_date(result) if result is not None else None
        else:
            result = super().intersection(other)
        return DateSpanSet(_inner=result) if result is not None else None

    def minus(self, other: TimeDate) -> DateSpanSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`DateSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset, minus_spanset_timestamptz
        """
        if isinstance(other, date):
            result = minus_spanset_date(self._inner, date_to_date_adt(other))
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
            union_spanset_date, union_spanset_spanset, union_spanset_span
        """
        if isinstance(other, date):
            result = union_spanset_date(self._inner, date_to_date_adt(other))
        else:
            result = super().union(other)
        return DateSpanSet(_inner=result) if result is not None else None

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzspanset(self.to_tstzspanset(), *args, **kwargs)
