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
from typing import Optional, Union, Any, TYPE_CHECKING

from pymeos_cffi import as_tinstant
from pymeos_cffi.functions import temporal_timestamps, timestamptz_to_datetime, datetime_to_timestamptz, \
    pg_timestamptz_in
from .temporal import Temporal
from ..time import Period

if TYPE_CHECKING:
    pass


class TInstant(Temporal, ABC):
    """
    Abstract class for representing temporal values of instant subtype.
    """
    __slots__ = ['_inner']

    _make_function = None
    _cast_function = None

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, Any]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__()
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

    @classmethod
    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, ``'Instant'``.
        """
        return "Instant"

    @property
    def timestamp(self):
        """
        Timestamp.
        """
        ts, count = temporal_timestamps(self._inner)
        assert count == 1
        return timestamptz_to_datetime(ts[0])

    @property
    def period(self):
        """
        Period on which the temporal value is defined ignoring the potential
        time gaps.
        """
        return Period(lower=self.timestamp, upper=self.timestamp, lower_inc=True, upper_inc=True)

    def value(self):
        """
        Value component.
        """
        return self.start_value

    @property
    def start_instant(self):
        """
        Start instant.
        """
        return self

    @property
    def end_instant(self):
        """
        End instant.
        """
        return self

    def instant_n(self, n: int):
        """
        N-th instant.
        """
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    @property
    def instants(self):
        """
        List of instants.
        """
        return [self]

    @property
    def start_timestamp(self):
        """
        Start timestamp.
        """
        return self.timestamp

    @property
    def end_timestamp(self):
        """
        End timestamp.
        """
        return self.timestamp

    def timestamp_n(self, n):
        """
        N-th timestamp
        """
        if n == 1:
            return self.timestamp
        else:
            raise Exception("ERROR: Out of range")

    @property
    def timestamps(self):
        """
        List of timestamps.
        """
        return [self.timestamp]
