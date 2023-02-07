###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Union, TYPE_CHECKING, Tuple, Set, Generic, TypeVar, Type

from pandas import DataFrame
from pymeos_cffi import *

from .interpolation import TInterpolation
from ..time import *

if TYPE_CHECKING:
    from .tinstant import TInstant
    from ..main import TBool
TBase = TypeVar('TBase')
TG = TypeVar('TG', bound='Temporal[Any]')
TI = TypeVar('TI', bound='TInstant[Any]')
TS = TypeVar('TS', bound='TSequence[Any]')
TSS = TypeVar('TSS', bound='TSequenceSet[Any]')
Self = TypeVar('Self', bound='Temporal[Any]')


class Temporal(Generic[TBase, TG, TI, TS, TSS], ABC):
    __slots__ = ['_inner']
    """
    Abstract class for representing temporal values of any subtype.
    """

    BaseClass = None
    """
    Class of the base type, for example, ``float`` for ``TFloat``
    """

    ComponentClass = None
    """
    Class of the components, for example, 

    1. ``TFloatInst`` for both ``TFloatI`` and ``TFloatSeq``
    2. ``TFloatSeq`` for ``TFloatS``.
    """

    _parse_function = None

    def _expandable(self) -> bool:
        return False

    def interpolation(self) -> TInterpolation:
        """
        Returns the interpolation of `self`

        MEOS Functions:
            temporal_interpolation
        """
        val = temporal_interpolation(self._inner)
        return TInterpolation.from_string(val)

    @abstractmethod
    def value_set(self) -> Set[TBase]:
        """
        Returns the unique values in `self`.
        """
        pass

    def values(self) -> List[TBase]:
        """
        Returns the list of values taken by `self`.
        """
        return [i.value() for i in self.instants()]

    @abstractmethod
    def start_value(self) -> TBase:
        """
        Returns the starting value of `self`.
        """
        pass

    @abstractmethod
    def end_value(self) -> TBase:
        """
        Returns the end value of `self`.
        """
        pass

    def min_value(self) -> TBase:
        """
        Returns the minimum value that `self` takes.
        """
        return min(self.value_set())

    def max_value(self) -> TBase:
        """
        Returns the maximum value that `self` takes.
        """
        return max(self.value_set())

    @abstractmethod
    def value_at_timestamp(self, timestamp: datetime) -> TBase:
        """
        Returns the value that `self` takes at a certain moment.
        """
        pass

    def time(self) -> PeriodSet:
        """
        Returns the :class:`PeriodSet` on which `self` is defined.

        MEOS Functions:
            temporal_time
        """
        return PeriodSet(_inner=temporal_time(self._inner))

    def duration(self) -> timedelta:
        """
        Returns the duration of `self` taking into account any possible gap.

        MEOS Functions:
            temporal_duration
        """
        return interval_to_timedelta(temporal_duration(self._inner, False))

    def timespan(self) -> timedelta:
        """
        Returns the duration of `self` ignoring any potential gap.

        MEOS Functions:
            temporal_duration
        """
        return interval_to_timedelta(temporal_duration(self._inner, True))

    def period(self) -> Period:
        """
        Returns the :class:`Period` on which `self` is defined ignoring potential time gaps.

        MEOS Functions:
            temporal_to_period
        """
        return Period(_inner=temporal_to_period(self._inner))

    def num_instants(self) -> int:
        """
        Returns the number of instants in `self`.

        MEOS Functions:
            temporal_num_instants
        """
        return temporal_num_instants(self._inner)

    def start_instant(self) -> TI:
        """
        Returns the first instant in `self`.

        MEOS Functions:
            temporal_start_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_start_instant(self._inner))

    def end_instant(self) -> TI:
        """
        Returns the last instant in `self`.

        MEOS Functions:
            temporal_end_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_end_instant(self._inner))

    def max_instant(self) -> TI:
        """
        Returns the instant in `self` with the maximum value.

        MEOS Functions:
            temporal_max_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_max_instant(self._inner))

    def min_instant(self) -> TI:
        """
        Returns the instant in `self` with the minimum value.

        MEOS Functions:
            temporal_min_instant
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_min_instant(self._inner))

    def instant_n(self, n: int) -> TI:
        """
        Returns the n-th instant in `self`.

        MEOS Functions:
            temporal_instant_n
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_instant_n(self._inner, n))

    def instants(self) -> List[TI]:
        """
        Returns the instants in `self`.

        MEOS Functions:
            temporal_instants
        """
        from ..factory import _TemporalFactory
        ins, count = temporal_instants(self._inner)
        return [_TemporalFactory.create_temporal(ins[i]) for i in range(count)]

    def num_timestamps(self) -> int:
        """
        Returns the number of timestamps in `self`.

        MEOS Functions:
            temporal_num_timestamps
        """
        return temporal_num_timestamps(self._inner)

    def start_timestamp(self) -> datetime:
        """
        Returns the first timestamp in `self`.

        MEOS Functions:
            temporal_start_timestamps
        """
        return timestamptz_to_datetime(temporal_start_timestamp(self._inner))

    def end_timestamp(self) -> datetime:
        """
        Returns the last timestamp in `self`.

        MEOS Functions:
            temporal_end_timestamps
        """
        return timestamptz_to_datetime(temporal_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        Returns the n-th timestamp in `self`.

        MEOS Functions:
            temporal_timestamp_n
        """
        return timestamptz_to_datetime(temporal_timestamp_n(self._inner, n))

    def timestamps(self) -> List[datetime]:
        """
        Returns the timestamps in `self`.

        MEOS Functions:
            temporal_timestamps
        """
        ts, count = temporal_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    def segments(self) -> List[TS]:
        """
        Returns the temporal segments in `self`.

        MEOS Functions:
            temporal_segments
        """
        seqs, count = temporal_segments(self._inner)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(seqs[i]) for i in range(count)]

    def shift(self, delta: timedelta) -> Period:
        """
        Returns a new :class:`Temporal` that starts like ``self`` shifted by ``shift``.

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').shift(timedelta(days=2))
            >>> 'Period([2000-01-03 00:00:00+01, 2000-01-12 00:00:00+01])'

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        MEOS Functions:
            temporal_shift_tscale
        """
        return self.shift_tscale(shift=delta)

    def tscale(self, duration: timedelta) -> Period:
        """
        Returns a new :class:`Temporal` that starts like ``self``but has duration ``duration``.

        Examples:
            >>> Period('[2000-01-01, 2000-01-10]').tscale(timedelta(days=2))
            >>> 'Period([2000-01-01 00:00:00+01, 2000-01-03 00:00:00+01])'

        Args:
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        MEOS Functions:
            temporal_shift_tscale
        """
        return self.shift_tscale(duration=duration)

    def shift_tscale(self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None) -> Self:
        """
        Returns a new :class:`Temporal` that starts like ``self`` shifted by ``shift`` and has duration ``duration``.

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance representing the duration of the new period

        MEOS Functions:
            temporal_shift_tscale
        """
        assert shift is not None or duration is not None, 'shift and duration must not be both None'
        scaled = temporal_shift_tscale(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None
        )
        return Temporal._factory(scaled)

    def to_instant(self) -> TI:
        """
        Returns `self` as a :class:`TInstant`.

        MEOS Functions:
            temporal_to_tinstant
        """
        inst = temporal_to_tinstant(self._inner)
        return Temporal._factory(inst)

    def to_sequence(self, discrete: bool = False) -> TS:
        """
        Returns `self` as a :class:`TSequence`.

        Args:
            discrete: whether the sequence returned is discrete or continuous (stepwise or linear depending on subtype).

        MEOS Functions:
            temporal_to_tcontseq, temporal_to_tdiscseq
        """
        seq = temporal_to_tcontseq(self._inner) if not discrete else temporal_to_tdiscseq(self._inner)
        return Temporal._factory(seq)

    def to_sequenceset(self) -> TSS:
        """
        Returns `self` as a :class:`TSequenceSet`.

        MEOS Functions:
            temporal_to_tsequenceset
        """
        ss = temporal_to_tsequenceset(self._inner)
        return Temporal._factory(ss)

    def to_dataframe(self) -> DataFrame:
        """
        Returns `self` as a :class:`pd.DataFrame` with two columns: `time` and `value`.
        """
        data = {
            'time': self.timestamps,
            'value': [i.value() for i in self.instants()]
        }
        return DataFrame(data).set_index(keys='time')

    def append(self, instant: TInstant[TBase]) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with `instant` appended.

        MEOS Functions:
            temporal_append_tinstant
        """
        new_inner = temporal_append_tinstant(self._inner, instant._inner, self._expandable())
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def merge(self, other: Union[Temporal[TBase], List[Temporal[TBase]]]) -> TG:
        """
        Returns a new :class:`Temporal` object that is the result of merging `self` with `other`.

        MEOS Functions:
            temporal_merge, temporal_merge_array
        """
        if isinstance(other, Temporal):
            new_temp = temporal_merge(self._inner, other._inner)
        elif isinstance(other, list):
            new_temp = temporal_merge_array([self._inner, *(o._inner for o in other)], len(other) + 1)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(new_temp)

    def insert(self, other: TG, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with `other` inserted.

        Args:
            other: :class:`Temporal` object to insert in `self`
            connect: wether to connect the inserted elements with the existing elements.

        MEOS Functions:
            temporal_insert
        """
        new_inner = temporal_insert(self._inner, other._inner, connect)
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def update(self, other: TG, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` udpated with `other`.

        Args:
            other: :class:`Temporal` object to update `self` with
            connect: wether to connect the updated elements with the existing elements.

        MEOS Functions:
            temporal_update
        """
        new_inner = temporal_update(self._inner, other._inner, connect)
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    def delete(self, other: Time, connect: bool = False) -> TG:
        """
        Returns a new :class:`Temporal` object equal to `self` with elements at `other` removed.

        Args:
            other: :class:`Time` object to remove from `self`
            connect: wether to connect the potential gaps generated by the deletions.

        MEOS Functions:
            temporal_update
        """
        if isinstance(other, datetime):
            new_inner = temporal_delete_timestamp(self._inner, datetime_to_timestamptz(other), connect)
        elif isinstance(other, TimestampSet):
            new_inner = temporal_delete_timestampset(self._inner, other._inner, connect)
        elif isinstance(other, Period):
            new_inner = temporal_delete_period(self._inner, other._inner, connect)
        elif isinstance(other, PeriodSet):
            new_inner = temporal_delete_periodset(self._inner, other._inner, connect)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        if new_inner == self._inner:
            return self
        return Temporal._factory(new_inner)

    # TODO: Move to proper classes (Sequence[Set] with continuous base type)
    def to_linear(self: Self) -> Self:
        """
        Returns `self` transformed from stepwise to linear interpolation.

        MEOS Functions:
            temporal_step_to_linear
        """
        new_temp = temporal_step_to_linear(self._inner)
        return Temporal._factory(new_temp)

    def intersects(self, other: Time) -> bool:
        """
        Returns whther `self` transformed from stepwise to linear interpolation.

        MEOS Functions:
            temporal_step_to_linear
        """
        if isinstance(other, datetime):
            return temporal_overlaps_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return temporal_overlaps_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return temporal_overlaps_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return temporal_overlaps_periodset(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return after_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return after_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return after_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return after_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return before_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return before_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return before_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return before_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return overafter_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overafter_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return overafter_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overafter_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return overbefore_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overbefore_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return overbefore_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overbefore_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def at(self, other: Time) -> TG:
        if isinstance(other, datetime):
            result = temporal_at_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = temporal_at_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            result = temporal_at_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = temporal_at_periodset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def at_max(self) -> TG:
        result = temporal_at_max(self._inner)
        return Temporal._factory(result)

    def at_min(self) -> TG:
        result = temporal_at_min(self._inner)
        return Temporal._factory(result)

    def minus(self, other: Time) -> TG:
        if isinstance(other, Period):
            result = temporal_minus_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = temporal_minus_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            result = temporal_minus_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = temporal_minus_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def minus_max(self) -> TG:
        result = temporal_minus_max(self._inner)
        return Temporal._factory(result)

    def minus_min(self) -> TG:
        result = temporal_minus_min(self._inner)
        return Temporal._factory(result)

    def is_adjacent(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return adjacent_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return adjacent_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_temporal_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Time, Temporal]) -> bool:
        if isinstance(container, datetime):
            return contained_temporal_timestamp(self._inner, datetime_to_timestamptz(container))
        elif isinstance(container, TimestampSet):
            return contained_temporal_timestampset(self._inner, container._inner)
        elif isinstance(container, Period):
            return contained_temporal_period(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_temporal_periodset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_temporal_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Time, Temporal]) -> bool:
        if isinstance(content, datetime):
            return contains_temporal_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_temporal_timestampset(self._inner, content._inner)
        elif isinstance(content, Period):
            return contains_temporal_period(self._inner, content._inner)
        elif isinstance(content, PeriodSet):
            return contains_temporal_periodset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_temporal_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return overlaps_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overlaps_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return overlaps_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_temporal_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[Time, Temporal]) -> bool:
        if isinstance(other, datetime):
            return same_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return same_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Period):
            return same_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return same_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return same_temporal_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def frechet_distance(self, other: Temporal) -> float:
        """
        Compute the Frechet distance between two temporal values.
        """
        return temporal_frechet_distance(self._inner, other._inner)

    def dyntimewarp_distance(self, other: Temporal) -> float:
        """
        Computes the Dynamic Time Warp distance between two temporal values.
        """
        return temporal_dyntimewarp_distance(self._inner, other._inner)

    def frechet_path(self, other: Temporal) -> List[Tuple[int, int]]:
        """
        Compute the Frechet path between two temporal values.
        """
        matches, count = temporal_frechet_path(self._inner, other._inner)
        return [(matches[i].i, matches[i].j) for i in range(count)]

    def dyntimewarp_path(self, other: Temporal) -> List[Tuple[int, int]]:
        """
        Computes the Dynamic Time Warp path between two temporal values.
        """
        matches, count = temporal_dyntimewarp_path(self._inner, other._inner)
        return [(matches[i].i, matches[i].j) for i in range(count)]

    def time_split(self, start: Union[str, datetime], duration: Union[str, timedelta]) -> List[TG]:
        st = datetime_to_timestamptz(start) if isinstance(start, datetime) else pg_timestamptz_in(start, -1)
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
        tiles, new_count = temporal_time_split(self._inner, dt, st)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def time_split_n(self, n: int) -> List[TG]:
        st = temporal_start_timestamp(self._inner)
        dt = timedelta_to_interval((self.end_timestamp() - self.start_timestamp()) / n)
        tiles, new_count = temporal_time_split(self._inner, dt, st)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def __comparable(self, other: Temporal) -> bool:
        if not isinstance(other, Temporal):
            return False
        if self.BaseClass == other.BaseClass:
            return True
        if self.BaseClass in [int, float] and other.BaseClass in [int, float]:
            return True
        return False

    def __assert_comparable(self, other: Temporal) -> None:
        if not self.__comparable(other):
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def temporal_less(self, other: Temporal) -> TBool:
        """
        Temporal less than
        """
        self.__assert_comparable(other)
        result = tlt_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Temporal) -> TBool:
        """
        Temporal less or equal
        """
        self.__assert_comparable(other)
        result = tle_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_equal(self, other: Temporal) -> TBool:
        """
        Temporal equality
        """
        self.__assert_comparable(other)
        result = teq_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Temporal) -> TBool:
        """
        Temporal inequality
        """
        self.__assert_comparable(other)
        result = tne_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Temporal) -> TBool:
        """
        Temporal greater or equal
        """
        self.__assert_comparable(other)
        result = tge_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater(self, other: Temporal) -> TBool:
        """
        Temporal greater than
        """
        self.__assert_comparable(other)
        result = tgt_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def __lt__(self, other):
        """
        Temporal less than
        """
        return self.temporal_less(other)

    def __le__(self, other):
        """
        Temporal less or equal
        """
        return self.temporal_less_or_equal(other)

    def __eq__(self, other):
        """
        Temporal equality
        """
        return self.temporal_equal(other)

    def __ne__(self, other):
        """
        Temporal inequality
        """
        return self.temporal_not_equal(other)

    def __ge__(self, other):
        """
        Temporal greater or equal
        """
        return self.temporal_greater_or_equal(other)

    def __gt__(self, other):
        """
        Temporal greater than
        """
        return self.temporal_greater(other)

    def __hash__(self) -> int:
        return temporal_hash(self._inner)

    def __contains__(self, item):
        return self.contains(item)

    def __str__(self):
        """
        String
        """
        pass

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    def __copy__(self):
        inner_copy = temporal_copy(self._inner)
        return self.__class__._factory(inner_copy)

    @abstractmethod
    def as_wkt(self) -> str:
        pass

    def as_mfjson(self, with_bbox: bool = True, flags: int = 3, precision: int = 6, srs: Optional[str] = None) -> str:
        return temporal_as_mfjson(self._inner, with_bbox, flags, precision, srs)

    def as_hexwkb(self) -> str:
        return temporal_as_hexwkb(self._inner, 0)[0]

    @classmethod
    def from_merge(cls: Type[Self], *temporals: TG) -> Self:
        result = temporal_merge_array([temp._inner for temp in temporals], len(temporals))
        return Temporal._factory(result)

    @classmethod
    def from_merge_array(cls: Type[Self], temporals: List[TG]) -> Self:
        result = temporal_merge_array([temp._inner for temp in temporals], len(temporals))
        return Temporal._factory(result)

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str) -> Self:
        result = temporal_from_hexwkb(hexwkb)
        return Temporal._factory(result)

    @classmethod
    def from_mfjson(cls: Type[Self], mfjson: str) -> Self:
        result = temporal_from_mfjson(mfjson)
        return Temporal._factory(result)

    @classmethod
    def _factory(cls, inner):
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(inner)
