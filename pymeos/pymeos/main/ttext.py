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

from pymeos_cffi.functions import ttext_in, ttextinst_make, datetime_to_timestamptz, ttext_out, \
    ttext_start_value, ttext_end_value, ttext_value_at_timestamp, ttext_values, text2cstring, ttext_upper, ttext_lower, \
    textcat_ttext_text, textcat_ttext_ttext
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet


class TText(Temporal, ABC):
    """
    Abstract class for representing temporal strings of any subtype.
    """

    BaseClass = str
    BaseClassDiscrete = True

    _parse_function = ttext_in

    @property
    def values(self):
        values, count = ttext_values(self._inner)
        return [text2cstring(values[i]) for i in range(count)]

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

    def concatenate(self, other: Union[str, TText]):
        if isinstance(other, str):
            return self.__class__(_inner=textcat_ttext_text(self._inner, other))
        elif isinstance(other, TText):
            return self.__class__(_inner=textcat_ttext_ttext(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __add__(self, other):
        return self.concatenate(other)

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        return ttext_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    @property
    def interpolation(self) -> TInterpolation:
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return TInterpolation.STEPWISE

    def __str__(self):
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

    @property
    def value(self):
        """
        Geometry representing the values taken by the temporal value.
        """
        return self.values[0]


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
