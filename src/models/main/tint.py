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

from spans.types import intrange
from ..temporal import Temporal, TInstant, TInstantSet, TSequence, TSequenceSet

from datetime import datetime
from lib.functions import tinstantset_make, tint_in, tint_out, tintinst_make, datetime_to_timestamptz, \
    pg_timestamptz_in, tint_values, tint_start_value, tint_end_value, tsequence_make, temporal_subtype, \
        tsequenceset_make


class TInt(Temporal):
    """
    Abstract class for representing temporal integers of any subtype.
    """

    BaseClass = int
    BaseClassDiscrete = True

    @staticmethod
    def read_from_cursor(value, cursor=None):
        if not value:
            return None
        if value[0] != '{' and value[0] != '[' and value[0] != '(':
            return TIntInst(value)
        elif value[0] == '[' or value[0] == '(':
            return TIntSeq(value)
        elif value[0] == '{':
            if value[1] == '[' or value[1] == '(':
                return TIntSeqSet(value)
            else:
                return TIntInstSet(value)
        raise Exception("ERROR: Could not parse temporal integer value")

    @staticmethod
    def write(value):
        if not isinstance(value, TInt):
            raise ValueError('Value must be an instance of a subclass of TInt')
        return value.__str__().strip("'")

    @property
    def valueRange(self):
        """
        Range of values taken by the temporal value as defined by its minimum and maximum value
        """
        return intrange(self.min_value, self.max_value, True, True)

    @property
    def start_value(self):
        """
        Start value.
        """
        return tint_start_value(self._inner)

    @property
    def end_value(self):
        """
        End value.
        """
        return tint_end_value(self._inner)

    @property
    def min_value(self):
        """
        Minimum value.
        """
        return min(self.values)

    @property
    def max_value(self):
        """
        Maximum value.
        """
        return max(self.values)

    def value_at_timestamp(self, timestamp):
        """
        Value at timestamp.
        """
        # TODO check here
        if timestamp == self._time:
            return self._value
        else:
            return None

    def __str__(self):
        return tint_out(self._inner)


class TIntInst(TInstant, TInt):
    """
    Class for representing temporal integers of instant subtype.

    ``TIntInst`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TIntInst('10@2019-09-01')

    Another possibility is to give the ``value`` and the ``time`` arguments,
    which can be instances of ``str``, ``int`` or ``datetime``.

        >>> TIntInst('10', '2019-09-08 00:00:00+01')
        >>> TIntInst(['10', '2019-09-08 00:00:00+01'])
        >>> TIntInst(10, parse('2019-09-08 00:00:00+01'))
        >>> TIntInst([10, parse('2019-09-08 00:00:00+01')])

    """

    def __init__(self, value, time=None):
        super().__init__()
        if time is None:
            self._inner = tint_in(value)
        else:
            value = int(value)
            ts = datetime_to_timestamptz(time) if isinstance(time, datetime) \
                else pg_timestamptz_in(time, -1)
            self._inner = tintinst_make(value, ts)
        assert temporal_subtype(self._inner) == "Instant", "Internal error"

    @property
    def value(self) -> int:
        """
        Value component.
        """
        # TODO check
        return tint_values(self._inner)[0]

    @property
    def values(self):
        """
        List of distinct values.
        """
        # TODO check
        return [self.value]

class TIntInstSet(TInstantSet, TInt):
    """
    Class for representing temporal integers of instant set subtype.

    ``TIntInstSet`` objects can be created with a single argument of type string
    as in MobilityDB.

        >>> TIntInstSet('10@2019-09-01')

    Another possibility is to give a tuple or list of composing instants,
    which can be instances of ``str`` or ``TIntInst``.

        >>> TIntInstSet('10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01')
        >>> TIntInstSet(TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01'))
        >>> TIntInstSet(['10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01'])
        >>> TIntInstSet([TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01')])

    """

    ComponentClass = TIntInst

    def __init__(self,  *argv, merge:bool=True):
        super().__init__()
        instants = list()
        for item in argv:
            if isinstance(item, (tuple, list)):
                for inst in item:
                    instants.append(inst._inner if isinstance(inst, TIntInst) else tint_in(inst))
            else:
                instants.append(item._inner if isinstance(item, TIntInst) else tint_in(item))
        if len(instants) == 1 and temporal_subtype(instants[0]) == "InstantSet":
            self._inner = instants[0]
        else:
            self._inner = tinstantset_make(instants, len(instants), merge)
        assert temporal_subtype(self._inner) == "InstantSet", "Internal error"

    @property
    def values(self):
        """
        List of distinct values.
        """
        # TODO check
        return [True, False]

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

    Some examples are given next.

        >>> TIntSeq(['10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01'])
        >>> TIntSeq([TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01')])
        >>> TIntSeq(['10@2019-09-01 00:00:00+01', '20@2019-09-02 00:00:00+01', '10@2019-09-03 00:00:00+01'], True, True)
        >>> TIntSeq([TIntInst('10@2019-09-01 00:00:00+01'), TIntInst('20@2019-09-02 00:00:00+01'), TIntInst('10@2019-09-03 00:00:00+01')], True, True)

    """

    ComponentClass = TIntInst

    def __init__(self, instantList, lower_inc=True, upper_inc=False, normalize=True):
        # TODO Should the __init__ function also accept vairable-length arguments
        # like that for TIntInstSet?
        super().__init__()
        if isinstance(instantList, str):
            self._inner = tint_in(instantList)
        else:
            instants = [x._inner if isinstance(x, TIntInst) else tint_in(x) for x in instantList]
            # TODO The parameter linear of tsequence_make can be inferred from interpolation() of the given data type
            self._inner = tsequence_make(instants, len(instants), lower_inc, upper_inc, False, normalize)
        assert temporal_subtype(self._inner) == "Sequence", "Internal error"

    @classmethod
    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'

    @property
    def values(self):
        """
        List of distinct values.
        """
        # TODO 
        return [True, False]

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

    def __init__(self, sequenceList, normalize=True):
        # TODO Should the __init__ function also accept vairable-length arguments
        # like that for TIntInstSet?
        super().__init__()
        if isinstance(sequenceList, str):
            self._inner = tint_in(sequenceList)
        else:
            seqs = [x._inner if isinstance(x, TIntSeq) else tint_in(x) for x in sequenceList]
            self._inner = tsequenceset_make(seqs, len(seqs), normalize)
        assert temporal_subtype(self._inner) == "SequenceSet", "Internal error"

    @classmethod
    @property
    def interpolation(self):
        """
        Interpolation of the temporal value, that is, ``'Stepwise'``.
        """
        return 'Stepwise'

    @property
    def values(self):
        """
        List of distinct values.
        """
        # TODO check
        return [True, False]
