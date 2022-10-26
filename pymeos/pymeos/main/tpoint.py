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

from abc import ABC
from ctypes import Union
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, Set, Tuple

from dateutil.parser import parse
from geopandas import GeoDataFrame
# from movingpandas import Trajectory
from postgis import Point, Geometry
from pymeos_cffi import tpointseq_make_coords, pg_timestamptz_in, gserialized_as_geojson, tpoint_trajectory, \
    tpoint_as_ewkt, tpoint_at_values, tpoint_at_stbox, adjacent_tpoint_geo, adjacent_tpoint_stbox, \
    adjacent_tpoint_tpoint, teq_tgeompoint_point, tpoint_azimuth, tpoint_cumulative_length, tpoint_get_coord, \
    tpoint_set_srid, tpoint_make_simple, tdwithin_tpoint_geo, tdwithin_tpoint_tpoint, tintersects_tpoint_geo, \
    ttouches_tpoint_geo, tcontains_geo_tpoint, tdisjoint_tpoint_geo
from pymeos_cffi.functions import tgeogpoint_in, tgeompoint_in, tpoint_start_value, tpoint_end_value, \
    tpoint_values, tpoint_length, tpoint_speed, tpoint_srid, tpoint_value_at_timestamp, datetime_to_timestamptz, \
    temporal_simplify, \
    tpoint_at_geometry, tpoint_minus_geometry, gserialized_in, tpoint_out, tgeompoint_from_base, tgeompointinst_make, \
    tgeompointdiscseq_from_base_time, \
    tgeompointseq_from_base_time, tgeompointseqset_from_base_time, tgeogpoint_from_base, tgeogpointinst_make, \
    tgeogpointdiscseq_from_base_time, tgeogpointseq_from_base_time, tgeogpointseqset_from_base_time, \
    gserialized_to_shapely_geometry, tpoint_minus_values, tpoint_minus_stbox, contained_tpoint_geo, \
    contained_tpoint_stbox, contained_tpoint_tpoint, contains_tpoint_tpoint, contains_tpoint_stbox, contains_tpoint_geo, \
    overlaps_tpoint_geo, overlaps_tpoint_stbox, overlaps_tpoint_tpoint, same_tpoint_tpoint, same_tpoint_stbox, \
    same_tpoint_geo, distance_tpoint_geo, distance_tpoint_tpoint, nad_tpoint_geo, nad_tpoint_stbox, nad_tpoint_tpoint, \
    nai_tpoint_geo, nai_tpoint_tpoint, shortestline_tpoint_tpoint, shortestline_tpoint_geo, tpoint_twcentroid, \
    tgeompoint_always_eq, tgeompoint_ever_eq, tgeogpoint_always_eq, tgeogpoint_ever_eq, tne_tgeompoint_point, \
    teq_tgeogpoint_point, tne_tgeogpoint_point, bearing_tpoint_point, bearing_tpoint_tpoint, tpoint_is_simple, \
    tpoint_stboxes, overafter_tpoint_tpoint, left_tpoint_stbox, left_tpoint_tpoint, overleft_tpoint_stbox, \
    overleft_tpoint_tpoint, right_tpoint_stbox, right_tpoint_tpoint, overright_tpoint_stbox, overright_tpoint_tpoint, \
    below_tpoint_stbox, below_tpoint_tpoint, overbelow_tpoint_stbox, overbelow_tpoint_tpoint, above_tpoint_stbox, \
    above_tpoint_tpoint, overabove_tpoint_stbox, overabove_tpoint_tpoint, front_tpoint_stbox, front_tpoint_tpoint, \
    overfront_tpoint_stbox, overfront_tpoint_tpoint, back_tpoint_stbox, back_tpoint_tpoint, overback_tpoint_stbox, \
    overback_tpoint_tpoint, before_tpoint_stbox, before_tpoint_tpoint, overbefore_tpoint_stbox, \
    overbefore_tpoint_tpoint, after_tpoint_stbox, after_tpoint_tpoint, overafter_tpoint_stbox, left_tpoint_geo, \
    overleft_tpoint_geo, right_tpoint_geo, overright_tpoint_geo, below_tpoint_geo, overbelow_tpoint_geo, \
    above_tpoint_geo, overabove_tpoint_geo, front_tpoint_geo, overfront_tpoint_geo, back_tpoint_geo, \
    overback_tpoint_geo, tgeompoint_tgeogpoint, contains_geo_tpoint, disjoint_tpoint_geo, disjoint_tpoint_tpoint, \
    dwithin_tpoint_geo, dwithin_tpoint_tpoint, intersects_tpoint_geo, intersects_tpoint_tpoint, touches_tpoint_geo
from shapely.geometry.base import BaseGeometry

from .tfloat import TFloatSeqSet
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation
from ..time import TimestampSet, Period, PeriodSet

if TYPE_CHECKING:
    from ..boxes import STBox


# Add method to Point to make the class hashable
def __hash__(self):
    return hash(self.values())


setattr(Point, '__hash__', __hash__)


class TPoint(Temporal, ABC):

    @property
    def srid(self):
        """
        Returns the SRID.
        """
        return tpoint_srid(self._inner)

    def set_srid(self, srid: int) -> TPoint:
        return self.__class__(_inner=tpoint_set_srid(self._inner, srid))

    @property
    def start_value(self, precision: int = 6) -> BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_start_value(self._inner), precision)

    @property
    def end_value(self, precision: int = 6) -> BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_end_value(self._inner), precision)

    @property
    def value_set(self, precision: int = 6) -> Set[BaseGeometry]:
        values, count = tpoint_values(self._inner)
        return {gserialized_to_shapely_geometry(values[i], precision) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime, precision: int = 6) -> BaseGeometry:
        """
        Value at timestamp.
        """
        return gserialized_to_shapely_geometry(
            tpoint_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)[0], precision)

    def simplify(self, tolerance: float, synchronized: bool = False) -> TPoint:
        return self.__class__(_inner=temporal_simplify(self._inner, tolerance, synchronized))

    def length(self) -> float:
        return tpoint_length(self._inner)

    def cumulative_length(self) -> Temporal:
        result = tpoint_cumulative_length(self._inner)
        return Temporal._factory(result)

    def speed(self) -> Temporal:
        result = tpoint_speed(self._inner)
        return Temporal._factory(result)

    def x(self):
        result = tpoint_get_coord(self._inner, 0)
        return Temporal._factory(result)

    def y(self):
        result = tpoint_get_coord(self._inner, 1)
        return Temporal._factory(result)

    def z(self):
        result = tpoint_get_coord(self._inner, 2)
        return Temporal._factory(result)

    def stboxes(self) -> List[STBox]:
        from ..boxes import STBox
        result, count = tpoint_stboxes(self._inner)
        return [STBox(_inner=result + i) for i in range(count)]

    def is_simple(self) -> bool:
        return tpoint_is_simple(self._inner)

    def make_simple(self) -> List[TPoint]:
        result, count = tpoint_make_simple(self._inner)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(result[i]) for i in range(count)]

    def is_adjacent(self, other: Union[Geometry, STBox, TPoint,
                                       Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return adjacent_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return adjacent_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return adjacent_tpoint_tpoint(self._inner, other._inner)
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[Geometry, STBox, TPoint,
                                               Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        from ..boxes import STBox
        if isinstance(container, Geometry):
            gs = gserialized_in(container.to_ewkb(), -1)
            return contained_tpoint_geo(self._inner, gs)
        elif isinstance(container, STBox):
            return contained_tpoint_stbox(self._inner, container._inner)
        elif isinstance(container, TPoint):
            return contained_tpoint_tpoint(self._inner, container._inner)
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[Geometry, STBox, TPoint,
                                      Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        from ..boxes import STBox
        if isinstance(content, Geometry):
            gs = gserialized_in(content.to_ewkb(), -1)
            return contains_tpoint_geo(self._inner, gs)
        elif isinstance(content, STBox):
            return contains_tpoint_stbox(self._inner, content._inner)
        elif isinstance(content, TPoint):
            return contains_tpoint_tpoint(self._inner, content._inner)
        else:
            return super().contains(content)

    def overlaps(self, other: Union[Geometry, STBox, TPoint,
                                    Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overlaps_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overlaps_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overlaps_tpoint_tpoint(self._inner, other._inner)
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[Geometry, STBox, TPoint,
                                   Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return same_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return same_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return same_tpoint_tpoint(self._inner, other._inner)
        else:
            return super().is_same(other)

    def is_left(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return left_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return left_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return left_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_left(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overleft_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overleft_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overleft_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_right(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return right_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return right_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return right_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_right(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overright_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overright_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overright_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_below(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return below_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return below_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return below_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_below(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overbelow_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overbelow_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overbelow_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_above(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return above_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return above_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return above_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_above(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overabove_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overabove_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overabove_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_front(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return front_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return front_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return front_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_front(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overfront_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overfront_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overfront_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_back(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return back_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return back_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return back_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_back(self, other: Union[Geometry, STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return overback_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return overback_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overback_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_before(self, other: Union[STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, STBox):
            return before_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return before_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, STBox):
            return overbefore_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overbefore_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, STBox):
            return after_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return after_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[STBox, TPoint]) -> bool:
        from ..boxes import STBox
        if isinstance(other, STBox):
            return overafter_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return overafter_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def at(self, other: Union[Geometry, List[Geometry], STBox, datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tpoint_at_geometry(self._inner, gs)
        elif isinstance(other, list):
            gss = [gserialized_in(gm.to_ewkb(), -1) for gm in other]
            result = tpoint_at_values(self._inner, gss)
        elif isinstance(other, STBox):
            result = tpoint_at_stbox(self._inner, other._inner)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[Geometry, List[Geometry], STBox,
                                 datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tpoint_minus_geometry(self._inner, gs)
        elif isinstance(other, list):
            gss = [gserialized_in(gm.to_ewkb(), -1) for gm in other]
            result = tpoint_minus_values(self._inner, gss)
        elif isinstance(other, STBox):
            result = tpoint_minus_stbox(self._inner, other._inner)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def within_distance(self, other: Union[Geometry, TPoint], distance: float) -> Temporal:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tdwithin_tpoint_geo(self._inner, gs, distance, False, False)
        elif isinstance(other, TPoint):
            result = tdwithin_tpoint_tpoint(self._inner, other._inner, distance, False, False)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def intersects(self, other: Geometry) -> Temporal:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = tintersects_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def touches(self, other: Geometry) -> Temporal:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = ttouches_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def is_contained(self, container: Geometry) -> Temporal:
        gs = gserialized_in(container.to_ewkb(), -1)
        result = tcontains_geo_tpoint(gs, self._inner, False, False)
        return Temporal._factory(result)

    def disjoint(self, other: Geometry) -> Temporal:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = tdisjoint_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def is_ever_contained(self, container: Geometry) -> bool:
        gs = gserialized_in(container.to_ewkb(), -1)
        return contains_geo_tpoint(gs, self._inner) == 1

    def is_ever_disjoint(self, other: Union[Geometry, TPoint]) -> bool:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = disjoint_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = disjoint_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def is_ever_within_distance(self, other: Union[Geometry, TPoint], distance: float) -> bool:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = dwithin_tpoint_geo(self._inner, gs, distance)
        elif isinstance(other, TPoint):
            result = dwithin_tpoint_tpoint(self._inner, other._inner, distance)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def ever_intersects(self, other: Union[Geometry, TPoint]) -> bool:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = intersects_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = intersects_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def ever_touches(self, other: Geometry) -> bool:
        gs = gserialized_in(other.to_ewkb(), -1)
        return touches_tpoint_geo(gs, self._inner) == 1

    def distance(self, other: Union[Geometry, TPoint]) -> TPoint:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = distance_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = distance_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def nearest_approach_distance(self, other: Union[Geometry, STBox, TPoint]) -> float:
        from ..boxes import STBox
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return nad_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def nearest_approach_instant(self, other: Union[Geometry, TPoint]) -> TPoint:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = nai_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = nai_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def shortest_line(self, other: Union[Geometry, TPoint]) -> BaseGeometry:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = shortestline_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = shortestline_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return gserialized_to_shapely_geometry(result[0], 10)

    def bearing(self, other: Union[Geometry, TPoint]) -> Temporal:
        if isinstance(other, Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = bearing_tpoint_point(self._inner, gs, False)
        elif isinstance(other, TPoint):
            result = bearing_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def azimuth(self) -> Temporal:
        result = tpoint_azimuth(self._inner)
        return Temporal._factory(result)

    def time_weighted_centroid(self) -> BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_twcentroid(self._inner), 10)

    def as_geojson(self, option: int = 1, precision: int = 6, srs: Optional[str] = None) -> str:
        return gserialized_as_geojson(tpoint_trajectory(self._inner), option, precision, srs)

    def to_shapely_geometry(self, precision: int = 6) -> BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_trajectory(self._inner), precision)

    def to_dataframe(self) -> GeoDataFrame:
        data = {
            'time': self.timestamps,
            'geometry': [i.value for i in self.instants]
        }
        return GeoDataFrame(data, crs=self.srid).set_index(keys=['time'])

    def __str__(self):
        return tpoint_out(self._inner, 5)

    def as_wkt(self, precision: int = 6):
        return tpoint_out(self._inner, precision)

    def as_ewkt(self, precision: int = 6):
        return tpoint_as_ewkt(self._inner, precision)


class TPointInst(TPoint, TInstant, ABC):
    """
    Abstract class for representing temporal points of instant subtype.
    """
    pass


class TPointSeq(TPoint, TSequence, ABC):
    """
    Abstract class for representing temporal points of sequence subtype.
    """

    @staticmethod
    def from_arrays(t: List[Union[datetime, str]], x: List[float], y: List[float], z: Optional[List[float]] = None,
                    srid: int = 0, geodetic: bool = False, lower_inc: bool = True, upper_inc: bool = False,
                    interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True) -> TPointSeq:
        from ..factory import _TemporalFactory
        assert len(t) == len(x) == len(y)
        times = [datetime_to_timestamptz(ti) if isinstance(ti, datetime) else pg_timestamptz_in(ti, -1) for ti in t]
        return _TemporalFactory.create_temporal(
            tpointseq_make_coords(x, y, z, times, len(t), srid, geodetic, lower_inc, upper_inc, interpolation,
                                  normalize)
        )

    def plot(self, *args, **kwargs):
        from ..plotters import TemporalPointSequencePlotter
        return TemporalPointSequencePlotter.plot_xy(self, *args, **kwargs)


class TPointSeqSet(TPoint, TSequenceSet, ABC):
    """
    Abstract class for representing temporal points of sequence set subtype.
    """

    @property
    def speed(self):
        return TFloatSeqSet(_inner=tpoint_speed(self._inner))

    def to_dataframe(self) -> GeoDataFrame:
        data = {
            'sequence': [i + 1 for i, seq in enumerate(self.sequences) for _ in range(seq.instants)],
            'time': [t for seq in self.sequences for t in seq.timestamps],
            'geometry': [v for seq in self.sequences for v in seq.values]
        }
        return GeoDataFrame(data, crs=self.srid).set_index(keys=['sequence', 'time'])

    def plot(self, *args, **kwargs):
        from ..plotters import TemporalPointSequenceSetPlotter
        return TemporalPointSequenceSetPlotter.plot_xy(self, *args, **kwargs)


class TGeomPoint(TPoint, ABC):
    """
    Abstract class for representing temporal geometric or geographic points of any subtype.
    """

    BaseClass = Point
    BaseClassDiscrete = False
    _parse_function = tgeompoint_in

    @staticmethod
    def from_base(value: Geometry, base: Temporal, interpolation: TInterpolation = TInterpolation.LINEAR) -> TGeomPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        result = tgeompoint_from_base(gs, base._inner, interpolation)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: Geometry, base: Union[datetime, TimestampSet, Period, PeriodSet],
                       interpolation: TInterpolation = None) -> TGeomPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        if isinstance(base, datetime):
            return TGeomPointInst(_inner=tgeompointinst_make(gs, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TGeomPointSeq(_inner=tgeompointdiscseq_from_base_time(gs, base._inner))
        elif isinstance(base, Period):
            return TGeomPointSeq(_inner=tgeompointseq_from_base_time(gs, base._inner, interpolation))
        elif isinstance(base, PeriodSet):
            return TGeomPointSeqSet(_inner=tgeompointseqset_from_base_time(gs, base._inner, interpolation))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    def to_geographic(self) -> TGeogPoint:
        result = tgeompoint_tgeogpoint(self._inner, True)
        return Temporal._factory(result)

    def always_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_always_eq(self._inner, gs)

    def always_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_ever_eq(self._inner, gs)

    def ever_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_ever_eq(self._inner, gs)

    def ever_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_always_eq(self._inner, gs)

    def never_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_ever_eq(self._inner, gs)

    def never_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_always_eq(self._inner, gs)

    def temporal_equal(self, other: Union[Point, Temporal]) -> Temporal:
        if isinstance(other, Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = teq_tgeompoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[Point, Temporal]) -> Temporal:
        if isinstance(other, Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tne_tgeompoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value.startswith('Interp=Stepwise;'):
            value1 = value.replace('Interp=Stepwise;', '')
            if value1[0] == '{':
                return TGeomPointSeqSet(string=value)
            else:
                return TGeomPointSeq(string=value)
        elif value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TGeomPointInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TGeomPointSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TGeomPointSeqSet(string=value)
            else:
                return TGeomPointSeq(string=value)
        raise Exception("ERROR: Could not parse temporal point value")

    @property
    def hasz(self):
        """
        Does the temporal point has Z dimension?
        """
        return self.start_value.z is not None


class TGeogPoint(TPoint, ABC):
    """
    Abstract class for representing temporal geographic points of any subtype.
    """

    BaseClass = Point
    BaseClassDiscrete = False
    _parse_function = tgeogpoint_in

    @staticmethod
    def from_base(value: Geometry, base: Temporal, interpolation: TInterpolation = TInterpolation.LINEAR) -> TGeogPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        result = tgeogpoint_from_base(gs, base._inner, interpolation)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: Geometry, base: Union[datetime, TimestampSet, Period, PeriodSet],
                       interpolation: TInterpolation = None) -> TGeogPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        if isinstance(base, datetime):
            return TGeogPointInst(_inner=tgeogpointinst_make(gs, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TGeogPointSeq(_inner=tgeogpointdiscseq_from_base_time(gs, base._inner))
        elif isinstance(base, Period):
            return TGeogPointSeq(_inner=tgeogpointseq_from_base_time(gs, base._inner, interpolation))
        elif isinstance(base, PeriodSet):
            return TGeogPointSeqSet(_inner=tgeogpointseqset_from_base_time(gs, base._inner, interpolation))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    def to_geometric(self) -> TGeogPoint:
        result = tgeompoint_tgeogpoint(self._inner, False)
        return Temporal._factory(result)

    def always_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_always_eq(self._inner, gs)

    def always_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_ever_eq(self._inner, gs)

    def ever_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_ever_eq(self._inner, gs)

    def ever_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_always_eq(self._inner, gs)

    def never_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_ever_eq(self._inner, gs)

    def never_not_equal(self, value: Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_always_eq(self._inner, gs)

    def temporal_equal(self, other: Union[Point, Temporal]) -> Temporal:
        if isinstance(other, Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = teq_tgeogpoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[Point, Temporal]) -> Temporal:
        if isinstance(other, Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tne_tgeogpoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value.startswith('Interp=Stepwise;'):
            value1 = value.replace('Interp=Stepwise;', '')
            if value1[0] == '{':
                return TGeogPointSeqSet(string=value)
            else:
                return TGeogPointSeq(string=value)
        elif value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TGeogPointInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TGeogPointSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TGeogPointSeqSet(string=value)
            else:
                return TGeogPointSeq(string=value)
        raise Exception("ERROR: Could not parse temporal point value")

    @property
    def hasz(self):
        """
        Does the temporal point has Z dimension?
        """
        return self.start_value.z is not None


class TGeomPointInst(TPointInst, TGeomPoint):
    """
    Class for representing temporal geometric points of instant subtype.

    ``TGeomPointInst`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TGeomPointInst('Point(10.0 10.0)@2019-09-01')
        >>> TGeomPointInst('SRID=4326,Point(10.0 10.0)@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``Point`` or ``datetime``.
    Additionally, the SRID can be specified, it will be 0 by default if not
    given.

        >>> TGeomPointInst('Point(10.0 10.0)', '2019-09-08 00:00:00+01', 4326)
        >>> TGeomPointInst(['Point(10.0 10.0)', '2019-09-08 00:00:00+01', 4326])
        >>> TGeomPointInst(Point(10.0, 10.0), parse('2019-09-08 00:00:00+01'), 4326)
        >>> TGeomPointInst([Point(10.0, 10.0), parse('2019-09-08 00:00:00+01'), 4326])

    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(self, string: Optional[str] = None, *, point: Optional[Union[str, Point]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, srid: Optional[int] = 0, _inner=None) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            self._inner = tgeompoint_in(f"SRID={srid};{point}@{timestamp}")


# noinspection PyTypeChecker
class TGeogPointInst(TPointInst, TGeogPoint):
    """
    Class for representing temporal geographic points of instant subtype.

    ``TGeogPointInst`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TGeogPointInst(string='Point(10.0 10.0)@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``Point`` or ``datetime``.
    Additionally, the SRID can be specified, it will be 0 by default if not
    given.

        >>> TGeogPointInst(point='Point(10.0 10.0)',timestamp='2019-09-08 00:00:00+01')
        >>> TGeogPointInst(point=Point(10.0, 10.0),timestamp=parse('2019-09-08 00:00:00+01'))

    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(self, string: Optional[str] = None, *, point: Optional[Union[str, Point, Tuple[float, float]]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, srid: Optional[int] = 0, _inner=None) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            p = f'POINT({point[0]} {point[1]})' if isinstance(point, tuple) else f'{point}'
            self._inner = tgeogpoint_in(f"SRID={srid};{p}@{timestamp}")


class TGeomPointSeq(TPointSeq, TGeomPoint):
    """
    Class for representing temporal geometric points of sequence subtype.

    ``TGeomPointSeq`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TGeomPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')
        >>> TGeomPointSeq('Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances
      of ``str`` or ``TGeogPointInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not,  where by default '`lower_inc``
      is ``True`` and ``upper_inc`` is ``False``,
    * ``interp`` which is either ``'Linear'`` or ``'Stepwise'``, the former
      being the default

    Some pymeos_examples are shown next.

        >>> TGeomPointSeq(['Point(10.0 10.0)@2019-09-01 00:00:00+01', 'Point(20.0 20.0)@2019-09-02 00:00:00+01', 'Point(10.0 10.0)@2019-09-03 00:00:00+01'])
        >>> TGeomPointSeq([TGeomPointInst('Point(10.0 10.0)@2019-09-01 00:00:00+01'), TGeomPointInst('Point(20.0 20.0)@2019-09-02 00:00:00+01'), TGeomPointInst('Point(10.0 10.0)@2019-09-03 00:00:00+01')])
        >>> TGeomPointSeq(['Point(10.0 10.0)@2019-09-01 00:00:00+01', 'Point(20.0 20.0)@2019-09-02 00:00:00+01', 'Point(10.0 10.0)@2019-09-03 00:00:00+01'], True, True, 'Stepwise')
        >>> TGeomPointSeq([TGeomPointInst('Point(10.0 10.0)@2019-09-01 00:00:00+01'), TGeomPointInst('Point(20.0 20.0)@2019-09-02 00:00:00+01'), TGeomPointInst('Point(10.0 10.0)@2019-09-03 00:00:00+01')], True, True, 'Stepwise')

    """

    ComponentClass = TGeomPointInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TGeomPointInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, interpolation: TInterpolation = TInterpolation.LINEAR,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TGeogPointSeq(TPointSeq, TGeogPoint):
    """
    Class for representing temporal geographic points of sequence subtype.

    ``TGeogPointSeq`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TGeogPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')
        >>> TGeogPointSeq('Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01, Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances
      of ``str`` or ``TGeogPointInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are includive or not,  where by default '`lower_inc``
      is ``True`` and ``upper_inc`` is ``False``, and
    * ``interp`` which is either ``'Linear'``, ``'Stepwise'`` or ``'Discrete'``, the first
      being the default.
    * ``srid`` is an integer specifiying the SRID

    Some pymeos_examples are shown next.

        >>> TGeogPointSeq(['Point(10.0 10.0)@2019-09-01 00:00:00+01', 'Point(20.0 20.0)@2019-09-02 00:00:00+01', 'Point(10.0 10.0)@2019-09-03 00:00:00+01'])
        >>> TGeogPointSeq([TGeogPointInst(string='Point(10.0 10.0)@2019-09-01 00:00:00+01'), TGeogPointInst(string='Point(20.0 20.0)@2019-09-02 00:00:00+01'), TGeogPointInst(string='Point(10.0 10.0)@2019-09-03 00:00:00+01')])
        >>> TGeogPointSeq(['Point(10.0 10.0)@2019-09-01 00:00:00+01', 'Point(20.0 20.0)@2019-09-02 00:00:00+01', 'Point(10.0 10.0)@2019-09-03 00:00:00+01'], True, True, 'Stepwise')
        >>> TGeogPointSeq([TGeogPointInst(string='Point(10.0 10.0)@2019-09-01 00:00:00+01'), TGeogPointInst(string='Point(20.0 20.0)@2019-09-02 00:00:00+01'), TGeogPointInst(string='Point(10.0 10.0)@2019-09-03 00:00:00+01')], True, True, 'Stepwise')

    """

    ComponentClass = TGeogPointInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TGeogPointInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TGeomPointSeqSet(TPointSeqSet, TGeomPoint):
    """
    Class for representing temporal geometric points of sequence subtype.

    ``TGeomPointSeqSet`` objects can be created with a single argument of type
    string as in MobilityDB.

        >>> TGeomPointSeqSet('{[Point(10.0 10.0)@2019-09-01 00:00:00+01], [Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]}')
        >>> TGeomPointSeqSet('Interp=Stepwise;{[Point(10.0 10.0)@2019-09-01 00:00:00+01], [Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]}')

    Another possibility is to give the arguments as follows:

    * ``sequenceList`` is the list of composing sequences, which can be instances
      of ``str`` or ``TGeomPointSeq``,
    * ``interp`` can be ``'Linear'``, ``'Stepwise'`` or ``'Discrete'``, the first being
      the default, and
    * ``srid`` is an integer specifiying the SRID, if will be 0 by default if
      not given.

    Some pymeos_examples are shown next.

        >>> TGeomPointSeqSet(['[Point(10.0 10.0)@2019-09-01 00:00:00+01]', '[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'])
        >>> TGeomPointSeqSet(['[Point(10.0 10.0)@2019-09-01 00:00:00+01]', '[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'], 'Linear')
        >>> TGeomPointSeqSet(['Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01]', 'Interp=Stepwise;[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'], 'Stepwise')
        >>> TGeomPointSeqSet([TGeomPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01]'), TGeomPointSeq('[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')])
        >>> TGeomPointSeqSet([TGeomPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01]'),  TGeomPointSeq('[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')], 'Linear')
        >>> TGeomPointSeqSet([TGeomPointSeq('Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01]'), TGeomPointSeq('Interp=Stepwise;[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')], 'Stepwise')

    """

    ComponentClass = TGeomPointSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TGeomPointSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)


class TGeogPointSeqSet(TPointSeqSet, TGeogPoint):
    """
    Class for representing temporal geographic points of sequence subtype.

    ``TGeogPointSeqSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TGeogPointSeqSet('{[Point(10.0 10.0)@2019-09-01 00:00:00+01], [Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]}')
        >>> TGeogPointSeqSet('Interp=Stepwise;{[Point(10.0 10.0)@2019-09-01 00:00:00+01], [Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]}')

    Another possibility is to give the arguments as follows:

    * ``sequenceList`` is the list of composing sequences, which can be instances
      of ``str`` or ``TGeogPointSeq``,
    * ``interp`` can be ``'Linear'`` or ``'Stepwise'``, the former being
      the default, and
    * ``srid`` is an integer specifiying the SRID, if will be 0 by default if
      not given.

    Some pymeos_examples are shown next.

        >>> TGeogPointSeqSet(['[Point(10.0 10.0)@2019-09-01 00:00:00+01]', '[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'])
        >>> TGeogPointSeqSet(['[Point(10.0 10.0)@2019-09-01 00:00:00+01]', '[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'], 'Linear')
        >>> TGeogPointSeqSet(['Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01]', 'Interp=Stepwise;[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]'], 'Stepwise')
        >>> TGeogPointSeqSet([TGeogPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01]'), TGeogPointSeq('[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')])
        >>> TGeogPointSeqSet([TGeogPointSeq('[Point(10.0 10.0)@2019-09-01 00:00:00+01]'),  TGeogPointSeq('[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')], 'Linear')
        >>> TGeogPointSeqSet([TGeogPointSeq('Interp=Stepwise;[Point(10.0 10.0)@2019-09-01 00:00:00+01]'), TGeogPointSeq('Interp=Stepwise;[Point(20.0 20.0)@2019-09-02 00:00:00+01, Point(10.0 10.0)@2019-09-03 00:00:00+01]')], 'Stepwise')

    """

    ComponentClass = TGeogPointSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TGeogPointSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
