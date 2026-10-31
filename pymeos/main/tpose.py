from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar, overload

import shapely.geometry.base as shpb
from pymeos_cffi import *

from ..collections import *
from ..collections.pose import Pose, PoseSet
from ..mixins import TSpatialIO, TTemporallyComparable
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.tpose_methods import TPoseRegularMixin
from .tfloat import TFloat
from .tpoint import TPoint

if TYPE_CHECKING:
    from ..boxes import STBox

Self = TypeVar("Self", bound="TPose")


class TPose(
    TPoseRegularMixin,
    Temporal[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"],
    TTemporallyComparable,
    TSpatialIO,
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
    def from_base_temporal(value: Pose, base: Temporal) -> TPose:
        """
        Create a temporal pose from a pose and the time frame of another
        temporal object.

        Args:
            value: Pose value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TPose` object.

        MEOS Functions:
            tpose_from_base_temp
        """
        result = tpose_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: Pose, base: datetime, interpolation: None = None) -> TPoseInst: ...

    @staticmethod
    @overload
    def from_base_time(value: Pose, base: TsTzSet, interpolation: None = None) -> TPoseSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Pose, base: TsTzSpan, interpolation: TInterpolation = None) -> TPoseSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Pose, base: TsTzSpanSet, interpolation: TInterpolation = None) -> TPoseSeqSet: ...

    @staticmethod
    def from_base_time(value: Pose, base: Time, interpolation: TInterpolation = None) -> TPose:
        """
        Create a temporal pose from a pose and a time object.

        Args:
            value: Pose value.
            base: Time object to use as temporal dimension.
            interpolation: Interpolation of the temporal pose.

        Returns:
            A new temporal pose.

        MEOS Functions:
            tposeinst_make, tposeseq_from_base_tstzset,
            tposeseq_from_base_tstzspan, tposeseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TPoseInst(_inner=tposeinst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TPoseSeq(_inner=tposeseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TPoseSeq(_inner=tposeseq_from_base_tstzspan(value._inner, base._inner, interpolation))
        elif isinstance(base, TsTzSpanSet):
            return TPoseSeqSet(_inner=tposeseqset_from_base_tstzspanset(value._inner, base._inner, interpolation))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal pose from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal pose.

        MEOS Functions:
            tpose_from_mfjson
        """
        result = tpose_from_mfjson(mfjson)
        return Temporal._factory(result)

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
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, max_decimals)

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

    def values(self) -> list[Pose]:
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

    def value_set(self) -> set[Pose]:
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
        return Pose(_inner=tpose_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True)[0])

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

    def yaw(self) -> TFloat:
        """
        Returns the rotation of `self` as a temporal float.

        Returns:
            A new :class:`TFloat` with the rotation.

        MEOS Functions:
            tpose_yaw
        """
        result = tpose_yaw(self._inner)
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
    def never_equal(self, value: Pose | TPose) -> bool:
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

    def never_not_equal(self, value: Pose | TPose) -> bool:
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
    # ------------------------- Restrictions ----------------------------------
    # ------------------------- Distance Operations ---------------------------
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
        string: str | None = None,
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
        string: str | None = None,
        *,
        instant_list: list[str | TPoseInst] | None = None,
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


class TPoseSeqSet(TSequenceSet[Pose, "TPose", "TPoseInst", "TPoseSeq", "TPoseSeqSet"], TPose):
    """
    Class for representing temporal poses over a tstzspan of time with gaps.
    """

    ComponentClass = TPoseSeq

    def __init__(
        self,
        string: str | None = None,
        *,
        sequence_list: list[str | TPoseSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
