from copy import copy
from datetime import datetime, timezone, timedelta
from spans.types import intrange, floatrange

import pytest

from pymeos import TBox, TInterpolation, TimestampSet, Period, PeriodSet, \
    TInt, TIntInst, TIntSeq, TIntSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet

from tests.conftest import TestPyMEOS


class TestTBox(TestPyMEOS):

    @staticmethod
    def assert_tbox_equality(tbox: TBox,
                             xmin: float = None,
                             xmax: float = None,
                             tmin: datetime = None,
                             tmax: datetime = None,
                             xmin_inc: bool = None,
                             xmax_inc: bool = None,
                             tmin_inc: bool = None,
                             tmax_inc: bool = None):
        if xmin is not None:
            assert tbox.xmin() == xmin
        if xmax is not None:
            assert tbox.xmax() == xmax
        if tmin is not None:
            assert tbox.tmin() == tmin
        if tmax is not None:
            assert tbox.tmax() == tmax
        if xmin_inc is not None:
            assert tbox.xmin_inc() == xmin_inc
        if xmax_inc is not None:
            assert tbox.xmax_inc() == xmax_inc
        if tmin_inc is not None:
            assert tbox.tmin_inc() == tmin_inc
        if tmax_inc is not None:
            assert tbox.tmax_inc() == tmax_inc

class TestTBoxConstructors(TestTBox):
    tbx = TBox('TBOX X([1,2])')
    tbt = TBox('TBOX T([2019-09-01,2019-09-02])')
    tbxt = TBox('TBOX XT([1,2],[2019-09-01,2019-09-02])')

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('TBox X([1,2])', TBox, 'TBOX X([1, 2])'),
            ('TBox T([2019-09-01,2019-09-02])', TBox, 
             'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            ('TBox XT([1,2],[2019-09-01,2019-09-02])', TBox, 
             'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])')
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_string_constructor(self, source, type, expected):
        tb = type(source)
        assert isinstance(tb, type)
        assert str(tb) == expected

    # def test_hexwkb_constructor(self):
        # source = '010321000300A01E4E713402000000F66B85340200070003000000000000F03F0000000000000040'
        # tbox = TBox.from_hexwkb(source)
        # self.assert_tbox_equality(tbox, 1, 2, 
                                  # datetime(2019, 9, 1, tzinfo=timezone.utc),
                                  # datetime(2019, 9, 2, tzinfo=timezone.utc),
                                  # True, True, True, True)

    # @pytest.mark.parametrize(
        # 'time, expected',
        # [
            # (datetime(2019, 9, 1), 
                # 'TBOX T([2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (TimestampSet('{2019-09-01, 2019-09-02}'),
                # 'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (Period('[2019-09-01, 2019-09-02]'),
                # 'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'),
                # 'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        # ],
        # ids=['Timestamp', 'TimestampSet', 'Period', 'PeriodSet']
    # )
    # def test_from_time_constructor(self, time, expected):
        # tb = TBox.from_time(time)
        # assert isinstance(tb, TBox)
        # assert str(tb) == expected

    @pytest.mark.parametrize(
        'value, expected',
        [
            (1, 'TBOX X([1, 1])'),
            (1.5, 'TBOX X([1.5, 1.5])'),
            (intrange(1, 2, True, True), 'TBOX X([1, 2])'),
            (floatrange(1.5, 2.5, True, True), 'TBOX X([1.5, 2.5])'),
        ],
        ids=['int', 'float', 'intrange', 'floatrange']
    )
    def test_from_value_time_constructor(self, value, expected):
        tb = TBox.from_value(value)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    # @pytest.mark.parametrize(
        # 'value, time, expected',
        # [
            # (1, datetime(2019, 9, 1),
                # 'TBOX XT([1, 1],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (1.5, datetime(2019, 9, 1),
                # 'TBOX XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (intrange(1, 2, True, True), datetime(2019, 9, 1),
                # 'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (floatrange(1.5, 2.5, True, True), datetime(2019, 9, 1),
                # 'TBOX XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (1, Period('[2019-09-01, 2019-09-02]'),
                # 'TBOX XT([1, 1],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (1.5, Period('[2019-09-01, 2019-09-02]'),
                # 'TBOX XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (intrange(1, 2, True, True), Period('[2019-09-01, 2019-09-02]'),
                # 'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (floatrange(1.5, 2.5, True, True), Period('[2019-09-01, 2019-09-02]'),
                # 'TBOX XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        # ],
        # ids=['int-Timestamp', 'float-Timestamp', 'intrange-Timestamp', 'floatrange-Timestamp',
             # 'int-Period', 'float-Period', 'intrange-Period', 'floatrange-Period',]
    # )
    # def test_from_value_time_constructor(self, value, time, expected):
        # tb = TBox.from_value_time(value, time)
        # assert isinstance(tb, TBox)
        # assert str(tb) == expected

    @pytest.mark.parametrize(
        'tnumber, expected',
        [
            (TIntInst('1@2019-09-01'), 'TBOX XT([1, 1],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (TFloatInst('1.5@2019-09-01'), 'TBOX XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
        ],
        ids=['Tint', 'Tfloat']
    )
    def test_from_tnumber_constructor(self, tnumber, expected):
        tb = TBox.from_tnumber(tnumber)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        'tbox',
        [tbx, tbt, tbxt],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_from_as_hexwkb_constructor(self, tbox):
        assert tbox == tbox.from_hexwkb(tbox.as_hexwkb())

    @pytest.mark.parametrize(
        'tbox',
        [tbx, tbt, tbxt],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_copy_constructor(self, tbox):
        other = copy(tbox)
        assert tbox == other
        assert tbox is not other


class TestTBoxOutputs(TestTBox):
    tbx = TBox('TBOX X([1,2])')
    tbt = TBox('TBOX T([2019-09-01,2019-09-02])')
    tbxt = TBox('TBOX XT([1,2],[2019-09-01,2019-09-02])')
                                                                  
    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, 'TBOX X([1, 2])'),
            (tbt, 'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (tbxt, 'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_str(self, tbox, expected):
        assert str(tbox) == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, 'TBox(TBOX X([1, 2]))'),
            (tbt, 'TBox(TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))'),
            (tbxt, 'TBox(TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))'),
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_repr(self, tbox, expected):
        assert repr(tbox) == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, '0101070003000000000000F03F0000000000000040'),
            (tbt, '010221000300A01E4E713402000000F66B85340200'),
            (tbxt, '010321000300A01E4E713402000000F66B85340200070003000000000000F03F0000000000000040'),
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_as_hexwkb(self, tbox, expected):
        assert tbox.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'tbox',
        [tbx, tbt, tbxt],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_from_hexwkb_constructor(self, tbox):
        assert tbox == tbox.from_hexwkb(tbox.as_hexwkb())


class TestTBoxAccessors(TestTBox):
    tbx = TBox('TBox X([1,2])')
    tbt = TBox('TBox T([2019-09-01,2019-09-02])')
    tbxt = TBox('TBox XT([1,2],[2019-09-01,2019-09-02])')

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, True),
            (tbt, False),
            (tbxt, True)
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_has_x(self, tbox, expected):
        assert tbox.has_x() == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, False),
            (tbt, True),
            (tbxt, True)
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_has_t(self, tbox, expected):
        assert tbox.has_t() == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, 1),
            (tbt, None),
            (tbxt, 1)
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_xmin(self, tbox, expected):
        assert tbox.xmin() == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, 2),
            (tbt, None),
            (tbxt, 2)
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_xmax(self, tbox, expected):
        assert tbox.xmax() == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, None),
            (tbt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbxt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc))
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_tmin(self, tbox, expected):
        assert tbox.tmin() == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (tbx, None),
            (tbt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbxt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc))
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_tmax(self, tbox, expected):
        assert tbox.tmax() == expected

class TestTBoxOperators(TestTBox):
    tbx1 = TBox('TBox X([1,2])')
    tbt1 = TBox('TBox T([2019-09-01,2019-09-02])')
    tbxt1 = TBox('TBox XT([1,2],[2019-09-01,2019-09-02])')
    tbx2 = TBox('TBox X([2,3])')
    tbt2 = TBox('TBox T([2019-09-02,2019-09-03])')
    tbxt2 = TBox('TBox XT([2,3],[2019-09-02,2019-09-03])')

    @pytest.mark.parametrize(
        'tbox1, tbox2, expected',
        [
            (tbx1, tbx2, TBox('TBox X([1,3])')),
            (tbt1, tbt2, TBox('TBox T([2019-09-01,2019-09-03])')),
            (tbxt1, tbxt2, TBox('TBox XT([1,3],[2019-09-01,2019-09-03])'))
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_add(self, tbox1, tbox2, expected):
        assert tbox1 + tbox2 == expected

    @pytest.mark.parametrize(
        'tbox1, tbox2, expected',
        [
            (tbx1, tbx2, TBox('TBox X([2,2])')),
            (tbt1, tbt2, TBox('TBox T([2019-09-02,2019-09-02])')),
            (tbxt1, tbxt2, TBox('TBox XT([2,2],[2019-09-02,2019-09-02])'))
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_mul(self, tbox1, tbox2, expected):
        assert tbox1 * tbox2 == expected

