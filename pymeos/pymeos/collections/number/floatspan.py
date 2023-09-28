from __future__ import annotations

from typing import List, Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import floatset_in, floatset_make, floatset_out, set_to_spanset, floatset_start_value, floatset_end_value, \
    floatset_value_n, floatset_values, contains_floatset_float, intersection_floatset_float, intersection_set_set, minus_floatset_float, \
    minus_set_set, union_set_set, union_floatset_float, floatset_shift_scale, minus_float_floatset, distance_floatset_float, \
    floatspan_in, floatspan_lower, floatspan_upper, numspan_shift_scale, contains_floatspan_float, adjacent_floatspan_float, \
    adjacent_span_span, float_to_floatspan, overlaps_span_span, span_eq, left_floatspan_float, overleft_floatspan_float, \
    right_floatspan_float, overright_floatspan_float, intersection_span_span, intersection_spanset_spanset, \
    intersection_spanset_span, minus_floatspan_float, minus_span_span, minus_spanset_span, union_floatspan_float, \
    union_span_span, union_spanset_span, floatspan_out

from .. import Span, SpanSet
from ..base import Set

if TYPE_CHECKING:
    from ...boxes import TBox
    from .floatset import FloatSet
    from .floatspanset import FloatSpanSet


class FloatSpan(Span[float]):
    """
    Class for representing sets of contiguous float values between a lower and
    an upper bound. The bounds may be inclusive or not.

    ``FloatSpan`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> FloatSpan('(2.5, 5.21]')

    Another possibility is to provide the ``lower`` and ``upper`` named parameters (of type str or float), and
    optionally indicate whether the bounds are inclusive or exclusive (by default, the lower bound is inclusive and the
    upper is exclusive):

        >>> FloatSpan(lower=2.0, upper=5.8)
        >>> FloatSpan(lower=2.0, upper=5.8, lower_inc=False, upper_inc=True)
        >>> FloatSpan(lower='2.0', upper='5.8', upper_inc=True)
    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'floatspan'

    _parse_function = floatspan_in
    _parse_value_function = float
    _make_function = floatspan_in

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

    # ------------------------- Accessors -------------------------------------
    def lower(self) -> float:
        """
        Returns the lower bound of ``self``.

        Returns:
            The lower bound of the span as a :class:`float`

        MEOS Functions:
            period_lower
        """

        return floatspan_lower(self._inner)

    def upper(self) -> float:
        """
        Returns the upper bound of ``self``.

        Returns:
            The upper bound of the span as a :class:`float`

        MEOS Functions:
            period_upper
        """
        return floatspan_upper(self._inner)

    def width(self) -> float:
        """
        Returns the width of ``self``.

        Returns:
            Returns a `float` representing the width of the span

        MEOS Functions:
            span_width
        """
        return self.width()

    # ------------------------- Transformations -------------------------------
    def shift(self, delta: float) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds shifted by ``delta``.

        Args:
            delta: The value to shift by

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        return self.shift_scale(delta, None)

    def scale(self, new_width: float) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds scaled so that the width is ``new_width``.

        Args:
            new_width: The new width

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        return self.shift_scale(None, new_width)

    def shift_scale(self, delta: Optional[float], new_width: Optional[float]) -> FloatSpan:
        """
        Return a new ``FloatSpan`` with the lower and upper bounds shifted by ``delta`` and scaled so that the width is ``new_width``.

        Args:
            delta: The value to shift by
            new_width: The new width

        Returns:
            A new ``FloatSpan`` instance

        MEOS Functions:
            floatspan_shift_scale
        """
        return FloatSpan(numspan_shift_scale(self._inner, delta, new_width, delta is not None, new_width is not None))

    # ------------------------- Topological Operations --------------------------------

    def is_adjacent(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset, adjacent_floatset_float
        """
        if isinstance(other, float):
            return adjacent_floatspan_float(self._inner, other)
        elif isinstance(other, TBox):
            return self.is_adjacent(other.to_span())
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[TBox, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is contained in ``container``.

        Args:
            container: object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_span_span, contained_span_spanset, contained_floatset_float
        """
        if isinstance(container, TBox):
            return self.is_contained_in(container.to_span())
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set, contains_floatset_float
        """
        if isinstance(content, float):
            return contains_floatspan_float(self._inner, content)
        elif isinstance(content, TBox):
            return self.contains(content.to_span())
        else:
            return super().contains(content)

    def overlaps(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` overlaps ``other``. That is, both share at least an instant

        Args:
            other: object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_span_span, overlaps_span_spanset, overlaps_period_timestampset,
            overlaps_period_temporal
        """
        if isinstance(other, float):
            return overlaps_span_span(self._inner, float_to_floatspan(other))
        elif isinstance(other, TBox):
            return self.overlaps(other.to_span())
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` and the bounding period of ``other`` is the same.

        Args:
            other: object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_period_temporal
        """
        if isinstance(other, float):
            return span_eq(self._inner, float_to_floatspan(other))
        elif isinstance(other, TBox):
            return self.is_same(other.to_span())
        else:
            return super().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is, ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset, left_floatspan_float
        """
        if isinstance(other, float):
            return left_floatspan_float(self._inner, other)
        elif isinstance(other, TBox):
            return self.is_left(other.to_span())
        else:
            return super().is_left(other)

    def is_over_or_left(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset, overleft_floatspan_float
        """
        if isinstance(other, float):
            return overleft_floatspan_float(self._inner, other)
        elif isinstance(other, TBox):
            return self.is_over_or_left(other.to_span())
        else:
            return super().is_over_or_left(other)

    def is_right(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self`` starts after ``other`` ends.

        Args:
            other: object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset, right_floatspan_float
        """
        if isinstance(other, float):
            return right_floatspan_float(other, self._inner)
        elif isinstance(other, TBox):
            return self.is_right(other.to_span())
        else:
            return super().is_right(other)

    def is_over_or_right(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Args:
            other: object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overright_floatspan_float
        """
        if isinstance(other, float):
            return overright_floatspan_float(other, self._inner)
        elif isinstance(other, TBox):
            return self.is_over_or_right(other.to_span())
        else:
            return super().is_over_or_right(other)

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other: Union[float, TBox, FloatSet, FloatSpan, FloatSpanSet]) -> float:
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

        Returns:
            A :class:`datetime.timedelta` instance

        MEOS Functions:
            distance_span_span, distance_span_spanset, distance_floatset_float,
        """
        if isinstance(other, float):
            return distance_floatset_float(self._inner, other)
        elif isinstance(other, TBox):
            return self.distance(other.to_span())
        else:
            return super().distance(other)

    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: float) -> Optional[float]:
        ...

    @overload
    def intersection(self, other: FloatSpan) -> Optional[FloatSpan]:
        ...

    @overload
    def intersection(self, other: Union[FloatSet, FloatSpanSet]) -> Optional[FloatSpanSet]:
        ...

    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Collection[float]` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span, intersection_floatset_float
        """
        from .floatset import FloatSet
        from .floatspanset import FloatSpanSet
        if isinstance(other, float):
            return intersection_floatset_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return self.intersection(other.to_span())
        elif isinstance(other, FloatSpan):
            result = intersection_span_span(self._inner, other._inner)
            return FloatSpan(_inner=result) if result is not None else None
        elif isinstance(other, FloatSpanSet):
            result = intersection_spanset_span(other._inner, self._inner)
            return FloatSpanSet(_inner=result) if result is not None else None
        else:
            super().intersection(other)

    def minus(self, other: Union[float, FloatSet, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            minus_span_span, minus_spanset_span, minus_floatset_float
        """
        from .floatset import FloatSet
        from .floatspanset import FloatSpanSet
        if isinstance(other, float):
            result = minus_floatspan_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return self.minus(other.to_spanset())
        elif isinstance(other, FloatSpan):
            result = minus_span_span(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            result = minus_spanset_span(other._inner, self._inner)
        else:
            super().minus(other)
        return FloatSpanSet(_inner=result) if result is not None else None

    def union(self, other: Union[float, FloatSet, FloatSpan, FloatSpanSet]) -> FloatSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_spanset_span, union_span_span, union_floatset_float
        """
        from .floatset import FloatSet
        from .floatspanset import FloatSpanSet
        if isinstance(other, float):
            result = union_floatspan_float(self._inner, other)
        elif isinstance(other, FloatSet):
            return self.union(other.to_spanset())
        elif isinstance(other, FloatSpan):
            result = union_span_span(self._inner, other._inner)
        elif isinstance(other, FloatSpanSet):
            result = union_spanset_span(other._inner, self._inner)
        else:
            super().union(other)
        return FloatSpanSet(_inner=result) if result is not None else None
