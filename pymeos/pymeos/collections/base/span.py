from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union
from typing import TypeVar, Type, Callable, Any, TYPE_CHECKING

from pymeos_cffi import *

from .collection import Collection

if TYPE_CHECKING:
    from .spanset import SpanSet

T = TypeVar("T")
Self = TypeVar("Self", bound="Span[Any]")


class Span(Collection[T], ABC):
    """
    Base class for all span classes.
    """

    __slots__ = ["_inner"]

    _parse_function: Callable[[str], "CData"] = None
    _parse_value_function: Callable[[Union[str, T]], Any] = None
    _make_function: Callable[[Any, Any, bool, bool], "CData"] = None

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        lower: Optional[Union[str, T]] = None,
        upper: Optional[Union[str, T]] = None,
        lower_inc: Optional[bool] = True,
        upper_inc: Optional[bool] = False,
        _inner=None,
    ):
        super().__init__()
        assert (_inner is not None) or (
            (string is not None) != (lower is not None and upper is not None)
        ), "Either string must be not None or both lower and upper must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            lower_converted = self.__class__._parse_value_function(lower)
            upper_converted = self.__class__._parse_value_function(upper)
            self._inner = self.__class__._make_function(
                lower_converted, upper_converted, lower_inc, upper_inc
            )

    def __copy__(self: Self) -> Self:
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Span` instance

        MEOS Functions:
            span_copy
        """
        inner_copy = span_copy(self._inner)
        return self.__class__(_inner=inner_copy)

    @classmethod
    def from_wkb(cls: Type[Self], wkb: bytes) -> Self:
        """
        Returns a `TsTzSpan` from its WKB representation.

        Args:
            wkb: The WKB string.

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            span_from_wkb
        """
        return cls(_inner=(span_from_wkb(wkb)))

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str) -> Self:
        """
        Returns a `TsTzSpan` from its WKB representation in hex-encoded ASCII.

        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`TsTzSpan` instance

        MEOS Functions:
            span_from_hexwkb
        """
        result = span_from_hexwkb(hexwkb)
        return cls(_inner=result)

    # ------------------------- Output ----------------------------------------
    @abstractmethod
    def __str__(self) -> str:
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance
        """
        raise NotImplementedError()

    def __repr__(self):
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance
        """
        return f"{self.__class__.__name__}" f"({self})"

    def as_wkb(self) -> bytes:
        """
        Returns the WKB representation of ``self``.

        Returns:
            A :class:`str` object with the WKB representation of ``self``.

        MEOS Functions:
            span_as_wkb
        """
        return span_as_wkb(self._inner, 4)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.

        Returns:
            A :class:`str` object with the WKB representation of ``self`` in
            hex-encoded ASCII.

        MEOS Functions:
            span_as_hexwkb
        """
        return span_as_hexwkb(self._inner, -1)[0]

    # ------------------------- Conversions -----------------------------------
    @abstractmethod
    def to_spanset(self) -> SpanSet:
        """
        Returns a tstzspan set containing ``self``.

        Returns:
            A new :class:`TsTzSpanSet` instance

        MEOS Functions:
            span_to_spanset
        """
        return span_to_spanset(self._inner)

    # ------------------------- Accessors -------------------------------------
    @abstractmethod
    def lower(self) -> T:
        """
        Returns the lower bound of a tstzspan
        """
        return NotImplementedError()

    @abstractmethod
    def upper(self) -> T:
        """
        Returns the upper bound of a tstzspan
        """
        return NotImplementedError()

    def lower_inc(self) -> bool:
        """
        Returns whether the lower bound of the tstzspan is inclusive or not

        Returns:
            True if the lower bound of the tstzspan is inclusive and False
            otherwise

        MEOS Functions:
            span_lower_inc
        """
        return span_lower_inc(self._inner)

    def upper_inc(self) -> bool:
        """
        Returns whether the upper bound of the tstzspan is inclusive or not

        Returns:
            True if the upper bound of the tstzspan is inclusive and False
            otherwise

        MEOS Functions:
            span_upper_inc
        """
        return span_upper_inc(self._inner)

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            span_hash
        """
        return span_hash(self._inner)

    # ------------------------- Topological Operations ------------------------
    @abstractmethod
    def is_adjacent(self: Self, other) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share
        a bound but only one of them contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_span_span, adjacent_span_spanset,
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return adjacent_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return adjacent_spanset_span(other._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_contained_in(self, container) -> bool:
        """
        Returns whether ``self`` is contained in ``container``.

        Args:
            container: temporal object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_span_span, contained_span_spanset, contained_tstzspan_temporal
        """
        from .spanset import SpanSet

        if isinstance(container, Span):
            return contained_span_span(self._inner, container._inner)
        elif isinstance(container, SpanSet):
            return contained_span_spanset(self._inner, container._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")

    def contains(self, content) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_tstzspan_timestamp,
            contains_tstzspan_tstzset, contains_tstzspan_temporal
        """
        from .spanset import SpanSet

        if isinstance(content, Span):
            return contains_span_span(self._inner, content._inner)
        elif isinstance(content, SpanSet):
            return contains_span_spanset(self._inner, content._inner)
        else:
            raise TypeError(f"Operation not supported with type {content.__class__}")

    def __contains__(self, item):
        """
        Return whether ``self`` contains ``item``.

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_span_span, contains_span_spanset, contains_tstzspan_timestamp,
            contains_tstzspan_tstzset, contains_tstzspan_temporal
        """
        return self.contains(item)

    def overlaps(self, other) -> bool:
        """
        Returns whether ``self`` overlaps ``other``. That is, both share at
        least an element.

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_span_span, overlaps_span_spanset
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return overlaps_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overlaps_spanset_span(other._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_same(self, other) -> bool:
        """
        Returns whether ``self`` and the bounding tstzspan of ``other`` is the
        same.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            same_tstzspan_temporal
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return span_eq(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return span_eq(self._inner, spanset_span(other._inner))
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other) -> bool:
        """
        Returns whether ``self`` is strictly before ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return left_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return left_span_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_left(self, other) -> bool:
        """
        Returns whether ``self`` is before ``other`` allowing overlap. That is,
        ``self`` ends before ``other`` ends (or at the same time).

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return overleft_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overleft_span_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_right(self, other) -> bool:
        """
        Returns whether ``self`` is after ``other`` allowing overlap. That is,
        ``self`` starts after ``other`` starts (or at the same time).

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset, overafter_tstzspan_timestamp,
            overafter_tstzspan_tstzset, overafter_tstzspan_temporal
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return overright_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overright_span_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_right(self, other) -> bool:
        """
        Returns whether ``self`` is strictly after ``other``. That is, ``self``
        starts after ``other`` ends.

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_span_span, right_span_spanset
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return right_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return right_span_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other):
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other:  object to compare with

        Returns:
            The distance metric in the appropriate format depending on the subclass.
        """
        raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Set Operations --------------------------------
    @abstractmethod
    def intersection(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A collection instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_tstzspan_timestamp
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return intersection_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return intersection_spanset_span(other._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def __mul__(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Span` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_span_span, intersection_spanset_span,
            intersection_tstzspan_timestamp
        """
        return self.intersection(other)

    @abstractmethod
    def minus(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`SpanSet` instance.
        """
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __sub__(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`SpanSet` instance.
        """
        return self.minus(other)

    @abstractmethod
    def union(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`SpanSet` instance.

        MEOS Functions:
        union_spanset_span, union_span_span
        """
        from .spanset import SpanSet

        if isinstance(other, Span):
            return union_span_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return union_spanset_span(other._inner, self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`TsTzSpanSet` instance.

        MEOS Functions:
        union_tstzspan_timestamp, union_spanset_span, union_span_span
        """
        return self.union(other)

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Return whether ``self`` and ``other`` are equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            span_eq
        """
        if isinstance(other, self.__class__):
            return span_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Return whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            span_neq
        """
        if isinstance(other, self.__class__):
            return span_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            span_lt
        """
        if isinstance(other, self.__class__):
            return span_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            span_le
        """
        if isinstance(other, self.__class__):
            return span_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            span_gt
        """
        if isinstance(other, self.__class__):
            return span_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            span_ge
        """
        if isinstance(other, self.__class__):
            return span_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")
