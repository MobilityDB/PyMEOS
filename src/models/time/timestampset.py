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
from typing import Optional, List, Union

from dateutil.parser import parse

from lib.functions import pg_timestamp_in, datetime_to_timestamptz, timestampset_end_timestamp, \
    timestampset_start_timestamp, timestampset_num_timestamps, \
    timestampset_timestamps, \
    timestampset_timestamp_n, \
    timestampset_out, timestamptz_to_datetime, pg_timestamptz_out, timestampset_shift_tscale, timedelta_to_interval, \
    timestampset_eq, timestampset_ne, timestampset_cmp, timestampset_lt, timestampset_le, timestampset_ge, \
    timestampset_gt, timestampset_make, timestampset_in, timestampset_hash, timestampset_copy
from .period import Period

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class TimestampSet:
    """
    Class for representing lists of distinct timestamp values.

    ``TimestampSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TimestampSet(string='{2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01, 2019-09-11 00:00:00+01}')

    Another possibility is to give a tuple or list of composing timestamps,
    which can be instances of ``str`` or ``datetime``. The composing timestamps
    must be given in increasing order.

        >>> TimestampSet(timestamp_list=['2019-09-08 00:00:00+01', '2019-09-10 00:00:00+01', '2019-09-11 00:00:00+01'])
        >>> TimestampSet(timestamp_list=[parse('2019-09-08 00:00:00+01'), parse('2019-09-10 00:00:00+01'), parse('2019-09-11 00:00:00+01')])

    """

    __slots__ = ['_inner']

    def __init__(self, *, string: Optional[str] = None, timestamp_list: Optional[List[Union[str, datetime]]] = None,
                 _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (timestamp_list is not None)), \
            "Either string must be not None or timestamp_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = timestampset_in(string)
        else:
            times = [pg_timestamp_in(ts, -1) if isinstance(ts, str) else datetime_to_timestamptz(ts)
                     for ts in timestamp_list]
            self._inner = timestampset_make(times, len(times))

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
        return Period(lower=pg_timestamptz_out(timestampset_start_timestamp(self._inner)),
                      upper=pg_timestamptz_out(timestampset_end_timestamp(self._inner)),
                      lower_inc=True, upper_inc=True)

    @property
    def num_timestamps(self):
        """
        Number of timestamps
        """
        return timestampset_num_timestamps(self._inner)

    @property
    def start_timestamp(self):
        """
        Start timestamp
        """
        return timestamptz_to_datetime(timestampset_start_timestamp(self._inner))

    @property
    def end_timestamp(self):
        """
        End timestamp
        """
        return timestamptz_to_datetime(timestampset_end_timestamp(self._inner))

    def timestamp_n(self, n):
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
        return [timestamptz_to_datetime(tss[i]) for i in range(self.num_timestamps)]

    def shift(self, timedelta):
        """
        Shift the timestamp set by a time interval
        """
        tss = timestampset_shift_tscale(self._inner, timedelta_to_interval(timedelta), None)
        return TimestampSet(_inner=tss)

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
        return TimestampSet(string=value)

    @staticmethod
    def write(value):
        if not isinstance(value, TimestampSet):
            raise ValueError('Value must be an instance of TimestampSet class')
        return value.__str__().strip("'")

    def __copy__(self):
        inner_copy = timestampset_copy(self._inner)
        return TimestampSet(_inner=inner_copy)

    def __str__(self):
        return timestampset_out(self._inner)

    def __hash__(self) -> int:
        return timestampset_hash(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')
