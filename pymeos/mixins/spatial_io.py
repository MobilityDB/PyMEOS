from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pymeos_cffi import (
    temporal_from_hexwkb,
    temporal_from_wkb,
    tspatial_as_ewkb,
    tspatial_as_ewkt,
    tspatial_as_hexewkb,
    wkb_variant_from_endian,
)

if TYPE_CHECKING:
    from ..temporal import Temporal

Self = TypeVar("Self", bound="Temporal[Any]")


class TSpatialIO:
    """
    The input and output forms carrying the SRID of a spatial temporal value,
    as the SQL ``asEWKT``, ``asEWKB``, ``asHexEWKB`` and their readers write
    and read them; a mixin of the spatial temporal classes as #TSimplifiable
    is of #TPoint, its ``as_ewkt`` the one #TPoint states.
    """

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the Extended Well-Known Text representation of ``self``, its
        text preceded by its SRID.

        Args:
            max_decimals: The number of decimal places of the coordinates.

        Returns:
            A :class:`str` with the EWKT of ``self``.

        MEOS Functions:
            tspatial_as_ewkt
        """
        return tspatial_as_ewkt(self._inner, max_decimals)

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns the Extended Well-Known Binary representation of ``self``, its
        WKB carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            The EWKB of ``self``.

        MEOS Functions:
            tspatial_as_ewkb, wkb_variant_from_endian
        """
        return tspatial_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns the Extended Well-Known Binary representation of ``self`` as a
        hex-encoded string.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` with the hex-encoded EWKB of ``self``.

        MEOS Functions:
            tspatial_as_hexewkb, wkb_variant_from_endian
        """
        return tspatial_as_hexewkb(self._inner, wkb_variant_from_endian(endian))[0]

    @classmethod
    def from_ewkt(cls: type[Self], ewkt: str) -> Self:
        """
        Returns a temporal value from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT.

        Returns:
            A temporal value of the class's type.

        MEOS Functions:
            <type>_in
        """
        return cls.from_text(ewkt)

    @classmethod
    def from_ewkb(cls: type[Self], ewkb: bytes) -> Self:
        """
        Returns a temporal value from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB.

        Returns:
            A temporal value of the class's type.

        MEOS Functions:
            temporal_from_wkb
        """
        from ..temporal import Temporal

        return Temporal._factory(temporal_from_wkb(ewkb))

    @classmethod
    def from_hexewkb(cls: type[Self], hexewkb: str) -> Self:
        """
        Returns a temporal value from its hex-encoded EWKB, the inverse of
        :meth:`as_hexewkb`.

        Args:
            hexewkb: The hex-encoded EWKB.

        Returns:
            A temporal value of the class's type.

        MEOS Functions:
            temporal_from_hexwkb
        """
        from ..temporal import Temporal

        return Temporal._factory(temporal_from_hexwkb(hexewkb))
