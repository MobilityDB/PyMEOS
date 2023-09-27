from __future__ import annotations

from typing import Optional, overload, Union

from pymeos_cffi import *

from .. import Span, SpanSet
from ..base import Set


class FloatSet(Set[float]):
    """
    Class for representing a set of text values.

    ``FloatSet`` objects can be created with a single argument of type float as
    in MobilityDB.

        >>> FloatSet(string='{1.5, 2.5, 3.5, 4.5}')

    Another possibility is to create a ``FloatSet`` object from a list of floats.

        >>> FloatSet(elements=[1.5, 2.5, 3.5, 4.5])


    """

    __slots__ = ['_inner']

    _parse_function = floatset_in
    _parse_value_function = lambda x: x
    _make_function = floatset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`float` instance

        MEOS Functions:
            floatset_out
        """
        return floatset_out(self._inner)

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
            A :class:`float` instance

        MEOS Functions:
            floatset_start_value
        """
        return floatset_start_value(self._inner)

    def end_element(self):
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`float` instance

        MEOS Functions:
            floatset_end_value
        """
        return floatset_end_value(self._inner)

    def element_n(self, n: float):
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
        return floatset_value_n(self._inner, n)

    def elements(self):
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`float` instances

        MEOS Functions:
            floatset_values
        """
        elems = floatset_values(self._inner)
        return [elems[i] for i in range(self.num_elements())]

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: float) -> Optional[float]:
        ...

    @overload
    def intersection(self, other: FloatSet) -> Optional[FloatSet]:
        ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the
            intersection is empty.

        MEOS Functions:
            intersection_floatset_text, intersection_set_set
        """
        if isinstance(other, float):
            return intersection_floatset_text(self._inner, other)
        elif isinstance(other, FloatSet):
            result = super().intersection(other)
            return FloatSet(elements=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[FloatSet, float]) -> Optional[FloatSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            A :class:`FloatSet` instance.

        MEOS Functions:
            minus_floatset_text, minus_set_set
        """
        if isinstance(other, float):
            result = minus_floatset_text(self._inner, other)
            return FloatSet(elements=result) if result is not None else None
        elif isinstance(other, FloatSet):
            result = super().minus(other)
            return FloatSet(elements=result) if result is not None else None
        else:
            return super().minus(other)

    def union(self, other: Union[FloatSet, float]) -> FloatSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`FloatSet` or :class:`float` instance

        Returns:
            A :class:`FloatSet` instance.

        MEOS Functions:
            union_floatset_text, union_set_set
        """
        if isinstance(other, float):
            result = union_floatset_text(self._inner, other)
            return FloatSet(elements=result) if result is not None else None
        elif isinstance(other, FloatSet):
            result = super().union(other)
            return FloatSet(elements=result) if result is not None else None
        else:
            return super().union(other)
