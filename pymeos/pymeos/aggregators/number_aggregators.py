from pymeos_cffi import tnumber_tavg_transfn, tnumber_tavg_finalfn, tint_tmax_transfn, tint_tmin_transfn, \
    tfloat_tmax_transfn, tfloat_tmin_transfn, tint_tsum_transfn, tfloat_tsum_transfn, tnumber_extent_transfn

from .aggregator import BaseAggregator
from ..boxes import TBox
from ..main import TInt, TFloat, TNumber


class TemporalAverageAggregator(BaseAggregator[TNumber, TNumber]):
    _add_function = tnumber_tavg_transfn
    _final_function = tnumber_tavg_finalfn


class TemporalNumberExtentAggregator(BaseAggregator[TNumber, TBox]):
    _add_function = tnumber_extent_transfn

    @classmethod
    def _finish(cls, state) -> TBox:
        return TBox(_inner=state)


class TemporalIntMaxAggregator(BaseAggregator[TNumber, TBox]):
    _add_function = tint_tmax_transfn


class TemporalIntMinAggregator(BaseAggregator[TInt, TInt]):
    _add_function = tint_tmin_transfn


class TemporalIntSumAggregator(BaseAggregator[TInt, TInt]):
    _add_function = tint_tsum_transfn


class TemporalFloatMaxAggregator(BaseAggregator[TFloat, TFloat]):
    _add_function = tfloat_tmax_transfn


class TemporalFloatMinAggregator(BaseAggregator[TFloat, TFloat]):
    _add_function = tfloat_tmin_transfn


class TemporalFloatSumAggregator(BaseAggregator[TFloat, TFloat]):
    _add_function = tfloat_tsum_transfn
