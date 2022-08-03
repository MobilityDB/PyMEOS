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

import re
from .period import Period
import warnings

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class PeriodSet:
    """
    Class for representing lists of disjoint periods.

    ``PeriodSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> PeriodSet('{[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01], [2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]}')

    Another possibility is to give a list or tuple specifying the composing
    periods, which can be instances  of ``str`` or ``Period``. The composing
    periods must be given in increasing order.

        >>> PeriodSet(['[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'])
        >>> PeriodSet([Period('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), Period('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')])
        >>> PeriodSet('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')
        >>> PeriodSet(Period('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), Period('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'))

    """

    __slots__ = ['_periodList']

    def __init__(self, *argv):
        self._periodList = []
        # Constructor with a single argument of type string
        if len(argv) == 1 and isinstance(argv[0], str):
            ps = argv[0].strip()
            if ps[0] == '{' and ps[-1] == '}':
                p = re.compile(r'[\[|\(].*?[^\]\)][\]|\)]')
                periods = p.findall(ps)
                for period in periods:
                    self._periodList.append(Period(period))
            else:
                raise Exception("ERROR: Could not parse period set value")
        # Constructor with a single argument of type list
        elif len(argv) == 1 and isinstance(argv[0], list):
            # List of strings representing periods
            if all(isinstance(arg, str) for arg in argv[0]):
                for arg in argv[0]:
                    self._periodList.append(Period(arg))
            # List of periods
            elif all(isinstance(arg, Period) for arg in argv[0]):
                for arg in argv[0]:
                    self._periodList.append(arg)
            else:
                raise Exception("ERROR: Could not parse period set value")
        # Constructor with multiple arguments
        else:
            # Arguments are of type string
            if all(isinstance(arg, str) for arg in argv):
                for arg in argv:
                    self._periodList.append(Period(arg))
            # Arguments are of type period
            elif all(isinstance(arg, Period) for arg in argv):
                for arg in argv:
                    self._periodList.append(arg)
            else:
                raise Exception("ERROR: Could not parse period set value")
        # Verify validity of the resulting instance
        self._valid()

    def _valid(self):
        if any(x.upper > y.lower or \
            (x.upper == y.lower and x.upper_inc and x.lower_inc) \
                   for x, y in zip(self._periodList, self._periodList[1:])):
            raise Exception("ERROR: The periods of a period set cannot overlap")
        return True

    @property
    def duration(self):
        """
        Time interval on which the period set is defined
        """
        result = self._periodList[0].duration
        for period in self._periodList[1:]:
            result = result + period.duration
        return result

    @property
    def timespan(self):
        """
        Time interval on which the period set is defined
        """
        return self.endTimestamp - self.startTimestamp


    @property
    def period(self):
        """
        Period on which the period set is defined ignoring the potential time gaps
        """
        return Period((self._periodList[0]).lower, (self._periodList[-1]).upper,
                      self._periodList[0].lower_inc, self._periodList[-1].upper_inc)

    @property
    def numTimestamps(self):
        """
        Number of distinct timestamps
        """
        return len(self.timestamps)

    @property
    def startTimestamp(self):
        """
        Start timestamp
        """
        return self._periodList[0].lower

    @property
    def endTimestamp(self):
        """
        End timestamp
        """
        return self._periodList[-1].upper

    def timestampN(self, n):
        """
        N-th distinct timestamp
        """
        # 1-based
        if 1 <= n <= len(self.timestamps):
            return (self.timestamps)[n - 1]
        else:
            raise Exception("ERROR: there is no value at this index")

    @property
    def timestamps(self):
        """
        Distinct timestamps
        """
        timestampList = []
        for period in self._periodList:
            timestampList.append(period.lower)
            timestampList.append(period.upper)
        # Remove duplicates
        return list(dict.fromkeys(timestampList))

    @property
    def numPeriods(self):
        """
        Number of periods
        """
        return len(self._periodList)

    @property
    def startPeriod(self):
        """
        Start period
        """
        return self._periodList[0]

    @property
    def endPeriod(self):
        """
        End period
        """
        return self._periodList[self.numPeriods - 1]

    def periodN(self, n):
        """
        N-th period
        """
        # 1-based
        if 1 <= n <= len(self._periodList):
            return self._periodList[n - 1]
        else:
            raise Exception("ERROR: Out of range")

    @property
    def periods(self):
        """
        Periods
        """
        return self._periodList

    def shift(self, timedelta):
        """
        Shift the period set by a time interval
        """
        return PeriodSet([period.shift(timedelta) for period in self._periodList])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (len(other._periodList) == len(self._periodList) and
                other._periodList == self._periodList):
                return True
        return False

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "{}".format(self.__str__())
    # End Psycopg2 interface.

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return PeriodSet(value)

    @staticmethod
    def write(value):
        if not isinstance(value, PeriodSet):
            raise ValueError('Value must be an instance of PeriodSet class')
        return value.__str__().strip("'")

    def __str__(self):
        return "'{{{}}}'".format(', '.join('{}'.format(period.__str__().replace("'", ""))
            for period in self._periodList))

    def __repr__(self):
        return (f'{self.__class__.__name__ }'
                f'({self._periodList!r})')