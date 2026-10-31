from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar, overload

import shapely.geometry.base as shp
from pymeos_cffi import *

from ..collections import *
from ..collections.npoint import Npoint, Nsegment
from ..mixins import TSpatialIO, TTemporallyComparable
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.tnpoint_methods import TNpointRegularMixin

if TYPE_CHECKING:
    from ..boxes import STBox
    from .tfloat import TFloat
    from .tpoint import TGeomPoint


Self = TypeVar("Self", bound="TNpoint")


class TNpoint(
    TNpointRegularMixin,
    Temporal[Npoint, "TNpoint", "TNpointInst", "TNpointSeq", "TNpointSeqSet"],
    TTemporallyComparable,
    TSpatialIO,
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
    @staticmethod
    def from_base_temporal(value: Npoint, base: Temporal) -> TNpoint:
        """
        Create a temporal network point from a network point and the time frame of another
        temporal object.

        Args:
            value: Npoint value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TNpoint` object.

        MEOS Functions:
            tnpoint_from_base_temp
        """
        result = tnpoint_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: Npoint, base: datetime, interpolation: None = None) -> TNpointInst: ...

    @staticmethod
    @overload
    def from_base_time(value: Npoint, base: TsTzSet, interpolation: None = None) -> TNpointSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Npoint, base: TsTzSpan, interpolation: TInterpolation = None) -> TNpointSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Npoint, base: TsTzSpanSet, interpolation: TInterpolation = None) -> TNpointSeqSet: ...

    @staticmethod
    def from_base_time(value: Npoint, base: Time, interpolation: TInterpolation = None) -> TNpoint:
        """
        Create a temporal network point from a network point and a time object.

        Args:
            value: Npoint value.
            base: Time object to use as temporal dimension.
            interpolation: Interpolation of the temporal network point.

        Returns:
            A new temporal network point.

        MEOS Functions:
            tnpointinst_make, tnpointseq_from_base_tstzset,
            tnpointseq_from_base_tstzspan, tnpointseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TNpointInst(_inner=tnpointinst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TNpointSeq(_inner=tnpointseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TNpointSeq(_inner=tnpointseq_from_base_tstzspan(value._inner, base._inner, interpolation))
        elif isinstance(base, TsTzSpanSet):
            return TNpointSeqSet(_inner=tnpointseqset_from_base_tstzspanset(value._inner, base._inner, interpolation))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal network point from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal network point.

        MEOS Functions:
            tnpoint_from_mfjson
        """
        result = tnpoint_from_mfjson(mfjson)
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
            A string with the string representation of `self`.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the Well-Known Text representation of `self`.

        Returns:
            A string with the Well-Known Text representation of `self`.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, max_decimals)

    # ------------------------- Value Accessors -------------------------------
    def start_value(self) -> Npoint:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`Npoint` with the start value.

        MEOS Functions:
            tnpoint_start_value
        """
        return Npoint(_inner=tnpoint_start_value(self._inner))

    def end_value(self) -> Npoint:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`Npoint` with the end value.

        MEOS Functions:
            tnpoint_end_value
        """
        return Npoint(_inner=tnpoint_end_value(self._inner))

    def value_set(self) -> set[Npoint]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`Npoint` with the values.

        MEOS Functions:
            tnpoint_values
        """
        values, count = tnpoint_values(self._inner)
        return {Npoint(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> Npoint:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`Npoint` with the value.

        MEOS Functions:
            tnpoint_value_at_timestamptz
        """
        _, value = tnpoint_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True)
        return Npoint(_inner=value)

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
        return gserialized_to_shapely_geometry(tnpoint_trajectory(self._inner), precision)

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
        return gserialized_to_shapely_geometry(tnpoint_twcentroid(self._inner), precision)

    def positions(self) -> list[Nsegment]:
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
    def never_equal(self, value: Npoint | TNpoint) -> bool:
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

    def never_not_equal(self, value: Npoint | TNpoint) -> bool:
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
    # ------------------------- Distance Operations ---------------------------
    # ------------------------- Restrictions ----------------------------------
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
        string: str | None = None,
        *,
        value: str | Npoint | None = None,
        timestamp: str | datetime | None = None,
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
        string: str | None = None,
        *,
        instant_list: list[str | TNpointInst] | None = None,
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
        string: str | None = None,
        *,
        sequence_list: list[str | TNpointSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
