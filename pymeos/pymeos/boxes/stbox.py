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

from postgis import Geometry
from pymeos_cffi import *
from shapely.geometry.base import BaseGeometry

from ..main import TPoint
from ..time import *


class STBox:
    __slots__ = ['_inner']

    def __init__(self, string: Optional[str] = None, *,
                 xmin: Optional[Union[str, float]] = None, xmax: Optional[Union[str, float]] = None,
                 ymin: Optional[Union[str, float]] = None, ymax: Optional[Union[str, float]] = None,
                 zmin: Optional[Union[str, float]] = None, zmax: Optional[Union[str, float]] = None,
                 tmin: Optional[Union[str, datetime]] = None, tmax: Optional[Union[str, datetime]] = None,
                 tmin_inc: bool = True, tmax_inc: bool = True,
                 geodetic: bool = False, srid: Optional[int] = None,
                 _inner=None):

        assert (_inner is not None) or (string is not None) != (
                (xmin is not None and xmax is not None and ymin is not None and ymax is not None) or
                (tmin is not None and tmax is not None)), \
            "Either string must be not None or at least a bound pair (xmin/max and ymin/max, or tmin/max)" \
            " must be not None"

        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = stbox_in(string)
        else:
            period = None
            hast = tmin is not None and tmax is not None
            hasx = xmin is not None and xmax is not None and ymin is not None and ymax is not None
            hasz = zmin is not None and zmax is not None
            if hast:
                period = Period(lower=tmin, upper=tmax, lower_inc=tmin_inc, upper_inc=tmax_inc)._inner
            self._inner = stbox_make(period, hasx, hasz, geodetic, srid or 0, float(xmin or 0), float(xmax or 0),
                                     float(ymin or 0), float(ymax or 0), float(zmin or 0), float(zmax or 0))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> STBox:
        result = stbox_from_hexwkb(hexwkb)
        return STBox(_inner=result)

    def as_hexwkb(self) -> str:
        return stbox_as_hexwkb(self._inner, -1)[0]

    @staticmethod
    def from_space(value: Geometry) -> STBox:
        return STBox.from_geometry(value)

    @staticmethod
    def from_geometry(geom: Geometry) -> STBox:
        gs = gserialized_in(geom.to_ewkb(), -1)
        return STBox(_inner=geo_to_stbox(gs))

    @staticmethod
    def from_time(time: Time) -> STBox:
        if isinstance(time, datetime):
            result = timestamp_to_stbox(datetime_to_timestamptz(time))
        elif isinstance(time, TimestampSet):
            result = timestampset_to_stbox(time)
        elif isinstance(time, Period):
            result = period_to_stbox(time)
        elif isinstance(time, PeriodSet):
            result = periodset_to_stbox(time)
        else:
            raise TypeError(f'Operation not supported with type {time.__class__}')
        return STBox(_inner=result)

    @staticmethod
    def from_expanding_bounding_box(value: Union[Geometry, TPoint], expansion: float):
        if isinstance(value, Geometry):
            gs = gserialized_in(value.to_ewkb(), -1)
            result = geo_expand_spatial(gs, expansion)
        elif isinstance(value, TPoint):
            result = tpoint_expand_spatial(value._inner, expansion)
        else:
            raise TypeError(f'Operation not supported with type {value.__class__}')
        return STBox(_inner=result)

    @staticmethod
    def from_space_time(value: Geometry, time: Union[datetime, Period]) -> STBox:
        return STBox.from_geometry_time(value, time)

    @staticmethod
    def from_geometry_time(geometry: Geometry, time: Union[datetime, Period]) -> STBox:
        gs = gserialized_in(geometry.to_ewkb(), -1)
        if isinstance(time, datetime):
            result = geo_timestamp_to_stbox(gs, datetime_to_timestamptz(time))
        elif isinstance(time, Period):
            result = geo_period_to_stbox(gs, time._inner)
        else:
            raise TypeError(f'Operation not supported with types {geometry.__class__} and {time.__class__}')
        return STBox(_inner=result)

    @staticmethod
    def from_tpoint(temporal: TPoint) -> STBox:
        return STBox(_inner=tpoint_to_stbox(temporal._inner))

    def tile(self, size: float, duration: Optional[Union[timedelta, str]] = None,
             origin: Optional[Union[BaseGeometry, Geometry]] = None,
             start: Union[datetime, str, None] = None) -> List[List[List[List[STBox]]]]:
        dt = timedelta_to_interval(duration) if isinstance(duration, timedelta) \
            else pg_interval_in(duration, -1) if isinstance(duration, str) \
            else None
        st = datetime_to_timestamptz(start) if isinstance(start, datetime) \
            else pg_timestamptz_in(start, -1) if isinstance(start, str) \
            else datetime_to_timestamptz(self.tmin)
        gs = geometry_to_gserialized(origin) if origin is not None \
            else gserialized_in('POINT(0 0)', -1)
        tiles, dimensions = stbox_tile_list(self._inner, size, dt, gs, st)
        x_size = dimensions[0] if self.has_xy else 1
        y_size = dimensions[1] if self.has_xy else 1
        z_size = dimensions[2] if self.has_z else 1
        t_size = dimensions[3] if self.has_t else 1
        x_factor = y_size * z_size * t_size
        y_factor = z_size * t_size
        z_factor = t_size
        return [[[[STBox(_inner=tiles + x * x_factor + y * y_factor + z * z_factor + t) for t in range(t_size)]
                  for z in range(z_size)] for y in range(y_size)] for x in range(x_size)]

    def tile_flat(self, size: float, duration: Optional[Union[timedelta, str]] = None,
                  origin: Optional[Union[BaseGeometry, Geometry]] = None,
                  start: Union[datetime, str, None] = None) -> List[STBox]:
        boxes = self.tile(size, duration, origin, start)
        return [b
                for x in boxes
                for y in x
                for z in y
                for b in z
                ]

    def to_geometry(self, precision: int = 5) -> BaseGeometry:
        return gserialized_to_shapely_geometry(stbox_to_geo(self._inner), precision)

    def to_period(self) -> Period:
        return Period(_inner=stbox_to_period(self._inner))

    @property
    def has_xy(self):
        return stbox_hasx(self._inner)

    @property
    def has_z(self):
        return stbox_hasz(self._inner)

    @property
    def has_t(self):
        return stbox_hast(self._inner)

    @property
    def geodetic(self):
        """
        Is the box is geodetic?
        """
        return stbox_isgeodetic(self._inner)

    @property
    def xmin(self):
        """
        Minimum X
        """
        return stbox_xmin(self._inner)

    @property
    def ymin(self):
        """
        Minimum Y
        """
        return stbox_ymin(self._inner)

    @property
    def zmin(self):
        """
        Minimum Z
        """
        return stbox_zmin(self._inner)

    @property
    def tmin(self):
        """
        Minimum T
        """
        return timestamptz_to_datetime(stbox_tmin(self._inner))

    @property
    def xmax(self):
        """
        Maximum X
        """
        return stbox_xmax(self._inner)

    @property
    def ymax(self):
        """
        Maximum Y
        """
        return stbox_ymax(self._inner)

    @property
    def zmax(self):
        """
        Maximum Z
        """
        return stbox_zmax(self._inner)

    @property
    def tmax(self):
        """
        Maximum T
        """
        return timestamptz_to_datetime(stbox_tmax(self._inner))

    @property
    def srid(self):
        """
        SRID of the geographic coordinates
        """
        return self._inner.srid

    def set_srid(self, value: int) -> STBox:
        return STBox(_inner=stbox_set_srid(self._inner, value))

    def expand(self, other: Union[STBox, float, timedelta]) -> STBox:
        if isinstance(other, STBox):
            result = stbox_copy(self._inner)
            stbox_expand(other._inner, result)
        elif isinstance(other, float):
            result = stbox_expand_spatial(self._inner, other)
        elif isinstance(other, timedelta):
            result = stbox_expand_temporal(self._inner, timedelta_to_interval(other))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return STBox(_inner=result)

    def shift_tscale(self, shift_delta: Optional[timedelta] = None, scale_delta: Optional[timedelta] = None):
        """
        Shift the spatio-temporal box by a time interval
        """
        assert shift_delta is not None or scale_delta is not None, 'shift and scale deltas must not be both None'
        stbox_shift_tscale(
            timedelta_to_interval(shift_delta) if shift_delta else None,
            timedelta_to_interval(scale_delta) if scale_delta else None,
            self._inner
        )

    def union(self, other: STBox, strict: bool = True) -> STBox:
        return STBox(_inner=union_stbox_stbox(self._inner, other._inner, strict))

    # TODO: Check returning None for empty intersection is the desired behaviour
    def intersection(self, other: STBox) -> Optional[STBox]:
        result = intersection_stbox_stbox(self._inner, other._inner)
        return STBox(_inner=result) if result else None

    def is_adjacent(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return adjacent_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return adjacent_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_contained_in(self, container: Union[STBox, TPoint]) -> bool:
        if isinstance(container, STBox):
            return contained_stbox_stbox(self._inner, container._inner)
        elif isinstance(container, TPoint):
            return contained_stbox_tpoint(self._inner, container._inner)
        else:
            raise TypeError(f'Operation not supported with type {container.__class__}')

    def contains(self, content: Union[STBox, TPoint]) -> bool:
        if isinstance(content, STBox):
            return contains_stbox_stbox(self._inner, content._inner)
        elif isinstance(content, TPoint):
            return contains_stbox_tpoint(self._inner, content._inner)
        else:
            raise TypeError(f'Operation not supported with type {content.__class__}')

    def overlaps(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overlaps_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overlaps_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return same_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return same_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_left(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return left_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return left_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_left(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overleft_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overleft_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_right(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return right_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return right_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_right(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overright_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overright_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_below(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return below_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return below_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_below(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overbelow_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overbelow_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_above(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return above_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return above_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_above(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overabove_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overabove_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_front(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return front_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return front_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_front(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overfront_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overfront_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_back(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return back_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return back_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_back(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overback_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overback_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return before_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return before_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overbefore_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overbefore_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return after_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return after_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[STBox, TPoint]) -> bool:
        if isinstance(other, STBox):
            return overafter_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overafter_stbox_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def nearest_approach_distance(self, other: Union[Geometry, STBox]) -> float:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return nad_stbox_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_stbox_stbox(self._inner, other._inner)
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
            return stbox_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return stbox_ne(self._inner, other._inner)
        return True

    def __cmp__(self, other):
        if isinstance(other, self.__class__):
            return stbox_cmp(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return stbox_lt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return stbox_le(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return stbox_gt(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return stbox_ge(self._inner, other._inner)
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def __copy__(self) -> STBox:
        inner_copy = stbox_copy(self._inner)
        return STBox(_inner=inner_copy)

    def __str__(self):
        return stbox_out(self._inner, 6)

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self})')

    def plot_xy(self, *args, **kwargs):
        from ..plotters import BoxPlotter
        return BoxPlotter.plot_stbox_xy(self, *args, **kwargs)

    def plot_xt(self, *args, **kwargs):
        from ..plotters import BoxPlotter
        return BoxPlotter.plot_stbox_xt(self, *args, **kwargs)

    def plot_yt(self, *args, **kwargs):
        from ..plotters import BoxPlotter
        return BoxPlotter.plot_stbox_yt(self, *args, **kwargs)

    @staticmethod
    def read_from_cursor(value, _):
        if not value:
            return None
        return STBox(string=value)
