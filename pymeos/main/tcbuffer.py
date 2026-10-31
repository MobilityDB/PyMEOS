from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar, overload

import shapely.geometry.base as shpb
from pymeos_cffi import *

from ..collections import *
from ..collections.cbuffer import Cbuffer, CbufferSet
from ..mixins import TSpatialIO, TTemporallyComparable
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.tcbuffer_methods import TCbufferRegularMixin
from .tfloat import TFloat
from .tpoint import TPoint

if TYPE_CHECKING:
    from ..boxes import STBox

Self = TypeVar("Self", bound="TCbuffer")


class TCbuffer(
    TCbufferRegularMixin,
    Temporal[Cbuffer, "TCbuffer", "TCbufferInst", "TCbufferSeq", "TCbufferSeqSet"],
    TTemporallyComparable,
    TSpatialIO,
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
            tcbuffer_traversed_area
        """
        return gserialized_to_shapely_geometry(tcbuffer_traversed_area(self._inner), 15)

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
    def start_value(self) -> Cbuffer:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`Cbuffer` with the start value.

        MEOS Functions:
            tcbuffer_start_value
        """
        return Cbuffer(_inner=tcbuffer_start_value(self._inner))

    def end_value(self) -> Cbuffer:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`Cbuffer` with the end value.

        MEOS Functions:
            tcbuffer_end_value
        """
        return Cbuffer(_inner=tcbuffer_end_value(self._inner))

    def value_set(self) -> set[Cbuffer]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`Cbuffer` with the values.

        MEOS Functions:
            tcbuffer_values
        """
        values, count = tcbuffer_values(self._inner)
        return {Cbuffer(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> Cbuffer:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`Cbuffer` with the value.

        MEOS Functions:
            tcbuffer_value_at_timestamptz
        """
        _, value = tcbuffer_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True)
        return Cbuffer(_inner=value)

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: Cbuffer, base: Temporal) -> TCbuffer:
        """
        Create a temporal circular buffer from a circular buffer and the time frame of another
        temporal object.

        Args:
            value: Cbuffer value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TCbuffer` object.

        MEOS Functions:
            tcbuffer_from_base_temp
        """
        result = tcbuffer_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: Cbuffer, base: datetime, interpolation: None = None) -> TCbufferInst: ...

    @staticmethod
    @overload
    def from_base_time(value: Cbuffer, base: TsTzSet, interpolation: None = None) -> TCbufferSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Cbuffer, base: TsTzSpan, interpolation: TInterpolation = None) -> TCbufferSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Cbuffer, base: TsTzSpanSet, interpolation: TInterpolation = None) -> TCbufferSeqSet: ...

    @staticmethod
    def from_base_time(value: Cbuffer, base: Time, interpolation: TInterpolation = None) -> TCbuffer:
        """
        Create a temporal circular buffer from a circular buffer and a time object.

        Args:
            value: Cbuffer value.
            base: Time object to use as temporal dimension.
            interpolation: Interpolation of the temporal circular buffer.

        Returns:
            A new temporal circular buffer.

        MEOS Functions:
            tcbufferinst_make, tcbufferseq_from_base_tstzset,
            tcbufferseq_from_base_tstzspan, tcbufferseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TCbufferInst(_inner=tcbufferinst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TCbufferSeq(_inner=tcbufferseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TCbufferSeq(_inner=tcbufferseq_from_base_tstzspan(value._inner, base._inner, interpolation))
        elif isinstance(base, TsTzSpanSet):
            return TCbufferSeqSet(_inner=tcbufferseqset_from_base_tstzspanset(value._inner, base._inner, interpolation))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal circular buffer from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal circular buffer.

        MEOS Functions:
            tcbuffer_from_mfjson
        """
        result = tcbuffer_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Ever and Always Comparisons -------------------
    def never_equal(self, value: Cbuffer | TCbuffer) -> bool:
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

    def never_not_equal(self, value: Cbuffer | TCbuffer) -> bool:
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
    # ------------------------- Restrictions ----------------------------------
    # ------------------------- Distance Operations ---------------------------
    # ------------------------- Ever Spatial Relationships --------------------
    def is_ever_contained_in(self, container: shpb.BaseGeometry | Cbuffer) -> bool:
        """
        Returns whether `self` is ever contained by `container`, as
        #TPoint.is_ever_contained_in.

        MEOS Functions:
            econtains_geo_tcbuffer, econtains_cbuffer_tcbuffer
        """
        if isinstance(container, shpb.BaseGeometry):
            result = econtains_geo_tcbuffer(geo_to_gserialized(container, False), self._inner)
        elif isinstance(container, Cbuffer):
            result = econtains_cbuffer_tcbuffer(container._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_ever_coveredby(self, container: shpb.BaseGeometry | Cbuffer) -> bool:
        """
        Returns whether `self` is ever covered by `container`: the covers
        relationship with `container` first, as #TCbuffer.is_ever_contained_in
        is for contains and as PostGIS's coveredby is for covers.

        MEOS Functions:
            ecovers_geo_tcbuffer, ecovers_cbuffer_tcbuffer
        """
        if isinstance(container, shpb.BaseGeometry):
            result = ecovers_geo_tcbuffer(geo_to_gserialized(container, False), self._inner)
        elif isinstance(container, Cbuffer):
            result = ecovers_cbuffer_tcbuffer(container._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    # ------------------------- Always Spatial Relationships ------------------
    def is_always_contained_in(self, container: shpb.BaseGeometry | Cbuffer) -> bool:
        """
        Returns whether `self` is always contained by `container`, as
        #TPoint.is_ever_contained_in for the ever relationship.

        MEOS Functions:
            acontains_geo_tcbuffer, acontains_cbuffer_tcbuffer
        """
        if isinstance(container, shpb.BaseGeometry):
            result = acontains_geo_tcbuffer(geo_to_gserialized(container, False), self._inner)
        elif isinstance(container, Cbuffer):
            result = acontains_cbuffer_tcbuffer(container._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    def is_always_coveredby(self, container: shpb.BaseGeometry | Cbuffer) -> bool:
        """
        Returns whether `self` is always covered by `container`: the covers
        relationship with `container` first, as
        #TCbuffer.is_always_contained_in is for contains.

        MEOS Functions:
            acovers_geo_tcbuffer, acovers_cbuffer_tcbuffer
        """
        if isinstance(container, shpb.BaseGeometry):
            result = acovers_geo_tcbuffer(geo_to_gserialized(container, False), self._inner)
        elif isinstance(container, Cbuffer):
            result = acovers_cbuffer_tcbuffer(container._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")
        return result == 1

    # ------------------------- Temporal Spatial Relationships ----------------
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
        string: str | None = None,
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
        string: str | None = None,
        *,
        instant_list: list[str | TCbufferInst] | None = None,
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
        string: str | None = None,
        *,
        sequence_list: list[str | TCbufferSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
