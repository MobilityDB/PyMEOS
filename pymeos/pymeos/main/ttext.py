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
from datetime import datetime
from typing import Optional, Union, List, Set

from dateutil.parser import parse
from pymeos_cffi import tlt_ttext_text
from pymeos_cffi.functions import ttext_in, ttextinst_make, datetime_to_timestamptz, ttext_out, \
    ttext_start_value, ttext_end_value, ttext_value_at_timestamp, ttext_values, text2cstring, ttext_upper, ttext_lower, \
    textcat_ttext_text, textcat_ttext_ttext, ttext_from_base, ttextdiscseq_from_base_time, ttextseq_from_base_time, \
    ttextseqset_from_base_time, ttext_max_value, ttext_min_value, ttext_at_value, ttext_at_values, ttext_minus_value, \
    ttext_minus_values, textcat_text_ttext, ttext_always_lt, ttext_always_le, ttext_always_eq, ttext_ever_eq, \
    ttext_ever_lt, ttext_ever_le, tgt_ttext_text, tge_ttext_text, tne_ttext_text, teq_ttext_text, tle_ttext_text

from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import TimestampSet, Period, PeriodSet


class TText(Temporal, ABC):
    """
    Abstract class for representing temporal strings of any subtype.
    """

    BaseClass = str

    _parse_function = ttext_in

    def at(self, other: Union[str, List[str], datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, str):
            result = ttext_at_value(self._inner, other)
        elif isinstance(other, list):
            result = ttext_at_values(self._inner, other)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[str, List[str], datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, str):
            result = ttext_minus_value(self._inner, other)
        elif isinstance(other, list):
            result = ttext_minus_values(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    @staticmethod
    def from_base(value: str, base: Temporal) -> TText:
        result = ttext_from_base(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: str, base: Union[datetime, TimestampSet, Period, PeriodSet]) -> TText:
        if isinstance(base, datetime):
            return TTextInst(_inner=ttextinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TTextSeq(_inner=ttextdiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TTextSeq(_inner=ttextseq_from_base_time(value, base._inner))
        elif isinstance(base, PeriodSet):
            return TTextSeqSet(_inner=ttextseqset_from_base_time(value, base._inner))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @property
    def value_set(self) -> Set[str]:
        values, count = ttext_values(self._inner)
        return {text2cstring(values[i]) for i in range(count)}

    @property
    def min_value(self):
        return ttext_min_value(self._inner)

    @property
    def max_value(self):
        return ttext_max_value(self._inner)

    @property
    def start_value(self):
        return ttext_start_value(self._inner)

    @property
    def end_value(self):
        return ttext_end_value(self._inner)

    def upper(self) -> TText:
        return self.__class__(_inner=ttext_upper(self._inner))

    def lower(self) -> TText:
        return self.__class__(_inner=ttext_lower(self._inner))

    def concatenate(self, other: Union[str, TText], other_before: bool = False):
        if isinstance(other, str):
            result = textcat_ttext_text(self._inner, other) if not other_before \
                else textcat_text_ttext(other, self._inner)
        elif isinstance(other, TText):
            result = textcat_ttext_ttext(self._inner, other._inner) if not other_before \
                else textcat_ttext_ttext(other._inner, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return self.__class__(_inner=result)

    def always_less(self, value: str) -> bool:
        return ttext_always_lt(self._inner, value)

    def always_less_or_equal(self, value: str) -> bool:
        return ttext_always_le(self._inner, value)

    def always_equal(self, value: str) -> bool:
        return ttext_always_eq(self._inner, value)

    def always_not_equal(self, value: str) -> bool:
        return not ttext_ever_eq(self._inner, value)

    def always_greater_or_equal(self, value: str) -> bool:
        return not ttext_ever_lt(self._inner, value)

    def always_greater(self, value: str) -> bool:
        return not ttext_ever_le(self._inner, value)

    def ever_less(self, value: str) -> bool:
        return ttext_ever_lt(self._inner, value)

    def ever_less_or_equal(self, value: str) -> bool:
        return ttext_ever_le(self._inner, value)

    def ever_equal(self, value: str) -> bool:
        return ttext_ever_eq(self._inner, value)

    def ever_not_equal(self, value: str) -> bool:
        return not ttext_always_eq(self._inner, value)

    def ever_greater_or_equal(self, value: str) -> bool:
        return not ttext_always_lt(self._inner, value)

    def ever_greater(self, value: str) -> bool:
        return not ttext_always_le(self._inner, value)

    def never_less(self, value: str) -> bool:
        return not ttext_ever_lt(self._inner, value)

    def never_less_or_equal(self, value: str) -> bool:
        return not ttext_ever_le(self._inner, value)

    def never_equal(self, value: str) -> bool:
        return not ttext_ever_eq(self._inner, value)

    def never_not_equal(self, value: str) -> bool:
        return ttext_always_eq(self._inner, value)

    def never_greater_or_equal(self, value: str) -> bool:
        return ttext_always_lt(self._inner, value)

    def never_greater(self, value: str) -> bool:
        return ttext_always_le(self._inner, value)

    def temporal_less(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = tlt_ttext_text(self._inner, other)
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = tle_ttext_text(self._inner, other)
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_equal(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = teq_ttext_text(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = tne_ttext_text(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = tge_ttext_text(self._inner, other)
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[str, Temporal]) -> Temporal:
        if isinstance(other, str):
            result = tgt_ttext_text(self._inner, other)
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    def __add__(self, other):
        return self.concatenate(other)

    def __radd__(self, other):
        return self.concatenate(other, True)

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        return ttext_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def __str__(self):
        return ttext_out(self._inner)

    def as_wkt(self):
        return ttext_out(self._inner)

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TTextInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TTextSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TTextSeqSet(string=value)
            else:
                return TTextSeq(string=value)
        raise Exception("ERROR: Could not parse temporal text value")


class TTextInst(TInstant, TText):
    """
    Class for representing temporal strings of instant subtype.

    ``TTextInst`` objects can be created 
    with a single argument of type string as in MobilityDB.

        >>> TTextInst('AA@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str`` or ``datetime``.

        >>> TTextInst('AA', '2019-09-08 00:00:00+01')
        >>> TTextInst(['AA', '2019-09-08 00:00:00+01'])
        >>> TTextInst('AA', parse('2019-09-08 00:00:00+01'))
        >>> TTextInst(['AA', parse('2019-09-08 00:00:00+01')])

    """

    """It is not possible to call super().__init__(value, time) since it is necessary
    to strip the eventual double quotes enclosing the value
    """

    _make_function = ttextinst_make
    _cast_function = str

    def __init__(self, string: Optional[str] = None, *, value: Optional[str] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TTextSeq(TSequence, TText):
    """
    Class for representing temporal strings of sequence subtype.

    ``TTextSeq`` objects can be created 
    with a single argument of type string as in MobilityDB.

        >>> TTextSeq('[AA@2019-09-01 00:00:00+01, BB@2019-09-02 00:00:00+01, AA@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances of
      ``str`` or ``TTextInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.

    Some pymeos_examples are given next.

        >>> TTextSeq(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'])
        >>> TTextSeq(TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01')])
        >>> TTextSeq(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'], True, True)
        >>> TTextSeq([TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TTextInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TTextInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TTextSeqSet(TSequenceSet, TText):
    """
    Class for representing temporal strings of sequence subtype.

    ``TTextSeqSet`` objects can be created with a single argument of typestring as in MobilityDB.

        >>> TTextSeqSet('{[AA@2019-09-01 00:00:00+01], [BB@2019-09-02 00:00:00+01, AA@2019-09-03 00:00:00+01]}')

    Another possibility is to give the list of composing sequences, which can be
    instances of ``str`` or ``TTextSeq``.

        >>> TTextSeqSet(['[AA@2019-09-01 00:00:00+01]', '[BB@2019-09-02 00:00:00+01, AA@2019-09-03 00:00:00+01]'])
        >>> TTextSeqSet([TTextSeq('[AA@2019-09-01 00:00:00+01]'), TTextSeq('[BB@2019-09-02 00:00:00+01, AA@2019-09-03 00:00:00+01]')])
        >>> TTextSeqSet([TTextSeq('[AA@2019-09-01 00:00:00+01]'), TTextSeq('[BB@2019-09-02 00:00:00+01, AA@2019-09-03 00:00:00+01]')])

    """

    ComponentClass = TTextSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TTextSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
