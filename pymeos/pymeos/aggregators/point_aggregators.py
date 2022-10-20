from pymeos_cffi import tpoint_extent_transfn

from .aggregator import BaseAggregator
from ..boxes import STBox


class TemporalNumberExtentAggregator(BaseAggregator):
    _add_function = tpoint_extent_transfn
    _final_function = lambda x: x
    _result_function = lambda x: STBox(_inner=x)
