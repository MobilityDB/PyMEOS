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
from abc import ABC, abstractmethod

from lib.functions import temporal_intersects_timestamp, datetime_to_timestamptz, temporal_intersects_timestampset, \
    temporal_intersects_period, temporal_intersects_periodset, temporal_time, interval_to_timedelta, temporal_duration, \
    temporal_timespan, temporal_num_instants, periodset_to_period, temporal_num_timestamps, timestamptz_to_datetime, \
    temporal_start_timestamp, temporal_end_timestamp, temporal_timestamp_n, temporal_timestamps, temporal_shift_tscale, \
    timedelta_to_interval, temporal_eq, temporal_le, temporal_lt, temporal_ge, temporal_gt, temporal_ne, temporal_cmp, \
    temporal_hash
from ..time import Period, PeriodSet

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class Temporal(ABC):
    __slots__ = ['_inner']
    """
    Abstract class for representing temporal values of any subtype.
    """

    BaseClass = None
    """
    Class of the base type, for example, ``float`` for ``TFloat``
    """

    BaseClassDiscrete = None
    """
    Boolean value that states whether the base type is discrete or not, 
    for example, ``True`` for ``int`` and ``False`` for ``float``
    """

    ComponentClass = None
    """
    Class of the components, for example, 

    1. ``TFloatInst`` for both ``TFloatI`` and ``TFloatSeq``
    2. ``TFloatSeq`` for ``TFloatS``.
    """

    @classmethod
    @abstractmethod
    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, one of ``'Instant'``,
        ``'InstantSet'``, ``'Sequence'``, or ``'SequenceSet'``.
        """
        pass

    @property
    @abstractmethod
    def values(self):
        """
        List of distinct values taken by the temporal value.
        """
        pass

    @property
    @abstractmethod
    def start_value(self):
        """
        Start value.
        """
        pass

    @property
    @abstractmethod
    def end_value(self):
        """
        End value.
        """
        pass

    @property
    def min_value(self):
        """
        Minimum value.
        """
        return min(self.values)

    @property
    def max_value(self):
        """
        Maximum value.
        """
        return max(self.values)

    @abstractmethod
    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        pass

    @property
    def time(self):
        """
        Period set on which the temporal value is defined.
        """
        return PeriodSet(_inner=temporal_time(self._inner))

    @property
    def duration(self):
        """
        Interval on which the temporal value is defined.
        """
        return interval_to_timedelta(temporal_duration(self._inner))

    @property
    def timespan(self):
        """
        Interval on which the temporal value is defined ignoring potential
        time gaps.
        """
        return interval_to_timedelta(temporal_timespan(self._inner))

    @property
    def period(self):
        """
        Period on which the temporal value is defined ignoring potential
        time gaps.
        """
        return Period(_inner=periodset_to_period(temporal_time(self._inner)))

    @property
    def num_instants(self):
        """
        Number of distinct instants.
        """
        return temporal_num_instants(self._inner)

    @property
    @abstractmethod
    def start_instant(self):
        """
         Start instant.
        """
        pass

    @property
    @abstractmethod
    def end_instant(self):
        """
        End instant.
        """
        pass

    @abstractmethod
    def instant_n(self, n):
        """
        N-th instant.
        """
        pass

    @property
    @abstractmethod
    def instants(self):
        """
        List of instants.
        """
        pass

    @property
    def num_timestamps(self):
        """
        Number of distinct timestamps.
        """
        return temporal_num_timestamps(self._inner)

    @property
    def start_timestamp(self):
        """
        Start timestamp.
        """
        return timestamptz_to_datetime(temporal_start_timestamp(self._inner))

    @property
    def end_timestamp(self):
        """
        End timestamp.
        """
        return timestamptz_to_datetime(temporal_end_timestamp(self._inner))

    def timestamp_n(self, n):
        """
        N-th timestamp.
        """
        return timestamptz_to_datetime(temporal_timestamp_n(self._inner, n))

    @property
    def timestamps(self):
        """
        List of timestamps.
        """
        ts, count = temporal_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    def shift(self, timedelta):
        """
        Shift the temporal value by a time interval
        """
        new_inner = temporal_shift_tscale(self._inner, timedelta_to_interval(timedelta), None)
        return self.__class__(_inner=new_inner)

    def intersects_timestamp(self, datetime):
        """
        Does the temporal value intersect the timestamp?
        """
        return temporal_intersects_timestamp(self._inner, datetime_to_timestamptz(datetime))

    def intersects_timestamp_set(self, timestamp_set):
        """
        Does the temporal value intersect the timestamp set?
        """
        return temporal_intersects_timestampset(self._inner, timestamp_set._inner)

    def intersects_period(self, period):
        """
        Does the temporal value intersect the period?
        """
        return temporal_intersects_period(self._inner, period._inner)

    def intersects_period_set(self, period_set):
        """
        Does the temporal value intersect the period set?
        """
        return temporal_intersects_periodset(self._inner, period_set._inner)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    def getquoted(self):
        return "{}".format(self.__str__())

    # End Psycopg2 interface.

    def __cmp__(self, other):
        """
        Comparison
        """
        if self.__class__ == other.__class__:
            return temporal_cmp(self._inner, other._inner)
        return 0

    def __lt__(self, other):
        """
        Less than
        """
        if self.__class__ == other.__class__:
            return temporal_lt(self._inner, other._inner)
        raise ComparisonError(self.__class__, other.__class__)

    def __le__(self, other):
        """
        Less or equal
        """
        if self.__class__ == other.__class__:
            return temporal_le(self._inner, other._inner)
        raise ComparisonError(self.__class__, other.__class__)

    def __eq__(self, other):
        """
        Equality
        """
        if self.__class__ == other.__class__:
            return temporal_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Inequality
        """
        if self.__class__ == other.__class__:
            return temporal_ne(self._inner, other._inner)
        return True

    def __ge__(self, other):
        """
        Greater or equal
        """
        if self.__class__ == other.__class__:
            return temporal_ge(self._inner, other._inner)
        raise ComparisonError(self.__class__, other.__class__)

    def __gt__(self, other):
        """
        Greater than
        """
        if self.__class__ == other.__class__:
            return temporal_gt(self._inner, other._inner)
        raise ComparisonError(self.__class__, other.__class__)

    def __hash__(self) -> int:
        return temporal_hash(self._inner)

    def __str__(self):
        """
        String
        """
        pass

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')


class ComparisonError(TypeError):
    def __init__(self, type1, type2) -> None:
        super().__init__(f'Comparison not supported between types {type1} and {type2}')
