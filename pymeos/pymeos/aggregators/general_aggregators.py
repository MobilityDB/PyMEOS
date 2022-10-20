from pymeos_cffi import temporal_tcount_transfn, temporal_extent_transfn

from ..time import Period
from .aggregator import BaseAggregator, BaseGranularityAggregator


class TemporalCountAggregator(BaseGranularityAggregator):
    _add_function = temporal_tcount_transfn


class TemporalExtentAggregator(BaseAggregator):
    _add_function = temporal_extent_transfn
    _final_function = lambda x: x
    _result_function = lambda x: Period(_inner=x)
