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
from spans.types import floatrange
from ..temporal import Temporal, TInstant, TInstantSet, TSequence, TSequenceSet


class TFloat(Temporal, ABC):
    """
    Abstract class for representing temporal floats of any subtype.
    """

    BaseClass = float
    BaseClassDiscrete = False

    @property
    def valueRange(self):
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return floatrange(self.min_value, self.max_value, True, True)

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value.startswith('Interp=Stepwise;'):
            value1 = value.replace('Interp=Stepwise;', '')
            if value1[0] == '{':
                return TFloatSeqSet(value)
            else:
                return TFloatSeq(value)
        elif value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TFloatInst(value)
        elif value[0] == '[' or value[0] == '(':
            return TFloatSeq(value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TFloatSeqSet(value)
            else:
                return TFloatInstSet(value)
        raise Exception("ERROR: Could not parse temporal float value")

    @staticmethod
    def write(value):
        if not isinstance(value, TFloat):
            raise ValueError('Value must be an instance of a subclass of TFloat')
        return value.__str__().strip("'")


class TFloatInst(TInstant, TFloat):
    """
    Class for representing temporal floats of instant subtype.

    ``TFloatInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatInst('10.0@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``float`` or ``datetime``.

        >>> TFloatInst('10.0', '2019-09-08 00:00:00+01')
        >>> TFloatInst(['10.0', '2019-09-08 00:00:00+01'])
        >>> TFloatInst(10.0, parse('2019-09-08 00:00:00+01'))
        >>> TFloatInst([10.0, parse('2019-09-08 00:00:00+01')])

    """

    def __init__(self, value, time=None):
        super().__init__(value, time)

    @property
    def values(self):
        """
        List of ranges representing the values taken by the temporal value
        """
        return [floatrange(self._value, self._value, True, True)]


class TFloatInstSet(TInstantSet, TFloat):
    """
    Class for representing temporal floats of instant set subtype.

    ``TFloatInstSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatInstSet('10.0@2019-09-01')

    Another possibility is to give a tuple or list of composing instants,
    which can be instances of ``str`` or ``TFloatInst``.

        >>> TFloatInstSet('10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01')
        >>> TFloatInstSet(TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01'))
        >>> TFloatInstSet(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
        >>> TFloatInstSet([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])

    """

    ComponentClass = TFloatInst

    def __init__(self,  *argv):
        super().__init__(*argv)

    @property
    def values(self):
        """
        List of ranges representing the values taken by the temporal value.
        """
        values = super().values
        return [floatrange(value, value, True, True) for value in values]


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

    def __init__(self, instantList, lower_inc=None, upper_inc=None, interp=None):
        super().__init__(instantList, lower_inc, upper_inc, interp)

    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, which is either ``'Linear'`` or ``'Stepwise'``.
        """
        return self._interp

    def _interpolate(self, inst1, inst2, timestamp):
        """
        Interpolate the temporal value at a timestamp between inst1 and inst2.
        """
        # preconditions
        if not (isinstance(inst1, TFloatInst) and
            isinstance(inst2, TFloatInst) and isinstance(timestamp, datetime) and
            inst1._time < timestamp and timestamp < inst2._time):
            Exception("Erroneous arguments for function TFloatSeq._interpolate")

        duration1 = timestamp - inst1._time
        duration2 = inst2._time - inst1._time
        ratio = duration1.total_seconds() / duration2.total_seconds()
        return inst1._value + (inst2._value - inst1._value) * ratio

    @property
    def values(self):
        """
        List of ranges representing the values taken by the temporal value.
        """
        min = self.min_value
        max = self.max_value
        lower = self.start_value
        upper = self.end_value
        min_inc = min < lower or (min == lower and self.lower_inc)
        max_inc = max > upper or (max == upper and self.upper_inc)
        if not min_inc:
            min_inc = min in self._instantList[1:-1]
        if not max_inc:
            max_inc = max in self._instantList[1:-1]
        return [floatrange(min, max, min_inc, max_inc)]


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

    def __init__(self, sequenceList, interp=None):
        super().__init__(sequenceList, interp)

    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, which is either ``'Linear'`` or ``'Stepwise'``.
        """
        return self._interp

    @property
    def values(self):
        """
        List of ranges representing the values taken by the temporal value
        """
        ranges = sorted([seq.valueRange for seq in self._sequenceList])
        # Normalize list of ranges
        result = []
        range = ranges[0]
        for range1 in ranges[1:]:
            if range.adjacent(range1) or range.overlap(range1):
                range = range.union(range1)
            else:
                result.append(range)
                range = range1
        result.append(range)
        return result

