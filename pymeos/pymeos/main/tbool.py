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
from typing import Optional, Union, List

from dateutil.parser import parse
from pymeos_cffi import tbooldiscseq_from_base_time, tbool_at_value
from pymeos_cffi.functions import tbool_in, datetime_to_timestamptz, tboolinst_make, tbool_out, \
    tbool_values, tbool_start_value, tbool_end_value, \
    tbool_value_at_timestamp, tand_tbool_bool, tand_tbool_tbool, tor_tbool_bool, tor_tbool_tbool, tnot_tbool, \
    tbool_always_eq, tbool_ever_eq, teq_tbool_bool, tne_tbool_bool, tbool_from_base, tboolseq_from_base_time, \
    tboolseqset_from_base_time, tbool_minus_value

from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import TimestampSet, Period, PeriodSet


class TBool(Temporal, ABC):
    """
    Abstract class for representing temporal Booleans of any subtype.
    """

    BaseClass = bool
    BaseClassDiscrete = True
    _parse_function = tbool_in

    def at(self, other: Union[bool, datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, bool):
            result = tbool_at_value(self._inner, other)
        else:
            return super().at(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def minus(self, other: Union[bool, datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, bool):
            result = tbool_minus_value(self._inner, other)
        else:
            return super().minus(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    @staticmethod
    def from_base(value: bool, base: Temporal) -> TBool:
        result = tbool_from_base(value, base._inner)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    @staticmethod
    def from_base_time(value: bool, base: Union[datetime, TimestampSet, Period, PeriodSet]) -> TBool:
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
    def values(self) -> List[bool]:
        """
        List of distinct values.
        """
        values, count = tbool_values(self._inner)
        return [values[i] for i in range(count)]

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

    def tnot(self) -> TBool:
        return self.__class__(_inner=tnot_tbool(self._inner))

    def tand(self, other: Union[bool, TBool]) -> TBool:
        if isinstance(other, bool):
            return self.__class__(_inner=tand_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tand_tbool_tbool(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def tor(self, other: Union[bool, TBool]) -> TBool:
        if isinstance(other, bool):
            return self.__class__(_inner=tor_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tor_tbool_tbool(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __neg__(self):
        return self.tnot()

    def __invert__(self):
        return self.tnot()

    def __and__(self, other):
        return self.tand(other)

    def __or__(self, other):
        return self.tor(other)

    def __lt__(self, other):
        """
        Less than
        """
        return NotImplemented

    def __le__(self, other):
        """
        Less or equal
        """
        return NotImplemented

    def __eq__(self, other):
        """
        Equality
        """
        if isinstance(other, bool):
            from ..factory import _TemporalFactory
            result = teq_tbool_bool(self._inner, other)
            return _TemporalFactory.create_temporal(result)
        return super().__eq__(other)

    def __ne__(self, other):
        """
        Inequality
        """
        if isinstance(other, bool):
            from ..factory import _TemporalFactory
            result = tne_tbool_bool(self._inner, other)
            return _TemporalFactory.create_temporal(result)
        return super().__eq__(other)

    def __ge__(self, other):
        """
        Greater or equal
        """
        return NotImplemented

    def __gt__(self, other):
        """
        Greater than
        """
        return NotImplemented

    def __str__(self):
        return tbool_out(self._inner)

    def as_wkt(self):
        return tbool_out(self._inner)

    @staticmethod
    def read_from_cursor(value, cursor=None):
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


class TBoolInst(TInstant, TBool):
    """
    Class for representing temporal Booleans of instant subtype.

    ``TBoolInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBoolInst('true@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``bool``, or ``datetime``.

        >>> TBoolInst('True', '2019-09-08 00:00:00+01')
        >>> TBoolInst(['True', '2019-09-08 00:00:00+01'])
        >>> TBoolInst(True, parse('2019-09-08 00:00:00+01'))
        >>> TBoolInst([True, parse('2019-09-08 00:00:00+01')])

    """

    """
    It is not possible to call super().__init__(value, time) since bool('False') == True
    and eval('False') == False. Furthermore eval('false') gives an error
    """

    _make_function = tboolinst_make
    _cast_function = bool

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, bool]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TBoolSeq(TSequence, TBool):
    """
    Class for representing temporal Booleans of sequence subtype.

    ``TBoolSeq`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBoolSeq('[true@2019-09-01 00:00:00+01, false@2019-09-02 00:00:00+01, true@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows.

    * ``instantList`` is the list of composing instants, which can be instances of
      ``str`` or ``TBoolInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.

    Some pymeos_examples are given next.

        >>> TBoolSeq(['true@2019-09-01 00:00:00+01', 'false@2019-09-02 00:00:00+01', 'true@2019-09-03 00:00:00+01'])
        >>> TBoolSeq(TBoolInst('true@2019-09-01 00:00:00+01'), TBoolInst('false@2019-09-02 00:00:00+01'), TBoolInst('true@2019-09-03 00:00:00+01')])
        >>> TBoolSeq(['true@2019-09-01 00:00:00+01', 'false@2019-09-02 00:00:00+01', 'true@2019-09-03 00:00:00+01'], True, True)
        >>> TBoolSeq([TBoolInst('true@2019-09-01 00:00:00+01'), TBoolInst('false@2019-09-02 00:00:00+01'), TBoolInst('true@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TBoolInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TBoolInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TBoolSeqSet(TSequenceSet, TBool):
    """
    Class for representing temporal Booleans of sequence set subtype.

    ``TBoolSeqSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBoolSeqSet('{[true@2019-09-01 00:00:00+01], [false@2019-09-02 00:00:00+01, true@2019-09-03 00:00:00+01]}')

    Another possibility is to give the list of composing sequences, which
    can be instances of ``str`` or ``TBoolSeq``.

        >>> TBoolSeqSet(['[true@2019-09-01 00:00:00+01]', '[false@2019-09-02 00:00:00+01, true@2019-09-03 00:00:00+01]'])
        >>> TBoolSeqSet([TBoolSeq('[true@2019-09-01 00:00:00+01]'), TBoolSeq('[false@2019-09-02 00:00:00+01, true@2019-09-03 00:00:00+01]')])
        >>> TBoolSeqSet([TBoolSeq('[true@2019-09-01 00:00:00+01]'), TBoolSeq('[false@2019-09-02 00:00:00+01, true@2019-09-03 00:00:00+01]')])

    """

    ComponentClass = TBoolSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TBoolSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
