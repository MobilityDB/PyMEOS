from __future__ import annotations

from abc import ABC
from typing import TypeVar, overload

from pymeos_cffi import *

from ..collections import *
from ..collections.cell import H3Index
from ..temporal import Temporal, TInstant, TInterpolation, TSequence, TSequenceSet
from ._generated.th3index_methods import TH3IndexRegularMixin
from .tcellindex import TCellIndex

Self = TypeVar("Self", bound="TH3Index")


class TH3Index(
    TH3IndexRegularMixin,
    TCellIndex[H3Index, "TH3Index", "TH3IndexInst", "TH3IndexSeq", "TH3IndexSeqSet"],
    ABC,
):
    """
    Abstract class for temporal H3 cells.
    """

    _mobilitydb_name = "th3index"

    BaseClass = H3Index

    _parse_function = th3index_in

    def __init__(self, _inner) -> None:
        super().__init__()

    # ------------------------- Constructors ----------------------------------
    @staticmethod
    def from_base_temporal(value: H3Index, base: Temporal) -> TH3Index:
        """
        Create a temporal H3 cell from a cell and the time frame of another
        temporal object.

        Args:
            value: H3Index value of the temporal.
            base: Temporal object to use as time frame.

        Returns:
            A new :class:`TH3Index` object.

        MEOS Functions:
            th3index_from_base_temp
        """
        result = th3index_from_base_temp(value._inner, base._inner)
        return Temporal._factory(result)

    @staticmethod
    @overload
    def from_base_time(value: H3Index, base: datetime) -> TH3IndexInst: ...

    @staticmethod
    @overload
    def from_base_time(value: H3Index, base: TsTzSet | TsTzSpan) -> TH3IndexSeq: ...

    @staticmethod
    @overload
    def from_base_time(value: H3Index, base: TsTzSpanSet) -> TH3IndexSeqSet: ...

    @staticmethod
    def from_base_time(value: H3Index, base: Time) -> TH3Index:
        """
        Create a temporal H3 cell from a cell and a time object.

        Args:
            value: H3Index value.
            base: Time object to use as temporal dimension.

        Returns:
            A new temporal H3 cell.

        MEOS Functions:
            th3indexinst_make, th3indexseq_from_base_tstzset,
            th3indexseq_from_base_tstzspan, th3indexseqset_from_base_tstzspanset
        """
        if isinstance(base, datetime):
            return TH3IndexInst(_inner=th3indexinst_make(value._inner, datetime_to_timestamptz(base)))
        elif isinstance(base, TsTzSet):
            return TH3IndexSeq(_inner=th3indexseq_from_base_tstzset(value._inner, base._inner))
        elif isinstance(base, TsTzSpan):
            return TH3IndexSeq(_inner=th3indexseq_from_base_tstzspan(value._inner, base._inner))
        elif isinstance(base, TsTzSpanSet):
            return TH3IndexSeqSet(_inner=th3indexseqset_from_base_tstzspanset(value._inner, base._inner))
        raise TypeError(f"Operation not supported with type {base.__class__}")

    @classmethod
    def from_mfjson(cls: type[Self], mfjson: str) -> Self:
        """
        Returns a temporal H3 cell from a MF-JSON string.

        Args:
            mfjson: The MF-JSON string.

        Returns:
            A temporal H3 cell.

        MEOS Functions:
            th3index_from_mfjson
        """
        result = th3index_from_mfjson(mfjson)
        return Temporal._factory(result)

    # ------------------------- Value Accessors -------------------------------
    def start_value(self) -> H3Index:
        """
        Returns the start value of `self`.

        Returns:
            A :class:`H3Index` with the start value.

        MEOS Functions:
            th3index_start_value
        """
        return H3Index(_inner=th3index_start_value(self._inner))

    def end_value(self) -> H3Index:
        """
        Returns the end value of `self`.

        Returns:
            A :class:`H3Index` with the end value.

        MEOS Functions:
            th3index_end_value
        """
        return H3Index(_inner=th3index_end_value(self._inner))

    def value_set(self) -> set[H3Index]:
        """
        Returns the set of values of `self`.

        Returns:
            A :class:`set` of :class:`H3Index` with the values.

        MEOS Functions:
            th3index_values
        """
        values, count = th3index_values(self._inner)
        return {H3Index(_inner=values[i]) for i in range(count)}

    def value_at_timestamp(self, timestamp: datetime) -> H3Index:
        """
        Returns the value of `self` at the given timestamp.

        Args:
            timestamp: A :class:`datetime` representing the timestamp.

        Returns:
            A :class:`H3Index` with the value.

        MEOS Functions:
            th3index_value_at_timestamptz
        """
        return H3Index(_inner=th3index_value_at_timestamptz(self._inner, datetime_to_timestamptz(timestamp), True))

    # ------------------------- Database Operations ---------------------------
    @staticmethod
    def read_from_cursor(value, _=None):
        """
        Reads a :class:`TH3Index` from a database cursor. Used when
        automatically loading objects from the database.
        Users should use the class constructor instead.
        """
        if not value:
            return None
        if value[0] != "{" and value[0] != "[" and value[0] != "(":
            return TH3IndexInst(string=value)
        elif value[0] == "[" or value[0] == "(":
            return TH3IndexSeq(string=value)
        elif value[0] == "{":
            if value[1] == "[" or value[1] == "(":
                return TH3IndexSeqSet(string=value)
            else:
                return TH3IndexSeq(string=value)
        raise Exception("ERROR: Could not parse temporal H3 cell value")


class TH3IndexInst(
    TInstant[H3Index, "TH3Index", "TH3IndexInst", "TH3IndexSeq", "TH3IndexSeqSet"],
    TH3Index,
):
    """
    Class for representing temporal H3 cells at a single instant.
    """

    _make_function = th3indexinst_make
    _cast_function = lambda x: h3index_in(x) if isinstance(x, str) else x._inner

    def __init__(
        self,
        string: str | None = None,
        *,
        value: str | H3Index | None = None,
        timestamp: str | datetime | None = None,
        _inner=None,
    ) -> None:
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TH3IndexSeq(
    TSequence[H3Index, "TH3Index", "TH3IndexInst", "TH3IndexSeq", "TH3IndexSeqSet"],
    TH3Index,
):
    """
    Class for representing temporal H3 cells over a tstzspan of time.
    """

    ComponentClass = TH3IndexInst

    def __init__(
        self,
        string: str | None = None,
        *,
        instant_list: list[str | TH3IndexInst] | None = None,
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


class TH3IndexSeqSet(
    TSequenceSet[H3Index, "TH3Index", "TH3IndexInst", "TH3IndexSeq", "TH3IndexSeqSet"],
    TH3Index,
):
    """
    Class for representing temporal H3 cells over a tstzspan of time
    with gaps.
    """

    ComponentClass = TH3IndexSeq

    def __init__(
        self,
        string: str | None = None,
        *,
        sequence_list: list[str | TH3IndexSeq] | None = None,
        normalize: bool = True,
        _inner=None,
    ):
        super().__init__(
            string=string,
            sequence_list=sequence_list,
            normalize=normalize,
            _inner=_inner,
        )
