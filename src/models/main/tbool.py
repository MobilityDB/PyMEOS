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

from parsec import *
from datetime import datetime
from dateutil.parser import parse
from ..temporal import Temporal, TInstant, TInstantSet, TSequence, TSequenceSet
from ..temporal.temporal_parser import parse_temporalinst


class TBool(Temporal):
    """
    Abstract class for representing temporal Booleans of any subtype.
    """

    BaseClass = bool
    BaseClassDiscrete = True

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TBoolInst(value)
        elif value[0] == '[' or value[0] == '(':
            return TBoolSeq(value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TBoolSeqSet(value)
            else:
                return TBoolInstSet(value)
        raise Exception("ERROR: Could not parse temporal boolean value")

    @staticmethod
    def write(value):
        if not isinstance(value, TBool):
            raise ValueError('Value must be an instance of a subclass of TBool')
        return value.__str__().strip("'")


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
    def __init__(self, value, time=None):
        if time is None:
            # Constructor with a single argument of type string
            if isinstance(value, str):
                couple = parse_temporalinst(value, 0)
                value = couple[2][0]
                time = couple[2][1]
            # Constructor with a single argument of type tuple or list
            elif isinstance(value, (tuple, list)):
                value, time = value
            else:
                raise Exception("ERROR: Could not parse temporal instant value")
        # Now both value and time are not None
        assert(isinstance(value, (str, bool))), "ERROR: Invalid value argument"
        assert(isinstance(time, (str, datetime))), "ERROR: Invalid time argument"
        if isinstance(value, str):
            if value.lower() == 'true' or value.lower() == 't':
                self._value = True
            elif value.lower() == 'false' or value.lower() == 'f':
                self._value = False
            else:
                raise Exception("ERROR: Could not parse temporal instant value")
        else:
            self._value =  value
        self._time = parse(time) if isinstance(time, str) else time


class TBoolInstSet(TInstantSet, TBool):
    """
    Class for representing temporal Booleans of instant set subtype.

    ``TBoolInstSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBoolInstSet('AA@2019-09-01')

    Another possibility is to give a tuple or list of arguments,
    which can be instances of ``str`` or ``TBoolInst``.

        >>> TBoolInstSet('AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01')
        >>> TBoolInstSet(TBoolInst('AA@2019-09-01 00:00:00+01'), TBoolInst('BB@2019-09-02 00:00:00+01'), TBoolInst('AA@2019-09-03 00:00:00+01'))
        >>> TBoolInstSet(['AA@2019-09-01 00:00:00+01', 'BB@2019-09-02 00:00:00+01', 'AA@2019-09-03 00:00:00+01'])
        >>> TBoolInstSet([TBoolInst('AA@2019-09-01 00:00:00+01'), TBoolInst('BB@2019-09-02 00:00:00+01'), TBoolInst('AA@2019-09-03 00:00:00+01')])

    """

    ComponentClass = TBoolInst

    def __init__(self,  *argv):
        super().__init__(*argv)


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

    Some examples are given next.

        >>> TBoolSeq(['true@2019-09-01 00:00:00+01', 'false@2019-09-02 00:00:00+01', 'true@2019-09-03 00:00:00+01'])
        >>> TBoolSeq(TBoolInst('true@2019-09-01 00:00:00+01'), TBoolInst('false@2019-09-02 00:00:00+01'), TBoolInst('true@2019-09-03 00:00:00+01')])
        >>> TBoolSeq(['true@2019-09-01 00:00:00+01', 'false@2019-09-02 00:00:00+01', 'true@2019-09-03 00:00:00+01'], True, True)
        >>> TBoolSeq([TBoolInst('true@2019-09-01 00:00:00+01'), TBoolInst('false@2019-09-02 00:00:00+01'), TBoolInst('true@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TBoolInst

    def __init__(self, instantList, lower_inc=None, upper_inc=None):
        super().__init__(instantList, lower_inc, upper_inc)

    @classmethod
    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'


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

    def __init__(self, sequenceList):
        super().__init__(sequenceList)

    @classmethod
    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'

