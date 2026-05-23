from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

import shapely.geometry.base as shp
from pymeos_cffi import *

if TYPE_CHECKING:
    from ...boxes import STBox


class Cbuffer:
    """
    Class for representing a circular buffer, that is, a point together with a
    radius.

    ``Cbuffer`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> Cbuffer('Cbuffer(Point(1 1), 2)')

    Another possibility is to provide the ``point`` and the ``radius``
    arguments.

        >>> Cbuffer(point=Point(1, 1), radius=2.0)

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "cbuffer"

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        point: Optional[Union[str, shp.BaseGeometry]] = None,
        radius: Optional[float] = None,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (
            point is not None and radius is not None
        ), (
            "Either string must be not None or both point and radius must be"
            " not None"
        )
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = cbuffer_in(string)
        else:
            if isinstance(point, str):
                gs = geom_in(point, -1)
            else:
                gs = geometry_to_gserialized(point)
            self._inner = cbuffer_make(gs, float(radius))

    def __copy__(self) -> Cbuffer:
        """
        Returns a copy of ``self``.

        Returns:
            A :class:`Cbuffer` instance.

        MEOS Functions:
            cbuffer_copy
        """
        inner_copy = cbuffer_copy(self._inner)
        return Cbuffer(_inner=inner_copy)

    @staticmethod
    def from_wkb(wkb: bytes) -> Cbuffer:
        """
        Returns a `Cbuffer` from its WKB representation.

        Args:
            wkb: WKB representation

        Returns:
            A new :class:`Cbuffer` instance

        MEOS Functions:
            cbuffer_from_wkb
        """
        result = cbuffer_from_wkb(wkb, len(wkb))
        return Cbuffer(_inner=result)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Cbuffer:
        """
        Returns a `Cbuffer` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`Cbuffer` instance

        MEOS Functions:
            cbuffer_from_hexwkb
        """
        result = cbuffer_from_hexwkb(hexwkb)
        return Cbuffer(_inner=result)

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            cbuffer_out
        """
        return cbuffer_out(self._inner, max_decimals)

    def __repr__(self):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            cbuffer_out
        """
        return f"{self.__class__.__name__}" f"({self})"

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            cbuffer_as_text
        """
        return cbuffer_as_text(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            cbuffer_as_text
        """
        return cbuffer_as_text(self._inner, max_decimals)

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            cbuffer_as_ewkt
        """
        return cbuffer_as_ewkt(self._inner, max_decimals)

    def as_wkb(self) -> bytes:
        """
        Returns the WKB representation of ``self``.

        Returns:
            A :class:`bytes` object with the WKB representation of ``self``.

        MEOS Functions:
            cbuffer_as_wkb
        """
        return cbuffer_as_wkb(self._inner, 4)[0]

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in
            hex-encoded ASCII.

        MEOS Functions:
            cbuffer_as_hexwkb
        """
        return cbuffer_as_hexwkb(self._inner, -1, None)

    # ------------------------- Conversions -----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the geometry representation of ``self``.

        Args:
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            cbuffer_to_geom
        """
        return gserialized_to_shapely_geometry(
            cbuffer_to_geom(self._inner), precision
        )

    def to_stbox(self) -> STBox:
        """
        Returns the bounding box of ``self``.

        Returns:
            A new :class:`~pymeos.boxes.STBox` instance.

        MEOS Functions:
            cbuffer_to_stbox
        """
        from ...boxes import STBox

        return STBox(_inner=cbuffer_to_stbox(self._inner))

    @staticmethod
    def from_geometry(geom: shp.BaseGeometry) -> Cbuffer:
        """
        Returns a `Cbuffer` from a geometry.

        Args:
            geom: A :class:`~shapely.geometry.base.BaseGeometry` instance.

        Returns:
            A new :class:`Cbuffer` instance.

        MEOS Functions:
            geom_to_cbuffer
        """
        result = geom_to_cbuffer(geometry_to_gserialized(geom))
        return Cbuffer(_inner=result)

    # ------------------------- Accessors -------------------------------------
    def point(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the point of ``self``.

        Args:
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            cbuffer_point
        """
        return gserialized_to_shapely_geometry(
            cbuffer_point(self._inner), precision
        )

    def radius(self) -> float:
        """
        Returns the radius of ``self``.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            cbuffer_radius
        """
        return cbuffer_radius(self._inner)

    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            cbuffer_srid
        """
        return cbuffer_srid(self._inner)

    def hash(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            cbuffer_hash
        """
        return cbuffer_hash(self._inner)

    def __hash__(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            cbuffer_hash
        """
        return cbuffer_hash(self._inner)

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> Cbuffer:
        """
        Returns `self` rounded to the given number of decimal digits.

        Args:
            max_decimals: Maximum number of decimal digits.

        Returns:
            A new :class:`Cbuffer` instance.

        MEOS Functions:
            cbuffer_round
        """
        return Cbuffer(_inner=cbuffer_round(self._inner, max_decimals))

    def set_srid(self, srid: int) -> Cbuffer:
        """
        Returns a new :class:`Cbuffer` with the SRID set to ``srid``.

        Args:
            srid: The SRID to set.

        Returns:
            A new :class:`Cbuffer` instance.

        MEOS Functions:
            cbuffer_set_srid
        """
        new_inner = cbuffer_copy(self._inner)
        cbuffer_set_srid(new_inner, srid)
        return Cbuffer(_inner=new_inner)

    def transform(self, srid: int) -> Cbuffer:
        """
        Returns a new :class:`Cbuffer` transformed to another SRID.

        Args:
            srid: The desired SRID.

        Returns:
            A new :class:`Cbuffer` instance.

        MEOS Functions:
            cbuffer_transform
        """
        return Cbuffer(_inner=cbuffer_transform(self._inner, srid))

    # ------------------------- Distance Operations ---------------------------
    def distance(
        self, other: Union[Cbuffer, shp.BaseGeometry, STBox]
    ) -> float:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: A :class:`Cbuffer`, geometry or
                :class:`~pymeos.boxes.STBox` instance.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            distance_cbuffer_cbuffer, distance_cbuffer_geo,
            distance_cbuffer_stbox
        """
        from ...boxes import STBox

        if isinstance(other, Cbuffer):
            return distance_cbuffer_cbuffer(self._inner, other._inner)
        elif isinstance(other, shp.BaseGeometry):
            return distance_cbuffer_geo(
                self._inner, geometry_to_gserialized(other)
            )
        elif isinstance(other, STBox):
            return distance_cbuffer_stbox(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def nearest_approach_distance(self, other: STBox) -> float:
        """
        Returns the nearest approach distance between ``self`` and ``other``.

        Args:
            other: A :class:`~pymeos.boxes.STBox` instance.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            nad_cbuffer_stbox
        """
        from ...boxes import STBox

        if isinstance(other, STBox):
            return nad_cbuffer_stbox(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Spatial Relationships -------------------------
    def contains(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` contains ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` contains ``other``, ``False`` otherwise.

        MEOS Functions:
            contains_cbuffer_cbuffer
        """
        return contains_cbuffer_cbuffer(self._inner, other._inner) == 1

    def covers(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` covers ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` covers ``other``, ``False`` otherwise.

        MEOS Functions:
            covers_cbuffer_cbuffer
        """
        return covers_cbuffer_cbuffer(self._inner, other._inner) == 1

    def is_disjoint(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` is disjoint from ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` is disjoint from ``other``, ``False``
            otherwise.

        MEOS Functions:
            disjoint_cbuffer_cbuffer
        """
        return disjoint_cbuffer_cbuffer(self._inner, other._inner) == 1

    def intersects(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` intersects ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` intersects ``other``, ``False`` otherwise.

        MEOS Functions:
            intersects_cbuffer_cbuffer
        """
        return intersects_cbuffer_cbuffer(self._inner, other._inner) == 1

    def touches(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` touches ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` touches ``other``, ``False`` otherwise.

        MEOS Functions:
            touches_cbuffer_cbuffer
        """
        return touches_cbuffer_cbuffer(self._inner, other._inner) == 1

    def is_within_distance(self, other: Cbuffer, distance: float) -> bool:
        """
        Returns whether ``self`` is within ``distance`` of ``other``.

        Args:
            other: A :class:`Cbuffer` instance.
            distance: The distance to check.

        Returns:
            ``True`` if ``self`` is within ``distance`` of ``other``, ``False``
            otherwise.

        MEOS Functions:
            dwithin_cbuffer_cbuffer
        """
        return dwithin_cbuffer_cbuffer(self._inner, other._inner, distance) == 1

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` is equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is equal to ``other``, ``False`` otherwise.

        MEOS Functions:
            cbuffer_eq
        """
        if isinstance(other, self.__class__):
            return cbuffer_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` is not equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is not equal to ``other``, ``False``
            otherwise.

        MEOS Functions:
            cbuffer_ne
        """
        if isinstance(other, self.__class__):
            return cbuffer_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Returns whether ``self`` is less than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than ``other``, ``False`` otherwise.

        MEOS Functions:
            cbuffer_lt
        """
        if isinstance(other, self.__class__):
            return cbuffer_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Returns whether ``self`` is less than or equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than or equal to ``other``, ``False``
            otherwise.

        MEOS Functions:
            cbuffer_le
        """
        if isinstance(other, self.__class__):
            return cbuffer_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Returns whether ``self`` is greater than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is greater than ``other``, ``False``
            otherwise.

        MEOS Functions:
            cbuffer_gt
        """
        if isinstance(other, self.__class__):
            return cbuffer_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Returns whether ``self`` is greater than or equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is greater than or equal to ``other``,
            ``False`` otherwise.

        MEOS Functions:
            cbuffer_ge
        """
        if isinstance(other, self.__class__):
            return cbuffer_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def cmp(self, other: Cbuffer) -> int:
        """
        Returns -1, 0, or 1 depending on whether ``self`` is less than, equal
        to, or greater than ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            cbuffer_cmp
        """
        return cbuffer_cmp(self._inner, other._inner)

    def same(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` is spatially the same as ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` is the same as ``other``, ``False`` otherwise.

        MEOS Functions:
            cbuffer_same
        """
        return cbuffer_same(self._inner, other._inner)

    def not_same(self, other: Cbuffer) -> bool:
        """
        Returns whether ``self`` is spatially not the same as ``other``.

        Args:
            other: A :class:`Cbuffer` instance.

        Returns:
            ``True`` if ``self`` is not the same as ``other``, ``False``
            otherwise.

        MEOS Functions:
            cbuffer_nsame
        """
        return cbuffer_nsame(self._inner, other._inner)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`Cbuffer` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return Cbuffer(string=value)
