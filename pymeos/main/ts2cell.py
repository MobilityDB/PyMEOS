from __future__ import annotations

from abc import ABC
from typing import TypeVar, overload

from pymeos_cffi import *

from ..collections import *
from ..collections.cell import S2Cell
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.ts2cell_methods import TS2CellRegularMixin
from .tcellindex import TCellIndex

Self = TypeVar("Self", bound="TS2Cell")


class TS2Cell(
    TS2CellRegularMixin,
    TCellIndex[S2Cell, "TS2Cell", "TS2CellInst", "TS2CellSeq", "TS2CellSeqSet"],
    ABC,
):
    """
    Abstract class for temporal S2 cells.
    """

    _mobilitydb_name = "ts2cell"

    BaseClass = S2Cell

    _parse_function = ts2cell_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: S2Cell, base: Temporal) -> TS2Cell:
        """
        Create a temporal S2 cell from a cell and the time frame of another
        temporal object.

        Args:
            value: S2Cell value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TS2Cell` object.

        MEOS Functions:
            ts2cell_from_base_temp
        """
        result = ts2cell_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: S2Cell, base: datetime) -> TS2CellInst: ...

    @staticmethod
    @overload
    def from_base_time(value: S2Cell, base: TsTzSet | TsTzSpan) -> TS2CellSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: S2Cell, base: TsTzSpanSet) -> TS2CellSeqSet: ...

    @staticmethod
    def from_base_time(value: S2Cell, base: Time) -> TS2Cell:
        """
        Create a temporal S2 cell from a cell and a time object.

        Args:
            value: S2Cell value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal S2 cell.

        MEOS Functions:
            ts2cellinst_make, ts2cellseq_from_base_tstzset,
            ts2cellseq_from_base_tstzspan, ts2cellseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TS2CellInst(_inner=ts2cellinst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TS2CellSeq(_inner=ts2cellseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TS2CellSeq(_inner=ts2cellseq_from_base_tstzspan(value._inner, base._inner))
        elif isinstance(base, TsTzSpanSet):
            return TS2CellSeqSet(_inner=ts2cellseqset_from_base_tstzspanset(value._inner, base._inner))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal S2 cell from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal S2 cell.

        MEOS Functions:
            ts2cell_from_mfjson
        """
        result = ts2cell_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Value Accessors -------------------------------
    def start_value(self) -> S2Cell:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`S2Cell` with the start value.

        MEOS Functions:
            ts2cell_start_value
        """
        return S2Cell(_inner=ts2cell_start_value(self._inner))

    def end_value(self) -> S2Cell:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`S2Cell` with the end value.

        MEOS Functions:
            ts2cell_end_value
        """
        return S2Cell(_inner=ts2cell_end_value(self._inner))

    def value_set(self) -> set[S2Cell]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`S2Cell` with the values.

        MEOS Functions:
            ts2cell_values
        """
        values, count = ts2cell_values(self._inner)
        return {S2Cell(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> S2Cell:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`S2Cell` with the value.

        MEOS Functions:
            ts2cell_value_at_timestamptz
        """
        return S2Cell(_inner=ts2cell_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True))

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TS2Cell` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TS2CellInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TS2CellSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TS2CellSeqSet(string=value)
            else:
                return TS2CellSeq(string=value)
        raise Exception("ERROR: Could not parse temporal S2 cell value")


class TS2CellInst(
    TInstant[S2Cell, "TS2Cell", "TS2CellInst", "TS2CellSeq", "TS2CellSeqSet"],
    TS2Cell,
):
    """
    Class for representing temporal S2 cells at a single instant.
    """

    _make_function = ts2cellinst_make
    _cast_function = lambda x: s2cell_in(x) if isinstance(x, str) else x._inner

    def __init__(
        self,
        string: str | None = None,
        *,
        value: str | S2Cell | None = None,
        timestamp: str | datetime | None = None,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TS2CellSeq(
    TSequence[S2Cell, "TS2Cell", "TS2CellInst", "TS2CellSeq", "TS2CellSeqSet"],
    TS2Cell,
):
    """
    Class for representing temporal S2 cells over a tstzspan of time.
    """

    ComponentClass = TS2CellInst

    def __init__(
        self,
        string: str | None = None,
        *,
        instant_list: list[str | TS2CellInst] | None = None,
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


class TS2CellSeqSet(
    TSequenceSet[S2Cell, "TS2Cell", "TS2CellInst", "TS2CellSeq", "TS2CellSeqSet"],
    TS2Cell,
):
    """
    Class for representing temporal S2 cells over a tstzspan of time
    with gaps.
    """

    ComponentClass = TS2CellSeq

    def __init__(
        self,
        string: str | None = None,
        *,
        sequence_list: list[str | TS2CellSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
