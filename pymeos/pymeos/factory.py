from pymeos_cffi import MeosType, MeosTemporalSubtype

from .main import (
    TBoolInst,
    TBoolSeq,
    TBoolSeqSet,
    TIntInst,
    TIntSeq,
    TIntSeqSet,
    TFloatInst,
    TFloatSeq,
    TFloatSeqSet,
    TTextInst,
    TTextSeq,
    TTextSeqSet,
    TGeomPointInst,
    TGeomPointSeq,
    TGeomPointSeqSet,
    TGeogPointInst,
    TGeogPointSeq,
    TGeogPointSeqSet,
)
from .collections import (
    GeometrySet,
    GeographySet,
    IntSet,
    IntSpan,
    IntSpanSet,
    FloatSet,
    FloatSpan,
    FloatSpanSet,
    TextSet,
    DateSet,
    DateSpan,
    DateSpanSet,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)


class _TemporalFactory:
    """
    Factory class to create the proper PyMEOS class from a MEOS object.

    This class is used internally by PyMEOS classes and there shouldn't be any need to
    be used outside of them.
    """

    _mapper = {
        (MeosType.T_TBOOL, MeosTemporalSubtype.INSTANT): TBoolInst,
        (MeosType.T_TBOOL, MeosTemporalSubtype.SEQUENCE): TBoolSeq,
        (MeosType.T_TBOOL, MeosTemporalSubtype.SEQUENCE_SET): TBoolSeqSet,
        (MeosType.T_TINT, MeosTemporalSubtype.INSTANT): TIntInst,
        (MeosType.T_TINT, MeosTemporalSubtype.SEQUENCE): TIntSeq,
        (MeosType.T_TINT, MeosTemporalSubtype.SEQUENCE_SET): TIntSeqSet,
        (MeosType.T_TFLOAT, MeosTemporalSubtype.INSTANT): TFloatInst,
        (MeosType.T_TFLOAT, MeosTemporalSubtype.SEQUENCE): TFloatSeq,
        (MeosType.T_TFLOAT, MeosTemporalSubtype.SEQUENCE_SET): TFloatSeqSet,
        (MeosType.T_TTEXT, MeosTemporalSubtype.INSTANT): TTextInst,
        (MeosType.T_TTEXT, MeosTemporalSubtype.SEQUENCE): TTextSeq,
        (MeosType.T_TTEXT, MeosTemporalSubtype.SEQUENCE_SET): TTextSeqSet,
        (MeosType.T_TGEOMPOINT, MeosTemporalSubtype.INSTANT): TGeomPointInst,
        (MeosType.T_TGEOMPOINT, MeosTemporalSubtype.SEQUENCE): TGeomPointSeq,
        (MeosType.T_TGEOMPOINT, MeosTemporalSubtype.SEQUENCE_SET): TGeomPointSeqSet,
        (MeosType.T_TGEOGPOINT, MeosTemporalSubtype.INSTANT): TGeogPointInst,
        (MeosType.T_TGEOGPOINT, MeosTemporalSubtype.SEQUENCE): TGeogPointSeq,
        (MeosType.T_TGEOGPOINT, MeosTemporalSubtype.SEQUENCE_SET): TGeogPointSeqSet,
    }

    @staticmethod
    def create_temporal(inner):
        """
        Creates the appropriate PyMEOS Temporal class from a meos object.

        Args:
            inner: MEOS object.

        Returns:
            An instance of the appropriate subclass of :class:`Temporal` wrapping
            `inner`.
        """
        if inner is None:
            return None
        temp_type = (inner.temptype, inner.subtype)
        return _TemporalFactory._mapper[temp_type](_inner=inner)


class _CollectionFactory:
    """
    Factory class to create the proper PyMEOS collection class from a MEOS object.

    This class is used internally by PyMEOS classes and there shouldn't be any need
    to be used outside of them.
    """

    _mapper = {
        MeosType.T_GEOMSET: GeometrySet,
        MeosType.T_GEOGSET: GeographySet,
        MeosType.T_INTSET: IntSet,
        MeosType.T_INTSPAN: IntSpan,
        MeosType.T_INTSPANSET: IntSpanSet,
        MeosType.T_FLOATSET: FloatSet,
        MeosType.T_FLOATSPAN: FloatSpan,
        MeosType.T_FLOATSPANSET: FloatSpanSet,
        MeosType.T_TEXTSET: TextSet,
        MeosType.T_DATESET: DateSet,
        MeosType.T_DATESPAN: DateSpan,
        MeosType.T_DATESPANSET: DateSpanSet,
        MeosType.T_TSTZSET: TsTzSet,
        MeosType.T_TSTZSPAN: TsTzSpan,
        MeosType.T_TSTZSPANSET: TsTzSpanSet,
    }

    @staticmethod
    def create_collection(inner):
        """
        Creates the appropriate PyMEOS Collection class from a meos object.

        Args:
            inner: MEOS object.

        Returns:
            An instance of the appropriate subclass of :class:`Collection` wrapping
            `inner`.
        """
        if inner is None:
            return None

        attributes = ["spansettype", "spantype", "settype"]
        collection_type = next(
            getattr(inner, attribute)
            for attribute in attributes
            if hasattr(inner, attribute)
        )
        return _CollectionFactory._mapper[collection_type](_inner=inner)
