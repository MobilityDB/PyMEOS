from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Union, overload, TYPE_CHECKING, get_args

from dateutil.parser import parse
from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from ..boxes import Box
    from .periodset import PeriodSet
    from .timestampset import TimestampSet
    from .time import Time


class Period:
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

    def __init__(self, string: Optional[str] = None, *, lower: Optional[Union[str, datetime]] = None,
                 upper: Optional[Union[str, datetime]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (lower is not None and upper is not None)), \
            "Either string must be not None or both lower and upper must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = period_in(string)
        else:
            lower_ts = pg_timestamptz_in(lower, -1) if isinstance(lower, str) else datetime_to_timestamptz(lower)
            upper_ts = pg_timestamptz_in(upper, -1) if isinstance(upper, str) else datetime_to_timestamptz(upper)
            self._inner = period_make(lower_ts, upper_ts, lower_inc, upper_inc)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Period:
        """
        Returns a `Period` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            span_from_hexwkb
        """
        result = span_from_hexwkb(hexwkb)
        return Period(_inner=result)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            span_as_hexwkb
        """
        return span_as_hexwkb(self._inner, -1)[0]

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

    def lower_inc(self) -> bool:
        """
        Returns whether the lower bound of the period is inclusive or not

        Returns:
            True if the lower bound of the period is inclusive and False otherwise

        MEOS Functions:
            span_lower_inc
        """
        return span_lower_inc(self._inner)

    def upper_inc(self) -> bool:
        """
        Returns whether the upper bound of the period is inclusive or not

        Returns:
            True if the upper bound of the period is inclusive and False otherwise

        MEOS Functions:
            span_upper_inc
        """
        return span_upper_inc(self._inner)

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
        return span_width(self._inner)

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
            period_shift_tscale
        """
        return self.shift_tscale(shift=delta)

    def tscale(self, duration: timedelta) -> Period:
        """
        Returns a new period that starts as ``self`` but has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').tscale(timedelta(days=2))
            >>> 'Period([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            period_shift_tscale
        """
        return self.shift_tscale(duration=duration)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> Period:
        """
        Returns a new period that starts at ``self`` shifted by ``shift`` and has duration ``duration``

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift_tscale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01])'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            period_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        modified = period_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return Period(_inner=modified)

    def expand(self, other: Period) -> Period:
        """
        Returns a new period that includes both ``self`` and ``other``

        Examples:
            >>> Period('[2000-01-01, 2000-01-04)').expand(Period('[2000-01-05, 2000-01-10]'))
            >>> 'Period([2000-01-01 00:00:00+01, 2000-01-10 00:00:00+01])'

        Args:
            other: :class:`Period` instance to expand the period

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            span_expand
        """
        copy = span_copy(self._inner)
        span_expand(other._inner, copy)
        return Period(_inner=copy)

    def to_periodset(self) -> PeriodSet:
        """
        Returns a period set containing ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .periodset import PeriodSet
        return PeriodSet(_inner=span_to_spanset(self._inner))

    def is_adjacent(self, other: Union[Time, Temporal, Box]) -> bool:
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
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return adjacent_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_spanset_span(other._inner, self._inner)
        elif isinstance(other, datetime):
            return adjacent_period_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return adjacent_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return adjacent_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, Temporal, Box]) -> bool:
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
        from .periodset import PeriodSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(container, Period):
            return contained_span_span(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_span_spanset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_span_span(self._inner, temporal_to_period(container._inner))
        elif isinstance(container, Box):
            return contained_span_span(self._inner, container.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Time, Temporal, Box]) -> bool:
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
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(content, Period):
            return contains_span_span(self._inner, content._inner)
        elif isinstance(content, PeriodSet):
            return contains_span_spanset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_period_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_span_span(self._inner, set_span(content._inner))
        elif isinstance(content, Temporal):
            return contains_span_span(self._inner, temporal_to_period(content._inner))
        elif isinstance(content, get_args(Box)):
            return contains_span_span(self._inner, content.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal, Box]) -> bool:
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
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return overlaps_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_spanset_span(other._inner, self._inner)
        elif isinstance(other, datetime):
            return overlaps_span_span(self._inner, timestamp_to_period(datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return overlaps_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return overlaps_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overlaps_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> Period('[2012-01-01, 2012-01-02)').is_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02)').is_before(Period('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_before(Period('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, before_period_timestamp,
            before_period_timestampset, before_period_temporal
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return left_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return left_span_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_timestamp_period(datetime_to_timestamptz(other), self._inner)
        if isinstance(other, TimestampSet):
            return left_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return left_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return left_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Examples:
            >>> Period('[2012-01-01, 2012-01-02)').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> Period('[2012-01-03, 2012-01-05]').is_over_or_before(Period('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overbefore_period_timestamp,
            overbefore_period_timestampset, overbefore_period_temporal
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return overleft_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overleft_span_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overleft_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return overleft_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overleft_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_after(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_over_or_after(Period('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overafter_period_timestamp,
            overafter_period_timestampset, overafter_period_temporal
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return overright_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overright_span_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_period_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overright_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return overright_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return overright_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self`` starts after ``other`` ends.

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]').is_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('(2012-01-02, 2012-01-03]').is_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> Period('[2012-01-02, 2012-01-03]').is_after(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, after_period_timestamp,
            after_period_timestampset, after_period_temporal
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Period):
            return right_span_span(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return right_span_spanset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_timestamp_period(datetime_to_timestamptz(other), self._inner)
        if isinstance(other, TimestampSet):
            return right_span_span(self._inner, set_span(other._inner))
        elif isinstance(other, Temporal):
            return right_span_span(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return right_span_span(self._inner, other.to_period()._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[Time, Temporal, Box]) -> bool:
        """
        Returns whether ``self`` and the bounding period of ``other`` is the same.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_period_temporal
        """
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Temporal):
            return span_eq(self._inner, temporal_to_period(other._inner))
        elif isinstance(other, get_args(Box)):
            return span_eq(self._inner, other.to_period()._inner)
        elif isinstance(other, Period):
            return span_eq(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return span_eq(self._inner, spanset_span(other._inner))
        elif isinstance(other, datetime):
            return span_eq(self._inner, timestamp_to_period(datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return span_eq(self._inner, set_span(other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
        from .periodset import PeriodSet
        from .timestampset import TimestampSet
        from ..temporal import Temporal
        from ..boxes import Box
        if isinstance(other, Temporal):
            return timedelta(seconds=distance_span_span(self._inner, temporal_to_period(other._inner)))
        elif isinstance(other, Period):
            return timedelta(seconds=distance_span_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return timedelta(seconds=distance_spanset_span(other._inner, self._inner))
        elif isinstance(other, datetime):
            return timedelta(seconds=distance_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return timedelta(seconds=distance_span_span(self._inner, set_span(other._inner)))
        elif isinstance(other, get_args(Box)):
            return timedelta(seconds=distance_span_span(self._inner, other.to_period()._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
            result = intersection_spanset_span(set_to_spanset(other._inner), self._inner)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = intersection_span_span(self._inner, other._inner)
            return Period(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return PeriodSet(_inner=result) if result is not None else None
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = minus_span_spanset(self._inner, set_to_spanset(other._inner))
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, Period):
            result = minus_span_span(self._inner, other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        elif isinstance(other, PeriodSet):
            result = minus_span_spanset(self._inner, other._inner)
            return PeriodSet(_inner=result) if result is not None else None
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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
            return PeriodSet(_inner=union_period_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return PeriodSet(_inner=union_spanset_span(set_to_spanset(other._inner), self._inner))
        if isinstance(other, Period):
            return PeriodSet(_inner=union_span_span(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_spanset_span(other._inner, self._inner))
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
        intersection_span_span, intersection_spanset_span, intersection_period_timestamp
        """
        return self.intersection(other)

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        union_period_timestamp, union_spanset_span, union_span_span
        """
        return self.union(other)

    def __sub__(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        minus_period_timestamp, minus_span_spanset, minus_span_span
        """
        return self.minus(other)

    def __contains__(self, item):
        """
        Return whether ``self`` temporally contains ``item``.

        Examples:
            >>> Period('[2012-01-02, 2012-01-03]') in Period('[2012-01-01, 2012-01-04]')
            >>> True
            >>> Period('(2012-01-01, 2012-01-02)') in Period('[2012-01-01, 2012-01-02]')
            >>> True
            >>> Period('[2012-01-01, 2012-01-02]') in Period('(2012-01-01, 2012-01-02)')
            >>> False

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_period_timestamp,
            contains_period_timestampset, contains_period_temporal
        """
        return self.contains(item)

    def __eq__(self, other):
        """
        Return whether ``self`` and ``other`` are equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            span_eq
        """
        if isinstance(other, self.__class__):
            return span_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Return whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            span_neq
        """
        if isinstance(other, self.__class__):
            return span_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            span_lt
        """
        if isinstance(other, self.__class__):
            return span_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            span_le
        """
        if isinstance(other, self.__class__):
            return span_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            span_gt
        """
        if isinstance(other, self.__class__):
            return span_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            span_ge
        """
        if isinstance(other, self.__class__):
            return span_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`Period` from a database cursor. Used when automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return Period(string=value)

    def __copy__(self):
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            span_copy
        """
        inner_copy = span_copy(self._inner)
        return Period(_inner=inner_copy)

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            period_out
        """
        return period_out(self._inner)

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            span_hash
        """
        return span_hash(self._inner)

    def __repr__(self):
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            period_out
        """
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_period(self, *args, **kwargs)
