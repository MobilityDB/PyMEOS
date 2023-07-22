from __future__ import annotations

from datetime import timedelta, datetime
from typing import Optional, Union, List, overload, get_args
from typing import TYPE_CHECKING

from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from ..boxes import Box
    from .period import Period
    from .timestampset import TimestampSet
    from .time import Time


class PeriodSet:
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

    def __init__(self, string: Optional[str] = None, *, period_list: Optional[List[Union[str, Period]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (period_list is not None)), \
            "Either string must be not None or period_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = periodset_in(string)
        else:
            periods = [period_in(period)[0] if isinstance(period, str) else period._inner[0] for period in period_list]
            self._inner = spanset_make(periods, normalize)

    # ------------------------- Input/Output ----------------------------------
    @staticmethod
    def from_hexwkb(hexwkb: str) -> PeriodSet:
        """
        Returns a `PeriodSet` from its WKB representation in hex-encoded ASCII.
        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            spanset_from_hexwkb
        """
        result = spanset_from_hexwkb(hexwkb)
        return PeriodSet(_inner=result)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.
        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            spanset_as_hexwkb
        """
        return spanset_as_hexwkb(self._inner, -1)[0]

    # ------------------------- Accessors -------------------------------------
    def duration(self) -> timedelta:
        """
        Returns the duration of the periodset taking into account the gaps within,
        i.e. the sum of the durations of the periods within.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the periodset

        MEOS Functions:
            periodset_duration
        """
        return interval_to_timedelta(periodset_duration(self._inner, False))

    def timespan(self) -> timedelta:
        """
        Returns the duration of the periodset ignoring any gap, i.e. the duration from the
        lower bound of the first period to the upper bound of the last period.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the periodset

        MEOS Functions:
            periodset_duration
        """
        return interval_to_timedelta(periodset_duration(self._inner, True))

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            periodset_num_timestamps
        """
        return periodset_num_timestamps(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_start_timestamp
        """
        return timestamptz_to_datetime(periodset_start_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_end_timestamp
        """
        return timestamptz_to_datetime(periodset_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            periodset_timestamp_n
        """
        result = periodset_timestamp_n(self._inner, n + 1)
        if result is None:
            raise IndexError(f"Index {n} out of range 0 - {self.num_timestamps() - 1}")
        return timestamptz_to_datetime(result)

    def timestamps(self) -> List[datetime]:
        """
        Returns the list of distinc timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            periodset_timestamps
        """
        ts, count = periodset_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    def num_periods(self) -> int:
        """
        Returns the number of periods in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            spanset_num_spans
        """
        return spanset_num_spans(self._inner)

    def start_period(self) -> Period:
        """
        Returns the first period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            periodset_lower
        """
        from .period import Period
        return Period(_inner=spanset_start_span(self._inner))

    def end_period(self) -> Period:
        """
        Returns the last period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            periodset_upper
        """
        from .period import Period
        return Period(_inner=spanset_end_span(self._inner))

    def period_n(self, n: int) -> Period:
        """
        Returns the n-th period in ``self``.
        Returns:
            A :class:`Period` instance

        MEOS Functions:
            spanset_span_n
        """
        from .period import Period

        result = spanset_span_n(self._inner, n + 1)
        if result is None:
            raise IndexError(f"Index {n} out of range 0 - {self.num_periods() - 1}")
        return Period(_inner=result)

    def periods(self) -> List[Period]:
        """
        Returns the list of periods in ``self``.
        Returns:
            A :class:`list[Period]` instance

        MEOS Functions:
            spanset_spans
        """
        from .period import Period
        ps = spanset_spans(self._inner)
        return [Period(_inner=ps[i]) for i in range(self.num_periods())]

    # ------------------------- Conversions ----------------------------------
    def to_period(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            spanset_span
        """
        from .period import Period
        return Period(_inner=spanset_span(self._inner))

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
    def is_adjacent(self, other: Union[Time, Temporal, Box]) -> bool:
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
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return adjacent_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return adjacent_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_spanset_spanset(self._inner, set_to_spanset(other._inner))
        elif isinstance(other, Temporal):
            return adjacent_spanset_spanset(self._inner, temporal_time(other._inner))
        elif isinstance(other, get_args(Box)):
            return adjacent_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, Temporal, Box]) -> bool:
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
        from .period import Period
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(container, Period):
            return contained_spanset_span(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_spanset_spanset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_spanset_spanset(self._inner, temporal_time(container._inner))
        elif isinstance(container, get_args(Box)):
            return contained_spanset_span(self._inner, container.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Time, Temporal, Box]) -> bool:
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
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(content, Period):
            return contains_spanset_span(self._inner, content._inner)
        if isinstance(content, PeriodSet):
            return contains_spanset_spanset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_periodset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_spanset_spanset(self._inner, set_to_spanset(content._inner))
        elif isinstance(content, Temporal):
            return contains_spanset_spanset(self._inner, temporal_time(content._inner))
        elif isinstance(content, get_args(Box)):
            return contains_spanset_span(self._inner, content.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

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

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal, Box]) -> bool:
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
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return overlaps_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overlaps_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_spanset_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return overlaps_spanset_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overlaps_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[Time, Temporal, Box]) -> bool:
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
    def is_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``.That is, ``self`` starts after ``other`` ends.

        Examples:
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_after(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{(2012-01-02, 2012-01-03]}').is_after(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_after(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_spanset_span, right_spanset_spanset, overbefore_timestamp_periodset
        """
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overbefore_timestamp_periodset(datetime_to_timestamptz(other), self._inner)
        elif isinstance(other, TimestampSet):
            return right_spanset_span(self._inner, set_span(other._inner))
        elif isinstance(other, Period):
            return right_spanset_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return right_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return right_spanset_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return right_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_before(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_before(PeriodSet('{(2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_before(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
        before_periodset_timestamp, left_spanset_span, left_spanset_spanset
        """
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return before_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return left_spanset_spanset(self._inner, set_to_spanset(other._inner))
        elif isinstance(other, Period):
            return left_spanset_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return left_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return left_spanset_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return left_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_after(PeriodSet('{[2012-01-01, 2012-01-02)}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_after(PeriodSet('{[2012-01-01, 2012-01-02]}'))
            >>> True
            >>> PeriodSet('{[2012-01-02, 2012-01-03]}').is_over_or_after(PeriodSet('{[2012-01-01, 2012-01-03]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset, overafter_periodset_timestamp,
            overafter_periodset_timestampset,
        """
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, datetime):
            return overafter_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overright_spanset_span(self._inner, set_span(other._inner))
        elif isinstance(other, Period):
            return overright_spanset_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overright_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overright_spanset_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overright_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Examples:
            >>> PeriodSet('{[2012-01-01, 2012-01-02)}').is_over_or_before(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-01, 2012-01-02]}').is_over_or_before(PeriodSet('{[2012-01-02, 2012-01-03]}'))
            >>> True
            >>> PeriodSet('{[2012-01-03, 2012-01-05]}').is_over_or_before(PeriodSet('{[2012-01-01, 2012-01-04]}'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_spanset_span, overleft_spanset_spanset, overbefore_periodset_timestamp,
            overbefore_periodset_timestampset, overbefore_periodset_temporal
        """
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return overleft_spanset_span(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overleft_spanset_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overleft_spanset_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return overleft_spanset_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overleft_spanset_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
        from .period import Period
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Temporal):
            return timedelta(seconds=distance_spanset_span(self._inner, temporal_to_period(other._inner)))
        elif isinstance(other, Period):
            return timedelta(seconds=distance_spanset_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return timedelta(seconds=distance_spanset_spanset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timedelta(seconds=distance_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return timedelta(seconds=distance_spanset_span(self._inner, set_span(other._inner)))
        elif isinstance(other, get_args(Box)):
            return timedelta(seconds=distance_spanset_span(self._inner, other.to_period()._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
            result = intersection_spanset_spanset(self._inner, set_to_spanset(other._inner))
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = intersection_spanset_span(self._inner, other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = intersection_spanset_spanset(self._inner, other._inner)
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
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            result = minus_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = minus_spanset_spanset(self._inner, set_to_spanset(other._inner))
        elif isinstance(other, Period):
            result = minus_spanset_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = minus_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
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
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, datetime):
            return PeriodSet(_inner=union_periodset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=union_spanset_spanset(self._inner, set_to_spanset(other._inner)))
        elif isinstance(other, Period):
            return PeriodSet(_inner=union_spanset_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_spanset_spanset(self._inner, other._inner))

        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Return whether ``self`` and ``other`` are equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            spanset_eq
        """
        if isinstance(other, self.__class__):
            return spanset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Return whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            spanset_ne
        """
        if isinstance(other, self.__class__):
            return spanset_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            spanset_lt
        """
        if isinstance(other, self.__class__):
            return spanset_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            spanset_le
        """
        if isinstance(other, self.__class__):
            return spanset_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            spanset_gt
        """
        if isinstance(other, self.__class__):
            return spanset_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            spanset_ge
        """
        if isinstance(other, self.__class__):
            return spanset_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    # ------------------------- Plot Operations -------------------------------
    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
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

    def __copy__(self):
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            spanset_copy
        """
        inner_copy = spanset_copy(self._inner)
        return PeriodSet(_inner=inner_copy)

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            periodset_out
        """
        return periodset_out(self._inner)

    def __repr__(self):
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            periodset_out
        """
        return (f'{self.__class__.__name__}'
                f'({self})')

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            spanset_hash
        """
        return spanset_hash(self._inner)

