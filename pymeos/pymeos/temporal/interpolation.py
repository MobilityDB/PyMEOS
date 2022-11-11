from __future__ import annotations

from enum import IntEnum


class TInterpolation(IntEnum):
    NONE = 0
    DISCRETE = 1
    STEPWISE = 2
    LINEAR = 3

    @staticmethod
    def from_string(source: str, none: bool = True) -> TInterpolation:
        if source.lower() == 'discrete':
            return TInterpolation.DISCRETE
        elif source.lower() == 'linear':
            return TInterpolation.LINEAR
        elif source.lower() == 'stepwise':
            return TInterpolation.STEPWISE
        elif source.lower() == 'none' or none:
            return TInterpolation.NONE
        else:
            raise ValueError(f"Value {source} doesn't represent any valid interpolation")
