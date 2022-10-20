from pymeos_cffi import tnumber_tavg_transfn, tnumber_tavg_finalfn, tint_tmax_transfn, tint_tmin_transfn, \
    tfloat_tmax_transfn, tfloat_tmin_transfn, tint_tsum_transfn, tfloat_tsum_transfn, tnumber_extent_transfn

from ..boxes import TBox
from .aggregator import BaseAggregator


class TemporalAverageAggregator(BaseAggregator):
    _add_function = tnumber_tavg_transfn
    _final_function = tnumber_tavg_finalfn


class TemporalNumberExtentAggregator(BaseAggregator):
    _add_function = tnumber_extent_transfn
    _final_function = lambda x: x
    _result_function = lambda x: TBox(_inner=x)


class TemporalIntMaxAggregator(BaseAggregator):
    _add_function = tint_tmax_transfn


class TemporalIntMinAggregator(BaseAggregator):
    _add_function = tint_tmin_transfn


class TemporalIntSumAggregator(BaseAggregator):
    _add_function = tint_tsum_transfn


class TemporalFloatMaxAggregator(BaseAggregator):
    _add_function = tfloat_tmax_transfn


class TemporalFloatMinAggregator(BaseAggregator):
    _add_function = tfloat_tmin_transfn


class TemporalFloatSumAggregator(BaseAggregator):
    _add_function = tfloat_tsum_transfn
