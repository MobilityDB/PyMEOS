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
from dateutil.parser import parse
from ..temporal.temporal_parser import parse_temporalinst
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

    def __init__(self, value, time=None):
        if(time is None):
            # Constructor with a single argument of type string
            if (isinstance(value, str)):
                couple = parse_temporalinst(value, 0)
                value = couple[2][0]
                time = couple[2][1]
            # Constructor with a single argument of type tuple or list
            elif (isinstance(value, (tuple, list))):
                value, time = value
            else:
                raise Exception("ERROR: Could not parse temporal instant value")
        # Now both value and time are not None
        assert(isinstance(value, str)), "ERROR: Invalid value argument"
        assert(isinstance(time, (str, datetime))), "ERROR: Invalid time argument"
        # Remove double quotes if present
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        self._value = value
        self._time = parse(time) if isinstance(time, str) else time


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

    def __init__(self,  *argv):
        super().__init__(*argv)


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

    def __init__(self, instantList, lower_inc=None, upper_inc=None):
        super().__init__(instantList, lower_inc, upper_inc)

    @classmethod
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

    def __init__(self, sequenceList):
        super().__init__(sequenceList)

    @classmethod
    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'


