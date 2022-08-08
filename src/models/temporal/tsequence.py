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
from lib.functions import tpoint_length, tpoint_as_text
from ..temporal import TemporalInstants
from ..time import Period, PeriodSet


class TSequence(TemporalInstants):
    """
    Abstract class for representing temporal values of sequence subtype.
    """

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
        return self._inner.lower_inc

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
                inst2 = self._instantList[i + 1]
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
    def numInstants(self):
        """
        Number of instants.
        """
        return self._inner.count

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
        return tpoint_as_text(self._inner, 3)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._instantList!r}, {self._lower_inc!r}, {self._upper_inc!r}, {self._interp!r})')

    @property
    def distance(self):
        return tpoint_length(self._inner)
