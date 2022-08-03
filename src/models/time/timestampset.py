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
from datetime import datetime

import _meos_cffi
from dateutil.parser import parse

from .period import Period
from ...functions import pg_timestamp_in, timestamp_to_timestampset, union_timestampset_timestamp, \
    datetime_to_timestamptz

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


class TimestampSet:
    """
    Class for representing lists of distinct timestamp values.

    ``TimestampSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TimestampSet('{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TimestampSet(['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TimestampSet([parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])
        >>> TimestampSet('2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01')
        >>> TimestampSet(parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01'))

    """

    __slots__ = ['_inner']

    def __init__(self, *argv):
        # Constructor with a single argument of type string
        if len(argv) == 1 and isinstance(argv[0], str):
            ts = argv[0].strip()
            self._inner = _lib.timestampset_in(ts.encode('utf-8'))
        # Constructor with a single argument of type list
        elif len(argv) == 1 and isinstance(argv[0], list):
            # List of strings representing datetime values
            if all(isinstance(arg, str) for arg in argv[0]):
                self._inner = timestamp_to_timestampset(pg_timestamp_in(argv[0][0], -1))
                for arg in argv[0][1:]:
                    self._inner = union_timestampset_timestamp(self._inner, pg_timestamp_in(arg, -1))
            # List of datetimes
            elif all(isinstance(arg, datetime) for arg in argv[0]):
                self._inner = timestamp_to_timestampset(datetime_to_timestamptz(argv[0][0]))
                for arg in argv[0][1:]:
                    self._inner = union_timestampset_timestamp(self._inner, datetime_to_timestamptz(arg))
            else:
                raise Exception("ERROR: Could not parse timestamp set value")
        # Constructor with multiple arguments
        else:
            # Arguments are of type string
            if all(isinstance(arg, str) for arg in argv):
                self._inner = timestamp_to_timestampset(pg_timestamp_in(argv[0], -1))
                for arg in argv[1:]:
                    self._inner = union_timestampset_timestamp(self._inner, pg_timestamp_in(arg, -1))
            # Arguments are of type datetime
            elif all(isinstance(arg, datetime) for arg in argv):
                self._inner = timestamp_to_timestampset(datetime_to_timestamptz(argv[0]))
                for arg in argv[1:]:
                    self._inner = union_timestampset_timestamp(self._inner, datetime_to_timestamptz(arg))
            else:
                raise Exception("ERROR: Could not parse timestamp set value")

    @property
    def timespan(self):
        """
        Interval on which the timestamp set is defined ignoring the potential time gaps
        """
        return self._datetimeList[-1] - self._datetimeList[0]

    @property
    def period(self):
        """
        Period on which the timestamp set is defined ignoring the potential time gaps
        """
        return Period(self._datetimeList[0], self._datetimeList[-1], True, True)

    @property
    def numTimestamps(self):
        """
        Number of timestamps
        """
        return len(self._datetimeList)

    @property
    def startTimestamp(self):
        """
        Start timestamp
        """
        return self._datetimeList[0]

    @property
    def endTimestamp(self):
        """
        End timestamp
        """
        return self._datetimeList[-1]

    def timestampN(self, n):
        """
        N-th timestamp
        """
        # 1-based
        if 0 < n <= len(self._datetimeList):
            return self._datetimeList[n - 1]
        else:
            raise Exception("ERROR: there is no value at this index")

    @property
    def timestamps(self):
        """
        Distinct timestamps
        """
        return self._datetimeList

    def shift(self, timedelta):
        """
        Shift the timestamp set by a time interval
        """
        return TimestampSet([datetime + timedelta for datetime in self._datetimeList])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (len(other._datetimeList) == len(self._datetimeList) and
                    other._datetimeList == self._datetimeList):
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
        return TimestampSet(value)

    @staticmethod
    def write(value):
        if not isinstance(value, TimestampSet):
            raise ValueError('Value must be an instance of TimestampSet class')
        return value.__str__().strip("'")

    def __str__(self):
        return "'{{{}}}'".format(', '.join('{}'.format(datetime.__str__())
                                           for datetime in self._datetimeList))

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._datetimeList!r})')
