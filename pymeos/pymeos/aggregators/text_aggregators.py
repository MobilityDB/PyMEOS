from pymeos_cffi import ttext_tmin_transfn, ttext_tmax_transfn

from pymeos.aggregators.aggregator import BaseAggregator


class TemporalTextMaxAggregator(BaseAggregator):
    _add_function = ttext_tmax_transfn


class TemporalTextMinAggregator(BaseAggregator):
    _add_function = ttext_tmin_transfn
