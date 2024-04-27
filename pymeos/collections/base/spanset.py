from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union
from typing import TypeVar, Type, Callable, Any, TYPE_CHECKING, List

from pymeos_cffi import *

from .collection import Collection

if TYPE_CHECKING:
    from .span import Span

T = TypeVar("T")
Self = TypeVar("Self", bound="Span[Any]")


class SpanSet(Collection[T], ABC):
    """
    Base class for all spanset classes.
    """

    __slots__ = ["_inner"]

    _parse_function: Callable[[str], "CData"] = None
    _parse_value_function: Callable[[Union[str, T]], Any] = None

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        span_list: Optional[List[Union[str, Span]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__()
        assert (_inner is not None) or (
            (string is not None) != (span_list is not None)
        ), "Either string must be not None or span_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            spans = [self.__class__._parse_value_function(p) for p in span_list]
            self._inner = spanset_make(spans, normalize, True)

    def __copy__(self: Self) -> Self:
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`SpanSet` instance

        MEOS Functions:
            spanset_copy
        """
        inner_copy = spanset_copy(self._inner)
        return self.__class__(_inner=inner_copy)

    @classmethod
    def from_wkb(cls: Type[Self], wkb: bytes) -> Self:
        """
        Returns a `SpanSet` from its WKB representation.

        Args:
            wkb: The WKB string.

        Returns:
            A new :class:`SpanSet` instance

        MEOS Functions:
            spanset_from_wkb
        """
        result = spanset_from_wkb(wkb)
        return cls(_inner=result)

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str) -> Self:
        """
        Returns a `SpanSet` from its WKB representation in hex-encoded ASCII.
        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`SpanSet` instance

        MEOS Functions:
            spanset_from_hexwkb
        """
        result = spanset_from_hexwkb(hexwkb)
        return cls(_inner=result)

    # ------------------------- Output ----------------------------------------
    @abstractmethod
    def __str__(self):
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

        MEOS Functions:
            tstzspanset_out
        """
        return f"{self.__class__.__name__}" f"({self})"

    def as_wkb(self) -> bytes:
        """
        Returns the WKB representation of ``self``.

        Returns:
            A :class:`str` object with the WKB representation of ``self``.

        MEOS Functions:
            spanset_as_wkb
        """
        return spanset_as_wkb(self._inner, 4)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.
        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            spanset_as_hexwkb
        """
        return spanset_as_hexwkb(self._inner, -1)[0]

    # ------------------------- Conversions -----------------------------------
    @abstractmethod
    def to_span(self) -> Span:
        """
        Returns a span that encompasses ``self``.

        Returns:
            A new :class:`Span` instance

        MEOS Functions:
            spanset_span
        """
        return spanset_span(self._inner)

    # ------------------------- Accessors -------------------------------------

    def num_spans(self) -> int:
        """
        Returns the number of spans in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            spanset_num_spans
        """
        return spanset_num_spans(self._inner)

    @abstractmethod
    def start_span(self) -> Span:
        """
        Returns the first span in ``self``.
        Returns:
            A :class:`Span` instance

        MEOS Functions:
            spanset_start_span
        """
        return spanset_start_span(self._inner)

    @abstractmethod
    def end_span(self) -> Span:
        """
        Returns the last span in ``self``.
        Returns:
            A :class:`Span` instance

        MEOS Functions:
            spanset_end_span
        """
        return spanset_end_span(self._inner)

    @abstractmethod
    def span_n(self, n: int) -> Span:
        """
        Returns the n-th span in ``self``.
        Returns:
            A :class:`Span` instance

        MEOS Functions:
            spanset_span_n
        """
        return spanset_span_n(self._inner, n + 1)

    @abstractmethod
    def spans(self) -> List[Span]:
        """
        Returns the list of tstzspans in ``self``.
        Returns:
            A :class:`list[TsTzSpan]` instance

        MEOS Functions:
            spanset_spans
        """
        return spanset_spans(self._inner)

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            spanset_hash
        """
        return spanset_hash(self._inner)

    # ------------------------- Transformations -------------------------------

    # ------------------------- Topological Operations ------------------------
    def is_adjacent(self, other) -> bool:
        """
        Returns whether ``self`` is adjacent to ``other``. That is, they share a bound but only one of them
        contains it.

        Args:
            other: object to compare with

        Returns:
            True if adjacent, False otherwise

        MEOS Functions:
            adjacent_spanset_span, adjacent_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return adjacent_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return adjacent_spanset_spanset(self._inner, other._inner)
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
            contained_spanset_span, contained_spanset_spanset
        """
        from .span import Span

        if isinstance(container, Span):
            return contained_spanset_span(self._inner, container._inner)
        elif isinstance(container, SpanSet):
            return contained_spanset_spanset(self._inner, container._inner)
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
        contains_spanset_span, contains_spanset_spanset,
        """
        from .span import Span

        if isinstance(content, Span):
            return contains_spanset_span(self._inner, content._inner)
        elif isinstance(content, SpanSet):
            return contains_spanset_spanset(self._inner, content._inner)
        else:
            raise TypeError(f"Operation not supported with type {content.__class__}")

    def __contains__(self, item):
        """
        Returns whether ``self`` contains ``content``.

        Args:
            item: temporal object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_spanset_span, contains_spanset_spanset
        """
        return self.contains(item)

    def overlaps(self, other) -> bool:
        """
        Returns whether ``self`` overlaps ``other``. That is, both share at least an instant

        Args:
            other: temporal object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_spanset_span, overlaps_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return overlaps_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overlaps_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_same(self, other) -> bool:
        """
        Returns whether the bounding span of `self` is the same as the bounding span of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if same, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_same`
        """
        return self.to_span().is_same(other)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other) -> bool:
        """
        Returns whether ``self`` is strictly to the left of ``other``. That is, ``self`` ends before ``other`` starts.

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
        before_tstzspanset_timestamp, left_spanset_span, left_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return left_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return left_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_left(self, other) -> bool:
        """
        Returns whether ``self`` is to the left of ``other`` allowing overlap. That is, ``self`` ends before ``other`` ends (or
        at the same time).

        Args:
            other: temporal object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_spanset_span, overleft_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return overleft_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overleft_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_right(self, other) -> bool:
        """
        Returns whether ``self`` is to the right of ``other`` allowing overlap. That is, ``self`` starts after ``other`` starts
        (or at the same time).

        Args:
            other: temporal object to compare with

        Returns:
            True if overlapping or after, False otherwise

        MEOS Functions:
            overright_spanset_span, overright_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return overright_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return overright_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_right(self, other) -> bool:
        """
        Returns whether ``self`` is strictly to the right of ``other``.That is, ``self`` starts after ``other`` ends.

        Args:
            other: temporal object to compare with

        Returns:
            True if after, False otherwise

        MEOS Functions:
            right_spanset_span, right_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return right_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return right_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Distance Operations ---------------------------
    def distance(self, other):
        """
        Returns the distance between ``self`` and ``other``.

        Args:
            other: object to compare with

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
        intersection_spanset_spanset, intersection_spanset_span
        """
        from .span import Span

        if isinstance(other, Span):
            return intersection_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return intersection_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def __mul__(self, other):
        """
        Returns the temporal intersection of ``self`` and ``other``.

        Args:
            other: temporal object to intersect with

        Returns:
            A :class:`Time` instance. The actual class depends on ``other``.

        MEOS Functions:
        intersection_tstzspanset_timestamp, intersection_spanset_spanset, intersection_spanset_span
        """
        return self.intersection(other)

    @abstractmethod
    def minus(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`TsTzSpanSet` instance.

        MEOS Functions:
        minus_spanset_span, minus_spanset_spanset
        """
        from .span import Span

        if isinstance(other, Span):
            return minus_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return minus_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def __sub__(self, other):
        """
        Returns the temporal difference of ``self`` and ``other``.

        Args:
            other: temporal object to diff with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        minus_spanset_span, minus_spanset_spanset, minus_tstzspanset_timestamp
        """
        return self.minus(other)

    @abstractmethod
    def union(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
            union_tstzspanset_timestamp, union_spanset_spanset,
            union_spanset_span
        """
        from .span import Span

        if isinstance(other, Span):
            return union_spanset_span(self._inner, other._inner)
        elif isinstance(other, SpanSet):
            return union_spanset_spanset(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def __add__(self, other):
        """
        Returns the temporal union of ``self`` and ``other``.

        Args:
            other: temporal object to merge with

        Returns:
            A :class:`PeriodSet` instance.

        MEOS Functions:
        union_tstzspanset_timestamp, union_spanset_spanset, union_spanset_span
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
            spanset_eq
        """
        if isinstance(other, self.__class__):
            return spanset_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Return whether ``self`` and ``other`` are not equal.

        Args:
            other: temporal object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            spanset_ne
        """
        if isinstance(other, self.__class__):
            return spanset_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            spanset_lt
        """
        if isinstance(other, self.__class__):
            return spanset_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            spanset_le
        """
        if isinstance(other, self.__class__):
            return spanset_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            spanset_gt
        """
        if isinstance(other, self.__class__):
            return spanset_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: temporal object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            spanset_ge
        """
        if isinstance(other, self.__class__):
            return spanset_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")
