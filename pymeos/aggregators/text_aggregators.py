from pymeos_cffi import *

from ..main import TText
from .aggregator import BaseAggregator


class TemporalTextMaxAggregator(BaseAggregator[TText, TText]):
    """
    Temporal maximum of all aggregated temporal texts.

    MEOS Functions:
        ttext_tmax_transfn, temporal_tagg_finalfn
    """

    _add_function = ttext_tmax_transfn


class TemporalTextMinAggregator(BaseAggregator[TText, TText]):
    """
    Temporal minimum of all aggregated temporal texts.

    MEOS Functions:
        ttext_tmin_transfn, temporal_tagg_finalfn
    """

    _add_function = ttext_tmin_transfn
