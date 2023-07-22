from __future__ import annotations

from abc import ABC
from functools import reduce
from typing import Optional, Union, List, Set, overload, TYPE_CHECKING

from pymeos_cffi import *

from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import *

if TYPE_CHECKING:
    from .tbool import TBool


class TText(Temporal[str, 'TText', 'TTextInst', 'TTextSeq', 'TTextSeqSet'], ABC):
    BaseClass = str

    _parse_function = ttext_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Input/Output ----------------------------------
    @staticmethod
    def from_base_temporal(value: str, base: Temporal) -> TText:
        """
        Create a temporal string from a string and the time frame of another temporal object.

        Args:
            value: string value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TText` object.

        MEOS Functions:
            ttext_from_base_temp
        """
        result = ttext_from_base_temp(value, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: str, base: datetime) -> TTextInst:
        ...

    @staticmethod
    @overload
    def from_base_time(value: str, base: Union[TimestampSet, Period]) -> TTextSeq:
        ...

    @staticmethod
    @overload
    def from_base_time(value: str, base: PeriodSet) -> TTextSeqSet:
        ...

    @staticmethod
    def from_base_time(value: str, base: Time) -> TText:
        """
        Create a temporal string from a :class:`str` and a time object.

        Args:
            value: string value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttextinst_make, ttextseq_from_base_timestampset,
            ttextseq_from_base_period, ttextseqset_from_base_periodset
        """
        if isinstance(base, datetime):
            return TTextInst(_inner=ttextinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TTextSeq(_inner=ttextseq_from_base_timestampset(value, base._inner))
        elif isinstance(base, Period):
            return TTextSeq(_inner=ttextseq_from_base_period(value, base._inner))
        elif isinstance(base, PeriodSet):
            return TTextSeqSet(_inner=ttextseqset_from_base_periodset(value, base._inner))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    def __str__(self) -> str:
        """
        Returns the string representation of `self`.

        Returns:
            A string with the string representation of `self`.

        MEOS Functions:
            ttext_out
        """
        return ttext_out(self._inner)

    def as_wkt(self) -> str:
        """
        Returns the Well-Known Text representation of `self`.

        Returns:
            A string with the Well-Known Text representation of `self`.

        MEOS Functions:
            ttext_as_wkt
        """
        return ttext_out(self._inner)

    # ------------------------- Accessors -------------------------------------
    def value_set(self) -> Set[str]:
        """
        Returns the set of unique values of the temporal string.

        Returns:
            A set of unique values.

        MEOS Functions:
            ttext_values
        """
        values, count = ttext_values(self._inner)
        return {text2cstring(values[i]) for i in range(count)}

    def min_value(self) -> str:
        """
        Returns the minimum value of the temporal string.

        Returns:
            A :class:`str` with the minimum value.

        MEOS Functions:
            ttext_min_value
        """
        return ttext_min_value(self._inner)

    def max_value(self) -> str:
        """
        Returns the maximum value of the temporal string.

        Returns:
            A :class:`str` with the maximum value.

        MEOS Functions:
            ttext_max_value
        """
        return ttext_max_value(self._inner)

    def start_value(self) -> str:
        """
        Returns the start value of the temporal string.

        Returns:
            A :class:`str` with the start value.

        MEOS Functions:
            ttext_start_value
        """
        return ttext_start_value(self._inner)

    def end_value(self) -> str:
        """
        Returns the end value of the temporal string.

        Returns:
            A :class:`str` with the end value.

        MEOS Functions:
            ttext_end_value
        """
        return ttext_end_value(self._inner)

    def upper(self) -> TText:
        """
        Returns a new temporal string with the values of `self` converted to upper case.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_upper
        """
        return self.__class__(_inner=ttext_upper(self._inner))

    def lower(self) -> TText:
        """
        Returns a new temporal string with the values of `self` converted to lower case.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_lower
        """
        return self.__class__(_inner=ttext_lower(self._inner))

    def value_at_timestamp(self, timestamp: datetime) -> str:
        """
        Returns the value that `self` takes at a certain moment.

        Args:
            timestamp: The moment to get the value.

        Returns:
            A string with the value of `self` at `timestamp`.

        MEOS Functions:
            ttext_value_at_timestamp
        """
        result = ttext_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)
        return text2cstring(result[0])

    # ------------------------- Ever and Always Comparisons -------------------
    def always_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_eq
        """
        return ttext_always_eq(self._inner, value)

    def always_not_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always not equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always not equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_eq
        """
        return not ttext_always_eq(self._inner, value)

    def always_less(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always less than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always less than `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_lt
        """
        return ttext_always_lt(self._inner, value)

    def always_less_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always less than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always less than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_le
        """
        return ttext_always_le(self._inner, value)

    def always_greater(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always greater than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always greater than `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_le
        """
        return not ttext_ever_le(self._inner, value)

    def always_greater_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are always greater than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are always greater than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_lt
        """
        return not ttext_ever_lt(self._inner, value)

    def ever_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_eq
        """
        return ttext_ever_eq(self._inner, value)

    def ever_not_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever not equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever not equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_eq
        """
        return not ttext_ever_eq(self._inner, value)

    def ever_less(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever less than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever less than `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_lt
        """
        return ttext_ever_lt(self._inner, value)

    def ever_less_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever less than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever less than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_le
        """
        return ttext_ever_le(self._inner, value)

    def ever_greater(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever greater than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever greater than `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_le
        """
        return not ttext_always_le(self._inner, value)

    def ever_greater_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are ever greater than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are ever greater than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_lt
        """
        return not ttext_always_lt(self._inner, value)

    def never_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_eq
        """
        return not ttext_ever_eq(self._inner, value)

    def never_not_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never not equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never not equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_eq
        """
        return ttext_always_eq(self._inner, value)

    def never_less(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never less than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never less than `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_lt
        """
        return not ttext_ever_lt(self._inner, value)

    def never_less_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never less than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never less than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_ever_le
        """
        return not ttext_ever_le(self._inner, value)

    def never_greater_or_equal(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never greater than or equal to `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never greater than or equal to `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_lt
        """
        return ttext_always_lt(self._inner, value)

    def never_greater(self, value: str) -> bool:
        """
        Returns whether the values of `self` are never greater than `value`.

        Args:
            value: String value to compare.

        Returns:
            `True` if the values of `self` are never greater than `value`, `False` otherwise.

        MEOS Functions:
            ttext_always_le
        """
        return ttext_always_le(self._inner, value)

    # ------------------------- Temporal Comparisons --------------------------
    def temporal_equal(self, other: Union[str, Temporal]) -> Temporal:
        """
        Returns the temporal equality relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal equality relation.

        MEOS Functions:
            teq_ttext_text, teq_temporal_temporal
        """
        if isinstance(other, str):
            result = teq_ttext_text(self._inner, other)
        else:
            return super().temporal_equal(other)
        return Temporal._factory(result)

    def temporal_not_equal(self, other: Union[str, Temporal]) -> Temporal:
        """
        Returns the temporal not equal relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal not equal relation.

        MEOS Functions:
            tne_ttext_text, tne_temporal_temporal
        """
        if isinstance(other, str):
            result = tne_ttext_text(self._inner, other)
        else:
            return super().temporal_not_equal(other)
        return Temporal._factory(result)

    def temporal_less(self, other: Union[str, Temporal]) -> TBool:
        """
        Returns the temporal less than relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less than relation.

        MEOS Functions:
            tlt_ttext_text, tlt_temporal_temporal
        """
        if isinstance(other, str):
            result = tlt_ttext_text(self._inner, other)
        else:
            return super().temporal_less(other)
        return Temporal._factory(result)

    def temporal_less_or_equal(self, other: Union[str, Temporal]) -> Temporal:
        """
        Returns the temporal less or equal relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal less or equal relation.

        MEOS Functions:
            tle_ttext_text, tle_temporal_temporal
        """
        if isinstance(other, str):
            result = tle_ttext_text(self._inner, other)
        else:
            return super().temporal_less_or_equal(other)
        return Temporal._factory(result)

    def temporal_greater(self, other: Union[str, Temporal]) -> Temporal:
        """
        Returns the temporal greater than relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater than relation.

        MEOS Functions:
            tgt_ttext_text, tgt_temporal_temporal
        """
        if isinstance(other, str):
            result = tgt_ttext_text(self._inner, other)
        else:
            return super().temporal_greater(other)
        return Temporal._factory(result)

    def temporal_greater_or_equal(self, other: Union[str, Temporal]) -> Temporal:
        """
        Returns the temporal greater or equal relation between `self` and `other`.

        Args:
            other: A string or temporal object to compare to `self`.

        Returns:
            A :class:`TBool` with the result of the temporal greater or equal relation.

        MEOS Functions:
            tge_ttext_text, tge_temporal_temporal
        """
        if isinstance(other, str):
            result = tge_ttext_text(self._inner, other)
        else:
            return super().temporal_greater_or_equal(other)
        return Temporal._factory(result)

    # ------------------------- Restrictions ----------------------------------
    def at(self, other: Union[str, List[str], datetime, TimestampSet, Period, PeriodSet]) -> TText:
        """
        Returns a new temporal string with the values of `self` restricted to the time or value `other`.

        Args:
            other: Time or value to restrict to.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_at_value, temporal_at_timestamp, temporal_at_timestampset, temporal_at_period, temporal_at_periodset
        """
        if isinstance(other, str):
            result = ttext_at_value(self._inner, other)
        elif isinstance(other, list):
            # result = ttext_at_values(self._inner, other)
            results = [ttext_at_value(self._inner, value) for value in other]
            result = temporal_merge_array(results, len(results))
        else:
            return super().at(other)
        return Temporal._factory(result)

    def minus(self, other: Union[str, List[str], datetime, TimestampSet, Period, PeriodSet]) -> TText:
        """
        Returns a new temporal string with the values of `self` restricted to the complement of the time or value
         `other`.

        Args:
            other: Time or value to restrict to the complement of.

        Returns:
            A new temporal string.

        MEOS Functions:
            ttext_minus_value, temporal_minus_timestamp, temporal_minus_timestampset, temporal_minus_period,
            temporal_minus_periodset
        """
        if isinstance(other, str):
            result = ttext_minus_value(self._inner, other)
        elif isinstance(other, list):
            result = reduce(ttext_minus_value, other, self._inner)
        else:
            return super().minus(other)
        return Temporal._factory(result)

    # ------------------------- Text Operations ------------------------------
    def concatenate(self, other: Union[str, TText], other_before: bool = False):
        """
        Returns a new temporal string with the values of `self` concatenated with the values of `other`.

        Args:
            other: Temporal string or string to concatenate.
            other_before: If `True` the values of `other` are prepended to the values of `self`.

        Returns:
            A new temporal string.

        MEOS Functions:
            textcat_ttext_text, textcat_text_ttext, textcat_ttext_ttext

        """
        if isinstance(other, str):
            result = textcat_ttext_text(self._inner, other) if not other_before \
                else textcat_text_ttext(other, self._inner)
        elif isinstance(other, TText):
            result = textcat_ttext_ttext(self._inner, other._inner) if not other_before \
                else textcat_ttext_ttext(other._inner, self._inner)
        else:
            raise TypeError(f'Operation not supported with type {other.__class__}')
        return self.__class__(_inner=result)

    def __add__(self, other):
        """
        Returns a new temporal string with the values of `self` concatenated with the values of `other`.

        Args:
            other: Temporal string or string to concatenate.

        Returns:
            A new temporal string.

        MEOS Functions:
            textcat_ttext_text, textcat_text_ttext, textcat_ttext_ttext
        """
        return self.concatenate(other)

    def __radd__(self, other):
        """
        Returns a new temporal string with the values of `other` concatenated with the values of `self`.

        Args:
            other: Temporal string or string to concatenate.

        Returns:
            A new temporal string.

        MEOS Functions:
            textcat_ttext_text, textcat_text_ttext, textcat_ttext_ttext
        """
        return self.concatenate(other, True)

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TText` from a database cursor. Used when automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TTextInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TTextSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TTextSeqSet(string=value)
            else:
                return TTextSeq(string=value)
        raise Exception("ERROR: Could not parse temporal text value")


class TTextInst(TInstant[str, 'TText', 'TTextInst', 'TTextSeq', 'TTextSeqSet'], TText):
    """
    Class for representing temporal strings at a single instant.
    """
    _make_function = ttextinst_make
    _cast_function = str

    def __init__(self, string: Optional[str] = None, *, value: Optional[str] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TTextSeq(TSequence[str, 'TText', 'TTextInst', 'TTextSeq', 'TTextSeqSet'], TText):
    """
    Class for representing temporal strings over a period of time.
    """
    ComponentClass = TTextInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TTextInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         expandable=expandable, interpolation=interpolation, normalize=normalize, _inner=_inner)


class TTextSeqSet(TSequenceSet[str, 'TText', 'TTextInst', 'TTextSeq', 'TTextSeqSet'], TText):
    """
    Class for representing temporal strings over a period of time with gaps.
    """
    ComponentClass = TTextSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TTextSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
