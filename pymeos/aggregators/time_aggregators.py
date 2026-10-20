from datetime import datetime

from pymeos_cffi import (
    datetime_to_timestamptz,
    set_union_finalfn,
    set_union_transfn,
    span_union_transfn,
    spanset_union_finalfn,
    spanset_union_transfn,
    timestamptz_union_transfn,
)

from ..collections import TsTzSet, TsTzSpan, TsTzSpanSet
from .aggregator import BaseAggregator


class TimeInstantaneousUnionAggregator(BaseAggregator[datetime | TsTzSet, TsTzSet]):
    """
    Temporal union of instantaneous time objects (:class:'~datetime.datetime' and
    :class:`~pymeos.time.tstzset.TsTzSet`).

    MEOS Functions:
        timestamp_union_transfn, set_union_transfn, set_union_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, datetime):
            state = timestamptz_union_transfn(state, datetime_to_timestamptz(temporal))
        elif isinstance(temporal, TsTzSet):
            state = set_union_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> TsTzSet:
        result = set_union_finalfn(state)
        return TsTzSet(_inner=result)


class TimeContinuousUnionAggregator(BaseAggregator[TsTzSpan | TsTzSpanSet, TsTzSpanSet]):
    """
    Temporal union of continuous time objects (:class:`~pymeos.time.tstzspan.TsTzSpan` and
    :class:`~pymeos.time.tstzspanset.TsTzSpanSet`).

    Aggregates as #TimeInstantaneousUnionAggregator does, through the transition and final
    functions MEOS provides for the union of spans.

    MEOS Functions:
        span_union_transfn, spanset_union_transfn, spanset_union_finalfn
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, TsTzSpan):
            state = span_union_transfn(state, temporal._inner)
        elif isinstance(temporal, TsTzSpanSet):
            state = spanset_union_transfn(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> TsTzSpanSet:
        result = spanset_union_finalfn(state)
        return TsTzSpanSet(_inner=result)
