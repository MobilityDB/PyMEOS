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
from ._generated.tcbuffer_methods import TCbufferRegularMixin

if TYPE_CHECKING:
    from .tbool import TBool
    from ..boxes import STBox

Self = TypeVar("Self", bound="TCbuffer")


class TCbuffer(
    TCbufferRegularMixin,
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
    # ------------------------- Restrictions ----------------------------------
    # ------------------------- Distance Operations ---------------------------
    # ------------------------- Ever Spatial Relationships --------------------
    # ------------------------- Always Spatial Relationships ------------------
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
