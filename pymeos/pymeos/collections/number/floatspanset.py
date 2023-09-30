from __future__ import annotations

from typing import Union, overload, Optional, TYPE_CHECKING

from pymeos_cffi import floatspanset_in, floatspanset_out

from pymeos.collections import SpanSet

if TYPE_CHECKING:
    from .floatspan import FloatSpan

class FloatSpanSet(SpanSet[float]):
    """
    Class for representing lists of disjoint intspans.

    ``FloatSpanSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> FloatSpanSet(string='{[8, 10], [11, 1]}')

    Another possibility is to give a list specifying the composing
    spans, which can be instances  of ``str`` or ``FloatSpan``. The composing
    spans must be given in increasing order.

        >>> FloatSpanSet(span_list=['[8, 10]', '[11, 12]'])
        >>> FloatSpanSet(span_list=[FloatSpan('[8, 10]'), FloatSpan('[11, 12]')])

    """

    __slots__ = ['_inner']

    _mobilitydb_name = 'floatspanset'

    _parse_function = floatspanset_in
    _parse_value_function = lambda span: floatspanset_in(span)[0] if isinstance(spanset, str) else floatspanset_in._inner[0]


    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            floatspanset_out
        """
        return floatspanset_out(self._inner)

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

    # ------------------------- Accessors -------------------------------------
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


    # ------------------------- Set Operations --------------------------------
    @overload
    def intersection(self, other: FloatSpan) -> FloatSpanSet:
        ...

    @overload
    def intersection(self, other: FloatSpanSet) -> FloatSpanSet:
        ...

    @overload
    def intersection(self, other: float) -> float:
        ...

    def intersection(self, other: Union[float, FloatSpan, FloatSpanSet]) -> Union[float, FloatSpanSet]:
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            An float or a :class:`FloatSpanSet` instance. The actual class depends
            on ``other``.

        MEOS Functions:
            intersection_floatspanset_int, intersection_spanset_spanset,
            intersection_spanset_span
        """
        from .floatspan import FloatSpan
        if isinstance(other, float):
            result = intersection_floatspanset_int(self._inner, float)
            return timestamptz_to_int(result) if result is not None else None
        elif isinstance(other, TimestampSet):
            result = super().intersection(other)
            return TimestampSet(_inner=result) if result is not None else None
        elif isinstance(other, FloatSpan):
            result = super().intersection(other)
            return FloatSpanSet(_inner=result) if result is not None else None
        elif isinstance(other, FloatSpanSet):
            result = super().intersection(other)
            return FloatSpanSet(_inner=result) if result is not None else None
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def __mul__(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_floatspanset_int, intersection_spanset_spanset,
            intersection_spanset_span
        """
        return self.intersection(other)

    def minus(self, other: Time) -> FloatSpanSet:
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            minus_spanset_span, minus_spanset_spanset, minus_floatspanset_int
        """
        if isinstance(other, float):
            result = minus_floatspanset_int(self._inner, float)
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
            minus_floatspanset_int
        """
        return self.minus(other)

    def union(self, other: Time) -> FloatSpanSet:
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`FloatSpanSet` instance.

        MEOS Functions:
            union_floatspanset_int, union_spanset_spanset,
            union_spanset_span
        """
        if isinstance(other, float):
            result = union_floatspanset_int(self._inner, float)
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
            union_floatspanset_int, union_spanset_spanset,
            union_spanset_span
        """
        return self.union(other)

