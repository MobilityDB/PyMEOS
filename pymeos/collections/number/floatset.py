from __future__ import annotations

from typing import List, Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import (
    floatset_in,
    floatset_make,
    floatset_out,
    floatset_start_value,
    floatset_end_value,
    floatset_value_n,
    floatset_values,
    contains_set_float,
    intersection_set_float,
    intersection_set_set,
    left_set_float,
    overleft_set_float,
    right_set_float,
    overright_set_float,
    minus_set_float,
    minus_set_set,
    union_set_set,
    union_set_float,
    floatset_shift_scale,
    minus_float_set,
    distance_set_float,
    distance_floatset_floatset,
)

from .floatspan import FloatSpan
from .floatspanset import FloatSpanSet
from ..base import Set

if TYPE_CHECKING:
    from .intset import IntSet


class FloatSet(Set[float]):
    """
    Class for representing a set of text values.

    ``TextSet`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> FloatSet(string='{1, 3, 56}')

    Another possibility is to create a ``TextSet`` object from a list of
    strings or floats.

        >>> FloatSet(elements=[1, '2', 3, '56'])


    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "floatset"

    _parse_function = floatset_in
    _parse_value_function = float
    _make_function = floatset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            floatset_out
        """
        return floatset_out(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_intset(self) -> IntSet:
        """
        Converts ``self`` to an :class:`IntSet` instance.

        Returns:
            A new :class:`IntSet` instance
        """
        from .intset import IntSet

        return IntSet(elements=[int(x) for x in self.elements()])

    # ------------------------- Accessors -------------------------------------

    def start_element(self) -> float:
        """
        Returns the first element in ``self``.

        Returns:
            A :class:`float` instance

        MEOS Functions:
            floatset_start_value
        """
        return floatset_start_value(self._inner)

    def end_element(self) -> float:
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`float` instance

        MEOS Functions:
            floatset_end_value
        """
        return floatset_end_value(self._inner)

    def element_n(self, n: int) -> float:
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`float` instance

        MEOS Functions:
            floatset_value_n
        """
        super().element_n(n)
        return floatset_value_n(self._inner, n + 1)

    def elements(self) -> List[float]:
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`float` instances

        MEOS Functions:
            floattset_values
        """
        elems = floatset_values(self._inner)
        return [elems[i] for i in range(self.num_elements())]

    # ------------------------- Transformations ------------------------------------

    def shift(self, delta: float) -> FloatSet:
        """
        Returns a new ``FloatSet`` instance with all elements shifted by ``delta``.

        Args:
            delta: The value to shift by.

        Returns:
            A new :class:`FloatSet` instance

        MEOS Functions:
            floatset_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, new_width: float) -> FloatSet:
        """
        Returns a new ``FloatSet`` instance with all elements scaled to so that the encompassing
        span has width ``new_width``.

        Args:
            new_width: The new width.

        Returns:
            A new :class:`FloatSet` instance

        MEOS Functions:
            floatset_shift_scale
        """
        return self.shift_scale(None, new_width)

    def shift_scale(
        self, delta: Optional[float], new_width: Optional[float]
    ) -> FloatSet:
        """
        Returns a new ``FloatSet`` instance with all elements shifted by ``delta`` and scaled to so that the
         encompassing span has width ``new_width``.

        Args:
            delta: The value to shift by.
            new_width: The new width.

        Returns:
            A new :class:`FloatSet` instance

        MEOS Functions:
            floatset_shift_scale
        """
        return FloatSet(
            _inner=floatset_shift_scale(
                self._inner, delta, new_width, delta is not None, new_width is not None
            )
        )

    # ------------------------- Topological Operations --------------------------------

    def contains(self, content: Union[FloatSet, float]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_set_float
        """
        if isinstance(content, float):
            return contains_set_float(self._inner, content)
        else:
            return super().contains(content)

    # ------------------------- Position Operations --------------------------------

    def is_left(self, content: Union[FloatSet, float]) -> bool:
        """
        Returns whether ``self`` is strictly to the left of ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            left_set_set, left_set_float
        """
        if isinstance(content, float):
            return left_set_float(self._inner, content)
        else:
            return super().is_left(content)

    def is_over_or_left(self, content: Union[FloatSet, float]) -> bool:
        """
        Returns whether ``self`` is to the left of ``other`` allowing overlap.
        That is, ``self`` ends before ``other`` ends (or at the same value).

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            overleft_set_set, overleft_set_float
        """
        if isinstance(content, float):
            return overleft_set_float(self._inner, content)
        else:
            return super().is_over_or_left(content)

    def is_right(self, content: Union[FloatSet, float]) -> bool:
        """
        Returns whether ``self`` is strictly to the left of ``other``. That is,
        ``self`` starts before ``other`` ends.

        Args:
            content: object to compare with

        Returns:
            True if is rigth, False otherwise

        MEOS Functions:
            right_set_set, right_set_float
        """
        if isinstance(content, float):
            return right_set_float(self._inner, content)
        else:
            return super().is_right(content)

    def is_over_or_right(self, content: Union[FloatSet, float]) -> bool:
        """
        Returns whether ``self`` is to the right of ``other`` allowing overlap.
        That is, ``self`` ends after ``other`` ends (or at the same value).

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            overright_set_set, overright_set_float
        """
        if isinstance(content, float):
            return overright_set_float(self._inner, content)
        else:
            return super().is_over_or_right(content)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: float) -> Optional[float]: ...

    @overload
    def intersection(self, other: FloatSet) -> Optional[FloatSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the intersection is empty.

        MEOS Functions:
            intersection_set_set, intersection_set_float
        """
        if isinstance(other, float):
            return intersection_set_float(self._inner, other)
        elif isinstance(other, FloatSet):
            result = intersection_set_set(self._inner, other._inner)
            return FloatSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[FloatSet, float]) -> Optional[FloatSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            A :class:`FloatSet` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_set_set, minus_set_float
        """
        if isinstance(other, float):
            result = minus_set_float(self._inner, other)
            return FloatSet(_inner=result) if result is not None else None
        elif isinstance(other, FloatSet):
            result = minus_set_set(self._inner, other._inner)
            return FloatSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: float) -> Optional[float]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`float` instance

        Returns:
            A :class:`float` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_float_set

        See Also:
            :meth:`minus`
        """
        return minus_float_set(other, self._inner)

    def union(self, other: Union[FloatSet, float]) -> FloatSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            A :class:`FloatSet` instance.

        MEOS Functions:
            union_set_set, union_set_float
        """
        if isinstance(other, float):
            result = union_set_float(self._inner, other)
            return FloatSet(_inner=result) if result is not None else None
        elif isinstance(other, FloatSet):
            result = union_set_set(self._inner, other._inner)
            return FloatSet(_inner=result) if result is not None else None
        else:
            return super().union(other)

    # ------------------------- Distance Operations ---------------------------

    def distance(
        self, other: Union[int, float, FloatSet, FloatSpan, FloatSpanSet]
    ) -> float:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A :class:`float` instance

        MEOS Functions:
            distance_set_float, distance_floatset_floatset,
            distance_floatspanset_floatspan, distance_floatspanset_floatspanset
        """
        from .floatspan import FloatSpan
        from .floatspanset import FloatSpanSet

        if isinstance(other, int):
            return distance_set_float(self._inner, float(other))
        elif isinstance(other, float):
            return distance_set_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return distance_floatset_floatset(self._inner, other._inner)
        elif isinstance(other, FloatSpan):
            return self.to_spanset().distance(other)
        elif isinstance(other, FloatSpanSet):
            return self.to_spanset().distance(other)
        else:
            return super().distance(other)
