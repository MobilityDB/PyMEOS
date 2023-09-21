from __future__ import annotations

from enum import IntEnum


class TInterpolation(IntEnum):
    """
    Enum for representing the different types of interpolation present in
    PyMEOS.
    """
    NONE = 0
    DISCRETE = 1
    STEPWISE = 2
    LINEAR = 3

    @staticmethod
    def from_string(source: str, none: bool = True) -> TInterpolation:
        """
        Returns the :class:`TInterpolation` element equivalent to `source`.

        Args:
            source: :class:`string` representing the interpolation
            none: indicates whether to return `TIntepolation.NONE` when
            `source` represents an invalid interpolation

        Returns:
            A new :class:`TInterpolation` instance.

        Raises:
            ValueError: when `source` doesn't represent any valid interpolation
            and `none` is False

        """
        if source.lower() == 'discrete':
            return TInterpolation.DISCRETE
        elif source.lower() == 'linear':
            return TInterpolation.LINEAR
        elif source.lower() == 'stepwise' or source.lower() == 'step':
            return TInterpolation.STEPWISE
        elif source.lower() == 'none' or none:
            return TInterpolation.NONE
        else:
            raise ValueError(f"Value {source} doesn't represent any valid interpolation")
