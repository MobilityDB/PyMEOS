from __future__ import annotations

from typing import Optional, TYPE_CHECKING

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
        string: Optional[str] = None,
        *,
        rid: Optional[int] = None,
        pos1: Optional[float] = None,
        pos2: Optional[float] = None,
        _inner=None,
    ):
        assert (_inner is not None) or (string is not None) != (
            rid is not None and pos1 is not None and pos2 is not None
        ), (
            "Either string must be not None or rid, pos1 and pos2 must be"
            " not None"
        )
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
    def __str__(self, max_decimals: int = 15) -> str:
        """
        Returns the string representation of ``self``.

        MEOS Functions:
            nsegment_out
        """
        return nsegment_out(self._inner, max_decimals)

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

    # ------------------------- Conversions -----------------------------------
    def to_geometry(self, precision: int = 15) -> shp.BaseGeometry:
        """
        Returns ``self`` as a `shapely`
        :class:`~shapely.geometry.base.BaseGeometry`.

        MEOS Functions:
            nsegment_to_geom
        """
        return gserialized_to_shapely_geometry(
            nsegment_to_geom(self._inner), precision
        )

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
