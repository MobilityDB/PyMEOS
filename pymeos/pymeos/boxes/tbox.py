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
from datetime import datetime, timedelta
from typing import Optional, Union

from dateutil.parser import parse
from pymeos_cffi import int_to_tbox, float_to_tbox, span_to_tbox, datetime_to_timestamptz, tnumber_to_tbox, \
    tbox_to_period
from pymeos_cffi.functions import tbox_in, floatspan_make, tbox_make, tbox_out, tbox_eq, tbox_hasx, tbox_hast, \
    tbox_xmin, tbox_tmin, timestamptz_to_datetime, tbox_tmax, tbox_xmax, tbox_expand, tbox_expand_value, \
    tbox_expand_temporal, timedelta_to_interval, tbox_shift_tscale, contains_tbox_tbox, contained_tbox_tbox, \
    adjacent_tbox_tbox, overlaps_tbox_tbox, same_tbox_tbox, overafter_tbox_tbox, left_tbox_tbox, overleft_tbox_tbox, \
    right_tbox_tbox, overright_tbox_tbox, before_tbox_tbox, overbefore_tbox_tbox, after_tbox_tbox, union_tbox_tbox, \
    intersection_tbox_tbox, tbox_cmp, tbox_lt, tbox_le, tbox_gt, tbox_ge, tbox_copy, tbox_as_hexwkb, tbox_from_hexwkb, \
    intspan_make, timestamp_to_tbox, timestampset_to_tbox, period_to_tbox, periodset_to_tbox, int_timestamp_to_tbox, \
    float_timestamp_to_tbox, int_period_to_tbox, float_period_to_tbox, span_timestamp_to_tbox, span_period_to_tbox
from spans import intrange, floatrange

from ..main import TNumber
from ..time import TimestampSet, Period, PeriodSet

try:
    # Do not make psycopg2 a requirement.
    from psycopg2.extensions import ISQLQuote
except ImportError:
    warnings.warn('psycopg2 not installed', ImportWarning)


class TBox:
    """
    Class for representing bounding boxes with value (``X``) and/or time (``T``)
    dimensions.


    ``TBox`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TBox(string="TBOX((1.0, 2000-01-01), (2.0, 2000-01-02))")
        >>> TBox(string="TBOX((1.0,), (2.0,))")
        >>> TBox(string="TBOX((, 2000-01-01), (, 2000-01-02))")

    Another possibility is to give the bounds in the following order:
    ``xmin``, ``tmin``, ``xmax``, ``tmax``, where the bounds can be
    instances of ``str``, ``float`` or ``datetime``. All arguments are
    optional but they must be given in pairs for each dimension and at
    least one pair must be given.

        >>> TBox(xmin="1.0", tmin="2000-01-01", xmax="2.0", tmax="2000-01-02")
        >>> TBox(xmin=1.0, xmax=2.0)
        >>> TBox(tmin=parse("2000-01-01"), tmax=parse("2000-01-02"))

    """
    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *,
                 xmin: Optional[Union[str, float]] = None,
                 tmin: Optional[Union[str, datetime]] = None,
                 xmax: Optional[Union[str, float]] = None,
                 tmax: Optional[Union[str, datetime]] = None,
                 _inner=None):
        assert (_inner is not None) or (string is not None) != (
                (xmin is not None and xmax is not None) or (tmin is not None and tmax is not None)), \
            "Either string must be not None or at least a bound pair (xmin/max or tmin/max) must be not None"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = tbox_in(string)
        else:
            span = None
            period = None
            if xmin is not None and xmax is not None:
                span = floatspan_make(float(xmin), float(xmax), True, True)
            if tmin is not None and tmax is not None:
                period = Period(lower=tmin, upper=tmax, lower_inc=True, upper_inc=True)._inner
            self._inner = tbox_make(period, span)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> TBox:
        result = tbox_from_hexwkb(hexwkb)
        return TBox(_inner=result)

    def as_hexwkb(self) -> str:
        return tbox_as_hexwkb(self._inner, -1)[0]

    @staticmethod
    def from_value(value: Union[int, float, intrange, floatrange]) -> TBox:
        if isinstance(value, int):
            result = int_to_tbox(value)
        elif isinstance(value, float):
            result = float_to_tbox(value)
        elif isinstance(value, intrange):
            result = span_to_tbox(intspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc))
        elif isinstance(value, floatrange):
            result = span_to_tbox(floatspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc))
        else:
            raise TypeError(f'Operation not supported with type {value.__class__}')
        return TBox(_inner=result)

    @staticmethod
    def from_time(time: Union[datetime, TimestampSet, Period, PeriodSet]) -> TBox:
        if isinstance(time, datetime):
            result = timestamp_to_tbox(datetime_to_timestamptz(time))
        elif isinstance(time, TimestampSet):
            result = timestampset_to_tbox(time)
        elif isinstance(time, Period):
            result = period_to_tbox(time)
        elif isinstance(time, PeriodSet):
            result = periodset_to_tbox(time)
        else:
            raise TypeError(f'Operation not supported with type {time.__class__}')
        return TBox(_inner=result)

    @staticmethod
    def from_value_time(value: Union[int, float, intrange, floatrange],
                        time: Union[datetime, Period]) -> TBox:
        if isinstance(value, int) and isinstance(time, datetime):
            result = int_timestamp_to_tbox(value, datetime_to_timestamptz(time))
        elif isinstance(value, int) and isinstance(time, Period):
            result = int_period_to_tbox(value, time)
        elif isinstance(value, float) and isinstance(time, datetime):
            result = float_timestamp_to_tbox(value, datetime_to_timestamptz(time))
        elif isinstance(value, float) and isinstance(time, Period):
            result = float_period_to_tbox(value, time)
        elif isinstance(value, intrange) and isinstance(time, datetime):
            result = span_timestamp_to_tbox(intspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc),
                                            datetime_to_timestamptz(time))
        elif isinstance(value, intrange) and isinstance(time, Period):
            result = span_period_to_tbox(intspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc), time)
        elif isinstance(value, floatrange) and isinstance(time, Period):
            result = span_period_to_tbox(floatspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc),
                                         time)
        elif isinstance(value, floatrange) and isinstance(time, datetime):
            result = span_timestamp_to_tbox(floatspan_make(value.lower, value.upper, value.lower_inc, value.upper_inc),
                                            datetime_to_timestamptz(time))
        else:
            raise TypeError(f'Operation not supported with types {value.__class__} and {time.__class__}')
        return TBox(_inner=result)

    @staticmethod
    def from_tnumber(temporal: TNumber) -> TBox:
        return TBox(_inner=tnumber_to_tbox(temporal._inner))

    def to_floatrange(self) -> floatrange:
        # TODO: Check that a Box always has inclusive bound
        return floatrange(self.xmin, self.xmax, True, True)

    def to_period(self) -> Period:
        return Period(_inner=tbox_to_period(self._inner))

    @property
    def has_x(self):
        return tbox_hasx(self._inner)

    @property
    def has_t(self):
        return tbox_hast(self._inner)

    @property
    def xmin(self):
        """
        Minimum X
        """
        return tbox_xmin(self._inner)

    @property
    def tmin(self):
        """
        Minimum T
        """
        return timestamptz_to_datetime(tbox_tmin(self._inner))

    @property
    def xmax(self):
        """
        Maximum X
        """
        return tbox_xmax(self._inner)

    @property
    def tmax(self):
        """
        Maximum T
        """
        return timestamptz_to_datetime(tbox_tmax(self._inner))

    def expand(self, other: Union[TBox, float, timedelta]) -> TBox:
        if isinstance(other, TBox):
            result = tbox_copy(self._inner)
            tbox_expand(other._inner, result)
        elif isinstance(other, float):
            result = tbox_expand_value(self._inner, other)
        elif isinstance(other, timedelta):
            result = tbox_expand_temporal(self._inner, timedelta_to_interval(other))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return TBox(_inner=result)

    def shift_tscale(self, shift_delta: Optional[timedelta] = None, scale_delta: Optional[timedelta] = None):
        """
        Shift the temporal box by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        tbox_shift_tscale(
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None,
            self._inner
        )

    def union(self, other: TBox) -> TBox:
        return TBox(_inner=union_tbox_tbox(self._inner, other._inner))

    def intersection(self, other: TBox) -> TBox:
        return TBox(_inner=intersection_tbox_tbox(self._inner, other._inner))

    def is_adjacent(self, container: TBox) -> bool:
        return adjacent_tbox_tbox(self._inner, container._inner)

    def is_contained_in(self, container: TBox) -> bool:
        return contained_tbox_tbox(self._inner, container._inner)

    def contains(self, content: TBox) -> bool:
        return contains_tbox_tbox(self._inner, content._inner)

    def overlaps(self, content: TBox) -> bool:
        return overlaps_tbox_tbox(self._inner, content._inner)

    def is_same(self, content: TBox) -> bool:
        return same_tbox_tbox(self._inner, content._inner)

    def is_left(self, content: TBox) -> bool:
        return left_tbox_tbox(self._inner, content._inner)

    def is_over_or_left(self, content: TBox) -> bool:
        return overleft_tbox_tbox(self._inner, content._inner)

    def is_right(self, content: TBox) -> bool:
        return right_tbox_tbox(self._inner, content._inner)

    def is_over_or_right(self, content: TBox) -> bool:
        return overright_tbox_tbox(self._inner, content._inner)

    def is_before(self, content: TBox) -> bool:
        return before_tbox_tbox(self._inner, content._inner)

    def is_over_or_before(self, content: TBox) -> bool:
        return overbefore_tbox_tbox(self._inner, content._inner)

    def is_after(self, content: TBox) -> bool:
        return after_tbox_tbox(self._inner, content._inner)

    def is_over_or_after(self, content: TBox) -> bool:
        return overafter_tbox_tbox(self._inner, content._inner)

    def __add__(self, other):
        return self.union(other)

    def __mul__(self, other):
        return self.intersection(other)

    def __contains__(self, item):
        return self.contains(item)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return tbox_eq(self._inner, other._inner)
        return False

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return tbox_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return tbox_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return tbox_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return tbox_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return tbox_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __copy__(self) -> TBox:
        inner_copy = tbox_copy(self._inner)
        return TBox(_inner=inner_copy)

    def __str__(self):
        return tbox_out(self._inner, 3)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        return TBox(string=value)

    # Psycopg2 interface.
    def __conform__(self, protocol):
        if protocol is ISQLQuote:
            return self

    # End Psycopg2 interface.
