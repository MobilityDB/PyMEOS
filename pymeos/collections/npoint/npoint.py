from __future__ import annotations

from typing import TYPE_CHECKING

import shapely.geometry.base as shp
from pymeos_cffi import *

if TYPE_CHECKING:
    from ...boxes import STBox


class Npoint:
    """
    Class for representing a network point, i.e. a point defined by a route
    identifier and a relative position along that route.

    ``Npoint`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> Npoint('NPoint(1, 0.5)')

    Another possibility is to provide the route identifier and the relative
    position with the corresponding parameters.

        >>> Npoint(route=1, position=0.5)

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "npoint"

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: str | None = None,
        *,
        route: int | None = None,
        position: float | None = None,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (route is not None and position is not None), (
            "Either string must be not None or route and position must be not None"
        )
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = npoint_in(string)
        else:
            self._inner = npoint_make(route, position)

    @staticmethod
    def from_wkb(wkb: bytes) -> Npoint:
        """
        Returns a `Npoint` from its WKB representation.

        Args:
            wkb: WKB representation

        Returns:
            A new :class:`Npoint` instance

        MEOS Functions:
            npoint_from_wkb
        """
        result = npoint_from_wkb(wkb)
        return Npoint(_inner=result)

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Npoint:
        """
        Returns a `Npoint` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`Npoint` instance

        MEOS Functions:
            npoint_from_hexwkb
        """
        result = npoint_from_hexwkb(hexwkb)
        return Npoint(_inner=result)

    @staticmethod
    def from_geometry(geom: shp.BaseGeometry) -> Npoint:
        """
        Returns a `Npoint` from a `shp.BaseGeometry`.

        Args:
            geom: A `shp.BaseGeometry` instance.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            geompoint_to_npoint
        """
        gs = geometry_to_gserialized(geom)
        return Npoint(_inner=geompoint_to_npoint(gs))

    def __copy__(self) -> Npoint:
        """
        Returns a copy of ``self``.

        Returns:
            A :class:`Npoint` instance.

        MEOS Functions:
            npoint_round
        """
        inner_copy = npoint_round(self._inner, 100)
        return Npoint(_inner=inner_copy)

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            npoint_as_text
        """
        return self.as_text(max_decimals)

    def __repr__(self):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            npoint_out
        """
        return f"{self.__class__.__name__}({self})"

    def as_wkb(self, endian: str = "") -> bytes:
        """
        Returns the WKB representation of ``self``.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` object with the WKB representation of ``self``.

        MEOS Functions:
            npoint_as_wkb, wkb_variant_from_endian
        """
        return npoint_as_wkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexwkb(self, endian: str = "") -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in
            hex-encoded ASCII.

        MEOS Functions:
            npoint_as_hexwkb, wkb_variant_from_endian
        """
        return npoint_as_hexwkb(self._inner, wkb_variant_from_endian(endian))[0]

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the
            coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            npoint_as_ewkt
        """
        return npoint_as_ewkt(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the
            coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            npoint_as_text
        """
        return npoint_as_text(self._inner, max_decimals)

    @staticmethod
    def from_text(string: str) -> Npoint:
        """
        Returns a :class:`Npoint` from its text, the inverse of :meth:`as_text`.

        Args:
            string: The text representation.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            npoint_in
        """
        return Npoint(_inner=npoint_in(string))

    @staticmethod
    def from_ewkt(ewkt: str) -> Npoint:
        """
        Returns a :class:`Npoint` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            npoint_in
        """
        return Npoint(_inner=npoint_in(ewkt))

    @staticmethod
    def from_ewkb(ewkb: bytes) -> Npoint:
        """
        Returns a :class:`Npoint` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            npoint_from_wkb
        """
        return Npoint(_inner=npoint_from_wkb(ewkb))

    @staticmethod
    def from_hexewkb(hexewkb: str) -> Npoint:
        """
        Returns a :class:`Npoint` from its hex-encoded EWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            npoint_from_hexwkb
        """
        return Npoint(_inner=npoint_from_hexwkb(hexewkb))

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns its Extended Well-Known Binary, its WKB carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            npoint_as_ewkb, wkb_variant_from_endian
        """
        return npoint_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns its Extended Well-Known Binary as a hex-encoded string.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            npoint_as_hexewkb, wkb_variant_from_endian
        """
        return npoint_as_hexewkb(self._inner, wkb_variant_from_endian(endian))[0]

    # ------------------------- Conversions -----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns the geometry represented by ``self``.

        Args:
            precision: The number of decimal places to use for the coordinates.

        Returns:
            A new :class:`~shapely.geometry.base.BaseGeometry` instance.

        MEOS Functions:
            npoint_to_geompoint
        """
        return gserialized_to_shapely_geometry(npoint_to_geompoint(self._inner), precision)

    def to_stbox(self) -> STBox:
        """
        Returns the bounding box of ``self`` as an :class:`STBox`.

        Returns:
            A new :class:`STBox` instance.

        MEOS Functions:
            npoint_to_stbox
        """
        from ...boxes import STBox

        return STBox(_inner=npoint_to_stbox(self._inner))

    # ------------------------- Accessors -------------------------------------
    def route(self) -> int:
        """
        Returns the route identifier of ``self``.

        Returns:
            An :class:`int` with the route identifier of ``self``.

        MEOS Functions:
            npoint_route
        """
        return npoint_route(self._inner)

    def position(self) -> float:
        """
        Returns the relative position of ``self`` along its route.

        Returns:
            A :class:`float` with the relative position of ``self``.

        MEOS Functions:
            npoint_position
        """
        return npoint_position(self._inner)

    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        Returns:
            An :class:`int` with the SRID of ``self``.

        MEOS Functions:
            npoint_srid
        """
        return npoint_srid(self._inner)

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> Npoint:
        """
        Returns a new :class:`Npoint` with the relative position of ``self``
        rounded to ``max_decimals`` decimal places.

        Args:
            max_decimals: The number of decimal places.

        Returns:
            A new :class:`Npoint` instance.

        MEOS Functions:
            npoint_round
        """
        return Npoint(_inner=npoint_round(self._inner, max_decimals))

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` is equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is equal to ``other``, ``False`` otherwise.

        MEOS Functions:
            npoint_eq
        """
        if isinstance(other, self.__class__):
            return npoint_eq(self._inner, other._inner)
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
            npoint_ne
        """
        if isinstance(other, self.__class__):
            return npoint_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Returns whether ``self`` is less than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than ``other``, ``False`` otherwise.

        MEOS Functions:
            npoint_lt
        """
        if isinstance(other, self.__class__):
            return npoint_lt(self._inner, other._inner)
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
            npoint_le
        """
        if isinstance(other, self.__class__):
            return npoint_le(self._inner, other._inner)
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
            npoint_gt
        """
        if isinstance(other, self.__class__):
            return npoint_gt(self._inner, other._inner)
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
            npoint_ge
        """
        if isinstance(other, self.__class__):
            return npoint_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __hash__(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            An :class:`int` with the hash of ``self``.

        MEOS Functions:
            npoint_hash
        """
        return npoint_hash(self._inner)
