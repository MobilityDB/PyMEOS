from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, TYPE_CHECKING, Set, TypeVar

import shapely.geometry.base as shpb
from pymeos_cffi import *

from .tfloat import TFloat
from .tpoint import TPoint
from ..collections import *
from ..collections.cbuffer import Cbuffer, CbufferSet
from ..mixins import TTemporallyComparable
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation

if TYPE_CHECKING:
    from .tbool import TBool
    from ..boxes import STBox

Self = TypeVar("Self", bound="TCbuffer")


class TCbuffer(
    Temporal[Cbuffer, "TCbuffer", "TCbufferInst", "TCbufferSeq", "TCbufferSeqSet"],
    TTemporallyComparable,
    ABC,
):
    """
    Abstract class for temporal circular buffers.
    """

    _mobilitydb_name = "tcbuffer"

    BaseClass = Cbuffer

    _parse_function = tcbuffer_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_point_radius(point: TPoint, radius: TFloat) -> TCbuffer:
        """
        Create a temporal circular buffer from a temporal point and a temporal
        float representing the radius.

        Args:
            point: A :class:`TPoint` with the center.
            radius: A :class:`TFloat` with the radius.

        Returns:
            A new :class:`TCbuffer` object.

        MEOS Functions:
            tcbuffer_make
        """
        result = tcbuffer_make(point._inner, radius._inner)
        return Temporal._factory(result)

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns the string representation of `self`.

        Returns:
            A :class:`str` with the string representation of `self`.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, 15)

    def as_wkt(self, precision: int = 15) -> str:
        """
        Returns the temporal circular buffer as a WKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal circular buffer.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, precision)

    def as_ewkt(self, precision: int = 15) -> str:
        """
        Returns the temporal circular buffer as an EWKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal circular buffer.

        MEOS Functions:
            tspatial_as_ewkt
        """
        return tspatial_as_ewkt(self._inner, precision)

    # ------------------------- Conversions -----------------------------------
    def to_tfloat(self) -> TFloat:
        """
        Returns the temporal float of the radii of `self`.

        Returns:
            A new :class:`TFloat` object.

        MEOS Functions:
            tcbuffer_to_tfloat
        """
        result = tcbuffer_to_tfloat(self._inner)
        return Temporal._factory(result)

    def to_tgeompoint(self) -> TPoint:
        """
        Returns the temporal geometry point of the centers of `self`.

        Returns:
            A new :class:`TGeomPoint` object.

        MEOS Functions:
            tcbuffer_to_tgeompoint
        """
        result = tcbuffer_to_tgeompoint(self._inner)
        return Temporal._factory(result)

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

    def radius(self) -> TFloat:
        """
        Returns the radius of `self` as a temporal float.

        Returns:
            A new :class:`TFloat` with the radius.

        MEOS Functions:
            tcbuffer_radius
        """
        result = tcbuffer_radius(self._inner)
        return Temporal._factory(result)

    def points(self) -> CbufferSet:
        """
        Returns the set of points of `self`.

        Returns:
            A :class:`CbufferSet` with the points.

        MEOS Functions:
            tcbuffer_points
        """
        return CbufferSet(_inner=tcbuffer_points(self._inner))

    def traversed_area(self) -> shpb.BaseGeometry:
        """
        Returns the traversed area of `self` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` representing the
            traversed area.

        MEOS Functions:
            tcbuffer_trav_area
        """
        return gserialized_to_shapely_geometry(tcbuffer_trav_area(self._inner), 15)

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
        Returns a new :class:`TCbuffer` with the given SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TCbuffer` instance.

        MEOS Functions:
            tspatial_set_srid
        """
        return self.__class__(_inner=tspatial_set_srid(self._inner, srid))

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> TCbuffer:
        """
        Round the coordinate values to a number of decimal places.

        Returns:
            A new :class:`TCbuffer` object.

        MEOS Functions:
            temporal_round
        """
        result = temporal_round(self._inner, max_decimals)
        return Temporal._factory(result)

    def transform(self: Self, srid: int) -> Self:
        """
        Returns a new :class:`TCbuffer` transformed to another SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TCbuffer` instance.

        MEOS Functions:
            tspatial_transform
        """
        result = tspatial_transform(self._inner, srid)
        return Temporal._factory(result)

    # ------------------------- Value Accessors -------------------------------
    # MEOS exposes NO typed value accessor or value-based constructor for the
    # temporal circular buffer: there is no tcbuffer_start_value/end_value/
    # value_set/value_at_timestamp, no tcbufferinst_make, and no
    # tcbuffer_from_base_*; the only generic accessor returns an opaque Datum
    # that cannot be rebuilt into a Cbuffer without Datum-hiding internals.
    # These overrides keep the class concrete and fail loudly instead of
    # making the whole type uninstantiable.  from_mfjson is being added
    # upstream by MobilityDB#1051 (feat/tcbuffer-mfjson); the others remain
    # unimplemented in MEOS and are a separate upstream feature.
    def start_value(self) -> Cbuffer:
        """Not exposed by MEOS for the temporal circular buffer."""
        raise NotImplementedError(
            "MEOS exposes no typed start_value for the temporal circular "
            "buffer (no tcbuffer_start_value); pending upstream."
        )

    def end_value(self) -> Cbuffer:
        """Not exposed by MEOS for the temporal circular buffer."""
        raise NotImplementedError(
            "MEOS exposes no typed end_value for the temporal circular "
            "buffer (no tcbuffer_end_value); pending upstream."
        )

    def value_set(self) -> Set[Cbuffer]:
        """Not exposed by MEOS for the temporal circular buffer."""
        raise NotImplementedError(
            "MEOS exposes no typed value_set for the temporal circular "
            "buffer (no tcbuffer_values); pending upstream."
        )

    def value_at_timestamp(self, timestamp: datetime) -> Cbuffer:
        """Not exposed by MEOS for the temporal circular buffer."""
        raise NotImplementedError(
            "MEOS exposes no typed value_at_timestamp for the temporal "
            "circular buffer (no tcbuffer_value_at_timestamp); pending "
            "upstream."
        )

    @staticmethod
    def from_base_time(value: Cbuffer, base: Time) -> TCbuffer:
        """Not exposed by MEOS for the temporal circular buffer."""
        raise NotImplementedError(
            "MEOS exposes no value-based constructor for the temporal "
            "circular buffer (no tcbufferinst_make / tcbuffer_from_base_*); "
            "pending upstream."
        )

    @classmethod
    def from_mfjson(cls, mfjson: str) -> TCbuffer:
        """MF-JSON input is being added upstream (MobilityDB#1051)."""
        raise NotImplementedError(
            "MEOS MF-JSON input for the temporal circular buffer is being "
            "added upstream by MobilityDB#1051 (feat/tcbuffer-mfjson)."
        )

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tcbuffer_cbuffer, always_eq_tcbuffer_tcbuffer
        """
        if isinstance(value, Cbuffer):
            return always_eq_tcbuffer_cbuffer(self._inner, value._inner) > 0
        elif isinstance(value, TCbuffer):
            return always_eq_tcbuffer_tcbuffer(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tcbuffer_cbuffer, always_ne_tcbuffer_tcbuffer
        """
        if isinstance(value, Cbuffer):
            return always_ne_tcbuffer_cbuffer(self._inner, value._inner) > 0
        elif isinstance(value, TCbuffer):
            return always_ne_tcbuffer_tcbuffer(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tcbuffer_cbuffer, ever_eq_tcbuffer_tcbuffer
        """
        if isinstance(value, Cbuffer):
            return ever_eq_tcbuffer_cbuffer(self._inner, value._inner) > 0
        elif isinstance(value, TCbuffer):
            return ever_eq_tcbuffer_tcbuffer(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tcbuffer_cbuffer, ever_ne_tcbuffer_tcbuffer
        """
        if isinstance(value, Cbuffer):
            return ever_ne_tcbuffer_cbuffer(self._inner, value._inner) > 0
        elif isinstance(value, TCbuffer):
            return ever_ne_tcbuffer_tcbuffer(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tcbuffer_cbuffer, ever_eq_tcbuffer_tcbuffer
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`Cbuffer` or :class:`TCbuffer` to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tcbuffer_cbuffer, ever_ne_tcbuffer_tcbuffer
        """
        return not self.ever_not_equal(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[Cbuffer, TCbuffer]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A :class:`Cbuffer` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tcbuffer_cbuffer, teq_temporal_temporal
        """
        if isinstance(other, Cbuffer):
            result = teq_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[Cbuffer, TCbuffer]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A :class:`Cbuffer` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal
            relation.

        MEOS Functions:
            tne_tcbuffer_cbuffer, tne_temporal_temporal
        """
        if isinstance(other, Cbuffer):
            result = tne_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Union[Cbuffer, shpb.BaseGeometry, STBox, Time]) -> TCbuffer:
        """
        Returns a new temporal circular buffer with the values of `self`
        restricted to `other`.

        Args:
            other: An object to restrict the values of `self` to.

        Returns:
            A new :class:`TCbuffer` with the values of `self` restricted to
            `other`.

        MEOS Functions:
            tcbuffer_at_cbuffer, tcbuffer_at_geom, tcbuffer_at_stbox,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Cbuffer):
            result = tcbuffer_at_cbuffer(self._inner, other._inner)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tcbuffer_at_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tcbuffer_at_stbox(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[Cbuffer, shpb.BaseGeometry, STBox, Time]) -> TCbuffer:
        """
        Returns a new temporal circular buffer with the values of `self`
        restricted to the complement of `other`.

        Args:
            other: An object to restrict the values of `self` to the
            complement of.

        Returns:
            A new :class:`TCbuffer` with the values of `self` restricted to
            the complement of `other`.

        MEOS Functions:
            tcbuffer_minus_cbuffer, tcbuffer_minus_geom, tcbuffer_minus_stbox,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Cbuffer):
            result = tcbuffer_minus_cbuffer(self._inner, other._inner)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tcbuffer_minus_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tcbuffer_minus_stbox(self._inner, other._inner, True)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TFloat:
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` with the temporal distance.

        MEOS Functions:
            tdistance_tcbuffer_geo, tdistance_tcbuffer_cbuffer,
            tdistance_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tdistance_tcbuffer_geo(self._inner, gs)
        elif isinstance(other, Cbuffer):
            result = tdistance_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = tdistance_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[shpb.BaseGeometry, Cbuffer, STBox, TCbuffer]
    ) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` with the nearest approach distance.

        MEOS Functions:
            nad_tcbuffer_geo, nad_tcbuffer_cbuffer, nad_tcbuffer_stbox,
            nad_tcbuffer_tcbuffer
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            return nad_tcbuffer_geo(self._inner, gs)
        elif isinstance(other, Cbuffer):
            return nad_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, STBox):
            return nad_tcbuffer_stbox(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            return nad_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_instant(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> TCbufferInst:
        """
        Returns the nearest approach instant between `self` and `other`.

        Args:
            other: An object to check the nearest approach instant to.

        Returns:
            A new :class:`TCbufferInst` with the nearest approach instant.

        MEOS Functions:
            nai_tcbuffer_geo, nai_tcbuffer_cbuffer, nai_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = nai_tcbuffer_geo(self._inner, gs)
        elif isinstance(other, Cbuffer):
            result = nai_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = nai_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def shortest_line(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> shpb.BaseGeometry:
        """
        Returns the shortest line between `self` and `other`.

        Args:
            other: An object to check the shortest line to.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` with the
            shortest line.

        MEOS Functions:
            shortestline_tcbuffer_geo, shortestline_tcbuffer_cbuffer,
            shortestline_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = shortestline_tcbuffer_geo(self._inner, gs)
        elif isinstance(other, Cbuffer):
            result = shortestline_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = shortestline_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return gserialized_to_shapely_geometry(result, 10)

    # ------------------------- Ever Spatial Relationships --------------------
    def is_ever_contains(self, other: Union[shpb.BaseGeometry, Cbuffer]) -> bool:
        """
        Returns whether `self` ever contains `other`.

        MEOS Functions:
            econtains_tcbuffer_geo, econtains_tcbuffer_cbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = econtains_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = econtains_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_covers(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> bool:
        """
        Returns whether `self` ever covers `other`.

        MEOS Functions:
            ecovers_tcbuffer_geo, ecovers_tcbuffer_cbuffer,
            ecovers_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = ecovers_tcbuffer_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, Cbuffer):
            result = ecovers_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = ecovers_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_disjoint(self, other: Union[shpb.BaseGeometry, Cbuffer]) -> bool:
        """
        Returns whether `self` is ever disjoint from `other`.

        MEOS Functions:
            edisjoint_tcbuffer_geo, edisjoint_tcbuffer_cbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = edisjoint_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = edisjoint_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_ever_within_distance(
        self,
        other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer],
        distance: float,
    ) -> bool:
        """
        Returns whether `self` is ever within `distance` of `other`.

        MEOS Functions:
            edwithin_tcbuffer_geo, edwithin_tcbuffer_cbuffer,
            edwithin_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = edwithin_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False), distance
            )
        elif isinstance(other, Cbuffer):
            result = edwithin_tcbuffer_cbuffer(self._inner, other._inner, distance)
        elif isinstance(other, TCbuffer):
            result = edwithin_tcbuffer_tcbuffer(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_intersects(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> bool:
        """
        Returns whether `self` ever intersects `other`.

        MEOS Functions:
            eintersects_tcbuffer_geo, eintersects_tcbuffer_cbuffer,
            eintersects_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = eintersects_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = eintersects_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = eintersects_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def ever_touches(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> bool:
        """
        Returns whether `self` ever touches `other`.

        MEOS Functions:
            etouches_tcbuffer_geo, etouches_tcbuffer_cbuffer,
            etouches_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = etouches_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = etouches_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = etouches_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Always Spatial Relationships ------------------
    def is_always_contains(self, other: Union[shpb.BaseGeometry, Cbuffer]) -> bool:
        """
        Returns whether `self` always contains `other`.

        MEOS Functions:
            acontains_tcbuffer_geo, acontains_tcbuffer_cbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = acontains_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = acontains_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_always_covers(self, other: Union[shpb.BaseGeometry, Cbuffer]) -> bool:
        """
        Returns whether `self` always covers `other`.

        MEOS Functions:
            acovers_tcbuffer_geo, acovers_tcbuffer_cbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = acovers_tcbuffer_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, Cbuffer):
            result = acovers_tcbuffer_cbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_always_disjoint(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> bool:
        """
        Returns whether `self` is always disjoint from `other`.

        MEOS Functions:
            adisjoint_tcbuffer_geo, adisjoint_tcbuffer_cbuffer,
            adisjoint_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = adisjoint_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = adisjoint_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = adisjoint_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def is_always_within_distance(
        self,
        other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer],
        distance: float,
    ) -> bool:
        """
        Returns whether `self` is always within `distance` of `other`.

        MEOS Functions:
            adwithin_tcbuffer_geo, adwithin_tcbuffer_cbuffer,
            adwithin_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = adwithin_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False), distance
            )
        elif isinstance(other, Cbuffer):
            result = adwithin_tcbuffer_cbuffer(self._inner, other._inner, distance)
        elif isinstance(other, TCbuffer):
            result = adwithin_tcbuffer_tcbuffer(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def always_intersects(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> bool:
        """
        Returns whether `self` always intersects `other`.

        MEOS Functions:
            aintersects_tcbuffer_geo, aintersects_tcbuffer_cbuffer,
            aintersects_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = aintersects_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = aintersects_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = aintersects_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    def always_touches(
        self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]
    ) -> bool:
        """
        Returns whether `self` always touches `other`.

        MEOS Functions:
            atouches_tcbuffer_geo, atouches_tcbuffer_cbuffer,
            atouches_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = atouches_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = atouches_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = atouches_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return result == 1

    # ------------------------- Temporal Spatial Relationships ----------------
    def contains(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TBool:
        """
        Returns a temporal boolean of whether `self` contains `other`.

        MEOS Functions:
            tcontains_tcbuffer_geo, tcontains_tcbuffer_cbuffer,
            tcontains_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = tcontains_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = tcontains_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = tcontains_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def covers(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TBool:
        """
        Returns a temporal boolean of whether `self` covers `other`.

        MEOS Functions:
            tcovers_tcbuffer_geo, tcovers_tcbuffer_cbuffer,
            tcovers_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = tcovers_tcbuffer_geo(self._inner, geo_to_gserialized(other, False))
        elif isinstance(other, Cbuffer):
            result = tcovers_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = tcovers_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def disjoint(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TBool:
        """
        Returns a temporal boolean of whether `self` is disjoint from `other`.

        MEOS Functions:
            tdisjoint_tcbuffer_geo, tdisjoint_tcbuffer_cbuffer,
            tdisjoint_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = tdisjoint_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = tdisjoint_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = tdisjoint_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def within_distance(
        self,
        other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer],
        distance: float,
    ) -> TBool:
        """
        Returns a temporal boolean of whether `self` is within `distance` of
        `other`.

        MEOS Functions:
            tdwithin_tcbuffer_geo, tdwithin_tcbuffer_cbuffer,
            tdwithin_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = tdwithin_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False), distance
            )
        elif isinstance(other, Cbuffer):
            result = tdwithin_tcbuffer_cbuffer(self._inner, other._inner, distance)
        elif isinstance(other, TCbuffer):
            result = tdwithin_tcbuffer_tcbuffer(self._inner, other._inner, distance)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def intersects(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TBool:
        """
        Returns a temporal boolean of whether `self` intersects `other`.

        MEOS Functions:
            tintersects_tcbuffer_geo, tintersects_tcbuffer_cbuffer,
            tintersects_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = tintersects_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = tintersects_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = tintersects_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def touches(self, other: Union[shpb.BaseGeometry, Cbuffer, TCbuffer]) -> TBool:
        """
        Returns a temporal boolean of whether `self` touches `other`.

        MEOS Functions:
            ttouches_tcbuffer_geo, ttouches_tcbuffer_cbuffer,
            ttouches_tcbuffer_tcbuffer
        """
        if isinstance(other, shpb.BaseGeometry):
            result = ttouches_tcbuffer_geo(
                self._inner, geo_to_gserialized(other, False)
            )
        elif isinstance(other, Cbuffer):
            result = ttouches_tcbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, TCbuffer):
            result = ttouches_tcbuffer_tcbuffer(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TCbuffer` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TCbufferInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TCbufferSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TCbufferSeqSet(string=value)
            else:
                return TCbufferSeq(string=value)
        raise Exception("ERROR: Could not parse temporal circular buffer value")


class TCbufferInst(
    TInstant[Cbuffer, "TCbuffer", "TCbufferInst", "TCbufferSeq", "TCbufferSeqSet"],
    TCbuffer,
):
    """
    Class for representing temporal circular buffers at a single instant.
    """

    _make_function = lambda *args: None
    _cast_function = lambda x: None

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        _inner=None,
    ) -> None:
        super().__init__(string=string, _inner=_inner)


class TCbufferSeq(
    TSequence[Cbuffer, "TCbuffer", "TCbufferInst", "TCbufferSeq", "TCbufferSeqSet"],
    TCbuffer,
):
    """
    Class for representing temporal circular buffers over a tstzspan of time.
    """

    ComponentClass = TCbufferInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TCbufferInst]]] = None,
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


class TCbufferSeqSet(
    TSequenceSet[Cbuffer, "TCbuffer", "TCbufferInst", "TCbufferSeq", "TCbufferSeqSet"],
    TCbuffer,
):
    """
    Class for representing temporal circular buffers over a tstzspan of time
    with gaps.
    """

    ComponentClass = TCbufferSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TCbufferSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
