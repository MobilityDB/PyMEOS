from pymeos_cffi import tbool_tand_transfn, tbool_tor_transfn

from ..main import TBool
from .aggregator import BaseAggregator


class TemporalAndAggregator(BaseAggregator):
    _add_function = tbool_tand_transfn
    _accepted_types = [TBool]


class TemporalOrAggregator(BaseAggregator):
    _add_function = tbool_tor_transfn
    _accepted_types = [TBool]
