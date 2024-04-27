from datetime import datetime
from typing import Union

from pymeos_cffi import (
    timestamptz_tcount_transfn,
    datetime_to_timestamptz,
    tstzset_tcount_transfn,
    temporal_tcount_transfn,
    tstzspan_tcount_transfn,
    tstzspanset_tcount_transfn,
    temporal_extent_transfn,
    timestamptz_extent_transfn,
    set_extent_transfn,
    span_extent_transfn,
    spanset_extent_transfn,
)

from .aggregator import BaseAggregator
from ..boxes import Box
from ..collections import Time, TsTzSet, TsTzSpan, TsTzSpanSet
from ..main import TIntSeq, TIntSeqSet
from ..temporal import Temporal, TInterpolation


class TemporalInstantCountAggregator(
    BaseAggregator[Union[datetime, TsTzSet, Temporal], TIntSeq]
):
    """
    Temporal count for instantaneous temporal objects:

     - :class:`~datetime.datetime`
     - :class:`~pymeos.time.tstzset.TsTzSet`
     - :class:`~pymeos.temporal.temporal.Temporal` with Discrete interpolation

    MEOS Functions:
        timestamp_tcount_transfn, tstzset_tcount_transfn, temporal_tcount_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, datetime):
            state = timestamptz_tcount_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TsTzSet):
            state = tstzset_tcount_transfn(state, temporal._inner)
        elif (
            isinstance(temporal, Temporal)
            and temporal.interpolation() == TInterpolation.DISCRETE
        ):
            state = temporal_tcount_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state


class TemporalPeriodCountAggregator(
    BaseAggregator[Union[TsTzSpan, TsTzSpanSet, Temporal], TIntSeqSet]
):
    """
    Temporal count for non-instantaneous temporal objects:

     - :class:`~pymeos.time.tstzspan.TsTzSpan`
     - :class:`~pymeos.time.tstzspanset.TsTzSpanSet`
     - :class:`~pymeos.temporal.temporal.Temporal` without Discrete interpolation

    MEOS Functions:
        tstzspan_tcount_transfn, tstzspanset_tcount_transfn, temporal_tcount_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, TsTzSpan):
            state = tstzspan_tcount_transfn(state, temporal._inner)
        elif isinstance(temporal, TsTzSpanSet):
            state = tstzspanset_tcount_transfn(state, temporal._inner)
        elif (
            isinstance(temporal, Temporal)
            and temporal.interpolation() != TInterpolation.DISCRETE
        ):
            state = temporal_tcount_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state


class TemporalExtentAggregator(BaseAggregator[Union[Time, Temporal], TsTzSpan]):
    """
    Temporal extent of any kind of temporal object, i.e. smallest :class:`~pymeos.time.tstzspan.TsTzSpan` that includes
    all aggregated temporal objects.

    MEOS Functions:
        temporal_extent_transfn, timestamp_extent_transfn, tstzset_extent_transfn, span_extent_transfn,
         spanset_extent_transfn, temporal_tagg_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, Temporal):
            state = temporal_extent_transfn(state, temporal._inner)
        elif isinstance(temporal, datetime):
            state = timestamptz_extent_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TsTzSet):
            state = set_extent_transfn(state, temporal._inner)
        elif isinstance(temporal, TsTzSpan):
            state = span_extent_transfn(state, temporal._inner)
            pass
        elif isinstance(temporal, TsTzSpanSet):
            state = spanset_extent_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> Union[Temporal, Time, Box]:
        return TsTzSpan(_inner=state)
