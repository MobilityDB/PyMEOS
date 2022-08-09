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
from lib.functions import temporal_start_instant, temporal_end_instant, temporal_instant_n, temporal_instants, \
    temporal_num_sequences, temporal_start_sequence, temporal_end_sequence, temporal_sequence_n, temporal_sequences
from ..temporal.temporal import Temporal


class TSequenceSet(Temporal):
    """
    Abstract class for representing temporal values of sequence set subtype.
    """

    def temp_subtype(cls):
        """
        Subtype of the temporal value, that is, ``'SequenceSet'``.
        """
        return "SequenceSet"

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        for seq in self._sequenceList:
            per = seq.period
            if per.lower > timestamp:
                return None
            if per.contains_timestamp(timestamp):
                return seq.value_at_timestamp(timestamp)
        return None

    @property
    def start_instant(self):
        """
        Start instant.
        """
        return self.ComponentClass.ComponentClass(_inner=temporal_start_instant(self._inner))

    @property
    def end_instant(self):
        """
        End instant.
        """
        return self.ComponentClass.ComponentClass(_inner=temporal_end_instant(self._inner))

    def instant_n(self, n):
        """
        N-th distinct instant.
        """
        # 1-based
        return self.ComponentClass.ComponentClass(_inner=temporal_instant_n(self._inner, n))

    @property
    def instants(self):
        """
        List of instants.
        """
        ts, count = temporal_instants(self._inner)
        return [self.ComponentClass.ComponentClass(_inner=ts[i]) for i in range(count)]

    @property
    def num_sequences(self):
        """
        Number of sequences.
        """
        return temporal_num_sequences(self._inner)

    @property
    def start_sequence(self):
        """
        Start sequence.
        """
        return self.ComponentClass(_inner=temporal_start_sequence(self._inner))

    @property
    def end_sequence(self):
        """
        End sequence.
        """
        return self.ComponentClass(_inner=temporal_end_sequence(self._inner))

    def sequence_n(self, n):
        """
        N-th sequence.
        """
        # 1-based
        return self.ComponentClass(_inner=temporal_sequence_n(self._inner, n))

    @property
    def sequences(self):
        """
        List of sequences.
        """
        ss, count = temporal_sequences(self._inner)
        return [self.ComponentClass(_inner=ss[i]) for i in range(count)]

    # Comparisons are missing
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._sequenceList == other._sequenceList and self._interp == other._interp:
                return True
        return False

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'({self._sequenceList!r}, {self._interp!r})')
