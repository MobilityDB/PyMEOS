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

    def at(self, other: Union[intrange, floatrange, List[intrange], List[floatrange], TBox, Time]) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to the value or time `other`.

        Args:
            other: A time or value object to restrict the values of `self` to.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            tnumber_at_span, tnumber_at_spanset, tnumber_at_tbox,
            temporal_at_timestamp, temporal_at_timestampset, temporal_at_period, temporal_at_periodset
        """
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
        """
        Returns a new temporal object with the values of `self` restricted to the complement of the value or time
         `other`.

        Args:
            other: A time or value object to restrict the values of `self` to the complement of.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            tnumber_minus_span, tnumber_minus_spanset, tnumber_minus_tbox,
            temporal_minus_timestamp, temporal_minus_timestampset, temporal_minus_period, temporal_minus_periodset
        """
        from ..boxes import TBox
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
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to compare to `self`.

        Returns:
            A :class:`TFloat` with the distance between `self` and `other`.

        MEOS Functions:
            distance_tfloat_float, distance_tnumber_tnumber
        """
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
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to add to `self`.

        Returns:
            A new temporal object of the same subtype as `self`.
        """
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
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int` or :class:`float` to add to `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            add_int_tint, add_float_tfloat
        """
        if isinstance(other, int):
            result = add_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = add_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def sub(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` minus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to subtract from `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            sub_tint_int, sub_tfloat_float, sub_tnumber_tnumber
        """
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
        """
        Returns a new temporal object with the values of `other` minus `self`.

        Args:
            other: A :class:`int` or :class:`float` to subtract `self` to.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            sub_int_tint, sub_float_tfloat
        """
        if isinstance(other, int):
            result = sub_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = sub_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def mul(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` multiplied by `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to multiply `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_tint_int, mult_tfloat_float, mult_tnumber_tnumber
        """
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
        """
        Returns a new temporal object with the values of `self` multiplied by `other`.

        Args:
            other: A :class:`int` or :class:`float` to multiply by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_int_tint, mult_float_tfloat
        """
        if isinstance(other, int):
            result = mult_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = mult_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def div(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` divided by `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to divide `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_tint_int, div_tfloat_float, div_tnumber_tnumber
        """
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
        """
        Returns a new temporal object with the values of `other` divided by `self`.

        Args:
            other: A :class:`int` or :class:`float` to divide by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_int_tint, div_float_tfloat
        """
        if isinstance(other, int):
            result = div_int_tint(other, self._inner)
        elif isinstance(other, float):
            result = div_float_tfloat(other, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return Temporal._factory(result)

    def integral(self) -> float:
        """
        Returns the integral of `self`.

        Returns:
            The integral of `self`.

        MEOS Function:
            tnumber_integral
        """
        return tnumber_integral(self._inner)

    def time_weighted_average(self) -> float:
        """
        Returns the time weighted average of `self`.

        Returns:
            The time weighted average of `self`.

        MEOS Function:
            tnumber_twavg
        """
        return tnumber_twavg(self._inner)

    def __add__(self, other):
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to add to `self`.

        Returns:
            A new temporal object of the same subtype as `self`.
        """
        return self.add(other)

    def __radd__(self, other):
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int` or :class:`float` to add to `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            add_int_tint, add_float_tfloat
        """
        return self.radd(other)

    def __sub__(self, other):
        """
        Returns a new temporal object with the values of `self` minus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to subtract from `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            sub_tint_int, sub_tfloat_float, sub_tnumber_tnumber
        """
        return self.sub(other)

    def __rsub__(self, other):
        """
        Returns a new temporal object with the values of `other` minus `self`.

        Args:
            other: A :class:`int` or :class:`float` to subtract `self` to.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            sub_int_tint, sub_float_tfloat
        """
        return self.rsub(other)

    def __mul__(self, other):
        """
        Returns a new temporal object with the values of `self` multiplied by `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to multiply `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_tint_int, mult_tfloat_float, mult_tnumber_tnumber
        """
        return self.mul(other)

    def __rmul__(self, other):
        """
        Returns a new temporal object with the values of `self` multiplied by `other`.

        Args:
            other: A :class:`int` or :class:`float` to multiply by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_int_tint, mult_float_tfloat
        """
        return self.rmul(other)

    def __truediv__(self, other):
        """
        Returns a new temporal object with the values of `self` divided by `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to divide `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_tint_int, div_tfloat_float, div_tnumber_tnumber
        """
        return self.div(other)

    def __rtruediv__(self, other):
        """
        Returns a new temporal object with the values of `other` divided by `self`.

        Args:
            other: A :class:`int` or :class:`float` to divide by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_int_tint, div_float_tfloat
        """
        return self.rdiv(other)
