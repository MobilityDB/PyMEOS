from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload, get_args

from dateutil.parser import parse
from pymeos_cffi import *

from .timecollection import TimeCollection
from ..base import Set

if TYPE_CHECKING:
    from ...temporal import Temporal
    from .tstzspan import TsTzSpan
    from .tstzspanset import TsTzSpanSet
    from .time import Time
    from ...boxes import Box


class TsTzSet(Set[datetime], TimeCollection[datetime]):
    """
    Class for representing lists of distinct timestamp values.

    ``TsTzSet`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TsTzSet(string='{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TsTzSet(elements=['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TsTzSet(elements=[parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "tstzset"

    _parse_function = tstzset_in
    _parse_value_function = lambda x: (
        pg_timestamptz_in(x, -1) if isinstance(x, str) else datetime_to_timestamptz(x)
    )
    _make_function = tstzset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            tstzset_out
        """
        return tstzset_out(self._inner)

    # ------------------------- Conversions -----------------------------------
    # ------------------------- Accessors -------------------------------------
    def duration(self) -> timedelta:
        """
        Returns the duration of the time ignoring gaps, i.e. the duration from
        the first timestamp to the last one.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the tstzspan

        MEOS Functions:
            tstzspan_duration
        """
        return interval_to_timedelta(tstzspan_duration(set_span(self._inner)))

    def start_element(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzset_start_timestamp
        """
        return timestamptz_to_datetime(tstzset_start_value(self._inner))

    def end_element(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            tstzset_end_timestamp
        """
        return timestamptz_to_datetime(tstzset_end_value(self._inner))

    def element_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            set_timestamptz_n
        """
        super().element_n(n)
        return timestamptz_to_datetime(tstzset_value_n(self._inner, n + 1))

    def elements(self) -> List[datetime]:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            set_timestamptzs
        """
        tss = tstzset_values(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_elements())]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> TsTzSet:
        """
        Returns a new TsTzSet that is the result of shifting ``self`` by
        ``delta``

        Examples:
            >>> TsTzSet('{2000-01-01, 2000-01-10}').shift(timedelta(days=2))
            >>> 'TsTzSet({2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            tstzset_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: timedelta) -> TsTzSet:
        """
        Returns a new TsTzSet that with the scaled so that the span of
        ``self`` is ``duration``.

        Examples:
            >>> TsTzSet('{2000-01-01, 2000-01-10}').scale(timedelta(days=2))
            >>> 'TsTzSet({2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            tstzset_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(
        self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None
    ) -> TsTzSet:
        """
        Returns a new TsTzSet that is the result of shifting and scaling
        ``self``.

        Examples:
            >>> TsTzSet('{2000-01-01, 2000-01-10}').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TsTzSet({2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            tstzset_shift_scale
        """
        assert (
            shift is not None or duration is not None
        ), "shift and scale deltas must not be both None"
        tss = tstzset_shift_scale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return TsTzSet(_inner=tss)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[TsTzSpan, TsTzSpanSet, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is,
        they share a bound but only one of them contains it.

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_adjacent(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_adjacent(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> False  # Both contain bound
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_adjacent(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> False  # Neither contain bound

        Args:
            other: temporal object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_spanset_span
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, Temporal):
            return self.is_adjacent(other.time())
        elif isinstance(other, get_args(Box)):
            return self.is_adjacent(other.to_span())
        else:
            super().is_adjacent(other)

    def is_contained_in(
        self, container: Union[TsTzSpan, TsTzSpanSet, TsTzSet, Temporal, Box]
    ) -> bool:
        """
        Returns whether ``self`` is temporally contained in ``container``.

        Examples:
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_contained_in(TsTzSpan('[2012-01-01, 2012-01-04]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_contained_in(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_contained_in(TsTzSpan('(2012-01-01, 2012-01-02)'))
            >>> False

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_span_span, contained_span_spanset, contained_set_set,
            contained_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(container, Temporal):
            return self.is_contained_in(container.time())
        elif isinstance(container, get_args(Box)):
            return self.is_contained_in(container.to_span())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[datetime, TsTzSet, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').contains(TsTzSet('{2012-01-01}'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').contains(TsTzSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_timestamptz, contains_set_set,
            contains_spanset_spanset
        """
        from ...temporal import Temporal

        if isinstance(content, datetime):
            return contains_set_timestamptz(
                self._inner, datetime_to_timestamptz(content)
            )
        elif isinstance(content, Temporal):
            return self.to_spanset().contains(content)
        else:
            return super().contains(content)

    def __contains__(self, item):
        """
        Returns whether ``self`` temporally contains ``content``.

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-04}').contains(parse('2012-01-01]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').contains(TsTzSet('{2012-01-01}'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').contains(TsTzSet('{2012-01-01, 2012-01-03}'))
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_timestamptz, contains_set_set,
            contains_spanset_spanset
        """
        return self.contains(item)

    def overlaps(
        self, other: Union[TsTzSpan, TsTzSpanSet, TsTzSet, Temporal, Box]
    ) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-02}').overlaps(TsTzSet('{2012-01-02, 2012-01-03}'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').overlaps(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').overlaps(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_set_set, overlaps_span_span, overlaps_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return contains_set_timestamptz(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.to_spanset().overlaps(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().overlaps(other)
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Time, Temporal, Box]) -> bool:
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
        return self.to_span().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_left(TsTzSet('{2012-01-03}'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_left(TsTzSpan('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overafter_timestamp_tstzspan, left_span_span, left_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return after_timestamptz_set(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, Temporal):
            return self.to_span().is_left(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().is_left(other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_over_or_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSet('{2012-01-01, 2012-01-02}').is_over_or_left(TsTzSpan('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TsTzSet('{2012-01-03, 2012-01-05}').is_over_or_left(TsTzSpan('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overbefore_tstzspan_timestamp, overleft_span_span, overleft_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overafter_timestamptz_set(
                datetime_to_timestamptz(other), self._inner
            )
        elif isinstance(other, Temporal):
            return self.to_span().is_over_or_left(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().is_over_or_left(other.to_span())
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_over_or_right(TsTzSpan('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
        overafter_tstzspan_timestamp, overright_span_span, overright_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return overbefore_timestamptz_set(
                datetime_to_timestamptz(other), self._inner
            )
        elif isinstance(other, Temporal):
            return self.to_span().is_over_or_right(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().is_over_or_right(other)
        else:
            return super().is_over_or_right(other)

    def is_right(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, the
        first timestamp in ``self`` is after ``other``.

        Examples:
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_right(TsTzSpan('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_right(TsTzSet('{2012-01-01}'))
            >>> True
            >>> TsTzSet('{2012-01-02, 2012-01-03}').is_right(TsTzSpan('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            overbefore_timestamptz_set, right_set_set, right_span_span,
            right_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return before_timestamptz_set(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, Temporal):
            return self.to_span().is_right(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().is_right(other)
        else:
            return super().is_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[Time, Temporal, Box]) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_set_timestamptz, distance_tstzset_tstzset,
            distance_tstzspanset_tstzspan, distance_tstzspanset_tstzspanset
        """
        from .tstzspan import TsTzSpan
        from .tstzspanset import TsTzSpanSet
        from ...temporal import Temporal
        from ...boxes import Box

        if isinstance(other, datetime):
            return timedelta(
                seconds=distance_set_timestamptz(
                    self._inner, datetime_to_timestamptz(other)
                )
            )
        elif isinstance(other, TsTzSet):
            return timedelta(
                seconds=distance_tstzset_tstzset(self._inner, other._inner)
            )
        elif isinstance(other, TsTzSpan):
            return self.to_spanset().distance(other)
        elif isinstance(other, TsTzSpanSet):
            return self.to_spanset().distance(other)
        elif isinstance(other, Temporal):
            return self.to_span().distance(other)
        elif isinstance(other, get_args(Box)):
            return self.to_span().distance(other)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: datetime) -> Optional[datetime]: ...

    @overload
    def intersection(self, other: TsTzSet) -> Optional[TsTzSet]: ...

    @overload
    def intersection(
        self, other: Union[TsTzSpan, TsTzSpanSet, Temporal, Box]
    ) -> Optional[TsTzSpanSet]: ...

    def intersection(self, other: Union[Time, Temporal]) -> Optional[Time]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_set_set, intersection_spanset_span,
            intersection_spanset_spanset
        """
        from .tstzspan import TsTzSpan
        from .tstzspanset import TsTzSpanSet

        if isinstance(other, datetime):
            result = intersection_set_timestamptz(
                self._inner, datetime_to_timestamptz(other)
            )
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TsTzSet):
            result = intersection_set_set(self._inner, other._inner)
            return TsTzSet(_inner=result) if result is not None else None
        elif isinstance(other, TsTzSpan):
            return self.to_spanset().intersection(other)
        elif isinstance(other, TsTzSpanSet):
            return self.to_spanset().intersection(other)
        elif isinstance(other, Temporal):
            return self.intersection(other.time())
        elif isinstance(other, get_args(Box)):
            return self.intersection(other.to_span())
        else:
            return super().intersection(other)

    @overload
    def minus(self, other: Union[datetime, TsTzSet]) -> Optional[TsTzSet]: ...

    @overload
    def minus(
        self, other: Union[TsTzSpan, TsTzSpanSet, Temporal, Box]
    ) -> Optional[TsTzSpanSet]: ...

    def minus(self, other: Union[Time, Temporal, Box]) -> Optional[Time]:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            minus_set_timestamptz, minus_set_set, minus_spanset_span,
            minus_spanset_spanset
        """
        from .tstzspan import TsTzSpan
        from .tstzspanset import TsTzSpanSet

        if isinstance(other, datetime):
            result = minus_set_timestamptz(self._inner, datetime_to_timestamptz(other))
            return TsTzSet(_inner=result) if result is not None else None
        elif isinstance(other, TsTzSet):
            result = minus_set_set(self._inner, other._inner)
            return TsTzSet(_inner=result) if result is not None else None
        elif isinstance(other, TsTzSpan):
            return self.to_spanset().minus(other)
        elif isinstance(other, TsTzSpanSet):
            return self.to_spanset().minus(other)
        elif isinstance(other, Temporal):
            return self.minus(other.time())
        elif isinstance(other, get_args(Box)):
            return self.minus(other.to_span())
        else:
            return super().minus(other)

    def subtract_from(self, other: datetime) -> Optional[datetime]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`datetime` instance

        Returns:
            A :class:`datetime` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_timestamptz_set

        See Also:
            :meth:`minus`
        """
        return timestamptz_to_datetime(
            minus_timestamptz_set(datetime_to_timestamptz(other), self._inner)
        )

    @overload
    def union(self, other: Union[datetime, TsTzSet]) -> TsTzSet: ...

    @overload
    def union(
        self, other: Union[TsTzSpan, TsTzSpanSet, Temporal, Box]
    ) -> TsTzSpanSet: ...

    def union(self, other: Union[Time, Temporal, Box]) -> Union[TsTzSpanSet, TsTzSet]:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            union_set_timestamptz, union_set_set, union_spanset_span,
            union_spanset_spanset
        """
        from .tstzspan import TsTzSpan
        from .tstzspanset import TsTzSpanSet

        if isinstance(other, datetime):
            return TsTzSet(
                _inner=union_set_timestamptz(
                    self._inner, datetime_to_timestamptz(other)
                )
            )
        elif isinstance(other, TsTzSet):
            return TsTzSet(_inner=union_set_set(self._inner, other._inner))
        elif isinstance(other, TsTzSpan):
            return self.to_spanset().union(other)
        elif isinstance(other, TsTzSpanSet):
            return self.to_spanset().union(other)
        elif isinstance(other, Temporal):
            return self.union(other.time())
        elif isinstance(other, get_args(Box)):
            return self.union(other.to_span())
        else:
            return super().union(other)

    # ------------------------- Comparisons -----------------------------------

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter

        return TimePlotter.plot_tstzset(self, *args, **kwargs)
