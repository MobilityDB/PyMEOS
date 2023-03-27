from __future__ import annotations

from abc import ABC
from typing import Union, List, TYPE_CHECKING, TypeVar

from pymeos_cffi import *
from spans import intrange, floatrange

from ..temporal import Temporal

if TYPE_CHECKING:
    from ..boxes import TBox
    from ..time import Time
    from .tfloat import TFloat

TBase = TypeVar('TBase', int, float)
TG = TypeVar('TG', 'TNumber[int]', 'TNumber[float]')
TI = TypeVar('TI', 'TInstant[int]', 'TInstant[float]')
TS = TypeVar('TS', 'TSequence[int]', 'TSequence[float]')
TSS = TypeVar('TSS', 'TSequenceSet[int]', 'TSequenceSet[float]')


class TNumber(Temporal[TBase, TG, TI, TS, TSS], ABC):

    def bounding_box(self) -> TBox:
        """
        Returns the bounding box of `self`.

        Returns:
            The bounding box of `self`.

        MEOS Functions:
            tbox_tnumber
        """
        from ..boxes import TBox
        return TBox(_inner=tnumber_to_tbox(self._inner))

    def is_adjacent(self, other: Union[int, float, floatrange, intrange, TBox, TNumber, Time, Temporal]) -> bool:
        """
        Returns whether the bounding box of `self` is adjacent to the bounding box of `other`.

        Args:
            other: A time or temporal object to compare to `self`.

        Returns:
            True if adjacent, False otherwise.

        MEOS Functions:
            adjacent_floatspan_float, adjacent_tbox_tbox, adjacent_span_span
        """
        if isinstance(other, int):
            return adjacent_floatspan_float(tnumber_to_span(self._inner), float(other))
        elif isinstance(other, float):
            return adjacent_floatspan_float(tnumber_to_span(self._inner), other)
        elif isinstance(other, TBox):
            return adjacent_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return adjacent_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        elif isinstance(other, floatrange):
            return adjacent_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, intrange):
            return adjacent_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[TBox, TNumber, floatrange, intrange, Time, Temporal]) -> bool:
        if isinstance(container, TBox):
            return contained_tbox_tbox(tnumber_to_tbox(self._inner), container._inner)
        elif isinstance(container, TNumber):
            return contained_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(container._inner))
        elif isinstance(container, floatrange):
            return contained_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(container))
        elif isinstance(container, intrange):
            return contained_span_span(tnumber_to_span(self._inner), intrange_to_intspan(container))
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[int, float, floatrange, intrange, TBox, TNumber, Time, Temporal]) -> bool:
        if isinstance(content, int):
            return contains_floatspanset_float(tnumber_values(self._inner), float(content))
        elif isinstance(content, float):
            return contains_floatspanset_float(tnumber_values(self._inner), content)
        elif isinstance(content, TBox):
            return contains_tbox_tbox(tnumber_to_tbox(self._inner), content._inner)
        elif isinstance(content, TNumber):
            return contains_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(content._inner))
        elif isinstance(content, floatrange):
            return contains_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(content))
        elif isinstance(content, intrange):
            return contains_span_span(tnumber_to_span(self._inner), intrange_to_intspan(content))
        else:
            return super().contains(content)

    def is_left(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return left_intspan_int(tnumber_to_span(self._inner), other)
        elif isinstance(other, float):
            return left_floatspan_float(tnumber_to_span(self._inner), other)
        elif isinstance(other, intrange):
            return left_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return left_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return left_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return left_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_over_or_left(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return overleft_intspan_int(tnumber_to_span(self._inner), other)
        elif isinstance(other, float):
            return overleft_floatspan_float(tnumber_to_span(self._inner), other)
        elif isinstance(other, intrange):
            return overleft_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return overleft_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return overleft_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return overleft_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def overlaps(self, other: Union[TBox, TNumber, floatrange, intrange, Time, Temporal]) -> bool:
        if isinstance(other, TBox):
            return overlaps_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return overlaps_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        elif isinstance(other, floatrange):
            return overlaps_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, intrange):
            return overlaps_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        else:
            return super().overlaps(other)

    def is_over_or_right(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return overright_intspan_int(tnumber_to_span(self._inner), other)
        elif isinstance(other, float):
            return overright_floatspan_float(tnumber_to_span(self._inner), other)
        elif isinstance(other, intrange):
            return overright_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return overright_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return overright_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return overright_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_right(self, other: Union[int, float, intrange, floatrange, TBox, TNumber]) -> bool:
        if isinstance(other, int):
            return right_intspan_int(tnumber_to_span(self._inner), other)
        elif isinstance(other, float):
            return right_floatspan_float(tnumber_to_span(self._inner), other)
        elif isinstance(other, intrange):
            return right_span_span(tnumber_to_span(self._inner), intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            return right_span_span(tnumber_to_span(self._inner), floatrange_to_floatspan(other))
        elif isinstance(other, TBox):
            return right_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return right_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')

    def is_same(self, other: Union[TBox, TNumber, floatrange, intrange, Time, Temporal]) -> bool:
        if isinstance(other, TBox):
            return same_tbox_tbox(tnumber_to_tbox(self._inner), other._inner)
        elif isinstance(other, TNumber):
            return same_tbox_tbox(tnumber_to_tbox(self._inner), tnumber_to_tbox(other._inner))
        elif isinstance(other, floatrange):
            return same_tbox_tbox(tnumber_to_tbox(self._inner), numspan_to_tbox(floatrange_to_floatspan(other)))
        elif isinstance(other, intrange):
            return same_tbox_tbox(tnumber_to_tbox(self._inner), numspan_to_tbox(intrange_to_intspan(other)))
        else:
            return super().is_same(other)

    def at(self, other: Union[intrange, floatrange, List[intrange], List[floatrange], TBox, Time]) -> TG:
        from ..boxes import TBox
        if isinstance(other, intrange):
            result = tnumber_at_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            result = tnumber_at_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, list) and isinstance(other[0], intrange):
            spans = [intrange_to_intspan(ir) for ir in other]
            spanset = spanset_make(spans, len(spans), True)
            result = tnumber_at_spanset(self._inner, spanset)
        elif isinstance(other, list) and isinstance(other[0], floatrange):
            spans = [floatrange_to_floatspan(fr) for fr in other]
            spanset = spanset_make(spans, len(spans), True)
            result = tnumber_at_spanset(self._inner, spanset)
        elif isinstance(other, TBox):
            result = tnumber_at_tbox(self._inner, other._inner)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[intrange, floatrange, List[intrange], List[floatrange], TBox, Time]) -> TG:
        if isinstance(other, intrange):
            result = tnumber_minus_span(self._inner, intrange_to_intspan(other))
        elif isinstance(other, floatrange):
            result = tnumber_minus_span(self._inner, floatrange_to_floatspan(other))
        elif isinstance(other, list) and isinstance(other[0], intrange):
            spans = [intrange_to_intspan(ir) for ir in other]
            spanset = spanset_make(spans, len(spans), True)
            result = tnumber_minus_spanset(self._inner, spanset)
        elif isinstance(other, list) and isinstance(other[0], floatrange):
            spans = [floatrange_to_floatspan(fr) for fr in other]
            spanset = spanset_make(spans, len(spans), True)
            result = tnumber_minus_spanset(self._inner, spanset)
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
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: A :class:`int`, :class:`float`, :class:`TNumber` or :class:`TBox` to compare to `self`.

        Returns:
            A :class:`float` with the nearest approach distance between `self` and `other`.

        MEOS Functions:
            nad_tfloat_float, nad_tfloat_tfloat, nad_tnumber_tbox
        """
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
