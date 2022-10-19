from pymeos_cffi import tnumber_tavg_transfn, tnumber_tavg_finalfn, tint_tmax_transfn, tint_tmin_transfn, \
    tfloat_tmax_transfn, tfloat_tmin_transfn, tint_tsum_transfn, tfloat_tsum_transfn, tnumber_extent_transfn

from ..boxes import TBox
from .aggregator import BaseAggregator


class TemporalAverageAggregator(BaseAggregator):
    add_function = tnumber_tavg_transfn
    final_function = tnumber_tavg_finalfn


class TemporalNumberExtentAggregator(BaseAggregator):
    add_function = tnumber_extent_transfn
    final_function = lambda x: x
    result_function = lambda x: TBox(_inner=x)


class TemporalIntMaxAggregator(BaseAggregator):
    add_function = tint_tmax_transfn


class TemporalIntMinAggregator(BaseAggregator):
    add_function = tint_tmin_transfn


class TemporalIntSumAggregator(BaseAggregator):
    add_function = tint_tsum_transfn


class TemporalFloatMaxAggregator(BaseAggregator):
    add_function = tfloat_tmax_transfn


class TemporalFloatMinAggregator(BaseAggregator):
    add_function = tfloat_tmin_transfn


class TemporalFloatSumAggregator(BaseAggregator):
    add_function = tfloat_tsum_transfn