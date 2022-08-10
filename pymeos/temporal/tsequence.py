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

from pymeos_cffi.functions import tpoint_length
from ..temporal import TemporalInstants


class TSequence(TemporalInstants, ABC):
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

    @property
    def distance(self):
        return tpoint_length(self._inner)
