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
from typing import Optional, Union, List, Any, Literal

from pymeos_cffi.functions import tsequence_make

from .temporal import Temporal
from .interpolation import TInterpolation


class TSequence(Temporal, ABC):
    """
    Abstract class for representing temporal values of sequence subtype.
    """

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, Any]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True, _inner=None):
        super().__init__()
        assert (_inner is not None) or ((string is not None) != (instant_list is not None)), \
            "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = _inner
        elif string is not None:
            self._inner = self.__class__._parse_function(string)
        else:
            self._instants = [x._inner if isinstance(x, self.ComponentClass) else self.__class__._parse_function(x) for
                              x in instant_list]
            # TODO Fix maxcount parameter value
            self._inner = tsequence_make(self._instants, len(self._instants), 10000000, lower_inc, upper_inc,
                                         interpolation.value, normalize)

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
