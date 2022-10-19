from pymeos_cffi import temporal_tcount_transfn

from pymeos.aggregators.aggregator import BaseAggregator


class TemporalCountAggregator(BaseAggregator):
    add_function = temporal_tcount_transfn
