from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, TypeVar

from pymeos_cffi import *

from ..mixins import TSpatialIO
from ..temporal import Temporal

if TYPE_CHECKING:
    from ..boxes import STBox
    from .tbool import TBool
    from .tfloat import TFloat
    from .tint import TInt
    from .tpoint import TPoint

TBase = TypeVar("TBase")
TG = TypeVar("TG", bound="TCellIndex")
TI = TypeVar("TI", bound="TInstant[Any]")
TS = TypeVar("TS", bound="TSequence[Any]")
TSS = TypeVar("TSS", bound="TSequenceSet[Any]")
Self = TypeVar("Self", bound="TCellIndex")


class TCellIndex(Temporal[TBase, TG, TI, TS, TSS], TSpatialIO, ABC):
    """
    Abstract class for temporal cells of a discrete global grid, the
    :class:`TH3Index`, :class:`TQuadbin` and :class:`TS2Cell` classes, as
    #TPoint is of the temporal points. Its text output is #TInt.__str__'s,
    through the template writer, its bounding box, SRID and ever and never
    comparisons #TCbuffer.bounding_box's, #TCbuffer.srid's and
    #TCbuffer.never_equal's. A cell carries no SRID, its grid fixing it, and a
    temporal cell carries that SRID in its bounding box, from which
    #TSpatialIO.as_ewkt writes it.
    """

    # ------------------------- Output ----------------------------------------
    def __str__(self) -> str:
        """
        Returns the text representation of ``self``, its :meth:`as_text`.
        """
        return self.as_text()

    def as_text(self) -> str:
        """
        Returns the text representation of ``self``, each cell written as
        its hexadecimal digits.

        Returns:
            A :class:`str` with the text representation of ``self``.

        MEOS Functions:
            temporal_out
        """
        return temporal_out(self._inner, 0)

    def as_wkt(self) -> str:
        """
        Returns the text representation of ``self``, its :meth:`as_text`.

        Returns:
            A :class:`str` with the text representation of ``self``.

        MEOS Functions:
            temporal_out
        """
        return temporal_out(self._inner, 0)

    # ------------------------- Accessors -------------------------------------
    def bounding_box(self) -> STBox:
        """
        Returns the bounding box of ``self``.

        Returns:
            An :class:`~pymeos.boxes.STBox` representing the bounding box.

        MEOS Functions:
            tspatial_to_stbox
        """
        from ..boxes import STBox

        return STBox(_inner=tspatial_to_stbox(self._inner))

    def srid(self) -> int:
        """
        Returns the SRID of ``self``, the one its grid fixes, as #TCbuffer.srid
        returns that of a temporal circular buffer.

        Returns:
            An :class:`int` representing the SRID.

        MEOS Functions:
            tspatial_srid
        """
        return tspatial_srid(self._inner)

    def get_resolution(self) -> TInt:
        """
        Returns the resolution of the cells of ``self`` as a temporal integer.

        Returns:
            A new :class:`TInt`.

        MEOS Functions:
            tcellindex_get_resolution
        """
        return Temporal._factory(tcellindex_get_resolution(self._inner))

    def is_valid_cell(self) -> TBool:
        """
        Returns whether the cells of ``self`` are valid cells of their grid,
        as a temporal boolean.

        Returns:
            A new :class:`TBool`.

        MEOS Functions:
            tcellindex_is_valid_cell
        """
        return Temporal._factory(tcellindex_is_valid_cell(self._inner))

    def cell_area(self) -> TFloat:
        """
        Returns the area of the cells of ``self`` in square meters, as a
        temporal float.

        Returns:
            A new :class:`TFloat`.

        MEOS Functions:
            tcellindex_cell_area
        """
        return Temporal._factory(tcellindex_cell_area(self._inner))

    # ------------------------- Conversions -----------------------------------
    def cell_to_parent(self: Self, resolution: int) -> Self:
        """
        Returns the cells of the coarser ``resolution`` containing the cells
        of ``self``.

        Args:
            resolution: The resolution of the parents.

        Returns:
            A new temporal cell of the class of ``self``.

        MEOS Functions:
            tcellindex_cell_to_parent
        """
        return Temporal._factory(tcellindex_cell_to_parent(self._inner, resolution))

    def cell_to_point(self) -> TPoint:
        """
        Returns the centers of the cells of ``self`` as a temporal point, a
        :class:`TGeomPoint` for a Quadbin cell and a :class:`TGeogPoint` for an
        H3 or S2 cell.

        Returns:
            A new :class:`TPoint`.

        MEOS Functions:
            tcellindex_cell_to_point
        """
        return Temporal._factory(tcellindex_cell_to_point(self._inner))

    # ------------------------- Ever and Always Comparisons -------------------
    def never_equal(self, value) -> bool:
        """
        Returns whether the values of ``self`` are never equal to ``value``.

        Args:
            value: A cell, a set of cells or a temporal cell of the grid of
                ``self``.

        Returns:
            ``True`` if the values of ``self`` are never equal to ``value``,
            ``False`` otherwise.

        MEOS Functions:
            ever_eq_<type>_<type>
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value) -> bool:
        """
        Returns whether the values of ``self`` are never not equal to
        ``value``.

        Args:
            value: A cell or a temporal cell of the grid of ``self``.

        Returns:
            ``True`` if the values of ``self`` are never not equal to
            ``value``, ``False`` otherwise.

        MEOS Functions:
            ever_ne_<type>_<type>
        """
        return not self.ever_not_equal(value)
