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
from abc import ABC

from pymeos_cffi.functions import temporal_timestamps, timestamptz_to_datetime
from ..temporal import Temporal
from ..time import Period


class TInstant(Temporal, ABC):
    """
    Abstract class for representing temporal values of instant subtype.
    """
    __slots__ = ['_inner']

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

    @property
    def value(self) -> bool:
        """
        Value component.
        """
        return self.values[0]

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

    def instant_n(self, n):
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
