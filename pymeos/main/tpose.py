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
from ._generated.tpose_methods import TPoseRegularMixin

if TYPE_CHECKING:
    from ..boxes import STBox

Self = TypeVar("Self", bound="TPose")


class TPose(
    TPoseRegularMixin,
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

    # ------------------------- Value Constructors ----------------------------
    # The value accessors below (start_value/end_value/value_set/
    # value_at_timestamp/value_n) are MEOS-backed and implemented. MEOS does
    # not yet export a value-based / MF-JSON constructor for the temporal
    # pose; these two overrides keep the class concrete and fail loudly
    # instead of making the whole type uninstantiable. Tracked upstream:
    # from_base_time -> MobilityDB#1084 (from-base time family),
    # from_mfjson   -> MobilityDB#1085 (export tpose_from_mfjson).
    @staticmethod
    def from_base_time(value: Pose, base: Time) -> TPose:
        """Pending upstream (MobilityDB#1084)."""
        raise NotImplementedError(
            "MEOS does not yet export a value-based constructor for the "
            "temporal pose (tpose_from_base_*); tracked by MobilityDB#1084."
        )

    @classmethod
    def from_mfjson(cls, mfjson: str) -> TPose:
        """Pending upstream (MobilityDB#1085)."""
        raise NotImplementedError(
            "MEOS does not yet export MF-JSON input for the temporal pose "
            "(tpose_from_mfjson); tracked by MobilityDB#1085."
        )

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
        return gserialized_to_shapely_geometry(tpose_trajectory(self._inner), precision)

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
