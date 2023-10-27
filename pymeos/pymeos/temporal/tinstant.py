from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Optional, Union, Any, TYPE_CHECKING, TypeVar, List

from pymeos_cffi import *

from .temporal import Temporal

TBase = TypeVar("TBase")
TG = TypeVar("TG", bound="Temporal[Any]")
TI = TypeVar("TI", bound="TInstant[Any]")
TS = TypeVar("TS", bound="TSequence[Any]")
TSS = TypeVar("TSS", bound="TSequenceSet[Any]")
Self = TypeVar("Self", bound="TInstant[Any]")


class TInstant(Temporal[TBase, TG, TI, TS, TSS], ABC):
    """
    Base class for temporal instant types, i.e. temporal values that are
    defined at a single point in time.
    """

    __slots__ = ["_inner"]

    _make_function = None
    _cast_function = None

    def __init__(
        self,
        string: Optional[str] = None,
        *,
        value: Optional[Union[str, TBase]] = None,
        timestamp: Optional[Union[str, datetime]] = None,
        _inner=None,
    ):
        assert (_inner is not None) or (
            (string is not None) != (value is not None and timestamp is not None)
        ), "Either string must be not None or both point and timestamp must be not"
        if _inner is not None:
            self._inner = as_tinstant(_inner)
        elif string is not None:
            self._inner = as_tinstant(self.__class__._parse_function(string))
        else:
            ts = (
                datetime_to_timestamptz(timestamp)
                if isinstance(timestamp, datetime)
                else pg_timestamptz_in(timestamp, -1)
            )
            self._inner = self.__class__._make_function(
                self.__class__._cast_function(value), ts
            )

    def value(self) -> TBase:
        """
        Returns the value of the temporal instant.

        Returns:
            The value of the temporal instant.
        """
        return self.start_value()

    def timestamp(self) -> datetime:
        """
        Returns the timestamp of the temporal instant.

        Returns:
            A :class:`~datetime.datetime` object.

        MEOS Functions:
            temporal_timestamps
        """
        ts, count = temporal_timestamps(self._inner)
        assert count == 1
        return timestamptz_to_datetime(ts[0])

    def start_instant(self: Self) -> Self:
        return self

    def end_instant(self: Self) -> Self:
        return self

    def instant_n(self: Self, n: int) -> Self:
        if n == 0:
            return self
        else:
            raise Exception("ERROR: Out of range")

    def instants(self: Self) -> List[Self]:
        return [self]

    def start_timestamp(self) -> datetime:
        return self.timestamp()

    def end_timestamp(self) -> datetime:
        return self.timestamp()

    def timestamp_n(self, n) -> datetime:
        if n == 0:
            return self.timestamp()
        else:
            raise Exception("ERROR: Out of range")

    def timestamps(self) -> List[datetime]:
        return [self.timestamp()]
