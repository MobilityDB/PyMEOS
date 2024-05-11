from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Union, List, overload
from typing import TypeVar, Type, Callable, Any, TYPE_CHECKING, Iterable

from pymeos_cffi import *

from .collection import Collection

if TYPE_CHECKING:
    from .spanset import SpanSet
    from .span import Span

    from ..number import IntSet, IntSpan, IntSpanSet, FloatSet, FloatSpan, FloatSpanSet
    from ..time import DateSet, DateSpan, DateSpanSet, TsTzSet, TsTzSpan, TsTzSpanSet

T = TypeVar("T")
Self = TypeVar("Self", bound="Set[Any]")


class Set(Collection[T], ABC):
    """
    Base class for all set classes.
    """

    __slots__ = ["_inner"]

    _parse_function: Callable[[str], "CData"] = None
    _parse_value_function: Callable[[Union[str, T]], Any] = None
    _make_function: Callable[[Iterable[Any]], "CData"] = None

    # ------------------------- Constructors ----------------------------------
    def __init__(
        self,
        string: Optional[str] = None,
        *,
        elements: Optional[List[Union[str, T]]] = None,
        _inner=None,
    ):
        super().__init__()
        assert (_inner is not None) or (
            (string is not None) != (elements is not None)
        ), "Either string must be not None or elements must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            parsed_elements = [
                self.__class__._parse_value_function(ts) for ts in elements
            ]
            self._inner = self.__class__._make_function(parsed_elements)

    def __copy__(self: Self) -> Self:
        """
        Return a copy of ``self``.

        Returns:
            A new :class:`Span` instance

        MEOS Functions:
            set_copy
        """
        inner_copy = set_copy(self._inner)
        return self.__class__(_inner=inner_copy)

    @classmethod
    def from_wkb(cls: Type[Self], wkb: bytes) -> Self:
        """
        Returns a `Set` from its WKB representation.
        Args:
            wkb: WKB representation

        Returns:
            A new :class:`Set` instance

        MEOS Functions:
            set_from_wkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_from_wkb(wkb))

    @classmethod
    def from_hexwkb(cls: Type[Self], hexwkb: str) -> Self:
        """
        Returns a `Set` from its WKB representation in hex-encoded ASCII.
        Args:
            hexwkb: WKB representation in hex-encoded ASCII

        Returns:
            A new :class:`Set` instance

        MEOS Functions:
            set_from_hexwkb
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection((set_from_hexwkb(hexwkb)))

    # ------------------------- Output ----------------------------------------
    @abstractmethod
    def __str__(self) -> str:
        """
        Return the string representation of the content of ``self``.

        Returns:
            A new :class:`str` instance
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Return the string representation of ``self``.

        Returns:
            A new :class:`str` instance

        MEOS Functions:
            set_out
        """
        return f"{self.__class__.__name__}" f"({self})"

    def as_wkb(self) -> bytes:
        """
        Returns the WKB representation of ``self``.
        Returns:
            A :class:`str` object with the WKB representation of ``self``.

        MEOS Functions:
            set_as_wkb
        """
        return set_as_wkb(self._inner, 4)

    def as_hexwkb(self) -> str:
        """
        Returns the WKB representation of ``self`` in hex-encoded ASCII.
        Returns:
            A :class:`str` object with the WKB representation of ``self`` in hex-encoded ASCII.

        MEOS Functions:
            set_as_hexwkb
        """
        return set_as_hexwkb(self._inner, -1)[0]

    # ------------------------- Conversions -----------------------------------
    @overload
    def to_span(self: Type[IntSet]) -> IntSpan: ...

    @overload
    def to_span(self: Type[FloatSet]) -> FloatSpan: ...

    @overload
    def to_span(self: Type[TsTzSet]) -> TsTzSpan: ...

    @overload
    def to_span(self: Type[DateSet]) -> DateSpan: ...

    def to_span(self) -> Span:
        """
        Returns a span that encompasses ``self``.

        Returns:
            A new :class:`Span` instance

        MEOS Functions:
            set_span
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_span(self._inner))

    @overload
    def to_spanset(self: Type[IntSet]) -> IntSpanSet: ...

    @overload
    def to_spanset(self: Type[FloatSet]) -> FloatSpanSet: ...

    @overload
    def to_spanset(self: Type[TsTzSet]) -> TsTzSpanSet: ...

    @overload
    def to_spanset(self: Type[DateSet]) -> DateSpanSet: ...

    def to_spanset(self) -> SpanSet:
        """
        Returns a SpanSet that contains a Span for each element in ``self``.

        Returns:
            A new :class:`SpanSet` instance

        MEOS Functions:
            set_to_spanset
        """
        from ...factory import _CollectionFactory

        return _CollectionFactory.create_collection(set_to_spanset(self._inner))

    # ------------------------- Accessors -------------------------------------

    def num_elements(self) -> int:
        """
        Returns the number of elements in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            set_num_values
        """
        return set_num_values(self._inner)

    def __len__(self):
        """
        Returns the number of elements in ``self``.
        Returns:
            An :class:`int`

        MEOS Functions:
            set_num_values
        """
        return self.num_elements()

    @abstractmethod
    def start_element(self) -> T:
        """
        Returns the first element in ``self``.
        Returns:
            A :class:`T` instance
        """
        raise NotImplementedError()

    @abstractmethod
    def end_element(self) -> T:
        """
        Returns the last element in ``self``.
        Returns:
            A :class:`T` instance
        """
        raise NotImplementedError()

    @abstractmethod
    def element_n(self, n: int) -> T:
        """
        Returns the n-th element in ``self``.
        Returns:
            A :class:`T` instance
        """
        if n < 0 or n >= self.num_elements():
            raise IndexError(f"Index {n} out of bounds")

    @abstractmethod
    def elements(self) -> List[T]:
        """
        Returns the list of distinct elements in ``self``.
        Returns:
            A :class:`list[T]` instance
        """
        raise NotImplementedError()

    def __hash__(self) -> int:
        """
        Return the hash representation of ``self``.

        Returns:
            A new :class:`int` instance

        MEOS Functions:
            set_hash
        """
        return set_hash(self._inner)

    # ------------------------- Topological Operations ------------------------

    def is_contained_in(self, container) -> bool:
        """
        Returns whether ``self`` is contained in ``container``.

        Args:
            container: object to compare with

        Returns:
            True if contained, False otherwise

        MEOS Functions:
            contained_set_set
        """
        if isinstance(container, Set):
            return contained_set_set(self._inner, container._inner)
        else:
            raise TypeError(f"Operation not supported with type {container.__class__}")

    @abstractmethod
    def contains(self, content) -> bool:
        """
        Returns whether ``self`` contains ``content``.

        Args:
            content: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set
        """
        if isinstance(content, Set):
            return contains_set_set(self._inner, content._inner)
        else:
            raise TypeError(f"Operation not supported with type {content.__class__}")

    def __contains__(self, item):
        """
        Returns whether ``self`` contains ``content``.

        Args:
            item: object to compare with

        Returns:
            True if contains, False otherwise

        MEOS Functions:
            contains_set_set
        """
        return self.contains(item)

    def overlaps(self, other) -> bool:
        """
        Returns whether ``self`` overlaps ``other``. That is, both share at least an instant

        Args:
            other: object to compare with

        Returns:
            True if overlaps, False otherwise

        MEOS Functions:
            overlaps_set_set, overlaps_span_span, overlaps_spanset_spanset
        """
        if isinstance(other, Set):
            return overlaps_set_set(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other) -> bool:
        """
        Returns whether ``self`` is strictly to the left of ``other``. That is,
        ``self`` ends before ``other`` starts.

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            left_span_span, left_span_spanset
        """
        if isinstance(other, Set):
            return left_set_set(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_left(self, other) -> bool:
        """
        Returns whether ``self`` is to the left of ``other`` allowing overlap.
        That is, ``self`` ends before ``other`` ends (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if before, False otherwise

        MEOS Functions:
            overleft_span_span, overleft_span_spanset
        """
        if isinstance(other, Set):
            return overleft_set_set(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_over_or_right(self, other) -> bool:
        """
        Returns whether ``self`` is to the right of ``other`` allowing overlap. That is, ``self`` starts after ``other``
        starts (or at the same value).

        Args:
            other: object to compare with

        Returns:
            True if overlapping or to the right, False otherwise

        MEOS Functions:
            overright_span_span, overright_span_spanset
        """
        if isinstance(other, Set):
            return overright_set_set(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")

    def is_right(self, other) -> bool:
        """
        Returns whether ``self`` is strictly to the right of ``other``. That is, the first element in ``self``
        is to the right ``other``.

        Args:
            other: object to compare with

        Returns:
            True if right, False otherwise

        MEOS Functions:
            right_set_set, right_span_span, right_span_spanset
        """
        if isinstance(other, Set):
            return right_set_set(self._inner, other._inner)
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
            A :class:`Collection` instance. The actual class depends on ``other``.

        MEOS Functions:
            intersection_set_set, intersection_spanset_span,
            intersection_spanset_spanset
        """
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __mul__(self, other):
        """
        Returns the intersection of ``self`` and ``other``.

        Args:
            other: object to intersect with

        Returns:
            A :class:`Collection` instance. The actual class depends on ``other``.
        """
        return self.intersection(other)

    @abstractmethod
    def minus(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`Collection` instance. The actual class depends on ``other``.
        """
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __sub__(self, other):
        """
        Returns the difference of ``self`` and ``other``.

        Args:
            other: object to diff with

        Returns:
            A :class:`Collection` instance. The actual class depends on ``other``.
        """
        return self.minus(other)

    @abstractmethod
    def subtract_from(self, other):
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: object to subtract ``self`` from

        Returns:
            A :class:`Collection` instance or an element instance. The actual class depends on ``other``.

        See Also:
            :meth:`minus`
        """
        raise NotImplementedError()

    def __rsub__(self, other):
        """
        Returns the difference of ``other`` and ``self``.

        Args:
            other: object to subtract ``self`` from

        Returns:
            A :class:`Collection` instance or an element instance. The actual class depends on ``other``.
        """
        return self.subtract_from(other)

    @abstractmethod
    def union(self, other):
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`Collection` instance. The actual class depends on ``other``.
        """
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __add__(self, other):
        """
        Returns the union of ``self`` and ``other``.

        Args:
            other: object to merge with

        Returns:
            A :class:`Collection` instance. The actual class depends on ``other``.
        """
        return self.union(other)

    # ------------------------- Comparisons -----------------------------------
    def __eq__(self, other):
        """
        Returns whether ``self`` and ``other`` are equal.

        Args:
            other: object to compare with

        Returns:
            True if equal, False otherwise

        MEOS Functions:
            set_eq
        """
        if isinstance(other, self.__class__):
            return set_eq(self._inner, other._inner)
        return False

    def __ne__(self, other):
        """
        Returns whether ``self`` and ``other`` are not equal.

        Args:
            other: object to compare with

        Returns:
            True if not equal, False otherwise

        MEOS Functions:
            set_ne
        """
        if isinstance(other, self.__class__):
            return set_ne(self._inner, other._inner)
        return True

    def __lt__(self, other):
        """
        Return whether ``self`` is less than ``other``.

        Args:
            other: object to compare with

        Returns:
            True if less than, False otherwise

        MEOS Functions:
            set_lt
        """
        if isinstance(other, self.__class__):
            return set_lt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __le__(self, other):
        """
        Return whether ``self`` is less than or equal to ``other``.

        Args:
            other: object to compare with

        Returns:
            True if less than or equal, False otherwise

        MEOS Functions:
            set_le
        """
        if isinstance(other, self.__class__):
            return set_le(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __gt__(self, other):
        """
        Return whether ``self`` is greater than ``other``.

        Args:
            other: object to compare with

        Returns:
            True if greater than, False otherwise

        MEOS Functions:
            set_gt
        """
        if isinstance(other, self.__class__):
            return set_gt(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __ge__(self, other):
        """
        Return whether ``self`` is greater than or equal to ``other``.

        Args:
            other: object to compare with

        Returns:
            True if greater than or equal, False otherwise

        MEOS Functions:
            set_ge
        """
        if isinstance(other, self.__class__):
            return set_ge(self._inner, other._inner)
        raise TypeError(f"Operation not supported with type {other.__class__}")
