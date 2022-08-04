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
from datetime import datetime, timedelta
from dateutil.parser import parse
from ..time import Period, PeriodSet
from ..temporal import Temporal
from ..temporal.temporal_parser import parse_temporalinst


class TInstant(Temporal):
    """
    Abstract class for representing temporal values of instant subtype.
    """
    __slots__ = ['_value', '_time']

    @classmethod
    def tempSubtype(cls):
        """
        Subtype of the temporal value, that is, ``'Instant'``.
        """
        return "Instant"

    @property
    def getValue(self):
        """
        Value component.
        """
        return self._value

    @property
    def getValues(self):
        """
        List of distinct values.
        """
        return [self._value]

    @property
    def startValue(self):
        """
        Start value.
        """
        return self._value

    @property
    def endValue(self):
        """
        End value.
        """
        return self._value

    @property
    def minValue(self):
        """
        Minimum value.
        """
        return self._value

    @property
    def maxValue(self):
        """
        Maximum value.
        """
        return self._value

    def valueAtTimestamp(self, timestamp):
        """
        Value at timestamp.
        """
        if timestamp == self._time:
            return self._value
        else:
            return None

    @property
    def getTimestamp(self):
        """
        Timestamp.
        """
        return self._time

    @property
    def getTime(self):
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet([Period(self._time, self._time, True, True)])

    @property
    def duration(self):
        """
        Interval on which the temporal value is defined. It is zero for
        temporal values of instant subtype.
        """
        return timedelta(0)

    @property
    def timespan(self):
        """
        Interval on which the temporal value is defined ignoring the potential
        time gaps. It is zero for temporal values of instant subtype.
        """
        return timedelta(0)

    @property
    def period(self):
        """
        Period on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return Period(self._time, self._time, True, True)

    @property
    def numInstants(self):
        """
        Number of instants.
        """
        return 1

    @property
    def startInstant(self):
        """
        Start instant.
        """
        return self

    @property
    def endInstant(self):
        """
        End instant.
        """
        return self

    def instantN(self, n):
        """
        N-th instant.
        """
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    @property
    def instants(self):
        """
        List of instants.
        """
        return [self]

    @property
    def numTimestamps(self):
        """
        Number of timestamps.
        """
        return 1

    @property
    def startTimestamp(self):
        """
        Start timestamp.
        """
        return self._time

    @property
    def endTimestamp(self):
        """
        End timestamp.
        """
        return self._time

    def timestampN(self, n):
        """
        N-th timestamp
        """
        if n == 1:
            return self._time
        else:
            raise Exception("ERROR: Out of range")

    @property
    def timestamps(self):
        """
        List of timestamps.
        """
        return [self._time]

    def shift(self, timedelta):
        """
        Shift the temporal value by a time interval.
        """
        self._time += timedelta
        return self

    def intersectsTimestamp(self, timestamp):
        """
        Does the temporal value intersect the timestamp?
        """
        return self._time == timestamp

    def intersectsPeriod(self, period):
        """
        Does the temporal value intersect the period?
        """
        return period.contains_timestamp(self._time)

    # Comparisons are missing
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._value == other._value and self._time == other._time:
                return True
        return False

    def __str__(self):
        return f"{self._value!s}@{self._time!s}"

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._value!r}, {self._time!r})')

