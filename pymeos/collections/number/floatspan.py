from __future__ import annotations

from typing import Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import (
    intersection_span_float,
    distance_span_float,
    floatspan_in,
    floatspan_lower,
    floatspan_upper,
    floatspan_shift_scale,
    contains_span_float,
    adjacent_span_float,
    float_to_span,
    span_eq,
    left_span_float,
    overleft_span_float,
    right_span_float,
    overright_span_float,
    intersection_span_span,
    intersection_spanset_span,
    minus_span_float,
    minus_span_span,
    minus_spanset_span,
    union_span_float,
    union_span_span,
    union_spanset_span,
    floatspan_out,
    floatspan_make,
    floatspan_width,
    floatspan_to_intspan,
    distance_floatspan_floatspan,
    distance_floatspanset_floatspan,
)

from ..base import Span

if TYPE_CHECKING:
    from .floatset import FloatSet
    from .floatspanset import FloatSpanSet
    from .intspan import IntSpan


class FloatSpan(Span[float]):
    """
    Class for representing sets of contiguous float values between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``FloatSpan`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> FloatSpan('(2.5, 5.21]')

    Another possibility is to provide the ``lower`` and ``upper`` named
    parameters (of type str or float), and optionally indicate whether the
    bounds are inclusive or exclusive (by default, the lower bound is inclusive
    and the upper is exclusive):

        >>> FloatSpan(lower=2.0, upper=5.8)
        >>> FloatSpan(lower=2.0, upper=5.8, lower_inc=False, upper_inc=True)
        >>> FloatSpan(lower='2.0', upper='5.8', upper_inc=True)
    """

    __slots__ = ["_inner"]

    _mobilitydb_name = "floatspan"

    _parse_function = floatspan_in
    _parse_value_function = float
    _make_function = floatspan_make

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15) -> str:
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            floatspan_out
        """
        return floatspan_out(self._inner, max_decimals)

    # ------------------------- Conversions -----------------------------------

    def to_spanset(self) -> FloatSpanSet:
        """
        Returns a spanset containing ``self``.

        Returns:
            A new :class:`FloatSpanSet` instance

        MEOS Functions:
            span_to_spanset
        """
        from .floatspanset import FloatSpanSet

        return FloatSpanSet(_inner=super().to_spanset())

    def to_intspan(self) -> IntSpan:
        """
        Converts ``self`` to a :class:`IntSpan` instance.

        Returns:
            A new :class:`IntSpan` instance

        MEOS Functions:
            floatspan_to_intspan
        """
        from .intspan import IntSpan

        return IntSpan(_inner=floatspan_to_intspan(self._inner))

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> float:
        """
        Returns the lower bound of ``self``.

        Returns:
            The lower bound of the span as a :class:`float`

        MEOS Functions:
            tstzspan_lower
        """

        return floatspan_lower(self._inner)

    def upper(self) -> float:
        """
        Returns the upper bound of ``self``.

        Returns:
            The upper bound of the span as a :class:`float`

        MEOS Functions:
            tstzspan_upper
        """
        return floatspan_upper(self._inner)

    def width(self) -> float:
        """
        Returns the width of ``self``.

        Returns:
            Returns a `float` representing the width of the span

        MEOS Functions:
            floatspan_width
        """
        return floatspan_width(self._inner)

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: float) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds shifted by
        ``delta``.

        Args:
            delta: The value to shift by

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, width: float) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds scaled so
        that the width is ``width``.

        Args:
            width: The new width

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        return self.shift_scale(None, width)

    def shift_scale(self, delta: Optional[float], width: Optional[float]) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds shifted by
        ``delta`` and scaled so that the width is ``width``.

        Args:
            delta: The value to shift by
            width: The new width

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        d = delta if delta is not None else 0
        w = width if width is not None else 0
        modified = floatspan_shift_scale(
            self._inner, d, w, delta is not None, width is not None
        )
        return FloatSpan(_inner=modified)

    # ------------------------- Topological Operations --------------------------------

    def is_adjacent(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share
        a bound but only one of them contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_span_float
        """
        if isinstance(other, int) or isinstance(other, float):
            return adjacent_span_float(self._inner, float(other))
        else:
            return super().is_adjacent(other)

    def contains(self, content: Union[int, float, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_span_float
        """
        if isinstance(content, int) or isinstance(content, float):
            return contains_span_float(self._inner, float(content))
        else:
            return super().contains(content)

    def is_same(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> bool:
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
        if isinstance(other, int) or isinstance(other, float):
            return span_eq(self._inner, float_to_span(float(other)))
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, left_span_float
        """
        if isinstance(other, int) or isinstance(other, float):
            return left_span_float(self._inner, float(other))
        else:
            return super().is_left(other)

    def is_over_or_left(
        self, other: Union[int, float, FloatSpan, FloatSpanSet]
    ) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overleft_span_float
        """
        if isinstance(other, int) or isinstance(other, float):
            return overleft_span_float(self._inner, float(other))
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self``
        starts after ``other`` ends.

        Args:
            other: object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, right_span_float
        """
        if isinstance(other, int) or isinstance(other, float):
            return right_span_float(self._inner, float(other))
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[float, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overright_span_float
        """
        if isinstance(other, int) or isinstance(other, float):
            return overright_span_float(self._inner, float(other))
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
            A float value

        MEOS Functions:
            distance_span_float, distance_floatspan_floatspan,
            distance_floatspanset_floatspan,
        """
        from .floatset import FloatSet
        from .floatspanset import FloatSpanSet

        if isinstance(other, int):
            return distance_span_float(self._inner, float(other))
        elif isinstance(other, float):
            return distance_span_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return self.distance(other.to_spanset())
        elif isinstance(other, FloatSpan):
            return distance_floatspan_floatspan(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            return distance_floatspanset_floatspan(other._inner, self._inner)
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: Union[int, float]) -> Optional[float]: ...

    @overload
    def intersection(self, other: FloatSpan) -> Optional[FloatSpan]: ...

    @overload
    def intersection(self, other: FloatSpanSet) -> Optional[FloatSpanSet]: ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Collection[float]` instance. The actual class depends on
            ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_set_float
        """
        from .floatspanset import FloatSpanSet

        if isinstance(other, int) or isinstance(other, float):
            return intersection_span_float(self._inner, float(other))
        elif isinstance(other, FloatSpan):
            result = intersection_span_span(self._inner, other._inner)
            return FloatSpan(_inner=result) if result is not None else None
        elif isinstance(other, FloatSpanSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return FloatSpanSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            minus_span_span, minus_spanset_span, minus_span_float
        """
        from .floatspanset import FloatSpanSet

        if isinstance(other, int) or isinstance(other, float):
            result = minus_span_float(self._inner, float(other))
        elif isinstance(other, FloatSpan):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            result = minus_spanset_span(other._inner, self._inner)
        else:
            result = super().minus(other)
        return FloatSpanSet(_inner=result) if result is not None else None

    def union(self, other: Union[int, float, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`TsTzSpanSet` instance.

        MEOS Functions:
            union_spanset_span, union_span_span, union_span_float
        """
        from .floatspanset import FloatSpanSet

        if isinstance(other, int) or isinstance(other, float):
            result = union_span_float(self._inner, float(other))
        elif isinstance(other, FloatSpan):
            result = union_span_span(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            result = union_spanset_span(other._inner, self._inner)
        else:
            result = super().union(other)
        return FloatSpanSet(_inner=result) if result is not None else None
