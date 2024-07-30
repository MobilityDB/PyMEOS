from __future__ import annotations

from abc import ABC
from typing import (
    Optional,
    List,
    TYPE_CHECKING,
    Set,
    Tuple,
    Union,
    TypeVar,
    Type,
    overload,
)

import shapely.geometry as shp
import shapely.geometry.base as shpb
from pymeos_cffi import *

from .tbool import TBool
from .tfloat import TFloat, TFloatInst, TFloatSeq, TFloatSeqSet
from ..collections import *
from ..mixins import TSimplifiable
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation

if TYPE_CHECKING:
    from ..boxes import STBox, Box
    from geopandas import GeoDataFrame


def import_geopandas():
    try:
        import geopandas as gpd

        return gpd
    except ImportError:
        print("Geopandas not found. Please install geopandas to use this function.")
        raise


TG = TypeVar("TG", bound="TPoint")
TI = TypeVar("TI", bound="TPointInst")
TS = TypeVar("TS", bound="TPointSeq")
TSS = TypeVar("TSS", bound="TPointSeqSet")
Self = TypeVar("Self", bound="TPoint")
TF = TypeVar("TF", bound="TFloat", covariant=True)


class TPoint(Temporal[shp.Point, TG, TI, TS, TSS], TSimplifiable, ABC):
    """
    Abstract class for temporal points.
    """

    _projection_cache: dict[tuple[int, int], "LWPROJ"] = {}

    # ------------------------- Constructors ----------------------------------
    def __init__(self, _inner) -> None:
        super().__init__()

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str, srid: Optional[int] = None) -> Self:
        result = super().from_hexwkb(hexwkb)
        return result.set_srid(srid) if srid is not None else result

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns the string representation of the temporal point.

        Returns:
            A new :class:`str` representing the temporal point.

        MEOS Functions:
            tpoint_out
        """
        return tpoint_as_text(self._inner, 15)

    def as_wkt(self, precision: int = 15) -> str:
        """
        Returns the temporal point as a WKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal point.

        MEOS Functions:
            tpoint_out
        """
        return tpoint_as_text(self._inner, precision)

    def as_ewkt(self, precision: int = 15) -> str:
        """
        Returns the temporal point as an EWKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal point  .

        MEOS Functions:
            tpoint_as_ewkt
        """
        return tpoint_as_ewkt(self._inner, precision)

    def as_geojson(
        self, option: int = 1, precision: int = 15, srs: Optional[str] = None
    ) -> str:
        """
        Returns the trajectory of the temporal point as a GeoJSON string.

        Args:
            option: The option to use when serializing the trajectory.
            precision: The precision of the returned geometry.
            srs: The spatial reference system of the returned geometry.

        Returns:
            A new GeoJSON string representing the trajectory of the temporal point.

        MEOS Functions:
            gserialized_as_geojson
        """
        return geo_as_geojson(tpoint_trajectory(self._inner), option, precision, srs)

    def to_shapely_geometry(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the trajectory of the temporal point as a Shapely geometry.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` representing the
            trajectory.

        MEOS Functions:
            gserialized_to_shapely_geometry
        """
        return gserialized_to_shapely_geometry(
            tpoint_trajectory(self._inner), precision
        )

    # ------------------------- Accessors -------------------------------------
    def bounding_box(self) -> STBox:
        """
        Returns the bounding box of the `self`.

        Returns:
            An :class:`~pymeos.boxes.STBox` representing the bounding box.

        MEOS Functions:
            tpoint_to_stbox
        """
        from ..boxes import STBox

        return STBox(_inner=tpoint_to_stbox(self._inner))

    def values(self, precision: int = 15) -> List[shp.Point]:
        """
        Returns the values of the temporal point.

        Returns:
            A :class:`list` of :class:`~shapely.geometry.Point` with the values.

        MEOS Functions:
            temporal_instants
        """
        return [i.value(precision=precision) for i in self.instants()]

    def start_value(self, precision: int = 15) -> shp.Point:
        """
        Returns the start value of the temporal point.

        Returns:
            A :class:`~shapely.geometry.Point` with the start value.

        MEOS Functions:
            tpoint_start_value
        """
        return gserialized_to_shapely_point(tpoint_start_value(self._inner), precision)

    def end_value(self, precision: int = 15) -> shp.Point:
        """
        Returns the end value of the temporal point.

        Returns:
            A :class:`~shapely.geometry.Point` with the end value.

        MEOS Functions:
            tpoint_end_value
        """
        return gserialized_to_shapely_point(tpoint_end_value(self._inner), precision)

    def value_set(self, precision: int = 15) -> Set[shp.Point]:
        """
        Returns the set of values of `self`.
        Note that when the interpolation is linear, the set will contain only the waypoints.

        Returns:
            A :class:`set` of :class:`~shapely.geometry.Point` with the values.

        MEOS Functions:
            tpoint_values
        """
        values, count = tpoint_values(self._inner)
        return {
            gserialized_to_shapely_point(values[i], precision) for i in range(count)
        }

    def value_at_timestamp(self, timestamp: datetime, precision: int = 15) -> shp.Point:
        """
        Returns the value of the temporal point at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.
            precision: An :class:`int` representing the precision of the coordinates.

        Returns:
            A :class:`~shapely.geometry.Point` with the value.

        MEOS Functions:
            tpoint_value_at_timestamp
        """
        return gserialized_to_shapely_point(
            tpoint_value_at_timestamptz(
                self._inner, datetime_to_timestamptz(timestamp), True
            )[0],
            precision,
        )

    def length(self) -> float:
        """
        Returns the length of the trajectory.

        Returns:
            A :class:`float` with the length of the trajectory.

        MEOS Functions:
            tpoint_length
        """
        return tpoint_length(self._inner)

    def cumulative_length(self) -> TFloat:
        """
        Returns the cumulative length of the trajectory.

        Returns:
            A :class:`TFloat` with the cumulative length of the trajectory.

        MEOS Functions:
            tpoint_cumulative_length
        """
        result = tpoint_cumulative_length(self._inner)
        return Temporal._factory(result)

    def speed(self) -> TFloat:
        """
        Returns the speed of the temporal point.

        Returns:
            A :class:`TFloat` with the speed of the temporal point.

        MEOS Functions:
            tpoint_speed
        """
        result = tpoint_speed(self._inner)
        return Temporal._factory(result)

    def x(self) -> TF:
        """
        Returns the x coordinate of the temporal point.

        Returns:
            A :class:`TFloat` with the x coordinate of the temporal point.

        MEOS Functions:
            tpoint_get_x
        """
        result = tpoint_get_x(self._inner)
        return Temporal._factory(result)

    def y(self) -> TF:
        """
        Returns the y coordinate of the temporal point.

        Returns:
            A :class:`TFloat` with the y coordinate of the temporal point.

        MEOS Functions:
            tpoint_get_y
        """
        result = tpoint_get_y(self._inner)
        return Temporal._factory(result)

    def z(self) -> TF:
        """
        Returns the z coordinate of the temporal point.

        Returns:
            A :class:`TFloat` with the z coordinate of the temporal point.

        MEOS Functions:
            tpoint_get_z
        """
        result = tpoint_get_z(self._inner)
        return Temporal._factory(result)

    def has_z(self) -> bool:
        """
        Returns whether the temporal point has a z coordinate.

        Returns:
            A :class:`bool` indicating whether the temporal point has a z coordinate.

        MEOS Functions:
            tpoint_start_value
        """
        return self.bounding_box().has_z()

    def stboxes(self) -> List[STBox]:
        """
        Returns a collection of :class:`STBox`es representing the bounding boxes of the segments of the temporal point.

        Returns:
            A :class:`list` of :class:`STBox`es.

        MEOS Functions:
            tpoint_stboxes
        """
        from ..boxes import STBox

        result, count = tpoint_stboxes(self._inner)
        return [STBox(_inner=result + i) for i in range(count)]

    def is_simple(self) -> bool:
        """
        Returns whether the temporal point is simple. That is, whether it does not self-intersect.

        Returns:
            A :class:`bool` indicating whether the temporal point is simple.

        MEOS Functions:
            tpoint_is_simple
        """
        return tpoint_is_simple(self._inner)

    def bearing(self, other: Union[shpb.BaseGeometry, TPoint]) -> TFloat:
        """
        Returns the temporal bearing between the temporal point and `other`.

        Args:
            other: An object to check the bearing to.

        Returns:
            A new :class:`TFloat` indicating the temporal bearing between the temporal point and `other`.

        MEOS Functions:
            bearing_tpoint_point, bearing_tpoint_tpoint
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = bearing_tpoint_point(self._inner, gs, False)
        elif isinstance(other, TPoint):
            result = bearing_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def direction(self) -> float:
        """
        Returns the azimuth of the temporal point between the start and end locations.

        Returns:
            A new :class:`TFloatSeqSet` indicating the direction of the temporal point.

        MEOS Functions:
            tpoint_direction
        """
        return tpoint_direction(self._inner)

    def azimuth(self) -> TFloatSeqSet:
        """
        Returns the temporal azimuth of the temporal point.

        Returns:
            A new :class:`TFloatSeqSet` indicating the temporal azimuth of the temporal point.

        MEOS Functions:
            tpoint_azimuth
        """
        result = tpoint_azimuth(self._inner)
        return Temporal._factory(result)

    def angular_difference(self) -> TFloatSeqSet:
        """
        Returns the angular_difference of the temporal point.

        Returns:
            A new :class:`TFloatSeqSet` indicating the temporal angular_difference of the temporal point.

        MEOS Functions:
            tpoint_angular_difference
        """
        result = tpoint_angular_difference(self._inner)
        return Temporal._factory(result)

    def time_weighted_centroid(self, precision: int = 15) -> shp.Point:
        """
        Returns the time weighted centroid of the temporal point.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` indicating the time weighted centroid of the temporal point.

        MEOS Functions:
            tpoint_twcentroid
        """
        return gserialized_to_shapely_geometry(tpoint_twcentroid(self._inner), precision)  # type: ignore

    # ------------------------- Spatial Reference System ----------------------
    def srid(self) -> int:
        """
        Returns the SRID.

        Returns:
            An :class:`int` representing the SRID.

        MEOS Functions:
            tpoint_srid
        """
        return tpoint_srid(self._inner)

    def set_srid(self: Self, srid: int) -> Self:
        """
        Returns a new TPoint with the given SRID.


        """
        return self.__class__(_inner=tpoint_set_srid(self._inner, srid))

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> TPoint:
        """
        Round the coordinate values to a number of decimal places.

        Returns:
            A new :class:`TGeomPoint` object.

        MEOS Functions:
            tpoint_round
        """
        result = tpoint_round(self._inner, max_decimals)
        return Temporal._factory(result)

    def make_simple(self) -> List[TPoint]:
        """
        Split the temporal point into a collection of simple temporal points.

        Returns:
            A :class:`list` of :class:`TPoint`es.

        MEOS Functions:
            tpoint_make_simple
        """
        result, count = tpoint_make_simple(self._inner)
        return [Temporal._factory(result[i]) for i in range(count)]

    def expand(self, other: Union[int, float]) -> STBox:
        """
        Expands ``self`` with `other`.
        The result is equal to ``self`` but with the spatial dimensions
        expanded by `other` in all directions.

        Args:
            other: The object to expand ``self`` with.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            tpoint_expand_space
        """
        from ..boxes import STBox

        result = tpoint_expand_space(self._inner, float(other))
        return STBox(_inner=result)

    def transform(self: Self, srid: int) -> Self:
        """
        Returns a new :class:`TPoint` of the same subclass of ``self`` transformed to another SRID

        Args:
            srid: The desired SRID

        Returns:
             A new :class:`TPoint` instance

         MEOS Functions:
            tpoint_transform
        """
        srids = (self.srid(), srid)
        if srids not in self._projection_cache:
            self._projection_cache[srids] = lwproj_transform(*srids)
        result = tpoint_transform_pj(self._inner, srid, self._projection_cache[srids])
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Union[shpb.BaseGeometry, GeoSet, STBox, Time]) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to `other`.

        Args:
            other: An object to restrict the values of `self` to.

        Returns:
            A new :TPoint: with the values of `self` restricted to `other`.

        MEOS Functions:
            tpoint_at_value, tpoint_at_stbox, temporal_at_values,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan, temporal_at_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, shp.Point):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_at_value(self._inner, gs)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_at_geom_time(self._inner, gs, None, None)
        elif isinstance(other, GeoSet):
            result = temporal_at_values(self._inner, other._inner)
        elif isinstance(other, STBox):
            result = tpoint_at_stbox(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[shpb.BaseGeometry, GeoSet, STBox, Time]) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to the complement of `other`.

        Args:
            other: An object to restrict the values of `self` to the complement of.

        Returns:
            A new :TPoint: with the values of `self` restricted to the complement of `other`.

        MEOS Functions:
            tpoint_minus_value, tpoint_minus_stbox, temporal_minus_values,
            temporal_minus_timestamp, temporal_minus_tstzset, temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, shp.Point):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_minus_value(self._inner, gs)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tpoint_minus_geom_time(self._inner, gs, None, None)
        elif isinstance(other, GeoSet):
            result = temporal_minus_values(self._inner, other._inner)
        elif isinstance(other, STBox):
            result = tpoint_minus_stbox(self._inner, other._inner, True)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is left to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if left, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_before`
        """
        return self.bounding_box().is_left(other)

    def is_over_or_left(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or left to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or left, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_left(other)

    def is_right(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is right to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if right, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_after`
        """
        return self.bounding_box().is_right(other)

    def is_over_or_right(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or right to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or right, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_right(other)

    def is_below(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is below to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if below, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_before`
        """
        return self.bounding_box().is_below(other)

    def is_over_or_below(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or below to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or below, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_below(other)

    def is_above(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is above to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if above, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_after`
        """
        return self.bounding_box().is_above(other)

    def is_over_or_above(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or above to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or above, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_above(other)

    def is_front(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is front to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if front, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_before`
        """
        return self.bounding_box().is_front(other)

    def is_over_or_front(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or front to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or front, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_front(other)

    def is_behind(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is behind to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if behind, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_after`
        """
        return self.bounding_box().is_behind(other)

    def is_over_or_behind(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or behind to the bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or behind, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_behind(other)

    # ------------------------- Ever Spatial Relationships --------------------
    def is_ever_contained_in(self, container: Union[shpb.BaseGeometry, STBox]) -> bool:
        """
        Returns whether the temporal point is ever contained by `container`.

        Args:
            container: An object to check for containing `self`.

        Returns:
            A :class:`bool` indicating whether the temporal point is ever contained by `container`.

        MEOS Functions:
            econtains_geo_tpoint
        """
        from ..boxes import STBox

        if isinstance(container, shpb.BaseGeometry):
            gs = geo_to_gserialized(container, isinstance(self, TGeogPoint))
            result = econtains_geo_tpoint(gs, self._inner)
        elif isinstance(container, STBox):
            result = econtains_geo_tpoint(stbox_to_geo(container._inner), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_ever_disjoint(self, other: TPoint) -> bool:
        """
        Returns whether the temporal point is ever disjoint from `other`.

        Args:
            other: An object to check for disjointness with.

        Returns:
            A :class:`bool` indicating whether the temporal point is ever disjoint from `other`.

        MEOS Functions:
            edisjoint_tpoint_geo, edisjoint_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, TPoint):
            result = edisjoint_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_within_distance(
        self, other: Union[shpb.BaseGeometry, TPoint, STBox], distance: float
    ) -> bool:
        """
        Returns whether the temporal point is ever within `distance` of `other`.

        Args:
            other: An object to check the distance to.
            distance: The distance to check in units of the spatial reference system.

        Returns:
            A :class:`bool` indicating whether the temporal point is ever within `distance` of `other`.

        MEOS Functions:
            edwithin_tpoint_geo, edwithin_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = edwithin_tpoint_geo(self._inner, gs, distance)
        elif isinstance(other, STBox):
            result = edwithin_tpoint_geo(
                self._inner, stbox_to_geo(other._inner), distance
            )
        elif isinstance(other, TPoint):
            result = edwithin_tpoint_tpoint(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_intersects(self, other: Union[shpb.BaseGeometry, TPoint, STBox]) -> bool:
        """
        Returns whether the temporal point ever intersects `other`.

        Args:
            other: An object to check for intersection with.

        Returns:
            A :class:`bool` indicating whether the temporal point ever intersects `other`.

        MEOS Functions:
            eintersects_tpoint_geo, eintersects_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = eintersects_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            result = eintersects_tpoint_geo(self._inner, stbox_to_geo(other._inner))
        elif isinstance(other, TPoint):
            result = eintersects_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_touches(self, other: Union[shpb.BaseGeometry, STBox]) -> bool:
        """
        Returns whether the temporal point ever touches `other`.

        Args:
            other: An object to check for touching with.

        Returns:
            A :class:`bool` indicating whether the temporal point ever touches `other`.

        MEOS Functions:
            etouches_tpoint_geo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = etouches_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            result = etouches_tpoint_geo(self._inner, stbox_to_geo(other._inner))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Temporal Spatial Relationships ----------------
    def is_spatially_contained_in(
        self, container: Union[shpb.BaseGeometry, STBox]
    ) -> TBool:
        """
        Returns a new temporal boolean indicating whether the temporal point is contained by `container`.

        Args:
            container: An object to check for containing `self`.

        Returns:
            A new :TBool: indicating whether the temporal point is contained by `container`.

        MEOS Functions:
            tcontains_geo_tpoint
        """
        from ..boxes import STBox

        if isinstance(container, shpb.BaseGeometry):
            gs = geo_to_gserialized(container, isinstance(self, TGeogPoint))
            result = tcontains_geo_tpoint(gs, self._inner, False, False)
        elif isinstance(container, STBox):
            gs = stbox_to_geo(container._inner)
            result = tcontains_geo_tpoint(gs, self._inner, False, False)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return Temporal._factory(result)

    def disjoint(self, other: Union[shpb.BaseGeometry, STBox]) -> TBool:
        """
        Returns a new temporal boolean indicating whether the temporal point intersects `other`.

        Args:
            other: An object to check for intersection with.

        Returns:
            A new :TBool: indicating whether the temporal point intersects `other`.

        MEOS Functions:
            tintersects_tpoint_geo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tdisjoint_tpoint_geo(self._inner, gs, False, False)
        elif isinstance(other, STBox):
            result = tdisjoint_tpoint_geo(
                self._inner, stbox_to_geo(other._inner), False, False
            )
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def within_distance(
        self, other: Union[shpb.BaseGeometry, TPoint, STBox], distance: float
    ) -> TBool:
        """
        Returns a new temporal boolean indicating whether the temporal point is within `distance` of `other`.

        Args:
            other: An object to check the distance to.
            distance: The distance to check in units of the spatial reference system.

        Returns:
            A new :TBool: indicating whether the temporal point is within `distance` of `other`.

        MEOS Functions:
            tdwithin_tpoint_geo, tdwithin_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tdwithin_tpoint_geo(self._inner, gs, distance, False, False)
        elif isinstance(other, STBox):
            result = tdwithin_tpoint_geo(
                self._inner, stbox_to_geo(other._inner), distance, False, False
            )
        elif isinstance(other, TPoint):
            result = tdwithin_tpoint_tpoint(
                self._inner, other._inner, distance, False, False
            )
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def intersects(self, other: Union[shpb.BaseGeometry, STBox]) -> TBool:
        """
        Returns a new temporal boolean indicating whether the temporal point intersects `other`.

        Args:
            other: An object to check for intersection with.

        Returns:
            A new :TBool: indicating whether the temporal point intersects `other`.

        MEOS Functions:
            tintersects_tpoint_geo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = tintersects_tpoint_geo(self._inner, gs, False, False)
        elif isinstance(other, STBox):
            result = tintersects_tpoint_geo(
                self._inner, stbox_to_geo(other._inner), False, False
            )
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def touches(self, other: Union[shpb.BaseGeometry, STBox]) -> TBool:
        """
        Returns a new temporal boolean indicating whether the temporal point touches `other`.

        Args:
            other: An object to check for touching with.

        Returns:
            A new :TBool: indicating whether the temporal point touches `other`.

        MEOS Functions:
            ttouches_tpoint_geo
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = ttouches_tpoint_geo(self._inner, gs, False, False)
        elif isinstance(other, STBox):
            result = ttouches_tpoint_geo(
                self._inner, stbox_to_geo(other._inner), False, False
            )
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[shpb.BaseGeometry, TPoint, STBox]) -> TFloat:
        """
        Returns the temporal distance between the temporal point and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` indicating the temporal distance between the temporal point and `other`.

        MEOS Functions:
            distance_tpoint_point, distance_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = distance_tpoint_point(self._inner, gs)
        elif isinstance(other, STBox):
            result = distance_tpoint_point(self._inner, stbox_to_geo(other._inner))
        elif isinstance(other, TPoint):
            result = distance_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[shpb.BaseGeometry, STBox, TPoint]
    ) -> float:
        """
        Returns the nearest approach distance between the temporal point and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` indicating the nearest approach distance between the temporal point and `other`.

        MEOS Functions:
            nad_tpoint_geo, nad_tpoint_stbox, nad_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            return nad_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_tpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_instant(self, other: Union[shpb.BaseGeometry, TPoint]) -> TI:
        """
        Returns the nearest approach instant between the temporal point and `other`.

        Args:
            other: An object to check the nearest approach instant to.

        Returns:
            A new temporal instant indicating the nearest approach instant between the temporal point and `other`.

        MEOS Functions:
            nai_tpoint_geo, nai_tpoint_tpoint
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = nai_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = nai_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def shortest_line(
        self, other: Union[shpb.BaseGeometry, TPoint]
    ) -> shpb.BaseGeometry:
        """
        Returns the shortest line between the temporal point and `other`.

        Args:
            other: An object to check the shortest line to.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` indicating the shortest line between the temporal point
            and `other`.

        MEOS Functions:
            shortestline_tpoint_geo, shortestline_tpoint_tpoint
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = shortestline_tpoint_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = shortestline_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return gserialized_to_shapely_geometry(result, 10)

    # ------------------------- Tiling Operations -----------------------------
    def tile(
        self,
        size: float,
        duration: Optional[Union[timedelta, str]] = None,
        origin: Optional[shpb.BaseGeometry] = None,
        start: Union[datetime, str, None] = None,
        remove_empty: Optional[bool] = False,
    ) -> List[TG]:
        """
        Split the temporal point into segments following the tiling of the
        bounding box.

        Args:
            size: The size of the spatial tiles. If `self` has a spatial
                dimension and this argument is not provided, the tiling will be
                only temporal.
            duration: The duration of the temporal tiles. If `self` has a time
                dimension and this argument is not provided, the tiling will be
                only spatial.
            origin: The origin of the spatial tiling. If not provided, the
                origin will be (0, 0, 0).
            start: The start time of the temporal tiling. If not provided,
                the start time used by default is Monday, January 3, 2000.
            remove_empty: If True, remove the tiles that are empty.

        Returns:
            A list of :class:`TPoint` objects.

        See Also:
            :meth:`STBox.tile`
        """
        from ..boxes import STBox

        bbox = STBox.from_tpoint(self)
        tiles = bbox.tile(size, duration, origin, start)
        if remove_empty:
            return [x for x in (self.at(tile) for tile in tiles) if x]
        else:
            return [self.at(tile) for tile in tiles]

    # ------------------------- Split Operations ------------------------------
    def space_split(
        self,
        xsize: float,
        ysize: Optional[float] = None,
        zsize: Optional[float] = None,
        origin: Optional[shpb.BaseGeometry] = None,
        bitmatrix: Optional[bool] = False,
    ) -> List[Temporal]:
        """
        Splits `self` into fragments with respect to space buckets

        Args:
            xsize: Size of the x dimension.
            ysize: Size of the y dimension.
            zsize: Size of the z dimension.
            origin: The origin of the spatial tiling. If not provided, the
                origin will be (0, 0, 0).
            bitmatrix: If True, use a bitmatrix to speed up the process.

        Returns:
            A list of temporal points.

        MEOS Functions:
            tpoint_value_split
        """
        ysz = ysize if ysize is not None else xsize
        zsz = zsize if zsize is not None else xsize
        gs = (
            geo_to_gserialized(origin, isinstance(self, TGeogPoint))
            if origin is not None
            else (
                pgis_geography_in("Point(0 0 0)", -1)
                if isinstance(self, TGeogPoint)
                else pgis_geometry_in("Point(0 0 0)", -1)
            )
        )
        fragments, values, count = tpoint_space_split(
            self._inner, xsize, ysz, zsz, gs, bitmatrix
        )
        from ..factory import _TemporalFactory

        return [_TemporalFactory.create_temporal(fragments[i]) for i in range(count)]

    def space_time_split(
        self,
        xsize: float,
        duration: Union[str, timedelta],
        ysize: Optional[float] = None,
        zsize: Optional[float] = None,
        origin: Optional[shpb.BaseGeometry] = None,
        time_start: Optional[Union[str, datetime]] = None,
        bitmatrix: Optional[bool] = False,
    ) -> List[Temporal]:
        """
        Splits `self` into fragments with respect to space and tstzspan buckets.

        Args:
            xsize: Size of the x dimension.
            ysize: Size of the y dimension.
            zsize: Size of the z dimension.
            duration: Duration of the tstzspan buckets.
            origin: The origin of the spatial tiling. If not provided, the
                origin will be (0, 0, 0).
            time_start: Start time of the first tstzspan bucket. If None, the
                start time used by default is Monday, January 3, 2000.
            bitmatrix: If True, use a bitmatrix to speed up the process.

        Returns:
            A list of temporal floats.

        MEOS Functions:
            tfloat_value_time_split
        """
        ysz = ysize if ysize is not None else xsize
        zsz = zsize if zsize is not None else xsize
        dt = (
            timedelta_to_interval(duration)
            if isinstance(duration, timedelta)
            else pg_interval_in(duration, -1)
        )
        gs = (
            geo_to_gserialized(origin, isinstance(self, TGeogPoint))
            if origin is not None
            else (
                pgis_geography_in("Point(0 0 0)", -1)
                if isinstance(self, TGeogPoint)
                else pgis_geometry_in("Point(0 0 0)", -1)
            )
        )
        if time_start is None:
            st = pg_timestamptz_in("2000-01-03", -1)
        else:
            st = (
                datetime_to_timestamptz(time_start)
                if isinstance(time_start, datetime)
                else pg_timestamptz_in(time_start, -1)
            )
        fragments, points, times, count = tpoint_space_time_split(
            self._inner, xsize, ysz, zsz, dt, gs, st, bitmatrix
        )
        return [Temporal._factory(fragments[i]) for i in range(count)]


class TPointInst(
    TInstant[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC
):
    """
    Abstract class for temporal point instants.
    """

    def value(self, precision: int = 15) -> shp.Point:
        """
        Returns the value of the temporal point instant.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.point.Point` representing the value of the temporal point instant.
        """
        return self.start_value(precision=precision)

    def x(self) -> TFloatInst:
        return super().x()

    def y(self) -> TFloatInst:
        return super().y()

    def z(self) -> TFloatInst:
        return super().z()


class TPointSeq(
    TSequence[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC
):
    """
    Abstract class for temporal point sequences.
    """

    def x(self) -> TFloatSeq:
        return super().x()

    def y(self) -> TFloatSeq:
        return super().y()

    def z(self) -> TFloatSeq:
        return super().z()

    def plot(self, *args, **kwargs):
        """
        Plots the temporal point sequence.

        Args:
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.

        See Also:
            :func:`~pygeos.plotters.point_sequence_plotter.TemporalPointSequencePlotter.plot_xy`
        """
        from ..plotters import TemporalPointSequencePlotter

        return TemporalPointSequencePlotter.plot_xy(self, *args, **kwargs)


class TPointSeqSet(
    TSequenceSet[shpb.BaseGeometry, TG, TI, TS, TSS], TPoint[TG, TI, TS, TSS], ABC
):
    """
    Abstract class for temporal point sequence sets.
    """

    def to_dataframe(self, precision: int = 15) -> GeoDataFrame:
        """
        Returns the temporal point sequence set as a GeoPandas DataFrame.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`GeoDataFrame` representing the temporal point
            sequence set.
        """
        gpd = import_geopandas()
        sequences = self.sequences()
        data = {
            "sequence": [
                i + 1
                for i, seq in enumerate(sequences)
                for _ in range(seq.num_instants())
            ],
            "time": [t for seq in sequences for t in seq.timestamps()],
            "geometry": [
                v for seq in sequences for v in seq.values(precision=precision)
            ],
        }
        return gpd.GeoDataFrame(data, crs=self.srid()).set_index(
            keys=["sequence", "time"]
        )

    def x(self) -> TFloatSeqSet:
        return super().x()

    def y(self) -> TFloatSeqSet:
        return super().y()

    def z(self) -> TFloatSeqSet:
        return super().z()

    def plot(self, *args, **kwargs):
        """
        Plots the temporal point sequence set.

        Args:
            *args: Additional arguments to pass to the plot function.
            **kwargs: Additional keyword arguments to pass to the plot function.

        Returns:
            List with the plotted elements.

        See Also:
            :func:`~pygeos.plotters.point_sequenceset_plotter.TemporalPointSequenceSetPlotter.plot_xy`
        """
        from ..plotters import TemporalPointSequenceSetPlotter

        return TemporalPointSequenceSetPlotter.plot_xy(self, *args, **kwargs)


class TGeomPoint(
    TPoint["TGeomPoint", "TGeomPointInst", "TGeomPointSeq", "TGeomPointSeqSet"], ABC
):
    """
    Abstract class for temporal geometric points.
    """

    _mobilitydb_name = "tgeompoint"

    BaseClass = shp.Point
    _parse_function = tgeompoint_in

    # ------------------------- Output ----------------------------------------
    @staticmethod
    def from_base_temporal(value: shpb.BaseGeometry, base: Temporal) -> TGeomPoint:
        """
        Creates a temporal geometric point from a base geometry and the time
        frame of another temporal object.

        Args:
            value: The base geometry.
            base: The temporal object defining the time frame.

        Returns:
            A new :class:`TGeomPoint` object.

        MEOS Functions:
            tpoint_from_base_temp
        """
        gs = geometry_to_gserialized(value)
        result = tpoint_from_base_temp(gs, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: datetime, interpolation: None = None
    ) -> TGeomPointInst: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: TsTzSet, interpolation: None = None
    ) -> TGeomPointSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: TsTzSpan, interpolation: TInterpolation = None
    ) -> TGeomPointSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry,
        base: TsTzSpanSet,
        interpolation: TInterpolation = None,
    ) -> TGeomPointSeqSet: ...

    @staticmethod
    def from_base_time(
        value: shpb.BaseGeometry, base: Time, interpolation: TInterpolation = None
    ) -> TGeomPoint:
        """
        Creates a temporal geometric point from a base geometry and a time value.

        Args:
            value: The base geometry.
            base: The time value.
            interpolation: The interpolation method.

        Returns:
            A new :class:`TGeomPoint` object.

        MEOS Functions:
            tpointinst_make, tpointseq_from_base_tstzset,
            tpointseq_from_base_tstzspan, tpointseqset_from_base_tstzspanset
        """
        gs = geometry_to_gserialized(value)
        if isinstance(base, datetime):
            return TGeomPointInst(
                _inner=tpointinst_make(gs, datetime_to_timestamptz(base))
            )
        elif isinstance(base, TsTzSet):
            return TGeomPointSeq(_inner=tpointseq_from_base_tstzset(gs, base._inner))
        elif isinstance(base, TsTzSpan):
            return TGeomPointSeq(
                _inner=tpointseq_from_base_tstzspan(gs, base._inner, interpolation)
            )
        elif isinstance(base, TsTzSpanSet):
            return TGeomPointSeqSet(
                _inner=tpointseqset_from_base_tstzspanset(
                    gs, base._inner, interpolation
                )
            )
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: Type[Self], mfjson: str) -> Self:
        """
        Returns a temporal object from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal object from a MF-JSON string.

        MEOS Functions:
            tgeompoint_from_mfjson
        """

        result = tgeompoint_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Conversions ----------------------------------
    def to_geographic(self) -> TGeogPoint:
        """
        Returns a copy of `self` converted to geographic coordinates.

        Returns:
            A new :class:`TGeogPoint` object.

        MEOS Functions:
            tgeompoint_to_tgeogpoint
        """
        result = tgeompoint_to_tgeogpoint(self._inner)
        return Temporal._factory(result)

    def to_dataframe(self) -> GeoDataFrame:
        """
        Returns the trajectory of the temporal point as a GeoPandas DataFrame.

        Returns:
            A new :class:`GeoDataFrame` representing the trajectory.
        """
        gpd = import_geopandas()
        data = {
            "time": self.timestamps(),
            "geometry": [i.value() for i in self.instants()],
        }
        return gpd.GeoDataFrame(data, crs=self.srid()).set_index(keys=["time"])

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is always equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is always equal to `value`, False otherwise.

        MEOS Functions:
            always_eq_tpoint_point, always_eq_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return always_eq_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeomPoint):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is always different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is always different to `value`, False otherwise.

        MEOS Functions:
            always_ne_tpoint_point, always_ne_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return always_ne_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeomPoint):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is ever equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is ever equal to `value`, False otherwise.

        MEOS Functions:
            ever_eq_tpoint_point, ever_eq_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return ever_eq_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeomPoint):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is ever different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is ever different to `value`, False otherwise.

        MEOS Functions:
            ever_ne_tpoint_point, ever_ne_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return ever_ne_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeomPoint):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is never equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is never equal to `value`, False otherwise.

        MEOS Functions:
            ever_eq_tpoint_point, ever_eq_temporal_temporal
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[shpb.BaseGeometry, TGeomPoint]) -> bool:
        """
        Returns whether `self` is never different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is never different to `value`, False otherwise.

        MEOS Functions:
            ever_ne_tpoint_point, ever_ne_temporal_temporal
        """
        return not self.ever_not_equal(value)

    def is_ever_disjoint(
        self, other: Union[shpb.BaseGeometry, TGeomPoint, STBox]
    ) -> bool:
        """
        Returns whether the temporal point is ever disjoint from `other`.

        Args:
            other: An object to check for disjointness with.

        Returns:
            A :class:`bool` indicating whether the temporal point is ever disjoint from `other`.

        MEOS Functions:
            edisjoint_tpoint_geo, edisjoint_tpoint_tpoint
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, isinstance(self, TGeogPoint))
            result = edisjoint_tpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            result = edisjoint_tpoint_geo(self._inner, stbox_to_geo(other._inner))
        elif isinstance(other, TGeomPoint):
            result = edisjoint_tpoint_tpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[shp.Point, TGeomPoint]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tpoint_point, teq_temporal_temporal
        """
        if isinstance(other, shp.Point):
            gs = geometry_to_gserialized(other)
            result = teq_tpoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[shp.Point, TGeomPoint]) -> TBool:
        """
        Returns the temporal inequality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal inequality relation.

        MEOS Functions:
            tne_tpoint_point, tne_temporal_temporal
        """
        if isinstance(other, shp.Point):
            gs = geometry_to_gserialized(other)
            result = tne_tpoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TGeogPoint` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value.startswith("Interp=Stepwise;"):
            value1 = value.replace("Interp=Stepwise;", "")
            if value1[0] == "{":
                return TGeomPointSeqSet(string=value)
            else:
                return TGeomPointSeq(string=value)
        elif value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TGeomPointInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TGeomPointSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TGeomPointSeqSet(string=value)
            else:
                return TGeomPointSeq(string=value)
        raise Exception("ERROR: Could not parse temporal point value")


class TGeogPoint(
    TPoint["TGeogPoint", "TGeogPointInst", "TGeogPointSeq", "TGeogPointSeqSet"], ABC
):
    """
    Abstract class for representing temporal geographic points.
    """

    _mobilitydb_name = "tgeogpoint"

    BaseClass = shp.Point
    _parse_function = tgeogpoint_in

    # ------------------------- Output ----------------------------------------
    @staticmethod
    def from_base_temporal(value: shpb.BaseGeometry, base: Temporal) -> TGeogPoint:
        """
        Creates a temporal geographic point from a base geometry and the time
        frame of another temporal object.

        Args:
            value: The base geometry.
            base: The temporal object defining the time frame.

        Returns:
            A new :class:`TGeogPoint` object.

        MEOS Functions:
            tpoint_from_base_temp
        """
        gs = geography_to_gserialized(value)
        result = tpoint_from_base_temp(gs, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: datetime, interpolation: TInterpolation = None
    ) -> TGeogPointInst: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: TsTzSet, interpolation: TInterpolation = None
    ) -> TGeogPointSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry, base: TsTzSpan, interpolation: TInterpolation = None
    ) -> TGeogPointSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: shpb.BaseGeometry,
        base: TsTzSpanSet,
        interpolation: TInterpolation = None,
    ) -> TGeogPointSeqSet: ...

    @staticmethod
    def from_base_time(
        value: shpb.BaseGeometry, base: Time, interpolation: TInterpolation = None
    ) -> TGeogPoint:
        """
        Creates a temporal geographic point from a base geometry and a time object.

        Args:
            value: The base geometry.
            base: The time object defining the time frame.
            interpolation: The interpolation method.

        Returns:
            A new :class:`TGeogPoint` object.

        MEOS Functions:
            tpointinst_make, tpointseq_from_base_tstzset,
            tpointseq_from_base_tstzspan, tpointseqset_from_base_tstzspanset
        """
        gs = geography_to_gserialized(value)
        if isinstance(base, datetime):
            return TGeogPointInst(
                _inner=tpointinst_make(gs, datetime_to_timestamptz(base))
            )
        elif isinstance(base, TsTzSet):
            return TGeogPointSeq(_inner=tpointseq_from_base_tstzset(gs, base._inner))
        elif isinstance(base, TsTzSpan):
            return TGeogPointSeq(
                _inner=tpointseq_from_base_tstzspan(gs, base._inner, interpolation)
            )
        elif isinstance(base, TsTzSpanSet):
            return TGeogPointSeqSet(
                _inner=tpointseqset_from_base_tstzspanset(
                    gs, base._inner, interpolation
                )
            )
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: Type[Self], mfjson: str) -> Self:
        """
        Returns a temporal object from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal object from a MF-JSON string.

        MEOS Functions:
            tgeogpoint_from_mfjson
        """

        result = tgeogpoint_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Conversions ----------------------------------
    def to_geometric(self) -> TGeomPoint:
        """
        Converts the temporal geographic point to a temporal geometric point.

        Returns:
            A new :class:`TGeomPoint` object.

        MEOS Functions:
            tgeogpoint_to_tgeompoint
        """
        result = tgeogpoint_to_tgeompoint(self._inner)
        return Temporal._factory(result)

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is always equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is always equal to `value`, False otherwise.

        MEOS Functions:
            always_eq_tpoint_point, always_eq_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geography_to_gserialized(value)
            return always_eq_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeogPoint):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is always different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is always different to `value`, False otherwise.

        MEOS Functions:
            always_ne_tpoint_point, always_ne_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geography_to_gserialized(value)
            return always_ne_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeogPoint):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is ever equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is ever equal to `value`, False otherwise.

        MEOS Functions:
            ever_eq_tpoint_point, ever_eq_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geography_to_gserialized(value)
            return ever_eq_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeogPoint):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is ever different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is ever different to `value`, False otherwise.

        MEOS Functions:
            ever_ne_tpoint_point, ever_ne_temporal_temporal
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geography_to_gserialized(value)
            return ever_ne_tpoint_point(self._inner, gs) > 0
        elif isinstance(value, TGeogPoint):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is never equal to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is never equal to `value`, False otherwise.

        MEOS Functions:
            ever_eq_tpoint_point, ever_eq_temporal_temporal
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[shpb.BaseGeometry, TGeogPoint]) -> bool:
        """
        Returns whether `self` is never different to `value`.

        Args:
            value: The geometry to compare with.

        Returns:
            True if `self` is never different to `value`, False otherwise.

        MEOS Functions:
            ever_ne_tpoint_point, ever_ne_temporal_temporal
        """
        return not self.ever_not_equal(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[shp.Point, TGeogPoint]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tpoint_point, teq_temporal_temporal
        """
        if isinstance(other, shp.Point):
            gs = geography_to_gserialized(other)
            result = teq_tpoint_point(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[shp.Point, TGeogPoint]) -> TBool:
        """
        Returns the temporal inequality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal inequality relation.

        MEOS Functions:
            tne_tpoint_point, tne_temporal_temporal
        """
        if isinstance(other, shp.Point):
            gs = geography_to_gserialized(other)
            result = tne_tpoint_point(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TGeogPoint` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value.startswith("Interp=Stepwise;"):
            value1 = value.replace("Interp=Stepwise;", "")
            if value1[0] == "{":
                return TGeogPointSeqSet(string=value)
            else:
                return TGeogPointSeq(string=value)
        elif value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TGeogPointInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TGeogPointSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TGeogPointSeqSet(string=value)
            else:
                return TGeomPointSeq(string=value)
        raise Exception("ERROR: Could not parse temporal point value")


class TGeomPointInst(
    TPointInst["TGeomPoint", "TGeomPointInst", "TGeomPointSeq", "TGeomPointSeqSet"],
    TGeomPoint,
):
    """
    Class for representing temporal geometric points at a single instant.
    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        point: Optional[
            Union[str, shp.Point, Tuple[float, float], Tuple[float, float, float]]
        ] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        srid: Optional[int] = 0,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            if isinstance(point, tuple):
                p = f'POINT({" ".join(str(x) for x in point)})'
            else:
                p = f"{point}"
            full_str = (
                f"SRID={srid};{p}@{timestamp}"
                if srid is not None
                else f"{p}@{timestamp}"
            )
            self._inner = tgeompoint_in(full_str)


class TGeogPointInst(
    TPointInst["TGeogPoint", "TGeogPointInst", "TGeogPointSeq", "TGeogPointSeqSet"],
    TGeogPoint,
):
    """
    Class for representing temporal geographic points at a single instant.
    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        point: Optional[
            Union[str, shp.Point, Tuple[float, float], Tuple[float, float, float]]
        ] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        srid: Optional[int] = 4326,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=point, timestamp=timestamp, _inner=_inner)
        if self._inner is None:
            if isinstance(point, tuple):
                p = f'POINT({" ".join(str(x) for x in point)})'
            else:
                p = f"{point}"
            full_str = (
                f"SRID={srid};{p}@{timestamp}"
                if srid is not None
                else f"{p}@{timestamp}"
            )
            self._inner = tgeogpoint_in(full_str)


class TGeomPointSeq(
    TPointSeq["TGeomPoint", "TGeomPointInst", "TGeomPointSeq", "TGeomPointSeqSet"],
    TGeomPoint,
):
    """
    Class for representing temporal geometric points over a tstzspan of time.
    """

    ComponentClass = TGeomPointInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TGeomPointInst]]] = None,
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.LINEAR,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            instant_list=instant_list,
            lower_inc=lower_inc,
            upper_inc=upper_inc,
            interpolation=interpolation,
            normalize=normalize,
            _inner=_inner,
        )


class TGeogPointSeq(
    TPointSeq["TGeogPoint", "TGeogPointInst", "TGeogPointSeq", "TGeogPointSeqSet"],
    TGeogPoint,
):
    """
    Class for representing temporal geographic points over a tstzspan of time.
    """

    ComponentClass = TGeogPointInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TGeogPointInst]]] = None,
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.LINEAR,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            instant_list=instant_list,
            lower_inc=lower_inc,
            upper_inc=upper_inc,
            interpolation=interpolation,
            normalize=normalize,
            _inner=_inner,
        )


class TGeomPointSeqSet(
    TPointSeqSet["TGeomPoint", "TGeomPointInst", "TGeomPointSeq", "TGeomPointSeqSet"],
    TGeomPoint,
):
    """
    Class for representing temporal geometric points over a tstzspan of time
    with gaps.
    """

    ComponentClass = TGeomPointSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TGeomPointSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )


class TGeogPointSeqSet(
    TPointSeqSet["TGeogPoint", "TGeogPointInst", "TGeogPointSeq", "TGeogPointSeqSet"],
    TGeogPoint,
):
    """
    Class for representing temporal geographic points over a tstzspan of time
    with gaps.
    """

    ComponentClass = TGeogPointSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TGeogPointSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
