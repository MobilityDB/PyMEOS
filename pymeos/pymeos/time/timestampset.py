from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, List, Union, TYPE_CHECKING, overload

from dateutil.parser import parse
from pymeos_cffi import *

if TYPE_CHECKING:
    from ..temporal import Temporal
    from .period import Period
    from .periodset import PeriodSet
    from .time import Time


class TimestampSet:
    """
    Class for representing lists of distinct timestamp values.

    ``TimestampSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TimestampSet(string='{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TimestampSet(timestamp_list=['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TimestampSet(timestamp_list=[parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])

    """

    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *, timestamp_list: Optional[List[Union[str, datetime]]] = None,
                 _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (timestamp_list is not None)), \
            "Either string must be not None or timestamp_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = timestampset_in(string)
        else:
            times = [pg_timestamp_in(ts, -1) if isinstance(ts, str) else datetime_to_timestamptz(ts)
                     for ts in timestamp_list]
            self._inner = timestampset_make(times, len(times))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> TimestampSet:
        """
        Returns a `TimestampSet` from its WKB representation in hex-encoded ASCII.
        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`TimestampSet` instance

        MEOS Functions:
            timestampset_from_hexwkb
        """
        result = timestampset_from_hexwkb(hexwkb)
        return TimestampSet(_inner=result)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.
        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            timestampset_as_hexwkb
        """
        return timestampset_as_hexwkb(self._inner, -1)[0]

    def timespan(self) -> timedelta:
        """
        Returns the duration of the time ignoring gaps, i.e. the duration from the
        first timestamp to the last one.

        Returns:
            A :class:`datetime.timedelta` instance representing the duration of the period

        MEOS Functions:
            timestampset_timespan
        """
        return interval_to_timedelta(timestampset_timespan(self._inner))

    def period(self) -> Period:
        """
        Returns a period that encompasses ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            timestampset_start_timestamp, timestampset_end_timestamp
        """
        from .period import Period
        return Period(lower=pg_timestamptz_out(timestampset_start_timestamp(self._inner)),
                      upper=pg_timestamptz_out(timestampset_end_timestamp(self._inner)),
                      lower_inc=True, upper_inc=True)

    def to_periodset(self) -> PeriodSet:
        """
        Returns a PeriodSet that contains a Period for each Timestamp in ``self``.

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_to_periodset
        """
        from .periodset import PeriodSet
        return PeriodSet(_inner=timestampset_to_periodset(self._inner))

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            timestampset_num_timestamps
        """
        return timestampset_num_timestamps(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_start_timestamp
        """
        return timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_end_timestamp
        """
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in ``self``.
        Returns:
            A :class:`datetime` instance

        MEOS Functions:
            timestampset_timestamp_n
        """
        return timestamptz_to_datetime(timestampset_timestamp_n(self._inner, n))

    def timestamps(self) -> List[datetime]:
        """
        Returns the list of distinc timestamps in ``self``.
        Returns:
            A :class:`list[datetime]` instance

        MEOS Functions:
            timestampset_timestamps
        """
        tss = timestampset_timestamps(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_timestamps())]

    def shift(self, delta: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that is the result of shifting ``self`` by ``delta``

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift(timedelta(days=2))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01})'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_tscale
        """
        return self.shift_tscale(shift=delta)

    def tscale(self, duration: timedelta) -> TimestampSet:
        """
        Returns a new TimestampSet that starts as ``self`` but has duration ``duration``

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').tscale(timedelta(days=2))
            >>> 'TimestampSet({2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01})'

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_tscale
        """
        return self.shift_tscale(duration=duration)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> TimestampSet:
        """
        Returns a new TimestampSet that starts at ``self`` shifted by ``shift`` and has duration ``duration``

        Examples:
            >>> TimestampSet('{2000-01-01, 2000-01-10}').shift_tscale(shift=timedelta(days=2), duration=timedelta(days=4))
            >>> 'TimestampSet({2000-01-03 00:00:00+01, 2000-01-07 00:00:00+01})'

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        Returns:
            A new :class:`PeriodSet` instance

        MEOS Functions:
            timestampset_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and scale deltas must not be both None'
        tss = timestampset_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return TimestampSet(_inner=tss)

    def is_adjacent(self, other: Union[Period, PeriodSet, Temporal]) -> bool:
        """
        Returns whether ``self`` is temporally adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

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
            adjacent_timestampset_period, adjacent_timestampset_periodset, adjacent_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return adjacent_timestampset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
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
            contained_timestampset_period, contained_timestampset_periodset, contained_timestampset_timestampset,
            contained_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(container, Period):
            return contained_timestampset_period(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_timestampset_periodset(self._inner, container._inner)
        elif isinstance(container, TimestampSet):
            return contained_timestampset_timestampset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_timestampset_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

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
            contains_timestampset_timestamp, contains_timestampset_timestampset, contains_timestampset_temporal
        """
        from ..temporal import Temporal
        if isinstance(content, datetime):
            return contains_timestampset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_timestampset_timestampset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_timestampset_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet, Temporal]) -> bool:
        """
        Returns whether ``self`` temporally overlaps ``other``. That is, both share at least an instant

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
            overlaps_timestampset_period, overlaps_timestampset_periodset, overlaps_timestampset_timestampset,
            overlaps_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        from ..temporal import Temporal
        if isinstance(other, Period):
            return overlaps_timestampset_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Time) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, the first timestamp in ``self``
        is after ``other``.

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(TimestampSet('{2012-01-01}'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_after(Period('[2012-01-01, 2012-01-02]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            after_timestampset_period, after_timestampset_periodset, after_timestampset_timestamp,
            after_timestampset_timestampset, after_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return after_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return after_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return after_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Time) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(TimestampSet('{2012-01-03}'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(Period('(2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_before(Period('[2012-01-02, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            before_timestampset_period, before_timestampset_periodset, before_timestampset_timestamp,
            before_timestampset_timestampset, before_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return before_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return before_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return before_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Time) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Examples:
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-02)'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-02]'))
            >>> True
            >>> TimestampSet('{2012-01-02, 2012-01-03}').is_over_or_after(Period('[2012-01-01, 2012-01-03]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overafter_timestampset_period, overafter_timestampset_periodset, overafter_timestampset_timestamp,
            overafter_timestampset_timestampset, overafter_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return overafter_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overafter_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overafter_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Time) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Examples:
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-01, 2012-01-02}').is_over_or_before(Period('[2012-01-02, 2012-01-03]'))
            >>> True
            >>> TimestampSet('{2012-01-03, 2012-01-05}').is_over_or_before(Period('[2012-01-01, 2012-01-04]'))
            >>> False

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overbefore_timestampset_period, overbefore_timestampset_periodset, overbefore_timestampset_timestamp,
            overbefore_timestampset_timestampset, overbefore_timestampset_temporal
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return overbefore_timestampset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overbefore_timestampset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_timestampset_timestamp(self._inner, datetime_to_timestamptz(other))
        if isinstance(other, TimestampSet):
            return overbefore_timestampset_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Temporal) -> bool:
        """
        Returns whether ``self`` and ``other`` have the same temporal dimension.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_timestampset_temporal
        """
        from ..temporal import Temporal
        if isinstance(other, Temporal):
            return same_timestampset_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def distance(self, other: Time) -> timedelta:
        """
        Returns the temporal distance between ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_timestampset_period, distance_timestampset_periodset, distance_timestampset_timestamp, distance_timestampset_timestampset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return timedelta(seconds=distance_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return timedelta(seconds=distance_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timedelta(seconds=distance_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return timedelta(seconds=distance_timestampset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def intersection(self, other: datetime) -> datetime:
        ...

    @overload
    def intersection(self, other: Union[Period, PeriodSet, TimestampSet]) -> TimestampSet:
        ...

    def intersection(self, other: Time) -> Union[datetime, TimestampSet]:
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_timestampset_period, intersection_timestampset_periodset, intersection_timestampset_timestamp,
            intersection_timestampset_timestampset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return TimestampSet(_inner=intersection_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return TimestampSet(_inner=intersection_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return timestamptz_to_datetime(
                intersection_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=intersection_timestampset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def minus(self, other: Time) -> TimestampSet:
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            minus_timestampset_period, minus_timestampset_periodset, minus_timestampset_timestamp,
            minus_timestampset_timestampset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return TimestampSet(_inner=minus_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return TimestampSet(_inner=minus_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return TimestampSet(_inner=minus_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=minus_timestampset_timestampset(self._inner, other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    @overload
    def union(self, other: Union[Period, PeriodSet]) -> PeriodSet:
        ...

    @overload
    def union(self, other: Union[datetime, TimestampSet]) -> TimestampSet:
        ...

    def union(self, other: Time) -> Union[PeriodSet, TimestampSet]:
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_timestampset_period, union_timestampset_periodset, union_timestampset_timestamp,
            union_timestampset_timestampset
        """
        from .period import Period
        from .periodset import PeriodSet
        if isinstance(other, Period):
            return PeriodSet(_inner=union_timestampset_period(self._inner, other._inner))
        elif isinstance(other, PeriodSet):
            return PeriodSet(_inner=union_timestampset_periodset(self._inner, other._inner))
        elif isinstance(other, datetime):
            return TimestampSet(_inner=union_timestampset_timestamp(self._inner, datetime_to_timestamptz(other)))
        elif isinstance(other, TimestampSet):
            return TimestampSet(_inner=union_timestampset_timestampset(self._inner, other._inner))
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
            intersection_timestampset_period, intersection_timestampset_periodset, intersection_timestampset_timestamp,
            intersection_timestampset_timestampset
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
            union_timestampset_period, union_timestampset_periodset, union_timestampset_timestamp,
            union_timestampset_timestampset
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
            minus_timestampset_period, minus_timestampset_periodset, minus_timestampset_timestamp,
            minus_timestampset_timestampset
        """
        return self.minus(other)

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
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_timestampset_timestamp, contains_timestampset_timestampset, contains_timestampset_temporal
        """
        return self.contains(item)

    def __eq__(self, other):
        """
        Returns whether ``self`` and ``other`` are equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            timestampset_eq
        """
        if isinstance(other, self.__class__):
            return timestampset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            timestampset_ne
        """
        if isinstance(other, self.__class__):
            return timestampset_ne(self._inner, other._inner)
        return True

    def __cmp__(self, other):
        """
        Returns the result of comparing ``self`` and ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            -1 if less than, 0 if equal, and 1 if greater than

        MEOS Functions:
            timestampset_cmp
        """
        if isinstance(other, self.__class__):
            return timestampset_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            timestampset_lt
        """
        if isinstance(other, self.__class__):
            return timestampset_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            timestampset_le
        """
        if isinstance(other, self.__class__):
            return timestampset_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            timestampset_gt
        """
        if isinstance(other, self.__class__):
            return timestampset_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            timestampset_ge
        """
        if isinstance(other, self.__class__):
            return timestampset_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        if not value:
            return None
        return TimestampSet(string=value)

    def __copy__(self):
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Period` instance

        MEOS Functions:
            timestampset_copy
        """
        inner_copy = timestampset_copy(self._inner)
        return TimestampSet(_inner=inner_copy)

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            timestampset_out
        """
        return timestampset_out(self._inner)

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            timestampset_hash
        """
        return timestampset_hash(self._inner)

    def __repr__(self):
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            timestampset_out
        """
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import TimePlotter
        return TimePlotter.plot_timestampset(self, *args, **kwargs)
