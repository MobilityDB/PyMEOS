from enum import Enum

from .main import TBoolInst, TBoolSeq, TBoolSeqSet, \
    TIntInst, TIntSeq, TIntSeqSet, \
    TFloatInst, TFloatSeq, TFloatSeqSet, \
    TTextInst, TTextSeq, TTextSeqSet, \
    TGeomPointInst, TGeomPointSeq, TGeomPointSeqSet, \
    TGeogPointInst, TGeogPointSeq, TGeogPointSeqSet


class TempType(Enum):
    """
    Enum for representing the different base/temporal types present in MEOS.

    This class is used internally by PyMEOS classes and there shouldn't be any need to be used outside of them.
    """
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
        """
        Return the temporal type of `c`.

        Args:
            c: MEOS object.

        Returns:
            A :class:`TempType` representing the temporal type (int, float, bool, etc.).
        """
        temp_type = c.temptype
        if temp_type == 20:
            return cls.BOOL
        elif temp_type == 27:
            return cls.FLOAT
        elif temp_type == 29:
            return cls.INT
        elif temp_type == 35:
            return cls.TEXT
        elif temp_type == 40:
            return cls.GM_POINT
        elif temp_type == 41:
            return cls.GG_POINT
        raise Exception(f'Invalid temporal type: {temp_type}. Valid temporal types are: 12 (bool), 18 (float), '
                        f'21 (int), 22 (text), 25 (geometric point) and 26 (geographical point).')

    @classmethod
    def get_sub_type(cls, c):
        """
        Return the temporal subtype of `c`.

        Args:
            c: MEOS object.

        Returns:
            A :class:`TempType` representing the temporal subtype (instant, sequence or sequenceSet).
        """
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
        """
        Return the temporal MEOS type of `c` as a tuple of temporal type and subtype.

        Args:
            c: MEOS object.

        Returns:
            Tuple of two :class:`TempType` representing the temporal type (int, float, bool, etc.) and the temporal
             subtype (instant, sequence or sequenceSet).
        """
        return TempType.get_temp_type(c), TempType.get_sub_type(c)


class _TemporalFactory:
    """
    Factory class to create the proper PyMEOS class from a MEOS object.

    This class is used internally by PyMEOS classes and there shouldn't be any need to be used outside of them.
    """
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
        """
        Creates the appropriate PyMEOS Temporal class from a meos object.

        Args:
            inner: MEOS object.

        Returns:
            An appropriate subclass of :class:`Temporal` wrapping `inner`.
        """
        if inner is None:
            return None
        temp_type = TempType.get_type(inner)
        return _TemporalFactory._mapper[temp_type](_inner=inner)
