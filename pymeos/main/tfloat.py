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
from abc import ABC
from datetime import datetime
from typing import Optional, List, Literal, Union

from dateutil.parser import parse
from spans.types import floatrange

from pymeos_cffi.functions import tfloat_start_value, tfloat_end_value, tfloat_values, tfloat_value_at_timestamp, \
    datetime_to_timestamptz, tfloat_out, tfloatinst_make, tfloat_in
from .tnumber import TNumber
from ..temporal import TInstant, TInstantSet, TSequence, TSequenceSet


class TFloat(TNumber, ABC):
    """
    Abstract class for representing temporal floats of any subtype.
    """

    BaseClass = float
    BaseClassDiscrete = False
    _parse_function = tfloat_in

    @staticmethod
    def read_from_cursor(value, cursor=None):
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
                return TFloatInstSet(string=value)
        raise Exception("ERROR: Could not parse temporal float value")

    @property
    def value_range(self):
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return floatrange(self.min_value, self.max_value, True, True)

    @property
    def start_value(self):
        """
        Start value.
        """
        return tfloat_start_value(self._inner)

    @property
    def end_value(self):
        """
        End value.
        """
        return tfloat_end_value(self._inner)

    @property
    def values(self):
        """
        List of distinct values.
        """
        values, count = tfloat_values(self._inner)
        return [values[i] for i in range(count)]

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        return tfloat_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def to_str(self, max_decimals=5):
        return tfloat_out(self._inner, max_decimals)

    def __str__(self):
        return tfloat_out(self._inner, 5)


class TFloatInst(TInstant, TFloat):
    """
    Class for representing temporal floats of instant subtype.

    ``TFloatInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatInst(string='10.0@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``float`` or ``datetime``.

        >>> TFloatInst(value='10.0', timestamp='2019-09-08 00:00:00+01')
        >>> TFloatInst(value=10.0, timestamp=parse('2019-09-08 00:00:00+01'))

    """

    _make_function = tfloatinst_make
    _cast_function = int

    def __init__(self, *, string: Optional[str] = None, value: Optional[Union[str, float]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TFloatInstSet(TInstantSet, TFloat):
    """
    Class for representing temporal floats of instant set subtype.

    ``TFloatInstSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatInstSet(string='10.0@2019-09-01')

    Another possibility is to give a tuple or list of composing instants,
    which can be instances of ``str`` or ``TFloatInst``.

        >>> TFloatInstSet(instant_list=['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
        >>> TFloatInstSet(instant_list=[TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])

    """

    ComponentClass = TFloatInst

    def __init__(self, *, string: Optional[str] = None, instant_list: Optional[List[Union[str, TFloatInst]]] = None,
                 merge: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, merge=merge, _inner=_inner)


class TFloatSeq(TSequence, TFloat):
    """
    Class for representing temporal floats of sequence subtype.

    ``TFloatSeq`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatSeq('[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')
        >>> TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances of
      ``str`` or ``TFloatInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.
    * ``interp`` which is either ``'Linear'`` or ``'Stepwise'``, the former being
      the default.

    Some examples are shown next.

        >>> TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
        >>> TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])
        >>> TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'], True, True, 'Stepwise')
        >>> TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')], True, True, 'Stepwise')

    """

    ComponentClass = TFloatInst

    def __init__(self, *, string: Optional[str] = None, instant_list: Optional[List[Union[str, TFloatInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: Literal['Linear', 'Stepwise'] = 'Linear', normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TFloatSeqSet(TSequenceSet, TFloat):
    """
    Class for representing temporal floats of sequence subtype.

    ``TFloatSeqSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatSeqSet('{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')
        >>> TFloatSeqSet('Interp=Stepwise;{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')

    Another possibility is to give the arguments as follows:

    * ``sequenceList`` is a list of composing sequences, which can be
      instances of ``str`` or ``TFloatSeq``,
    * ``interp`` can be ``'Linear'`` or ``'Stepwise'``, the former being
      the default.

    Some examples are shown next.

        >>> TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'])
        >>> TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Linear')
        >>> TFloatSeqSet(['Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]', 'Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Stepwise')
        >>> TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')])
        >>> TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'),  TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Linear')
        >>> TFloatSeqSet([TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Stepwise')

    """

    ComponentClass = TFloatSeq

    def __init__(self, *, string: Optional[str] = None, sequence_list: Optional[List[Union[str, TFloatSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
