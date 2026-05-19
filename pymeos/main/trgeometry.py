from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, TYPE_CHECKING, Set, TypeVar

import shapely.geometry.base as shpb
from pymeos_cffi import *

from .tbool import TBool
from .tfloat import TFloat
from .tpoint import TPoint
from ..collections import *
from ..collections.pose import Pose
from ..mixins import TTemporallyComparable
from ..temporal import Temporal, TInstant, TSequence, TSequenceSet, TInterpolation
from ._generated.trgeometry_methods import TRgeometryRegularMixin

if TYPE_CHECKING:
    from ..boxes import STBox
    from .tpose import TPose

Self = TypeVar("Self", bound="TRgeometry")


class TRgeometry(
    TRgeometryRegularMixin,
    Temporal[
        shpb.BaseGeometry,
        "TRgeometry",
        "TRgeometryInst",
        "TRgeometrySeq",
        "TRgeometrySeqSet",
    ],
    TTemporallyComparable,
    ABC,
):
    """
    Abstract class for temporal rigid geometries.
    """

    _mobilitydb_name = "trgeometry"

    BaseClass = shpb.BaseGeometry

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
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
            geo_tpose_to_trgeo
        """
        gs = geometry_to_gserialized(geometry)
        result = geo_tpose_to_trgeo(gs, tpose._inner)
        return Temporal._factory(result)

    # MEOS does not export a value-based or MF-JSON constructor for the
    # temporal rigid geometry. These overrides keep TRgeometry/Inst/Seq/
    # SeqSet concrete and fail loudly instead of making the type
    # uninstantiable; both are pending upstream MEOS work.
    @staticmethod
    def from_base_time(value: shpb.BaseGeometry, base: Time) -> TRgeometry:
        """Pending upstream (MEOS trgeometry from-base not exported)."""
        raise NotImplementedError(
            "MEOS does not export a value-based constructor for the "
            "temporal rigid geometry (trgeometry from-base); pending "
            "upstream."
        )

    @classmethod
    def from_mfjson(cls, mfjson: str) -> TRgeometry:
        """Pending upstream (MEOS trgeometry MF-JSON not exported)."""
        raise NotImplementedError(
            "MEOS does not export MF-JSON input for the temporal rigid "
            "geometry (trgeometry_from_mfjson); pending upstream."
        )

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns the string representation of `self`.

        Returns:
            A :class:`str` with the string representation of `self`.

        MEOS Functions:
            trgeo_out
        """
        return trgeo_out(self._inner)

    def as_wkt(self, precision: int = 15) -> str:
        """
        Returns the temporal rigid geometry as a WKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal rigid geometry.

        MEOS Functions:
            tspatial_as_text
        """
        return tspatial_as_text(self._inner, precision)

    def as_ewkt(self, precision: int = 15) -> str:
        """
        Returns the temporal rigid geometry as an EWKT string.

        Args:
            precision: The precision of the returned geometry.

        Returns:
            A new :class:`str` representing the temporal rigid geometry.

        MEOS Functions:
            tspatial_as_ewkt
        """
        return tspatial_as_ewkt(self._inner, precision)

    # ------------------------- Conversions -----------------------------------
    def to_tpose(self) -> TPose:
        """
        Returns the temporal pose of `self`.

        Returns:
            A new :class:`TPose` object.

        MEOS Functions:
            trgeo_to_tpose
        """
        result = trgeo_to_tpose(self._inner)
        return Temporal._factory(result)

    def to_tpoint(self) -> TPoint:
        """
        Returns the temporal point of the positions of `self`.

        Returns:
            A new :class:`TPoint` object.

        MEOS Functions:
            trgeo_to_tpoint
        """
        result = trgeo_to_tpoint(self._inner)
        return Temporal._factory(result)

    def to_instant(self) -> "TRgeometryInst":
        """
        Returns `self` as a :class:`TRgeometryInst`.

        MEOS Functions:
            trgeo_to_tinstant
        """
        return Temporal._factory(trgeo_to_tinstant(self._inner))

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
            trgeo_geom
        """
        return gserialized_to_shapely_geometry(trgeo_geom(self._inner), precision)

    def values(self, precision: int = 15) -> List[shpb.BaseGeometry]:
        """
        Returns the values of `self`.

        Returns:
            A :class:`list` of :class:`~shapely.geometry.base.BaseGeometry`
            with the values.

        MEOS Functions:
            trgeo_value_n
        """
        return [i.value(precision=precision) for i in self.instants()]

    def start_value(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the start
            value.

        MEOS Functions:
            trgeo_start_value
        """
        return gserialized_to_shapely_geometry(
            trgeo_start_value(self._inner), precision
        )

    def end_value(self, precision: int = 15) -> shpb.BaseGeometry:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the end value.

        MEOS Functions:
            trgeo_end_value
        """
        return gserialized_to_shapely_geometry(trgeo_end_value(self._inner), precision)

    def value_set(self, precision: int = 15) -> Set[shpb.BaseGeometry]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`~shapely.geometry.base.BaseGeometry`
            with the values.

        MEOS Functions:
            trgeo_value_n
        """
        return {i.value(precision=precision) for i in self.instants()}

    def value_at_timestamp(
        self, timestamp: datetime, precision: int = 15
    ) -> shpb.BaseGeometry:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.
            precision: An :class:`int` representing the precision of the
                coordinates.

        Returns:
            A :class:`~shapely.geometry.base.BaseGeometry` with the value.

        MEOS Functions:
            tgeo_value_at_timestamptz
        """
        return gserialized_to_shapely_geometry(
            tgeo_value_at_timestamptz(
                self._inner, datetime_to_timestamptz(timestamp), True
            )[0],
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
            trgeo_value_n
        """
        return gserialized_to_shapely_geometry(
            trgeo_value_n(self._inner, n + 1)[0], precision
        )

    def start_instant(self: Self) -> TRgeometryInst:
        """
        Returns the first instant of `self`.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeo_start_instant
        """
        return Temporal._factory(trgeo_start_instant(self._inner))

    def end_instant(self: Self) -> TRgeometryInst:
        """
        Returns the last instant of `self`.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeo_end_instant
        """
        return Temporal._factory(trgeo_end_instant(self._inner))

    def instant_n(self, n: int) -> TRgeometryInst:
        """
        Returns the ``n``-th instant of `self`.

        Args:
            n: The 0-based index of the instant to return.

        Returns:
            A new :class:`TRgeometryInst` object.

        MEOS Functions:
            trgeo_instant_n
        """
        return Temporal._factory(trgeo_instant_n(self._inner, n + 1))

    def instants(self) -> List[TRgeometryInst]:
        """
        Returns the instants of `self`.

        Returns:
            A :class:`list` of :class:`TRgeometryInst` objects.

        MEOS Functions:
            trgeo_instants
        """
        ins, count = trgeo_instants(self._inner)
        return [Temporal._factory(ins[i]) for i in range(count)]

    def points(self) -> GeometrySet:
        """
        Returns the set of points of `self`.

        Returns:
            A :class:`GeometrySet` with the points.

        MEOS Functions:
            trgeo_points
        """
        from ..factory import _CollectionFactory

        return _CollectionFactory.create_collection(trgeo_points(self._inner))

    def rotation(self) -> TFloat:
        """
        Returns the rotation of `self` as a temporal float.

        Returns:
            A new :class:`TFloat` with the rotation.

        MEOS Functions:
            trgeo_rotation
        """
        result = trgeo_rotation(self._inner)
        return Temporal._factory(result)

    def traversed_area(
        self, unary_union: bool = True, precision: int = 15
    ) -> shpb.BaseGeometry:
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
            trgeo_traversed_area
        """
        return gserialized_to_shapely_geometry(
            trgeo_traversed_area(self._inner, unary_union), precision
        )

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
            trgeo_round
        """
        result = trgeo_round(self._inner, max_decimals)
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
            trgeo_set_interp
        """
        result = trgeo_set_interp(self._inner, interpolation.value)
        return Temporal._factory(result)

    def append_instant(
        self: Self,
        instant: TRgeometryInst,
        max_dist: Optional[float] = 0.0,
        max_time: Optional[timedelta] = None,
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
            trgeo_append_tinstant
        """
        interp = self.interpolation()
        mt = timedelta_to_interval(max_time) if max_time is not None else None
        result = trgeo_append_tinstant(
            self._inner, instant._inner, interp.value, max_dist, mt, False
        )
        return Temporal._factory(result)

    def append_sequence(self: Self, sequence: TRgeometrySeq) -> TRgeometry:
        """
        Returns a new :class:`TRgeometry` with `sequence` appended.

        Args:
            sequence: The :class:`TRgeometrySeq` to append.

        Returns:
            A new :class:`TRgeometry` object.

        MEOS Functions:
            trgeo_append_tsequence
        """
        result = trgeo_append_tsequence(self._inner, sequence._inner, False)
        return Temporal._factory(result)

    # ------------------------- Ever and Always Comparisons -------------------
    def never_equal(self, value: Union[shpb.BaseGeometry, TRgeometry]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_trgeo_geo, ever_eq_trgeo_trgeo
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[shpb.BaseGeometry, TRgeometry]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`~shapely.geometry.base.BaseGeometry` or
                :class:`TRgeometry` to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_trgeo_geo, ever_ne_trgeo_trgeo
        """
        return not self.ever_not_equal(value)

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
            trgeo_restrict_timestamptz, trgeo_restrict_tstzset,
            trgeo_restrict_tstzspan, trgeo_restrict_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeo_restrict_timestamptz(
                self._inner, datetime_to_timestamptz(other), True
            )
        elif isinstance(other, TsTzSet):
            result = trgeo_restrict_tstzset(self._inner, other._inner, True)
        elif isinstance(other, TsTzSpan):
            result = trgeo_restrict_tstzspan(self._inner, other._inner, True)
        elif isinstance(other, TsTzSpanSet):
            result = trgeo_restrict_tstzspanset(self._inner, other._inner, True)
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
            trgeo_restrict_timestamptz, trgeo_restrict_tstzset,
            trgeo_restrict_tstzspan, trgeo_restrict_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeo_restrict_timestamptz(
                self._inner, datetime_to_timestamptz(other), False
            )
        elif isinstance(other, TsTzSet):
            result = trgeo_restrict_tstzset(self._inner, other._inner, False)
        elif isinstance(other, TsTzSpan):
            result = trgeo_restrict_tstzspan(self._inner, other._inner, False)
        elif isinstance(other, TsTzSpanSet):
            result = trgeo_restrict_tstzspanset(self._inner, other._inner, False)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Splitting -------------------------------------
    def segments(self) -> List["TRgeometrySeq"]:
        """
        Returns the temporal segments of `self`.

        MEOS Functions:
            trgeo_segments
        """
        seqs, count = trgeo_segments(self._inner)
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
            trgeo_delete_timestamptz, trgeo_delete_tstzset,
            trgeo_delete_tstzspan, trgeo_delete_tstzspanset
        """
        if isinstance(other, datetime):
            result = trgeo_delete_timestamptz(
                self._inner, datetime_to_timestamptz(other), connect
            )
        elif isinstance(other, TsTzSet):
            result = trgeo_delete_tstzset(self._inner, other._inner, connect)
        elif isinstance(other, TsTzSpan):
            result = trgeo_delete_tstzspan(self._inner, other._inner, connect)
        elif isinstance(other, TsTzSpanSet):
            result = trgeo_delete_tstzspanset(self._inner, other._inner, connect)
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
            trgeo_before_timestamptz
        """
        result = trgeo_before_timestamptz(
            self._inner, datetime_to_timestamptz(timestamp), strict
        )
        return Temporal._factory(result)

    def after(self, timestamp: datetime, strict: bool = False) -> TRgeometry:
        """
        Returns a new temporal rigid geometry with the values of `self`
        after `timestamp`.

        Args:
            timestamp: A :class:`datetime` to restrict after.
            strict: Whether the bound is strict.

        MEOS Functions:
            trgeo_after_timestamptz
        """
        result = trgeo_after_timestamptz(
            self._inner, datetime_to_timestamptz(timestamp), strict
        )
        return Temporal._factory(result)

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
        string: Optional[str] = None,
        *,
        geometry: Optional[shpb.BaseGeometry] = None,
        pose: Optional[Pose] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ) -> None:
        super().__init__(string=string, _inner=_inner)
        if self._inner is None:
            gs = geometry_to_gserialized(geometry)
            ts = (
                datetime_to_timestamptz(timestamp)
                if isinstance(timestamp, datetime)
                else pg_timestamptz_in(timestamp, -1)
            )
            self._inner = trgeoinst_make(gs, pose._inner, ts)


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
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TRgeometryInst]]] = None,
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
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TRgeometrySeq]]] = None,
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
            trgeo_start_sequence
        """
        return self.ComponentClass(_inner=trgeo_start_sequence(self._inner))

    def end_sequence(self) -> TRgeometrySeq:
        """
        Returns the last sequence of `self`.

        MEOS Functions:
            trgeo_end_sequence
        """
        return self.ComponentClass(_inner=trgeo_end_sequence(self._inner))

    def sequence_n(self, n: int) -> TRgeometrySeq:
        """
        Returns the ``n``-th sequence of `self` (0-based).

        MEOS Functions:
            trgeo_sequence_n
        """
        return self.ComponentClass(_inner=trgeo_sequence_n(self._inner, n + 1))

    def sequences(self) -> List[TRgeometrySeq]:
        """
        Returns the list of sequences of `self`.

        MEOS Functions:
            trgeo_sequences
        """
        seqs, count = trgeo_sequences(self._inner)
        return [self.ComponentClass(_inner=seqs[i]) for i in range(count)]
