from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Generic, TypeVar, Type, Callable, Any, TYPE_CHECKING, Iterable
from typing import Optional, Union, overload, get_args, List

from pymeos_cffi import *

if TYPE_CHECKING:
    from .spanset import SpanSet
    from .span import Span

T = TypeVar('T')
Self = TypeVar('Self', bound='Set[Any]')


class Collection(Generic[T], ABC):
    # ------------------------- Topological Operations ------------------------
    # @abstractmethod
    # def is_adjacent(self, other) -> bool:
        # raise NotImplementedError()

    @abstractmethod
    def is_contained_in(self, container) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def contains(self, content) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __contains__(self, item):
        raise NotImplementedError()

    @abstractmethod
    def overlaps(self, other) -> bool:
        raise NotImplementedError()

    # @abstractmethod
    # def is_same(self, other) -> bool:
        # raise NotImplementedError()

    # ------------------------- Position Operations ---------------------------
    @abstractmethod
    def is_left(self, other) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_over_or_left(self, other) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_over_or_right(self, other) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_right(self, other) -> bool:
        raise NotImplementedError()

    # ------------------------- Database Operations ---------------------------

    # ------------------------- Database Operations ---------------------------
    @classmethod
    def read_from_cursor(cls, value, _=None):
        """
        Reads a :class:`STBox` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return cls(string=value)
