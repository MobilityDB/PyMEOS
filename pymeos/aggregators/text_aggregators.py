from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..main import TText


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
