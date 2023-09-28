from __future__ import annotations

from typing import List, Union, overload, Optional

from pymeos_cffi import intset_in, intset_make, intset_out, intset_start_value, intset_end_value, \
    intset_value_n, intset_values, contains_intset_int, intersection_intset_int, intersection_set_set, minus_intset_int, \
    minus_set_set, union_set_set, union_intset_int, intset_shift_scale, minus_int_intset, distance_intset_int

from .intspan import IntSpan
from .intspanset import IntSpanSet
from ..base import Set


class IntSet(Set[int]):
    """
    Class for representing a set of text values.

    ``TextSet`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> IntSet(string='{1, 3, 56}')

    Another possibility is to create a ``TextSet`` object from a list of
    strings or integers.

        >>> IntSet(elements=[1, '2', 3, '56'])


    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'intset'

    _parse_function = intset_in
    _parse_value_function = int
    _make_function = intset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            intset_out
        """
        return intset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> IntSpanSet:
        """
        Returns a SpanSet that contains a Span for each element in ``self``.

        Returns:
            A new :class:`IntSpanSet` instance

        MEOS Functions:
            set_to_spanset
        """

        return IntSpanSet(_inner=super().to_spanset())

    def to_span(self) -> IntSpan:
        """
        Returns a span that encompasses ``self``.

        Returns:
            A new :class:`IntSpan` instance

        MEOS Functions:
            set_span
        """
        return IntSpan(_inner=super().to_span())

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> int:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`int` instance

        MEOS Functions:
            intset_start_value
        """
        return intset_start_value(self._inner)

    def end_element(self) -> int:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`int` instance

        MEOS Functions:
            intset_end_value
        """
        return intset_end_value(self._inner)

    def element_n(self, n: int) -> int:
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
        return intset_value_n(self._inner, n + 1)

    def elements(self) -> List[int]:
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`int` instances

        MEOS Functions:
            inttset_values
        """
        elems = intset_values(self._inner)
        return [elems[i] for i in range(self.num_elements())]

    # ------------------------- Transformations ------------------------------------

    def shift(self, delta: int) -> IntSet:
        """
        Returns a new ``IntSet`` instance with all elements shifted by ``delta``.

        Args:
            delta: The value to shift by.

        Returns:
            A new :class:`IntSet` instance

        MEOS Functions:
            intset_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, new_width: int) -> IntSet:
        """
        Returns a new ``IntSet`` instance with all elements scaled to so that the encompassing
        span has width ``new_width``.

        Args:
            new_width: The new width.

        Returns:
            A new :class:`IntSet` instance

        MEOS Functions:
            intset_shift_scale
        """
        return self.shift_scale(None, new_width)

    def shift_scale(self, delta: Optional[int], new_width: Optional[int]) -> IntSet:
        """
        Returns a new ``IntSet`` instance with all elements shifted by ``delta`` and scaled to so that the
         encompassing span has width ``new_width``.

        Args:
            delta: The value to shift by.
            new_width: The new width.

        Returns:
            A new :class:`IntSet` instance

        MEOS Functions:
            intset_shift_scale
        """
        return IntSet(
            _inner=intset_shift_scale(self._inner, delta, new_width, delta is not None, new_width is not None))

    # ------------------------- Topological Operations --------------------------------

    def contains(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_intset_int
        """
        if isinstance(content, int):
            return contains_intset_int(self._inner, content)
        else:
            return super().contains(content)

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
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_set_set, intersection_intset_int
        """
        if isinstance(other, int):
            return intersection_intset_int(self._inner, other)
        elif isinstance(other, IntSet):
            result = intersection_set_set(self._inner, other._inner)
            return IntSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[IntSet, int]) -> Optional[IntSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            A :class:`IntSet` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_set_set, minus_intset_int
        """
        if isinstance(other, int):
            result = minus_intset_int(self._inner, other)
            return IntSet(_inner=result) if result is not None else None
        elif isinstance(other, IntSet):
            result = minus_set_set(self._inner, other._inner)
            return IntSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: int) -> Optional[int]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`int` instance

        Returns:
            A :class:`int` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_int_intset

        See Also:
            :meth:`minus`
        """
        return minus_int_intset(other, self._inner)

    def union(self, other: Union[IntSet, int]) -> IntSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            A :class:`IntSet` instance.

        MEOS Functions:
            union_set_set, union_intset_int
        """
        if isinstance(other, int):
            result = union_intset_int(self._inner, other)
            return IntSet(_inner=result) if result is not None else None
        elif isinstance(other, IntSet):
            result = union_set_set(self._inner, other._inner)
            return IntSet(_inner=result) if result is not None else None
        else:
            return super().union(other)

    # ------------------------- Distance Operations ---------------------------

    def distance(self, other: Union[int, IntSet, IntSpan, IntSpanSet]) -> float:
        if isinstance(other, int):
            return distance_intset_int(self._inner, other)
        else:
            return super().distance(other)
