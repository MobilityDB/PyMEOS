from __future__ import annotations

from typing import overload

from pymeos_cffi import *

from ..base import Set
from .h3index import H3Index


class H3IndexSet(Set[H3Index]):
    """
    Class for representing a set of :class:`H3Index` values.

    ``H3IndexSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> H3IndexSet(string='{8a2a1072b59ffff, 880326b885fffff}')

    Another possibility is to create a ``H3IndexSet`` object from a list of
    :class:`H3Index` instances or of their texts.

        >>> H3IndexSet(elements=[H3Index('8a2a1072b59ffff'), '880326b885fffff'])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "h3indexset"

    _parse_function = h3indexset_in
    _parse_value_function = lambda x: h3index_in(x) if isinstance(x, str) else x._inner
    _make_function = h3indexset_make

    # ------------------------- Constructors ----------------------------------
    # The SRID forms of a spatial set, as #CbufferSet.from_ewkb and
    # #CbufferSet.as_ewkt carry them.

    @classmethod
    def from_ewkb(cls: type[Self], ewkb: bytes) -> Self:
        """
        Returns a :class:`H3IndexSet` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`H3IndexSet` instance.

        MEOS Functions:
            set_from_wkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_wkb(ewkb))

    @classmethod
    def from_hexewkb(cls: type[Self], hexewkb: str) -> Self:
        """
        Returns a :class:`H3IndexSet` from its HEXEWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`H3IndexSet` instance.

        MEOS Functions:
            set_from_hexwkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_hexwkb(hexewkb))

    @classmethod
    def from_ewkt(cls: type[Self], ewkt: str) -> Self:
        """
        Returns a :class:`H3IndexSet` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`H3IndexSet` instance.

        MEOS Functions:
            h3indexset_in
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

    def start_element(self) -> H3Index:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`H3Index` instance

        MEOS Functions:
            h3indexset_start_value
        """
        return H3Index(_inner=h3indexset_start_value(self._inner))

    def end_element(self) -> H3Index:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`H3Index` instance

        MEOS Functions:
            h3indexset_end_value
        """
        return H3Index(_inner=h3indexset_end_value(self._inner))

    def element_n(self, n: int) -> H3Index:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`H3Index` instance

        MEOS Functions:
            h3indexset_value_n
        """
        super().element_n(n)
        return H3Index(_inner=h3indexset_value_n(self._inner, n + 1))

    def elements(self) -> list[H3Index]:
        """
        Returns a list of all elements in ``self``.

        Returns:
            A list of :class:`H3Index` instances

        MEOS Functions:
            h3indexset_values
        """
        elems, count = h3indexset_values(self._inner)
        return [H3Index(_inner=elems[i]) for i in range(count)]

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: H3IndexSet | H3Index) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_h3index, contains_set_set
        """
        if isinstance(content, H3Index):
            return contains_set_h3index(self._inner, content._inner)
        else:
            return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: H3Index) -> H3IndexSet | None: ...

    @overload
    def intersection(self, other: H3IndexSet) -> H3IndexSet | None: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`H3IndexSet` or :class:`H3Index` instance

        Returns:
            A :class:`H3IndexSet` instance or ``None`` if the intersection is
            empty.

        MEOS Functions:
            intersection_set_h3index, intersection_set_set
        """
        if isinstance(other, H3Index):
            result = intersection_set_h3index(self._inner, other._inner)
            return H3IndexSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: H3IndexSet | H3Index) -> H3IndexSet | None:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`H3IndexSet` or :class:`H3Index` instance

        Returns:
            A :class:`H3IndexSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_set_h3index, minus_set_set
        """
        if isinstance(other, H3Index):
            result = minus_set_h3index(self._inner, other._inner)
            return H3IndexSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: H3Index) -> H3IndexSet | None:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`H3Index` instance

        Returns:
            A :class:`H3IndexSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_h3index_set

        See Also:
            :meth:`minus`
        """
        result = minus_h3index_set(other._inner, self._inner)
        return H3IndexSet(_inner=result) if result is not None else None

    def union(self, other: H3IndexSet | H3Index) -> H3IndexSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`H3IndexSet` or :class:`H3Index` instance

        Returns:
            A :class:`H3IndexSet` instance.

        MEOS Functions:
            union_set_h3index, union_set_set
        """
        if isinstance(other, H3Index):
            return H3IndexSet(_inner=union_set_h3index(self._inner, other._inner))
        else:
            return super().union(other)
