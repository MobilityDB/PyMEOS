from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Union, List, TYPE_CHECKING, TypeVar

from pymeos_cffi import *
from spans import intrange, floatrange

from ..temporal import Temporal

if TYPE_CHECKING:
    from ..boxes import TBox
    from ..time import TimestampSet, Period, PeriodSet
    from .tfloat import TFloat

TBase = TypeVar('TBase', int, float)
TG = TypeVar('TG', 'TNumber[int]', 'TNumber[float]')
TI = TypeVar('TI', 'TInstant[int]', 'TInstant[float]')
TS = TypeVar('TS', 'TSequence[int]', 'TSequence[float]')
TSS = TypeVar('TSS', 'TSequenceSet[int]', 'TSequenceSet[float]')


class TNumber(Temporal[TBase, TG, TI, TS, TSS], ABC):

    def is_adjacent(self, other: Union[TBox, TNumber, floatrange, intrange,
                                       Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, TBox):
            return adjacent_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return adjacent_tnumber_tnumber(self._inner, other._inner)
        elif isinstance(other, floatrange):
            return adjacent_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, intrange):
            return adjacent_tnumber_span(self._inner, intrange_to_intspan(other))
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[TBox, TNumber, floatrange, intrange,
                                               Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(container, TBox):
            return contained_tnumber_tbox(self._inner, container._inner)
        elif isinstance(container, TNumber):
            return contained_tnumber_tnumber(self._inner, container._inner)
        elif isinstance(container, floatrange):
            return contained_tnumber_span(self._inner, floatrange_to_floatspan(container))
        elif isinstance(container, intrange):
            return contained_tnumber_span(self._inner, intrange_to_intspan(container))
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[TBox, TNumber, floatrange, intrange,
                                      Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(content, TBox):
            return contains_tnumber_tbox(self._inner, content._inner)
        elif isinstance(content, TNumber):
            return contains_tnumber_tnumber(self._inner, content._inner)
        elif isinstance(content, floatrange):
            return contains_tnumber_span(self._inner, floatrange_to_floatspan(content))
        elif isinstance(content, intrange):
            return contains_tnumber_span(self._inner, intrange_to_intspan(content))
        else:
            return super().contains(content)

    def is_left(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return left_tint_int(self._inner, other)
        elif isinstance(other, float):
            return left_tfloat_float(self._inner, other)
        elif isinstance(other, intrange):
            return left_tnumber_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return left_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return left_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return left_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_left(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return overleft_tint_int(self._inner, other)
        elif isinstance(other, float):
            return overleft_tfloat_float(self._inner, other)
        elif isinstance(other, intrange):
            return overleft_tnumber_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return overleft_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return overleft_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overleft_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def overlaps(self, other: Union[TBox, TNumber, floatrange, intrange,
                                    Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, TBox):
            return overlaps_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overlaps_tnumber_tnumber(self._inner, other._inner)
        elif isinstance(other, floatrange):
            return overlaps_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, intrange):
            return overlaps_tnumber_span(self._inner, intrange_to_intspan(other))
        else:
            return super().overlaps(other)

    def is_over_or_right(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return overright_tint_int(self._inner, other)
        elif isinstance(other, float):
            return overright_tfloat_float(self._inner, other)
        elif isinstance(other, intrange):
            return overright_tnumber_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return overright_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return overright_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overright_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_right(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return right_tint_int(self._inner, other)
        elif isinstance(other, float):
            return right_tfloat_float(self._inner, other)
        elif isinstance(other, intrange):
            return right_tnumber_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return right_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return right_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return right_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[TBox, TNumber, floatrange, intrange,
                                   Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, TBox):
            return same_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return same_tnumber_tnumber(self._inner, other._inner)
        elif isinstance(other, floatrange):
            return same_tnumber_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, intrange):
            return same_tnumber_span(self._inner, intrange_to_intspan(other))
        else:
            return super().is_same(other)

    def is_before(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return before_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return before_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_before(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overbefore_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overbefore_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_after(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return after_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return after_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_after(self, other: Union[TBox, TNumber]) -> bool:
        if isinstance(other, TBox):
            return overafter_tnumber_tbox(self._inner, other._inner)
        elif isinstance(other, TNumber):
            return overafter_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def at(self, other: Union[intrange, floatrange, List[intrange], List[floatrange], TBox,
                              datetime, TimestampSet, Period, PeriodSet]) -> TG:
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
        return Temporal._factory(result)

    def minus(self, other: Union[intrange, floatrange, List[intrange], List[floatrange], TBox,
                                 datetime, TimestampSet, Period, PeriodSet]) -> TG:
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
        return Temporal._factory(result)

    def distance(self, other: Union[int, float, TNumber]) -> TFloat:
        if isinstance(other, int):
            result = distance_tfloat_float(self._inner, float(other))
        elif isinstance(other, float):
            result = distance_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = distance_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def nearest_approach_distance(self, other: Union[int, float, TNumber, TBox]) -> float:
        if isinstance(other, int):
            return nad_tfloat_float(self._inner, float(other))
        elif isinstance(other, float):
            return nad_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            return nad_tfloat_tfloat(self._inner, other._inner)
        elif isinstance(other, TBox):
            return nad_tnumber_tbox(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def add(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = add_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = add_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = add_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def radd(self, other: Union[int, float]) -> TNumber:
        if isinstance(other, int):
            result = add_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = add_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def sub(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = sub_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = sub_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = sub_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def rsub(self, other: Union[int, float]) -> TNumber:
        if isinstance(other, int):
            result = sub_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = sub_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def mul(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = mult_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = mult_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = mult_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def rmul(self, other: Union[int, float]) -> TNumber:
        if isinstance(other, int):
            result = mult_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = mult_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def div(self, other: Union[int, float, TNumber]) -> TNumber:
        if isinstance(other, int):
            result = div_tint_int(self._inner, other)
        elif isinstance(other, float):
            result = div_tfloat_float(self._inner, other)
        elif isinstance(other, TNumber):
            result = div_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def rdiv(self, other: Union[int, float]) -> TNumber:
        if isinstance(other, int):
            result = div_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = div_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

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
