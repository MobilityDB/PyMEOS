from pymeos_cffi import temporal_tcount_transfn, temporal_extent_transfn

from ..time import Period
from .aggregator import BaseAggregator


class TemporalCountAggregator(BaseAggregator):
    add_function = temporal_tcount_transfn


class TemporalExtentAggregator(BaseAggregator):
    add_function = temporal_extent_transfn
    final_function = lambda x: x
    result_function = lambda x: Period(_inner=x)
