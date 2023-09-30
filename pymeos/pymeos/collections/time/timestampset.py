from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload, get_args

from dateutil.parser import parse
from pymeos_cffi import *

from .time_collection import TimeCollection
from ..base import Set

if TYPE_CHECKING:
    from ...temporal import Temporal
    from .period import Period
    from .periodset import PeriodSet
    from .time import Time
    from ...boxes import Box


class TimestampSet(Set[datetime], TimeCollection):
    """
    Class for representing lists of distinct timestamp values.

    ``TimestampSet`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TimestampSet(string='{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TimestampSet(elements=['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TimestampSet(elements=[parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])

    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'tstzset'

    _parse_function = timestampset_in
    _parse_value_function = lambda x: pg_timestamptz_in(x, -1) if isinstance(x, str) else datetime_to_timestamptz(x)
    _make_function = timestampset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            timestampset_out
        """
        return timestampset_out(self._inner)

    # ------------------------- Conversions -----------------------------------
    def to_spanset(self) -> PeriodSet:
        """
        Returns a PeriodSet that contains a Period for each Timestamp in
        ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            set_to_spanset
        """
        from .periodset import PeriodSet
        return PeriodSet(_inner=super().to_spanset())

    def to_periodset(self) -> PeriodSet:
        """
        Returns a PeriodSet that contains a Period for each Timestamp in
        ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            set_to_spanset
        """
        return self.to_spanset()

    def to_span(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            set_span
        """
        from .period import Period
        return Period(_inner=super().to_span())

    def to_period(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            set_span
        """
        return self.to_span()

    # ------------------------- Accessors -------------------------------------
    def duration(self) -> timedelta:
        """
        Returns the duration of the time ignoring gaps, i.e. the duration from
        the first timestamp to the last one.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of
            the period

        MEOS Functions:
            period_duration
        """
        return interval_to_timedelta(period_duration(set_span(self._inner)))

    def start_element(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_start_timestamp
        """
        return timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    def end_element(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_end_timestamp
        """
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner))

    def element_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_timestamp_n
        """
        super().element_n(n)
        return timestamptz_to_datetime(timestampset_timestamp_n(self._inner, n + 1))

    def elements(self) -> List[datetime]:
        """
        Returns the list of distinct timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            timestampset_timestamps
        """
        tss = timestampset_values(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_elements())]

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that is the result of shifting ``self`` by
        ``delta``

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift(timedelta(days=2))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_scale
        """
        return self.shift_scale(shift=delta)

    def scale(self, duration: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that with the scaled so that the span of
        ``self`` is ``duration``.

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').scale(timedelta(days=2))
            >>> 'TimestampSet({2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_scale
        """
        return self.shift_scale(duration=duration)

    def shift_scale(self, shift: Optional[timedelta] = None,
        duration: Optional[timedelta] = None) -> TimestampSet:
        """
        Returns a new TimestampSet that is the result of shifting and scaling
        ``self``.

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift_scale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the
            span of the new set

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_scale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        tss = timestampset_shift_scale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return TimestampSet(_inner=tss)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other: Union[Period, PeriodSet, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is,
        they share a bound but only one of them contains it.

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
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, Temporal):
            return self.is_adjacent(other.time())
        elif isinstance(other, get_args(Box)):
            return self.is_adjacent(other.to_period())
        else:
            super().is_adjacent(other)

    def is_contained_in(self, container: Union[Period, PeriodSet, TimestampSet,
        Temporal, Box]) -> bool:
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
            contained_span_span, contained_span_spanset, contained_set_set,
            contained_spanset_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(container, Temporal):
            return self.is_contained_in(container.time())
        elif isinstance(container, Box):
            return self.is_contained_in(container.to_period())
        else:
            return super().is_contained_in(container)

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
            contains_timestampset_timestamp, contains_set_set, 
            contains_spanset_spanset
        """
        from ...temporal import Temporal
        if isinstance(content, datetime):
            return contains_timestampset_timestamp(self._inner,
                datetime_to_timestamptz(content))
        elif isinstance(content, Temporal):
            return self.to_spanset().contains(content)
        else:
            return super().contains(content)

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
            contains_timestampset_timestamp, contains_set_set, 
            contains_spanset_spanset
        """
        return self.contains(item)

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal,
        Box]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both
        share at least an instant

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
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return contains_timestampset_timestamp(self._inner,
                datetime_to_timestamptz(other))
        elif isinstance(other, Temporal):
            return self.to_spanset().overlaps(other)
        elif isinstance(other, Box):
            return self.to_span().overlaps(other)
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether the bounding period of `self` is the same as the
        bounding period of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if same, False otherwise.

        See Also:
            :meth:`Period.is_same`
        """
        return self.to_period().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_left(TimestampSet('{2012-01-03}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_left(Period('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_left(Period('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overafter_timestamp_period, left_span_span, left_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return after_timestamp_timestampset(datetime_to_timestamptz(other),
                self._inner)
        elif isinstance(other, Temporal):
            return self.to_period().is_left(other)
        elif isinstance(other, get_args(Box)):
            return self.to_period().is_left(other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_left(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_left(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-03, 2012-01-05}').is_over_or_left(Period('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overbefore_period_timestamp, overleft_span_span, overleft_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overafter_timestamp_timestampset(datetime_to_timestamptz(other),
                self._inner)
        elif isinstance(other, Temporal):
            return self.to_period().is_over_or_left(other)
        elif isinstance(other, get_args(Box)):
            return self.to_period().is_over_or_left(other.to_period())
        else:
            return super().is_over_or_left(other)

    def is_over_or_right(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_right(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_right(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_right(Period('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
        overafter_period_timestamp, overright_span_span, overright_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return overbefore_timestamp_timestampset(datetime_to_timestamptz(other),
                self._inner)
        elif isinstance(other, Temporal):
            return self.to_period().is_over_or_right(other)
        elif isinstance(other, get_args(Box)):
            return self.to_period().is_over_or_right(other)
        else:
            return super().is_over_or_right(other)

    def is_right(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, the
        first timestamp in ``self`` is after ``other``.

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_right(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_right(TimestampSet('{2012-01-01}'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_right(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            overbefore_timestamp_timestampset, right_set_set, right_span_span, 
            right_span_spanset
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return before_timestamp_timestampset(datetime_to_timestamptz(other),
                self._inner)
        elif isinstance(other, Temporal):
            return self.to_period().is_right(other)
        elif isinstance(other, get_args(Box)):
            return self.to_period().is_right(other)
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
            distance_timestampset_timestamp, distance_set_set, 
            distance_span_span, distance_spanset_span
        """
        from ...temporal import Temporal
        from ...boxes import Box
        if isinstance(other, datetime):
            return timedelta(seconds=distance_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, Temporal):
            return self.to_period().distance(other)
        elif isinstance(other, get_args(Box)):
            return self.to_period().distance(other)
        else:
            return timedelta(seconds=super().distance(other))

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: datetime) -> Optional[datetime]:
        ...

    @overload
    def intersection(self, other: TimestampSet) -> Optional[TimestampSet]:
        ...

    @overload
    def intersection(self, other: Union[Period, PeriodSet, Temporal, Box]) -> Optional[PeriodSet]:
        ...

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
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            result = intersection_timestampset_timestamp(self._inner,
                datetime_to_timestamptz(other))
            return timestamptz_to_datetime(result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = intersection_set_set(self._inner, other._inner)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            return self.to_periodset().intersection(other)
        elif isinstance(other, PeriodSet):
            return self.to_periodset().intersection(other)
        elif isinstance(other, Temporal):
            return self.intersection(other.time())
        elif isinstance(other, get_args(Box)):
            return self.intersection(other.to_period())
        else:
            return super().intersection(other)

    @overload
    def minus(self, other: Union[datetime, TimestampSet]) -> Optional[TimestampSet]:
        ...

    @overload
    def minus(self, other: Union[Period, PeriodSet, Temporal, Box]) -> Optional[PeriodSet]:
        ...

    def minus(self, other: Union[Time, Temporal, Box]) -> Optional[Time]:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            minus_timestampset_timestamp, minus_set_set, minus_spanset_span, 
            minus_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            result = minus_timestampset_timestamp(self._inner,
                datetime_to_timestamptz(other))
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = minus_set_set(self._inner, other._inner)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            return self.to_periodset().minus(other)
        elif isinstance(other, PeriodSet):
            return self.to_periodset().minus(other)
        elif isinstance(other, Temporal):
            return self.minus(other.time())
        elif isinstance(other, get_args(Box)):
            return self.minus(other.to_period())
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
            minus_timestamp_timestampset

        See Also:
            :meth:`minus`
        """
        return timestamptz_to_datetime(minus_timestamp_timestampset(datetime_to_timestamptz(other), self._inner))

    @overload
    def union(self, other: Union[datetime, TimestampSet]) -> TimestampSet:
        ...

    @overload
    def union(self, other: Union[Period, PeriodSet, Temporal, Box]) -> PeriodSet:
        ...

    def union(self, other: Union[Time, Temporal, Box]) -> Union[PeriodSet, TimestampSet]:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            union_timestampset_timestamp, union_set_set, union_spanset_span, 
            union_spanset_spanset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, datetime):
            return TimestampSet(_inner=union_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=union_set_set(self._inner, other._inner))
        elif isinstance(other, Period):
            return self.to_periodset().union(other)
        elif isinstance(other, PeriodSet):
            return self.to_periodset().union(other)
        elif isinstance(other, Temporal):
            return self.union(other.time())
        elif isinstance(other, get_args(Box)):
            return self.union(other.to_period())
        else:
            return super().union(other)

    # ------------------------- Comparisons -----------------------------------

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ...plotters import TimePlotter
        return TimePlotter.plot_timestampset(self, *args, **kwargs)
