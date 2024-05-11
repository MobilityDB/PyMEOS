from __future__ import annotations

from typing import List, Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import (
    intset_in,
    intset_make,
    intset_out,
    intset_start_value,
    intset_end_value,
    intset_value_n,
    intset_values,
    contains_set_int,
    intersection_set_int,
    intersection_set_set,
    minus_set_int,
    left_set_int,
    overleft_set_int,
    right_set_int,
    overright_set_int,
    minus_set_set,
    union_set_set,
    union_set_int,
    intset_shift_scale,
    minus_int_set,
    distance_set_int,
    distance_intset_intset,
)

from .intspan import IntSpan
from .intspanset import IntSpanSet
from ..base import Set

if TYPE_CHECKING:
    from .floatset import FloatSet


class IntSet(Set[int]):
    """
    Class for representing a set of integer values.

    ``IntSet`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> IntSet(string='{1, 3, 56}')

    Another possibility is to create a ``IntSet`` object from a list of
    strings or integers.

        >>> IntSet(elements=[1, '2', 3, '56'])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "intset"

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

    def to_floatset(self) -> FloatSet:
        """
        Converts ``self`` to a :class:`FloatSet` instance.

        Returns:
            A new :class:`FloatSet` instance
        """
        from .floatset import FloatSet

        return FloatSet(elements=[float(x) for x in self.elements()])

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

    def scale(self, width: int) -> IntSet:
        """
        Returns a new ``IntSet`` instance with all elements scaled to so that the encompassing
        span has width ``width``.

        Args:
            width: The new width.

        Returns:
            A new :class:`IntSet` instance

        MEOS Functions:
            intset_shift_scale
        """
        return self.shift_scale(None, width)

    def shift_scale(self, delta: Optional[int], width: Optional[int]) -> IntSet:
        """
        Returns a new ``IntSet`` instance with all elements shifted by
        ``delta`` and scaled to so that the encompassing span has width
        ``width``.

        Args:
            delta: The value to shift by.
            width: The new width.

        Returns:
            A new :class:`IntSet` instance

        MEOS Functions:
            intset_shift_scale
        """
        return IntSet(
            _inner=intset_shift_scale(
                self._inner, delta, width, delta is not None, width is not None
            )
        )

    # ------------------------- Topological Operations --------------------------------

    def contains(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_set_int
        """
        if isinstance(content, int):
            return contains_set_int(self._inner, content)
        else:
            return super().contains(content)

    # ------------------------- Position Operations --------------------------------

    def is_left(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` is strictly to the left of ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            content: object to compare with

        Returns:
            True if left, False otherwise

        MEOS Functions:
            left_set_set, left_set_int
        """
        if isinstance(content, int):
            return left_set_int(self._inner, content)
        else:
            return super().is_left(content)

    def is_over_or_left(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` is to the left of ``other`` allowing overlap.
        That is, ``self`` ends before ``other`` ends (or at the same value).

        Args:
            content: object to compare with

        Returns:
            True if is over or left, False otherwise

        MEOS Functions:
            overleft_set_set, overleft_set_int
        """
        if isinstance(content, int):
            return overleft_set_int(self._inner, content)
        else:
            return super().is_over_or_left(content)

    def is_right(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` is strictly to the right of ``other``. That is,
        ``self`` ends after ``other`` starts.

        Args:
            content: object to compare with

        Returns:
            True if right, False otherwise

        MEOS Functions:
            right_set_set, right_set_int
        """
        if isinstance(content, int):
            return right_set_int(self._inner, content)
        else:
            return super().is_right(content)

    def is_over_or_right(self, content: Union[IntSet, int]) -> bool:
        """
        Returns whether ``self`` is to the right of ``other`` allowing overlap.
        That is, ``self`` starts before ``other`` ends (or at the same value).

        Args:
            content: object to compare with

        Returns:
            True if is over or right, False otherwise

        MEOS Functions:
            overright_set_set, overright_set_int
        """
        if isinstance(content, int):
            return overright_set_int(self._inner, content)
        else:
            return super().is_over_or_right(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: int) -> Optional[int]: ...

    @overload
    def intersection(self, other: IntSet) -> Optional[IntSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_set_set, intersection_set_int
        """
        if isinstance(other, int):
            return intersection_set_int(self._inner, other)
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
            minus_set_set, minus_set_int
        """
        if isinstance(other, int):
            result = minus_set_int(self._inner, other)
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
            minus_int_set

        See Also:
            :meth:`minus`
        """
        return minus_int_set(other, self._inner)

    def union(self, other: Union[IntSet, int]) -> IntSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`IntSet` or :class:`int` instance

        Returns:
            A :class:`IntSet` instance.

        MEOS Functions:
            union_set_set, union_set_int
        """
        if isinstance(other, int):
            result = union_set_int(self._inner, other)
            return IntSet(_inner=result) if result is not None else None
        elif isinstance(other, IntSet):
            result = union_set_set(self._inner, other._inner)
            return IntSet(_inner=result) if result is not None else None
        else:
            return super().union(other)

    # ------------------------- Distance Operations ---------------------------

    def distance(self, other: Union[int, IntSet, IntSpan, IntSpanSet]) -> int:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A :class:`int` instance

        MEOS Functions:
            distance_set_int, distance_intset_intset, distance_intspanset_intspan,
            distance_intspanset_intspanset
        """
        from .intspan import IntSpan
        from .intspanset import IntSpanSet

        if isinstance(other, int):
            return distance_set_int(self._inner, other)
        elif isinstance(other, IntSet):
            return distance_intset_intset(self._inner, other._inner)
        elif isinstance(other, IntSpan):
            return self.to_spanset().distance(other)
        elif isinstance(other, IntSpanSet):
            return self.to_spanset().distance(other)
        else:
            return super().distance(other)
