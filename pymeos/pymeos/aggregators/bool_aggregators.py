from pymeos_cffi import tbool_tand_transfn, tbool_tor_transfn

from ..main import TBool
from .aggregator import BaseAggregator


class TemporalAndAggregator(BaseAggregator[TBool, TBool]):
    _add_function = tbool_tand_transfn


class TemporalOrAggregator(BaseAggregator[TBool, TBool]):
    _add_function = tbool_tor_transfn
