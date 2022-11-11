from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..main import TText


class TemporalTextMaxAggregator(BaseAggregator[TText, TText]):
    _add_function = ttext_tmax_transfn


class TemporalTextMinAggregator(BaseAggregator[TText, TText]):
    _add_function = ttext_tmin_transfn
