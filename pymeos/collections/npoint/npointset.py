from __future__ import annotations

from typing import List, Optional, Union

from pymeos_cffi import (
    npointset_in,
    npointset_out,
    npointset_make,
    npointset_start_value,
    npointset_end_value,
    npointset_value_n,
    npointset_values,
    npointset_routes,
    npoint_in,
)

from ..base import Set
from .npoint import Npoint


def _npointset_make(values: List["CData"]) -> "CData":
    return npointset_make(values, len(values))


class NpointSet(Set[Npoint]):
    """
    Class for representing a set of network points.

    ``NpointSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> NpointSet(string='{NPoint(1, 0.5), NPoint(2, 0.3)}')

    Another possibility is to create a ``NpointSet`` object from a list of
    network points.

        >>> NpointSet(elements=[Npoint(1, 0.5), Npoint(2, 0.3)])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "npointset"

    _parse_function = npointset_in
    _parse_value_function = lambda x: (
        npoint_in(x)._inner if isinstance(x, str) else x._inner
    )
    _make_function = _npointset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            npointset_out
        """
        return npointset_out(self._inner, max_decimals)

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

    def elements(self) -> List[Npoint]:
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
