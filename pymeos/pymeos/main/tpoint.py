from __future__ import annotations

from abc import ABC
from functools import reduce, cache
from typing import Optional, List, TYPE_CHECKING, Set, Tuple, Union, TypeVar

import postgis as pg
import shapely.geometry as shp
import shapely.geometry.base as shpb
from geopandas import GeoDataFrame
from pymeos_cffi import *

from .tbool import TBool
from .tfloat import TFloatSeqSet, TFloat
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation
from ..time import *

if TYPE_CHECKING:
    from ..boxes import STBox

TG = TypeVar('TG', bound='TPoint')
TI = TypeVar('TI', bound='TPointInst')
TS = TypeVar('TS', bound='TPointSeq')
TSS = TypeVar('TSS', bound='TPointSeqSet')
Self = TypeVar('Self', bound='TPoint')


class TPoint(Temporal[shp.Point, TG, TI, TS, TSS], ABC):

    def __init__(self, _inner) -> None:
        super().__init__()

    def srid(self):
        """
        Returns the SRID.
        """
        return tpoint_srid(self._inner)

    def set_srid(self: Self, srid: int) -> Self:
        return self.__class__(_inner=tpoint_set_srid(self._inner, srid))

    @cache
    def bounding_box(self) -> STBox:
        from ..boxes import STBox
        return STBox(_inner=tpoint_to_stbox(self._inner))

    def values(self, precision: int = 15) -> List[shp.Point]:
        return [i.value(precision=precision) for i in self.instants()]

    def start_value(self, precision: int = 15) -> shp.Point:
        return gserialized_to_shapely_point(tpoint_start_value(self._inner), precision)

    def end_value(self, precision: int = 15) -> shp.Point:
        return gserialized_to_shapely_point(tpoint_end_value(self._inner), precision)

    def value_set(self, precision: int = 15) -> Set[shp.Point]:
        values, count = tpoint_values(self._inner)
        return {gserialized_to_shapely_point(values[i], precision) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime, precision: int = 15) -> shp.Point:
        """
        Value at timestamp.
        """
        return gserialized_to_shapely_point(
            tpoint_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)[0], precision)

    def simplify_min_dist(self: Self, tolerance: float) -> Self:
        return self.__class__(_inner=temporal_simplify_min_dist(self._inner, tolerance))

    def simplify_min_time_delta(self: Self, tolerance: float) -> Self:
        return self.__class__(_inner=temporal_simplify_min_tdelta(self._inner, tolerance))

    def simplify_douglas_peucker(self: Self, tolerance: float, synchronized: bool = False) -> Self:
        return self.__class__(_inner=temporal_simplify_dp(self._inner, tolerance, synchronized))

    def simplify_max_dist(self: Self, tolerance: float, synchronized: bool = False) -> Self:
        return self.__class__(_inner=temporal_simplify_max_dist(self._inner, tolerance, synchronized))

    def length(self) -> float:
        return tpoint_length(self._inner)

    def cumulative_length(self) -> TFloat:
        result = tpoint_cumulative_length(self._inner)
        return Temporal._factory(result)

    def speed(self) -> TFloat:
        result = tpoint_speed(self._inner)
        return Temporal._factory(result)

    def x(self) -> TFloat:
        result = tpoint_get_coord(self._inner, 0)
        return Temporal._factory(result)

    def y(self) -> TFloat:
        result = tpoint_get_coord(self._inner, 1)
        return Temporal._factory(result)

    def z(self) -> TFloat:
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

    def at(self, other: Union[pg.Geometry, List[pg.Geometry], shpb.BaseGeometry, List[shpb.BaseGeometry], STBox,
    datetime, TimestampSet, Period, PeriodSet]) -> TG:
        from ..boxes import STBox
        if isinstance(other, pg.Geometry) or isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tpoint_at_geometry(self._inner, gs)
        elif isinstance(other, list):
            gss = [geometry_to_gserialized(gm) for gm in other]
            results = [tpoint_at_geometry(self._inner, gs) for gs in gss]
            result = temporal_merge_array(results, len(results))
        elif isinstance(other, STBox):
            result = tpoint_at_stbox(self._inner, other._inner)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[pg.Geometry, List[pg.Geometry], shpb.BaseGeometry, List[shpb.BaseGeometry], STBox,
    datetime, TimestampSet, Period, PeriodSet]) -> TG:
        from ..boxes import STBox
        if isinstance(other, pg.Geometry) or isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tpoint_minus_geometry(self._inner, gs)
        elif isinstance(other, list):
            gss = [geometry_to_gserialized(gm) for gm in other]
            result = reduce(tpoint_minus_value, gss, self._inner)
        elif isinstance(other, STBox):
            result = tpoint_minus_stbox(self._inner, other._inner)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def within_distance(self, other: Union[pg.Geometry, shpb.BaseGeometry, TPoint], distance: float) -> TBool:
        if isinstance(other, pg.Geometry) or isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tdwithin_tpoint_geo(self._inner, gs, distance, False, False)
        elif isinstance(other, TPoint):
            result = tdwithin_tpoint_tpoint(self._inner, other._inner, distance, False, False)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def intersects(self, other: pg.Geometry) -> TBool:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = tintersects_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def touches(self, other: pg.Geometry) -> TBool:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = ttouches_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def is_contained(self, container: pg.Geometry) -> TBool:
        gs = gserialized_in(container.to_ewkb(), -1)
        result = tcontains_geo_tpoint(gs, self._inner, False, False)
        return Temporal._factory(result)

    def disjoint(self, other: pg.Geometry) -> TBool:
        gs = gserialized_in(other.to_ewkb(), -1)
        result = tdisjoint_tpoint_geo(self._inner, gs, False, False)
        return Temporal._factory(result)

    def is_ever_contained(self, container: pg.Geometry) -> bool:
        gs = gserialized_in(container.to_ewkb(), -1)
        return econtains_geo_tpoint(gs, self._inner) == 1

    def is_ever_disjoint(self, other: Union[pg.Geometry, TPoint]) -> bool:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = edisjoint_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = edisjoint_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def is_ever_within_distance(self, other: Union[pg.Geometry, TPoint], distance: float) -> bool:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = edwithin_tpoint_geo(self._inner, gs, distance)
        elif isinstance(other, TPoint):
            result = edwithin_tpoint_tpoint(self._inner, other._inner, distance)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def ever_intersects(self, other: Union[pg.Geometry, TPoint]) -> bool:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = eintersects_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = eintersects_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return result == 1

    def ever_touches(self, other: pg.Geometry) -> bool:
        gs = gserialized_in(other.to_ewkb(), -1)
        return etouches_tpoint_geo(gs, self._inner) == 1

    def distance(self, other: Union[pg.Geometry, TPoint]) -> TFloat:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = distance_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = distance_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def nearest_approach_distance(self, other: Union[pg.Geometry, STBox, TPoint]) -> float:
        from ..boxes import STBox
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            return nad_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def nearest_approach_instant(self, other: Union[pg.Geometry, TPoint]) -> TI:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = nai_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = nai_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def shortest_line(self, other: Union[pg.Geometry, TPoint]) -> shpb.BaseGeometry:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = shortestline_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = shortestline_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return gserialized_to_shapely_geometry(result[0], 10)

    def bearing(self, other: Union[pg.Geometry, TPoint]) -> TFloat:
        if isinstance(other, pg.Geometry):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = bearing_tpoint_point(self._inner, gs, False)
        elif isinstance(other, TPoint):
            result = bearing_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def azimuth(self) -> TFloatSeqSet:
        result = tpoint_azimuth(self._inner)
        return Temporal._factory(result)

    def time_weighted_centroid(self) -> shpb.BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_twcentroid(self._inner), 10)

    def tile(self, size: float, duration: Optional[Union[timedelta, str]] = None,
             origin: Optional[Union[shpb.BaseGeometry, pg.Geometry]] = None,
             start: Union[datetime, str, None] = None) -> List[List[List[List[TG]]]]:
        from ..boxes import STBox
        bbox = STBox.from_tpoint(self)
        tiles = bbox.tile(size, duration, origin, start)
        return [[[[self.at(tile) for tile in z_dim]
                  for z_dim in y_dim] for y_dim in x_dim] for x_dim in tiles]

    def tile_flat(self, size: float, duration: Optional[Union[timedelta, str]] = None,
                  origin: Optional[Union[shpb.BaseGeometry, pg.Geometry]] = None,
                  start: Union[datetime, str, None] = None) -> List[TG]:
        from ..boxes import STBox
        bbox = STBox.from_tpoint(self)
        tiles = bbox.tile_flat(size, duration, origin, start)
        return [x for x in (self.at(tile) for tile in tiles) if x]

    def as_geojson(self, option: int = 1, precision: int = 15, srs: Optional[str] = None) -> str:
        return gserialized_as_geojson(tpoint_trajectory(self._inner), option, precision, srs)

    def to_shapely_geometry(self, precision: int = 15) -> shpb.BaseGeometry:
        return gserialized_to_shapely_geometry(tpoint_trajectory(self._inner), precision)

    def to_dataframe(self) -> GeoDataFrame:
        data = {
            'time': self.timestamps,
            'geometry': [i.value() for i in self.instants()]
        }
        return GeoDataFrame(data, crs=self.srid).set_index(keys=['time'])

    def __str__(self):
        return tpoint_out(self._inner, 15)

    def as_wkt(self, precision: int = 15):
        return tpoint_out(self._inner, precision)

    def as_ewkt(self, precision: int = 15):
        return tpoint_as_ewkt(self._inner, precision)


class TPointInst(TInstant[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC):
    def value(self, precision: int = 15) -> shp.Point:
        return self.start_value(precision=precision)


class TPointSeq(TSequence[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC):

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


class TPointSeqSet(TSequenceSet[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC):

    def speed(self):
        return TFloatSeqSet(_inner=tpoint_speed(self._inner))

    def to_dataframe(self, precision: int = 15) -> GeoDataFrame:
        sequences = self.sequences()
        data = {
            'sequence': [i + 1 for i, seq in enumerate(sequences) for _ in range(seq.num_instants())],
            'time': [t for seq in sequences for t in seq.timestamps()],
            'geometry': [v for seq in sequences for v in seq.values(precision=precision)]
        }
        return GeoDataFrame(data, crs=self.srid).set_index(keys=['sequence', 'time'])

    def plot(self, *args, **kwargs):
        from ..plotters import TemporalPointSequenceSetPlotter
        return TemporalPointSequenceSetPlotter.plot_xy(self, *args, **kwargs)


class TGeomPoint(TPoint['TGeomPoint', 'TGeomPointInst', 'TGeomPointSeq', 'TGeomPointSeqSet'], ABC):
    BaseClass = pg.Point
    _parse_function = tgeompoint_in

    @staticmethod
    def from_base(value: pg.Geometry, base: Temporal,
                  interpolation: TInterpolation = TInterpolation.LINEAR) -> TGeomPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        result = tgeompoint_from_base(gs, base._inner, interpolation)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: pg.Geometry, base: Time, interpolation: TInterpolation = None) -> TGeomPoint:
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

    def always_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_always_eq(self._inner, gs)

    def always_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_ever_eq(self._inner, gs)

    def ever_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_ever_eq(self._inner, gs)

    def ever_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_always_eq(self._inner, gs)

    def never_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeompoint_ever_eq(self._inner, gs)

    def never_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeompoint_always_eq(self._inner, gs)

    def temporal_equal(self, other: Union[pg.Point, Temporal]) -> Temporal:
        if isinstance(other, pg.Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = teq_tgeompoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[pg.Point, Temporal]) -> Temporal:
        if isinstance(other, pg.Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tne_tgeompoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    @staticmethod
    def read_from_cursor(value, _=None):
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

    def hasz(self):
        """
        Does the temporal point has Z dimension?
        """
        return self.start_value().has_z


class TGeogPoint(TPoint['TGeogPoint', 'TGeogPointInst', 'TGeogPointSeq', 'TGeogPointSeqSet'], ABC):
    BaseClass = pg.Point
    _parse_function = tgeogpoint_in

    @staticmethod
    def from_base(value: pg.Geometry, base: Temporal,
                  interpolation: TInterpolation = TInterpolation.LINEAR) -> TGeogPoint:
        gs = gserialized_in(value.to_ewkb(), -1)
        result = tgeogpoint_from_base(gs, base._inner, interpolation)
        return Temporal._factory(result)

    @staticmethod
    def from_base_time(value: pg.Geometry, base: Time, interpolation: TInterpolation = None) -> TGeogPoint:
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

    def always_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_always_eq(self._inner, gs)

    def always_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_ever_eq(self._inner, gs)

    def ever_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_ever_eq(self._inner, gs)

    def ever_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_always_eq(self._inner, gs)

    def never_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return not tgeogpoint_ever_eq(self._inner, gs)

    def never_not_equal(self, value: pg.Geometry) -> bool:
        gs = gserialized_in(value.to_ewkb(), -1)
        return tgeogpoint_always_eq(self._inner, gs)

    def temporal_equal(self, other: Union[pg.Point, Temporal]) -> Temporal:
        if isinstance(other, pg.Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = teq_tgeogpoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[pg.Point, Temporal]) -> Temporal:
        if isinstance(other, pg.Point):
            gs = gserialized_in(other.to_ewkb(), -1)
            result = tne_tgeogpoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    @staticmethod
    def read_from_cursor(value, _=None):
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

    def hasz(self):
        """
        Does the temporal point has Z dimension?
        """
        return self.start_value().has_z


class TGeomPointInst(TPointInst['TGeomPoint', 'TGeomPointInst', 'TGeomPointSeq', 'TGeomPointSeqSet'], TGeomPoint):
    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(self, string: Optional[str] = None, *, point: Optional[Union[str, pg.Point]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, srid: Optional[int] = 0, _inner=None) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            self._inner = tgeompoint_in(f"SRID={srid};{point}@{timestamp}")


class TGeogPointInst(TPointInst['TGeogPoint', 'TGeogPointInst', 'TGeogPointSeq', 'TGeogPointSeqSet'], TGeogPoint):
    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(self, string: Optional[str] = None, *,
                 point: Optional[Union[str, pg.Point, Tuple[float, float]]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, srid: Optional[int] = 0, _inner=None) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            p = f'POINT({point[0]} {point[1]})' if isinstance(point, tuple) else f'{point}'
            self._inner = tgeogpoint_in(f"SRID={srid};{p}@{timestamp}")


class TGeomPointSeq(TPointSeq['TGeomPoint', 'TGeomPointInst', 'TGeomPointSeq', 'TGeomPointSeqSet'], TGeomPoint):
    ComponentClass = TGeomPointInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TGeomPointInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         expandable=expandable, interpolation=interpolation, normalize=normalize, _inner=_inner)


class TGeogPointSeq(TPointSeq['TGeogPoint', 'TGeogPointInst', 'TGeogPointSeq', 'TGeogPointSeqSet'], TGeogPoint):
    ComponentClass = TGeogPointInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TGeogPointInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         expandable=expandable, interpolation=interpolation, normalize=normalize, _inner=_inner)


class TGeomPointSeqSet(TPointSeqSet['TGeomPoint', 'TGeomPointInst', 'TGeomPointSeq', 'TGeomPointSeqSet'], TGeomPoint):
    ComponentClass = TGeomPointSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TGeomPointSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)


class TGeogPointSeqSet(TPointSeqSet['TGeogPoint', 'TGeogPointInst', 'TGeogPointSeq', 'TGeogPointSeqSet'], TGeogPoint):
    ComponentClass = TGeogPointSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TGeogPointSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
