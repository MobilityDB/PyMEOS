from typing import TypeVar

from pymeos_cffi import (
    temporal_eq,
    temporal_ne,
    temporal_lt,
    temporal_le,
    temporal_gt,
    temporal_ge,
)

Self = TypeVar("Self", bound="Temporal[Any]")


class TComparable:
    def __eq__(self: Self, other):
        """
        Returns whether `self` is equal to `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the equality relation.

        MEOS Functions:
            temporal_eq
        """
        return temporal_eq(self._inner, other._inner)

    def __ne__(self: Self, other):
        """
        Returns whether `self` is not equal to `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the not equal relation.

        MEOS Functions:
            temporal_ne
        """
        return temporal_ne(self._inner, other._inner)

    def __lt__(self: Self, other):
        """
        Returns whether `self` is less than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the less than relation.

        MEOS Functions:
            temporal_lt
        """
        return temporal_lt(self._inner, other._inner)

    def __le__(self: Self, other):
        """
        Returns whether `self` is less or equal than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the less or equal than relation.

        MEOS Functions:
            temporal_le
        """
        return temporal_le(self._inner, other._inner)

    def __gt__(self: Self, other):
        """
        Returns whether `self` is greater than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the greater than relation.

        MEOS Functions:
            temporal_gt
        """
        return temporal_gt(self._inner, other._inner)

    def __ge__(self: Self, other):
        """
        Returns whether `self` is greater or equal than `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`bool` with the result of the greater or equal than
            relation.

        MEOS Functions:
            temporal_ge
        """
        return temporal_ge(self._inner, other._inner)
