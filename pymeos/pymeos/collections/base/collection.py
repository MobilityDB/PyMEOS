from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type

T = TypeVar("T")
Self = TypeVar("Self")


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
    def read_from_cursor(cls: Type[Self], value, _=None):
        """
        Reads a :class:`Collection` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        return cls(string=value)
