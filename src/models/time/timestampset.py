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

from lib.functions import pg_timestamp_in, timestamp_to_timestampset, union_timestampset_timestamp, \
    datetime_to_timestamptz, timestampset_end_timestamp, timestampset_start_timestamp, timestampset_num_timestamps, \
    timestampset_timestamps, \
    timestampset_timestamp_n, \
    timestampset_out, timestamptz_to_datetime, pg_timestamptz_out, timestampset_shift_tscale, timedelta_to_interval, \
    timestampset_eq, timestampset_ne, timestampset_cmp, timestampset_lt, timestampset_le, timestampset_ge, \
    timestampset_gt
from .period import Period

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

    def __init__(self, *argv, **kwargs):
        # Constructor with a single argument of type string
        if 'inner' in kwargs:
            self._inner = kwargs['inner']
        elif len(argv) == 1 and isinstance(argv[0], str):
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
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner)) - \
               timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    @property
    def period(self):
        """
        Period on which the timestamp set is defined ignoring the potential time gaps
        """
        return Period(pg_timestamptz_out(timestampset_start_timestamp(self._inner)),
                      pg_timestamptz_out(timestampset_end_timestamp(self._inner)), True, True)

    @property
    def numTimestamps(self):
        """
        Number of timestamps
        """
        return timestampset_num_timestamps(self._inner)

    @property
    def startTimestamp(self):
        """
        Start timestamp
        """
        return timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    @property
    def endTimestamp(self):
        """
        End timestamp
        """
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner))

    def timestampN(self, n):
        """
        N-th timestamp
        """
        # 1-based
        return timestamptz_to_datetime(timestampset_timestamp_n(self._inner, n))

    @property
    def timestamps(self):
        """
        Distinct timestamps
        """
        tss = timestampset_timestamps(self._inner)
        return [timestamptz_to_datetime(tss[i]) for i in range(self.numTimestamps)]

    def shift(self, timedelta):
        """
        Shift the timestamp set by a time interval
        """
        tss = timestampset_shift_tscale(self._inner, timedelta_to_interval(timedelta), None)
        return TimestampSet(inner=tss)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_ne(self._inner, other._inner)
        return False

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_cmp(self._inner, other._inner)
        return 0

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_lt(self._inner, other._inner)
        return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_le(self._inner, other._inner)
        return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_ge(self._inner, other._inner)
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return timestampset_gt(self._inner, other._inner)
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
        return timestampset_out(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._inner!r})')
