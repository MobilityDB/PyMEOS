from pymeos_cffi import ttext_tmin_transfn, ttext_tmax_transfn

from .aggregator import BaseAggregator
from ..main import TText


class TemporalTextMaxAggregator(BaseAggregator[TText, TText]):
    _add_function = ttext_tmax_transfn
    _accepted_types = [TText]


class TemporalTextMinAggregator(BaseAggregator[TText, TText]):
    _add_function = ttext_tmin_transfn
    _accepted_types = [TText]
