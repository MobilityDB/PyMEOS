from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypeVar

from ..base.collection import Collection

Self = TypeVar('Self', bound='Set[Any]')


class TimeCollection(Collection[datetime], ABC):

    def is_before(self, other) -> bool:
        return self.is_left(other)

    def is_over_or_before(self, other) -> bool:
        return self.is_over_or_left(other)

    def is_over_or_after(self, other) -> bool:
        return self.is_over_or_right(other)

    def is_after(self, other) -> bool:
        return self.is_right(other)
