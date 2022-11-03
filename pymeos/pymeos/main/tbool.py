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
from typing import Optional, Union, List, Set

from pymeos_cffi import *

from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import *


class TBool(Temporal[bool, 'TBool', 'TBoolInst', 'TBoolSeq', 'TBoolSeqSet'], ABC):
    BaseClass = bool
    _parse_function = tbool_in

    def __init__(self, _inner) -> None:
        super().__init__()

    def at(self, other: Union[bool, datetime, TimestampSet, Period, PeriodSet]) -> TBool:
        if isinstance(other, bool):
            result = tbool_at_value(self._inner, other)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[bool, datetime, TimestampSet, Period, PeriodSet]) -> TBool:
        if isinstance(other, bool):
            result = tbool_minus_value(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    @staticmethod
    def from_base(value: bool, base: Temporal) -> TBool:
        result = tbool_from_base(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: bool, base: Time) -> TBool:
        if isinstance(base, datetime):
            return TBoolInst(_inner=tboolinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TBoolSeq(_inner=tbooldiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TBoolSeq(_inner=tboolseq_from_base_time(value, base._inner))
        elif isinstance(base, PeriodSet):
            return TBoolSeqSet(_inner=tboolseqset_from_base_time(value, base._inner))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @property
    def value_set(self) -> Set[bool]:
        """
        List of distinct values.
        """
        values, count = tbool_values(self._inner)
        return {values[i] for i in range(count)}

    @property
    def start_value(self) -> bool:
        """
        Start value.
        """
        return tbool_start_value(self._inner)

    @property
    def end_value(self) -> bool:
        """
        End value.
        """
        return tbool_end_value(self._inner)

    def value_at_timestamp(self, timestamp) -> bool:
        """
        Value at timestamp.
        """
        return tbool_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def always(self, value: bool) -> bool:
        return tbool_always_eq(self._inner, value)

    def ever(self, value: bool) -> bool:
        return tbool_ever_eq(self._inner, value)

    def never(self, value: bool) -> bool:
        return not tbool_ever_eq(self._inner, value)

    def when_true(self) -> PeriodSet:
        return PeriodSet(_inner=tbool_when_true(self._inner))

    def when_false(self) -> PeriodSet:
        return PeriodSet(_inner=tbool_when_true(tnot_tbool(self._inner)))

    def temporal_equal(self, other: Union[bool, Temporal]) -> TBool:
        if isinstance(other, bool):
            result = teq_tbool_bool(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[bool, Temporal]) -> TBool:
        if isinstance(other, bool):
            result = tne_tbool_bool(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_not(self) -> TBool:
        return self.__class__(_inner=tnot_tbool(self._inner))

    def temporal_and(self, other: Union[bool, TBool]) -> TBool:
        if isinstance(other, bool):
            return self.__class__(_inner=tand_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tand_tbool_tbool(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def temporal_or(self, other: Union[bool, TBool]) -> TBool:
        if isinstance(other, bool):
            return self.__class__(_inner=tor_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tor_tbool_tbool(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __neg__(self):
        return self.temporal_not()

    def __invert__(self):
        return self.temporal_not()

    def __and__(self, other):
        return self.temporal_and(other)

    def __or__(self, other):
        return self.temporal_or(other)

    def __str__(self):
        return tbool_out(self._inner)

    def as_wkt(self):
        return tbool_out(self._inner)

    @staticmethod
    def read_from_cursor(value, _):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TBoolInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TBoolSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TBoolSeqSet(string=value)
            else:
                return TBoolSeq(string=value)
        raise Exception("ERROR: Could not parse temporal boolean value")


class TBoolInst(TInstant[bool, 'TBool', 'TBoolInst', 'TBoolSeq', 'TBoolSeqSet'], TBool):
    _make_function = tboolinst_make
    _cast_function = bool

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, bool]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TBoolSeq(TSequence[bool, 'TBool', 'TBoolInst', 'TBoolSeq', 'TBoolSeqSet'], TBool):
    ComponentClass = TBoolInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TBoolInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TBoolSeqSet(TSequenceSet[bool, 'TBool', 'TBoolInst', 'TBoolSeq', 'TBoolSeqSet'], TBool):
    ComponentClass = TBoolSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TBoolSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
