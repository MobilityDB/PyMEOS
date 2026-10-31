from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar

import shapely.geometry.base as shpb
from pymeos_cffi import *

from ..collections import *
from ..collections.pose import Pose
from ..mixins import TSpatialIO, TTemporallyComparable
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from .tbool import TBool
from .tfloat import TFloat
from .tpoint import TPoint

if TYPE_CHECKING:
    from ..boxes import STBox
    from .tpose import TPose

Self = TypeVar("Self", bound="TRgeometry")


class TRgeometry(
    Temporal[
        shpb.BaseGeometry,
        "TRgeometry",
        "TRgeometryInst",
        "TRgeometrySeq",
        "TRgeometrySeqSet",
    ],
    TTemporallyComparable,
    TSpatialIO,
    ABC,
):
    """
    Abstract class for temporal rigid geometries.
    """

    _mobilitydb_name = "trgeometry"

    _parse_function = trgeometry_in

    BaseClass = shpb.BaseGeometry

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_time(value: shpb.BaseGeometry, base: datetime, pose: Pose) -> TRgeometryInst:
        """
        Create a temporal rigid geometry instant from a reference geometry,
        the pose it takes and a timestamp.

        Args:
            value: A :class:`~shapely.geometry.base.BaseGeometry` with the
                reference geometry.
            base: A :class:`datetime` with the timestamp.
            pose: A :class:`Pose` with the pose of the geometry at `base`.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeometryinst_make
        """
        if isinstance(base, datetime):
            return TRgeometryInst(
                _inner=trgeometryinst_make(geometry_to_gserialized(value), pose._inner, datetime_to_timestamptz(base))
            )
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal rigid geometry from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal rigid geometry.

        MEOS Functions:
            trgeometry_from_mfjson
        """
        result = trgeometry_from_mfjson(mfjson)
        return Temporal._factory(result)

    @staticmethod
    def from_geometry_tpose(geometry: shpb.BaseGeometry, tpose: TPose) -> TRgeometry:
        """
        Create a temporal rigid geometry from a reference geometry and a
        temporal pose.

        Args:
            geometry: A :class:`~shapely.geometry.base.BaseGeometry` with the
                reference geometry.
            tpose: A :class:`TPose` with the temporal pose.

        Returns:
            A new :class:`TRgeometry` object.

        MEOS Functions:
            geometry_tpose_to_trgeometry
        """
        gs = geometry_to_gserialized(geometry)
        result = geometry_tpose_to_trgeometry(gs, tpose._inner)
        return Temporal._factory(result)

    # ------------------------- Output ----------------------------------------
    def __str__(self) -> str:
        """
        Returns the text representation of ``self``, its :meth:`as_text`.
        """
        return self.as_text()

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the string representation of `self`.

        Returns:
            A :class:`str` with the string representation of `self`.

        MEOS Functions:
            trgeometry_as_text
        """
        return trgeometry_as_text(self._inner, max_decimals)

    def as_wkt(self, precision: int = 15) -> str:
        """
        Returns the temporal rigid geometry as a WKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal rigid geometry.

        MEOS Functions:
            trgeometry_as_text
        """
        return trgeometry_as_text(self._inner, precision)

    def as_ewkt(self, precision: int = 15) -> str:
        """
        Returns the temporal rigid geometry as an EWKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal rigid geometry.

        MEOS Functions:
            trgeometry_as_ewkt
        """
        return trgeometry_as_ewkt(self._inner, precision)

    # ------------------------- Conversions -----------------------------------
    def to_tpose(self) -> TPose:
        """
        Returns the temporal pose of `self`.

        Returns:
            A new :class:`TPose` object.

        MEOS Functions:
            trgeometry_to_tpose
        """
        result = trgeometry_to_tpose(self._inner)
        return Temporal._factory(result)

    def to_tpoint(self) -> TPoint:
        """
        Returns the temporal point of the positions of `self`.

        Returns:
            A new :class:`TPoint` object.

        MEOS Functions:
            trgeometry_to_tgeompoint
        """
        result = trgeometry_to_tgeompoint(self._inner)
        return Temporal._factory(result)

    def to_instant(self) -> TRgeometryInst:
        """
        Returns `self` as a :class:`TRgeometryInst`.

        MEOS Functions:
            trgeometry_as_tinstant
        """
        return Temporal._factory(trgeometry_as_tinstant(self._inner))

    # ------------------------- Accessors -------------------------------------
    def bounding_box(self) -> STBox:
        """
        Returns the bounding box of `self`.

        Returns:
            An :class:`~pymeos.boxes.STBox` representing the bounding box.

        MEOS Functions:
            tspatial_to_stbox
        """
        from ..boxes import STBox

        return STBox(_inner=tspatial_to_stbox(self._inner))

    def geometry(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the reference geometry of `self` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` with the
            reference geometry.

        MEOS Functions:
            trgeometry_geom
        """
        return gserialized_to_shapely_geometry(trgeometry_geom(self._inner), precision)

    def values(self, precision: int = 15) -> list[shpb.BaseGeometry]:
        """
        Returns the values of `self`.

        Returns:
            A :class:`list` of :class:`~shapely.geometry.base.BaseGeometry`
            with the values.

        MEOS Functions:
            trgeometry_value_n
        """
        return [i.value(precision=precision) for i in self.instants()]

    def start_value(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the start
            value.

        MEOS Functions:
            trgeometry_start_value
        """
        return gserialized_to_shapely_geometry(trgeometry_start_value(self._inner), precision)

    def end_value(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the end value.

        MEOS Functions:
            trgeometry_end_value
        """
        return gserialized_to_shapely_geometry(trgeometry_end_value(self._inner), precision)

    def value_set(self, precision: int = 15) -> set[shpb.BaseGeometry]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`~shapely.geometry.base.BaseGeometry`
            with the values.

        MEOS Functions:
            trgeometry_value_n
        """
        return {i.value(precision=precision) for i in self.instants()}

    def value_at_timestamp(self, timestamp: datetime, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.
            precision: An :class:`int` representing the precision of the
                coordinates.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the value.

        MEOS Functions:
            trgeometry_value_at_timestamptz
        """
        return gserialized_to_shapely_geometry(
            trgeometry_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True)[0],
            precision,
        )

    def value_n(self, n: int, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the ``n``-th value of `self`.

        Args:
            n: The 0-based index of the value to return.
            precision: An :class:`int` representing the precision of the
                coordinates.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the value.

        MEOS Functions:
            trgeometry_value_n
        """
        return gserialized_to_shapely_geometry(trgeometry_value_n(self._inner, n + 1)[0], precision)

    def start_instant(self: Self) -> TRgeometryInst:
        """
        Returns the first instant of `self`.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeometry_start_instant
        """
        return Temporal._factory(trgeometry_start_instant(self._inner))

    def end_instant(self: Self) -> TRgeometryInst:
        """
        Returns the last instant of `self`.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeometry_end_instant
        """
        return Temporal._factory(trgeometry_end_instant(self._inner))

    def instant_n(self, n: int) -> TRgeometryInst:
        """
        Returns the ``n``-th instant of `self`.

        Args:
            n: The 0-based index of the instant to return.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeometry_instant_n
        """
        return Temporal._factory(trgeometry_instant_n(self._inner, n + 1))

    def instants(self) -> list[TRgeometryInst]:
        """
        Returns the instants of `self`.

        Returns:
            A :class:`list` of :class:`TRgeometryInst` objects.

        MEOS Functions:
            trgeometry_instants
        """
        ins, count = trgeometry_instants(self._inner)
        return [Temporal._factory(ins[i]) for i in range(count)]

    def points(self) -> GeometrySet:
        """
        Returns the set of points of `self`.

        Returns:
            A :class:`GeometrySet` with the points.

        MEOS Functions:
            trgeometry_points
        """
        from ..factory import _CollectionFactory

        return _CollectionFactory.create_collection(trgeometry_points(self._inner))

    def yaw(self) -> TFloat:
        """
        Returns the rotation of `self` as a temporal float.

        Returns:
            A new :class:`TFloat` with the rotation.

        MEOS Functions:
            trgeometry_yaw
        """
        result = trgeometry_yaw(self._inner)
        return Temporal._factory(result)

    def traversed_area(self, unary_union: bool = True, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the traversed area of `self` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        Args:
            unary_union: Whether to apply a unary union to the result.
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` with the
            traversed area.

        MEOS Functions:
            trgeometry_traversed_area
        """
        return gserialized_to_shapely_geometry(trgeometry_traversed_area(self._inner, unary_union), precision)

    # ------------------------- Spatial Reference System ----------------------
    def srid(self) -> int:
        """
        Returns the SRID of `self`.

        Returns:
            An :class:`int` representing the SRID.

        MEOS Functions:
            tspatial_srid
        """
        return tspatial_srid(self._inner)

    def set_srid(self: Self, srid: int) -> Self:
        """
        Returns a new :class:`TRgeometry` with the given SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TRgeometry` instance.

        MEOS Functions:
            tspatial_set_srid
        """
        return self.__class__(_inner=tspatial_set_srid(self._inner, srid))

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> TRgeometry:
        """
        Round the coordinate values to a number of decimal places.

        Returns:
            A new :class:`TRgeometry` object.

        MEOS Functions:
            trgeometry_round
        """
        result = trgeometry_round(self._inner, max_decimals)
        return Temporal._factory(result)

    def transform(self: Self, srid: int) -> Self:
        """
        Returns a new :class:`TRgeometry` transformed to another SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TRgeometry` instance.

        MEOS Functions:
            tspatial_transform
        """
        result = tspatial_transform(self._inner, srid)
        return Temporal._factory(result)

    def set_interpolation(self: Self, interpolation: TInterpolation) -> Self:
        """
        Returns a new :class:`TRgeometry` with the given interpolation.

        Args:
            interpolation: The desired interpolation.

        Returns:
            A new :class:`TRgeometry` instance.

        MEOS Functions:
            trgeometry_set_interp
        """
        result = trgeometry_set_interp(self._inner, interpolation.value)
        return Temporal._factory(result)

    def append_instant(
        self: Self,
        instant: TRgeometryInst,
        max_dist: float | None = 0.0,
        max_time: timedelta | None = None,
    ) -> TRgeometry:
        """
        Returns a new :class:`TRgeometry` with `instant` appended.

        Args:
            instant: The :class:`TRgeometryInst` to append.
            max_dist: The maximum distance between consecutive instants.
            max_time: The maximum time between consecutive instants.

        Returns:
            A new :class:`TRgeometry` object.

        MEOS Functions:
            trgeometry_append_tinstant
        """
        interp = self.interpolation()
        mt = timedelta_to_interval(max_time) if max_time is not None else None
        result = trgeometry_append_tinstant(self._inner, instant._inner, interp.value, max_dist, mt, False)
        return Temporal._factory(result)

    def append_sequence(self: Self, sequence: TRgeometrySeq) -> TRgeometry:
        """
        Returns a new :class:`TRgeometry` with `sequence` appended.

        Args:
            sequence: The :class:`TRgeometrySeq` to append.

        Returns:
            A new :class:`TRgeometry` object.

        MEOS Functions:
            trgeometry_append_tsequence
        """
        result = trgeometry_append_tsequence(self._inner, sequence._inner, False)
        return Temporal._factory(result)

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_trgeometry_geo, always_eq_trgeometry_trgeometry
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return always_eq_trgeometry_geo(self._inner, gs) > 0
        elif isinstance(value, TRgeometry):
            return always_eq_trgeometry_trgeometry(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_trgeometry_geo, always_ne_trgeometry_trgeometry
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return always_ne_trgeometry_geo(self._inner, gs) > 0
        elif isinstance(value, TRgeometry):
            return always_ne_trgeometry_trgeometry(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_trgeometry_geo, ever_eq_trgeometry_trgeometry
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return ever_eq_trgeometry_geo(self._inner, gs) > 0
        elif isinstance(value, TRgeometry):
            return ever_eq_trgeometry_trgeometry(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_trgeometry_geo, ever_ne_trgeometry_trgeometry
        """
        if isinstance(value, shpb.BaseGeometry):
            gs = geometry_to_gserialized(value)
            return ever_ne_trgeometry_geo(self._inner, gs) > 0
        elif isinstance(value, TRgeometry):
            return ever_ne_trgeometry_trgeometry(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_trgeometry_geo, ever_eq_trgeometry_trgeometry
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_trgeometry_geo, ever_ne_trgeometry_trgeometry
        """
        return not self.ever_not_equal(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: shpb.BaseGeometry | TRgeometry) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A :class:`~shapely.geometry.base.BaseGeometry` or temporal
                object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_trgeometry_geo, teq_temporal_temporal
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = teq_trgeometry_geo(self._inner, gs)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: shpb.BaseGeometry | TRgeometry) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A :class:`~shapely.geometry.base.BaseGeometry` or temporal
                object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal
            relation.

        MEOS Functions:
            tne_trgeometry_geo, tne_temporal_temporal
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tne_trgeometry_geo(self._inner, gs)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Ever Spatial Relationships --------------------
    # The names and dispatch are those of #TCbuffer.is_ever_covers and its
    # siblings, and #TPoint.is_ever_contained_in for a geometry containing self.
    def is_ever_contained_in(self, container: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` is ever contained by `container`.

        MEOS Functions:
            econtains_geo_trgeometry
        """
        if isinstance(container, shpb.BaseGeometry):
            result = econtains_geo_trgeometry(geo_to_gserialized(container, False), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_ever_covers(self, other: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` ever covers `other`.

        MEOS Functions:
            ecovers_trgeometry_geo
        """
        if isinstance(other, shpb.BaseGeometry):
            result = ecovers_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_coveredby(self, container: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` is ever covered by `container`: the covers
        relationship with `container` first, as #TRgeometry.is_ever_contained_in
        is for contains and as PostGIS's coveredby is for covers.

        MEOS Functions:
            ecovers_geo_trgeometry
        """
        if isinstance(container, shpb.BaseGeometry):
            result = ecovers_geo_trgeometry(geo_to_gserialized(container, False), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_ever_disjoint(self, other: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether `self` is ever disjoint from `other`.

        MEOS Functions:
            edisjoint_trgeometry_geo, edisjoint_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = edisjoint_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, TRgeometry):
            result = edisjoint_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_within_distance(self, other: shpb.BaseGeometry | TRgeometry, distance: float) -> bool:
        """
        Returns whether `self` is ever within `distance` of `other`.

        MEOS Functions:
            edwithin_trgeometry_geo, edwithin_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = edwithin_trgeometry_geo(self._inner, geo_to_gserialized(other, False), distance)
        elif isinstance(other, TRgeometry):
            result = edwithin_trgeometry_trgeometry(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_intersects(self, other: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether `self` ever intersects `other`.

        MEOS Functions:
            eintersects_trgeometry_geo, eintersects_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = eintersects_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, TRgeometry):
            result = eintersects_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_touches(self, other: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` ever touches `other`.

        MEOS Functions:
            etouches_trgeometry_geo
        """
        if isinstance(other, shpb.BaseGeometry):
            result = etouches_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Always Spatial Relationships ------------------
    def is_always_contained_in(self, container: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` is always contained by `container`.

        MEOS Functions:
            acontains_geo_trgeometry
        """
        if isinstance(container, shpb.BaseGeometry):
            result = acontains_geo_trgeometry(geo_to_gserialized(container, False), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_always_covers(self, other: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` always covers `other`.

        MEOS Functions:
            acovers_trgeometry_geo
        """
        if isinstance(other, shpb.BaseGeometry):
            result = acovers_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_always_coveredby(self, container: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` is always covered by `container`: the covers
        relationship with `container` first, as
        #TRgeometry.is_always_contained_in is for contains.

        MEOS Functions:
            acovers_geo_trgeometry
        """
        if isinstance(container, shpb.BaseGeometry):
            result = acovers_geo_trgeometry(geo_to_gserialized(container, False), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_always_disjoint(self, other: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether `self` is always disjoint from `other`.

        MEOS Functions:
            adisjoint_trgeometry_geo, adisjoint_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = adisjoint_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, TRgeometry):
            result = adisjoint_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_always_within_distance(self, other: shpb.BaseGeometry | TRgeometry, distance: float) -> bool:
        """
        Returns whether `self` is always within `distance` of `other`.

        MEOS Functions:
            adwithin_trgeometry_geo, adwithin_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = adwithin_trgeometry_geo(self._inner, geo_to_gserialized(other, False), distance)
        elif isinstance(other, TRgeometry):
            result = adwithin_trgeometry_trgeometry(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def always_intersects(self, other: shpb.BaseGeometry | TRgeometry) -> bool:
        """
        Returns whether `self` always intersects `other`.

        MEOS Functions:
            aintersects_trgeometry_geo, aintersects_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            result = aintersects_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, TRgeometry):
            result = aintersects_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def always_touches(self, other: shpb.BaseGeometry) -> bool:
        """
        Returns whether `self` always touches `other`.

        MEOS Functions:
            atouches_trgeometry_geo
        """
        if isinstance(other, shpb.BaseGeometry):
            result = atouches_trgeometry_geo(self._inner, geo_to_gserialized(other, False))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Time) -> TRgeometry:
        """
        Returns a new temporal rigid geometry with the values of `self`
        restricted to the time `other`.

        Args:
            other: A time object to restrict the values of `self` to.

        Returns:
            A new :class:`TRgeometry` with the values of `self` restricted to
            `other`.

        MEOS Functions:
            trgeometry_restrict_timestamptz, trgeometry_restrict_tstzset,
            trgeometry_restrict_tstzspan, trgeometry_restrict_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeometry_restrict_timestamptz(self._inner, datetime_to_timestamptz(other), True)
        elif isinstance(other, TsTzSet):
            result = trgeometry_restrict_tstzset(self._inner, other._inner, True)
        elif isinstance(other, TsTzSpan):
            result = trgeometry_restrict_tstzspan(self._inner, other._inner, True)
        elif isinstance(other, TsTzSpanSet):
            result = trgeometry_restrict_tstzspanset(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Time) -> TRgeometry:
        """
        Returns a new temporal rigid geometry with the values of `self`
        restricted to the complement of the time `other`.

        Args:
            other: A time object to restrict the values of `self` to the
                complement of.

        Returns:
            A new :class:`TRgeometry` with the values of `self` restricted to
            the complement of `other`.

        MEOS Functions:
            trgeometry_restrict_timestamptz, trgeometry_restrict_tstzset,
            trgeometry_restrict_tstzspan, trgeometry_restrict_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeometry_restrict_timestamptz(self._inner, datetime_to_timestamptz(other), False)
        elif isinstance(other, TsTzSet):
            result = trgeometry_restrict_tstzset(self._inner, other._inner, False)
        elif isinstance(other, TsTzSpan):
            result = trgeometry_restrict_tstzspan(self._inner, other._inner, False)
        elif isinstance(other, TsTzSpanSet):
            result = trgeometry_restrict_tstzspanset(self._inner, other._inner, False)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Splitting -------------------------------------
    def segments(self) -> list[TRgeometrySeq]:
        """
        Returns the temporal segments of `self`.

        MEOS Functions:
            trgeometry_segments
        """
        seqs, count = trgeometry_segments(self._inner)
        return [Temporal._factory(seqs[i]) for i in range(count)]

    # ------------------------- Modifications ---------------------------------
    def delete(self, other: Time, connect: bool = True) -> TRgeometry:
        """
        Returns a new temporal rigid geometry equal to `self` with the
        elements at `other` removed.

        Args:
            other: A time object to remove from `self`.
            connect: Whether to connect the resulting segments.

        MEOS Functions:
            trgeometry_delete_timestamptz, trgeometry_delete_tstzset,
            trgeometry_delete_tstzspan, trgeometry_delete_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeometry_delete_timestamptz(self._inner, datetime_to_timestamptz(other), connect)
        elif isinstance(other, TsTzSet):
            result = trgeometry_delete_tstzset(self._inner, other._inner, connect)
        elif isinstance(other, TsTzSpan):
            result = trgeometry_delete_tstzspan(self._inner, other._inner, connect)
        elif isinstance(other, TsTzSpanSet):
            result = trgeometry_delete_tstzspanset(self._inner, other._inner, connect)
        else:
            return super().delete(other, connect)
        return Temporal._factory(result)

    def before(self, timestamp: datetime, strict: bool = False) -> TRgeometry:
        """
        Returns a new temporal rigid geometry with the values of `self`
        before `timestamp`.

        Args:
            timestamp: A :class:`datetime` to restrict before.
            strict: Whether the bound is strict.

        MEOS Functions:
            trgeometry_before_timestamptz
        """
        result = trgeometry_before_timestamptz(self._inner, datetime_to_timestamptz(timestamp), strict)
        return Temporal._factory(result)

    def after(self, timestamp: datetime, strict: bool = False) -> TRgeometry:
        """
        Returns a new temporal rigid geometry with the values of `self`
        after `timestamp`.

        Args:
            timestamp: A :class:`datetime` to restrict after.
            strict: Whether the bound is strict.

        MEOS Functions:
            trgeometry_after_timestamptz
        """
        result = trgeometry_after_timestamptz(self._inner, datetime_to_timestamptz(timestamp), strict)
        return Temporal._factory(result)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: shpb.BaseGeometry | TPoint | TRgeometry) -> TFloat:
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` with the temporal distance.

        MEOS Functions:
            tdistance_trgeometry_geo, tdistance_trgeometry_tpoint, tdistance_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tdistance_trgeometry_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = tdistance_trgeometry_tpoint(self._inner, other._inner)
        elif isinstance(other, TRgeometry):
            result = tdistance_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(self, other: shpb.BaseGeometry | STBox | TPoint | TRgeometry) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` with the nearest approach distance.

        MEOS Functions:
            nad_trgeometry_geo, nad_trgeometry_stbox, nad_trgeometry_tpoint, nad_trgeometry_trgeometry
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            return nad_trgeometry_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_trgeometry_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_trgeometry_tpoint(self._inner, other._inner)
        elif isinstance(other, TRgeometry):
            return nad_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_instant(self, other: shpb.BaseGeometry | TPoint | TRgeometry) -> TRgeometryInst:
        """
        Returns the nearest approach instant between `self` and `other`.

        Args:
            other: An object to check the nearest approach instant to.

        Returns:
            A new :class:`TRgeometryInst` with the nearest approach instant.

        MEOS Functions:
            nai_trgeometry_geo, nai_trgeometry_tpoint, nai_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = nai_trgeometry_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = nai_trgeometry_tpoint(self._inner, other._inner)
        elif isinstance(other, TRgeometry):
            result = nai_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def shortest_line(self, other: shpb.BaseGeometry | TPoint | TRgeometry) -> shpb.BaseGeometry:
        """
        Returns the shortest line between `self` and `other`.

        Args:
            other: An object to check the shortest line to.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` with the
            shortest line.

        MEOS Functions:
            shortestline_trgeometry_geo, shortestline_trgeometry_tpoint,
            shortestline_trgeometry_trgeometry
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = shortestline_trgeometry_geo(self._inner, gs)
        elif isinstance(other, TPoint):
            result = shortestline_trgeometry_tpoint(self._inner, other._inner)
        elif isinstance(other, TRgeometry):
            result = shortestline_trgeometry_trgeometry(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return gserialized_to_shapely_geometry(result, 10)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TRgeometry` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TRgeometryInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TRgeometrySeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TRgeometrySeqSet(string=value)
            else:
                return TRgeometrySeq(string=value)
        raise Exception("ERROR: Could not parse temporal rigid geometry value")


class TRgeometryInst(
    TInstant[
        shpb.BaseGeometry,
        "TRgeometry",
        "TRgeometryInst",
        "TRgeometrySeq",
        "TRgeometrySeqSet",
    ],
    TRgeometry,
):
    """
    Class for representing temporal rigid geometries at a single instant.
    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(
        self,
        string: str | None = None,
        *,
        geometry: shpb.BaseGeometry | None = None,
        pose: Pose | None = None,
        timestamp: str | datetime | None = None,
        _inner=None,
    ) -> None:
        if string is None and _inner is None:
            gs = geometry_to_gserialized(geometry)
            ts = (
                datetime_to_timestamptz(timestamp) if isinstance(timestamp, datetime) else timestamptz_in(timestamp, -1)
            )
            _inner = trgeometryinst_make(gs, pose._inner, ts)
        super().__init__(string=string, _inner=_inner)

    def value(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the value of the temporal rigid geometry instant, its geometry
        placed by the pose of the instant, as #TPointInst.value does for a point.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` representing the
            value of the temporal rigid geometry instant.
        """
        return self.start_value(precision=precision)


class TRgeometrySeq(
    TSequence[
        shpb.BaseGeometry,
        "TRgeometry",
        "TRgeometryInst",
        "TRgeometrySeq",
        "TRgeometrySeqSet",
    ],
    TRgeometry,
):
    """
    Class for representing temporal rigid geometries over a tstzspan of time.
    """

    ComponentClass = TRgeometryInst

    def __init__(
        self,
        string: str | None = None,
        *,
        instant_list: list[str | TRgeometryInst] | None = None,
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


class TRgeometrySeqSet(
    TSequenceSet[
        shpb.BaseGeometry,
        "TRgeometry",
        "TRgeometryInst",
        "TRgeometrySeq",
        "TRgeometrySeqSet",
    ],
    TRgeometry,
):
    """
    Class for representing temporal rigid geometries over a tstzspan of time
    with gaps.
    """

    ComponentClass = TRgeometrySeq

    def __init__(
        self,
        string: str | None = None,
        *,
        sequence_list: list[str | TRgeometrySeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )

    # ------------------------- Accessors -------------------------------------
    def start_sequence(self) -> TRgeometrySeq:
        """
        Returns the first sequence of `self`.

        MEOS Functions:
            trgeometry_start_sequence
        """
        return self.ComponentClass(_inner=trgeometry_start_sequence(self._inner))

    def end_sequence(self) -> TRgeometrySeq:
        """
        Returns the last sequence of `self`.

        MEOS Functions:
            trgeometry_end_sequence
        """
        return self.ComponentClass(_inner=trgeometry_end_sequence(self._inner))

    def sequence_n(self, n: int) -> TRgeometrySeq:
        """
        Returns the ``n``-th sequence of `self` (0-based).

        MEOS Functions:
            trgeometry_sequence_n
        """
        return self.ComponentClass(_inner=trgeometry_sequence_n(self._inner, n + 1))

    def sequences(self) -> list[TRgeometrySeq]:
        """
        Returns the list of sequences of `self`.

        MEOS Functions:
            trgeometry_sequences
        """
        seqs, count = trgeometry_sequences(self._inner)
        return [self.ComponentClass(_inner=seqs[i]) for i in range(count)]
