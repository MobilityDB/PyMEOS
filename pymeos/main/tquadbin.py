from __future__ import annotations

from abc import ABC
from typing import TypeVar, overload

from pymeos_cffi import *

from ..collections import *
from ..collections.cell import Quadbin
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.tquadbin_methods import TQuadbinRegularMixin
from .tcellindex import TCellIndex

Self = TypeVar("Self", bound="TQuadbin")


class TQuadbin(
    TQuadbinRegularMixin,
    TCellIndex[Quadbin, "TQuadbin", "TQuadbinInst", "TQuadbinSeq", "TQuadbinSeqSet"],
    ABC,
):
    """
    Abstract class for temporal Quadbin cells.
    """

    _mobilitydb_name = "tquadbin"

    BaseClass = Quadbin

    _parse_function = tquadbin_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: Quadbin, base: Temporal) -> TQuadbin:
        """
        Create a temporal Quadbin cell from a cell and the time frame of another
        temporal object.

        Args:
            value: Quadbin value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TQuadbin` object.

        MEOS Functions:
            tquadbin_from_base_temp
        """
        result = tquadbin_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: Quadbin, base: datetime) -> TQuadbinInst: ...

    @staticmethod
    @overload
    def from_base_time(value: Quadbin, base: TsTzSet | TsTzSpan) -> TQuadbinSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: Quadbin, base: TsTzSpanSet) -> TQuadbinSeqSet: ...

    @staticmethod
    def from_base_time(value: Quadbin, base: Time) -> TQuadbin:
        """
        Create a temporal Quadbin cell from a cell and a time object.

        Args:
            value: Quadbin value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal Quadbin cell.

        MEOS Functions:
            tquadbininst_make, tquadbinseq_from_base_tstzset,
            tquadbinseq_from_base_tstzspan, tquadbinseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TQuadbinInst(_inner=tquadbininst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TQuadbinSeq(_inner=tquadbinseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TQuadbinSeq(_inner=tquadbinseq_from_base_tstzspan(value._inner, base._inner))
        elif isinstance(base, TsTzSpanSet):
            return TQuadbinSeqSet(_inner=tquadbinseqset_from_base_tstzspanset(value._inner, base._inner))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal Quadbin cell from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal Quadbin cell.

        MEOS Functions:
            tquadbin_from_mfjson
        """
        result = tquadbin_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Value Accessors -------------------------------
    def start_value(self) -> Quadbin:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`Quadbin` with the start value.

        MEOS Functions:
            tquadbin_start_value
        """
        return Quadbin(_inner=tquadbin_start_value(self._inner))

    def end_value(self) -> Quadbin:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`Quadbin` with the end value.

        MEOS Functions:
            tquadbin_end_value
        """
        return Quadbin(_inner=tquadbin_end_value(self._inner))

    def value_set(self) -> set[Quadbin]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`Quadbin` with the values.

        MEOS Functions:
            tquadbin_values
        """
        values, count = tquadbin_values(self._inner)
        return {Quadbin(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> Quadbin:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`Quadbin` with the value.

        MEOS Functions:
            tquadbin_value_at_timestamptz
        """
        return Quadbin(_inner=tquadbin_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True))

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TQuadbin` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TQuadbinInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TQuadbinSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TQuadbinSeqSet(string=value)
            else:
                return TQuadbinSeq(string=value)
        raise Exception("ERROR: Could not parse temporal Quadbin cell value")


class TQuadbinInst(
    TInstant[Quadbin, "TQuadbin", "TQuadbinInst", "TQuadbinSeq", "TQuadbinSeqSet"],
    TQuadbin,
):
    """
    Class for representing temporal Quadbin cells at a single instant.
    """

    _make_function = tquadbininst_make
    _cast_function = lambda x: quadbin_in(x) if isinstance(x, str) else x._inner

    def __init__(
        self,
        string: str | None = None,
        *,
        value: str | Quadbin | None = None,
        timestamp: str | datetime | None = None,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TQuadbinSeq(
    TSequence[Quadbin, "TQuadbin", "TQuadbinInst", "TQuadbinSeq", "TQuadbinSeqSet"],
    TQuadbin,
):
    """
    Class for representing temporal Quadbin cells over a tstzspan of time.
    """

    ComponentClass = TQuadbinInst

    def __init__(
        self,
        string: str | None = None,
        *,
        instant_list: list[str | TQuadbinInst] | None = None,
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


class TQuadbinSeqSet(
    TSequenceSet[Quadbin, "TQuadbin", "TQuadbinInst", "TQuadbinSeq", "TQuadbinSeqSet"],
    TQuadbin,
):
    """
    Class for representing temporal Quadbin cells over a tstzspan of time
    with gaps.
    """

    ComponentClass = TQuadbinSeq

    def __init__(
        self,
        string: str | None = None,
        *,
        sequence_list: list[str | TQuadbinSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
