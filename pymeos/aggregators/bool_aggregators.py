from pymeos_cffi import *

from ..main import TBool
from .aggregator import BaseAggregator


class TemporalAndAggregator(BaseAggregator[TBool, TBool]):
    """
    Temporal "and" of aggregated temporal booleans.

    MEOS Functions:
        tbool_tand_transfn, temporal_tagg_finalfn
    """

    _add_function = tbool_tand_transfn


class TemporalOrAggregator(BaseAggregator[TBool, TBool]):
    """
    Temporal "or" of aggregated temporal booleans.

    MEOS Functions:
        tbool_tor_transfn, temporal_tagg_finalfn
    """

    _add_function = tbool_tor_transfn
