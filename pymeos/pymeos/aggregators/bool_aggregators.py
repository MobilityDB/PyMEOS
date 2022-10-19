from pymeos_cffi import tbool_tand_transfn, tbool_tor_transfn

from pymeos.aggregators.aggregator import BaseAggregator


class TemporalAndAggregator(BaseAggregator):
    add_function = tbool_tand_transfn


class TemporalOrAggregator(BaseAggregator):
    add_function = tbool_tor_transfn
