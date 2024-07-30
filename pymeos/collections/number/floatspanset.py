from __future__ import annotations

from typing import Union, overload, Optional, TYPE_CHECKING, List

from pymeos_cffi import (
    floatspanset_in,
    floatspanset_out,
    floatspanset_width,
    floatspanset_shift_scale,
    adjacent_spanset_float,
    contains_spanset_float,
    spanset_eq,
    float_to_spanset,
    left_spanset_float,
    overleft_spanset_float,
    right_spanset_float,
    overright_spanset_float,
    distance_spanset_float,
    intersection_spanset_float,
    union_spanset_float,
    minus_spanset_float,
    floatspanset_to_intspanset,
    distance_floatspanset_floatspan,
    distance_floatspanset_floatspanset,
)

from ..base import SpanSet

if TYPE_CHECKING:
    from .floatset import FloatSet
    from .floatspan import FloatSpan
    from .intspanset import IntSpanSet


class FloatSpanSet(SpanSet[float]):
    """
    Class for representing lists of disjoint floatspans.

    ``FloatSpanSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> FloatSpanSet(string='{[8, 10], [11, 1]}')

    Another possibility is to give a list specifying the composing
    spans, which can be instances  of ``str`` or ``FloatSpan``. The composing
    spans must be given in increasing order.

        >>> FloatSpanSet(span_list=['[8, 10]', '[11, 12]'])
        >>> FloatSpanSet(span_list=[FloatSpan('[8, 10]'), FloatSpan('[11, 12]')])

    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "floatspanset"

    _parse_function = floatspanset_in
    _parse_value_function = lambda span: (
        floatspanset_in(span)[0] if isinstance(span, str) else span._inner[0]
    )

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            floatspanset_out
        """
        return floatspanset_out(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_span(self) -> FloatSpan:
        """
        Returns a span that encompasses ``self``.

        Returns:
            A new :class:`FloatSpan` instance

        MEOS Functions:
            spanset_span
        """
        from .floatspan import FloatSpan

        return FloatSpan(_inner=super().to_span())

    def to_intspanset(self) -> IntSpanSet:
        """
        Returns an intspanset that encompasses ``self``.

        Returns:
            A new :class:`IntSpanSet` instance

        MEOS Functions:
            floatspanset_to_intspanset
        """
        from .intspanset import IntSpanSet

        return IntSpanSet(_inner=floatspanset_to_intspanset(self._inner))

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
            floatspanset_width
        """
        return floatspanset_width(self._inner, ignore_gaps)

    def start_span(self) -> FloatSpan:
        """
        Returns the first span in ``self``.
        Returns:
            A :class:`FloatSpan` instance

        MEOS Functions:
            spanset_start_span
        """
        from .floatspan import FloatSpan

        return FloatSpan(_inner=super().start_span())

    def end_span(self) -> FloatSpan:
        """
        Returns the last span in ``self``.
        Returns:
            A :class:`FloatSpan` instance

        MEOS Functions:
            spanset_end_span
        """
        from .floatspan import FloatSpan

        return FloatSpan(_inner=super().end_span())

    def span_n(self, n: int) -> FloatSpan:
        """
        Returns the n-th span in ``self``.
        Returns:
            A :class:`FloatSpan` instance

        MEOS Functions:
            spanset_span_n
        """
        from .floatspan import FloatSpan

        return FloatSpan(_inner=super().span_n(n))

    def spans(self) -> List[FloatSpan]:
        """
        Returns the list of spans in ``self``.
        Returns:
            A :class:`list[FloatSpan]` instance

        MEOS Functions:
            spanset_spans
        """
        from .floatspan import FloatSpan

        ps = super().spans()
        return [FloatSpan(_inner=ps[i]) for i in range(self.num_spans())]

    # ------------------------- Transformations -------------------------------

    def shift(self, delta: int) -> FloatSpanSet:
        """
        Return a new ``FloatSpanSet`` with the lower and upper bounds shifted by
        ``delta``.

        Args:
            delta: The value to shift by

        Returns:
            A new ``FloatSpanSet`` instance

        MEOS Functions:
            floatspanset_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, width: int) -> FloatSpanSet:
        """
        Return a new ``FloatSpanSet`` with the lower and upper bounds scaled so
        that the width is ``width``.

        Args:
            width: The new width

        Returns:
            A new ``FloatSpanSet`` instance

        MEOS Functions:
            floatspanset_shift_scale
        """
        return self.shift_scale(None, width)

    def shift_scale(self, delta: Optional[int], width: Optional[int]) -> FloatSpanSet:
        """
        Return a new ``FloatSpanSet`` with the lower and upper bounds shifted by
        ``delta`` and scaled so that the width is ``width``.

        Args:
            delta: The value to shift by
            width: The new width

        Returns:
            A new ``FloatSpanSet`` instance

        MEOS Functions:
            floatspanset_shift_scale
        """
        d = delta if delta is not None else 0
        w = width if width is not None else 0
        modified = floatspanset_shift_scale(
            self._inner, d, w, delta is not None, width is not None
        )
        return FloatSpanSet(_inner=modified)

    # ------------------------- Topological Operations --------------------------------

    def is_adjacent(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share
        a bound but only one of them contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_spanset_span, adjacent_spanset_spanset,
            adjacent_spanset_float
        """
        if isinstance(other, int):
            return adjacent_spanset_float(self._inner, other)
        else:
            return super().is_adjacent(other)

    def contains(self, content: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset,
            contains_spanset_float
        """
        if isinstance(content, int):
            return contains_spanset_float(self._inner, content)
        else:
            return super().contains(content)

    def is_same(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
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
            return spanset_eq(self._inner, float_to_spanset(other))
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly left of ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if left, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, left_span_float
        """
        if isinstance(other, int):
            return left_spanset_float(self._inner, other)
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is left ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overleft_span_float
        """
        if isinstance(other, int):
            return overleft_spanset_float(self._inner, other)
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly right ``other``. That is, ``self``
        starts after ``other`` ends.

        Args:
            other: object to compare with

        Returns:
            True if right, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, right_span_float
        """
        if isinstance(other, int):
            return right_spanset_float(self._inner, other)
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[int, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is right ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset,
            overright_spanset_float
        """
        if isinstance(other, int):
            return overright_spanset_float(self._inner, other)
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(
        self, other: Union[int, float, FloatSet, FloatSpan, FloatSpanSet]
    ) -> float:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A :class:`float` value

        MEOS Functions:
        distance_spanset_float, distance_floatspanset_floatspan,
        distance_floatspanset_floatspanset

        """
        from .floatset import FloatSet
        from .floatspan import FloatSpan

        if isinstance(other, int):
            return distance_spanset_float(self._inner, float(other))
        elif isinstance(other, float):
            return distance_spanset_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, FloatSpan):
            return distance_floatspanset_floatspan(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            return distance_floatspanset_floatspanset(other._inner, self._inner)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: Union[int, float]) -> Optional[float]: ...

    @overload
    def intersection(self, other: FloatSpan) -> Optional[FloatSpanSet]: ...

    @overload
    def intersection(self, other: FloatSpanSet) -> Optional[FloatSpanSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            An int or a :class:`FloatSpanSet` instance. The actual class depends
            on ``other``.

        MEOS Functions:
            intersection_spanset_float, intersection_spanset_spanset,
            intersection_spanset_span
        """
        if isinstance(other, int) or isinstance(other, float):
            result = intersection_spanset_float(self._inner, float(other))
        else:
            result = super().intersection(other)
        return FloatSpanSet(_inner=result) if result is not None else None

    def __mul__(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_spanset_float, intersection_spanset_spanset,
            intersection_spanset_span
        """
        return self.intersection(other)

    def minus(self, other: Union[int, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset, minus_spanset_float
        """
        if isinstance(other, int) or isinstance(other, float):
            result = minus_spanset_float(self._inner, float(other))
        else:
            result = super().minus(other)
        return FloatSpanSet(_inner=result) if result is not None else None

    def __sub__(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset,
            minus_spanset_float
        """
        return self.minus(other)

    def union(self, other: Union[int, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            union_spanset_float, union_spanset_spanset,
            union_spanset_span
        """
        if isinstance(other, int) or isinstance(other, float):
            result = union_spanset_float(self._inner, float(other))
        else:
            result = super().union(other)
        return FloatSpanSet(_inner=result) if result is not None else None

    def __add__(self, other):
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            union_spanset_float, union_spanset_spanset,
            union_spanset_span
        """
        return self.union(other)
