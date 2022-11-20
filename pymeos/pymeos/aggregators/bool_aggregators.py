from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..main import TBool


class TemporalAndAggregator(BaseAggregator[TBool, TBool]):
    _add_function = tbool_tand_transfn


class TemporalOrAggregator(BaseAggregator[TBool, TBool]):
    _add_function = tbool_tor_transfn
