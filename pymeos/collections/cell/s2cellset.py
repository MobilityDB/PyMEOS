from __future__ import annotations

from typing import overload

from pymeos_cffi import *

from ..base import Set
from .s2cell import S2Cell


class S2CellSet(Set[S2Cell]):
    """
    Class for representing a set of :class:`S2Cell` values.

    ``S2CellSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> S2CellSet(string='{47c3c444c, 47c3c3}')

    Another possibility is to create a ``S2CellSet`` object from a list of
    :class:`S2Cell` instances or of their texts.

        >>> S2CellSet(elements=[S2Cell('47c3c444c'), '47c3c3'])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "s2cellset"

    _parse_function = s2cellset_in
    _parse_value_function = lambda x: s2cell_in(x) if isinstance(x, str) else x._inner
    _make_function = s2cellset_make

    # ------------------------- Constructors ----------------------------------
    # The SRID forms of a spatial set, as #CbufferSet.from_ewkb and
    # #CbufferSet.as_ewkt carry them.

    @classmethod
    def from_ewkb(cls: type[Self], ewkb: bytes) -> Self:
        """
        Returns a :class:`S2CellSet` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`S2CellSet` instance.

        MEOS Functions:
            set_from_wkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_wkb(ewkb))

    @classmethod
    def from_hexewkb(cls: type[Self], hexewkb: str) -> Self:
        """
        Returns a :class:`S2CellSet` from its HEXEWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`S2CellSet` instance.

        MEOS Functions:
            set_from_hexwkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_hexwkb(hexewkb))

    @classmethod
    def from_ewkt(cls: type[Self], ewkt: str) -> Self:
        """
        Returns a :class:`S2CellSet` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`S2CellSet` instance.

        MEOS Functions:
            s2cellset_in
        """
        return cls.from_text(ewkt)

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns the EWKB representation of ``self``, carrying the SRID of its
        bounding box.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`bytes` instance.

        MEOS Functions:
            spatialset_as_ewkb, wkb_variant_from_endian
        """
        return spatialset_as_ewkb(self._inner, wkb_variant_from_endian(endian))

    def as_hexewkb(self, endian: str = "") -> str:
        """
        Returns the HEXEWKB representation of ``self``, carrying the SRID of its
        bounding box.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_hexewkb, wkb_variant_from_endian
        """
        return spatialset_as_hexewkb(self._inner, wkb_variant_from_endian(endian))

    # ------------------------- Output ----------------------------------------

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``, its text preceded by the
        SRID of its bounding box.

        Args:
            max_decimals: The number of decimal places, as the catalog's
                writer takes it.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_ewkt
        """
        return spatialset_as_ewkt(self._inner, max_decimals)

    def __str__(self) -> str:
        """
        Returns the text representation of ``self``, its :meth:`as_text`.
        """
        return self.as_text()

    def as_text(self) -> str:
        """
        Return the text representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            set_out
        """
        return set_out(self._inner, 0)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> S2Cell:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`S2Cell` instance

        MEOS Functions:
            s2cellset_start_value
        """
        return S2Cell(_inner=s2cellset_start_value(self._inner))

    def end_element(self) -> S2Cell:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`S2Cell` instance

        MEOS Functions:
            s2cellset_end_value
        """
        return S2Cell(_inner=s2cellset_end_value(self._inner))

    def element_n(self, n: int) -> S2Cell:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`S2Cell` instance

        MEOS Functions:
            s2cellset_value_n
        """
        super().element_n(n)
        return S2Cell(_inner=s2cellset_value_n(self._inner, n + 1))

    def elements(self) -> list[S2Cell]:
        """
        Returns a list of all elements in ``self``.

        Returns:
            A list of :class:`S2Cell` instances

        MEOS Functions:
            s2cellset_values
        """
        elems, count = s2cellset_values(self._inner)
        return [S2Cell(_inner=elems[i]) for i in range(count)]

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: S2CellSet | S2Cell) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_s2cell, contains_set_set
        """
        if isinstance(content, S2Cell):
            return contains_set_s2cell(self._inner, content._inner)
        else:
            return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: S2Cell) -> S2CellSet | None: ...

    @overload
    def intersection(self, other: S2CellSet) -> S2CellSet | None: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`S2CellSet` or :class:`S2Cell` instance

        Returns:
            A :class:`S2CellSet` instance or ``None`` if the intersection is
            empty.

        MEOS Functions:
            intersection_set_s2cell, intersection_set_set
        """
        if isinstance(other, S2Cell):
            result = intersection_set_s2cell(self._inner, other._inner)
            return S2CellSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: S2CellSet | S2Cell) -> S2CellSet | None:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`S2CellSet` or :class:`S2Cell` instance

        Returns:
            A :class:`S2CellSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_set_s2cell, minus_set_set
        """
        if isinstance(other, S2Cell):
            result = minus_set_s2cell(self._inner, other._inner)
            return S2CellSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: S2Cell) -> S2CellSet | None:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`S2Cell` instance

        Returns:
            A :class:`S2CellSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_s2cell_set

        See Also:
            :meth:`minus`
        """
        result = minus_s2cell_set(other._inner, self._inner)
        return S2CellSet(_inner=result) if result is not None else None

    def union(self, other: S2CellSet | S2Cell) -> S2CellSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`S2CellSet` or :class:`S2Cell` instance

        Returns:
            A :class:`S2CellSet` instance.

        MEOS Functions:
            union_set_s2cell, union_set_set
        """
        if isinstance(other, S2Cell):
            return S2CellSet(_inner=union_set_s2cell(self._inner, other._inner))
        else:
            return super().union(other)
