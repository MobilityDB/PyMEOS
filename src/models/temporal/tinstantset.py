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

from datetime import timedelta
from ..time import Period, PeriodSet
from ..temporal import TemporalInstants
from ..temporal.temporal_parser import parse_temporalinstset


class TInstantSet(TemporalInstants):
    """
    Abstract class for representing temporal values of instant set subtype.
    """

    def __init__(self, *argv):
        self._instantList = []
        # Constructor with a single argument of type string
        if len(argv) == 1 and isinstance(argv[0], str):
            elements = parse_temporalinstset(argv[0], 0)
            for inst in elements[2]:
                self._instantList.append(self.ComponentClass(inst[0], inst[1]))
        # Constructor with a single argument of type list
        elif len(argv) == 1 and isinstance(argv[0], list):
            # List of strings representing instant values
            if all(isinstance(arg, str) for arg in argv[0]):
                for arg in argv[0]:
                    self._instantList.append(self.ComponentClass(arg))
            # List of instant values
            elif all(isinstance(arg, self.ComponentClass) for arg in argv[0]):
                for arg in argv[0]:
                    self._instantList.append(arg)
            else:
                raise Exception("ERROR: Could not parse temporal instant set value")
        # Constructor with multiple arguments
        else:
            # Arguments are of type string
            if all(isinstance(arg, str) for arg in argv):
                for arg in argv:
                    self._instantList.append(self.ComponentClass(arg))
            # Arguments are of type instant
            elif all(isinstance(arg, self.ComponentClass) for arg in argv):
                for arg in argv:
                    self._instantList.append(arg)
            else:
                raise Exception("ERROR: Could not parse temporal instant set value")
        # Verify validity of the resulting instance
        self._valid()

    def _valid(self):
        if any(x._time > y._time for x, y in zip(self._instantList, self._instantList[1:])):
            raise Exception("ERROR: The timestamps of a temporal instant must be increasing")

    @classmethod
    def tempSubtype(cls):
        """
        Subtype of the temporal value, that is, ``'InstantSet'``.
        """
        return "InstantSet"

    def valueAtTimestamp(self, timestamp):
        """
        Value at timestamp.
        """
    def valueAtTimestamp(self, timestamp):
        """
        Value at timestamp.
        """
        for inst in self._instantList:
            if inst._time > timestamp:
                return None
            if inst._time == timestamp:
                return inst._value
        return None

    @property
    def getTime(self):
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet([inst.period for inst in self._instantList])

    @property
    def duration(self):
        """
        Interval on which the temporal value is defined. It is zero for
        temporal values of instant set subtype.
        """
        return timedelta(0)

    @property
    def timespan(self):
        """
        Interval on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return self.endTimestamp - self.startTimestamp

    @property
    def period(self):
        """
        Period on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return Period(self.startTimestamp, self.endTimestamp, True, True)

    def intersectsTimestamp(self, timestamp):
        """
        Does the temporal value intersect the timestamp?
        """
        return any(inst._time == timestamp for inst in self._instantList)

    def intersectsPeriod(self, period):
        """
        Does the temporal value intersect the period?
        """
        return any(period.contains_timestamp(inst._time) for inst in self._instantList)

    # Comparisons are missing
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._instantList == other._instantList:
                return True
        return False

    def __str__(self):
        return (f"'{{{TemporalInstants.__str__(self)}}}'")

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._instantList!r})')