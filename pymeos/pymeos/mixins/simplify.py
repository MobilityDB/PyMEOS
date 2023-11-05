from datetime import timedelta
from typing import TypeVar

from pymeos_cffi import (
    temporal_simplify_min_dist,
    temporal_simplify_min_tdelta,
    timedelta_to_interval,
    temporal_simplify_dp,
    temporal_simplify_max_dist,
)

Self = TypeVar("Self", bound="Temporal[Any]")


class TSimplifiable:
    def simplify_min_distance(self: Self, distance: float) -> Self:
        """
        Simplifies a temporal value ensuring that consecutive values are at least a
        certain distance apart.

        Args:
            distance: :class:`float` indicating the minimum distance between two points.

        Returns:
            :class:`Temporal` with the same subtype as the input.

        MEOS Functions:
            temporal_simplify_min_dist
        """
        return self.__class__(_inner=temporal_simplify_min_dist(self._inner, distance))

    def simplify_min_tdelta(self: Self, distance: timedelta) -> Self:
        """
        Simplifies a temporal value ensuring that consecutive values are at least a
        certain time apart.

        Args:
            distance: :class:`timedelta` indicating the minimum time between two points.

        Returns:
            :class:`Temporal` with the same subtype as the input.

        MEOS Functions:
            temporal_simplify_min_tdelta
        """
        delta = timedelta_to_interval(distance)
        return self.__class__(_inner=temporal_simplify_min_tdelta(self._inner, delta))

    def simplify_douglas_peucker(
        self: Self, distance: float, synchronized: bool = False
    ) -> Self:
        """
        Simplifies a temporal value using the Douglas-Peucker line simplification
        algorithm.

        Args:
            distance: :class:`float` indicating the minimum distance between two points.
            synchronized: If `True`, the Synchronized Distance will be used. Otherwise,
                the spatial-only distance will be used.

        Returns:
            :class:`Temporal` with the same subtype as the input.

        MEOS Functions:
            temporal_simplify_dp
        """
        return self.__class__(
            _inner=temporal_simplify_dp(self._inner, distance, synchronized)
        )

    def simplify_max_distance(
        self: Self, distance: float, synchronized: bool = False
    ) -> Self:
        """
        Simplifies a temporal value using a single-pass Douglas-Peucker line
        simplification algorithm.

        Args:
            distance: :class:`float` indicating the minimum distance between two points.
            synchronized: If `True`, the Synchronized Distance will be used. Otherwise,
                the spatial-only distance will be used.

        Returns:
            :class:`Temporal` with the same subtype as the input.

        MEOS Functions:
            temporal_simplify_max_dist
        """
        return self.__class__(
            _inner=temporal_simplify_max_dist(self._inner, distance, synchronized)
        )
