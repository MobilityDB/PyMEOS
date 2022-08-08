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
from lib.functions import tpoint_as_text
from ..temporal.temporal import Temporal
from ..time import Period, PeriodSet


class TSequenceSet(Temporal):
    """
    Abstract class for representing temporal values of sequence set subtype.
    """

    def tempSubtype(cls):
        """
        Subtype of the temporal value, that is, ``'SequenceSet'``.
        """
        return "SequenceSet"

    @property
    def getValues(self):
        """
        List of distinct values taken by the temporal value.
        """
        values = [seq.getValues for seq in self._sequenceList]
        return list(dict.fromkeys([item for sublist in values for item in sublist]))

    @property
    def startValue(self):
        """
        Start value.
        """
        return self._sequenceList[0].startInstant._value

    @property
    def endValue(self):
        """
        End value.
        """
        return self._sequenceList[-1].endInstant._value

    @property
    def minValue(self):
        """
        Minimum value.
        """
        return min(seq.minValue for seq in self._sequenceList)

    @property
    def maxValue(self):
        """
        Maximum value.
        """
        return max(seq.maxValue for seq in self._sequenceList)

    def valueAtTimestamp(self, timestamp):
        """
        Value at timestamp.
        """
        for seq in self._sequenceList:
            per = seq.period
            if per.lower > timestamp:
                return None
            if per.contains_timestamp(timestamp):
                return seq.valueAtTimestamp(timestamp)
        return None

    @property
    def getTime(self):
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet([seq.period for seq in self._sequenceList])

    @property
    def duration(self):
        """
        Interval on which the period set is defined.
        """
        result = self._sequenceList[0].period.duration
        for sequence in self._sequenceList[1:]:
            result = result + sequence.period.duration
        return result

    @property
    def timespan(self):
        """
        Interval on which the period set is defined ignoring the potential
        time gaps.
        """
        return self.endTimestamp - self.startTimestamp

    @property
    def period(self):
        """
        Period on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return Period(self.startTimestamp, self.endTimestamp,
                      self._sequenceList[0]._lower_inc, self._sequenceList[-1]._upper_inc)

    @property
    def numInstants(self):
        """
        Number of distinct instants.
        """
        return len(self.instants)

    @property
    def startInstant(self):
        """
        Start instant.
        """
        return self._sequenceList[0].startInstant

    @property
    def endInstant(self):
        """
        End instant.
        """
        return self._sequenceList[-1].endInstant

    def instantN(self, n):
        """
        N-th distinct instant.
        """
        # 1-based
        if 1 <= n <= len(self.instants):
            return (self.instants)[n - 1]
        else:
            raise Exception("ERROR: Out of range")

    @property
    def instants(self):
        """
        List of instants.
        """
        instantList = []
        for sequence in self._sequenceList:
            for instant in sequence._instantList:
                instantList.append(instant)
        return instantList

    @property
    def numTimestamps(self):
        """
        Number of distinct timestamps.
        """
        return len(self.timestamps)

    @property
    def startTimestamp(self):
        """
        Start timestamp.
        """
        return self._sequenceList[0].startInstant.getTimestamp

    @property
    def endTimestamp(self):
        """
        End timestamp.
        """
        return self._sequenceList[-1].endInstant.getTimestamp

    def timestampN(self, n):
        """
        N-th distinct timestamp.
        """
        # 1-based
        if 1 <= n <= len(self.timestamps):
            return (self.timestamps)[n - 1]
        else:
            raise Exception("ERROR: Out of range")

    @property
    def timestamps(self):
        """
        List of timestamps.
        """
        timestampList = []
        for sequence in self._sequenceList:
            for instant in sequence._instantList:
                timestampList.append(instant.getTimestamp)
        # Remove duplicates
        timestampList = list(dict.fromkeys(timestampList))
        return timestampList

    @property
    def numSequences(self):
        """
        Number of sequences.
        """
        return len(self._sequenceList)

    @property
    def startSequence(self):
        """
        Start sequence.
        """
        return self._sequenceList[0]

    @property
    def endSequence(self):
        """
        End sequence.
        """
        return self._sequenceList[-1]

    def sequenceN(self, n):
        """
        N-th sequence.
        """
        # 1-based
        if 1 <= n <= len(self._sequenceList):
            return self._sequenceList[n - 1]
        else:
            raise Exception("ERROR: Out of range")

    @property
    def sequences(self):
        """
        List of sequences.
        """
        return self._sequenceList

    def shift(self, timedelta):
        """
        Shift the temporal value by a time interval.
        """
        for seq in self._sequenceList:
            seq = seq.shift(timedelta)
        return self

    def intersectsTimestamp(self, timestamp):
        """
        Does the temporal value intersect the timestamp?
        """
        return any(seq.intersectsTimestamp(timestamp) for seq in self._sequenceList)

    def intersectsPeriod(self, period):
        """
        Does the temporal value intersect the period?
        """
        return any(seq.intersectsPeriod(period) for seq in self._sequenceList)

    # Comparisons are missing
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._sequenceList == other._sequenceList and self._interp == other._interp:
                return True
        return False

    def __str__(self):
        return tpoint_as_text(self._inner, 3)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._sequenceList!r}, {self._interp!r})')
