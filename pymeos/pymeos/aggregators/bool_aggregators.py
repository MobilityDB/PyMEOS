from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..main import TBool


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
