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
from typing import Optional, List, Union, TYPE_CHECKING

from dateutil.parser import parse
from pymeos_cffi import tfloat_to_tint, tnumber_to_span, floatspan_lower, floatspan_upper, tfloat_min_value, \
    tfloat_max_value, tfloat_spans
from pymeos_cffi.functions import tfloat_start_value, tfloat_end_value, tfloat_values, tfloat_value_at_timestamp, \
    datetime_to_timestamptz, tfloat_out, tfloatinst_make, tfloat_in, tfloat_value_split, tfloat_from_base, \
    tfloatdiscseq_from_base_time, tfloatseq_from_base_time, tfloatseqset_from_base_time
from spans.types import floatrange

from .tnumber import TNumber
from ..temporal import TInterpolation, Temporal, TInstant, TSequence, TSequenceSet
from ..time import TimestampSet, Period, PeriodSet

if TYPE_CHECKING:
    from .tint import TInt


class TFloat(TNumber, ABC):
    """
    Abstract class for representing temporal floats of any subtype.
    """

    BaseClass = float
    BaseClassDiscrete = False
    _parse_function = tfloat_in

    def to_tint(self) -> TInt:
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(tfloat_to_tint(self._inner))

    def to_floatrange(self) -> floatrange:
        span = tnumber_to_span(self._inner)
        return floatrange(floatspan_lower(span), floatspan_upper(span), span.lower_inc, span.upper_inc)

    @staticmethod
    def from_base(value: float, base: Temporal, interpolation: TInterpolation = TInterpolation.LINEAR) -> TFloat:
        result = tfloat_from_base(value, base._inner, interpolation)
        from ..factory import _TemporalFactory
        return _TemporalFactory.create_temporal(result)

    @staticmethod
    def from_base_time(value: float, base: Union[datetime, TimestampSet, Period, PeriodSet],
                       interpolation: TInterpolation = None) -> TFloat:
        if isinstance(base, datetime):
            return TFloatInst(_inner=tfloatinst_make(value, datetime_to_timestamptz(base)))
        elif isinstance(base, TimestampSet):
            return TFloatSeq(_inner=tfloatdiscseq_from_base_time(value, base._inner))
        elif isinstance(base, Period):
            return TFloatSeq(_inner=tfloatseq_from_base_time(value, base._inner, interpolation))
        elif isinstance(base, PeriodSet):
            return TFloatSeqSet(_inner=tfloatseqset_from_base_time(value, base._inner, interpolation))
        raise TypeError(f'Operation not supported with type {base.__class__}')

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value.startswith('Interp=Stepwise;'):
            value1 = value.replace('Interp=Stepwise;', '')
            if value1[0] == '{':
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        elif value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TFloatInst(string=value)
        elif value[0] == '[' or value[0] == '(':
            return TFloatSeq(string=value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TFloatSeqSet(string=value)
            else:
                return TFloatSeq(string=value)
        raise Exception("ERROR: Could not parse temporal float value")

    @property
    def value_range(self) -> floatrange:
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return self.to_floatrange()

    @property
    def value_ranges(self) -> List[floatrange]:
        spans, count = tfloat_spans(self._inner)
        return [floatrange(floatspan_lower(spans[i]), floatspan_upper(spans[i]), spans[i].lower_inc, spans[i].upper_inc)
                for i in range(count)]

    @property
    def start_value(self) -> float:
        """
        Start value.
        """
        return tfloat_start_value(self._inner)

    @property
    def end_value(self) -> float:
        """
        End value.
        """
        return tfloat_end_value(self._inner)

    @property
    def values(self) -> List[float]:
        """
        List of distinct values.
        """
        values, count = tfloat_values(self._inner)
        return [values[i] for i in range(count)]

    @property
    def min_value(self) -> float:
        """
        Minimum value.
        """
        return tfloat_min_value(self._inner)

    @property
    def max_value(self) -> float:
        """
        Maximum value.
        """
        return tfloat_max_value(self._inner)

    def value_at_timestamp(self, timestamp) -> float:
        """
        Value at timestamp.
        """
        return tfloat_value_at_timestamp(self._inner, datetime_to_timestamptz(timestamp), True)

    def to_str(self, max_decimals=5) -> str:
        return tfloat_out(self._inner, max_decimals)

    def value_split(self, start: float, size: float, count: int) -> List[Temporal]:
        tiles, buckets, new_count = tfloat_value_split(self._inner, start, size, count)
        from ..factory import _TemporalFactory
        return [_TemporalFactory.create_temporal(tiles[i]) for i in range(new_count)]

    def __str__(self):
        return tfloat_out(self._inner, 5)

    def as_wkt(self, precision: int = 6) -> str:
        return tfloat_out(self._inner, precision)


class TFloatInst(TInstant, TFloat):
    """
    Class for representing temporal floats of instant subtype.

    ``TFloatInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatInst(string='10.0@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``float`` or ``datetime``.

        >>> TFloatInst(value='10.0', timestamp='2019-09-08 00:00:00+01')
        >>> TFloatInst(value=10.0, timestamp=parse('2019-09-08 00:00:00+01'))

    """

    _make_function = tfloatinst_make
    _cast_function = int

    def __init__(self, string: Optional[str] = None, *, value: Optional[Union[str, float]] = None,
                 timestamp: Optional[Union[str, datetime]] = None, _inner=None):
        super().__init__(string=string, value=value, timestamp=timestamp, _inner=_inner)


class TFloatSeq(TSequence, TFloat):
    """
    Class for representing temporal floats of sequence subtype.

    ``TFloatSeq`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatSeq('[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')
        >>> TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01, 20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')

    Another possibility is to give the arguments as follows:

    * ``instantList`` is the list of composing instants, which can be instances of
      ``str`` or ``TFloatInst``,
    * ``lower_inc`` and ``upper_inc`` are instances of ``bool`` specifying
      whether the bounds are inclusive or not. By default ``lower_inc``
      is ``True`` and ``upper_inc`` is ``False``.
    * ``interp`` which is either ``'Linear'``, ``'Stepwise'`` or ``'Discrete'``, the first being
      the default.

    Some pymeos_examples are shown next.

        >>> TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'])
        >>> TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')])
        >>> TFloatSeq(['10.0@2019-09-01 00:00:00+01', '20.0@2019-09-02 00:00:00+01', '10.0@2019-09-03 00:00:00+01'], True, True, 'Stepwise')
        >>> TFloatSeq([TFloatInst('10.0@2019-09-01 00:00:00+01'), TFloatInst('20.0@2019-09-02 00:00:00+01'), TFloatInst('10.0@2019-09-03 00:00:00+01')], True, True, 'Stepwise')

    """

    ComponentClass = TFloatInst

    def __init__(self, string: Optional[str] = None, *, instant_list: Optional[List[Union[str, TFloatInst]]] = None,
                 lower_inc: bool = True, upper_inc: bool = False,
                 interpolation: TInterpolation = TInterpolation.LINEAR, normalize: bool = True, _inner=None):
        super().__init__(string=string, instant_list=instant_list, lower_inc=lower_inc, upper_inc=upper_inc,
                         interpolation=interpolation, normalize=normalize, _inner=_inner)


class TFloatSeqSet(TSequenceSet, TFloat):
    """
    Class for representing temporal floats of sequence subtype.

    ``TFloatSeqSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TFloatSeqSet('{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')
        >>> TFloatSeqSet('Interp=Stepwise;{[10.0@2019-09-01 00:00:00+01], [20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]}')

    Another possibility is to give the arguments as follows:

    * ``sequenceList`` is a list of composing sequences, which can be
      instances of ``str`` or ``TFloatSeq``,
    * ``interp`` can be ``'Linear'``, ``'Stepwise'`` or ``'Discrete'``, the first being
      the default.

    Some pymeos_examples are shown next.

        >>> TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'])
        >>> TFloatSeqSet(['[10.0@2019-09-01 00:00:00+01]', '[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Linear')
        >>> TFloatSeqSet(['Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]', 'Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]'], 'Stepwise')
        >>> TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')])
        >>> TFloatSeqSet([TFloatSeq('[10.0@2019-09-01 00:00:00+01]'),  TFloatSeq('[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Linear')
        >>> TFloatSeqSet([TFloatSeq('Interp=Stepwise;[10.0@2019-09-01 00:00:00+01]'), TFloatSeq('Interp=Stepwise;[20.0@2019-09-02 00:00:00+01, 10.0@2019-09-03 00:00:00+01]')], 'Stepwise')

    """

    ComponentClass = TFloatSeq

    def __init__(self, string: Optional[str] = None, *, sequence_list: Optional[List[Union[str, TFloatSeq]]] = None,
                 normalize: bool = True, _inner=None):
        super().__init__(string=string, sequence_list=sequence_list, normalize=normalize, _inner=_inner)
