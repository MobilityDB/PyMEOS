from abc import ABC
from datetime import datetime

from ..base.collection import Collection


class TimeCollection(Collection[datetime], ABC):
    def is_before(self, other) -> bool:
        return self.is_left(other)

    def is_over_or_before(self, other) -> bool:
        return self.is_over_or_left(other)

    def is_over_or_after(self, other) -> bool:
        return self.is_over_or_right(other)

    def is_after(self, other) -> bool:
        return self.is_right(other)
