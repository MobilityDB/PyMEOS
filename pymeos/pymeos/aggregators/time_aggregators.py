from datetime import datetime
from typing import Union

from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..collections import TimestampSet, Period, PeriodSet


class TimeInstantaneousUnionAggregator(BaseAggregator[Union[datetime, TimestampSet], TimestampSet]):
    """
    Temporal union of instantaneous time objects (:class:'~datetime.datetime' and
    :class:`~pymeos.time.timestampset.TimestampSet`).

    MEOS Functions:
        timestamp_union_transfn, set_union_transfn, set_union_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, datetime):
            state = timestamp_union_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TimestampSet):
            state = set_union_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> TimestampSet:
        result = set_union_finalfn(state)
        return TimestampSet(_inner=result)


class TimeContinuousUnionAggregator(BaseAggregator[Union[Period, PeriodSet], PeriodSet]):
    """
    Temporal union of continuous time objects (:class:`~pymeos.time.period.Period` and
    :class:`~pymeos.time.periodset.PeriodSet`).

    MEOS Functions:
        union_spanset_span, union_spanset_spanset
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, Period):
            state = union_spanset_span(state, temporal._inner)
        elif isinstance(temporal, PeriodSet):
            state = union_spanset_spanset(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> PeriodSet:
        return PeriodSet(_inner=state)
