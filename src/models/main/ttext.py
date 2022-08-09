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

from datetime import datetime
from typing import Optional, Union, List

from dateutil.parser import parse

from lib.functions import ttext_in, ttextinst_make, datetime_to_timestamptz, pg_timestamptz_in, ttext_out, \
    ttext_start_value, ttext_end_value, ttext_value_at_timestamp, ttext_values, tinstantset_make, tsequence_make, \
    tsequenceset_make, text2cstring
from ..temporal import Temporal, TInstant, TInstantSet, TSequence, TSequenceSet


class TText(Temporal):
    """
    Abstract class for representing temporal strings of any subtype.
    """

    BaseClass = str
    BaseClassDiscrete = True

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TTextInst(value)
        elif value[0] == '[' or value[0] == '(':
            return TTextSeq(value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TTextSeqSet(value)
            else:
                return TTextInstSet(value)
        raise Exception("ERROR: Could not parse temporal text value")

    @staticmethod
    def write(value):
        if not isinstance(value, TText):
            raise ValueError('Value must be an instance of a subclass of TText')
        return value.__str__().strip("'")

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

    def value_at_timestamp(self, timestamp):
        return ttext_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def __str__(self):
        return ttext_out(self._inner)


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

    def __init__(self, *, string: Optional[str] = None, value: Optional[str] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        assert (_inner is not None) or ((string is not None) != (value is not None and timestamp is not None)), \
            "Either string must be not None or both point and timestamp must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = ttext_in(string)
        else:
            ts = datetime_to_timestamptz(timestamp) if isinstance(timestamp, datetime) \
                else pg_timestamptz_in(timestamp, -1)
            self._inner = ttextinst_make(value, ts)

    @property
    def value(self):
        """
        Geometry representing the values taken by the temporal value.
        """
        return self.values[0]


class TTextInstSet(TInstantSet, TText):
    """
    Class for representing temporal strings of instant set subtype.

    ``TTextInstSet`` objects can be created 
    with a single argument of type string as in MobilityDB.

        >>> TTextInstSet('AA@2019-09-01')

    Another possibility is to give a tuple or list of composing instants,
    which can be instances of ``str`` or ``TTextInst``.

        >>> TTextInstSet('AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01')
        >>> TTextInstSet(TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01'))
        >>> TTextInstSet(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'])
        >>> TTextInstSet([TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01')])

    """

    ComponentClass = TTextInst

    def __init__(self, *, string: Optional[str] = None, instant_list: Optional[List[Union[str, TTextInst]]] = None,
                 merge: bool = True, _inner=None):
        assert (_inner is not None) or ((string is not None) != (instant_list is not None)), \
            "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = ttext_in(string)
        else:
            instants = [x._inner if isinstance(x, TTextInst) else ttext_in(x) for x in instant_list]
            self._inner = tinstantset_make(instants, len(instants), merge)


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

    Some examples are given next.

        >>> TTextSeq(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'])
        >>> TTextSeq(TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01')])
        >>> TTextSeq(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'], True, True)
        >>> TTextSeq([TTextInst('AA@2019-09-01 00:00:00+01'), TTextInst('BB@2019-09-02 00:00:00+01'), TTextInst('AA@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TTextInst

    def __init__(self, *, string: Optional[str] = None, instant_list: Optional[List[Union[str, TTextInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (instant_list is not None)), \
            "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = ttext_in(string)
        else:
            self._instants = [x._inner if isinstance(x, TTextInst) else ttext_in(x) for x in instant_list]
            self._inner = tsequence_make(self._instants, len(self._instants), lower_inc, upper_inc, False, normalize)

    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'


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

    def __init__(self, *, string: Optional[str] = None, sequence_list: Optional[List[Union[str, TTextSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (sequence_list is not None)), \
            "Either string must be not None or sequence_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = ttext_in(string)
        else:
            sequences = [x._inner if isinstance(x, TTextSeq) else ttext_in(x) for x in sequence_list]
            self._inner = tsequenceset_make(sequences, len(sequences), normalize)

    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'
