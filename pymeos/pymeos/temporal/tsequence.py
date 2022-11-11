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
from typing import Optional, Union, List, Any, TypeVar, Type

from pymeos_cffi import *

from .interpolation import TInterpolation
from .temporal import Temporal

TBase = TypeVar('TBase')
TG = TypeVar('TG', bound='Temporal[Any]')
TI = TypeVar('TI', bound='TInstant[Any]')
TS = TypeVar('TS', bound='TSequence[Any]')
TSS = TypeVar('TSS', bound='TSequenceSet[Any]')
Self = TypeVar('Self', bound='TSequence[Any]')


class TSequence(Temporal[TBase, TG, TI, TS, TSS], ABC):
    """
    Abstract class for representing temporal values of sequence subtype.
    """

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, Any]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False, expandable: Union[bool, int] = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True, _inner=None):
        assert (_inner is not None) or ((string is not None) != (instant_list is not None)), \
            "Either string must be not None or instant_list must be not"
        if _inner is not None:
            self._inner = as_tsequence(_inner)
        elif string is not None:
            self._inner = as_tsequence(self.__class__._parse_function(string))
        else:
            self._instants = [x._inner if isinstance(x, self.ComponentClass) else self.__class__._parse_function(x) for
                              x in instant_list]
            count = len(self._instants)
            if not expandable:
                self._inner = tsequence_make(self._instants, count, lower_inc, upper_inc,
                                             interpolation.value, normalize)
            else:
                max_size = max(expandable, count) if isinstance(expandable, int) else 2 * count
                self._inner = tsequence_make_exp(self._instants, count, max_size, lower_inc, upper_inc,
                                                 interpolation.value, normalize)
        self._expandable_sequence = bool(expandable) or self._inner.maxcount > self._inner.count

    @property
    def _expandable(self) -> bool:
        return self._expandable_sequence

    @classmethod
    def from_instants(cls: Type[Self], instant_list: Optional[List[Union[str, Any]]],
                      lower_inc: bool = True, upper_inc: bool = False,
                      interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True) -> Self:
        return cls(instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc, interpolation=interpolation,
                   normalize=normalize)

    @property
    def lower_inc(self) -> bool:
        """
        Is the lower bound inclusive?
        """
        return self._inner.period.lower_inc

    @property
    def upper_inc(self) -> bool:
        """
        Is the upper bound inclusive?
        """
        return self._inner.period.upper_inc

    @property
    def num_sequences(self) -> int:
        """
        Number of sequences.
        """
        return 1

    @property
    def start_sequence(self: Self) -> Self:
        """
        Start sequence.
        """
        return self

    @property
    def end_sequence(self: Self) -> Self:
        """
        End sequence.
        """
        return self

    def sequence_n(self: Self, n) -> Self:
        """
        N-th sequence.
        """
        # 1-based
        if n == 1:
            return self
        else:
            raise Exception("ERROR: Out of range")

    @property
    def sequences(self: Self) -> List[Self]:
        """
        List of sequences.
        """
        return [self]

    def compact(self: Self) -> Self:
        result = tsequence_compact(self._inner)
        return Temporal._factory(result)

    def plot(self, *args, **kwargs):
        from ..plotters import TemporalSequencePlotter
        return TemporalSequencePlotter.plot(self, *args, **kwargs)
