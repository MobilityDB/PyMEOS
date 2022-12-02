from datetime import datetime, timedelta
from typing import Union

from pymeos_cffi import *

from .aggregator import BaseAggregator, BaseGranularityAggregator
from ..boxes import Box
from ..main import TIntSeq, TIntSeqSet
from ..temporal import Temporal, TInterpolation
from ..time import Time, TimestampSet, Period, PeriodSet


class TemporalInstantCountAggregator(BaseGranularityAggregator[Union[Time, Temporal], TIntSeq]):
    @classmethod
    def _add(cls, state, temporal, interval=None, origin='1970-01-01'):
        interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
            pg_interval_in(interval, -1) if isinstance(interval, str) else None
        origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
            pg_timestamptz_in(origin, -1)
        if isinstance(temporal, datetime):
            state = timestamp_tcount_transfn(state, datetime_to_timestamptz(temporal), interval_converted,
                                             origin_converted)
        elif isinstance(temporal, TimestampSet):
            state = timestampset_tcount_transfn(state, temporal._inner, interval_converted, origin_converted)
        elif isinstance(temporal, Temporal) and temporal.interpolation == TInterpolation.DISCRETE:
            state = temporal_tcount_transfn(state, temporal._inner, interval_converted, origin_converted)
        else:
            cls._error(temporal)
        return state


class TemporalPeriodCountAggregator(BaseGranularityAggregator[Union[Time, Temporal], TIntSeqSet]):
    @classmethod
    def _add(cls, state, temporal, interval=None, origin='1970-01-01'):
        interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
            pg_interval_in(interval, -1) if isinstance(interval, str) else None
        origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
            pg_timestamptz_in(origin, -1)
        if isinstance(temporal, Period):
            state = period_tcount_transfn(state, temporal._inner, interval_converted, origin_converted)
        elif isinstance(temporal, PeriodSet):
            state = periodset_tcount_transfn(state, temporal._inner, interval_converted, origin_converted)
        elif isinstance(temporal, Temporal) and temporal.interpolation != TInterpolation.DISCRETE:
            state = temporal_tcount_transfn(state, temporal._inner, interval_converted, origin_converted)
        else:
            cls._error(temporal)
        return state


class TemporalExtentAggregator(BaseAggregator[Union[Time, Temporal], Period]):

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, Temporal):
            state = temporal_extent_transfn(state, temporal._inner)
        elif isinstance(temporal, datetime):
            state = timestamp_extent_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TimestampSet):
            state = timestampset_extent_transfn(state, temporal._inner)
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
