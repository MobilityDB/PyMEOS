###############################################################################
#
# This MobilityDB code is provided under The PostgreSQL License.
#
# Copyright (c) 2019-2022, Université libre de Bruxelles and MobilityDB
# contributors
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose, without fee, and without a written 
# agreement is hereby granted, provided that the above copyright notice and
# this paragraph and the following two paragraphs appear in all copies.
#
# IN NO EVENT SHALL UNIVERSITE LIBRE DE BRUXELLES BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF UNIVERSITE LIBRE DE BRUXELLES HAS BEEN ADVISED OF THE POSSIBILITY 
# OF SUCH DAMAGE.
#
# UNIVERSITE LIBRE DE BRUXELLES SPECIFICALLY DISCLAIMS ANY WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON
# AN "AS IS" BASIS, AND UNIVERSITE LIBRE DE BRUXELLES HAS NO OBLIGATIONS TO 
# PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS. 
#
###############################################################################
from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Optional, Union, Any, TYPE_CHECKING, TypeVar, List

from pymeos_cffi import *

from .temporal import Temporal
from ..time import Period

if TYPE_CHECKING:
    pass

TBase = TypeVar('TBase')
TG = TypeVar('TG', bound='Temporal[Any]')
TI = TypeVar('TI', bound='TInstant[Any]')
TS = TypeVar('TS', bound='TSequence[Any]')
TSS = TypeVar('TSS', bound='TSequenceSet[Any]')
Self = TypeVar('Self', bound='TInstant[Any]')


class TInstant(Temporal[TBase, TG, TI, TS, TSS], ABC):
    """
    Abstract class for representing temporal values of instant subtype.
    """
    __slots__ = ['_inner']

    _make_function = None
    _cast_function = None

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, Any]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        assert (_inner is not None) or ((string is not None) != (value is not None and timestamp is not None)), \
            "Either string must be not None or both point and timestamp must be not"
        if _inner is not None:
            self._inner = as_tinstant(_inner)
        elif string is not None:
            self._inner = as_tinstant(self.__class__._parse_function(string))
        else:
            ts = datetime_to_timestamptz(timestamp) if isinstance(timestamp, datetime) \
                else pg_timestamptz_in(timestamp, -1)
            self._inner = self.__class__._make_function(self.__class__._cast_function(value), ts)

    def timestamp(self) -> datetime:
        """
        Timestamp.
        """
        ts, count = temporal_timestamps(self._inner)
        assert count == 1
        return timestamptz_to_datetime(ts[0])

    def period(self) -> Period:
        """
        Period on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return Period(lower=self.timestamp(), upper=self.timestamp(), lower_inc=True, upper_inc=True)

    def value(self) -> TBase:
        """
        Value component.
        """
        return self.start_value()

    def start_instant(self: Self) -> Self:
        """
        Start instant.
        """
        return self

    def end_instant(self: Self) -> Self:
        """
        End instant.
        """
        return self

    def instant_n(self: Self, n: int) -> Self:
        """
        N-th instant.
        """
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    def instants(self: Self) -> List[Self]:
        """
        List of instants.
        """
        return [self]

    def start_timestamp(self) -> datetime:
        """
        Start timestamp.
        """
        return self.timestamp()

    def end_timestamp(self) -> datetime:
        """
        End timestamp.
        """
        return self.timestamp()

    def timestamp_n(self, n) -> datetime:
        """
        N-th timestamp
        """
        if n == 1:
            return self.timestamp()
        else:
            raise Exception("ERROR: Out of range")

    def timestamps(self) -> List[datetime]:
        """
        List of timestamps.
        """
        return [self.timestamp()]
