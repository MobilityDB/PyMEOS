from pymeos_cffi import *

from .aggregator import BaseAggregator
from ..boxes import TBox
from ..main import TInt, TFloat, TNumber


class TemporalAverageAggregator(BaseAggregator[TNumber, TNumber]):
    """
    Temporal average of aggregated temporal numbers. Accepts both Temporal Integers and Temporal floats

    MEOS Functions:
        tnumber_tavg_transfn, tnumber_tavg_finalfn
    """

    _add_function = tnumber_tavg_transfn
    _final_function = tnumber_tavg_finalfn


class TemporalNumberExtentAggregator(BaseAggregator[TNumber, TBox]):
    """
    Temporal and numeric extent of aggregated temporal numbers, i.e. smallest :class:`~pymeos.time.boxes.TBox` that
    includes all aggregated temporal numbers.

    MEOS Functions:
        tnumber_extent_transfn, temporal_tagg_finalfn
    """

    _add_function = tnumber_extent_transfn

    @classmethod
    def _finish(cls, state) -> TBox:
        return TBox(_inner=state)


class TemporalIntMaxAggregator(BaseAggregator[TInt, TInt]):
    """
    Temporal maximum of all aggregated temporal integers.

    MEOS Functions:
        tint_tmax_transfn, temporal_tagg_finalfn
    """

    _add_function = tint_tmax_transfn


class TemporalIntMinAggregator(BaseAggregator[TInt, TInt]):
    """
    Temporal minimum of all aggregated temporal integers.

    MEOS Functions:
        tint_tmin_transfn, temporal_tagg_finalfn
    """

    _add_function = tint_tmin_transfn


class TemporalIntSumAggregator(BaseAggregator[TInt, TInt]):
    """
    Temporal summ of all aggregated temporal integers.

    MEOS Functions:
        tint_tsum_transfn, temporal_tagg_finalfn
    """

    _add_function = tint_tsum_transfn


class TemporalFloatMaxAggregator(BaseAggregator[TFloat, TFloat]):
    """
    Temporal maximum of all aggregated temporal floats.

    MEOS Functions:
        tfloat_tmax_transfn, temporal_tagg_finalfn
    """

    _add_function = tfloat_tmax_transfn


class TemporalFloatMinAggregator(BaseAggregator[TFloat, TFloat]):
    """
    Temporal minimum of all aggregated temporal floats.

    MEOS Functions:
        tfloat_tmin_transfn, temporal_tagg_finalfn
    """

    _add_function = tfloat_tmin_transfn


class TemporalFloatSumAggregator(BaseAggregator[TFloat, TFloat]):
    """
    Temporal summ of all aggregated temporal floats.

    MEOS Functions:
        tfloat_tsum_transfn, temporal_tagg_finalfn
    """

    _add_function = tfloat_tsum_transfn
