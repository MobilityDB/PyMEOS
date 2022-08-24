from __future__ import annotations

from abc import ABC
from typing import Union

from pymeos_cffi import tnumber_integral, tnumber_twavg
from pymeos_cffi.functions import add_tint_int, add_tfloat_float, add_tnumber_tnumber, div_tint_int, div_tfloat_float, \
    div_tnumber_tnumber, sub_tnumber_tnumber, sub_tfloat_float, sub_tint_int, mult_tint_int, mult_tfloat_float, \
    mult_tnumber_tnumber, tnumber_degrees, tnumber_derivative

from ..temporal import Temporal


class TNumber(Temporal, ABC):

    @property
    def min_value(self):
        """
        Minimum value.
        """
        return min(self.values)

    @property
    def max_value(self):
        """
        Maximum value.
        """
        return max(self.values)

    def add(self, other: Union[int, float, TNumber]) -> TNumber:
        from ..factory import _TemporalFactory
        if isinstance(other, int):
            return _TemporalFactory.create_temporal(add_tint_int(self._inner, other))
        elif isinstance(other, float):
            return _TemporalFactory.create_temporal(add_tfloat_float(self._inner, other))
        elif isinstance(other, TNumber):
            return _TemporalFactory.create_temporal(add_tnumber_tnumber(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def sub(self, other: Union[int, float, TNumber]) -> TNumber:
        from ..factory import _TemporalFactory
        if isinstance(other, int):
            return _TemporalFactory.create_temporal(sub_tint_int(self._inner, other))
        elif isinstance(other, float):
            return _TemporalFactory.create_temporal(sub_tfloat_float(self._inner, other))
        elif isinstance(other, TNumber):
            return _TemporalFactory.create_temporal(sub_tnumber_tnumber(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def mul(self, other: Union[int, float, TNumber]) -> TNumber:
        from ..factory import _TemporalFactory
        if isinstance(other, int):
            return _TemporalFactory.create_temporal(mult_tint_int(self._inner, other))
        elif isinstance(other, float):
            return _TemporalFactory.create_temporal(mult_tfloat_float(self._inner, other))
        elif isinstance(other, TNumber):
            return _TemporalFactory.create_temporal(mult_tnumber_tnumber(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def div(self, other: Union[int, float, TNumber]) -> TNumber:
        from ..factory import _TemporalFactory
        if isinstance(other, int):
            return _TemporalFactory.create_temporal(div_tint_int(self._inner, other))
        elif isinstance(other, float):
            return _TemporalFactory.create_temporal(div_tfloat_float(self._inner, other))
        elif isinstance(other, TNumber):
            return _TemporalFactory.create_temporal(div_tnumber_tnumber(self._inner, other._inner))
        raise TypeError(f'Operation not supported with type {other.__class__}')

    def to_degrees(self) -> TNumber:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tnumber_degrees(self._inner))

    def derivative(self) -> TNumber:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tnumber_derivative(self._inner))

    def integral(self) -> float:
        return tnumber_integral(self._inner)

    def time_weighted_average(self) -> float:
        return tnumber_twavg(self._inner)

    def __add__(self, other):
        return self.add(other)

    def __sub__(self, other):
        return self.sub(other)

    def __mul__(self, other):
        return self.mul(other)

    def __truediv__(self, other):
        return self.div(other)
