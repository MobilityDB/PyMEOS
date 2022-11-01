from __future__ import annotations

import abc
from datetime import datetime, timedelta
from typing import Optional, Union, List, Type, Generic, TypeVar

from pymeos_cffi import temporal_tagg_finalfn, datetime_to_timestamptz, pg_timestamptz_in, timedelta_to_interval, \
    pg_interval_in

from ..boxes import Box
from ..factory import _TemporalFactory
from ..temporal import Temporal
from ..time import Time

ResultType = TypeVar('ResultType', bound=Union[Temporal, Time, Box])
SourceType = TypeVar('SourceType', bound=Union[Temporal, Time, Box])
SelfAgg = TypeVar('SelfAgg', bound='Aggregation')


class BaseAggregator(Generic[SourceType, ResultType], abc.ABC):
    _add_function = None
    _final_function = temporal_tagg_finalfn

    _accepted_types: Union[Type, List[Type]] = [Temporal]

    @classmethod
    def aggregate(cls, temporals: List[SourceType]) -> ResultType:
        state = None
        for t in temporals:
            state = cls._add(state, t)
        return cls._finish(state)

    @classmethod
    def _add(cls, state, temporal: SourceType):
        cls._assert_correct_type(temporal)
        return cls._add_function(state, temporal._inner)

    @classmethod
    def _assert_correct_type(cls, element):
        if cls._accepted_types is None:
            return
        elif isinstance(cls._accepted_types, list):
            for at in cls._accepted_types:
                if isinstance(element, at):
                    return
        elif isinstance(element, cls._accepted_types):
            return
        cls._error(element)

    @classmethod
    def _finish(cls, state) -> SourceType:
        result = cls._final_function(state)
        return _TemporalFactory.create_temporal(result)

    @classmethod
    def start_aggregation(cls) -> Aggregation:
        return Aggregation(cls._add, cls._finish)

    @classmethod
    def _error(cls, element):
        raise TypeError(f'Cannot perform aggregation ({cls.__name__}) with the following element: '
                        f'{element} (Class: {element.__class__})')


class Aggregation(Generic[SourceType, ResultType]):

    def __init__(self, add_function, finish_function) -> None:
        super().__init__()
        self._add_function = add_function
        self._finish_function = finish_function
        self._state = None

    def add(self: SelfAgg, new_temporal: SourceType) -> SelfAgg:
        self._state = self._add_function(self._state, new_temporal)
        return self

    def aggregation(self) -> ResultType:
        return self._finish_function(self._state)


class BaseGranularityAggregator(BaseAggregator[SourceType, ResultType]):

    @classmethod
    def aggregate(cls, temporals: List[SourceType], interval: Optional[Union[str, timedelta]] = None,
                  origin: Union['str', datetime] = '1970-01-01') -> ResultType:
        state = None
        for t in temporals:
            state = cls._add(state, t, interval, origin)
        return cls._finish(state)

    @classmethod
    def _add(cls, state, temporal: SourceType, interval=None, origin='1970-01-01'):
        interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
            pg_interval_in(interval, -1) if isinstance(interval, str) else None
        origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
            pg_timestamptz_in(origin, -1)
        return cls._add_function(state, temporal._inner, interval_converted, origin_converted)

    @classmethod
    def start_aggregation(cls, interval: Optional[Union[str, timedelta]] = None,
                          origin: Union['str', datetime] = '1970-01-01') -> GranularAggregation[SourceType, ResultType]:
        return GranularAggregation(cls._add, cls._finish, interval, origin)


class GranularAggregation(Aggregation[SourceType, ResultType]):
    def __init__(self, add_function, finish_function, interval, origin) -> None:
        super().__init__(add_function, finish_function)
        self._interval = interval
        self._origin = origin

    def add(self: SelfAgg, new_temporal: SourceType) -> SelfAgg:
        self._state = self._add_function(self._state, new_temporal, self._interval, self._origin)
        return self
