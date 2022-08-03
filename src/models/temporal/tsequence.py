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

from ..time import Period, PeriodSet
from ..temporal import TemporalInstants
from ..temporal.temporal_parser import parse_temporalseq


class TSequence(TemporalInstants):
    """
    Abstract class for representing temporal values of sequence subtype.
    """
    __slots__ = ['_lower_inc', '_upper_inc', '_interp']

    def __init__(self, instantList, lower_inc=None, upper_inc=None, interp=None):
        assert (isinstance(lower_inc, (bool, type(None)))), "ERROR: Invalid lower bound flag"
        assert (isinstance(upper_inc, (bool, type(None)))), "ERROR: Invalid upper bound flag"
        assert (isinstance(interp, (str, type(None)))), "ERROR: Invalid interpolation"
        if isinstance(interp, str):
            assert (interp == 'Linear' or interp == 'Stepwise'), "ERROR: Invalid interpolation"
        self._instantList = []
        # Constructor with a first argument of type string and optional arguments for the bounds and interpolation
        if isinstance(instantList, str):
            elements = parse_temporalseq(instantList, 0)
            for inst in elements[2][0]:
                self._instantList.append(self.ComponentClass(inst[0], inst[1]))
            self._lower_inc = elements[2][1]
            self._upper_inc = elements[2][2]
            # Set interpolation with the argument or the flag from the string if given
            if interp is not None:
                self._interp = interp
            else:
                if self.BaseClassDiscrete:
                    self._interp = 'Stepwise'
                else:
                    self._interp = elements[2][3] if elements[2][3] is not None else 'Linear'
        # Constructor with a first argument of type list and optional arguments for the bounds and interpolation
        elif isinstance(instantList, list):
            # List of strings representing instant values
            if all(isinstance(arg, str) for arg in instantList):
                for arg in instantList:
                    self._instantList.append(self.ComponentClass(arg))
            # List of instant values
            elif all(isinstance(arg, self.ComponentClass) for arg in instantList):
                for arg in instantList:
                    self._instantList.append(arg)
            else:
                raise Exception("ERROR: Could not parse temporal sequence value")
            self._lower_inc = lower_inc if lower_inc is not None else True
            self._upper_inc = upper_inc if upper_inc is not None else False
            # Set the interpolation
            if interp is not None:
                self._interp = interp
            else:
                self._interp = 'Stepwise' if self.BaseClassDiscrete else 'Linear'
        else:
            raise Exception("ERROR: Could not parse temporal sequence value")
        # Verify validity of the resulting instance
        self._valid()

    def _valid(self):
        if len(self._instantList) == 1 and (not self._lower_inc or not self._lower_inc):
            raise Exception("ERROR: The lower and upper bounds must be inclusive for an instant temporal sequence")
        if any(x._time >= y._time for x, y in zip(self._instantList, self._instantList[1:])):
            raise Exception("ERROR: The timestamps of a temporal sequence must be increasing")
        if (self._interp == 'Stepwise' and len(self._instantList) > 1 and not self._upper_inc and
                    self._instantList[-1]._value != self._instantList[-2]._value):
            raise Exception(
                "ERROR: The last two values of a temporal sequence with exclusive upper bound and stepwise interpolation must be equal")
        return True

    @classmethod
    def tempSubtype(cls):
        """
        Subtype of the temporal value, that is, ``'Sequence'``.
        """
        return "Sequence"

    @property
    def lower_inc(self):
        """
        Is the lower bound inclusive?
        """
        return self._lower_inc

    @property
    def upper_inc(self):
        """
        Is the upper bound inclusive?
        """
        return self._upper_inc

    def valueAtTimestamp(self, timestamp):
        """
        Value at timestamp.
        """
        for i in range(len(self._instantList)):
            inst1 = self._instantList[i]
            if inst1._time > timestamp:
                return None

            if i < len(self._instantList) - 1:
                inst2 = self._instantList[i+1]
            else:
                inst2 = None
            if inst1._time == timestamp:
                if inst2 is not None or self._upper_inc:
                    return inst1._value
                else:
                    return None
            # We know that inst1._time < timestamp
            # if inst1 is the last instant
            if inst2 is None:
                return None
            else:
                if timestamp < inst2._time:
                    if self._interp == 'Stepwise':
                        return inst1._value
                    else:
                        return self._interpolate(inst1, inst2, timestamp)
        return None

    @property
    def getTime(self):
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet([self.period])

    @property
    def duration(self):
        """
        Interval on which the temporal value is defined.
        """
        return self.period.upper - self.period.lower

    @property
    def timespan(self):
        """
        Interval on which the temporal value is defined.
        """
        return self.period.upper - self.period.lower

    @property
    def period(self):
        """
        Period on which the temporal value is defined.
        """
        return Period(self.startTimestamp, self.endTimestamp, self.lower_inc, self.upper_inc)

    @property
    def numSequences(self):
        """
        Number of sequences.
        """
        return 1

    @property
    def startSequence(self):
        """
        Start sequence.
        """
        return self

    @property
    def endSequence(self):
        """
        End sequence.
        """
        return self

    def sequenceN(self, n):
        """
        N-th sequence.
        """
        # 1-based
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    @property
    def sequences(self):
        """
        List of sequences.
        """
        return [self]

    def intersectsTimestamp(self, timestamp):
        """
        Does the temporal value intersect the timestamp?
        """
        return self.period.contains_timestamp(timestamp)

    def intersectsPeriod(self, period):
        """
        Does the temporal value intersect the period?
        """
        return self.period.overlap(period)

    # Comparisons are missing
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._instantList == other._instantList and self._lower_inc == other._lower_inc and \
                            self._upper_inc == other._upper_inc and self._interp == other._interp:
                return True
        return False

    def __str__(self):
        interp_str = 'Interp=Stepwise;' if self._interp == 'Stepwise' and self.__class__.BaseClassDiscrete == False else ''
        lower_str = '[' if self._lower_inc else '('
        upper_str = ']' if self._upper_inc else ')'
        return (f"'{interp_str}{lower_str}{TemporalInstants.__str__(self)}{upper_str}'")

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._instantList!r}, {self._lower_inc!r}, {self._upper_inc!r}, {self._interp!r})')
