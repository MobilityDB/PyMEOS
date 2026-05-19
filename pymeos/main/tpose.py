from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, TYPE_CHECKING, Set, Type, TypeVar

import shapely.geometry.base as shpb
from pymeos_cffi import *

from .tbool import TBool
from .tfloat import TFloat
from .tpoint import TPoint
from ..collections import *
from ..collections.pose import Pose, PoseSet
from ..mixins import TTemporallyComparable
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation

if TYPE_CHECKING:
    from ..boxes import STBox

Self = TypeVar("Self", bound="TPose")


class TPose(
    Temporal[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"],
    TTemporallyComparable,
    ABC,
):
    """
    Abstract class for temporal poses.
    """

    _mobilitydb_name = "tpose"

    BaseClass = Pose

    _parse_function = tpose_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_tpoint_tfloat(tpoint: TPoint, tradius: TFloat) -> TPose:
        """
        Create a temporal pose from a temporal point and a temporal float
        representing the orientation.

        Args:
            tpoint: A :class:`TPoint` with the position.
            tradius: A :class:`TFloat` with the orientation.

        Returns:
            A new :class:`TPose` object.

        MEOS Functions:
            tpose_make
        """
        result = tpose_make(tpoint._inner, tradius._inner)
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
        Returns the temporal pose as a WKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal pose.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, precision)

    def as_ewkt(self, precision: int = 15) -> str:
        """
        Returns the temporal pose as an EWKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal pose.

        MEOS Functions:
            tspatial_as_ewkt
        """
        return tspatial_as_ewkt(self._inner, precision)

    # ------------------------- Conversions -----------------------------------
    def to_tpoint(self) -> TPoint:
        """
        Returns the temporal point of the positions of `self`.

        Returns:
            A new :class:`TPoint` object.

        MEOS Functions:
            tpose_to_tpoint
        """
        result = tpose_to_tpoint(self._inner)
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

    def values(self) -> List[Pose]:
        """
        Returns the values of `self`.

        Returns:
            A :class:`list` of :class:`Pose` with the values.

        MEOS Functions:
            tpose_values
        """
        values, count = tpose_values(self._inner)
        return [Pose(_inner=values[i]) for i in range(count)]

    def start_value(self) -> Pose:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`Pose` with the start value.

        MEOS Functions:
            tpose_start_value
        """
        return Pose(_inner=tpose_start_value(self._inner))

    def end_value(self) -> Pose:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`Pose` with the end value.

        MEOS Functions:
            tpose_end_value
        """
        return Pose(_inner=tpose_end_value(self._inner))

    def value_set(self) -> Set[Pose]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`Pose` with the values.

        MEOS Functions:
            tpose_values
        """
        values, count = tpose_values(self._inner)
        return {Pose(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> Pose:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`Pose` with the value.

        MEOS Functions:
            tpose_value_at_timestamptz
        """
        return Pose(
            _inner=tpose_value_at_timestamptz(
                self._inner, datetime_to_timestamptz(timestamp), True
            )[0]
        )

    def value_n(self, n: int) -> Pose:
        """
        Returns the ``n``-th value of `self`.

        Args:
            n: The 0-based index of the value to return.

        Returns:
            A :class:`Pose` with the value.

        MEOS Functions:
            tpose_value_n
        """
        return Pose(_inner=tpose_value_n(self._inner, n + 1)[0])

    def points(self) -> PoseSet:
        """
        Returns the set of points of `self`.

        Returns:
            A :class:`PoseSet` with the points.

        MEOS Functions:
            tpose_points
        """
        return PoseSet(_inner=tpose_points(self._inner))

    def trajectory(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the trajectory of `self` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` representing the
            trajectory.

        MEOS Functions:
            tpose_trajectory
        """
        return gserialized_to_shapely_geometry(
            tpose_trajectory(self._inner), precision
        )

    def rotation(self) -> TFloat:
        """
        Returns the rotation of `self` as a temporal float.

        Returns:
            A new :class:`TFloat` with the rotation.

        MEOS Functions:
            tpose_rotation
        """
        result = tpose_rotation(self._inner)
        return Temporal._factory(result)

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
        Returns a new :class:`TPose` with the given SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TPose` instance.

        MEOS Functions:
            tspatial_set_srid
        """
        return self.__class__(_inner=tspatial_set_srid(self._inner, srid))

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> TPose:
        """
        Round the coordinate values to a number of decimal places.

        Returns:
            A new :class:`TPose` object.

        MEOS Functions:
            temporal_round
        """
        result = temporal_round(self._inner, max_decimals)
        return Temporal._factory(result)

    def transform(self: Self, srid: int) -> Self:
        """
        Returns a new :class:`TPose` transformed to another SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`TPose` instance.

        MEOS Functions:
            tspatial_transform
        """
        result = tspatial_transform(self._inner, srid)
        return Temporal._factory(result)

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tpose_pose, always_eq_tpose_tpose
        """
        if isinstance(value, Pose):
            return always_eq_tpose_pose(self._inner, value._inner) > 0
        elif isinstance(value, TPose):
            return always_eq_tpose_tpose(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tpose_pose, always_ne_tpose_tpose
        """
        if isinstance(value, Pose):
            return always_ne_tpose_pose(self._inner, value._inner) > 0
        elif isinstance(value, TPose):
            return always_ne_tpose_tpose(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tpose_pose, ever_eq_tpose_tpose
        """
        if isinstance(value, Pose):
            return ever_eq_tpose_pose(self._inner, value._inner) > 0
        elif isinstance(value, TPose):
            return ever_eq_tpose_tpose(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tpose_pose, ever_ne_tpose_tpose
        """
        if isinstance(value, Pose):
            return ever_ne_tpose_pose(self._inner, value._inner) > 0
        elif isinstance(value, TPose):
            return ever_ne_tpose_tpose(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tpose_pose, ever_eq_tpose_tpose
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[Pose, TPose]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`Pose` or :class:`TPose` to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tpose_pose, ever_ne_tpose_tpose
        """
        return not self.ever_not_equal(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[Pose, TPose]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A :class:`Pose` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tpose_pose, teq_temporal_temporal
        """
        if isinstance(other, Pose):
            result = teq_tpose_pose(self._inner, other._inner)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[Pose, TPose]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A :class:`Pose` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal
            relation.

        MEOS Functions:
            tne_tpose_pose, tne_temporal_temporal
        """
        if isinstance(other, Pose):
            result = tne_tpose_pose(self._inner, other._inner)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Union[Pose, shpb.BaseGeometry, STBox, Time]) -> TPose:
        """
        Returns a new temporal pose with the values of `self` restricted to
        `other`.

        Args:
            other: An object to restrict the values of `self` to.

        Returns:
            A new :class:`TPose` with the values of `self` restricted to
            `other`.

        MEOS Functions:
            tpose_at_pose, tpose_at_geom, tpose_at_stbox,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Pose):
            result = tpose_at_pose(self._inner, other._inner)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tpose_at_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tpose_at_stbox(self._inner, other._inner, True)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[Pose, shpb.BaseGeometry, STBox, Time]) -> TPose:
        """
        Returns a new temporal pose with the values of `self` restricted to
        the complement of `other`.

        Args:
            other: An object to restrict the values of `self` to the
            complement of.

        Returns:
            A new :class:`TPose` with the values of `self` restricted to the
            complement of `other`.

        MEOS Functions:
            tpose_minus_pose, tpose_minus_geom, tpose_minus_stbox,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        from ..boxes import STBox

        if isinstance(other, Pose):
            result = tpose_minus_pose(self._inner, other._inner)
        elif isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tpose_minus_geom(self._inner, gs)
        elif isinstance(other, STBox):
            result = tpose_minus_stbox(self._inner, other._inner, True)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[shpb.BaseGeometry, Pose, TPose]) -> TFloat:
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: An object to check the distance to.

        Returns:
            A new :class:`TFloat` with the temporal distance.

        MEOS Functions:
            tdistance_tpose_point, tdistance_tpose_pose, tdistance_tpose_tpose
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = tdistance_tpose_point(self._inner, gs)
        elif isinstance(other, Pose):
            result = tdistance_tpose_pose(self._inner, other._inner)
        elif isinstance(other, TPose):
            result = tdistance_tpose_tpose(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[shpb.BaseGeometry, Pose, STBox, TPose]
    ) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: An object to check the nearest approach distance to.

        Returns:
            A :class:`float` with the nearest approach distance.

        MEOS Functions:
            nad_tpose_geo, nad_tpose_pose, nad_tpose_stbox, nad_tpose_tpose
        """
        from ..boxes import STBox

        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            return nad_tpose_geo(self._inner, gs)
        elif isinstance(other, Pose):
            return nad_tpose_pose(self._inner, other._inner)
        elif isinstance(other, STBox):
            return nad_tpose_stbox(self._inner, other._inner)
        elif isinstance(other, TPose):
            return nad_tpose_tpose(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_instant(
        self, other: Union[shpb.BaseGeometry, Pose, TPose]
    ) -> TPoseInst:
        """
        Returns the nearest approach instant between `self` and `other`.

        Args:
            other: An object to check the nearest approach instant to.

        Returns:
            A new :class:`TPoseInst` with the nearest approach instant.

        MEOS Functions:
            nai_tpose_geo, nai_tpose_pose, nai_tpose_tpose
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = nai_tpose_geo(self._inner, gs)
        elif isinstance(other, Pose):
            result = nai_tpose_pose(self._inner, other._inner)
        elif isinstance(other, TPose):
            result = nai_tpose_tpose(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def shortest_line(
        self, other: Union[shpb.BaseGeometry, Pose, TPose]
    ) -> shpb.BaseGeometry:
        """
        Returns the shortest line between `self` and `other`.

        Args:
            other: An object to check the shortest line to.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` with the
            shortest line.

        MEOS Functions:
            shortestline_tpose_geo, shortestline_tpose_pose,
            shortestline_tpose_tpose
        """
        if isinstance(other, shpb.BaseGeometry):
            gs = geo_to_gserialized(other, False)
            result = shortestline_tpose_geo(self._inner, gs)
        elif isinstance(other, Pose):
            result = shortestline_tpose_pose(self._inner, other._inner)
        elif isinstance(other, TPose):
            result = shortestline_tpose_tpose(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return gserialized_to_shapely_geometry(result, 10)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TPose` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TPoseInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TPoseSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TPoseSeqSet(string=value)
            else:
                return TPoseSeq(string=value)
        raise Exception("ERROR: Could not parse temporal pose value")


class TPoseInst(TInstant[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"], TPose):
    """
    Class for representing temporal poses at a single instant.
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


class TPoseSeq(TSequence[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"], TPose):
    """
    Class for representing temporal poses over a tstzspan of time.
    """

    ComponentClass = TPoseInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TPoseInst]]] = None,
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


class TPoseSeqSet(
    TSequenceSet[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"], TPose
):
    """
    Class for representing temporal poses over a tstzspan of time with gaps.
    """

    ComponentClass = TPoseSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TPoseSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
