from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..boxes import STBox
from ..main import TPoint


class TemporalPointExtentAggregator(BaseAggregator[TPoint, STBox]):
    _add_function = tpoint_extent_transfn

    @classmethod
    def _finish(cls, state) -> STBox:
        return STBox(_inner=state)
