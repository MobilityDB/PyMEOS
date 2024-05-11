from __future__ import annotations

from typing import Optional, Union, List, TYPE_CHECKING

import shapely.geometry.base as shp
from pymeos_cffi import *

from ..main import TPoint
from ..temporal import Temporal
from ..collections import *

if TYPE_CHECKING:
    from .box import Box


class STBox:
    """
    Class for representing a spatio-temporal box. Temporal bounds may be inclusive or
    exclusive.

    ``STBox`` objects can be created with a single argument of type string as in MobilityDB.

        >>> STBox('STBOX ZT(((1.0,2.0,3.0),(4.0,5.0,6.0)),[2001-01-01, 2001-01-02])')

    Another possibility is to provide the different dimensions with the corresponding parameters:
        - ``xmin``, ``xmax``, ``ymin``, ``ymax`` for spatial dimension
        - ``zmin``, ``zmax`` for the third spatial dimension
        - ``tmin``, ``tmax`` for temporal dimension
        - ``tmin_inc``, ``tmax_inc`` to specify if the temporal bounds are inclusive or exclusive
        - ``geodetic`` to specify if the spatial dimension is geodetic
        - ``srid`` to specify the spatial reference system identifier

    Note that at least the 2D spatial dimension or the temporal dimension must be provided.

        >>> STBox(xmin=1.0, xmax=4.0, ymin=2.0, ymax=5.0, tmin=datetime(2001, 1, 1), tmax=datetime(2001, 1, 2))

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "stbox"

    def _get_box(
        self,
        other: Union[shp.BaseGeometry, STBox, Temporal, Time],
        allow_space_only: bool = True,
        allow_time_only: bool = False,
    ) -> STBox:
        if allow_space_only and isinstance(other, shp.BaseGeometry):
            other_box = geo_to_stbox(geo_to_gserialized(other, self.geodetic()))
        elif isinstance(other, STBox):
            other_box = other._inner
        elif isinstance(other, TPoint):
            other_box = tpoint_to_stbox(other._inner)
        elif allow_time_only and isinstance(other, Temporal):
            other_box = tstzspan_to_stbox(temporal_to_tstzspan(other._inner))
        elif allow_time_only and isinstance(other, datetime):
            other_box = timestamptz_to_stbox(datetime_to_timestamptz(other))
        elif allow_time_only and isinstance(other, TsTzSet):
            other_box = tstzset_to_stbox(other._inner)
        elif allow_time_only and isinstance(other, TsTzSpan):
            other_box = tstzspan_to_stbox(other._inner)
        elif allow_time_only and isinstance(other, TsTzSpanSet):
            other_box = tstzspanset_to_stbox(other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return other_box

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        xmin: Optional[Union[str, float]] = None,
        xmax: Optional[Union[str, float]] = None,
        ymin: Optional[Union[str, float]] = None,
        ymax: Optional[Union[str, float]] = None,
        zmin: Optional[Union[str, float]] = None,
        zmax: Optional[Union[str, float]] = None,
        tmin: Optional[Union[str, datetime]] = None,
        tmax: Optional[Union[str, datetime]] = None,
        tmin_inc: bool = True,
        tmax_inc: bool = True,
        geodetic: bool = False,
        srid: Optional[int] = None,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (
            (
                xmin is not None
                and xmax is not None
                and ymin is not None
                and ymax is not None
            )
            or (tmin is not None and tmax is not None)
        ), (
            "Either string must be not None or at least a bound pair (xmin/max"
            " and ymin/max, or tmin/max) must be not None"
        )

        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = stbox_in(string)
        else:
            tstzspan = None
            hast = tmin is not None and tmax is not None
            hasx = (
                xmin is not None
                and xmax is not None
                and ymin is not None
                and ymax is not None
            )
            hasz = zmin is not None and zmax is not None
            if hast:
                tstzspan = TsTzSpan(
                    lower=tmin, upper=tmax, lower_inc=tmin_inc, upper_inc=tmax_inc
                )._inner
            self._inner = stbox_make(
                hasx,
                hasz,
                geodetic,
                srid or 0,
                float(xmin or 0),
                float(xmax or 0),
                float(ymin or 0),
                float(ymax or 0),
                float(zmin or 0),
                float(zmax or 0),
                tstzspan,
            )

    def __copy__(self) -> STBox:
        """
        Returns a copy of ``self``.

        Returns:
            A :class:`STBox` instance.

        MEOS Functions:
            stbox_copy
        """
        inner_copy = stbox_copy(self._inner)
        return STBox(_inner=inner_copy)

    @staticmethod
    def from_wkb(wkb: bytes) -> STBox:
        """
        Returns a `STBox` from its WKB representation.

        Args:
            wkb: WKB representation

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            stbox_from_wkb
        """
        result = stbox_from_wkb(wkb)
        return STBox(_inner=result)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> STBox:
        """
        Returns a `STBox` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            stbox_from_hexwkb
        """
        result = stbox_from_hexwkb(hexwkb)
        return STBox(_inner=result)

    @staticmethod
    def from_geometry(geom: shp.BaseGeometry, geodetic: bool = False) -> STBox:
        """
        Returns a `STBox` from a `shp.BaseGeometry`.

        Args:
            geom: A `shp.BaseGeometry` instance.
            geodetic: Whether to create a geodetic or geometric `STBox`.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            pgis_geometry_in, geo_to_stbox
        """
        gs = geo_to_gserialized(geom, geodetic)
        return STBox(_inner=geo_to_stbox(gs))

    @staticmethod
    def from_time(time: Time) -> STBox:
        """
        Returns a `STBox` from a `Time` instance.

        Args:
            time: A `Time` instance.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            timestamp_to_stbox, tstzset_to_stbox, tstzspan_to_stbox,
            tstzspanset_to_stbox
        """
        if isinstance(time, datetime):
            result = timestamptz_to_stbox(datetime_to_timestamptz(time))
        elif isinstance(time, TsTzSet):
            result = tstzset_to_stbox(time._inner)
        elif isinstance(time, TsTzSpan):
            result = tstzspan_to_stbox(time._inner)
        elif isinstance(time, TsTzSpanSet):
            result = tstzspanset_to_stbox(time._inner)
        else:
            raise TypeError(f"Operation not supported with type {time.__class__}")
        return STBox(_inner=result)

    @staticmethod
    def from_geometry_time(
        geometry: shp.BaseGeometry,
        time: Union[datetime, TsTzSpan],
        geodetic: bool = False,
    ) -> STBox:
        """
        Returns a `STBox` from a space and time dimension.

        Args:
            geometry: A `shp.BaseGeometry` instance representing the space dimension.
            time: A `Time` instance representing the time dimension.
            geodetic: Whether to create a geodetic or geometric `STBox`.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            geo_timestamp_to_stbox, geo_tstzspan_to_stbox
        """
        gs = geo_to_gserialized(geometry, geodetic)
        if isinstance(time, datetime):
            result = geo_timestamptz_to_stbox(gs, datetime_to_timestamptz(time))
        elif isinstance(time, TsTzSpan):
            result = geo_tstzspan_to_stbox(gs, time._inner)
        else:
            raise TypeError(
                f"Operation not supported with types "
                f"{geometry.__class__} and {time.__class__}"
            )
        return STBox(_inner=result)

    @staticmethod
    def from_tpoint(temporal: TPoint) -> STBox:
        """
        Returns the bounding box of a `TPoint` instance as an `STBox`.

        Args:
            temporal: A `TPoint` instance.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            tpoint_to_stbox
        """
        return STBox(_inner=tpoint_to_stbox(temporal._inner))

    @staticmethod
    def from_expanding_bounding_box(
        value: Union[shp.BaseGeometry, TPoint, STBox],
        expansion: float,
        geodetic: Optional[bool] = False,
    ) -> STBox:
        """
        Returns a `STBox` from a `shp.BaseGeometry`, `TPoint` or `STBox` instance,
        expanding its bounding box by the given amount.

        Args:
            value: A `shp.BaseGeometry`, `TPoint` or `STBox` instance.
            expansion: The amount to expand the bounding box.
            geodetic: Whether to create a geodetic or geometric `STBox`.
            Only used when value is a `shp.BaseGeometry` instance.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            geo_expand_space, tpoint_expand_space, stbox_expand_space
        """
        if isinstance(value, shp.BaseGeometry):
            gs = geo_to_gserialized(value, geodetic)
            result = geo_expand_space(gs, expansion)
        elif isinstance(value, TPoint):
            result = tpoint_expand_space(value._inner, expansion)
        elif isinstance(value, STBox):
            result = stbox_expand_space(value._inner, expansion)
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")
        return STBox(_inner=result)

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Returns a string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            stbox_out
        """
        return stbox_out(self._inner, max_decimals)

    def __repr__(self):
        """
        Returns a string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            stbox_out
        """
        return f"{self.__class__.__name__}" f"({self})"

    def as_wkb(self) -> bytes:
        """
        Returns the WKB representation of ``self``.

        Returns:
            A :class:`str` object with the WKB representation of ``self``.

        MEOS Functions:
            stbox_as_wkb
        """
        return stbox_as_wkb(self._inner, 4)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in
            hex-encoded ASCII.

        MEOS Functions:
            stbox_as_hexwkb
        """
        return stbox_as_hexwkb(self._inner, -1)[0]

    # ------------------------- Conversions ----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the spatial dimension of ``self`` as a `shapely`
        :class:`~shapely.BaseGeometry` instance.

        Args:
            precision: The precision of the geometry coordinates.

        Returns:
            A new :class:`~shapely.BaseGeometry` instance.

        MEOS Functions:
            stbox_to_geo
        """
        return gserialized_to_shapely_geometry(stbox_to_geo(self._inner), precision)

    def to_tstzspan(self) -> TsTzSpan:
        """
        Returns the temporal dimension of ``self`` as a `TsTzSpan` instance.

        Returns:
            A new :class:`TsTzSpan` instance.

        MEOS Functions:
            stbox_to_tstzspan
        """
        return TsTzSpan(_inner=stbox_to_tstzspan(self._inner))

    # ------------------------- Accessors -------------------------------------
    def has_xy(self) -> bool:
        """
        Returns whether ``self`` has a spatial (XY) dimension.

        Returns:
            True if ``self`` has a spatial dimension, False otherwise.

        MEOS Functions:
            stbox_hasx
        """
        return stbox_hasx(self._inner)

    def has_z(self) -> bool:
        """
        Returns whether ``self`` has a Z dimension.

        Returns:
            True if ``self`` has a Z dimension, False otherwise.

        MEOS Functions:
            stbox_hasz
        """
        return stbox_hasz(self._inner)

    def has_t(self) -> bool:
        """
        Returns whether ``self`` has a time dimension.

        Returns:
            True if ``self`` has a time dimension, False otherwise.

        MEOS Functions:
            stbox_hast
        """
        return stbox_hast(self._inner)

    def geodetic(self) -> bool:
        """
        Returns whether ``self`` is geodetic.

        Returns:
            True if ``self`` is geodetic, False otherwise.

        MEOS Functions:
            stbox_isgeodetic
        """
        return stbox_isgeodetic(self._inner)

    def xmin(self) -> Optional[float]:
        """
        Returns the minimum X coordinate of ``self``.

        Returns:
            A :class:`float` with the minimum X coordinate of ``self``.

        MEOS Functions:
            stbox_xmin
        """
        return stbox_xmin(self._inner)

    def ymin(self) -> Optional[float]:
        """
        Returns the minimum Y coordinate of ``self``.

        Returns:
            A :class:`float` with the minimum Y coordinate of ``self``.

        MEOS Functions:
            stbox_ymin
        """
        return stbox_ymin(self._inner)

    def zmin(self) -> Optional[float]:
        """
        Returns the minimum Z coordinate of ``self``.

        Returns:
            A :class:`float` with the minimum Z coordinate of ``self``.

        MEOS Functions:
            stbox_zmin
        """
        return stbox_zmin(self._inner)

    def tmin(self) -> Optional[datetime]:
        """
        Returns the starting time of ``self``.

        Returns:
            A :class:`datetime` with the minimum time coordinate of ``self``.

        MEOS Functions:
            stbox_tmin
        """
        result = stbox_tmin(self._inner)
        return timestamptz_to_datetime(result) if result else None

    def tmin_inc(self) -> bool:
        """
        Returns whether starting time of ``self`` is inclusive or not

        Returns:
            True if the starting time of ``self`` is inclusive and False
            otherwise

        MEOS Functions:
            stbox_tmin_inc
        """
        return stbox_tmin_inc(self._inner)

    def xmax(self) -> Optional[float]:
        """
        Returns the maximum X coordinate of ``self``.

        Returns:
            A :class:`float` with the maximum X coordinate of ``self``.

        MEOS Functions:
            stbox_xmax
        """
        return stbox_xmax(self._inner)

    def ymax(self) -> Optional[float]:
        """
        Returns the maximum Y coordinate of ``self``.

        Returns:
            A :class:`float` with the maximum Y coordinate of ``self``.

        MEOS Functions:
            stbox_ymax
        """
        return stbox_ymax(self._inner)

    def zmax(self) -> Optional[float]:
        """
        Returns the maximum Z coordinate of ``self``.

        Returns:
            A :class:`float` with the maximum Z coordinate of ``self``.

        MEOS Functions:
            stbox_zmax
        """
        return stbox_zmax(self._inner)

    def tmax(self) -> Optional[datetime]:
        """
        Returns the ending time of ``self``.

        Returns:
            A :class:`datetime` with the maximum time coordinate of ``self``.

        MEOS Functions:
            stbox_tmax
        """
        result = stbox_tmax(self._inner)
        return timestamptz_to_datetime(result) if result else None

    def tmax_inc(self) -> bool:
        """
        Returns whether ending time of ``self`` is inclusive or not

        Returns:
            True if the ending time of ``self`` is inclusive and False otherwise

        MEOS Functions:
            stbox_tmax_inc
        """
        return stbox_tmax_inc(self._inner)

    # ------------------------- Spatial Reference System ----------------------
    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        Returns:
            An :class:`int` with the SRID of ``self``.

        MEOS Functions:
            stbox_srid
        """
        return self._inner.srid

    def set_srid(self, value: int) -> STBox:
        """
        Returns a copy of ``self`` with the SRID set to ``value``.

        Args:
            value: The new SRID.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            stbox_set_srid
        """
        return STBox(_inner=stbox_set_srid(self._inner, value))

    # ------------------------- Transformations -------------------------------
    def get_space(self) -> STBox:
        """
        Get the spatial dimension of ``self``, removing the temporal dimension
        if any

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            stbox_get_space
        """
        result = stbox_get_space(self._inner)
        return STBox(_inner=result)

    def expand(self, other: Union[int, float, timedelta]) -> STBox:
        """
        Expands ``self`` with `other`.
        If `other` is a :class:`int` or a :class:`float`, the result is equal
        to ``self`` but with the spatial dimensions expanded by `other` in all
        directions. If `other` is a :class:`timedelta`, the result is equal to
        ``self``  but with the temporal dimension expanded by `other` in both
        directions.

        Args:
            other: The object to expand ``self`` with.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            stbox_expand_space, stbox_expand_time
        """
        if isinstance(other, int) or isinstance(other, float):
            result = stbox_expand_space(self._inner, float(other))
        elif isinstance(other, timedelta):
            result = stbox_expand_time(self._inner, timedelta_to_interval(other))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return STBox(_inner=result)

    def shift_time(self, delta: timedelta) -> STBox:
        """
        Returns a new `STBox` with the time dimension shifted by `delta`.

        Args:
            delta: :class:`datetime.timedelta` instance to shift

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            stbox_shift_scale_time

        See Also:
            :meth:`STBox.shift`
        """
        return self.shift_scale_time(shift=delta)

    def scale_time(self, duration: timedelta) -> STBox:
        """
        Returns a new `STBox` with the time dimension having duration
        `duration`.

        Args:
            duration: :class:`datetime.timedelta` instance with new duration

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            tstzspan_shift_scale

        See Also:
            :meth:`STBox.scale`
        """
        return self.shift_scale_time(duration=duration)

    def shift_scale_time(
        self, shift: Optional[timedelta] = None, duration: Optional[timedelta] = None
    ) -> STBox:
        """
        Returns a new `STBox` with the time dimension shifted by `shift` and
        with duration `duration`.

        Args:
            shift: :class:`datetime.timedelta` instance to shift
            duration: :class:`datetime.timedelta` instance with new duration

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            stbox_shift_scale_time

        See Also:
            :meth:`TsTzSpan.shift_scale`
        """
        assert (
            shift is not None or duration is not None
        ), "shift and scale deltas must not be both None"
        result = stbox_shift_scale_time(
            self._inner,
            timedelta_to_interval(shift) if shift else None,
            timedelta_to_interval(duration) if duration else None,
        )
        return STBox(_inner=result)

    def round(self, max_decimals: Optional[int] = 0) -> STBox:
        """
        Returns `self` rounded to the given number of decimal digits.

        Args:
            max_decimals: Maximum number of decimal digits.

        Returns:
            A new :class:`STBox` instance

        MEOS Functions:
            stbox_round
        """
        new_inner = stbox_copy(self._inner)
        stbox_round(new_inner, max_decimals)
        return STBox(_inner=new_inner)

    def transform(self, srid: int) -> STBox:
        """
        Returns a new :class:`STBox` transformed to another SRID

        Args:
            srid: The desired SRID

        Returns:
             A new :class:`STBox` instance

         MEOS Functions:
            stbox_transform
        """
        result = stbox_transform(self._inner, srid)
        return STBox(_inner=result)

    # ------------------------- Set Operations --------------------------------
    def union(self, other: STBox, strict: Optional[bool] = False) -> STBox:
        """
        Returns the union of `self` with `other`.

        Args:
            other: spatiotemporal box to merge with
            strict: Whether to fail if the boxes do not intersect.

        Returns:
            A :class:`STBox` instance.

        MEOS Functions:
            union_stbox_stbox
        """
        return STBox(_inner=union_stbox_stbox(self._inner, other._inner, strict))

    def __add__(self, other):
        """
        Returns the union of `self` with `other`. Fails if the union is not
        contiguous.

        Args:
            other: spatiotemporal box to merge with

        Returns:
            A :class:`STBox` instance.

        MEOS Functions:
            union_stbox_stbox
        """
        return self.union(other, False)

    # TODO: Check returning None for empty intersection is the desired behaviour
    def intersection(self, other: STBox) -> Optional[STBox]:
        """
        Returns the intersection of `self` with `other`.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`STBox` instance if the instersection is not empty, `None`
            otherwise.

        MEOS Functions:
            intersection_stbox_stbox
        """
        result = intersection_stbox_stbox(self._inner, other._inner)
        return STBox(_inner=result) if result else None

    def __mul__(self, other):
        """
        Returns the intersection of `self` with `other`.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`STBox` instance if the instersection is not empty, `None`
            otherwise.

        MEOS Functions:
            intersection_stbox_stbox
        """
        return self.intersection(other)

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(
        self, other: Union[shp.BaseGeometry, STBox, Temporal, Time]
    ) -> bool:
        """
        Returns whether ``self`` and `other` are adjacent. Two spatiotemporal
        boxes are adjacent if they share n dimensions and the intersection is
        of at most n-1 dimensions. Note that for `TPoint` instances, the
        bounding box of the temporal point is used.

        Args:
            other: The other spatiotemporal object to check adjacency with
            ``self``.

        Returns:
            ``True`` if ``self`` and `other` are adjacent, ``False`` otherwise.

        MEOS Functions:
            adjacent_stbox_stbox
        """
        return adjacent_stbox_stbox(
            self._inner, self._get_box(other, allow_time_only=True)
        )

    def is_contained_in(
        self, container: Union[shp.BaseGeometry, STBox, Temporal, Time]
    ) -> bool:
        """
        Returns whether ``self`` is contained in `container`. Note that for
        `TPoint` instances, the bounding box of the temporal point is used.

        Args:
            container: The spatiotemporal object to check containment with
            ``self``.

        Returns:
            ``True`` if ``self`` is contained in `container`, ``False`` otherwise.

        MEOS Functions:
            contained_stbox_stbox
        """
        return contained_stbox_stbox(
            self._inner, self._get_box(container, allow_time_only=True)
        )

    def contains(self, content: Union[shp.BaseGeometry, STBox, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` contains `content`. Note that for `TPoint`
        instances, the bounding box of the temporal point is used.

        Args:
            content: The spatiotemporal object to check containment with
            ``self``.

        Returns:
            ``True`` if ``self`` contains `content`, ``False`` otherwise.

        MEOS Functions:
            contains_stbox_stbox
        """
        return contains_stbox_stbox(
            self._inner, self._get_box(content, allow_time_only=True)
        )

    def __contains__(self, item):
        """
        Returns whether ``self`` contains `item`.

        Args:
            item: The spatiotemporal object to check if it is contained in
            ``self``.

        Returns:
            ``True`` if ``self`` contains ``item``, ``False`` otherwise.

        MEOS Functions:
            contains_stbox_stbox

        See Also:
            :meth:`STBox.contains`
        """
        return self.contains(item)

    def overlaps(self, other: Union[shp.BaseGeometry, STBox, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` overlaps `other`. Note that for `TPoint`
        instances, the bounding box of the temporal point is used.

        Args:
            other: The spatiotemporal object to check overlap with ``self``.

        Returns:
            ``True`` if ``self`` overlaps `other`, ``False`` otherwise.

        MEOS Functions:
            overlaps_stbox_stbox
        """
        return overlaps_stbox_stbox(
            self._inner, self._get_box(other, allow_time_only=True)
        )

    def is_same(self, other: Union[shp.BaseGeometry, STBox, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` is the same as `other`. Note that for `TPoint`
        instances, the bounding box of the temporal point is used.

        Args:
            other: The spatiotemporal object to check equality with ``self``.

        Returns:
            ``True`` if ``self`` is the same as `other`, ``False`` otherwise.

        MEOS Functions:
            same_stbox_stbox
        """
        return same_stbox_stbox(self._inner, self._get_box(other, allow_time_only=True))

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly to the left  of `other`. Checks
        the X dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly to the left of `other`,
            ``False`` otherwise.

        MEOS Functions:
            left_stbox_stbox
        """
        return left_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_left(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is to the left `other` allowing for overlap.
        That is, ``self`` does not extend to the right of `other`. Checks the
        X dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is to the left of `other` allowing for
            overlap, ``False`` otherwise.

        MEOS Functions:
            overleft_stbox_stbox, tpoint_to_stbox
        """
        return overleft_stbox_stbox(self._inner, self._get_box(other))

    def is_right(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly to the right of `other`.
        Checks the X dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly to the right of `other`,
            ``False`` otherwise.

        MEOS Functions:
            right_stbox_stbox
        """
        return right_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_right(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is to the right of `other` allowing for
        overlap. That is, ``self`` does not extend to the left of `other`.
        Checks the X dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is to the right of `other` allowing for
            overlap, ``False`` otherwise.

        MEOS Functions:
            overright_stbox_stbox
        """
        return overright_stbox_stbox(self._inner, self._get_box(other))

    def is_below(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly below `other`.
        Checks the Y dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly below `other`, ``False``
            otherwise.

        MEOS Functions:
            below_stbox_stbox
        """
        return below_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_below(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is below `other` allowing for overlap.
        That is, ``self`` does not extend above `other`. Checks the Y dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is below `other` allowing for overlap,
            ``False`` otherwise.

        MEOS Functions:
            overbelow_stbox_stbox
        """
        return overbelow_stbox_stbox(self._inner, self._get_box(other))

    def is_above(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly above `other`.
        Checks the Y dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly above `other`, ``False``
            otherwise.

        MEOS Functions:
            above_stbox_stbox
        """
        return above_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_above(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is above `other` allowing for overlap.
        That is, ``self`` does not extend below `other`.
        Checks the Y dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is above `other` allowing for overlap,
            ``False`` otherwise.

        MEOS Functions:
            overabove_stbox_stbox
        """
        return overabove_stbox_stbox(self._inner, self._get_box(other))

    def is_front(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly in front of `other`.
        Checks the Z dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly in front of `other`, ``False``
            otherwise.

        MEOS Functions:
            front_stbox_stbox
        """
        return front_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_front(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is in front of `other` allowing for overlap.
        That is, ``self`` does not extend behind `other`.
        Checks the Z dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is in front of `other` allowing for overlap,
            ``False`` otherwise.

        MEOS Functions:
            overfront_stbox_stbox
        """
        return overfront_stbox_stbox(self._inner, self._get_box(other))

    def is_behind(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is strictly behind `other`.
        Checks the Z dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly behind `other`, ``False``
            otherwise.

        MEOS Functions:
            back_stbox_stbox
        """
        return back_stbox_stbox(self._inner, self._get_box(other))

    def is_over_or_behind(self, other: Union[shp.BaseGeometry, STBox, TPoint]) -> bool:
        """
        Returns whether ``self`` is behind `other` allowing for overlap.
        That is, ``self`` does not extend in front of `other`.
        Checks the Z dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is behind `other` allowing for overlap,
            ``False`` otherwise.

        MEOS Functions:
            overback_stbox_stbox
        """
        return overback_stbox_stbox(self._inner, self._get_box(other))

    def is_before(self, other: Union[Box, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` is strictly before `other`.
        Checks the time dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly before `other`, ``False``
            otherwise.
        """
        return self.to_tstzspan().is_before(other)

    def is_over_or_before(self, other: Union[Box, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` is before `other` allowing for overlap.
        That is, ``self`` does not extend after `other`.
        Checks the time dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is before `other` allowing for overlap,
            ``False`` otherwise.
        """
        return self.to_tstzspan().is_over_or_before(other)

    def is_after(self, other: Union[Box, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` is strictly after `other`.
        Checks the time dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is strictly after `other`, ``False``
            otherwise.
        """
        return self.to_tstzspan().is_after(other)

    def is_over_or_after(self, other: Union[Box, Temporal, Time]) -> bool:
        """
        Returns whether ``self`` is after `other` allowing for overlap.
        That is, ``self`` does not extend before `other`.
        Checks the time dimension.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is after `other` allowing for overlap,
            ``False`` otherwise.
        """
        return self.to_tstzspan().is_over_or_after(other)

    # ------------------------- Distance Operations ---------------------------
    def nearest_approach_distance(
        self, other: Union[shp.BaseGeometry, STBox, TPoint]
    ) -> float:
        """
        Returns the distance between the nearest points of ``self`` and `other`.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            A :class:`float` with the distance between the nearest points of
            ``self`` and ``other``.

        MEOS Functions:
            nad_stbox_geo, nad_stbox_stbox
        """
        if isinstance(other, shp.BaseGeometry):
            gs = geo_to_gserialized(other, self.geodetic())
            return nad_stbox_geo(self._inner, gs)
        elif isinstance(other, STBox):
            return nad_stbox_stbox(self._inner, other._inner)
        elif isinstance(other, TPoint):
            return nad_tpoint_stbox(other._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Splitting --------------------------------------
    def quad_split_flat(self) -> List[STBox]:
        """
        Returns a list of 4 (or 8 if `self`has Z dimension) :class:`STBox`
        instances resulting from the quad  split of ``self``.

        Indices of returned array are as follows (back only present if Z
        dimension is present):

           >>> #    (front)          (back)
           >>> # -------------   -------------
           >>> # |  2  |  3  |   |  6  |  7  |
           >>> # ------------- + -------------
           >>> # |  0  |  1  |   |  4  |  5  |
           >>> # -------------   -------------

        Returns:
            A :class:`list` of :class:`STBox` instances.

        MEOS Functions:
            stbox_quad_split
        """
        boxes, count = stbox_quad_split(self._inner)
        return [STBox(_inner=boxes + i) for i in range(count)]

    def quad_split(self) -> Union[List[List[STBox]], List[List[List[STBox]]]]:
        """
        Returns a 2D (YxX) or 3D (ZxYxX) list of :class:`STBox` instances
        resulting from the quad split of ``self``.

        Indices of returned array are as follows:

           >>> #       (front)
           >>> # -------------------
           >>> # | [1][0] | [1][1] |
           >>> # -------------------
           >>> # | [0][0] | [0][1] |
           >>> # -------------------

        If Z dimension is present:

           >>> #          (front)                      (back)
           >>> # -------------------------   -------------------------
           >>> # | [0][1][0] | [0][1][1] |   | [1][1][0] | [1][1][1] |
           >>> # ------------------------- + -------------------------
           >>> # | [0][0][0] | [0][0][1] |   | [1][0][0] | [1][0][1] |
           >>> # -------------------------   -------------------------


        Returns:
            A 2D or 3D :class:`list` of :class:`STBox` instances.

        MEOS Functions:
            stbox_quad_split

        """
        boxes, count = stbox_quad_split(self._inner)
        if self.has_z():
            return [
                [
                    [STBox(_inner=boxes + i) for i in range(2)],
                    [STBox(_inner=boxes + i) for i in range(2, 4)],
                ],
                [
                    [STBox(_inner=boxes + i) for i in range(4, 6)],
                    [STBox(_inner=boxes + i) for i in range(6, 8)],
                ],
            ]
        else:
            return [
                [STBox(_inner=boxes + i) for i in range(2)],
                [STBox(_inner=boxes + i) for i in range(2, 4)],
            ]

    def tile(
        self,
        size: Optional[float] = None,
        duration: Optional[Union[timedelta, str]] = None,
        origin: Optional[shp.BaseGeometry] = None,
        start: Union[datetime, str, None] = None,
    ) -> List[STBox]:
        """
        Returns a list of `STBox` instances representing the tiles of
        ``self``.

        Args:
            size: The size of the spatial tiles. If the `STBox` instance has a
                spatial dimension and this argument is not provided, the tiling
                will be only temporal.
            duration: The duration of the temporal tiles. If the `STBox`
                instance has a time dimension and this argument is not
                provided, the tiling will be only spatial.
            origin: The origin of the spatial tiling. If not provided, the
                origin will be (0, 0, 0).
            start: The start time of the temporal tiling. If not provided,
                the start time used by default is Monday, January 3, 2000.

        Returns:
            A list of `STBox` instances.

        MEOS Functions:
            stbox_tile_list
        """
        sz = size or (
            max(
                self.xmax() - self.xmin(),
                self.ymax() - self.ymin(),
                (self.zmax() - self.zmin() if self.has_z() else 0),
            )
            + 1
        )
        dt = (
            timedelta_to_interval(duration)
            if isinstance(duration, timedelta)
            else pg_interval_in(duration, -1) if isinstance(duration, str) else None
        )
        st = (
            datetime_to_timestamptz(start)
            if isinstance(start, datetime)
            else (
                pg_timestamptz_in(start, -1)
                if isinstance(start, str)
                else pg_timestamptz_in("2000-01-03", -1) if self.has_t() else 0
            )
        )
        gs = (
            geo_to_gserialized(origin, self.geodetic())
            if origin is not None
            else (
                pgis_geography_in("Point(0 0 0)", -1)
                if self.geodetic()
                else pgis_geometry_in("Point(0 0 0)", -1)
            )
        )
        tiles, count = stbox_tile_list(self._inner, sz, sz, sz, dt, gs, st)
        return [STBox(_inner=tiles + i) for i in range(count)]

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` is equal to `other`.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is equal to ``other``, ``False`` otherwise.

        MEOS Functions:
            stbox_eq
        """
        if isinstance(other, self.__class__):
            return stbox_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` is not equal to `other`.

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is not equal to ``other``, ``False`` otherwise.

        MEOS Functions:
            stbox_ne
        """
        if isinstance(other, self.__class__):
            return stbox_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Returns whether ``self`` is less than `other`. Compares first the SRID,
        then the time dimension, and finally the spatial dimension (X, then Y
        then Z lower bounds and then the upper bounds).

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than ``other``, ``False`` otherwise.

        MEOS Functions:
            stbox_lt
        """
        if isinstance(other, self.__class__):
            return stbox_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Returns whether ``self`` is less than or equal to `other`. Compares
        first the SRID, then the time dimension, and finally the spatial
        dimension (X, then Y then Z lower bounds and then the upper bounds).

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than or equal to ``other``, ``False``
            otherwise.

        MEOS Functions:
            stbox_le
        """
        if isinstance(other, self.__class__):
            return stbox_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Returns whether ``self`` is greater than `other`. Compares first the
        SRID, then the time dimension, and finally the spatial dimension (X,
        then Y then Z lower bounds and then the upper bounds).

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is greater than ``other``, ``False`` otherwise.

        MEOS Functions:
            stbox_gt
        """
        if isinstance(other, self.__class__):
            return stbox_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Returns whether ``self`` is greater than or equal to `other`. Compares
        first the SRID, then the time dimension, and finally the spatial
        dimension (X, then Y then Z lower bounds and then the upper bounds).

        Args:
            other: The spatiotemporal object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is greater than or equal to ``other``,
            ``False`` otherwise.

        MEOS Functions:
            stbox_ge
        """
        if isinstance(other, self.__class__):
            return stbox_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Plot Operations -------------------------------
    def plot_xy(self, *args, **kwargs):
        """
        Plots the spatial dimension (XY) of ``self``.

        See Also:
            :func:`~pymeos.plotters.box_plotter.BoxPlotter.plot_stbox_xy`
        """
        from ..plotters import BoxPlotter

        return BoxPlotter.plot_stbox_xy(self, *args, **kwargs)

    def plot_xt(self, *args, **kwargs):
        """
        Plots the first spatial dimension and the temporal dimension (XT) of
        ``self``.

        See Also:
            :func:`~pymeos.plotters.box_plotter.BoxPlotter.plot_stbox_xt`
        """
        from ..plotters import BoxPlotter

        return BoxPlotter.plot_stbox_xt(self, *args, **kwargs)

    def plot_yt(self, *args, **kwargs):
        """
        Plots the second spatial dimension and the temporal dimension (YT) of
        ``self``.

        See Also:
            :func:`~pymeos.plotters.box_plotter.BoxPlotter.plot_stbox_yt`
        """
        from ..plotters import BoxPlotter

        return BoxPlotter.plot_stbox_yt(self, *args, **kwargs)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`STBox` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return STBox(string=value)
