from __future__ import annotations

from datetime import date, timedelta, datetime
from typing import TYPE_CHECKING, List, Optional, Union, overload

from dateutil.parser import parse
from pymeos_cffi import (
    dateset_in,
    pg_date_in,
    date_to_date_adt,
    dateset_make,
    dateset_out,
    dateset_start_value,
    date_adt_to_date,
    dateset_end_value,
    dateset_value_n,
    dateset_values,
    dateset_shift_scale,
    contains_set_date,
    before_set_date,
    overbefore_set_date,
    overafter_set_date,
    after_set_date,
    distance_set_date,
    intersection_set_date,
    intersection_set_set,
    minus_set_date,
    minus_set_set,
    minus_date_set,
    union_set_date,
    union_set_set,
    distance_dateset_dateset,
)

from .timecollection import TimeCollection
from ..base import Set

if TYPE_CHECKING:
    from .datespan import DateSpan
    from .datespanset import DateSpanSet
    from .tstzspanset import TsTzSpanSet
    from .tstzspan import TsTzSpan
    from .tstzspanset import TsTzSpanSet
    from .time import TimeDate


class DateSet(Set[date], TimeCollection[date]):
    """
    Class for representing lists of distinct dates.

    ``DateSet`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> DateSet(string='{2019-09-08, 2019-09-10, 2019-09-11}')

    Another possibility is to give a tuple or list of composing dates,
    which can be instances of ``str`` or ``date``. The composing dates
    must be given in increasing order.

        >>> DateSet(elements=['2019-09-08', '2019-09-10', '2019-09-11'])
        >>> DateSet(elements=[parse('2019-09-08'), parse('2019-09-10'), parse('2019-09-11')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "dateset"

    _parse_function = dateset_in
    _parse_value_function = lambda x: (
        pg_date_in(x) if isinstance(x, str) else date_to_date_adt(x)
    )
    _make_function = dateset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            dateset_out
        """
        return dateset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    # TODO Add back if function is actually implemented
    # def to_tstzspanset(self) -> TsTzSpanSet:
    #     """
    #     Returns a TsTzSpanSet that contains a TsTzSpan for each Timestamp in
    #     ``self``.

    #     Returns:
    #         A new :class:`TsTzSpanSet` instance

    #     MEOS Functions:
    #         set_to_spanset
    #     """
    #     from .tstzspanset import TsTzSpanSet
    #     from .tstzspan import TsTzSpan

    #     return TsTzSpanSet(
    #         span_list=[
    #             TsTzSpan(_inner=date_to_tstzspan(date_to_date_adt(d)))
    #             for d in self.elements()
    #         ]
    #     )

    # ------------------------- Accessors -------------------------------------
    def duration(self) -> timedelta:
        """
        Returns the duration of the time ignoring gaps, i.e. the duration from
        the first timestamp to the last one.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of ``self``

        MEOS Functions:
            tstzspan_duration
        """
        return self.to_span().duration()

    def start_element(self) -> date:
        """
        Returns the first date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            dateset_start_value
        """
        return date_adt_to_date(dateset_start_value(self._inner))

    def end_element(self) -> date:
        """
        Returns the last date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            dateset_end_value
        """
        return date_adt_to_date(dateset_end_value(self._inner))

    def element_n(self, n: int) -> date:
        """
        Returns the n-th date in ``self``.
        Returns:
            A :class:`date` instance

        MEOS Functions:
            dateset_value_n
        """
        super().element_n(n)
        return date_adt_to_date(dateset_value_n(self._inner, n + 1)[0])

    def elements(self) -> List[date]:
        """
        Returns the list of distinct dates in ``self``.
        Returns:
            A :class:`list[date]` instance

        MEOS Functions:
            dateset_values
        """
        tss = dateset_values(self._inner)
        return [date_adt_to_date(tss[i]) for i in range(self.num_elements())]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: Union[timedelta, int]) -> DateSet:
        """
        Returns a new :class:`DateSpanSet` that is the result of shifting ``self`` by
        ``delta``

        Examples:
            >>> DateSet('{2000-01-01, 2000-01-10}').shift(timedelta(days=2))
            >>> 'DateSet({2000-01-03, 2000-01-12})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`DateSpanSet` instance

        MEOS Functions:
            dateset_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: Union[timedelta, int]) -> DateSet:
        """
        Returns a new :class:`DateSet` that with the scaled so that the span of
        ``self`` is ``duration``.

        Examples:
            >>> DateSet('{2000-01-01, 2000-01-10}').scale(timedelta(days=2))
            >>> 'DateSet({2000-01-01, 2000-01-03})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`DateSet` instance

        MEOS Functions:
            dateset_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self,
        shift: Union[int, timedelta, None] = None,
        duration: Union[int, timedelta, None] = None,
    ) -> DateSet:
        """
        Returns a new :class:`DateSet` that is the result of shifting and scaling
        ``self``.

        Examples:
            >>> DateSet('{2000-01-01, 2000-01-10}').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'DateSet({2000-01-03, 2000-01-07})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`DateSet` instance

        MEOS Functions:
            dateset_shift_scale
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
        tss = dateset_shift_scale(
            self._inner, shift, duration, shift != 0, duration != 0
        )
        return DateSet(_inner=tss)

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: Union[date, datetime, DateSet]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> DateSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01').date())
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').contains(DateSet('{2012-01-01}'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').contains(DateSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_date, contains_set_set, contains_spanset_spanset
        """

        if isinstance(content, date):
            return contains_set_date(self._inner, date_to_date_adt(content))
        if isinstance(content, datetime):
            return contains_set_date(self._inner, date_to_date_adt(content.date()))
        else:
            return super().contains(content)

    def __contains__(self, item):
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> DateSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01').date())
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').contains(DateSet('{2012-01-01}'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').contains(DateSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_date, contains_set_set, contains_spanset_spanset
        """
        return self.contains(item)

    def overlaps(self, other: Union[date, DateSet, DateSpan, DateSpanSet]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> DateSet('{2012-01-01, 2012-01-02}').overlaps(DateSet('{2012-01-02, 2012-01-03}'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').overlaps(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').overlaps(DateSpan('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_set_set, overlaps_span_span, overlaps_spanset_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return contains_set_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSpan):
            return self.to_span().is_adjacent(other)
        elif isinstance(other, DateSpanSet):
            return self.to_spanset().is_adjacent(other)
        else:
            return super().overlaps(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> DateSet('{2012-01-01, 2012-01-02}').is_left(DateSet('{2012-01-03}'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').is_left(DateSpan('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').is_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            before_set_date, left_span_span
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return before_set_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSpan):
            return self.to_span().is_left(other)
        elif isinstance(other, DateSpanSet):
            return self.to_span().is_left(other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> DateSet('{2012-01-01, 2012-01-02}').is_over_or_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSet('{2012-01-01, 2012-01-02}').is_over_or_left(DateSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> DateSet('{2012-01-03, 2012-01-05}').is_over_or_left(DateSpan('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overbefore_set_date, overleft_span_span, overleft_span_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return overbefore_set_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSpan):
            return self.to_span().is_over_or_left(other)
        elif isinstance(other, DateSpanSet):
            return self.to_span().is_over_or_left(other)
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> DateSet('{2012-01-02, 2012-01-03}').is_over_or_right(DateSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSet('{2012-01-02, 2012-01-03}').is_over_or_right(DateSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> DateSet('{2012-01-02, 2012-01-03}').is_over_or_right(DateSpan('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overafter_set_date, overright_span_span, overright_span_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return overafter_set_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSpan):
            return self.to_span().is_over_or_after(other)
        elif isinstance(other, DateSpanSet):
            return self.to_span().is_over_or_after(other)
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: TimeDate) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, the
        first timestamp in ``self`` is after ``other``.

        Examples:
            >>> DateSet('{2012-01-02, 2012-01-03}').is_right(DateSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> DateSet('{2012-01-02, 2012-01-03}').is_right(DateSet('{2012-01-01}'))
            >>> True
            >>> DateSet('{2012-01-02, 2012-01-03}').is_right(DateSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            after_set_date, right_span_span, right_span_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return after_set_date(self._inner, date_to_date_adt(other))
        elif isinstance(other, DateSpan):
            return self.to_span().is_after(other)
        elif isinstance(other, DateSpanSet):
            return self.to_span().is_after(other)
        else:
            return super().is_over_or_left(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: TimeDate) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_set_date, distance_dateset_dateset,
            distance_datespanset_datespan, distance_datespanset_datespanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return timedelta(
                days=distance_set_date(self._inner, date_to_date_adt(other))
            )
        elif isinstance(other, DateSet):
            return timedelta(days=distance_dateset_dateset(self._inner, other._inner))
        elif isinstance(other, DateSpan):
            return self.to_spanset().distance(other)
        elif isinstance(other, DateSpanSet):
            return self.to_spanset().distance(other)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: Union[date, DateSet]) -> Optional[DateSet]: ...

    @overload
    def intersection(
        self, other: Union[DateSpan, DateSpanSet]
    ) -> Optional[DateSpanSet]: ...

    def intersection(self, other: TimeDate) -> Optional[TimeDate]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`TimeDate` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_set_date, intersection_set_set, intersection_spanset_span,
            intersection_spanset_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            result = intersection_set_date(self._inner, date_to_date_adt(other))
            return DateSet(_inner=result) if result is not None else None
        elif isinstance(other, DateSet):
            result = intersection_set_set(self._inner, other._inner)
            return DateSet(_inner=result) if result is not None else None
        elif isinstance(other, DateSpan):
            return self.to_spanset().intersection(other)
        elif isinstance(other, DateSpanSet):
            return self.to_spanset().intersection(other)
        else:
            return super().intersection(other)

    @overload
    def minus(self, other: Union[date, DateSet]) -> Optional[DateSet]: ...

    @overload
    def minus(self, other: Union[DateSpan, DateSpanSet]) -> Optional[DateSpanSet]: ...

    def minus(self, other: TimeDate) -> Optional[TimeDate]:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`TimeDate` instance. The actual class depends on ``other``.

        MEOS Functions:
            minus_set_date, minus_set_set, minus_spanset_span,
            minus_spanset_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            result = minus_set_date(self._inner, date_to_date_adt(other))
            return DateSet(_inner=result) if result is not None else None
        elif isinstance(other, DateSet):
            result = minus_set_set(self._inner, other._inner)
            return DateSet(_inner=result) if result is not None else None
        elif isinstance(other, DateSpan):
            return self.to_spanset().minus(other)
        elif isinstance(other, DateSpanSet):
            return self.to_spanset().minus(other)
        else:
            return super().minus(other)

    def subtract_from(self, other: date) -> Optional[date]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`date` instance

        Returns:
            A :class:`datetime` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_date_set

        See Also:
            :meth:`minus`
        """
        return date_adt_to_date(minus_date_set(date_to_date_adt(other), self._inner))

    @overload
    def union(self, other: Union[date, DateSet]) -> DateSet: ...

    @overload
    def union(self, other: Union[DateSpan, DateSpanSet]) -> DateSpanSet: ...

    def union(self, other: TimeDate) -> Union[DateSpanSet, DateSet]:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`TimeDate` instance. The actual class depends on ``other``.

        MEOS Functions:
            union_set_date, union_set_set, union_spanset_span,
            union_spanset_spanset
        """
        from .datespan import DateSpan
        from .datespanset import DateSpanSet

        if isinstance(other, date):
            return DateSet(_inner=union_set_date(self._inner, date_to_date_adt(other)))
        elif isinstance(other, DateSet):
            return DateSet(_inner=union_set_set(self._inner, other._inner))
        elif isinstance(other, DateSpan):
            return self.to_spanset().union(other)
        elif isinstance(other, DateSpanSet):
            return self.to_spanset().union(other)
        else:
            return super().union(other)

    # ------------------------- Comparisons -----------------------------------

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzspanset(
            self.to_spanset().to_tstzspanset(), *args, **kwargs
        )
