from __future__ import annotations

from typing import Union, overload, Optional, TYPE_CHECKING, List

from pymeos_cffi import (
    intspanset_in,
    intspanset_out,
    intspanset_width,
    intspanset_shift_scale,
    adjacent_spanset_int,
    contains_spanset_int,
    spanset_eq,
    int_to_spanset,
    left_spanset_int,
    overleft_spanset_int,
    right_spanset_int,
    overright_spanset_int,
    distance_spanset_int,
    intersection_spanset_int,
    union_spanset_int,
    minus_spanset_int,
    intspanset_to_floatspanset,
    distance_intspanset_intspan,
    distance_intspanset_intspanset,
)

from ..base import SpanSet

if TYPE_CHECKING:
    from .intset import IntSet
    from .intspan import IntSpan
    from .floatspanset import FloatSpanSet


class IntSpanSet(SpanSet[int]):
    """
    Class for representing lists of disjoint intspans.

    ``IntSpanSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> IntSpanSet(string='{[8, 10], [11, 1]}')

    Another possibility is to give a list specifying the composing
    spans, which can be instances  of ``str`` or ``IntSpan``. The composing
    spans must be given in increasing order.

        >>> IntSpanSet(span_list=['[8, 10]', '[11, 12]'])
        >>> IntSpanSet(span_list=[IntSpan('[8, 10]'), IntSpan('[11, 12]')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "intspanset"

    _parse_function = intspanset_in
    _parse_value_function = lambda span: (
        intspanset_in(span)[0] if isinstance(span, str) else span._inner[0]
    )

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            intspanset_out
        """
        return intspanset_out(self._inner)

    # ------------------------- Conversions -----------------------------------

    def to_span(self) -> IntSpan:
        """
        Returns a span that encompasses ``self``.

        Returns:
            A new :class:`IntSpan` instance

        MEOS Functions:
            spanset_span
        """
        from .intspan import IntSpan

        return IntSpan(_inner=super().to_span())

    def to_floatspanset(self) -> FloatSpanSet:
        """
        Converts ``self`` to a :class:`FloatSpanSet` instance.

        Returns:
            A new :class:`FloatSpanSet` instance

        MEOS Functions:
            intspanset_to_floatspanset
        """
        from .floatspanset import FloatSpanSet

        return FloatSpanSet(_inner=intspanset_to_floatspanset(self._inner))

    # ------------------------- Accessors -------------------------------------

    def width(self, ignore_gaps: Optional[bool] = False) -> float:
        """
        Returns the width of the spanset. By default, i.e., when the second
        argument is False, the function takes into account the gaps within,
        i.e., returns the sum of the widths of the spans within.
        Otherwise, the function returns the width of the spanset ignoring
        any gap, i.e., the width from the lower bound of the first span to
        the upper bound of the last span.

        Parameters:
            ignore_gaps: Whether to take into account potential gaps in
            the spanset.

        Returns:
            A `float` representing the duration of the spanset

        MEOS Functions:
            intspanset_width
        """
        return intspanset_width(self._inner, ignore_gaps)

    def start_span(self) -> IntSpan:
        """
        Returns the first span in ``self``.
        Returns:
            A :class:`IntSpan` instance

        MEOS Functions:
            spanset_start_span
        """
        from .intspan import IntSpan

        return IntSpan(_inner=super().start_span())

    def end_span(self) -> IntSpan:
        """
        Returns the last span in ``self``.
        Returns:
            A :class:`IntSpan` instance

        MEOS Functions:
            spanset_end_span
        """
        from .intspan import IntSpan

        return IntSpan(_inner=super().end_span())

    def span_n(self, n: int) -> IntSpan:
        """
        Returns the n-th span in ``self``.
        Returns:
            A :class:`IntSpan` instance

        MEOS Functions:
            spanset_span_n
        """
        from .intspan import IntSpan

        return IntSpan(_inner=super().span_n(n))

    def spans(self) -> List[IntSpan]:
        """
        Returns the list of spans in ``self``.
        Returns:
            A :class:`list[IntSpan]` instance

        MEOS Functions:
            spanset_spans
        """
        from .intspan import IntSpan

        ps = super().spans()
        return [IntSpan(_inner=ps[i]) for i in range(self.num_spans())]

    # ------------------------- Transformations -------------------------------

    def shift(self, delta: int) -> IntSpanSet:
        """
        Return a new ``IntSpanSet`` with the lower and upper bounds shifted by
        ``delta``.

        Args:
            delta: The value to shift by

        Returns:
            A new ``IntSpanSet`` instance

        MEOS Functions:
            intspanset_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, width: int) -> IntSpanSet:
        """
        Return a new ``IntSpanSet`` with the lower and upper bounds scaled so
        that the width is ``width``.

        Args:
            width: The new width

        Returns:
            A new ``IntSpanSet`` instance

        MEOS Functions:
            intspanset_shift_scale
        """
        return self.shift_scale(None, width)

    def shift_scale(self, delta: Optional[int], width: Optional[int]) -> IntSpanSet:
        """
        Return a new ``IntSpanSet`` with the lower and upper bounds shifted by
        ``delta`` and scaled so that the width is ``width``.

        Args:
            delta: The value to shift by
            width: The new width

        Returns:
            A new ``IntSpanSet`` instance

        MEOS Functions:
            intspanset_shift_scale
        """
        d = delta if delta is not None else 0
        w = width if width is not None else 0
        modified = intspanset_shift_scale(
            self._inner, d, w, delta is not None, width is not None
        )
        return IntSpanSet(_inner=modified)

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
            adjacent_spanset_span, adjacent_spanset_spanset,
            adjacent_spanset_int
        """
        if isinstance(other, int):
            return adjacent_spanset_int(self._inner, other)
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
            contains_spanset_span, contains_spanset_spanset,
            contains_spanset_int
        """
        if isinstance(content, int):
            return contains_spanset_int(self._inner, content)
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
            return spanset_eq(self._inner, int_to_spanset(other))
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly left of ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if left, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, left_span_int
        """
        if isinstance(other, int):
            return left_spanset_int(self._inner, other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[int, IntSpan, IntSpanSet]) -> bool:
        """
        Returns whether ``self`` is left ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overleft_span_int
        """
        if isinstance(other, int):
            return overleft_spanset_int(self._inner, other)
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
            return right_spanset_int(self._inner, other)
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
            overright_spanset_span, overright_spanset_spanset,
            overright_spanset_int
        """
        if isinstance(other, int):
            return overright_spanset_int(self._inner, other)
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[int, IntSet, IntSpan, IntSpanSet]) -> int:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A float value

        MEOS Functions:
            distance_spanset_int, distance_intspanset_intspan,
            distance_intspanset_intspanset
        """
        from .intset import IntSet
        from .intspan import IntSpan

        if isinstance(other, int):
            return distance_spanset_int(self._inner, other)
        elif isinstance(other, IntSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, IntSpan):
            return distance_intspanset_intspan(self._inner, other._inner)
        elif isinstance(other, IntSpanSet):
            return distance_intspanset_intspanset(other._inner, self._inner)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: int) -> Optional[int]: ...

    @overload
    def intersection(self, other: IntSpan) -> Optional[IntSpanSet]: ...

    @overload
    def intersection(self, other: IntSpanSet) -> Optional[IntSpanSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            An int or a :class:`IntSpanSet` instance. The actual class depends
            on ``other``.

        MEOS Functions:
            intersection_spanset_int, intersection_spanset_spanset,
            intersection_spanset_span
        """
        if isinstance(other, int):
            result = intersection_spanset_int(self._inner, other)
        else:
            result = super().intersection(other)
        return IntSpanSet(_inner=result) if result is not None else None

    def __mul__(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_spanset_int, intersection_spanset_spanset,
            intersection_spanset_span
        """
        return self.intersection(other)

    def minus(self, other: Union[int, IntSpan, IntSpanSet]) -> IntSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`IntSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset, minus_spanset_int
        """
        if isinstance(other, int):
            result = minus_spanset_int(self._inner, other)
        else:
            result = super().minus(other)
        return IntSpanSet(_inner=result) if result is not None else None

    def __sub__(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`IntSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset,
            minus_spanset_int
        """
        return self.minus(other)

    def union(self, other: Union[int, IntSpan, IntSpanSet]) -> IntSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`IntSpanSet` instance.

        MEOS Functions:
            union_spanset_int, union_spanset_spanset,
            union_spanset_span
        """
        if isinstance(other, int):
            result = union_spanset_int(self._inner, other)
        else:
            result = super().union(other)
        return IntSpanSet(_inner=result) if result is not None else None

    def __add__(self, other):
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`IntSpanSet` instance.

        MEOS Functions:
            union_spanset_int, union_spanset_spanset,
            union_spanset_span
        """
        return self.union(other)
