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

from typing import Optional, Union, List

from pymeos_cffi import *
from spans import intrange, floatrange

from ..main import TNumber
from ..time import *


class TBox:
    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *,
                 xmin: Optional[Union[str, float]] = None,
                 tmin: Optional[Union[str, datetime]] = None,
                 xmax: Optional[Union[str, float]] = None,
                 tmax: Optional[Union[str, datetime]] = None,
                 xmin_inc: bool = True,
                 xmax_inc: bool = True,
                 tmin_inc: bool = True,
                 tmax_inc: bool = True,
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
                span = floatspan_make(float(xmin), float(xmax), xmin_inc, xmax_inc)
            if tmin is not None and tmax is not None:
                period = Period(lower=tmin, upper=tmax, lower_inc=tmin_inc, upper_inc=tmax_inc)._inner
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
    def from_time(time: Time) -> TBox:
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

    def tile(self, size: float, duration: Union[timedelta, str],
             origin: Optional[float] = None, start: Union[datetime, str, None] = None) -> List[List[TBox]]:
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) else pg_interval_in(duration, -1)
        st = datetime_to_timestamptz(start) if isinstance(start, datetime) \
            else pg_timestamptz_in(start, -1) if isinstance(start, str) \
            else None
        tiles, rows, columns = tbox_tile_list(self._inner, size, dt, origin, st)
        return [[TBox(_inner=tiles + (c * rows + r)) for c in range(columns)] for r in range(rows)]

    def tile_flat(self, size: float, duration: Union[timedelta, str],
                  origin: Optional[float] = None, start: Union[datetime, str, None] = None) -> List[TBox]:
        tiles = self.tile(size, duration, origin, start)
        return [box for row in tiles for box in row]

    def to_floatrange(self) -> floatrange:
        return floatspan_to_floatrange(tbox_to_floatspan(self._inner))

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

    # TODO: Check returning None for empty intersection is the desired behaviour
    def intersection(self, other: TBox) -> Optional[TBox]:
        result = intersection_tbox_tbox(self._inner, other._inner)
        return TBox(_inner=result) if result else None

    def is_adjacent(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return adjacent_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return adjacent_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[TBox, TNumber]) -> bool:
        if isinstance(container, TBox):
            return contained_tbox_tbox(self._inner, container._inner)
        elif isinstance(container, TNumber):
            return contained_tbox_tnumber(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[TBox, TNumber]) -> bool:
        if isinstance(content, TBox):
            return contains_tbox_tbox(self._inner, content._inner)
        elif isinstance(content, TNumber):
            return contains_tbox_tnumber(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overlaps_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overlaps_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return same_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return same_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_left(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return left_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return left_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_left(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overleft_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overleft_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_right(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return right_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return right_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_right(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overright_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overright_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return before_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return before_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overbefore_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overbefore_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return after_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return after_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overafter_tbox_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overafter_tbox_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def nearest_approach_distance(self, other: TBox) -> float:
        if isinstance(other, TBox):
            return nad_tbox_tbox(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

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

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return tbox_ne(self._inner, other._inner)
        return True

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
        return tbox_out(self._inner, 6)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot(self, *args, **kwargs):
        from ..plotters import BoxPlotter
        return BoxPlotter.plot_tbox(self, *args, **kwargs)

    @staticmethod
    def read_from_cursor(value, _):
        if not value:
            return None
        return TBox(string=value)
