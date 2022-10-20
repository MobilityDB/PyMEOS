from __future__ import annotations

import abc
from datetime import datetime, timedelta
from typing import List, Optional, Union

from pymeos_cffi import temporal_tagg_finalfn, datetime_to_timestamptz, pg_timestamptz_in, timedelta_to_interval, \
    pg_interval_in

from ..factory import _TemporalFactory
from ..temporal import Temporal


class BaseAggregator(abc.ABC):
    _add_function = None
    _final_function = temporal_tagg_finalfn
    _result_function = _TemporalFactory.create_temporal

    @classmethod
    def aggregate(cls, temporals: List[Temporal]) -> Temporal:
        state = None
        for t in temporals:
            state = cls._add_function(state, t._inner)
        result = cls._final_function(state)
        return cls._result_function(result)

    @classmethod
    def start_aggregation(cls) -> Aggregation:
        return Aggregation(cls._add_function, cls._final_function, cls._result_function)


class BaseGranularityAggregator(BaseAggregator):

    @classmethod
    def aggregate(cls, temporals: List[Temporal], interval: Optional[Union[str, timedelta]] = None,
                  origin: Union['str', datetime] = '1970-01-01') -> Temporal:
        state = None
        for t in temporals:
            interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
                pg_interval_in(interval, -1) if isinstance(interval, str) else None
            origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
                pg_timestamptz_in(origin, -1)
            state = cls._add_function(state, t._inner, interval_converted, origin_converted)
        result = cls._final_function(state)
        return cls._result_function(result)

    @classmethod
    def start_aggregation(cls, interval: Optional[Union[str, timedelta]] = None,
                          origin: Union['str', datetime] = '1970-0-0') -> Aggregation:
        interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
            pg_interval_in(interval, -1)
        origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
            pg_timestamptz_in(origin, -1)
        return GranularAggregation(cls._add_function, cls._final_function, cls._result_function, interval_converted,
                                   origin_converted)


class Aggregation:

    def __init__(self, add_function, final_function, result_function) -> None:
        super().__init__()
        self._add_function = add_function
        self._final_function = final_function
        self._result_function = result_function
        self._state = None

    def add(self, new_temporal: Temporal) -> Aggregation:
        self._state = self._add_function(self._state, new_temporal._inner)
        return self

    def finish(self) -> Temporal:
        result = self._final_function(self._state)
        return self._result_function(result)


class GranularAggregation(Aggregation):
    def __init__(self, add_function, final_function, result_function, interval, origin) -> None:
        super().__init__(add_function, final_function, result_function)
        self._interval = interval
        self._origin = origin

    def add(self, new_temporal: Temporal) -> GranularAggregation:
        self._state = self._add_function(self._state, new_temporal._inner, self._interval, self._origin)
        return self
