from __future__ import annotations

import abc

from typing import List
from pymeos_cffi import temporal_tagg_finalfn

from ..factory import _TemporalFactory
from ..temporal import Temporal


class BaseAggregator(abc.ABC):
    add_function = None
    final_function = temporal_tagg_finalfn

    @classmethod
    def aggregate(cls, temporals: List[Temporal]) -> Temporal:
        state = None
        for t in temporals:
            state = cls.add_function(state, t._inner)
        result = cls.final_function(state)
        return _TemporalFactory.create_temporal(result)

    @classmethod
    def start_aggregation(cls) -> Aggregation:
        return Aggregation(cls.add_function, cls.final_function)


class Aggregation:

    def __init__(self, add_function, final_function) -> None:
        super().__init__()
        self.add_function = add_function
        self.final_function = final_function
        self._state = None

    def add(self, new_temporal: Temporal) -> Aggregation:
        self._state = self.add_function(self._state, new_temporal._inner)
        return self

    def finish(self) -> Temporal:
        result = self.final_function(self._state)
        return _TemporalFactory.create_temporal(result)
