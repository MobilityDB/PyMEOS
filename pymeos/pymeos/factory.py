from enum import Enum

from .main import TBoolInst, TBoolSeq, TBoolSeqSet, \
    TIntInst, TIntSeq, TIntSeqSet, \
    TFloatInst, TFloatSeq, TFloatSeqSet, \
    TTextInst, TTextSeq, TTextSeqSet, \
    TGeomPointInst, TGeomPointSeq, TGeomPointSeqSet, \
    TGeogPointInst, TGeogPointSeq, TGeogPointSeqSet


class TempType(Enum):
    BOOL = 1
    FLOAT = 2
    INT = 3
    TEXT = 4
    GG_POINT = 5
    GM_POINT = 6

    INSTANT = 10
    INSTANT_SET = 11
    SEQUENCE = 12
    SEQUENCE_SET = 13

    @classmethod
    def get_temp_type(cls, c):
        temp_type = c.temptype
        if temp_type == 12:
            return cls.BOOL
        elif temp_type == 18:
            return cls.FLOAT
        elif temp_type == 21:
            return cls.INT
        elif temp_type == 22:
            return cls.TEXT
        elif temp_type == 25:
            return cls.GM_POINT
        elif temp_type == 26:
            return cls.GG_POINT
        raise Exception(f'Invalid temporal type: {temp_type}. Valid temporal types are: 12 (bool), 18 (float), '
                        f'21 (int), 22 (text), 25 (geometric point) and 26 (geographical point).')

    @classmethod
    def get_sub_type(cls, c):
        subtype = c.subtype
        if subtype == 1:
            return cls.INSTANT
        elif subtype == 2:
            return cls.SEQUENCE
        elif subtype == 3:
            return cls.SEQUENCE_SET
        raise Exception(
            f'Invalid subtype: {subtype}. Valid subtypes are: 1 (Instant), 2 (Sequence) and 3 (Sequence Set)')

    @classmethod
    def get_type(cls, c):
        return TempType.get_temp_type(c), TempType.get_sub_type(c)


class _TemporalFactory:
    _mapper = {
        (TempType.BOOL, TempType.INSTANT): TBoolInst,
        (TempType.BOOL, TempType.SEQUENCE): TBoolSeq,
        (TempType.BOOL, TempType.SEQUENCE_SET): TBoolSeqSet,

        (TempType.INT, TempType.INSTANT): TIntInst,
        (TempType.INT, TempType.SEQUENCE): TIntSeq,
        (TempType.INT, TempType.SEQUENCE_SET): TIntSeqSet,

        (TempType.FLOAT, TempType.INSTANT): TFloatInst,
        (TempType.FLOAT, TempType.SEQUENCE): TFloatSeq,
        (TempType.FLOAT, TempType.SEQUENCE_SET): TFloatSeqSet,

        (TempType.TEXT, TempType.INSTANT): TTextInst,
        (TempType.TEXT, TempType.SEQUENCE): TTextSeq,
        (TempType.TEXT, TempType.SEQUENCE_SET): TTextSeqSet,

        (TempType.GM_POINT, TempType.INSTANT): TGeomPointInst,
        (TempType.GM_POINT, TempType.SEQUENCE): TGeomPointSeq,
        (TempType.GM_POINT, TempType.SEQUENCE_SET): TGeomPointSeqSet,

        (TempType.GG_POINT, TempType.INSTANT): TGeogPointInst,
        (TempType.GG_POINT, TempType.SEQUENCE): TGeogPointSeq,
        (TempType.GG_POINT, TempType.SEQUENCE_SET): TGeogPointSeqSet,
    }

    @staticmethod
    def create_temporal(inner):
        if inner is None:
            return None
        temp_type = TempType.get_type(inner)
        return _TemporalFactory._mapper[temp_type](_inner=inner)
