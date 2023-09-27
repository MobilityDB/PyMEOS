from __future__ import annotations

from typing import Optional, overload, Union

from pymeos_cffi import *

from .. import Span, SpanSet
from ..base import Set


class IntSet(Set[int]):
    """
    Class for representing a set of text values.

    ``IntSet`` objects can be created with a single argument of type integer as
    in MobilityDB.

        >>> IntSet(string='{1, 2, 3, 4}')

    Another possibility is to create a ``IntSet`` object from a list of integers.

        >>> IntSet(elements=[1, 2, 3, 4])


    """

    __slots__ = ['_inner']

    _parse_function = intset_in
    _parse_value_function = lambda x: x
    _make_function = intset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            intset_out
        """
        return intset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> SpanSet:
        raise NotImplementedError()

    def to_span(self) -> Span:
        raise NotImplementedError()

    # ------------------------- Accessors -------------------------------------

    def start_element(self):
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`int` instance

        MEOS Functions:
            intset_start_value
        """
        return intset_start_value(self._inner)

    def end_element(self):
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`int` instance

        MEOS Functions:
            intset_end_value
        """
        return intset_end_value(self._inner)

    def element_n(self, n: int):
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`int` instance

        MEOS Functions:
            intset_value_n
        """
        super().element_n(n)
        return intset_value_n(self._inner, n)

    def elements(self):
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`int` instances

        MEOS Functions:
            intset_values
        """
        elems = intset_values(self._inner)
        return [elems[i] for i in range(self.num_elements())]

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: int) -> Optional[int]:
        ...

    @overload
    def intersection(self, other: IntSet) -> Optional[IntSet]:
        ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the intersection is empty.

        MEOS Functions:
            intersection_intset_text, intersection_set_set
        """
        if isinstance(other, int):
            return intersection_intset_text(self._inner, other)
        elif isinstance(other, IntSet):
            result = super().intersection(other)
            return IntSet(elements=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[IntSet, int]) -> Optional[IntSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            A :class:`IntSet` instance.

        MEOS Functions:
            minus_intset_text, minus_set_set
        """
        if isinstance(other, int):
            result = minus_intset_text(self._inner, other)
            return IntSet(elements=result) if result is not None else None
        elif isinstance(other, IntSet):
            result = super().minus(other)
            return IntSet(elements=result) if result is not None else None
        else:
            return super().minus(other)

    def union(self, other: Union[IntSet, int]) -> IntSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            A :class:`IntSet` instance.

        MEOS Functions:
            union_intset_text, union_set_set
        """
        if isinstance(other, int):
            result = union_intset_text(self._inner, other)
            return IntSet(elements=result) if result is not None else None
        elif isinstance(other, IntSet):
            result = super().union(other)
            return IntSet(elements=result) if result is not None else None
        else:
            return super().union(other)
