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
from functools import cached_property

from lib.functions import tpoint_length
from ..temporal import TemporalInstants
from ..time import Period, PeriodSet


class TSequence(TemporalInstants):
    """
    Abstract class for representing temporal values of sequence subtype.
    """

    @classmethod
    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, ``'Sequence'``.
        """
        return "Sequence"

    @property
    def lower_inc(self):
        """
        Is the lower bound inclusive?
        """
        return self._inner.lower_inc

    @property
    def upper_inc(self):
        """
        Is the upper bound inclusive?
        """
        return self._inner._upper_inc

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        for i in range(len(self._instantList)):
            inst1 = self._instantList[i]
            if inst1._time > timestamp:
                return None

            if i < len(self._instantList) - 1:
                inst2 = self._instantList[i + 1]
            else:
                inst2 = None
            if inst1._time == timestamp:
                if inst2 is not None or self._upper_inc:
                    return inst1._value
                else:
                    return None
            # We know that inst1._time < timestamp
            # if inst1 is the last instant
            if inst2 is None:
                return None
            else:
                if timestamp < inst2._time:
                    if self._interp == 'Stepwise':
                        return inst1._value
                    else:
                        return self._interpolate(inst1, inst2, timestamp)
        return None

    @property
    def num_sequences(self):
        """
        Number of sequences.
        """
        return 1

    @property
    def start_sequence(self):
        """
        Start sequence.
        """
        return self

    @property
    def end_sequence(self):
        """
        End sequence.
        """
        return self

    def sequence_n(self, n):
        """
        N-th sequence.
        """
        # 1-based
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    @property
    def sequences(self):
        """
        List of sequences.
        """
        return [self]

    @cached_property
    def distance(self):
        return tpoint_length(self._inner)
