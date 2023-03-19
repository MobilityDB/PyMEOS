from datetime import datetime
from typing import Union

from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..time import TimestampSet


class TemporalTimestampUnionAggregator(BaseAggregator[Union[datetime, TimestampSet], TimestampSet]):
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

# class TemporalPeriodUnionAggregator(BaseAggregator[Union[Period, PeriodSet], PeriodSet]):
#     """
#     Temporal union of continuous time objects (:class:`~pymeos.time.period.Period` and
#     :class:`~pymeos.time.periodset.PeriodSet`).
#
#     MEOS Functions:
#         period_tunion_transfn, periodset_tunion_transfn, period_tunion_finalfn
#     """
#     @classmethod
#     def _add(cls, state, temporal):
#         if isinstance(temporal, Period):
#             state = period_tunion_transfn(state, temporal._inner)
#         elif isinstance(temporal, PeriodSet):
#             state = periodset_tunion_transfn(state, temporal._inner)
#         else:
#             cls._error(temporal)
#         return state
#
#     @classmethod
#     def _finish(cls, state) -> PeriodSet:
#         result = period_tunion_finalfn(state)
#         return PeriodSet(_inner=result)
