from __future__ import annotations

import abc
from datetime import datetime, timedelta
from typing import Optional, Union, List, Generic, TypeVar

from pymeos_cffi import *

from ..boxes import Box
from ..factory import _TemporalFactory
from ..temporal import Temporal
from ..time import Time

ResultType = TypeVar('ResultType', bound=Union[Temporal, Time, Box])
SourceType = TypeVar('SourceType', bound=Union[Temporal, Time, Box])
StateType = TypeVar('StateType')
SourceMeosType = TypeVar('SourceMeosType')
ResultMeosType = TypeVar('ResultMeosType')
SelfAgg = TypeVar('SelfAgg', bound='Aggregation')


class BaseAggregator(Generic[SourceType, ResultType], abc.ABC):
    """
    Abstract class for all aggregations.

    Can be easily extended overriding the :func:`~pymeos.aggregators.aggregator.BaseAggregator._add_function` and
    :func:`~pymeos.aggregators.aggregator.BaseAggregator._final_function` when the aggregation uses the inner MEOS
    objects, or :func:`~pymeos.aggregators.aggregator.BaseAggregator._add` and
    :func:`~pymeos.aggregators.aggregator.BaseAggregator._finish` for arbitrary aggregations.
    """

    @staticmethod
    def _add_function(state: Optional[StateType], meos_object: SourceMeosType) -> StateType:
        """
        Add `meos_object` to the aggregation. Usually a MEOS function.
        Args:
            state: current state of the aggregation.
            meos_object: new MEOS object to aggregate.

        Returns:
            New state of the aggregation after adding `meos_object`.

        """
        raise NotImplemented

    @staticmethod
    def _final_function(state: StateType) -> ResultMeosType:
        """
        Return the current value of the aggregation. Usually a MEOS function.
        Args:
            state: current state of the aggregation.

        Returns:
            Value of the aggregation.

        """
        return temporal_tagg_finalfn(state)

    @classmethod
    def _add(cls, state: Optional[StateType], temporal: SourceType) -> StateType:
        """
        Add the `temporal` object to the aggregation.
        Args:
            state: current state of the aggregation.
            temporal: new PyMEOS object to aggregate.

        Returns:
            New state of the aggregation after adding `temporal`.

        """
        return cls._add_function(state, temporal._inner)

    @classmethod
    def _finish(cls, state) -> ResultType:
        """
        Return the current value of the aggregation.
        Args:
            state: current state of the aggregation.

        Returns:
            Value of the aggregation.

        """
        result = cls._final_function(state)
        return _TemporalFactory.create_temporal(result)

    @classmethod
    def aggregate(cls, temporals: List[SourceType]) -> ResultType:
        """
        Aggregate a list of PyMEOS object at once.

        Useful when only the final result is desired and all the objects are available.

        For aggregating in a streaming fashion, see
        :func:'pymeos.aggregators.aggregator.BaseAggregator.start_aggregation'.

        Args:
            temporals: list of PyMEOS objects to aggregate.

        Returns:
            Result of applying the aggregation to the passed objects.

        """
        state = None
        for t in temporals:
            state = cls._add(state, t)
        return cls._finish(state)

    @classmethod
    def start_aggregation(cls) -> Aggregation:
        """
        Return an :class:`Aggregation` object that holds the state of a new aggregation.

        Returns:
            An :class:`Aggregation` instance
        """
        return Aggregation(cls._add, cls._finish)

    @classmethod
    def _error(cls, element):
        raise TypeError(f'Cannot perform aggregation ({cls.__name__}) with the following element: '
                        f'{element} (Class: {element.__class__})')


class Aggregation(Generic[SourceType, ResultType]):
    """
    Class representing an aggregation in process.

    This class is returned by the :func:`~pymeos.aggregators.aggregator.BaseAggregator.start_aggregation` method
    of :class:`BaseAggregator` subclasses, and shouldn't be created directly by the final user.
    """

    def __init__(self, add_function, finish_function) -> None:
        super().__init__()
        self._add_function = add_function
        self._finish_function = finish_function
        self._state = None

    def add(self: SelfAgg, new_temporal: SourceType) -> SelfAgg:
        """
        Add a new element to the aggregation.

        Returns itself to allowing chaining

        Examples:
            >>> aggregation.add(temporal1).add(temporal2)
            Is equivalent to
            >>> aggregation.add(temporal1)
            >>> aggregation.add(temporal2)

        Args:
            new_temporal: PyMEOS object to add to the aggregation

        Returns:
            `self`
        """
        self._state = self._add_function(self._state, new_temporal)
        return self

    def aggregation(self) -> ResultType:
        """
        Return the current aggregation value.

        Note that this doesn't finish the aggregation, so more elements can be still added.

        Examples:
            >>> aggregation.add(temporal1).add(temporal2)
            >>> intermediate = aggregation.aggregation()
            >>> aggregation.add(temporal3).add(temporal4)
            >>> final_result = aggregation.aggregation()

        Returns:
            Result of the aggregation
        """
        return self._finish_function(self._state)


class BaseGranularAggregator(BaseAggregator[SourceType, ResultType]):
    """
    Abstract class for granular aggregations.
    """

    @staticmethod
    def _add_function(state: Optional[StateType], meos_object: SourceMeosType, interval=None,
                      origin=None) -> StateType:
        raise NotImplemented

    @classmethod
    def aggregate(cls, temporals: List[SourceType], interval=None, origin=None) -> ResultType:
        """
        Aggregate a list of PyMEOS object at once with certain granularity.

        Useful when only the final result is desired and all the objects are available.

        For aggregating in a streaming fashion, see
        :func:`~pymeos.aggregators.aggregator.BaseGranularAggregator.start_aggregation`.

        Args:
            temporals: list of PyMEOS objects to aggregate.
            interval: width of the aggregation intervals
            origin: starting value of the first interval

        Returns:
            Result of applying the granular aggregation to the passed objects.

        """
        state = None
        for t in temporals:
            state = cls._add(state, t, interval, origin)
        return cls._finish(state)

    @classmethod
    def _add(cls, state: Optional[StateType], temporal: SourceType, interval=None, origin=None) -> StateType:
        """
        Add the `temporal` object to the aggregation.
        Args:
            state: current state of the aggregation.
            temporal: new PyMEOS object to aggregate.
            interval: width of the aggregation intervals
            origin: starting value of the first interval

        Returns:
            New state of the aggregation after adding `temporal`.

        """
        interval_converted = timedelta_to_interval(interval) if isinstance(interval, timedelta) else \
            pg_interval_in(interval, -1) if isinstance(interval, str) else None
        origin_converted = datetime_to_timestamptz(origin) if isinstance(origin, datetime) else \
            pg_timestamptz_in(origin, -1)
        return cls._add_function(state, temporal._inner, interval_converted, origin_converted)

    @classmethod
    def start_aggregation(cls, interval=None, origin=None) -> GranularAggregation[SourceType, ResultType]:
        return GranularAggregation(cls._add, cls._finish, interval, origin)


class GranularAggregation(Aggregation[SourceType, ResultType]):
    """
    Class representing a granular aggregation in process.

    This class is returned by the :func:`~pymeos.aggregators.aggregator.BaseGranularAggregator.start_aggregation` method
    of :class:`BaseGranularAggregator` subclasses, and shouldn't be created directly by the final user.
    """

    def __init__(self, add_function, finish_function, interval, origin) -> None:
        super().__init__(add_function, finish_function)
        self._interval = interval
        self._origin = origin

    def add(self: SelfAgg, new_temporal: SourceType) -> SelfAgg:
        self._state = self._add_function(self._state, new_temporal, self._interval, self._origin)
        return self
