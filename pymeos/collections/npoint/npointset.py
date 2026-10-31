from __future__ import annotations

from typing import overload

from pymeos_cffi import *

from ..base import Set
from .npoint import Npoint


class NpointSet(Set[Npoint]):
    """
    Class for representing a set of network points.

    ``NpointSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> NpointSet(string='{"NPoint(1, 0.5)", "NPoint(2, 0.3)"}')

    Another possibility is to create a ``NpointSet`` object from a list of
    network points.

        >>> NpointSet(elements=[Npoint(route=1, position=0.5), Npoint(route=2, position=0.3)])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "npointset"

    _parse_function = npointset_in
    _parse_value_function = lambda x: npoint_in(x)[0] if isinstance(x, str) else x._inner[0]
    _make_function = npointset_make

    # ------------------------- Constructors ----------------------------------

    @classmethod
    def from_ewkb(cls: type[Self], ewkb: bytes) -> Self:
        """
        Returns a :class:`NpointSet` from its EWKB, the inverse of :meth:`as_ewkb`.

        Args:
            ewkb: The EWKB representation.

        Returns:
            A new :class:`NpointSet` instance.

        MEOS Functions:
            set_from_wkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_wkb(ewkb))

    @classmethod
    def from_hexewkb(cls: type[Self], hexewkb: str) -> Self:
        """
        Returns a :class:`NpointSet` from its HEXEWKB, the inverse of :meth:`as_hexewkb`.

        Args:
            hexewkb: The HEXEWKB representation.

        Returns:
            A new :class:`NpointSet` instance.

        MEOS Functions:
            set_from_hexwkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_hexwkb(hexewkb))

    @classmethod
    def from_ewkt(cls: type[Self], ewkt: str) -> Self:
        """
        Returns a :class:`NpointSet` from its EWKT, the inverse of :meth:`as_ewkt`.

        Args:
            ewkt: The EWKT representation.

        Returns:
            A new :class:`NpointSet` instance.

        MEOS Functions:
            <type>_in
        """
        return cls.from_text(ewkt)

    def as_ewkb(self, endian: str = "") -> bytes:
        """
        Returns the EWKB representation of ``self``, carrying its SRID.

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
        Returns the HEXEWKB representation of ``self``, carrying its SRID.

        Args:
            endian: The byte order, ``"NDR"``, ``"XDR"`` or ``""`` for the
                machine's own.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_hexewkb, wkb_variant_from_endian
        """
        return spatialset_as_hexewkb(self._inner, wkb_variant_from_endian(endian))[0]

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            spatialset_as_text
        """
        return self.as_text(max_decimals)

    def as_ewkt(self, max_decimals: int = 15) -> str:
        """
        Returns the EWKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_ewkt
        """
        return spatialset_as_ewkt(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_text
        """
        return spatialset_as_text(self._inner, max_decimals)

    def as_text(self, max_decimals: int = 15) -> str:
        """
        Returns the WKT representation of ``self``.

        Args:
            max_decimals: The number of decimal places to use for the coordinates.

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            spatialset_as_text
        """
        return spatialset_as_text(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------
    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------
    def start_element(self) -> Npoint:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`Npoint` instance

        MEOS Functions:
            npointset_start_value
        """
        return Npoint(_inner=npointset_start_value(self._inner))

    def end_element(self) -> Npoint:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`Npoint` instance

        MEOS Functions:
            npointset_end_value
        """
        return Npoint(_inner=npointset_end_value(self._inner))

    def element_n(self, n: int) -> Npoint:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`Npoint` instance

        MEOS Functions:
            npointset_value_n
        """
        super().element_n(n)
        return Npoint(_inner=npointset_value_n(self._inner, n + 1)[0])

    def elements(self) -> list[Npoint]:
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`Npoint` instances

        MEOS Functions:
            npointset_values
        """
        elems = npointset_values(self._inner)
        return [Npoint(_inner=elems[i]) for i in range(self.num_elements())]

    def routes(self) -> Set[int]:
        """
        Returns the set of route identifiers of the elements in ``self``.

        Returns:
            A new :class:`Set` instance with the route identifiers.

        MEOS Functions:
            npointset_routes
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(npointset_routes(self._inner))

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: NpointSet | Npoint) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_npoint, contains_set_set
        """
        if isinstance(content, Npoint):
            return contains_set_npoint(self._inner, content._inner)
        else:
            return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: Npoint) -> NpointSet | None: ...

    @overload
    def intersection(self, other: NpointSet) -> NpointSet | None: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`NpointSet` or :class:`Npoint` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_set_npoint, intersection_set_set
        """
        if isinstance(other, Npoint):
            result = intersection_set_npoint(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        elif isinstance(other, NpointSet):
            result = intersection_set_set(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: NpointSet | Npoint) -> NpointSet | None:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`NpointSet` or :class:`Npoint` instance

        Returns:
            A :class:`NpointSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_set_npoint, minus_set_set
        """
        if isinstance(other, Npoint):
            result = minus_set_npoint(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        elif isinstance(other, NpointSet):
            result = minus_set_set(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: Npoint) -> NpointSet | None:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`Npoint` instance

        Returns:
            A :class:`NpointSet` instance.

        MEOS Functions:
            minus_npoint_set

        See Also:
            :meth:`minus`
        """
        result = minus_npoint_set(other._inner, self._inner)
        return NpointSet(_inner=result) if result is not None else None

    def union(self, other: NpointSet | Npoint) -> NpointSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`NpointSet` or :class:`Npoint` instance

        Returns:
            A :class:`NpointSet` instance.

        MEOS Functions:
            union_set_npoint, union_set_set
        """
        if isinstance(other, Npoint):
            result = union_set_npoint(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        elif isinstance(other, NpointSet):
            result = union_set_set(self._inner, other._inner)
            return NpointSet(_inner=result) if result is not None else None
        else:
            return super().union(other)
