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


class _TemporalFactory:
    """
    Factory class to create the proper PyMEOS class from a MEOS object.

    This class is used internally by PyMEOS classes and there shouldn't be any need to be used outside of them.
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
            An appropriate subclass of :class:`Temporal` wrapping `inner`.
        """
        if inner is None:
            return None
        temp_type = (inner.temptype, inner.subtype)
        return _TemporalFactory._mapper[temp_type](_inner=inner)
