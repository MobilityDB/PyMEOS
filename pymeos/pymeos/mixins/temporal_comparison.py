from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING

from pymeos_cffi import (
    teq_temporal_temporal,
    tne_temporal_temporal,
    tlt_temporal_temporal,
    tle_temporal_temporal,
    tgt_temporal_temporal,
    tge_temporal_temporal,
)

Self = TypeVar("Self", bound="Temporal[Any]")

if TYPE_CHECKING:
    from ..main import TBool
    from ..temporal import Temporal


class TTemporallyEquatable:
    def temporal_equal(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_temporal_temporal
        """
        result = teq_temporal_temporal(self._inner, other._inner)
        return self._factory(result)

    def temporal_not_equal(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_temporal_temporal
        """
        result = tne_temporal_temporal(self._inner, other._inner)
        return self._factory(result)


class TTemporallyComparable:
    def temporal_less(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal less than relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less than relation.

        MEOS Functions:
            tlt_temporal_temporal
        """
        result = tlt_temporal_temporal(self._inner, other._inner)
        return self._factory(result)

    def temporal_less_or_equal(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal less or equal relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less or equal
            relation.

        MEOS Functions:
            tle_temporal_temporal
        """
        result = tle_temporal_temporal(self._inner, other._inner)
        return self._factory(result)

    def temporal_greater_or_equal(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal greater or equal relation between `self` and
        `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater or equal
            relation.

        MEOS Functions:
            tge_temporal_temporal
        """
        result = tge_temporal_temporal(self._inner, other._inner)
        return self._factory(result)

    def temporal_greater(self: Self, other: Temporal) -> TBool:
        """
        Returns the temporal greater than relation between `self` and `other`.

        Args:
            other: A temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater than
            relation.

        MEOS Functions:
            tgt_temporal_temporal
        """
        result = tgt_temporal_temporal(self._inner, other._inner)
        return self._factory(result)
