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
    TNpointInst,
    TNpointSeq,
    TNpointSeqSet,
    TCbufferInst,
    TCbufferSeq,
    TCbufferSeqSet,
    TPoseInst,
    TPoseSeq,
    TPoseSeqSet,
    TRgeometryInst,
    TRgeometrySeq,
    TRgeometrySeqSet,
)
from .collections import (
    GeometrySet,
    GeographySet,
    NpointSet,
    CbufferSet,
    PoseSet,
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

try:  # the compiled binding (same source pymeos_cffi's own enums use)
    from _meos_cffi import lib as _meos_lib
except Exception:  # pragma: no cover - the binding is present at runtime
    _meos_lib = None


def _meos_type(name: str):
    """Return the MEOS type tag for ``name``.

    Robust to ``pymeos_cffi`` not yet wrapping a valid, compiled MEOS type
    tag in its ``MeosType`` enum: prefer the exposed enum member, else read
    the constant from the compiled binding (``_meos_cffi.lib`` — the very
    source ``pymeos_cffi`` builds its enums from), else ``None`` so the
    mapping is skipped and importing never fails.  ``MeosType`` is an
    ``IntEnum``, so an ``int`` key matches ``inner.temptype`` lookups
    identically to an enum-keyed one.
    """
    member = getattr(MeosType, name, None)
    if member is not None:
        return member
    if _meos_lib is not None and hasattr(_meos_lib, name):
        return int(getattr(_meos_lib, name))
    return None


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


# Extended temporal type families (cbuffer, npoint, pose, rgeo) are full
# user-facing temporal types and are wired exactly like every other type.
# Registered post-hoc through `_meos_type` so a build whose `pymeos_cffi`
# does not yet wrap these (valid, compiled) tags in its `MeosType` enum
# still imports cleanly and activates them automatically.
for _tag, _inst, _seq, _seqset in (
    ("T_TNPOINT", TNpointInst, TNpointSeq, TNpointSeqSet),
    ("T_TCBUFFER", TCbufferInst, TCbufferSeq, TCbufferSeqSet),
    ("T_TPOSE", TPoseInst, TPoseSeq, TPoseSeqSet),
    ("T_TRGEOMETRY", TRgeometryInst, TRgeometrySeq, TRgeometrySeqSet),
):
    _k = _meos_type(_tag)
    if _k is not None:
        _TemporalFactory._mapper[(_k, MeosTemporalSubtype.INSTANT)] = _inst
        _TemporalFactory._mapper[(_k, MeosTemporalSubtype.SEQUENCE)] = _seq
        _TemporalFactory._mapper[(_k, MeosTemporalSubtype.SEQUENCE_SET)] = (
            _seqset
        )

for _tag, _cls in (
    ("T_NPOINTSET", NpointSet),
    ("T_CBUFFERSET", CbufferSet),
    ("T_POSESET", PoseSet),
):
    _k = _meos_type(_tag)
    if _k is not None:
        _CollectionFactory._mapper[_k] = _cls
