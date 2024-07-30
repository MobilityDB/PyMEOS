from __future__ import annotations

from abc import ABC
from typing import Optional, List, Union, TYPE_CHECKING, Set, overload, Type, TypeVar

from pymeos_cffi import *

from .tnumber import TNumber
from ..collections import *
from ..mixins import TSimplifiable, TTemporallyComparable
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet

if TYPE_CHECKING:
    from ..boxes import TBox
    from .tint import TInt
    from .tbool import TBool


Self = TypeVar("Self", bound="TFloat")


class TFloat(
    TNumber[float, "TFloat", "TFloatInst", "TFloatSeq", "TFloatSeqSet"],
    TSimplifiable,
    TTemporallyComparable,
    ABC,
):
    _mobilitydb_name = "tfloat"

    BaseClass = float
    _parse_function = tfloat_in

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(
        value: float,
        base: Temporal,
        interpolation: TInterpolation = TInterpolation.LINEAR,
    ) -> TFloat:
        """
        Returns a new temporal float with the value `value` and the temporal
        frame of `base`.

        Args:
            value: Value of the temporal float.
            base: Temporal object to get the temporal frame from.
            interpolation: Interpolation of the temporal float.

        Returns:
            A new :class:`TFloat` object.

        MEOS Functions:
            tfloat_from_base_temp
        """
        result = tfloat_from_base_temp(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(
        value: float, base: datetime, interpolation: None = None
    ) -> TFloatInst: ...

    @staticmethod
    @overload
    def from_base_time(
        value: float, base: TsTzSet, interpolation: None = None
    ) -> TFloatSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: float, base: TsTzSpan, interpolation: TInterpolation = None
    ) -> TFloatSeq: ...

    @staticmethod
    @overload
    def from_base_time(
        value: float, base: TsTzSpanSet, interpolation: TInterpolation = None
    ) -> TFloatSeqSet: ...

    @staticmethod
    def from_base_time(
        value: float, base: Time, interpolation: TInterpolation = None
    ) -> TFloat:
        """
        Returns a new temporal float with the value `value` and the temporal
        frame of `base`.

        Args:
            value: Value of the temporal float.
            base: Time object to get the temporal frame from.
            interpolation: Interpolation of the temporal float.

        Returns:
            A new temporal float.

        MEOS Functions:
            tfloatinst_make, tfloatseq_from_base_tstzset,
            tfloatseq_from_base_time, tfloatseqset_from_base_time
        """
        if isinstance(base, datetime):
            return TFloatInst(
                _inner=tfloatinst_make(value, datetime_to_timestamptz(base))
            )
        elif isinstance(base, TsTzSet):
            return TFloatSeq(_inner=tfloatseq_from_base_tstzset(value, base._inner))
        elif isinstance(base, TsTzSpan):
            return TFloatSeq(
                _inner=tfloatseq_from_base_tstzspan(value, base._inner, interpolation)
            )
        elif isinstance(base, TsTzSpanSet):
            return TFloatSeqSet(
                _inner=tfloatseqset_from_base_tstzspanset(
                    value, base._inner, interpolation
                )
            )
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: Type[Self], mfjson: str) -> Self:
        """
        Returns a temporal object from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal object from a MF-JSON string.

        MEOS Functions:
            tfloat_from_mfjson
        """

        result = tfloat_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Output ----------------------------------------
    def __str__(self, max_decimals: int = 15):
        """
        Returns a string representation of `self`.

        Returns:
            A string representation of `self`.

        MEOS Functions:
            tfloat_out
        """
        return tfloat_out(self._inner, max_decimals)

    def as_wkt(self, max_decimals: int = 15) -> str:
        """
        Returns a WKT representation of `self`.

        Args:
            max_decimals: The number of decimals to use.

        Returns:
            A WKT representation of `self`.

        MEOS Functions:
            tfloat_out
        """
        return tfloat_out(self._inner, max_decimals)

    # ------------------------- Conversions ----------------------------------
    def to_tint(self) -> TInt:
        """
        Returns a new temporal integer with the values of `self` floored.
        This operation can only be performed when the interpolation is stepwise
        or discrete.

        Returns:
            A new temporal integer.

        MEOS Functions:
            tfloat_to_tint

        Raises:
            ValueError: If the interpolation is linear.
        """
        from ..factory import _TemporalFactory

        if self.interpolation() == TInterpolation.LINEAR:
            raise ValueError(
                "Cannot convert a temporal float with linear "
                "interpolation to a temporal integer"
            )
        return _TemporalFactory.create_temporal(tfloat_to_tint(self._inner))

    def to_floatrange(self) -> FloatSpan:
        """
        Returns value span of `self`.

        Returns:
            An :class:`FloatSpan` with the value span of `self`.

        MEOS Functions:
            tnumber_to_span
        """
        return FloatSpan(_inner=tnumber_to_span(self._inner))

    # ------------------------- Accessors -------------------------------------
    def value_span(self) -> FloatSpan:
        """
        Returns the value span of `self`.

        Returns:
            An :class:`FloatSpan` with the value span of `self`.

        MEOS Functions:
            tnumber_to_span
        """
        return self.to_floatrange()

    def value_spans(self) -> FloatSpanSet:
        """
        Returns the value spans of `self` taking into account gaps.

        Returns:
            A :class:`FloatSpanSet` with the value spans of `self`.

        MEOS Functions:
            tnumber_valuespans
        """
        return FloatSpanSet(_inner=(tnumber_valuespans(self._inner)))

    def start_value(self) -> float:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`float` with the start value.

        MEOS Functions:
            tfloat_start_value
        """
        return tfloat_start_value(self._inner)

    def end_value(self) -> float:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`float` with the end value.

        MEOS Functions:
            tfloat_end_value
        """
        return tfloat_end_value(self._inner)

    def value_set(self) -> Set[float]:
        """
        Returns the set of values of `self`.
        Note that when the interpolation is linear, the set will contain only
        the waypoints.

        Returns:
            A :class:`set` with the values of `self`.

        MEOS Functions:
            tint_values
        """
        values, count = tfloat_values(self._inner)
        return {values[i] for i in range(count)}

    def min_value(self) -> float:
        """
        Returns the minimum value of the `self`.

        Returns:
            A :class:`float` with the minimum value.

        MEOS Functions:
            tfloat_min_value
        """
        return tfloat_min_value(self._inner)

    def max_value(self) -> float:
        """
        Returns the maximum value of the `self`.

        Returns:
            A :class:`float` with the maximum value.

        MEOS Functions:
            tfloat_max_value
        """
        return tfloat_max_value(self._inner)

    # ------------------------- Ever and Always Comparisons -------------------
    def always_less(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always less than `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always less than `value`,
            `False` otherwise.

        MEOS Functions:
            always_lt_tfloat_float, always_lt_temporal_temporal
        """
        if isinstance(value, float):
            return always_lt_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_lt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_less_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always less than or equal to
        `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            always_le_tfloat_float, always_le_temporal_temporal
        """
        if isinstance(value, float):
            return always_le_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_le_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tfloat_float, always_eq_temporal_temporal
        """
        if isinstance(value, float):
            return always_eq_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tfloat_float, always_ne_temporal_temporal
        """
        if isinstance(value, float):
            return always_ne_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_greater_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always greater than or equal
        to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            always_ge_tfloat_float, always_ge_temporal_temporal
        """
        if isinstance(value, float):
            return always_ge_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_ge_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_greater(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are always greater than `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are always greater than `value`,
            `False` otherwise.

        MEOS Functions:
            always_gt_tfloat_float, always_gt_temporal_temporal
        """
        if isinstance(value, float):
            return always_gt_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return always_gt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_less(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever less than `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever less than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_lt_tfloat_float, ever_lt_temporal_temporal
        """
        if isinstance(value, float):
            return ever_lt_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_lt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_less_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever less than or equal to
        `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_le_tfloat_float, ever_le_temporal_temporal
        """
        if isinstance(value, float):
            return ever_le_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_le_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False`
            otherwise.

        MEOS Functions:
            ever_eq_tfloat_float, ever_eq_temporal_temporal
        """
        if isinstance(value, float):
            return ever_eq_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tfloat_float, ever_ne_temporal_temporal
        """
        if isinstance(value, float):
            return ever_ne_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_greater_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever greater than or equal to
        `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_ge_tfloat_float, ever_ge_temporal_temporal
        """
        if isinstance(value, float):
            return ever_ge_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_ge_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_greater(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are ever greater than `value`.

        Args:
            value: :class:`float` to compare.

        Returns:
            `True` if the values of `self` are ever greater than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_gt_tfloat_float, ever_gt_temporal_temporal
        """
        if isinstance(value, float):
            return ever_gt_tfloat_float(self._inner, value) > 0
        elif isinstance(value, TFloat):
            return ever_gt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_less(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never less than `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never less than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_lt_tfloat_float, ever_lt_temporal_temporal
        """
        return not self.ever_less(value)

    def never_less_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never less than or equal to
        `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_le_tfloat_float, ever_le_temporal_temporal
        """
        return not self.ever_less_or_equal(value)

    def never_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_eq_tfloat_float, ever_eq_temporal_temporal
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tfloat_float, ever_ne_temporal_temporal
        """
        return not self.ever_not_equal(value)

    def never_greater_or_equal(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never greater than or equal to
        `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_ge_tfloat_float, ever_ge_temporal_temporal
        """
        return not self.ever_greater_or_equal(value)

    def never_greater(self, value: Union[float, TFloat]) -> bool:
        """
        Returns whether the values of `self` are never greater than `value`.

        Args:
            value: :class:`float` value to compare.

        Returns:
            `True` if the values of `self` are never greater than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_gt_tfloat_float, ever_gt_temporal_temporal
        """
        return not self.ever_greater(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tfloat_float, teq_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = teq_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_tfloat_float, tne_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tne_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_less(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal less than relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less than relation.

        MEOS Functions:
            tlt_tfloat_float, tlt_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tlt_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal less or equal relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less or equal
            relation.

        MEOS Functions:
            tle_tfloat_float, tle_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tle_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal greater or equal relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater or equal
            relation.

        MEOS Functions:
            tge_tfloat_float, tge_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tge_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[int, float, TFloat]) -> TBool:
        """
        Returns the temporal greater than relation between `self` and `other`.

        Args:
            other: An :class:`int`, :class:`float` or temporal object to
            compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater than
            relation.

        MEOS Functions:
            tgt_tfloat_float, tgt_temporal_temporal
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tgt_tfloat_float(self._inner, float(other))
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(
        self,
        other: Union[
            float,
            int,
            FloatSet,
            IntSet,
            FloatSpan,
            IntSpan,
            FloatSpanSet,
            IntSpanSet,
            TBox,
            Time,
        ],
    ) -> TFloat:
        """
        Returns a new temporal float with the values of `self` restricted to
        the value or time `other`.

        Args:
            other: Value or time to restrict to.

        Returns:
            A new temporal float.

        MEOS Functions:
            tfloat_at_value, temporal_at_values, tnumber_at_span, tnumber_at_spanset,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tfloat_at_value(self._inner, float(other))
        elif isinstance(other, IntSet):
            return super().at(other.to_floatset())
        elif isinstance(other, IntSpan):
            return super().at(other.to_floatspan())
        elif isinstance(other, IntSpanSet):
            return super().at(other.to_floatspanset())
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self,
        other: Union[
            float,
            int,
            FloatSet,
            IntSet,
            FloatSpan,
            IntSpan,
            FloatSpanSet,
            IntSpanSet,
            TBox,
            Time,
        ],
    ) -> Temporal:
        """
        Returns a new temporal float with the values of `self` restricted to
        the complement of the time or value `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal float.

        MEOS Functions:
            tfloat_minus_value, temporal_minus_values, tnumber_minus_span, tnumber_minus_spanset,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tfloat_minus_value(self._inner, float(other))
        elif isinstance(other, IntSet):
            return super().minus(other.to_floatset())
        elif isinstance(other, IntSpan):
            return super().minus(other.to_floatspan())
        elif isinstance(other, IntSpanSet):
            return super().minus(other.to_floatspanset())
        else:
            return super().minus(other)
        return Temporal._factory(result)

    def value_at_timestamp(self, timestamp) -> float:
        """
        Returns the value that `self` takes at a certain moment.

        Args:
            timestamp: The moment to get the value.

        Returns:
            A class:`float` with the value of `self` at `timestamp`.

        MEOS Functions:
            tfloat_value_at_timestamp
        """
        return tfloat_value_at_timestamptz(
            self._inner, datetime_to_timestamptz(timestamp), True
        )

    def derivative(self) -> TFloat:
        """
        Returns the derivative of `self`.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tfloat_derivative
        """
        return Temporal._factory(tfloat_derivative(self._inner))

    # ------------------------- Transformations ----------------------------------
    def to_degrees(self, normalize: bool = True) -> TFloat:
        """
        Returns a copy of `self` converted from radians to degrees.

        Args:
            normalize: If True, the result will be normalized to the range
            [0, 360).

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tfloat_degrees
        """
        return Temporal._factory(tfloat_degrees(self._inner, normalize))

    def to_radians(self) -> TFloat:
        """
        Returns a copy of `self` converted from degrees to radians.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tfloat_radians
        """
        return Temporal._factory(tfloat_radians(self._inner))

    def round(self, max_decimals: int = 0) -> TFloat:
        """
        Returns `self` rounded to the given number of decimal digits.

        Args:
            max_decimals: Maximum number of decimal digits.

        Returns:
            A new :class:`TFloat` instance.

        MEOS Functions:
            tfloat_round
        """
        return Temporal._factory(tfloat_round(self._inner, max_decimals))

    # ------------------------- Split Operations ------------------------------
    def value_split(self, size: float, start: Optional[float] = 0) -> List[Temporal]:
        """
        Splits `self` into fragments with respect to value buckets

        Args:
            start: Start value of the first value bucket.
            size: Size of the value buckets.

        Returns:
            A list of temporal floats.

        MEOS Functions:
            tfloat_value_split
        """
        fragments, _, count = tfloat_value_split(self._inner, size, start)
        return [Temporal._factory(fragments[i]) for i in range(count)]

    def value_time_split(
        self,
        value_size: float,
        duration: Union[str, timedelta],
        value_start: Optional[float] = 0.0,
        time_start: Optional[Union[str, datetime]] = None,
    ) -> List[Temporal]:
        """
        Splits `self` into fragments with respect to value and tstzspan buckets.

        Args:
            value_size: Size of the value buckets.
            duration: Duration of the tstzspan buckets.
            value_start: Start value of the first value bucket. If None, the
                start value used by default is 0
            time_start: Start time of the first tstzspan bucket. If None, the
                start time used by default is Monday, January 3, 2000.

        Returns:
            A list of temporal floats.

        MEOS Functions:
            tfloat_value_time_split
        """
        if time_start is None:
            st = pg_timestamptz_in("2000-01-03", -1)
        else:
            st = (
                datetime_to_timestamptz(time_start)
                if isinstance(time_start, datetime)
                else pg_timestamptz_in(time_start, -1)
            )
        dt = (
            timedelta_to_interval(duration)
            if isinstance(duration, timedelta)
            else pg_interval_in(duration, -1)
        )
        fragments, _, _, count = tfloat_value_time_split(
            self._inner, value_size, dt, value_start, st
        )
        return [Temporal._factory(fragments[i]) for i in range(count)]

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TFloat` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value.startswith("Interp=Stepwise;"):
            value1 = value.replace("Interp=Stepwise;", "")
            if value1[0] == "{":
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        elif value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TFloatInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TFloatSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        raise Exception("ERROR: Could not parse temporal float value")


class TFloatInst(
    TInstant[float, "TFloat", "TFloatInst", "TFloatSeq", "TFloatSeqSet"], TFloat
):
    """
    Class for representing temporal floats at a single instant.
    """

    _make_function = tfloatinst_make
    _cast_function = float

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        value: Optional[Union[str, float]] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TFloatSeq(
    TSequence[float, "TFloat", "TFloatInst", "TFloatSeq", "TFloatSeqSet"], TFloat
):
    """
    Class for representing temporal floats over a tstzspan of time.
    """

    ComponentClass = TFloatInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TFloatInst]]] = None,
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.LINEAR,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            instant_list=instant_list,
            lower_inc=lower_inc,
            upper_inc=upper_inc,
            interpolation=interpolation,
            normalize=normalize,
            _inner=_inner,
        )


class TFloatSeqSet(
    TSequenceSet[float, "TFloat", "TFloatInst", "TFloatSeq", "TFloatSeqSet"], TFloat
):
    """
    Class for representing temporal floats over a tstzspan of time with gaps.
    """

    ComponentClass = TFloatSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TFloatSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
