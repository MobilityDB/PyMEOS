from datetime import datetime
from typing import Union

from pymeos_cffi import (
    timestamptz_union_transfn,
    datetime_to_timestamptz,
    set_union_transfn,
    set_union_finalfn,
    union_spanset_span,
    union_spanset_spanset,
)

from .aggregator import BaseAggregator
from ..collections import TsTzSet, TsTzSpan, TsTzSpanSet


class TimeInstantaneousUnionAggregator(
    BaseAggregator[Union[datetime, TsTzSet], TsTzSet]
):
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


class TimeContinuousUnionAggregator(
    BaseAggregator[Union[TsTzSpan, TsTzSpanSet], TsTzSpanSet]
):
    """
    Temporal union of continuous time objects (:class:`~pymeos.time.tstzspan.TsTzSpan` and
    :class:`~pymeos.time.tstzspanset.TsTzSpanSet`).

    MEOS Functions:
        union_spanset_span, union_spanset_spanset
    """

    @classmethod
    def _add(cls, state, temporal):
        if isinstance(temporal, TsTzSpan):
            state = union_spanset_span(state, temporal._inner)
        elif isinstance(temporal, TsTzSpanSet):
            state = union_spanset_spanset(state, temporal._inner)
        else:
            cls._error(temporal)
        return state

    @classmethod
    def _finish(cls, state) -> TsTzSpanSet:
        return TsTzSpanSet(_inner=state)
