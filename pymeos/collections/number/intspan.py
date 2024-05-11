from __future__ import annotations

from typing import Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import (
    intspan_in,
    intspan_lower,
    intspan_upper,
    intspan_shift_scale,
    contains_span_int,
    adjacent_span_int,
    intspan_width,
    int_to_span,
    span_eq,
    left_span_int,
    overleft_span_int,
    right_span_int,
    overright_span_int,
    intersection_span_int,
    intersection_span_span,
    intersection_spanset_span,
    minus_span_int,
    minus_span_span,
    minus_spanset_span,
    union_span_int,
    union_span_span,
    union_spanset_span,
    intspan_out,
    intspan_make,
    distance_span_int,
    intspan_to_floatspan,
    distance_intspan_intspan,
    distance_intspanset_intspan,
)

from ..base import Span

if TYPE_CHECKING:
    from .intset import IntSet
    from .intspanset import IntSpanSet
    from .floatspan import FloatSpan


class IntSpan(Span[int]):
    """
    Class for representing sets of contiguous integer values between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``IntSpan`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> IntSpan('(2, 5]')

    Another possibility is to provide the ``lower`` and ``upper`` named parameters (of type str or int), and
    optionally indicate whether the bounds are inclusive or exclusive (by default, the lower bound is inclusive and the
    upper is exclusive):

        >>> IntSpan(lower=2, upper=5)
        >>> IntSpan(lower=2, upper=5, lower_inc=False, upper_inc=True)
        >>> IntSpan(lower='2', upper='5', upper_inc=True)
    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "intspan"

    _parse_function = intspan_in
    _parse_value_function = int
    _make_function = intspan_make

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            intspan_out
        """
        return intspan_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> IntSpanSet:
        """
        Returns a spanset containing ``self``.

        Returns:
            A new :class:`IntSpanSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .intspanset import IntSpanSet

        return IntSpanSet(_inner=super().to_spanset())

    def to_floatspan(self) -> FloatSpan:
        """
        Converts ``self`` to a :class:`FloatSpan` instance.

        Returns:
            A new :class:`FloatSpan` instance

        MEOS Functions:
            intspan_to_floatspan
        """
        from .floatspan import FloatSpan

        return FloatSpan(_inner=intspan_to_floatspan(self._inner))

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> int:
        """
        Returns the lower bound of ``self``.

        Returns:
            The lower bound of the span as a :class:`int`

        MEOS Functions:
            tstzspan_lower
        """

        return intspan_lower(self._inner)

    def upper(self) -> int:
        """
        Returns the upper bound of ``self``.

        Returns:
            The upper bound of the span as a :class:`int`

        MEOS Functions:
            tstzspan_upper
        """
        return intspan_upper(self._inner)

    def width(self) -> float:
        """
        Returns the width of ``self``.

        Returns:
            Returns a `float` representing the width of the span

        MEOS Functions:
            intspan_width
        """
        return intspan_width(self._inner)

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: int) -> IntSpan:
        """
        Return a new ``IntSpan`` with the lower and upper bounds shifted by ``delta``.

        Args:
            delta: The value to shift by

        Returns:
            A new ``IntSpan`` instance

        MEOS Functions:
            intspan_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, width: int) -> IntSpan:
        """
        Return a new ``IntSpan`` with the lower and upper bounds scaled so that
        the width is ``width``.

        Args:
            width: The new width

        Returns:
            A new ``IntSpan`` instance

        MEOS Functions:
            intspan_shift_scale
        """
        return self.shift_scale(None, width)

    def shift_scale(self, delta: Optional[int], width: Optional[int]) -> IntSpan:
        """
        Return a new ``IntSpan`` with the lower and upper bounds shifted by
        ``delta`` and scaled so that the width is ``width``.

        Args:
            delta: The value to shift by
            width: The new width

        Returns:
            A new ``IntSpan`` instance

        MEOS Functions:
            intspan_shift_scale
        """
        d = delta if delta is not None else 0
        w = width if width is not None else 0
        modified = intspan_shift_scale(
            self._inner, d, w, delta is not None, width is not None
        )
        return IntSpan(_inner=modified)

    # ------------------------- Topological Operations --------------------------------

    def is_adjacent(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share
        a bound but only one of them contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_span_int
        """
        if isinstance(other, int):
            return adjacent_span_int(self._inner, other)
        else:
            return super().is_adjacent(other)

    def contains(self, content: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_int
        """
        if isinstance(content, int):
            return contains_span_int(self._inner, content)
        else:
            return super().contains(content)

    def is_same(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` and the bounding tstzspan of ``other`` is the
        same.

        Args:
            other: object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_tstzspan_temporal
        """
        if isinstance(other, int):
            return span_eq(self._inner, int_to_span(other))
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly left ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if left, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, left_span_int
        """
        if isinstance(other, int):
            return left_span_int(self._inner, other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is left ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if over or left, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overleft_span_int
        """
        if isinstance(other, int):
            return overleft_span_int(self._inner, other)
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly right ``other``. That is, ``self``
        starts after ``other`` ends.

        Args:
            other: object to compare with

        Returns:
            True if right, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, right_span_int
        """
        if isinstance(other, int):
            return right_span_int(self._inner, other)
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is right ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overright_span_int
        """
        if isinstance(other, int):
            return overright_span_int(self._inner, other)
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[int, IntSet, IntSpan, IntSpanSet]) -> int:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A :class:`int` value

        MEOS Functions:
            distance_span_int, distance_intspanset_intspan, distance_intspanset_intspan,
        """
        from .intset import IntSet
        from .intspanset import IntSpanSet

        if isinstance(other, int):
            return distance_span_int(self._inner, other)
        elif isinstance(other, IntSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, IntSpan):
            return distance_intspan_intspan(self._inner, other._inner)
        elif isinstance(other, IntSpanSet):
            return distance_intspanset_intspan(other._inner, self._inner)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: int) -> Optional[int]: ...

    @overload
    def intersection(self, other: IntSpan) -> Optional[IntSpan]: ...

    @overload
    def intersection(self, other: IntSpanSet) -> Optional[IntSpanSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Collection[int]` instance. The actual class depends on
            ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_span_int
        """
        from .intspanset import IntSpanSet

        if isinstance(other, int):
            return intersection_span_int(self._inner, other)
        elif isinstance(other, IntSpan):
            result = intersection_span_span(self._inner, other._inner)
            return IntSpan(_inner=result) if result is not None else None
        elif isinstance(other, IntSpanSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return IntSpanSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: Union[int, IntSpan, IntSpanSet]) -> IntSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`IntSpanSet` instance.

        MEOS Functions:
            minus_span_span, minus_spanset_span, minus_span_int
        """
        from .intspanset import IntSpanSet

        if isinstance(other, int):
            result = minus_span_int(self._inner, other)
        elif isinstance(other, IntSpan):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, IntSpanSet):
            result = minus_spanset_span(other._inner, self._inner)
        else:
            result = super().minus(other)
        return IntSpanSet(_inner=result) if result is not None else None

    def union(self, other: Union[int, IntSpan, IntSpanSet]) -> IntSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`TsTzSpanSet` instance.

        MEOS Functions:
            union_spanset_span, union_span_span, union_span_int
        """
        from .intspanset import IntSpanSet

        if isinstance(other, int):
            result = union_span_int(self._inner, other)
        elif isinstance(other, IntSpan):
            result = union_span_span(self._inner, other._inner)
        elif isinstance(other, IntSpanSet):
            result = union_spanset_span(other._inner, self._inner)
        else:
            result = super().union(other)
        return IntSpanSet(_inner=result) if result is not None else None
