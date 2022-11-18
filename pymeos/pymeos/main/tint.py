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

from abc import ABC
from typing import Optional, Union, List, TYPE_CHECKING, Set

from pymeos_cffi import *
from spans.types import intrange, floatrange

from .tnumber import TNumber
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import *

if TYPE_CHECKING:
    from ..boxes import TBox
    from .tfloat import TFloat


class TInt(TNumber[int, 'TInt', 'TIntInst', 'TIntSeq', 'TIntSeqSet'], ABC):
    BaseClass = int
    _parse_function = tint_in

    def is_adjacent(self, other: Union[int,
                                       TBox, TNumber, floatrange, intrange,
                                       Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return adjacent_tint_int(self._inner, other)
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[int,
                                               TBox, TNumber, floatrange, intrange,
                                               Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(container, int):
            return contained_tint_int(self._inner, container)
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[int,
                                      TBox, TNumber, floatrange, intrange,
                                      Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(content, int):
            return contains_tint_int(self._inner, content)
        else:
            return super().contains(content)

    def overlaps(self, other: Union[int,
                                    TBox, TNumber, floatrange, intrange,
                                    Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return overlaps_tint_int(self._inner, other)
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[int,
                                   TBox, TNumber, floatrange, intrange,
                                   Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return same_tint_int(self._inner, other)
        else:
            return super().is_same(other)

    def always_less(self, value: int) -> bool:
        return tint_always_lt(self._inner, value)

    def always_less_or_equal(self, value: int) -> bool:
        return tint_always_le(self._inner, value)

    def always_equal(self, value: int) -> bool:
        return tint_always_eq(self._inner, value)

    def always_not_equal(self, value: int) -> bool:
        return not tint_ever_eq(self._inner, value)

    def always_greater_or_equal(self, value: int) -> bool:
        return not tint_ever_lt(self._inner, value)

    def always_greater(self, value: int) -> bool:
        return not tint_ever_le(self._inner, value)

    def ever_less(self, value: int) -> bool:
        return tint_ever_lt(self._inner, value)

    def ever_less_or_equal(self, value: int) -> bool:
        return tint_ever_le(self._inner, value)

    def ever_equal(self, value: int) -> bool:
        return tint_ever_eq(self._inner, value)

    def ever_not_equal(self, value: int) -> bool:
        return not tint_always_eq(self._inner, value)

    def ever_greater_or_equal(self, value: int) -> bool:
        return not tint_always_lt(self._inner, value)

    def ever_greater(self, value: int) -> bool:
        return not tint_always_le(self._inner, value)

    def never_less(self, value: int) -> bool:
        return not tint_ever_lt(self._inner, value)

    def never_less_or_equal(self, value: int) -> bool:
        return not tint_ever_le(self._inner, value)

    def never_equal(self, value: int) -> bool:
        return not tint_ever_eq(self._inner, value)

    def never_not_equal(self, value: int) -> bool:
        return tint_always_eq(self._inner, value)

    def never_greater_or_equal(self, value: int) -> bool:
        return tint_always_lt(self._inner, value)

    def never_greater(self, value: int) -> bool:
        return tint_always_le(self._inner, value)

    def temporal_less(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = tlt_tint_int(self._inner, other)
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = tle_tint_int(self._inner, other)
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_equal(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = teq_tint_int(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = tne_tint_int(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = tge_tint_int(self._inner, other)
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[int, Temporal]) -> Temporal:
        if isinstance(other, int):
            result = tgt_tint_int(self._inner, other)
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    def at(self, other: Union[int, List[int],
                              intrange, floatrange, List[intrange], List[floatrange], TBox,
                              datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, int):
            result = tint_at_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], int):
            result = tint_at_values(self._inner, other)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[int, List[int],
                                 intrange, floatrange, List[intrange], List[floatrange], TBox,
                                 datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, int):
            result = tint_minus_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], int):
            result = tint_minus_values(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def nearest_approach_distance(self, other: Union[int, float, TNumber, TBox]) -> float:
        if isinstance(other, int):
            return nad_tint_int(self._inner, other)
        elif isinstance(other, TInt):
            return nad_tint_tint(self._inner, other._inner)
        else:
            return super(TInt, self).nearest_approach_distance(other)

    def to_tfloat(self) -> TFloat:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tint_to_tfloat(self._inner))

    def to_intrange(self) -> intrange:
        return intspan_to_intrange(tnumber_to_span(self._inner))

    @staticmethod
    def from_base(value: int, base: Temporal) -> TInt:
        result = tint_from_base(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: int, base: Time) -> TInt:
        if isinstance(base, datetime):
            return TIntInst(_inner=tintinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TIntSeq(_inner=tintdiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TIntSeq(_inner=tintseq_from_base_time(value, base._inner))
        elif isinstance(base, PeriodSet):
            return TIntSeqSet(_inner=tintseqset_from_base_time(value, base._inner))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TIntInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TIntSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TIntSeqSet(string=value)
            else:
                return TIntSeq(string=value)
        raise Exception("ERROR: Could not parse temporal integer value")

    @property
    def value_range(self) -> intrange:
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return self.to_intrange()

    @property
    def start_value(self) -> int:
        """
        Start value.
        """
        return tint_start_value(self._inner)

    @property
    def end_value(self) -> int:
        """
        End value.
        """
        return tint_end_value(self._inner)

    @property
    def value_set(self) -> Set[int]:
        """
        List of distinct values.
        """
        values, count = tint_values(self._inner)
        return {values[i] for i in range(count)}

    @property
    def min_value(self) -> int:
        """
        Minimum value.
        """
        return tint_min_value(self._inner)

    @property
    def max_value(self) -> int:
        """
        Maximum value.
        """
        return tint_max_value(self._inner)

    def value_at_timestamp(self, timestamp) -> int:
        """
        Value at timestamp.
        """
        return tint_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def value_split(self, start: int, size: int) -> List[Temporal]:
        tiles, new_count = tint_value_split(self._inner, size, start)
        return [Temporal._factory(tiles[i]) for i in range(new_count)]

    def time_value_split(self, value_start: int, value_size: int, time_start: Union[str, datetime],
                         duration: Union[str, timedelta]) -> List[Temporal]:
        st = datetime_to_timestamptz(time_start) if isinstance(time_start, datetime) \
            else pg_timestamptz_in(time_start, -1)
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
        tiles, new_count = tint_value_time_split(self._inner, value_size, value_start, dt, st)
        return [Temporal._factory(tiles[i]) for i in range(new_count)]

    def __str__(self):
        return tint_out(self._inner)

    def as_wkt(self):
        return tint_out(self._inner)


class TIntInst(TInstant[int, 'TInt', 'TIntInst', 'TIntSeq', 'TIntSeqSet'], TInt):
    _make_function = tintinst_make
    _cast_function = int

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, int]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TIntSeq(TSequence[int, 'TInt', 'TIntInst', 'TIntSeq', 'TIntSeqSet'], TInt):
    ComponentClass = TIntInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TIntInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         expandable=expandable, interpolation=interpolation, normalize=normalize, _inner=_inner)


class TIntSeqSet(TSequenceSet[int, 'TInt', 'TIntInst', 'TIntSeq', 'TIntSeqSet'], TInt):
    ComponentClass = TIntSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TIntSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
