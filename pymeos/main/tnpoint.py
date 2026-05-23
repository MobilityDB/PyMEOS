from __future__ import annotations

from abc import ABC
from typing import Optional, Union, List, TYPE_CHECKING, TypeVar

import shapely.geometry.base as shp
from pymeos_cffi import *

from ..collections import *
from ..collections.npoint import Npoint, NpointSet, Nsegment
from ..mixins import TTemporallyComparable
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet

if TYPE_CHECKING:
    from .tbool import TBool
    from .tfloat import TFloat
    from .tpoint import TGeomPoint
    from ..boxes import STBox


Self = TypeVar("Self", bound="TNpoint")


class TNpoint(
    Temporal[Npoint, "TNpoint", "TNpointInst", "TNpointSeq", "TNpointSeqSet"],
    TTemporallyComparable,
    ABC,
):
    """
    Abstract class for temporal network points.
    """

    _mobilitydb_name = "tnpoint"

    BaseClass = Npoint

    _parse_function = tnpoint_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15) -> str:
        """
        Returns the string representation of `self`.

        Returns:
            A string with the string representation of `self`.

        MEOS Functions:
            tnpoint_out
        """
        return tnpoint_out(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the Well-Known Text representation of `self`.

        Returns:
            A string with the Well-Known Text representation of `self`.

        MEOS Functions:
            tnpoint_out
        """
        return tnpoint_out(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------
    def to_tgeompoint(self) -> TGeomPoint:
        """
        Returns a temporal geometric point equivalent to `self`.

        Returns:
            A new :class:`TGeomPoint` instance.

        MEOS Functions:
            tnpoint_to_tgeompoint
        """
        result = tnpoint_to_tgeompoint(self._inner)
        return Temporal._factory(result)

    @staticmethod
    def from_tgeompoint(temporal: TGeomPoint) -> TNpoint:
        """
        Returns a temporal network point equivalent to a temporal geometric
        point.

        Args:
            temporal: A :class:`TGeomPoint` instance.

        Returns:
            A new :class:`TNpoint` instance.

        MEOS Functions:
            tgeompoint_to_tnpoint
        """
        result = tgeompoint_to_tnpoint(temporal._inner)
        return Temporal._factory(result)

    # ------------------------- Accessors -------------------------------------
    def bounding_box(self) -> STBox:
        """
        Returns the bounding box of `self`.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            tspatial_to_stbox
        """
        from ..boxes import STBox

        return STBox(_inner=tspatial_to_stbox(self._inner))

    def route(self) -> int:
        """
        Returns the route identifier of `self`. Only defined when `self` stays
        on a single route.

        Returns:
            An :class:`int` with the route identifier.

        MEOS Functions:
            tnpoint_route
        """
        return tnpoint_route(self._inner)

    def routes(self) -> Set[int]:
        """
        Returns the set of route identifiers of `self`.

        Returns:
            A :class:`Set` instance with the route identifiers.

        MEOS Functions:
            tnpoint_routes
        """
        from ..factory import _CollectionFactory

        return _CollectionFactory.create_collection(tnpoint_routes(self._inner))

    def length(self) -> float:
        """
        Returns the length of the trajectory of `self`.

        Returns:
            A :class:`float` with the length.

        MEOS Functions:
            tnpoint_length
        """
        return tnpoint_length(self._inner)

    def cumulative_length(self) -> TFloat:
        """
        Returns the cumulative length of the trajectory of `self`.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tnpoint_cumulative_length
        """
        result = tnpoint_cumulative_length(self._inner)
        return Temporal._factory(result)

    def speed(self) -> TFloat:
        """
        Returns the speed of `self`.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tnpoint_speed
        """
        result = tnpoint_speed(self._inner)
        return Temporal._factory(result)

    def trajectory(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the trajectory of `self`.

        Args:
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            tnpoint_trajectory
        """
        return gserialized_to_shapely_geometry(
            tnpoint_trajectory(self._inner), precision
        )

    def time_weighted_centroid(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the time weighted centroid of `self`.

        Args:
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            tnpoint_twcentroid
        """
        return gserialized_to_shapely_geometry(
            tnpoint_twcentroid(self._inner), precision
        )

    def positions(self) -> List[Nsegment]:
        """
        Returns the network segments covered by `self`.

        Returns:
            A :class:`list` of :class:`Nsegment` with the positions.

        MEOS Functions:
            tnpoint_positions
        """
        nss, count = tnpoint_positions(self._inner)
        return [Nsegment(_inner=nss[i]) for i in range(count)]

    # ------------------------- Spatial Reference System ----------------------
    def srid(self) -> int:
        """
        Returns the SRID of `self`.

        Returns:
            An :class:`int` with the SRID of `self`.

        MEOS Functions:
            tspatial_srid
        """
        return tspatial_srid(self._inner)

    def set_srid(self: Self, srid: int) -> Self:
        """
        Returns a copy of `self` with the SRID set to `srid`.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TNpoint` instance.

        MEOS Functions:
            tspatial_set_srid
        """
        return self.__class__(_inner=tspatial_set_srid(self._inner, srid))

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tnpoint_npoint, always_eq_tnpoint_tnpoint
        """
        if isinstance(value, Npoint):
            return always_eq_tnpoint_npoint(self._inner, value._inner) > 0
        elif isinstance(value, TNpoint):
            return always_eq_tnpoint_tnpoint(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tnpoint_npoint, always_ne_tnpoint_tnpoint
        """
        if isinstance(value, Npoint):
            return always_ne_tnpoint_npoint(self._inner, value._inner) > 0
        elif isinstance(value, TNpoint):
            return always_ne_tnpoint_tnpoint(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tnpoint_npoint, ever_eq_tnpoint_tnpoint
        """
        if isinstance(value, Npoint):
            return ever_eq_tnpoint_npoint(self._inner, value._inner) > 0
        elif isinstance(value, TNpoint):
            return ever_eq_tnpoint_tnpoint(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tnpoint_npoint, ever_ne_tnpoint_tnpoint
        """
        if isinstance(value, Npoint):
            return ever_ne_tnpoint_npoint(self._inner, value._inner) > 0
        elif isinstance(value, TNpoint):
            return ever_ne_tnpoint_tnpoint(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tnpoint_npoint, ever_eq_tnpoint_tnpoint
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[Npoint, TNpoint]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`Npoint` or :class:`TNpoint` to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tnpoint_npoint, ever_ne_tnpoint_tnpoint
        """
        return not self.ever_not_equal(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[Npoint, TNpoint]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: An :class:`Npoint` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tnpoint_npoint, teq_temporal_temporal
        """
        if isinstance(other, Npoint):
            result = teq_tnpoint_npoint(self._inner, other._inner)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[Npoint, TNpoint]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: An :class:`Npoint` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal
            relation.

        MEOS Functions:
            tne_tnpoint_npoint, tne_temporal_temporal
        """
        if isinstance(other, Npoint):
            result = tne_tnpoint_npoint(self._inner, other._inner)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Distance Operations ---------------------------
    def distance(
        self, other: Union[shp.BaseGeometry, Npoint, TNpoint]
    ) -> TFloat:
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tdistance_tnpoint_point, tdistance_tnpoint_npoint,
            tdistance_tnpoint_tnpoint
        """
        if isinstance(other, Npoint):
            result = tdistance_tnpoint_npoint(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tdistance_tnpoint_point(self._inner, gs)
        elif isinstance(other, TNpoint):
            result = tdistance_tnpoint_tnpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[shp.BaseGeometry, Npoint, STBox, TNpoint]
    ) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` with the nearest approach distance.

        MEOS Functions:
            nad_tnpoint_geo, nad_tnpoint_npoint, nad_tnpoint_stbox,
            nad_tnpoint_tnpoint
        """
        from ..boxes import STBox

        if isinstance(other, Npoint):
            return nad_tnpoint_npoint(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            return nad_tnpoint_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_tnpoint_stbox(self._inner, other._inner)
        elif isinstance(other, TNpoint):
            return nad_tnpoint_tnpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_instant(
        self, other: Union[shp.BaseGeometry, Npoint, TNpoint]
    ) -> TNpointInst:
        """
        Returns the nearest approach instant between `self` and `other`.

        Args:
            other: An object to check the nearest approach instant to.

        Returns:
            A new :class:`TNpointInst` instance.

        MEOS Functions:
            nai_tnpoint_geo, nai_tnpoint_npoint, nai_tnpoint_tnpoint
        """
        if isinstance(other, Npoint):
            result = nai_tnpoint_npoint(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = nai_tnpoint_geo(self._inner, gs)
        elif isinstance(other, TNpoint):
            result = nai_tnpoint_tnpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def shortest_line(
        self, other: Union[shp.BaseGeometry, Npoint, TNpoint], precision: int = 15
    ) -> shp.BaseGeometry:
        """
        Returns the shortest line between `self` and `other`.

        Args:
            other: An object to check the shortest line to.
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            shortestline_tnpoint_geo, shortestline_tnpoint_npoint,
            shortestline_tnpoint_tnpoint
        """
        if isinstance(other, Npoint):
            result = shortestline_tnpoint_npoint(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = shortestline_tnpoint_geo(self._inner, gs)
        elif isinstance(other, TNpoint):
            result = shortestline_tnpoint_tnpoint(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return gserialized_to_shapely_geometry(result, precision)

    # ------------------------- Restrictions ----------------------------------
    def at(
        self, other: Union[shp.BaseGeometry, Npoint, NpointSet, STBox, Time]
    ) -> TNpoint:
        """
        Returns a new temporal network point with the values of `self`
        restricted to `other`.

        Args:
            other: An object to restrict the values of `self` to.

        Returns:
            A new :class:`TNpoint` instance.

        MEOS Functions:
            tnpoint_at_geom, tnpoint_at_npoint, tnpoint_at_npointset,
            tnpoint_at_stbox, temporal_at_timestamp, temporal_at_tstzset,
            temporal_at_tstzspan, temporal_at_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Npoint):
            result = tnpoint_at_npoint(self._inner, other._inner)
        elif isinstance(other, NpointSet):
            result = tnpoint_at_npointset(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tnpoint_at_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tnpoint_at_stbox(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self, other: Union[shp.BaseGeometry, Npoint, NpointSet, STBox, Time]
    ) -> TNpoint:
        """
        Returns a new temporal network point with the values of `self`
        restricted to the complement of `other`.

        Args:
            other: An object to restrict the values of `self` to the
            complement of.

        Returns:
            A new :class:`TNpoint` instance.

        MEOS Functions:
            tnpoint_minus_geom, tnpoint_minus_npoint, tnpoint_minus_npointset,
            tnpoint_minus_stbox, temporal_minus_timestamp,
            temporal_minus_tstzset, temporal_minus_tstzspan,
            temporal_minus_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Npoint):
            result = tnpoint_minus_npoint(self._inner, other._inner)
        elif isinstance(other, NpointSet):
            result = tnpoint_minus_npointset(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            gs = geometry_to_gserialized(other)
            result = tnpoint_minus_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tnpoint_minus_stbox(self._inner, other._inner, True)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TNpoint` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value.startswith("Interp=Stepwise;"):
            value1 = value.replace("Interp=Stepwise;", "")
            if value1[0] == "{":
                return TNpointSeqSet(string=value)
            else:
                return TNpointSeq(string=value)
        elif value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TNpointInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TNpointSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TNpointSeqSet(string=value)
            else:
                return TNpointSeq(string=value)
        raise Exception("ERROR: Could not parse temporal network point value")


class TNpointInst(
    TInstant[Npoint, "TNpoint", "TNpointInst", "TNpointSeq", "TNpointSeqSet"],
    TNpoint,
):
    """
    Class for representing temporal network points at a single instant.
    """

    _make_function = tnpointinst_make
    _cast_function = lambda x: x._inner

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        value: Optional[Union[str, Npoint]] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TNpointSeq(
    TSequence[Npoint, "TNpoint", "TNpointInst", "TNpointSeq", "TNpointSeqSet"],
    TNpoint,
):
    """
    Class for representing temporal network points over a tstzspan of time.
    """

    ComponentClass = TNpointInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TNpointInst]]] = None,
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


class TNpointSeqSet(
    TSequenceSet[Npoint, "TNpoint", "TNpointInst", "TNpointSeq", "TNpointSeqSet"],
    TNpoint,
):
    """
    Class for representing temporal network points over a tstzspan of time
    with gaps.
    """

    ComponentClass = TNpointSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TNpointSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
