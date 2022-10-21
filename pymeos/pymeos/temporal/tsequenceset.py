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
from typing import Optional, List, Union, Any, TYPE_CHECKING

from pandas import DataFrame
from pymeos_cffi.functions import temporal_num_sequences, temporal_start_sequence, temporal_end_sequence, \
    temporal_sequence_n, temporal_sequences, \
    tsequenceset_make

from ..temporal.temporal import Temporal

if TYPE_CHECKING:
    from .tsequence import TSequence


class TSequenceSet(Temporal, ABC):
    """
    Abstract class for representing temporal values of sequence set subtype.
    """

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, Any]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (sequence_list is not None)), \
            "Either string must be not None or sequence_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            sequences = [x._inner if isinstance(x, self.ComponentClass) else self.__class__._parse_function(x)
                         for x in sequence_list]
            self._inner = tsequenceset_make(sequences, len(sequences), normalize)

    def temp_subtype(self):
        """
        Subtype of the temporal value, that is, ``'SequenceSet'``.
        """
        return "SequenceSet"

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
    def sequences(self) -> List[TSequence]:
        """
        List of sequences.
        """
        ss, count = temporal_sequences(self._inner)
        return [self.ComponentClass(_inner=ss[i]) for i in range(count)]

    def to_dataframe(self) -> DataFrame:
        data = {
            'sequence': [i + 1 for i, seq in enumerate(self.sequences) for _ in range(seq.num_instants)],
            'time': [t for seq in self.sequences for t in seq.timestamps],
            'value': [v for seq in self.sequences for v in seq.values]
        }
        return DataFrame(data).set_index(keys=['sequence', 'time'])
