from __future__ import annotations

from typing import List, Optional, Union, overload

from pymeos_cffi import *

from .cbuffer import Cbuffer
from ..base import Set


class CbufferSet(Set[Cbuffer]):
    """
    Class for representing a set of :class:`Cbuffer` values.

    ``CbufferSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> CbufferSet(string='{Cbuffer(Point(1 1), 1), Cbuffer(Point(2 2), 2)}')

    Another possibility is to create a ``CbufferSet`` object from a list of
    :class:`Cbuffer` instances.

        >>> CbufferSet(elements=[Cbuffer(point=Point(1, 1), radius=1)])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "cbufferset"

    _parse_function = cbufferset_in
    _parse_value_function = lambda x: (
        cbuffer_in(x) if isinstance(x, str) else x._inner
    )
    _make_function = cbufferset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            cbufferset_out
        """
        return cbufferset_out(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> Cbuffer:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`Cbuffer` instance

        MEOS Functions:
            cbufferset_start_value
        """
        return Cbuffer(_inner=cbufferset_start_value(self._inner))

    def end_element(self) -> Cbuffer:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`Cbuffer` instance

        MEOS Functions:
            cbufferset_end_value
        """
        return Cbuffer(_inner=cbufferset_end_value(self._inner))

    def element_n(self, n: int) -> Cbuffer:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`Cbuffer` instance

        MEOS Functions:
            cbufferset_value_n
        """
        super().element_n(n)
        return Cbuffer(_inner=cbufferset_value_n(self._inner, n + 1)[0])

    def elements(self) -> List[Cbuffer]:
        """
        Returns a list of all elements in ``self``.

        Returns:
            A list of :class:`Cbuffer` instances

        MEOS Functions:
            cbufferset_values
        """
        elems = cbufferset_values(self._inner)
        return [Cbuffer(_inner=elems[i]) for i in range(self.num_elements())]

    # ------------------------- Topological Operations ------------------------

    def contains(self, content: Union[CbufferSet, Cbuffer]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_cbuffer, contains_set_set
        """
        if isinstance(content, Cbuffer):
            return contains_set_cbuffer(self._inner, content._inner)
        else:
            return super().contains(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: Cbuffer) -> Optional[CbufferSet]: ...

    @overload
    def intersection(self, other: CbufferSet) -> Optional[CbufferSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`CbufferSet` or :class:`Cbuffer` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_set_cbuffer, intersection_set_set
        """
        if isinstance(other, Cbuffer):
            result = intersection_set_cbuffer(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        elif isinstance(other, CbufferSet):
            result = intersection_set_set(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[CbufferSet, Cbuffer]) -> Optional[CbufferSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`CbufferSet` or :class:`Cbuffer` instance

        Returns:
            A :class:`CbufferSet` instance or ``None`` if the difference is
            empty.

        MEOS Functions:
            minus_set_cbuffer, minus_set_set
        """
        if isinstance(other, Cbuffer):
            result = minus_set_cbuffer(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        elif isinstance(other, CbufferSet):
            result = minus_set_set(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: Cbuffer) -> Optional[CbufferSet]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`Cbuffer` instance

        Returns:
            A :class:`CbufferSet` instance.

        MEOS Functions:
            minus_cbuffer_set

        See Also:
            :meth:`minus`
        """
        result = minus_cbuffer_set(other._inner, self._inner)
        return CbufferSet(_inner=result) if result is not None else None

    def union(self, other: Union[CbufferSet, Cbuffer]) -> CbufferSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`CbufferSet` or :class:`Cbuffer` instance

        Returns:
            A :class:`CbufferSet` instance.

        MEOS Functions:
            union_set_cbuffer, union_set_set
        """
        if isinstance(other, Cbuffer):
            result = union_set_cbuffer(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        elif isinstance(other, CbufferSet):
            result = union_set_set(self._inner, other._inner)
            return CbufferSet(_inner=result) if result is not None else None
        else:
            return super().union(other)
