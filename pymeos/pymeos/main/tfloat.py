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
from typing import Optional, List, Union, TYPE_CHECKING, Set

from pymeos_cffi import *
from spans.types import floatrange, intrange

from .tnumber import TNumber
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import *

if TYPE_CHECKING:
    from ..boxes import TBox
    from .tint import TInt


class TFloat(TNumber[float, 'TFloat', 'TFloatInst', 'TFloatSeq', 'TFloatSeqSet'], ABC):
    BaseClass = float
    _parse_function = tfloat_in

    def is_adjacent(self, other: Union[int, float,
                                       TBox, TNumber, floatrange, intrange,
                                       Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return adjacent_tfloat_float(self._inner, float(other))
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[int, float,
                                               TBox, TNumber, floatrange, intrange,
                                               Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(container, int) or isinstance(container, float):
            return contained_tfloat_float(self._inner, float(container))
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[int, float,
                                      TBox, TNumber, floatrange, intrange,
                                      Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(content, int) or isinstance(content, float):
            return contains_tfloat_float(self._inner, float(content))
        else:
            return super().contains(content)

    def overlaps(self, other: Union[int, float,
                                    TBox, TNumber, floatrange, intrange,
                                    Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return overlaps_tfloat_float(self._inner, float(other))
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[int, float,
                                   TBox, TNumber, floatrange, intrange,
                                   Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int) or isinstance(other, float):
            return same_tfloat_float(self._inner, float(other))
        else:
            return super().is_same(other)

    def always_less(self, value: float) -> bool:
        return tfloat_always_lt(self._inner, value)

    def always_less_or_equal(self, value: float) -> bool:
        return tfloat_always_le(self._inner, value)

    def always_equal(self, value: float) -> bool:
        return tfloat_always_eq(self._inner, value)

    def always_not_equal(self, value: float) -> bool:
        return not tfloat_ever_eq(self._inner, value)

    def always_greater_or_equal(self, value: float) -> bool:
        return not tfloat_ever_lt(self._inner, value)

    def always_greater(self, value: float) -> bool:
        return not tfloat_ever_le(self._inner, value)

    def ever_less(self, value: float) -> bool:
        return tfloat_ever_lt(self._inner, value)

    def ever_less_or_equal(self, value: float) -> bool:
        return tfloat_ever_le(self._inner, value)

    def ever_equal(self, value: float) -> bool:
        return tfloat_ever_eq(self._inner, value)

    def ever_not_equal(self, value: float) -> bool:
        return not tfloat_always_eq(self._inner, value)

    def ever_greater_or_equal(self, value: float) -> bool:
        return not tfloat_always_lt(self._inner, value)

    def ever_greater(self, value: float) -> bool:
        return not tfloat_always_le(self._inner, value)

    def never_less(self, value: float) -> bool:
        return not tfloat_ever_lt(self._inner, value)

    def never_less_or_equal(self, value: float) -> bool:
        return not tfloat_ever_le(self._inner, value)

    def never_equal(self, value: float) -> bool:
        return not tfloat_ever_eq(self._inner, value)

    def never_not_equal(self, value: float) -> bool:
        return tfloat_always_eq(self._inner, value)

    def never_greater_or_equal(self, value: float) -> bool:
        return tfloat_always_lt(self._inner, value)

    def never_greater(self, value: float) -> bool:
        return tfloat_always_le(self._inner, value)

    def temporal_less(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = tlt_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = tle_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_equal(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = teq_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = tne_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = tge_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[int, float, Temporal]) -> Temporal:
        if isinstance(other, int) or isinstance(other, float):
            result = tgt_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    def at(self, other: Union[int, float, List[float], List[int],
                              intrange, floatrange, List[intrange], List[floatrange], TBox,
                              datetime, TimestampSet, Period, PeriodSet]) -> TFloat:
        if isinstance(other, float) or isinstance(other, int):
            result = tfloat_at_value(self._inner, float(other))
        elif isinstance(other, list) and (isinstance(other[0], float) or isinstance(other[0], int)):
            result = tfloat_at_values(self._inner, [float(x) for x in other])
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[float, List[float],
                                 intrange, floatrange, List[intrange], List[floatrange], TBox,
                                 datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, float):
            result = tfloat_minus_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], float):
            result = tfloat_minus_values(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def to_tint(self) -> TInt:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tfloat_to_tint(self._inner))

    def to_floatrange(self) -> floatrange:
        return floatspan_to_floatrange(tnumber_to_span(self._inner))

    @staticmethod
    def from_base(value: float, base: Temporal, interpolation: TInterpolation = TInterpolation.LINEAR) -> TFloat:
        result = tfloat_from_base(value, base._inner, interpolation)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: float, base: Time, interpolation: TInterpolation = None) -> TFloat:
        if isinstance(base, datetime):
            return TFloatInst(_inner=tfloatinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TFloatSeq(_inner=tfloatdiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TFloatSeq(_inner=tfloatseq_from_base_time(value, base._inner, interpolation))
        elif isinstance(base, PeriodSet):
            return TFloatSeqSet(_inner=tfloatseqset_from_base_time(value, base._inner, interpolation))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @staticmethod
    def read_from_cursor(value, _=None):
        if not value:
            return None
        if value.startswith('Interp=Stepwise;'):
            value1 = value.replace('Interp=Stepwise;', '')
            if value1[0] == '{':
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        elif value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TFloatInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TFloatSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        raise Exception("ERROR: Could not parse temporal float value")

    def value_range(self) -> floatrange:
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return self.to_floatrange()

    def value_ranges(self) -> List[floatrange]:
        spanset = tfloat_spanset(self._inner)
        spans, count = spanset_spans(spanset)
        return [floatspan_to_floatrange(spans[i]) for i in range(count)]

    def start_value(self) -> float:
        """
        Start value.
        """
        return tfloat_start_value(self._inner)

    def end_value(self) -> float:
        """
        End value.
        """
        return tfloat_end_value(self._inner)

    def value_set(self) -> Set[float]:
        """
        List of distinct values.
        """
        values, count = tfloat_values(self._inner)
        return {values[i] for i in range(count)}

    def min_value(self) -> float:
        """
        Minimum value.
        """
        return tfloat_min_value(self._inner)

    def max_value(self) -> float:
        """
        Maximum value.
        """
        return tfloat_max_value(self._inner)

    def value_at_timestamp(self, timestamp) -> float:
        """
        Value at timestamp.
        """
        return tfloat_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def to_str(self, max_decimals=5) -> str:
        return tfloat_out(self._inner, max_decimals)

    def value_split(self, start: float, size: float) -> List[Temporal]:
        tiles, new_count = tfloat_value_split(self._inner, size, start)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def time_value_split(self, value_start: float, value_size: float, time_start: Union[str, datetime],
                         duration: Union[str, timedelta]) -> List[Temporal]:
        st = datetime_to_timestamptz(time_start) if isinstance(time_start, datetime) \
            else pg_timestamptz_in(time_start, -1)
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
        tiles, new_count = tfloat_value_time_split(self._inner, value_size, value_start, dt, st)
        return [Temporal._factory(tiles[i]) for i in range(new_count)]

    def to_degrees(self) -> TNumber:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tfloat_degrees(self._inner))

    def derivative(self) -> TNumber:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tfloat_derivative(self._inner))

    def __str__(self):
        return tfloat_out(self._inner, 6)

    def as_wkt(self, precision: int = 6) -> str:
        return tfloat_out(self._inner, precision)


class TFloatInst(TInstant[float, 'TFloat', 'TFloatInst', 'TFloatSeq', 'TFloatSeqSet'], TFloat):
    _make_function = tfloatinst_make
    _cast_function = int

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, float]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TFloatSeq(TSequence[float, 'TFloat', 'TFloatInst', 'TFloatSeq', 'TFloatSeqSet'], TFloat):
    ComponentClass = TFloatInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TFloatInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         expandable=expandable, interpolation=interpolation, normalize=normalize, _inner=_inner)


class TFloatSeqSet(TSequenceSet[float, 'TFloat', 'TFloatInst', 'TFloatSeq', 'TFloatSeqSet'], TFloat):
    ComponentClass = TFloatSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TFloatSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
