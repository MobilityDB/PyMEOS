from __future__ import annotations

from typing import Optional, overload, Union

from pymeos_cffi import *

from ..base import Set


class TextSet(Set[str]):
    """
    Class for representing a set of text values.

    ``TextSet`` objects can be created with a single argument of type string as in MobilityDB.

        >>> TextSet(string='{a, b, c, def}')

    Another possibility is to create a ``TextSet`` object from a list of strings.

        >>> TextSet(elements=['a', 'b', 'c', 'def'])


    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'textset'

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

    def to_spanset(self):
        raise NotImplementedError()

    def to_span(self):
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
        return text2cstring(textset_value_n(self._inner, n + 1)[0])

    def elements(self):
        """
        Returns the elements in ``self``.

        Returns:
            A list of :class:`str` instances

        MEOS Functions:
            textset_values
        """
        elems = textset_values(self._inner)
        return [text2cstring(elems[i]) for i in range(self.num_elements())]

    # ------------------------- Topological Operations --------------------------------

    def contains(self, content: Union[TextSet, str]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_textset_text
        """
        if isinstance(content, str):
            return contains_textset_text(self._inner, content)
        else:
            return super().contains(content)

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
            return text2cstring(intersection_textset_text(self._inner, other)[0])
        elif isinstance(other, TextSet):
            result = intersection_set_set(self._inner, other._inner)
            return TextSet(_inner=result) if result is not None else None
        else:
            return super().intersection(other)

    def minus(self, other: Union[TextSet, str]) -> Optional[TextSet]:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: A :class:`TextSet` or :class:`str` instance

        Returns:
            A :class:`TextSet` instance or ``None`` if the difference is empty.

        MEOS Functions:
            minus_textset_text, minus_set_set
        """
        if isinstance(other, str):
            result = minus_textset_text(self._inner, other)
            return TextSet(_inner=result) if result is not None else None
        elif isinstance(other, TextSet):
            result = minus_set_set(self._inner, other._inner)
            return TextSet(_inner=result) if result is not None else None
        else:
            return super().minus(other)

    def subtract_from(self, other: str) -> Optional[str]:
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: A :class:`str` instance

        Returns:
            A :class:`str` instance.

        MEOS Functions:
            minus_geo_geoset

        See Also:
            :meth:`minus`
        """
        result = minus_text_textset(other, self._inner)
        return text2cstring(result[0]) if result is not None else None

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
            return TextSet(_inner=result) if result is not None else None
        elif isinstance(other, TextSet):
            result = union_set_set(self._inner, other._inner)
            return TextSet(_inner=result) if result is not None else None
        else:
            return super().union(other)
