from __future__ import annotations

from abc import ABC
from typing import Optional, Union, List, TYPE_CHECKING, Set, overload, TypeVar, Type

from pymeos_cffi import *

from .tnumber import TNumber
from ..collections import *
from ..mixins import TTemporallyComparable
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet

if TYPE_CHECKING:
    from ..boxes import TBox
    from .tfloat import TFloat
    from .tbool import TBool


Self = TypeVar("Self", bound="TInt")


class TInt(
    TNumber[int, "TInt", "TIntInst", "TIntSeq", "TIntSeqSet"],
    TTemporallyComparable,
    ABC,
):
    _mobilitydb_name = "tint"

    BaseClass = int
    _parse_function = tint_in

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: int, base: Temporal) -> TInt:
        """
        Returns a new temporal integer with the value `value` and the temporal
        frame of `base`.

        Args:
            value: Value of the temporal integer.
            base: Temporal object to get the temporal frame from.

        Returns:
            A new :class:`TInt` object.

        MEOS Functions:
            tint_from_base_temp
        """
        result = tint_from_base_temp(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: int, base: datetime) -> TIntInst: ...

    @staticmethod
    @overload
    def from_base_time(value: int, base: Union[TsTzSet, TsTzSpan]) -> TIntSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: int, base: TsTzSpanSet) -> TIntSeqSet: ...

    @staticmethod
    def from_base_time(value: int, base: Time) -> TInt:
        """
        Returns a new temporal int with the value `value` and the temporal
        frame of `base`.

        Args:
            value: Value of the temporal int.
            base: Time object to get the temporal frame from.

        Returns:
            A new temporal int.

        MEOS Functions:
            tintinst_make, tintseq_from_base_tstzset,
            tintseq_from_base_tstzspan, tintseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TIntInst(_inner=tintinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TIntSeq(_inner=tintseq_from_base_tstzset(value, base._inner))
        elif isinstance(base, TsTzSpan):
            return TIntSeq(_inner=tintseq_from_base_tstzspan(value, base._inner))
        elif isinstance(base, TsTzSpanSet):
            return TIntSeqSet(
                _inner=tintseqset_from_base_tstzspanset(value, base._inner)
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
            tint_from_mfjson
        """

        result = tint_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns a string representation of `self`.

        Returns:
            A string representation of `self`.

        MEOS Functions:
            tint_out
        """
        return tint_out(self._inner)

    def as_wkt(self):
        """
        Returns a WKT representation of `self`.

        Returns:
            A WKT representation of `self`.

        MEOS Functions:
            tint_as_wkt
        """
        return tint_out(self._inner)

    # ------------------------- Conversions ----------------------------------
    def to_tfloat(self) -> TFloat:
        """
        Returns a new temporal float with the values of `self`.

        Returns:
            A new temporal float.

        MEOS Functions:
            tint_to_tfloat
        """
        from ..factory import _TemporalFactory

        return _TemporalFactory.create_temporal(tint_to_tfloat(self._inner))

    def to_intspan(self) -> IntSpan:
        """
        Returns value span of `self`.

        Returns:
            An :class:`IntSpan` with the value span of `self`.

        MEOS Functions:
            tnumber_to_span
        """
        return IntSpan(_inner=tnumber_to_span(self._inner))

    # ------------------------- Accessors -------------------------------------
    def value_span(self) -> IntSpan:
        """
        Returns the value span of `self`.

        Returns:
            An :class:`IntSpan` with the value span of `self`.

        MEOS Functions:
            tnumber_to_span
        """
        return self.to_intspan()

    def value_spans(self) -> IntSpanSet:
        """
        Returns the value spans of `self` taking into account gaps.

        Returns:
            An :class:`IntSpanSet` with the value spans of `self`.

        MEOS Functions:
            tnumber_valuespans
        """
        return IntSpanSet(_inner=tnumber_valuespans(self._inner))

    def start_value(self) -> int:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`int` with the start value.

        MEOS Functions:
            tint_start_value
        """
        return tint_start_value(self._inner)

    def end_value(self) -> int:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`int` with the end value.

        MEOS Functions:
            tint_end_value
        """
        return tint_end_value(self._inner)

    def value_set(self) -> Set[int]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` with the values of `self`.

        MEOS Functions:
            tint_values
        """
        values, count = tint_values(self._inner)
        return {values[i] for i in range(count)}

    def min_value(self) -> int:
        """
        Returns the minimum value of the temporal int.

        Returns:
            A :class:`int` with the minimum value.

        MEOS Functions:
            tint_min_value
        """
        return tint_min_value(self._inner)

    def max_value(self) -> int:
        """
        Returns the maximum value of the temporal int.

        Returns:
            A :class:`int` with the maximum value.

        MEOS Functions:
            tint_max_value
        """
        return tint_max_value(self._inner)

    def value_at_timestamp(self, timestamp) -> int:
        """
        Returns the value that `self` takes at a certain moment.

        Args:
            timestamp: The moment to get the value.

        Returns:
            An :class:`int` with the value of `self` at `timestamp`.

        MEOS Functions:
            tint_value_at_timestamp
        """
        return tint_value_at_timestamptz(
            self._inner, datetime_to_timestamptz(timestamp), True
        )

    # ------------------------- Ever and Always Comparisons -------------------
    def always_less(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always less than `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always less than `value`,
            `False` otherwise.

        MEOS Functions:
            always_lt_tint_int, always_lt_temporal_temporal
        """
        if isinstance(value, int):
            return always_lt_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_lt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_less_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always less than or equal to
        `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            always_le_tint_int, always_le_temporal_temporal
        """
        if isinstance(value, int):
            return always_le_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_le_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_eq_tint_int, always_eq_temporal_temporal
        """
        if isinstance(value, int):
            return always_eq_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_not_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            always_ne_tint_int, always_ne_temporal_temporal
        """
        if isinstance(value, int):
            return always_ne_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_greater_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always greater than or equal
        to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            always_ge_tint_int, always_ge_temporal_temporal
        """
        if isinstance(value, int):
            return always_ge_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_ge_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def always_greater(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are always greater than `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are always greater than `value`,
            `False` otherwise.

        MEOS Functions:
            always_gt_tint_int, always_gt_temporal_temporal
        """
        if isinstance(value, int):
            return always_gt_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return always_gt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_less(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever less than `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever less than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_lt_tint_int, ever_lt_temporal_temporal
        """
        if isinstance(value, int):
            return ever_lt_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_lt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_less_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever less than or equal to
        `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_le_tint_int, ever_le_temporal_temporal
        """
        if isinstance(value, int):
            return ever_le_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_le_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_eq_tint_int, ever_eq_temporal_temporal
        """
        if isinstance(value, int):
            return ever_eq_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_not_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tint_int, ever_ne_temporal_temporal
        """
        if isinstance(value, int):
            return ever_ne_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_ne_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_greater_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever greater than or equal to
        `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_ge_tint_int, ever_ge_temporal_temporal
        """
        if isinstance(value, int):
            return ever_ge_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_ge_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_greater(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are ever greater than `value`.

        Args:
            value: :class:`int` to compare.

        Returns:
            `True` if the values of `self` are ever greater than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_gt_tint_int, ever_gt_temporal_temporal
        """
        if isinstance(value, int):
            return ever_gt_tint_int(self._inner, value) > 0
        elif isinstance(value, TInt):
            return ever_gt_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_less(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never less than `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never less than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_lt_tint_int, ever_lt_temporal_temporal
        """
        return not self.ever_less(value)

    def never_less_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never less than or equal to
        `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never less than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_le_tint_int, ever_le_temporal_temporal
        """
        return not self.ever_less_or_equal(value)

    def never_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_eq_tint_int, ever_eq_temporal_temporal
        """
        return not self.ever_equal(value)

    def never_not_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`,
            `False` otherwise.

        MEOS Functions:
            ever_ne_tint_int, ever_ne_temporal_temporal
        """
        return not self.ever_not_equal(value)

    def never_greater_or_equal(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never greater than or equal to
        `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never greater than or equal to
            `value`, `False` otherwise.

        MEOS Functions:
            ever_ge_tint_int, ever_ge_temporal_temporal
        """
        return not self.ever_greater_or_equal(value)

    def never_greater(self, value: Union[int, TInt]) -> bool:
        """
        Returns whether the values of `self` are never greater than `value`.

        Args:
            value: :class:`int` value to compare.

        Returns:
            `True` if the values of `self` are never greater than `value`,
            `False` otherwise.

        MEOS Functions:
            ever_gt_tint_int, ever_gt_temporal_temporal
        """
        return not self.ever_greater(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tint_int, teq_temporal_temporal
        """
        if isinstance(other, int):
            result = teq_tint_int(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_tint_int, tne_temporal_temporal
        """
        if isinstance(other, int):
            result = tne_tint_int(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_less(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal less than relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less than relation.

        MEOS Functions:
            tlt_tint_int, tlt_temporal_temporal
        """
        if isinstance(other, int):
            result = tlt_tint_int(self._inner, other)
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal less or equal relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less or equal
            relation.

        MEOS Functions:
            tle_tint_int, tle_temporal_temporal
        """
        if isinstance(other, int):
            result = tle_tint_int(self._inner, other)
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal greater or equal relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater or equal
            relation.

        MEOS Functions:
            tge_tint_int, tge_temporal_temporal
        """
        if isinstance(other, int):
            result = tge_tint_int(self._inner, other)
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[int, TInt]) -> TBool:
        """
        Returns the temporal greater than relation between `self` and `other`.

        Args:
            other: A :class:`int` or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater than
            relation.

        MEOS Functions:
            tgt_tint_int, tgt_temporal_temporal
        """
        if isinstance(other, int):
            result = tgt_tint_int(self._inner, other)
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(
        self,
        other: Union[
            int,
            float,
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
            TBox,
            Time,
        ],
    ) -> TInt:
        """
        Returns a new temporal int with th  e values of `self` restricted to
        the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal int.

        MEOS Functions:
            tint_at_value, temporal_at_values, tnumber_at_span, tnumber_at_spanset,
            temporal_at_timestamp, temporal_at_tstzset, temporal_at_tstzspan,
            temporal_at_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tint_at_value(self._inner, int(other))
        elif isinstance(other, FloatSet):
            return super().at(other.to_intset())
        elif isinstance(other, FloatSpan):
            return super().at(other.to_intspan())
        elif isinstance(other, FloatSpanSet):
            return super().at(other.to_intspanset())
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(
        self,
        other: Union[
            int,
            float,
            IntSet,
            FloatSet,
            IntSpan,
            FloatSpan,
            IntSpanSet,
            FloatSpanSet,
            TBox,
            Time,
        ],
    ) -> TInt:
        """
        Returns a new temporal int with the values of `self` restricted to the
        complement of the time or value `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal int.

        MEOS Functions:
            tint_minus_value, temporal_minus_values, tnumber_minus_span, tnumber_minus_spanset,
            temporal_minus_timestamp, temporal_minus_tstzset,
            temporal_minus_tstzspan, temporal_minus_tstzspanset
        """
        if isinstance(other, int) or isinstance(other, float):
            result = tint_minus_value(self._inner, int(other))
        elif isinstance(other, FloatSet):
            return super().minus(other.to_intset())
        elif isinstance(other, FloatSpan):
            return super().minus(other.to_intspan())
        elif isinstance(other, FloatSpanSet):
            return super().minus(other.to_intspanset())
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Distance --------------------------------------
    def nearest_approach_distance(
        self, other: Union[int, float, TNumber, TBox]
    ) -> float:
        """
        Returns the nearest approach distance between `self` and `other`.

        Args:
            other: A :class:`int`, :class:`float`, :class:`TNumber` or :class:`TBox` to compare to `self`.

        Returns:
            A :class:`float` with the nearest approach distance between `self`
            and `other`.

        MEOS Functions:
            nad_tint_int, nad_tint_tint, nad_tfloat_float, nad_tfloat_tfloat,
            nad_tnumber_tbox
        """
        if isinstance(other, int):
            return nad_tint_int(self._inner, other)
        elif isinstance(other, TInt):
            return nad_tint_tint(self._inner, other._inner)
        else:
            return super().nearest_approach_distance(other)

    # ------------------------- Split Operations ------------------------------
    def value_split(self, size: int, start: Optional[int] = 0) -> List[TInt]:
        """
        Splits `self` into fragments with respect to value buckets

        Args:
            start: Start value of the first value bucket.
            size: Size of the value buckets.

        Returns:
            A list of temporal ints.

        MEOS Functions:
            tint_value_split
        """
        fragments, values, count = tint_value_split(self._inner, size, start)
        return [Temporal._factory(fragments[i]) for i in range(count)]

    def value_time_split(
        self,
        value_size: int,
        duration: Union[str, timedelta],
        value_start: Optional[int] = 0,
        time_start: Optional[Union[str, datetime]] = None,
    ) -> List[TInt]:
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
            A list of temporal integers.

        MEOS Functions:
            tint_value_time_split
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
        tiles, _, _, count = tint_value_time_split(
            self._inner, value_size, dt, value_start, st
        )
        return [Temporal._factory(tiles[i]) for i in range(count)]

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TInt` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TIntInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TIntSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TIntSeqSet(string=value)
            else:
                return TIntSeq(string=value)
        raise Exception("ERROR: Could not parse temporal integer value")


class TIntInst(TInstant[int, "TInt", "TIntInst", "TIntSeq", "TIntSeqSet"], TInt):
    """
    Class for representing temporal integers at a single instant.
    """

    _make_function = tintinst_make
    _cast_function = int

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        value: Optional[Union[str, int]] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TIntSeq(TSequence[int, "TInt", "TIntInst", "TIntSeq", "TIntSeqSet"], TInt):
    """
    Class for representing temporal integers over a tstzspan of time.
    """

    ComponentClass = TIntInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TIntInst]]] = None,
        lower_inc: bool = True,
        upper_inc: bool = False,
        interpolation: TInterpolation = TInterpolation.STEPWISE,
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


class TIntSeqSet(TSequenceSet[int, "TInt", "TIntInst", "TIntSeq", "TIntSeqSet"], TInt):
    """
    Class for representing temporal integers over a tstzspan of time with gaps.
    """

    ComponentClass = TIntSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TIntSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
