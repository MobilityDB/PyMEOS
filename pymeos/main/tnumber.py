from __future__ import annotations

from abc import ABC
from typing import Union, TYPE_CHECKING, TypeVar

from pymeos_cffi import *

from ..collections import IntSet, FloatSet
from ..temporal import Temporal

if TYPE_CHECKING:
    from ..boxes import Box, TBox
    from ..collections import Time, IntSpan, IntSpanSet, FloatSpan, FloatSpanSet
    from .tint import TInt
    from .tfloat import TFloat

TBase = TypeVar("TBase", int, float)
TG = TypeVar("TG", "TNumber[int]", "TNumber[float]")
TI = TypeVar("TI", "TInstant[int]", "TInstant[float]")
TS = TypeVar("TS", "TSequence[int]", "TSequence[float]")
TSS = TypeVar("TSS", "TSequenceSet[int]", "TSequenceSet[float]")
Self = TypeVar("Self", bound="TNumber[Any]")


class TNumber(Temporal[TBase, TG, TI, TS, TSS], ABC):
    # ------------------------- Accessors -------------------------------------
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

    # ------------------------- Transformations -------------------------------
    def shift_value(self: Self, delta: Union[int, float]) -> Self:
        """
        Returns a new :class:`TNumber` with the value dimension shifted by
        ``delta``.

        Args:
            delta: value to shift

        MEOS Functions:
            tint_shift_value, tfloat_shift_value
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt):
            shifted = tint_shift_value(self._inner, int(delta))
        elif isinstance(self, TFloat):
            shifted = tfloat_shift_value(self._inner, float(delta))
        else:
            raise TypeError(f"Operation not supported with type {self.__class__}")
        return Temporal._factory(shifted)

    def scale_value(self: Self, width: Union[int, float]) -> Self:
        """
        Returns a new :class:`TNumber` scaled so the value dimension has
        width ``width``.

        Args:
            width: value representing the width of the new temporal number

        MEOS Functions:
            tint_scale_value, tfloat_scale_value
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt):
            scaled = tint_scale_value(self._inner, int(width))
        elif isinstance(self, TFloat):
            scaled = tfloat_scale_value(self._inner, float(width))
        else:
            raise TypeError(f"Operation not supported with type {self.__class__}")
        return Temporal._factory(scaled)

    def shift_scale_value(
        self: Self, shift: Union[int, float] = None, width: Union[int, float] = None
    ) -> Self:
        """
        Returns a new :class:`TNumber` with the value dimension shifted by
        ``shift`` and scaled so the value dimension has width ``width``.

        Args:
            shift: value to shift
            width: value representing the width of the new temporal number

        MEOS Functions:
            tint_shift_scale_value, tfloat_shift_scale_value
        """
        from .tint import TInt
        from .tfloat import TFloat

        assert (
            shift is not None or width is not None
        ), "shift and width must not be both None"

        if isinstance(self, TInt):
            scaled = tint_shift_scale_value(
                self._inner,
                int(shift) if shift else None,
                int(width) if width else None,
            )
        elif isinstance(self, TFloat):
            scaled = tfloat_shift_scale_value(
                self._inner,
                float(shift) if shift else None,
                float(width) if width else None,
            )
        else:
            raise TypeError(f"Operation not supported with type {self.__class__}")
        return Temporal._factory(scaled)

    # ------------------------- Restrictions ----------------------------------
    def at(
        self,
        other: Union[
            IntSet, FloatSet, IntSpan, FloatSpan, IntSpanSet, FloatSpanSet, TBox, Time
        ],
    ) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to
        the value or time `other`.

        Args:
            other: A time or value object to restrict the values of `self` to.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_at_values, tnumber_at_span, tnumber_at_spanset, tnumber_at_tbox,
            temporal_at_timestamp, temporal_at_tstzset,
            temporal_at_tstzspan, temporal_at_tstzspanset
        """
        from ..boxes import TBox
        from ..collections import (
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
        )

        if isinstance(other, IntSet) or isinstance(other, FloatSet):
            result = temporal_at_values(self._inner, other._inner)
        elif isinstance(other, IntSpan) or isinstance(other, FloatSpan):
            result = tnumber_at_span(self._inner, other._inner)
        elif isinstance(other, IntSpanSet) or isinstance(other, FloatSpanSet):
            result = tnumber_at_spanset(self._inner, other._inner)
        elif isinstance(other, TBox):
            result = tnumber_at_tbox(self._inner, other._inner)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self,
        other: Union[
            IntSet, FloatSet, IntSpan, FloatSpan, IntSpanSet, FloatSpanSet, TBox, Time
        ],
    ) -> TG:
        """
        Returns a new temporal object with the values of `self` restricted to
        the complement of the value or time `other`.

        Args:
            other: A time or value object to restrict the values of `self` to
            the complement of.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            temporal_minus_values, tnumber_minus_span, tnumber_minus_spanset, tnumber_minus_tbox,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        from ..boxes import TBox
        from ..collections import (
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
        )

        if isinstance(other, IntSet) or isinstance(other, FloatSet):
            result = temporal_minus_values(self._inner, other._inner)
        elif isinstance(other, IntSpan) or isinstance(other, FloatSpan):
            result = tnumber_minus_span(self._inner, other._inner)
        elif isinstance(other, IntSpanSet) or isinstance(other, FloatSpanSet):
            result = tnumber_minus_spanset(self._inner, other._inner)
        elif isinstance(other, TBox):
            result = tnumber_minus_tbox(self._inner, other._inner)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Position Operations ---------------------------
    def is_left(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is left to the bounding box
        of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if left, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_before`
        """
        return self.bounding_box().is_left(other)

    def is_over_or_left(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or left to the
        bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or left, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_left(other)

    def is_right(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is right to the bounding
        box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if right, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_after`
        """
        return self.bounding_box().is_right(other)

    def is_over_or_right(self, other: Union[Temporal, Box]) -> bool:
        """
        Returns whether the bounding box of `self` is over or right to the
        bounding box of `other`.

        Args:
            other: A box or a temporal object to compare to `self`.

        Returns:
            True if over or right, False otherwise.

        See Also:
            :meth:`TsTzSpan.is_over_or_before`
        """
        return self.bounding_box().is_over_or_right(other)

    # ------------------------- Mathematical Operations -------------------------
    def add(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to add
            to `self`.

        Returns:
            A new temporal object of the same subtype as `self`.
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = add_tint_int(self._inner, other)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = add_tfloat_float(self._inner, float(other))
        elif isinstance(other, TNumber):
            result = add_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
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
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = add_int_tint(other, self._inner)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = add_float_tfloat(float(other), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def sub(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` minus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to
            subtract from `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            sub_tint_int, sub_tfloat_float, sub_tnumber_tnumber
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = sub_tint_int(self._inner, other)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = sub_tfloat_float(self._inner, float(other))
        elif isinstance(other, TNumber):
            result = sub_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
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
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = sub_int_tint(other, self._inner)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = sub_float_tfloat(float(other), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def mul(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` multiplied by
        `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to
            multiply `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_tint_int, mult_tfloat_float, mult_tnumber_tnumber
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = mult_tint_int(self._inner, other)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = mult_tfloat_float(self._inner, float(other))
        elif isinstance(other, TNumber):
            result = mult_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def rmul(self, other: Union[int, float]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` multiplied by
        `other`.

        Args:
            other: A :class:`int` or :class:`float` to multiply by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_int_tint, mult_float_tfloat
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = mult_int_tint(other, self._inner)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = mult_float_tfloat(float(other), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def div(self, other: Union[int, float, TNumber]) -> TNumber:
        """
        Returns a new temporal object with the values of `self` divided by
        `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to divide
            `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_tint_int, div_tfloat_float, div_tnumber_tnumber
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = div_tint_int(self._inner, other)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = div_tfloat_float(self._inner, float(other))
        elif isinstance(other, TNumber):
            result = div_tnumber_tnumber(self._inner, other._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def rdiv(self, other: Union[int, float]) -> TNumber:
        """
        Returns a new temporal object with the values of `other` divided by
        `self`.

        Args:
            other: A :class:`int` or :class:`float` to divide by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_int_tint, div_float_tfloat
        """
        from .tint import TInt
        from .tfloat import TFloat

        if isinstance(self, TInt) and isinstance(other, int):
            result = div_int_tint(other, self._inner)
        elif isinstance(self, TFloat) and isinstance(other, (int, float)):
            result = div_float_tfloat(float(other), self._inner)
        else:
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def __add__(self, other):
        """
        Returns a new temporal object with the values of `self` plus `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to add to
            `self`.

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
            other: A :class:`int`, :class:`float` or :class:`TNumber` to
            subtract from `self`.

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
        Returns a new temporal object with the values of `self` multiplied by
        `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to
            multiply `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            mult_tint_int, mult_tfloat_float, mult_tnumber_tnumber
        """
        return self.mul(other)

    def __rmul__(self, other):
        """
        Returns a new temporal object with the values of `self` multiplied
        by `other`.

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
        Returns a new temporal object with the values of `self` divided by
        `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to divide
            `self` by.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_tint_int, div_tfloat_float, div_tnumber_tnumber
        """
        return self.div(other)

    def __rtruediv__(self, other):
        """
        Returns a new temporal object with the values of `other` divided by
        `self`.

        Args:
            other: A :class:`int` or :class:`float` to divide by `self`.

        Returns:
            A new temporal object of the same subtype as `self`.

        MEOS Functions:
            div_int_tint, div_float_tfloat
        """
        return self.rdiv(other)

    def abs(self) -> TNumber:
        """
        Returns the absolute value of `self`.

        Returns:
            A new :class:`TNumber` instance.

        MEOS Functions:
            tnumber_abs
        """
        from ..factory import _TemporalFactory

        return _TemporalFactory.create_temporal(tnumber_abs(self._inner))

    def delta_value(self) -> TNumber:
        """
        Returns the value difference between consecutive instants of `self`.

        Returns:
            A new :class:`TNumber` instance.

        MEOS Functions:
            tnumber_delta_value
        """
        from ..factory import _TemporalFactory

        return _TemporalFactory.create_temporal(tnumber_delta_value(self._inner))

    # ------------------------- Distance Operations --------------------------
    def distance(self, other: Union[int, float, TNumber]) -> TFloat:
        """
        Returns the temporal distance between `self` and `other`.

        Args:
            other: A :class:`int`, :class:`float` or :class:`TNumber` to
            compare to `self`.

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
            raise TypeError(f"Operation not supported with type {other.__class__}")
        return Temporal._factory(result)

    def nearest_approach_distance(
        self, other: Union[int, float, TNumber, TBox]
    ) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: A :class:`int`, :class:`float`, :class:`TNumber` or
            :class:`TBox` to compare to `self`.

        Returns:
            A :class:`float` with the nearest approach distance between `self`
            and `other`.

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
            raise TypeError(f"Operation not supported with type {other.__class__}")
