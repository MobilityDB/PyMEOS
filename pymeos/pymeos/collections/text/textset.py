from __future__ import annotations

from typing import Optional, overload, Union

from pymeos_cffi import *

from .. import Set, Span, SpanSet


class TextSet(Set[str]):
    """
    Class for representing a set of text values.

    ``TextSet`` objects can be created with a single argument of type string as
    in MobilityDB.

        >>> TextSet(string='{a, b, c, def}')

    Another possibility is to create a ``TextSet`` object from a list of strings.

        >>> TextSet(elements=['a', 'b', 'c', 'def'])


    """

    __slots__ = ['_inner']

    _parse_function = textset_in
    _parse_value_function = lambda x: x
    _make_function = textset_make

    # ------------------------- Constructors ----------------------------------

    # ------------------------- Output ----------------------------------------

    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            textset_out
        """
        return textset_out(self._inner)

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
            A :class:`str` instance

        MEOS Functions:
            textset_start_value
        """
        return textset_start_value(self._inner)

    def end_element(self):
        """
        Returns the last element in ``self``.

        Returns:
            A :class:`str` instance

        MEOS Functions:
            textset_end_value
        """
        return textset_end_value(self._inner)

    def element_n(self, n: int):
        """
        Returns the ``n``-th element in ``self``.

        Args:
            n: The 0-based index of the element to return.

        Returns:
            A :class:`str` instance

        MEOS Functions:
            textset_value_n
        """
        super().element_n(n)
        return textset_value_n(self._inner, n)

    def elements(self):
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`str` instances

        MEOS Functions:
            textset_values
        """
        elems = textset_values(self._inner)
        return [elems[i] for i in range(self.num_elements())]


    # ------------------------- Transformations --------------------------------
    def lowercase(self):
        """
        Returns a new textset that is the result of appling uppercase to ``self``

        Returns:
            A :class:`str` instance

        MEOS Functions:
            textset_lowercase
        """
        return textset_lowercase(self._inner)

    def uppercase(self):
        """
        Returns a new textset that is the result of appling uppercase to ``self``

        Returns:
            A :class:`str` instance

        MEOS Functions:
            textset_uppercase
        """
        return textset_uppercase(self._inner)

    # ------------------------- Set Operations --------------------------------

    @overload
    def intersection(self, other: str) -> Optional[str]:
        ...

    @overload
    def intersection(self, other: TextSet) -> Optional[TextSet]:
        ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: A :class:`TextSet` or :class:`str` instance

        Returns:
            An object of the same type as ``other`` or ``None`` if the intersection is empty.

        MEOS Functions:
            intersection_textset_text, intersection_set_set
        """
        if isinstance(other, str):
            return intersection_textset_text(self._inner, other)
        elif isinstance(other, TextSet):
            result = super().intersection(other)
            return TextSet(elements=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[TextSet, str]) -> Optional[TextSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`TextSet` or :class:`str` instance

        Returns:
            A :class:`TextSet` instance.

        MEOS Functions:
            minus_textset_text, minus_set_set
        """
        if isinstance(other, str):
            result = minus_textset_text(self._inner, other)
            return TextSet(elements=result) if result is not None else None
        elif isinstance(other, TextSet):
            result = super().minus(other)
            return TextSet(elements=result) if result is not None else None
        else:
            return super().minus(other)

    def union(self, other: Union[TextSet, str]) -> TextSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: A :class:`TextSet` or :class:`str` instance

        Returns:
            A :class:`TextSet` instance.

        MEOS Functions:
            union_textset_text, union_set_set
        """
        if isinstance(other, str):
            result = union_textset_text(self._inner, other)
            return TextSet(elements=result) if result is not None else None
        elif isinstance(other, TextSet):
            result = super().union(other)
            return TextSet(elements=result) if result is not None else None
        else:
            return super().union(other)
