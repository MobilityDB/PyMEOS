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

import warnings

from lib.functions import periodset_in, period_to_periodset, period_in, union_periodset_period, periodset_out, \
    periodset_duration, interval_to_timedelta, timestamptz_to_datetime, periodset_start_timestamp, \
    periodset_end_timestamp, periodset_timestamp_n, periodset_timestamps, periodset_num_periods, periodset_start_period, \
    periodset_end_period, periodset_period_n, periodset_periods, periodset_shift_tscale, timedelta_to_interval, \
    periodset_eq, periodset_ne, periodset_cmp, periodset_lt, periodset_le, periodset_ge, periodset_gt, \
    periodset_num_timestamps
from .period import Period

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

    __slots__ = ['_inner']

    def __init__(self, *argv, **kwargs):
        # Constructor with a single argument of type string
        if 'inner' in kwargs:
            self._inner = kwargs['inner']
        elif len(argv) == 1 and isinstance(argv[0], str):
            ps = argv[0].strip()
            self._inner = periodset_in(ps)
        # Constructor with a single argument of type list
        elif len(argv) == 1 and isinstance(argv[0], list):
            # List of strings representing periods
            if all(isinstance(arg, str) for arg in argv[0]):
                self._inner = period_to_periodset(period_in(argv[0][0]))
                for arg in argv[0][1:]:
                    self._inner = union_periodset_period(self._inner, period_in(arg))
            # List of periods
            elif all(isinstance(arg, Period) for arg in argv[0]):
                self._inner = period_to_periodset(argv[0][0]._inner)
                for arg in argv[0][1:]:
                    self._inner = union_periodset_period(self._inner, arg._inner)
            else:
                raise Exception("ERROR: Could not parse period set value")
        # Constructor with multiple arguments
        else:
            # Arguments are of type string
            if all(isinstance(arg, str) for arg in argv):
                self._inner = period_to_periodset(period_in(argv[0]))
                for arg in argv[1:]:
                    self._inner = union_periodset_period(self._inner, period_in(arg))
            # Arguments are of type period
            elif all(isinstance(arg, Period) for arg in argv):
                self._inner = period_to_periodset(argv[0]._inner)
                for arg in argv[1:]:
                    self._inner = union_periodset_period(self._inner, arg._inner)
            else:
                raise Exception("ERROR: Could not parse period set value")

    @property
    def duration(self):
        """
        Time interval on which the period set is defined
        """
        return interval_to_timedelta(periodset_duration(self._inner))

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
        start = self.startPeriod
        end = self.endPeriod
        return Period(lower=start.lower, upper=end.upper, lower_inc=start.lower_inc, upper_inc=end.upper_inc)

    @property
    def numTimestamps(self):
        """
        Number of distinct timestamps
        """
        return periodset_num_timestamps(self._inner)

    @property
    def startTimestamp(self):
        """
        Start timestamp
        """
        return timestamptz_to_datetime(periodset_start_timestamp(self._inner))

    @property
    def endTimestamp(self):
        """
        End timestamp
        """
        return timestamptz_to_datetime(periodset_end_timestamp(self._inner))

    def timestampN(self, n):
        """
        N-th distinct timestamp
        """
        # 1-based
        return timestamptz_to_datetime(periodset_timestamp_n(self._inner, n))

    @property
    def timestamps(self):
        """
        Distinct timestamps
        """
        ts, count = periodset_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[t]) for t in range(count)]

    @property
    def numPeriods(self):
        """
        Number of periods
        """
        return periodset_num_periods(self._inner)

    @property
    def startPeriod(self):
        """
        Start period
        """
        return Period(lower=periodset_start_period(self._inner), _inner=True)

    @property
    def endPeriod(self):
        """
        End period
        """
        return Period(lower=periodset_end_period(self._inner), _inner=True)

    def periodN(self, n):
        """
        N-th period
        """
        # 1-based
        return Period(lower=periodset_period_n(self._inner, n), _inner=True)

    @property
    def periods(self):
        """
        Periods
        """
        ps, count = periodset_periods(self._inner)
        return [Period(lower=ps[p], _inner=True) for p in range(count)]

    def shift(self, timedelta):
        """
        Shift the period set by a time interval
        """
        tss = periodset_shift_tscale(self._inner, timedelta_to_interval(timedelta), None)
        return PeriodSet(inner=tss)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return periodset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return periodset_ne(self._inner, other._inner)
        return False

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return periodset_cmp(self._inner, other._inner)
        return 0

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return periodset_lt(self._inner, other._inner)
        return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return periodset_le(self._inner, other._inner)
        return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return periodset_ge(self._inner, other._inner)
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return periodset_gt(self._inner, other._inner)
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
        return periodset_out(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._inner!r})')
