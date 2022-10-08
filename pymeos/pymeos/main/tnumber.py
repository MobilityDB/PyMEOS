from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Union, List, TYPE_CHECKING

from pymeos_cffi import tnumber_integral, tnumber_twavg, tnumber_at_span, intrange_to_intspan, \
    floatrange_to_floatspan, tnumber_at_spans, tnumber_at_tbox
from pymeos_cffi.functions import add_tint_int, add_tfloat_float, add_tnumber_tnumber, div_tint_int, div_tfloat_float, \
    div_tnumber_tnumber, sub_tnumber_tnumber, sub_tfloat_float, sub_tint_int, mult_tint_int, mult_tfloat_float, \
    mult_tnumber_tnumber, tnumber_minus_span, tnumber_minus_spans, \
    tnumber_minus_tbox, add_int_tint, add_float_tfloat, sub_float_tfloat, sub_int_tint, mult_int_tint, \
    mult_float_tfloat, div_float_tfloat, div_int_tint
from spans import intrange, floatrange

from ..temporal import Temporal

if TYPE_CHECKING:
    from ..boxes import TBox
    from ..time import TimestampSet, Period, PeriodSet


class TNumber(Temporal, ABC):

    def at(self, other: Union[intrange, floatrange, List[intrange], List[floatrange],
                              TBox, datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        from ..boxes import TBox
        if isinstance(other, intrange):
            result = tnumber_at_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            result = tnumber_at_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, list) and isinstance(other[0], intrange):
            spans = [intrange_to_intspan(ir) for ir in other]
            result = tnumber_at_spans(self._inner, spans, len(spans))
        elif isinstance(other, list) and isinstance(other[0], floatrange):
            spans = [floatrange_to_floatspan(fr) for fr in other]
            result = tnumber_at_spans(self._inner, spans, len(spans))
        elif isinstance(other, TBox):
            result = tnumber_at_tbox(self._inner, other._inner)
        else:
            return super().at(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def minus(self, other: Union[intrange, floatrange, List[intrange], List[floatrange],
                                 TBox, datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, intrange):
            result = tnumber_minus_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            result = tnumber_minus_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, list) and isinstance(other[0], intrange):
            spans = [intrange_to_intspan(ir) for ir in other]
            result = tnumber_minus_spans(self._inner, spans, len(spans))
        elif isinstance(other, list) and isinstance(other[0], floatrange):
            spans = [floatrange_to_floatspan(fr) for fr in other]
            result = tnumber_minus_spans(self._inner, spans, len(spans))
        elif isinstance(other, TBox):
            result = tnumber_minus_tbox(self._inner, other._inner)
        else:
            return super().minus(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def add(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = add_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = add_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = add_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def radd(self, other: Union[int, float]):
        if isinstance(other, int):
            result = add_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = add_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def sub(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = sub_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = sub_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = sub_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def rsub(self, other: Union[int, float]):
        if isinstance(other, int):
            result = sub_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = sub_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def mul(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = mult_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = mult_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = mult_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def rmul(self, other: Union[int, float]):
        if isinstance(other, int):
            result = mult_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = mult_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def div(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = div_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = div_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = div_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def rdiv(self, other: Union[int, float]):
        if isinstance(other, int):
            result = div_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = div_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def integral(self) -> float:
        return tnumber_integral(self._inner)

    def time_weighted_average(self) -> float:
        return tnumber_twavg(self._inner)

    def __add__(self, other):
        return self.add(other)

    def __radd__(self, other):
        return self.radd(other)

    def __sub__(self, other):
        return self.sub(other)

    def __rsub__(self, other):
        return self.rsub(other)

    def __mul__(self, other):
        return self.mul(other)

    def __rmul__(self, other):
        return self.rmul(other)

    def __truediv__(self, other):
        return self.div(other)

    def __rtruediv__(self, other):
        return self.rdiv(other)
