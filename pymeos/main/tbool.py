from __future__ import annotations

from abc import ABC
from typing import Optional, Union, List, Set, overload, Type, TypeVar

from pymeos_cffi import *

from ..collections import *
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet

Self = TypeVar("Self", bound="TBool")


class TBool(Temporal[bool, "TBool", "TBoolInst", "TBoolSeq", "TBoolSeqSet"], ABC):
    """
    Base class for temporal boolean.
    """

    _mobilitydb_name = "tbool"

    BaseClass = bool
    _parse_function = tbool_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: bool, base: Temporal) -> TBool:
        """
        Create a temporal Boolean from a Boolean value and the time frame of
        another temporal object.

        Args:
            value: Boolean value.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TBool` object.

        MEOS Functions:
            tbool_from_base_temp
        """
        result = tbool_from_base_temp(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: bool, base: datetime) -> TBoolInst: ...

    @staticmethod
    @overload
    def from_base_time(value: bool, base: Union[TsTzSet, TsTzSpan]) -> TBoolSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: bool, base: TsTzSpanSet) -> TBoolSeqSet: ...

    @staticmethod
    def from_base_time(value: bool, base: Time) -> TBool:
        """
        Create a temporal boolean from a boolean value and a time object.

        Args:
            value: Boolean value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal boolean.

        MEOS Functions:
            tboolinst_make, tboolseq_from_base_tstzset,
            tboolseq_from_base_tstzspan, tboolseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TBoolInst(
                _inner=tboolinst_make(value, datetime_to_timestamptz(base))
            )
        elif isinstance(base, TsTzSet):
            return TBoolSeq(_inner=tboolseq_from_base_tstzset(value, base._inner))
        elif isinstance(base, TsTzSpan):
            return TBoolSeq(_inner=tboolseq_from_base_tstzspan(value, base._inner))
        elif isinstance(base, TsTzSpanSet):
            return TBoolSeqSet(
                _inner=tboolseqset_from_base_tstzspanset(value, base._inner)
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
            tbool_from_mfjson
        """

        result = tbool_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Output ----------------------------------------
    def __str__(self):
        """
        Returns the string representation of `self`.

        MEOS Function:
            tbool_out
        """
        return tbool_out(self._inner)

    def as_wkt(self):
        """
        Returns the string representation of `self` in WKT format.

        MEOS Function:
            tbool_out
        """
        return tbool_out(self._inner)

    # ------------------------- Accessors -------------------------------------
    def value_set(self) -> Set[bool]:
        """
        Returns the unique values in `self`.

        MEOS Function:
            tbool_values
        """
        values, count = tbool_values(self._inner)
        return {values[i] for i in range(count)}

    def start_value(self) -> bool:
        """
        Returns the starting value of `self`.

        MEOS Function:
            tbool_start_value
        """
        return tbool_start_value(self._inner)

    def end_value(self) -> bool:
        """
        Returns the ending value of `self`.

        MEOS Function:
            tbool_end_value
        """
        return tbool_end_value(self._inner)

    def value_at_timestamp(self, timestamp) -> bool:
        """
        Returns the value that `self` takes at a certain moment.

        Args:
            timestamp: Timestamp to get the value at.

        Returns:
            The value at the given timestamp.

        MEOS Function:
            tbool_value_at_timestamptz
        """
        return tbool_value_at_timestamptz(
            self._inner, datetime_to_timestamptz(timestamp), True
        )

    # ------------------------- Ever and Always Comparisons -------------------
    def always_eq(self, value: Union[bool, TBool]) -> bool:
        """
        Returns whether `self` is always equal to `value`.

        Args:
            value: Value to check for.

        Returns:
            True if `self` is always equal to `value`, False otherwise.

        MEOS Function:
            always_eq_tbool_bool, always_eq_temporal_temporal
        """
        if isinstance(value, bool):
            return always_eq_tbool_bool(self._inner, value) > 0
        elif isinstance(value, TBool):
            return always_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def ever_eq(self, value: Union[bool, TBool]) -> bool:
        """
        Returns whether `self` is ever equal to `value`.

        Args:
            value: Value to check for.

        Returns:
            True if `self` is ever equal to `value`, False otherwise.

        MEOS Function:
            ever_eq_tbool_bool, ever_eq_temporal_temporal
        """
        if isinstance(value, bool):
            return ever_eq_tbool_bool(self._inner, value) > 0
        elif isinstance(value, TBool):
            return ever_eq_temporal_temporal(self._inner, value._inner) > 0
        else:
            raise TypeError(f"Operation not supported with type {value.__class__}")

    def never_eq(self, value: Union[bool, TBool]) -> bool:
        """
        Returns whether `self` is never equal to `value`.

        Args:
            value: Value to check for.

        Returns:
            True if `self` is never equal to `value`, False otherwise.

        MEOS Function:
            ever_eq_tbool_bool, ever_eq_temporal_temporal
        """
        return not self.ever_eq(value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A temporal or boolean object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_tbool_tbool, teq_temporal_temporal
        """
        if isinstance(other, bool):
            result = teq_tbool_bool(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal inequality relation between `self` and `other`.

        Args:
            other: A temporal or boolean object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal inequality relation.

        MEOS Functions:
            tne_tbool_tbool, tne_temporal_temporal
        """
        if isinstance(other, bool):
            result = tne_tbool_bool(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Union[bool, Time]) -> TBool:
        """
        Returns a new temporal boolean with the values of `self` restricted to
        the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal boolean.

        MEOS Functions:
            tbool_at_value, temporal_at_timestamp, temporal_at_tstzset,
            temporal_at_tstzspan, temporal_at_tstzspanset
        """
        if isinstance(other, bool):
            result = tbool_at_value(self._inner, other)
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[bool, Time]) -> TBool:
        """
        Returns a new temporal boolean with the values of `self` restricted to
        the complement of the time or value
        `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal boolean.

        MEOS Functions:
            tbool_minus_value, temporal_minus_timestamp,
            temporal_minus_tstzset, temporal_minus_tstzspan,
            temporal_minus_tstzspanset
        """
        if isinstance(other, bool):
            result = tbool_minus_value(self._inner, other)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Boolean Operations ----------------------------
    def temporal_and(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal conjunction of `self` and `other`.

        Args:
            other: A temporal or boolean object to combine with `self`.

        Returns:
            A :class:`TBool` with the temporal conjunction of `self` and
            `other`.

        MEOS Functions:
            tand_tbool_bool, tand_tbool_tbool
        """
        if isinstance(other, bool):
            return self.__class__(_inner=tand_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tand_tbool_tbool(self._inner, other._inner))
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __and__(self, other):
        """
        Returns the temporal conjunction of `self` and `other`.

        Args:
            other: A temporal or boolean object to combine with `self`.

        Returns:
            A :class:`TBool` with the temporal conjunction of `self` and `other`.

        MEOS Functions:
            tand_tbool_bool, tand_tbool_tbool
        """
        return self.temporal_and(other)

    def temporal_or(self, other: Union[bool, TBool]) -> TBool:
        """
        Returns the temporal disjunction of `self` and `other`.

        Args:
            other: A temporal or boolean object to combine with `self`.

        Returns:
            A :class:`TBool` with the temporal disjunction of `self` and `other`.

        MEOS Functions:
            tor_tbool_bool, tor_tbool_tbool
        """
        if isinstance(other, bool):
            return self.__class__(_inner=tor_tbool_bool(self._inner, other))
        elif isinstance(other, TBool):
            return self.__class__(_inner=tor_tbool_tbool(self._inner, other._inner))
        raise TypeError(f"Operation not supported with type {other.__class__}")

    def __or__(self, other):
        """
        Returns the temporal disjunction of `self` and `other`.

        Args:
            other: A temporal or boolean object to combine with `self`.

        Returns:
            A :class:`TBool` with the temporal disjunction of `self` and `other`.

        MEOS Functions:
            tor_tbool_bool, tor_tbool_tbool
        """
        return self.temporal_or(other)

    def temporal_not(self) -> TBool:
        """
        Returns the temporal negation of `self`.

        Returns:
            A :class:`TBool` with the temporal negation of `self`.

        MEOS Function:
            tnot_tbool
        """
        return self.__class__(_inner=tnot_tbool(self._inner))

    def __neg__(self):
        """
        Returns the temporal negation of `self`.

        Returns:
            A :class:`TBool` with the temporal negation of `self`.

        MEOS Function:
            tnot_tbool
        """
        return self.temporal_not()

    def __invert__(self):
        """
        Returns the temporal negation of `self`.

        Returns:
            A :class:`TBool` with the temporal negation of `self`.

        MEOS Function:
            tnot_tbool
        """
        return self.temporal_not()

    def when_true(self) -> Optional[TsTzSpanSet]:
        """
        Returns a tstzspan set with the tstzspans where `self` is True.

        Returns:
            A :class:`TsTzSpanSet` with the tstzspans where `self` is True.

        MEOS Function:
            tbool_when_true
        """
        result = tbool_when_true(self._inner)
        return TsTzSpanSet(_inner=result) if result is not None else None

    def when_false(self) -> Optional[TsTzSpanSet]:
        """
        Returns a tstzspan set with the tstzspans where `self` is False.

        Returns:
            A :class:`TsTzSpanSet` with the tstzspans where `self` is False.

        MEOS Function:
            tbool_when_true, tnot_tbool
        """
        result = tbool_when_true(tnot_tbool(self._inner))
        return TsTzSpanSet(_inner=result) if result is not None else None

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TBool` from a database cursor. Used when automatically
        loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TBoolInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TBoolSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TBoolSeqSet(string=value)
            else:
                return TBoolSeq(string=value)
        raise Exception("ERROR: Could not parse temporal boolean value")


class TBoolInst(TInstant[bool, "TBool", "TBoolInst", "TBoolSeq", "TBoolSeqSet"], TBool):
    """
    Class for representing temporal boolean values at a single instant.
    """

    _make_function = tboolinst_make
    _cast_function = bool

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        value: Optional[Union[str, bool]] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TBoolSeq(TSequence[bool, "TBool", "TBoolInst", "TBoolSeq", "TBoolSeqSet"], TBool):
    """
    Class for representing temporal boolean values over a tstzspan of time.
    """

    ComponentClass = TBoolInst

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        instant_list: Optional[List[Union[str, TBoolInst]]] = None,
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


class TBoolSeqSet(
    TSequenceSet[bool, "TBool", "TBoolInst", "TBoolSeq", "TBoolSeqSet"], TBool
):
    """
    Class for representing temporal boolean values over a tstzspan of time with gaps.
    """

    ComponentClass = TBoolSeq

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        sequence_list: Optional[List[Union[str, TBoolSeq]]] = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
