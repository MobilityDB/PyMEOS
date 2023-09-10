from datetime import datetime
from typing import Union

from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..boxes import Box
from ..main import TIntSeq, TIntSeqSet
from ..temporal import Temporal, TInterpolation
from ..collections import Time, TimestampSet, Period, PeriodSet


class TemporalInstantCountAggregator(BaseAggregator[
                                         Union[datetime, TimestampSet, Temporal],
                                         TIntSeq]):
    """
    Temporal count for instantaneous temporal objects:

     - :class:`~datetime.datetime`
     - :class:`~pymeos.time.timestampset.TimestampSet`
     - :class:`~pymeos.temporal.temporal.Temporal` with Discrete interpolation

    MEOS Functions:
        timestamp_tcount_transfn, timestampset_tcount_transfn, temporal_tcount_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, datetime):
            state = timestamp_tcount_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TimestampSet):
            state = timestampset_tcount_transfn(state, temporal._inner)
        elif isinstance(temporal, Temporal) and temporal.interpolation() == TInterpolation.DISCRETE:
            state = temporal_tcount_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state


class TemporalPeriodCountAggregator(BaseAggregator[Union[Period, PeriodSet, Temporal], TIntSeqSet]):
    """
    Temporal count for non-instantaneous temporal objects:

     - :class:`~pymeos.time.period.Period`
     - :class:`~pymeos.time.periodset.PeriodSet`
     - :class:`~pymeos.temporal.temporal.Temporal` without Discrete interpolation

    MEOS Functions:
        period_tcount_transfn, periodset_tcount_transfn, temporal_tcount_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, Period):
            state = period_tcount_transfn(state, temporal._inner)
        elif isinstance(temporal, PeriodSet):
            state = periodset_tcount_transfn(state, temporal._inner)
        elif isinstance(temporal, Temporal) and temporal.interpolation() != TInterpolation.DISCRETE:
            state = temporal_tcount_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state


class TemporalExtentAggregator(BaseAggregator[Union[Time, Temporal], Period]):
    """
    Temporal extent of any kind of temporal object, i.e. smallest :class:`~pymeos.time.period.Period` that includes
    all aggregated temporal objects.

    MEOS Functions:
        temporal_extent_transfn, timestamp_extent_transfn, timestampset_extent_transfn, span_extent_transfn,
         spanset_extent_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, Temporal):
            state = temporal_extent_transfn(state, temporal._inner)
        elif isinstance(temporal, datetime):
            state = timestamp_extent_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TimestampSet):
            state = set_extent_transfn(state, temporal._inner)
        elif isinstance(temporal, Period):
            state = span_extent_transfn(state, temporal._inner)
            pass
        elif isinstance(temporal, PeriodSet):
            state = spanset_extent_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> Union[Temporal, Time, Box]:
        return Period(_inner=state)
