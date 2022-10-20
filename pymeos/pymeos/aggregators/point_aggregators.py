from pymeos_cffi import tpoint_extent_transfn

from .aggregator import BaseAggregator
from ..boxes import STBox


class TemporalNumberExtentAggregator(BaseAggregator):
    add_function = tpoint_extent_transfn
    final_function = lambda x: x
    result_function = lambda x: STBox(_inner=x)
