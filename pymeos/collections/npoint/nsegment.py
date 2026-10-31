from __future__ import annotations

from typing import TYPE_CHECKING

import shapely.geometry.base as shp
from pymeos_cffi import *

if TYPE_CHECKING:
    from ...boxes import STBox


class Nsegment:
    """
    Class for representing a network segment, that is, a route identifier
    together with a start and end position along that route.

    ``Nsegment`` objects can be created with a single string argument as in
    MobilityDB.

        >>> Nsegment('NSegment(1, 0.2, 0.6)')

    Another possibility is to provide the ``rid``, ``pos1`` and ``pos2``
    arguments.

        >>> Nsegment(rid=1, pos1=0.2, pos2=0.6)
    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "nsegment"

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: str | None = None,
        *,
        rid: int | None = None,
        pos1: float | None = None,
        pos2: float | None = None,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (
            rid is not None and pos1 is not None and pos2 is not None
        ), "Either string must be not None or rid, pos1 and pos2 must be not None"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = nsegment_in(string)
        else:
            self._inner = nsegment_make(rid, float(pos1), float(pos2))

    def __copy__(self) -> Nsegment:
        """
        Returns a copy of ``self``.

        MEOS Functions:
            nsegment_round
        """
        return Nsegment(_inner=nsegment_round(self._inner, 100))

    # ------------------------- Output ----------------------------------------
    def __str__(self) -> str:
        """
        Returns the text representation of ``self``, its :meth:`as_text`.
        """
        return self.as_text()

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the string representation of ``self``.

        MEOS Functions:
            nsegment_as_text
        """
        return nsegment_as_text(self._inner, max_decimals)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    # ------------------------- Accessors -------------------------------------
    def route(self) -> int:
        """
        Returns the route identifier of ``self``.

        MEOS Functions:
            nsegment_route
        """
        return nsegment_route(self._inner)

    def start_position(self) -> float:
        """
        Returns the start position of ``self``.

        MEOS Functions:
            nsegment_start_position
        """
        return nsegment_start_position(self._inner)

    def end_position(self) -> float:
        """
        Returns the end position of ``self``.

        MEOS Functions:
            nsegment_end_position
        """
        return nsegment_end_position(self._inner)

    def srid(self) -> int:
        """
        Returns the SRID of ``self``.

        MEOS Functions:
            nsegment_srid
        """
        return nsegment_srid(self._inner)

    @staticmethod
    def from_text(string: str) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its text, the inverse of :meth:`as_text`.

        Args:
            string: The text representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_in
        """
        return Nsegment(_inner=nsegment_in(string))

    @staticmethod
    def from_ewkt(ewkt: str) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_in
        """
        return Nsegment(_inner=nsegment_in(ewkt))

    @staticmethod
    def from_wkb(wkb: bytes) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its WKB, the inverse of :meth:`as_wkb`.

        Args:
            wkb: The WKB representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_from_wkb
        """
        return Nsegment(_inner=nsegment_from_wkb(wkb))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its hex-encoded WKB, the inverse of :meth:`as_hexwkb`.

        Args:
            hexwkb: The HEXWKB representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_from_hexwkb
        """
        return Nsegment(_inner=nsegment_from_hexwkb(hexwkb))

    @staticmethod
    def from_ewkb(ewkb: bytes) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_from_wkb
        """
        return Nsegment(_inner=nsegment_from_wkb(ewkb))

    @staticmethod
    def from_hexewkb(hexewkb: str) -> Nsegment:
        """
        Returns a :class:`Nsegment` from its hex-encoded EWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`Nsegment` instance.

        MEOS Functions:
            nsegment_from_hexwkb
        """
        return Nsegment(_inner=nsegment_from_hexwkb(hexewkb))

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns its Extended Well-Known Text, its text preceded by its SRID.

        Args:
            max_decimals: The number of decimal places of the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            nsegment_as_ewkt
        """
        return nsegment_as_ewkt(self._inner, max_decimals)

    def as_wkb(self, endian: str = "") -> bytes:
        """
        Returns its plain Well-Known Binary, as the SQL ``asBinary`` writes it.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            nsegment_as_wkb, wkb_variant_from_endian
        """
        return nsegment_as_wkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexwkb(self, endian: str = "") -> str:
        """
        Returns its plain Well-Known Binary as a hex-encoded string, as the SQL ``asHexWKB`` writes it.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            nsegment_as_hexwkb, wkb_variant_from_endian
        """
        return nsegment_as_hexwkb(self._inner, wkb_variant_from_endian(endian))[0]

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns its Extended Well-Known Binary, its WKB carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            nsegment_as_ewkb, wkb_variant_from_endian
        """
        return nsegment_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns its Extended Well-Known Binary as a hex-encoded string.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            nsegment_as_hexewkb, wkb_variant_from_endian
        """
        return nsegment_as_hexewkb(self._inner, wkb_variant_from_endian(endian))[0]

    # ------------------------- Conversions -----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns ``self`` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        MEOS Functions:
            nsegment_to_geom
        """
        return gserialized_to_shapely_geometry(nsegment_to_geom(self._inner), precision)

    def to_stbox(self) -> STBox:
        """
        Returns the bounding box of ``self``.

        MEOS Functions:
            nsegment_to_stbox
        """
        from ...boxes import STBox

        return STBox(_inner=nsegment_to_stbox(self._inner))

    # ------------------------- Transformations -------------------------------
    def round(self, max_decimals: int = 0) -> Nsegment:
        """
        Returns ``self`` with the positions rounded to a number of decimals.

        MEOS Functions:
            nsegment_round
        """
        return Nsegment(_inner=nsegment_round(self._inner, max_decimals))

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other) -> bool:
        if isinstance(other, Nsegment):
            return str(self) == str(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(str(self))
