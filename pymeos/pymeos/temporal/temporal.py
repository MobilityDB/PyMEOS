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

import warnings
from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import Optional, List, Union, TYPE_CHECKING, Tuple, Set

from pandas import DataFrame
from pymeos_cffi import temporal_frechet_distance, temporal_time_split, temporal_at_timestampset, temporal_at_timestamp, \
    temporal_at_periodset, temporal_at_period, temporal_from_mfjson, temporal_as_hexwkb, temporal_intersects_timestamp, \
    datetime_to_timestamptz, temporal_intersects_timestampset, \
    temporal_intersects_period, temporal_intersects_periodset, temporal_time, interval_to_timedelta, temporal_duration, \
    temporal_timespan, temporal_num_instants, temporal_num_timestamps, timestamptz_to_datetime, \
    temporal_start_timestamp, temporal_end_timestamp, temporal_timestamp_n, temporal_timestamps, temporal_shift_tscale, \
    timedelta_to_interval, temporal_hash, temporal_copy, temporal_as_mfjson, teq_temporal_temporal, \
    tlt_temporal_temporal, tle_temporal_temporal, tne_temporal_temporal, tge_temporal_temporal, tgt_temporal_temporal, \
    after_temporal_period, after_temporal_periodset, after_temporal_timestamp, after_temporal_timestampset, \
    after_temporal_temporal, before_temporal_temporal, before_temporal_timestampset, before_temporal_timestamp, \
    before_temporal_periodset, before_temporal_period, overafter_temporal_period, overafter_temporal_periodset, \
    overafter_temporal_timestamp, overafter_temporal_timestampset, overafter_temporal_temporal, \
    overbefore_temporal_period, overbefore_temporal_periodset, overbefore_temporal_timestamp, \
    overbefore_temporal_timestampset, overbefore_temporal_temporal, temporal_from_hexwkb, temporal_start_instant, \
    temporal_end_instant, temporal_instant_n, temporal_instants, temporal_interpolation, temporal_max_instant, \
    temporal_min_instant, temporal_segments, temporal_dyntimewarp_distance, temporal_dyntimewarp_path, \
    temporal_frechet_path, temporal_minus_period, temporal_minus_periodset, temporal_minus_timestamp, \
    temporal_minus_timestampset, temporal_to_tinstant, temporal_to_tsequence, temporal_to_tsequenceset, \
    temporal_to_tdiscseq, temporal_append_tinstant, temporal_step_to_linear, temporal_merge, temporal_merge_array, \
    temporal_at_max, temporal_at_min, temporal_minus_max, temporal_minus_min, adjacent_temporal_period, \
    adjacent_temporal_periodset, adjacent_temporal_timestamp, adjacent_temporal_timestampset, \
    adjacent_temporal_temporal, contained_temporal_temporal, contained_temporal_timestampset, \
    contained_temporal_timestamp, contained_temporal_periodset, contained_temporal_period, contains_temporal_period, \
    contains_temporal_periodset, contains_temporal_timestamp, contains_temporal_timestampset, \
    contains_temporal_temporal, overlaps_temporal_temporal, overlaps_temporal_timestampset, overlaps_temporal_timestamp, \
    overlaps_temporal_periodset, overlaps_temporal_period, same_temporal_temporal, same_temporal_timestampset, \
    same_temporal_timestamp, same_temporal_periodset, same_temporal_period, temporal_to_period, pg_timestamptz_in, \
    pg_interval_in

from .interpolation import TInterpolation
from ..time import Period, PeriodSet, TimestampSet

if TYPE_CHECKING:
    from .tsequence import TSequence
    from .tsequenceset import TSequenceSet
    from .tinstant import TInstant

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class Temporal(ABC):
    __slots__ = ['_inner']
    """
    Abstract class for representing temporal values of any subtype.
    """

    BaseClass = None
    """
    Class of the base type, for example, ``float`` for ``TFloat``
    """

    BaseClassDiscrete = None
    """
    Boolean value that states whether the base type is discrete or not, 
    for example, ``True`` for ``int`` and ``False`` for ``float``
    """

    ComponentClass = None
    """
    Class of the components, for example, 

    1. ``TFloatInst`` for both ``TFloatI`` and ``TFloatSeq``
    2. ``TFloatSeq`` for ``TFloatS``.
    """

    _parse_function = None

    @classmethod
    @abstractmethod
    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, one of ``'Instant'``,
        ``'InstantSet'``, ``'Sequence'``, or ``'SequenceSet'``.
        """
        pass

    @property
    def interpolation(self) -> TInterpolation:
        """
        Interpolation of the temporal value, which is either ``'Linear'``, ``'Stepwise'`` or ``'Discrete'``.
        """
        val = temporal_interpolation(self._inner)
        if val == 'Discrete':
            return TInterpolation.DISCRETE
        elif val == 'Linear':
            return TInterpolation.LINEAR
        elif val == 'Stepwise':
            return TInterpolation.STEPWISE
        else:
            return TInterpolation.NONE

    @property
    @abstractmethod
    def value_set(self) -> Set:
        """
        List of distinct values taken by the temporal value.
        """
        pass

    @property
    def values(self) -> List:
        """
        List values taken by the temporal value.
        """
        return [i.value for i in self.instants]

    @property
    @abstractmethod
    def start_value(self):
        """
        Start value.
        """
        pass

    @property
    @abstractmethod
    def end_value(self):
        """
        End value.
        """
        pass

    @property
    def min_value(self):
        """
        Minimum value.
        """
        return min(self.value_set)

    @property
    def max_value(self):
        """
        Maximum value.
        """
        return max(self.value_set)

    @abstractmethod
    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        pass

    @property
    def time(self) -> PeriodSet:
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet(_inner=temporal_time(self._inner))

    @property
    def duration(self) -> timedelta:
        """
        Interval on which the temporal value is defined.
        """
        return interval_to_timedelta(temporal_duration(self._inner))

    @property
    def timespan(self) -> timedelta:
        """
        Interval on which the temporal value is defined ignoring potential
        time gaps.
        """
        return interval_to_timedelta(temporal_timespan(self._inner))

    @property
    def period(self) -> Period:
        """
        Period on which the temporal value is defined ignoring potential
        time gaps.
        """
        return Period(_inner=temporal_to_period(self._inner))

    @property
    def num_instants(self) -> int:
        """
        Number of distinct instants.
        """
        return temporal_num_instants(self._inner)

    @property
    def start_instant(self):
        """
         Start instant.
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_start_instant(self._inner))

    @property
    def end_instant(self):
        """
        End instant.
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_end_instant(self._inner))

    @property
    def max_instant(self):
        """
        Max instant.
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_max_instant(self._inner))

    @property
    def min_instant(self):
        """
        Min instant.
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_min_instant(self._inner))

    def instant_n(self, n: int):
        """
        N-th instant.
        """
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(temporal_instant_n(self._inner, n))

    @property
    def instants(self):
        """
        List of instants.
        """
        from ..factory import _TemporalFactory
        ins, count = temporal_instants(self._inner)
        return [_TemporalFactory.create_temporal(ins[i]) for i in range(count)]

    @property
    def num_timestamps(self) -> int:
        """
        Number of distinct timestamps.
        """
        return temporal_num_timestamps(self._inner)

    @property
    def start_timestamp(self) -> datetime:
        """
        Start timestamp.
        """
        return timestamptz_to_datetime(temporal_start_timestamp(self._inner))

    @property
    def end_timestamp(self) -> datetime:
        """
        End timestamp.
        """
        return timestamptz_to_datetime(temporal_end_timestamp(self._inner))

    def timestamp_n(self, n: int) -> datetime:
        """
        N-th timestamp.
        """
        return timestamptz_to_datetime(temporal_timestamp_n(self._inner, n))

    @property
    def timestamps(self) -> List[datetime]:
        """
        List of timestamps.
        """
        ts, count = temporal_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    @property
    def segments(self) -> List[TSequence]:
        seqs, count = temporal_segments(self._inner)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(seqs[i]) for i in range(count)]

    def shift_tscale(self, shift_delta: Optional[timedelta] = None,
                     scale_delta: Optional[timedelta] = None) -> Temporal:
        """
        Shift the temporal value by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        scaled = temporal_shift_tscale(
            self._inner,
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None
        )
        return Temporal._factory(scaled)

    def to_instant(self) -> TInstant:
        inst = temporal_to_tinstant(self._inner)
        return Temporal._factory(inst)

    def to_sequence(self, discrete: bool = False) -> TSequence:
        seq = temporal_to_tsequence(self._inner) if not discrete else temporal_to_tdiscseq(self._inner)
        return Temporal._factory(seq)

    def to_sequenceset(self) -> TSequenceSet:
        ss = temporal_to_tsequenceset(self._inner)
        return Temporal._factory(ss)

    def to_dataframe(self) -> DataFrame:
        data = {
            'time': self.timestamps,
            'value': [i.value for i in self.instants]
        }
        return DataFrame(data).set_index(keys='time')

    def append(self, instant: TInstant, expand: bool = False) -> Temporal:
        new_temp = temporal_append_tinstant(self._inner, instant._inner, expand)
        return Temporal._factory(new_temp)

    def merge(self, other: Temporal) -> Temporal:
        new_temp = temporal_merge(self._inner, other._inner)
        return Temporal._factory(new_temp)

    def merge_array(self, others: List[Temporal]) -> Temporal:
        new_temp = temporal_merge_array([self._inner, *(o._inner for o in others)], len(others) + 1)
        return Temporal._factory(new_temp)

    def to_linear(self) -> Temporal:
        new_temp = temporal_step_to_linear(self._inner)
        return Temporal._factory(new_temp)

    def intersects(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        if isinstance(other, Period):
            return temporal_intersects_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return temporal_intersects_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return temporal_intersects_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return temporal_intersects_timestampset(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[datetime, TimestampSet, Period, PeriodSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return after_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return after_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return after_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return after_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[datetime, TimestampSet, Period, PeriodSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return before_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return before_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return before_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return before_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[datetime, TimestampSet, Period, PeriodSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return overafter_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overafter_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overafter_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overafter_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[datetime, TimestampSet, Period, PeriodSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return overbefore_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overbefore_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overbefore_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overbefore_temporal_temporal(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def at(self, other: Union[datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, Period):
            result = temporal_at_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            result = temporal_at_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            result = temporal_at_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            result = temporal_at_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def at_max(self) -> Temporal:
        result = temporal_at_max(self._inner)
        return Temporal._factory(result)

    def at_min(self) -> Temporal:
        result = temporal_at_min(self._inner)
        return Temporal._factory(result)

    def minus(self, other: Union[datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
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

    def minus_max(self) -> Temporal:
        result = temporal_minus_max(self._inner)
        return Temporal._factory(result)

    def minus_min(self) -> Temporal:
        result = temporal_minus_min(self._inner)
        return Temporal._factory(result)

    def is_adjacent(self, other: Union[Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return adjacent_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return adjacent_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return adjacent_temporal_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(container, Period):
            return contained_temporal_period(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_temporal_periodset(self._inner, container._inner)
        elif isinstance(container, datetime):
            return contained_temporal_timestamp(self._inner, datetime_to_timestamptz(container))
        elif isinstance(container, TimestampSet):
            return contained_temporal_timestampset(self._inner, container._inner)
        elif isinstance(container, Temporal):
            return contained_temporal_temporal(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(content, Period):
            return contains_temporal_period(self._inner, content._inner)
        elif isinstance(content, PeriodSet):
            return contains_temporal_periodset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_temporal_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_temporal_timestampset(self._inner, content._inner)
        elif isinstance(content, Temporal):
            return contains_temporal_temporal(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return overlaps_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return overlaps_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overlaps_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overlaps_temporal_timestampset(self._inner, other._inner)
        elif isinstance(other, Temporal):
            return overlaps_temporal_temporal(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, Period):
            return same_temporal_period(self._inner, other._inner)
        elif isinstance(other, PeriodSet):
            return same_temporal_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return same_temporal_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return same_temporal_timestampset(self._inner, other._inner)
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
        Compute the  between two temporal values.
        """
        matches, count = temporal_frechet_path(self._inner, other._inner)
        return [(matches[i].i, matches[i].j) for i in range(count)]

    def dyntimewarp_path(self, other: Temporal) -> List[Tuple[int, int]]:
        """
        Computes the Dynamic Time Warp path between two temporal values.
        """
        matches, count = temporal_dyntimewarp_path(self._inner, other._inner)
        return [(matches[i].i, matches[i].j) for i in range(count)]

    def time_split(self, start: Union[str, datetime], duration: Union[str, timedelta]) -> List[Temporal]:
        st = datetime_to_timestamptz(start) if isinstance(start, datetime) else pg_timestamptz_in(start, -1)
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
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

    def temporal_less(self, other: Temporal) -> Temporal:
        """
        Temporal less than
        """
        self.__assert_comparable(other)
        result = tlt_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Temporal) -> Temporal:
        """
        Temporal less or equal
        """
        self.__assert_comparable(other)
        result = tle_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_equal(self, other: Temporal) -> Temporal:
        """
        Temporal equality
        """
        self.__assert_comparable(other)
        result = teq_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Temporal) -> Temporal:
        """
        Temporal inequality
        """
        self.__assert_comparable(other)
        result = tne_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Temporal) -> Temporal:
        """
        Temporal greater or equal
        """
        self.__assert_comparable(other)
        result = tge_temporal_temporal(self._inner, other._inner)
        return Temporal._factory(result)

    def temporal_greater(self, other: Temporal) -> Temporal:
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
        return self.__class__(_inner=inner_copy)

    @abstractmethod
    def as_wkt(self):
        pass

    def as_mfjson(self, with_bbox: bool = True, flags: int = 3, precision: int = 6, srs: Optional[str] = None) -> str:
        return temporal_as_mfjson(self._inner, with_bbox, flags, precision, srs)

    def as_hexwkb(self) -> str:
        return temporal_as_hexwkb(self._inner, 0)[0]

    @staticmethod
    def from_merge(*temporals: Temporal) -> Temporal:
        result = temporal_merge_array([temp._inner for temp in temporals], len(temporals))
        return Temporal._factory(result)

    @staticmethod
    def from_merge_array(temporals: List[Temporal]) -> Temporal:
        result = temporal_merge_array([temp._inner for temp in temporals], len(temporals))
        return Temporal._factory(result)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Temporal:
        result = temporal_from_hexwkb(hexwkb)
        return Temporal._factory(result)

    @staticmethod
    def from_mfjson(mfjson: str) -> Temporal:
        result = temporal_from_mfjson(mfjson)
        return Temporal._factory(result)

    @staticmethod
    def _factory(inner) -> Temporal:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(inner)
