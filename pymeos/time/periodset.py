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

from __future__ import annotations

import warnings
from datetime import timedelta, datetime
from typing import Optional, Union, List
from typing import TYPE_CHECKING

from pymeos_cffi.functions import periodset_in, period_in, periodset_duration, interval_to_timedelta, \
    timestamptz_to_datetime, periodset_start_timestamp, \
    periodset_end_timestamp, periodset_timestamp_n, periodset_timestamps, periodset_num_periods, periodset_start_period, \
    periodset_end_period, periodset_period_n, periodset_periods, periodset_shift_tscale, timedelta_to_interval, \
    periodset_eq, periodset_ne, periodset_cmp, periodset_lt, periodset_le, periodset_ge, periodset_gt, \
    periodset_num_timestamps, periodset_make, periodset_hash, periodset_out, periodset_copy, \
    periodset_to_period, adjacent_periodset_period, adjacent_periodset_timestamp, adjacent_periodset_timestampset, \
    datetime_to_timestamptz, adjacent_periodset_periodset, contained_periodset_period, contained_periodset_periodset, \
    contains_periodset_period, contains_periodset_periodset, contains_periodset_timestamp, \
    contains_periodset_timestampset, overlaps_periodset_period, overlaps_periodset_periodset, \
    overlaps_periodset_timestampset, after_periodset_period, after_periodset_periodset, after_periodset_timestamp, \
    after_periodset_timestampset, before_periodset_period, before_periodset_periodset, before_periodset_timestamp, \
    before_periodset_timestampset, overafter_periodset_period, overafter_periodset_periodset, \
    overafter_periodset_timestamp, overafter_periodset_timestampset, overbefore_periodset_period, \
    overbefore_periodset_periodset, overbefore_periodset_timestamp, overbefore_periodset_timestampset

if TYPE_CHECKING:
    # Import here to use in type hints
    from .period import Period
    from .timestampset import TimestampSet

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

        >>> PeriodSet(string='{[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01], [2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]}')

    Another possibility is to give a list or tuple specifying the composing
    periods, which can be instances  of ``str`` or ``Period``. The composing
    periods must be given in increasing order.

        >>> PeriodSet(period_list=['[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]', '[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]'])
        >>> PeriodSet(period_list=[Period('[2019-09-08 00:00:00+01, 2019-09-10 00:00:00+01]'), Period('[2019-09-11 00:00:00+01, 2019-09-12 00:00:00+01]')])

    """

    __slots__ = ['_inner']

    def __init__(self, *, string: Optional[str] = None, period_list: Optional[List[Union[str, Period]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (period_list is not None)), \
            "Either string must be not None or period_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = periodset_in(string)
        else:
            periods = [period_in(period) if isinstance(period, str) else period._inner for period in period_list]
            self._inner = periodset_make(periods, len(periods), normalize)

    @property
    def duration(self) -> timedelta:
        """
        Time interval on which the period set is defined
        """
        return interval_to_timedelta(periodset_duration(self._inner))

    @property
    def timespan(self) -> timedelta:
        """
        Time interval on which the period set is defined
        """
        return self.end_timestamp - self.start_timestamp

    def to_period(self) -> Period:
        """
        Period on which the period set is defined ignoring the potential time gaps
        """
        from .period import Period
        return Period(_inner=periodset_to_period(self._inner))

    @property
    def num_timestamps(self) -> int:
        """
        Number of distinct timestamps
        """
        return periodset_num_timestamps(self._inner)

    @property
    def start_timestamp(self) -> datetime:
        """
        Start timestamp
        """
        return timestamptz_to_datetime(periodset_start_timestamp(self._inner))

    @property
    def end_timestamp(self) -> datetime:
        """
        End timestamp
        """
        return timestamptz_to_datetime(periodset_end_timestamp(self._inner))

    def timestamp_n(self, n) -> datetime:
        """
        N-th distinct timestamp
        """
        # 1-based
        return timestamptz_to_datetime(periodset_timestamp_n(self._inner, n))

    @property
    def timestamps(self) -> List[datetime]:
        """
        Distinct timestamps
        """
        ts, count = periodset_timestamps(self._inner)
        return [timestamptz_to_datetime(ts[i]) for i in range(count)]

    @property
    def num_periods(self) -> int:
        """
        Number of periods
        """
        return periodset_num_periods(self._inner)

    @property
    def start_period(self) -> Period:
        """
        Start period
        """
        from .period import Period
        return Period(_inner=periodset_start_period(self._inner))

    @property
    def end_period(self) -> Period:
        """
        End period
        """
        from .period import Period
        return Period(_inner=periodset_end_period(self._inner))

    def period_n(self, n) -> Period:
        """
        N-th period
        """
        # 1-based
        from .period import Period
        return Period(_inner=periodset_period_n(self._inner, n))

    @property
    def periods(self) -> List[Period]:
        """
        Periods
        """
        from .period import Period
        ps, count = periodset_periods(self._inner)
        return [Period(_inner=ps[i]) for i in range(count)]

    def shift(self, timedelta) -> PeriodSet:
        """
        Shift the period set by a time interval
        """
        tss = periodset_shift_tscale(self._inner, timedelta_to_interval(timedelta), None)
        return PeriodSet(_inner=tss)

    def is_adjacent(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return adjacent_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return adjacent_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return adjacent_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return adjacent_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[Period, PeriodSet]) -> bool:
        from .period import Period
        if isinstance(container, Period):
            return contained_periodset_period(self._inner, container._inner)
        elif isinstance(container, PeriodSet):
            return contained_periodset_periodset(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(content, Period):
            return contains_periodset_period(self._inner, content._inner)
        if isinstance(content, PeriodSet):
            return contains_periodset_periodset(self._inner, content._inner)
        elif isinstance(content, datetime):
            return contains_periodset_timestamp(self._inner, datetime_to_timestamptz(content))
        elif isinstance(content, TimestampSet):
            return contains_periodset_timestampset(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[Period, PeriodSet, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overlaps_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overlaps_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, TimestampSet):
            return overlaps_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return after_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return after_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return after_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return after_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return before_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return before_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return before_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return before_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overafter_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overafter_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overafter_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overafter_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[Period, PeriodSet, datetime, TimestampSet]) -> bool:
        from .period import Period
        from .timestampset import TimestampSet
        if isinstance(other, Period):
            return overbefore_periodset_period(self._inner, other._inner)
        if isinstance(other, PeriodSet):
            return overbefore_periodset_periodset(self._inner, other._inner)
        elif isinstance(other, datetime):
            return overbefore_periodset_timestamp(self._inner, datetime_to_timestamptz(other))
        elif isinstance(other, TimestampSet):
            return overbefore_periodset_timestampset(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def __contains__(self, item):
        return self.contains(item)

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
        return PeriodSet(string=value)

    def __copy__(self):
        inner_copy = periodset_copy(self._inner)
        return PeriodSet(_inner=inner_copy)

    def __str__(self):
        return periodset_out(self._inner)

    def __hash__(self) -> int:
        return periodset_hash(self._inner)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')
