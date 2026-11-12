from __future__ import annotations

from typing import TYPE_CHECKING

from pymeos_cffi import *

if TYPE_CHECKING:
    from ...boxes import STBox
    from .h3indexset import H3IndexSet


class H3Index:
    """
    Class for representing an H3 cell index, the 64-bit identifier of a cell of the H3 hexagonal grid.

    MEOS holds a cell by value, as an unsigned 64-bit integer, so a
    ``H3Index`` holds that integer where the other base classes hold a pointer.
    A cell carries no SRID, its grid fixing it.

    ``H3Index`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> H3Index('8a2a1072b59ffff')

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "h3index"

    # ------------------------- Constructors ----------------------------------
    def __init__(self, string: str | None = None, *, _inner: int | None = None):
        assert (_inner is not None) != (string is not None), "Either string or _inner must be not None"
        if _inner is not None:
            self._inner = _inner
        else:
            self._inner = h3index_in(string)

    @staticmethod
    def from_text(string: str) -> H3Index:
        """
        Returns a :class:`H3Index` from its text, the inverse of :meth:`as_text`.

        Args:
            string: The text representation.

        Returns:
            A new :class:`H3Index` instance.

        MEOS Functions:
            h3index_in
        """
        return H3Index(_inner=h3index_in(string))

    @staticmethod
    def from_wkb(wkb: bytes) -> H3Index:
        """
        Returns a :class:`H3Index` from its WKB representation.

        Args:
            wkb: WKB representation

        Returns:
            A new :class:`H3Index` instance

        MEOS Functions:
            h3index_from_wkb
        """
        return H3Index(_inner=h3index_from_wkb(wkb))

    @staticmethod
    def from_hexwkb(hexwkb: str) -> H3Index:
        """
        Returns a :class:`H3Index` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`H3Index` instance

        MEOS Functions:
            h3index_from_hexwkb
        """
        return H3Index(_inner=h3index_from_hexwkb(hexwkb))

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns the text representation of ``self``, its :meth:`as_text`.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            h3index_out
        """
        return self.as_text()

    def __repr__(self):
        """
        Returns the string representation of ``self``.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            h3index_out
        """
        return f"{self.__class__.__name__}({self})"

    def as_text(self) -> str:
        """
        Returns the text representation of ``self``, the hexadecimal digits of
        the cell.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            h3index_out
        """
        return h3index_out(self._inner)

    def as_wkb(self, endian: str = "") -> bytes:
        """
        Returns the WKB representation of ``self``.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` object with the WKB representation of ``self``.

        MEOS Functions:
            h3index_as_wkb, wkb_variant_from_endian
        """
        return h3index_as_wkb(self._inner, wkb_variant_from_endian(endian))

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
            h3index_as_hexwkb, wkb_variant_from_endian
        """
        return h3index_as_hexwkb(self._inner, wkb_variant_from_endian(endian))

    # ------------------------- Conversions -----------------------------------
    def to_set(self) -> H3IndexSet:
        """
        Returns the set holding ``self`` alone.

        Returns:
            A new :class:`H3IndexSet` instance.

        MEOS Functions:
            h3index_to_set
        """
        from .h3indexset import H3IndexSet

        return H3IndexSet(_inner=h3index_to_set(self._inner))

    def to_stbox(self) -> STBox:
        """
        Returns the bounding box of the cell ``self``.

        Returns:
            A new :class:`~pymeos.boxes.STBox` instance.

        MEOS Functions:
            h3index_to_stbox
        """
        from ...boxes import STBox

        return STBox(_inner=h3index_to_stbox(self._inner))

    def cell_to_parent(self, resolution: int) -> H3Index:
        """
        Returns the cell of the coarser resolution ``resolution`` that contains ``self``.

        Args:
            resolution: The resolution of the parent.

        Returns:
            A new :class:`H3Index` instance.

        MEOS Functions:
            h3index_cell_to_parent
        """
        return H3Index(_inner=h3index_cell_to_parent(self._inner, resolution))

    # ------------------------- Accessors -------------------------------------
    def get_resolution(self) -> int:
        """
        Returns the resolution of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            h3index_get_resolution
        """
        return h3index_get_resolution(self._inner)

    def cell_area(self) -> float:
        """
        Returns the area of the cell ``self`` in square meters.

        Returns:
            A :class:`float` instance.

        MEOS Functions:
            h3index_cell_area
        """
        return h3index_cell_area(self._inner)

    def hash(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            h3index_hash
        """
        return h3index_hash(self._inner)

    def __hash__(self) -> int:
        """
        Returns the hash of ``self``.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            h3index_hash
        """
        return h3index_hash(self._inner)

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` is equal to ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is equal to ``other``, ``False`` otherwise.

        MEOS Functions:
            h3index_eq
        """
        if isinstance(other, self.__class__):
            return h3index_eq(self._inner, other._inner)
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
            h3index_ne
        """
        if isinstance(other, self.__class__):
            return h3index_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Returns whether ``self`` is less than ``other``.

        Args:
            other: The object to compare with ``self``.

        Returns:
            ``True`` if ``self`` is less than ``other``, ``False`` otherwise.

        MEOS Functions:
            h3index_lt
        """
        if isinstance(other, self.__class__):
            return h3index_lt(self._inner, other._inner)
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
            h3index_le
        """
        if isinstance(other, self.__class__):
            return h3index_le(self._inner, other._inner)
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
            h3index_gt
        """
        if isinstance(other, self.__class__):
            return h3index_gt(self._inner, other._inner)
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
            h3index_ge
        """
        if isinstance(other, self.__class__):
            return h3index_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def cmp(self, other: H3Index) -> int:
        """
        Returns -1, 0, or 1 depending on whether ``self`` is less than, equal
        to, or greater than ``other``.

        Args:
            other: A :class:`H3Index` instance.

        Returns:
            An :class:`int` instance.

        MEOS Functions:
            h3index_cmp
        """
        return h3index_cmp(self._inner, other._inner)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`H3Index` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return H3Index(string=value)
