from pymeos_cffi import tpoint_extent_transfn

from .aggregator import BaseAggregator
from ..boxes import STBox
from ..main import TPoint


class TemporalPointExtentAggregator(BaseAggregator):
    _add_function = tpoint_extent_transfn
    _accepted_types = [TPoint]

    @classmethod
    def _finish(cls, state) -> STBox:
        return STBox(_inner=state)
