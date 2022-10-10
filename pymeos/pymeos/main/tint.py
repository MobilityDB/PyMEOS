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
from typing import Optional, Union, List, TYPE_CHECKING

from dateutil.parser import parse
from pymeos_cffi import tint_value_split, tint_to_tfloat, intspan_to_intrange, nad_tint_tint
from pymeos_cffi.functions import tint_in, tint_out, tintinst_make, datetime_to_timestamptz, tint_values, \
    tint_start_value, tint_end_value, tint_value_at_timestamp, tint_from_base, tintdiscseq_from_base_time, \
    tintseq_from_base_time, tintseqset_from_base_time, tnumber_to_span, tint_min_value, tint_max_value, tint_at_value, \
    tint_at_values, tint_minus_value, tint_minus_values, adjacent_tint_int, contained_tint_int, contains_tint_int, \
    overlaps_tint_int, same_tint_int, nad_tint_int
from spans.types import intrange, floatrange

from .tnumber import TNumber
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import TimestampSet, Period, PeriodSet

if TYPE_CHECKING:
    from ..boxes import TBox
    from .tfloat import TFloat


class TInt(TNumber, ABC):
    """
    Abstract class for representing temporal integers of any subtype.
    """

    BaseClass = int
    BaseClassDiscrete = True
    _parse_function = tint_in

    def is_adjacent(self, other: Union[int,
                                       TBox, TNumber, floatrange, intrange,
                                       Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return adjacent_tint_int(self._inner, other)
        else:
            return super().is_adjacent(other)

    def is_contained_in(self, container: Union[int,
                                               TBox, TNumber, floatrange, intrange,
                                               Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(container, int):
            return contained_tint_int(self._inner, container)
        else:
            return super().is_contained_in(container)

    def contains(self, content: Union[int,
                                      TBox, TNumber, floatrange, intrange,
                                      Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(content, int):
            return contains_tint_int(self._inner, content)
        else:
            return super().contains(content)

    def overlaps(self, other: Union[int,
                                    TBox, TNumber, floatrange, intrange,
                                    Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return overlaps_tint_int(self._inner, other)
        else:
            return super().overlaps(other)

    def is_same(self, other: Union[int,
                                   TBox, TNumber, floatrange, intrange,
                                   Period, PeriodSet, datetime, TimestampSet, Temporal]) -> bool:
        if isinstance(other, int):
            return same_tint_int(self._inner, other)
        else:
            return super().is_same(other)

    def at(self, other: Union[int, List[int],
                              intrange, floatrange, List[intrange], List[floatrange], TBox,
                              datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, int):
            result = tint_at_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], int):
            result = tint_at_values(self._inner, other)
        else:
            return super().at(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def minus(self, other: Union[int, List[int],
                                 intrange, floatrange, List[intrange], List[floatrange], TBox,
                                 datetime, TimestampSet, Period, PeriodSet]) -> Temporal:
        if isinstance(other, int):
            result = tint_minus_value(self._inner, other)
        elif isinstance(other, list) and isinstance(other[0], int):
            result = tint_minus_values(self._inner, other)
        else:
            return super().minus(other)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    def nearest_approach_distance(self, other: Union[int, float, TNumber, TBox]) -> float:
        if isinstance(other, int):
            return nad_tint_int(self._inner, other)
        elif isinstance(other, TInt):
            return nad_tint_tint(self._inner, other._inner)
        else:
            return super(TInt, self).nearest_approach_distance(other)

    def to_tfloat(self) -> TFloat:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tint_to_tfloat(self._inner))

    def to_intrange(self) -> intrange:
        return intspan_to_intrange(tnumber_to_span(self._inner))

    @staticmethod
    def from_base(value: int, base: Temporal) -> TInt:
        result = tint_from_base(value, base._inner)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    @staticmethod
    def from_base_time(value: int, base: Union[datetime, TimestampSet, Period, PeriodSet]) -> TInt:
        if isinstance(base, datetime):
            return TIntInst(_inner=tintinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TIntSeq(_inner=tintdiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TIntSeq(_inner=tintseq_from_base_time(value, base._inner))
        elif isinstance(base, PeriodSet):
            return TIntSeqSet(_inner=tintseqset_from_base_time(value, base._inner))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TIntInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TIntSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TIntSeqSet(string=value)
            else:
                return TIntSeq(string=value)
        raise Exception("ERROR: Could not parse temporal integer value")

    @property
    def value_range(self) -> intrange:
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return self.to_intrange()

    @property
    def start_value(self) -> int:
        """
        Start value.
        """
        return tint_start_value(self._inner)

    @property
    def end_value(self) -> int:
        """
        End value.
        """
        return tint_end_value(self._inner)

    @property
    def values(self) -> List[int]:
        """
        List of distinct values.
        """
        values, count = tint_values(self._inner)
        return [values[i] for i in range(count)]

    @property
    def min_value(self) -> int:
        """
        Minimum value.
        """
        return tint_min_value(self._inner)

    @property
    def max_value(self) -> int:
        """
        Maximum value.
        """
        return tint_max_value(self._inner)

    def value_at_timestamp(self, timestamp) -> int:
        """
        Value at timestamp.
        """
        return tint_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def value_split(self, start: int, size: int, count: int) -> List[Temporal]:
        tiles, buckets, new_count = tint_value_split(self._inner, start, size, count)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def __str__(self):
        return tint_out(self._inner)

    def as_wkt(self):
        return tint_out(self._inner)


class TIntInst(TInstant, TInt):
    """
    Class for representing temporal integers of instant subtype.

    ``TIntInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TIntInst(string='10@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str`` or ``int`` and ``str`` or ``datetime`` respectively.

        >>> TIntInst(value='10', timestamp='2019-09-08 00:00:00+01')
        >>> TIntInst(value=10, timestamp=parse('2019-09-08 00:00:00+01'))

    """

    _make_function = tintinst_make
    _cast_function = int

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, int]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TIntSeq(TSequence, TInt):
    """
    Class for representing temporal integers of sequence subtype.

    ``TIntSeq`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TIntSeq('[10@2019-09-01 00:00:00+01, 20@2019-09-02 00:00:00+01, 10@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances of
      ``str`` or ``TIntInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.

    Some pymeos_examples are given next.

        >>> TIntSeq(['10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01'])
        >>> TIntSeq([TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01')])
        >>> TIntSeq(['10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01'], True, True)
        >>> TIntSeq([TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TIntInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TIntInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.STEPWISE, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TIntSeqSet(TSequenceSet, TInt):
    """
    Class for representing temporal integers of sequence subtype.

    ``TIntSeqSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TIntSeqSet('{[10@2019-09-01 00:00:00+01], [20@2019-09-02 00:00:00+01, 10@2019-09-03 00:00:00+01]}')

    Another possibility is to give the list of composing sequences, which
    can be instances of ``str`` or ``TIntSeq``.

        >>> TIntSeqSet(['[10@2019-09-01 00:00:00+01]', '[20@2019-09-02 00:00:00+01, 10@2019-09-03 00:00:00+01]'])
        >>> TIntSeqSet([TIntSeq('[10@2019-09-01 00:00:00+01]'), TIntSeq('[20@2019-09-02 00:00:00+01, 10@2019-09-03 00:00:00+01]')])
        >>> TIntSeqSet([TIntSeq('[10@2019-09-01 00:00:00+01]'), TIntSeq('[20@2019-09-02 00:00:00+01, 10@2019-09-03 00:00:00+01]')])

    """

    ComponentClass = TIntSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TIntSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
