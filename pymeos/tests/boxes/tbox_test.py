from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import (
    TBox,
    TInterpolation,
    TimestampSet,
    Period,
    PeriodSet,
    IntSpan,
    FloatSpan,
    TInt,
    TIntInst,
    TIntSeq,
    TIntSeqSet,
    TFloat,
    TFloatInst,
    TFloatSeq,
    TFloatSeqSet,
)

from tests.conftest import TestPyMEOS


class TestTBox(TestPyMEOS):
    @staticmethod
    def assert_tbox_equality(
        tbox: TBox,
        xmin: float = None,
        xmax: float = None,
        tmin: datetime = None,
        tmax: datetime = None,
        xmin_inc: bool = None,
        xmax_inc: bool = None,
        tmin_inc: bool = None,
        tmax_inc: bool = None,
    ):
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
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")

    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    tbix = TBox("TBOXINT X([1,2])")
    tbixt = TBox("TBOXINT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "source, expected",
        [
            ("TBOX T([2019-09-01,2019-09-02])", tbt),
            ("TBOXFLOAT X([1,2])", tbfx),
            ("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])", tbfxt),
            ("TBOXINT X([1,2])", tbix),
            ("TBOXINT XT([1,2],[2019-09-01,2019-09-02])", tbixt),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_string_constructor(self, source, expected):
        tb = TBox(source)
        assert isinstance(tb, TBox)
        assert tb == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                {"tmin": "2019-09-01", "tmax": datetime(2019, 9, 2), "tmax_inc": True},
                tbt,
            ),
            ({"xmin": "1", "xmax": 2.0, "xmax_inc": True}, tbfx),
            (
                {
                    "tmin": "2019-09-01",
                    "tmax": datetime(2019, 9, 2),
                    "tmax_inc": True,
                    "xmin": "1",
                    "xmax": 2.0,
                    "xmax_inc": True,
                },
                tbfxt,
            ),
            ({"xmin": 1, "xmax": 2, "xmax_inc": True}, tbix),
            (
                {
                    "tmin": "2019-09-01",
                    "tmax": datetime(2019, 9, 2),
                    "tmax_inc": True,
                    "xmin": 1,
                    "xmax": 2,
                    "xmax_inc": True,
                },
                tbixt,
            ),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_values_constructor(self, args, expected):
        tb = TBox(**args)
        assert isinstance(tb, TBox)
        assert tb == expected

    def test_hexwkb_constructor(self):
        source = (
            "010321000300A01E4E713402000000F66B85340200070003000000000000F03F"
            "0000000000000040"
        )
        tbox = TBox.from_hexwkb(source)
        assert isinstance(tbox, TBox)
        assert tbox == self.tbfxt

    @pytest.mark.parametrize(
        "value, expected",
        [
            (1, "TBOXINT X([1, 2))"),
            (1.5, "TBOXFLOAT X([1.5, 1.5])"),
            (IntSpan("[1, 2]"), "TBOXINT X([1, 3))"),
            (FloatSpan("[1.5, 2.5]"), "TBOXFLOAT X([1.5, 2.5])"),
        ],
        ids=["int", "float", "IntSpan", "FloatSpan"],
    )
    def test_from_value_constructor(self, value, expected):
        tb = TBox.from_value(value)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        "time, expected",
        [
            (
                datetime(2019, 9, 1),
                "TBOX T([2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TimestampSet("{2019-09-01, 2019-09-02}"),
                "TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                Period("[2019-09-01, 2019-09-02]"),
                "TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                PeriodSet("{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}"),
                "TBOX T([2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
        ],
        ids=["Timestamp", "TimestampSet", "Period", "PeriodSet"],
    )
    def test_from_time_constructor(self, time, expected):
        tb = TBox.from_time(time)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        "value, time, expected",
        [
            (
                1,
                datetime(2019, 9, 1),
                "TBOXINT XT([1, 2),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                1.5,
                datetime(2019, 9, 1),
                "TBOXFLOAT XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                IntSpan(lower=1, upper=2, lower_inc=True, upper_inc=True),
                datetime(2019, 9, 1),
                "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                FloatSpan(lower=1.5, upper=2.5, lower_inc=True, upper_inc=True),
                datetime(2019, 9, 1),
                "TBOXFLOAT XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                1,
                Period("[2019-09-01, 2019-09-02]"),
                "TBOXINT XT([1, 2),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                1.5,
                Period("[2019-09-01, 2019-09-02]"),
                "TBOXFLOAT XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                IntSpan(lower=1, upper=2, lower_inc=True, upper_inc=True),
                Period("[2019-09-01, 2019-09-02]"),
                "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                FloatSpan(lower=1.5, upper=2.5, lower_inc=True, upper_inc=True),
                Period("[2019-09-01, 2019-09-02]"),
                "TBOXFLOAT XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=[
            "int-Timestamp",
            "float-Timestamp",
            "IntSpan-Timestamp",
            "FloatSpan-Timestamp",
            "int-Period",
            "float-Period",
            "IntSpan-Period",
            "FloatSpan-Period",
        ],
    )
    def test_from_value_time_constructor(self, value, time, expected):
        tb = TBox.from_value_time(value, time)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        "tnumber, expected",
        [
            (
                TIntInst("1@2019-09-01"),
                "TBOXINT XT([1, 2),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TIntSeq("{1@2019-09-01,2@2019-09-02}"),
                "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TIntSeq("(1@2019-09-01,2@2019-09-02]"),
                "TBOXINT XT([1, 3),(2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TIntSeqSet("{(1@2019-09-01,2@2019-09-02],(1@2019-09-03,2@2019-09-05]}"),
                "TBOXINT XT([1, 3),(2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
            (
                TFloatInst("1.5@2019-09-01"),
                "TBOXFLOAT XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TFloatSeq("{1.5@2019-09-01,2.5@2019-09-02}"),
                "TBOXFLOAT XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TFloatSeq("[1.5@2019-09-01,2.5@2019-09-02)"),
                "TBOXFLOAT XT([1.5, 2.5),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00))",
            ),
            (
                TFloatSeqSet(
                    "{[1.5@2019-09-01,2.5@2019-09-02),[1.5@2019-09-03,1.5@2019-09-05)}"
                ),
                "TBOXFLOAT XT([1.5, 2.5),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00))",
            ),
        ],
        ids=[
            "TInt Instant",
            "TInt Discrete Sequence",
            "TInt Sequence",
            "TInt Sequence Set",
            "TFloat Instant",
            "TFloat Discrete Sequence",
            "TFloat Sequence",
            "TFloat Sequence Set",
        ],
    )
    def test_from_tnumber_constructor(self, tnumber, expected):
        tb = TBox.from_tnumber(tnumber)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        "tbox", [tbfx, tbt, tbfxt], ids=["TBoxFloat X", "TBox T", "TBoxFloat XT"]
    )
    def test_from_as_constructor(self, tbox):
        assert tbox == TBox(str(tbox))
        assert tbox == tbox.from_wkb(tbox.as_wkb())
        assert tbox == tbox.from_hexwkb(tbox.as_hexwkb())

    @pytest.mark.parametrize(
        "tbox", [tbfx, tbt, tbfxt], ids=["TBoxFloat X", "TBox T", "TBoxFloat XT"]
    )
    def test_copy_constructor(self, tbox):
        other = copy(tbox)
        assert tbox == other
        assert tbox is not other

    @pytest.mark.parametrize(
        "constructor, args",
        [
            (TBox.from_value, (None,)),
            (TBox.from_time, (None,)),
            (TBox.from_value_time, (None, None)),
        ],
        ids=["from_value", "from_time", "from_value_time"],
    )
    def test_wrong_type_in_constructors(self, constructor, args):
        with pytest.raises(TypeError):
            constructor(*args)


class TestTBoxOutputs(TestTBox):
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")

    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    tbix = TBox("TBOXINT X([1,2])")
    tbixt = TBox("TBOXINT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, "TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"),
            (tbfx, "TBOXFLOAT X([1, 2])"),
            (
                tbfxt,
                "TBOXFLOAT XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (tbix, "TBOXINT X([1, 3))"),
            (
                tbixt,
                "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_str(self, tbox, expected):
        assert str(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, "TBox(TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))"),
            (tbfx, "TBox(TBOXFLOAT X([1, 2]))"),
            (
                tbfxt,
                "TBox(TBOXFLOAT XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))",
            ),
            (tbix, "TBox(TBOXINT X([1, 3)))"),
            (
                tbixt,
                "TBox(TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))",
            ),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_repr(self, tbox, expected):
        assert repr(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, "010221000300A01E4E713402000000F66B85340200"),
            (tbfx, "0101070003000000000000F03F0000000000000040"),
            (
                tbfxt,
                "010321000300A01E4E713402000000F66B85340200070003000000000000F03F0000000000000040",
            ),
            (tbix, "01010D00010100000003000000"),
            (tbixt, "010321000300A01E4E713402000000F66B853402000D00010100000003000000"),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_as_hexwkb(self, tbox, expected):
        assert tbox.as_hexwkb() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbfx, FloatSpan(lower=1.0, upper=2.0, lower_inc=True, upper_inc=True)),
            (tbfxt, FloatSpan(lower=1.0, upper=2.0, lower_inc=True, upper_inc=True)),
            (tbix, FloatSpan(lower=1.0, upper=2.0, lower_inc=True, upper_inc=True)),
            (tbixt, FloatSpan(lower=1.0, upper=2.0, lower_inc=True, upper_inc=True)),
        ],
        ids=["TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_to_floatspan(self, tbox, expected):
        tb = tbox.to_floatspan()
        assert isinstance(tb, FloatSpan)
        assert tb == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, Period("[2019-09-01, 2019-09-02]")),
            (tbfxt, Period("[2019-09-01, 2019-09-02]")),
            (tbixt, Period("[2019-09-01, 2019-09-02]")),
        ],
        ids=["TBox T", "TBoxFloat XT", "TBoxInt XT"],
    )
    def test_to_period(self, tbox, expected):
        tb = tbox.to_period()
        assert isinstance(tb, Period)
        assert tb == expected


class TestTBoxAccessors(TestTBox):
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")

    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    tbix = TBox("TBOXINT X([1,2])")
    tbixt = TBox("TBOXINT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, False), (tbfx, True), (tbfxt, True), (tbix, True), (tbixt, True)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_has_x(self, tbox, expected):
        assert tbox.has_x() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, True), (tbfx, False), (tbfxt, True), (tbix, False), (tbixt, True)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_has_t(self, tbox, expected):
        assert tbox.has_t() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, None), (tbfx, 1), (tbfxt, 1), (tbix, 1), (tbixt, 1)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_xmin(self, tbox, expected):
        assert tbox.xmin() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, None), (tbfx, True), (tbfxt, True), (tbix, True), (tbixt, True)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_xmin_inc(self, tbox, expected):
        assert tbox.xmin_inc() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbfx, 2), (tbt, None), (tbfxt, 2)],
        ids=["TBoxFloat X", "TBox T", "TBoxFloat XT"],
    )
    def test_xmax(self, tbox, expected):
        assert tbox.xmax() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, None), (tbfx, True), (tbfxt, True), (tbix, False), (tbixt, False)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_xmax_inc(self, tbox, expected):
        assert tbox.xmax_inc() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbfx, None),
            (tbfxt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbix, None),
            (tbixt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_tmin(self, tbox, expected):
        assert tbox.tmin() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, True), (tbfx, None), (tbfxt, True), (tbix, None), (tbixt, True)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_tmin_inc(self, tbox, expected):
        assert tbox.tmin_inc() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbfx, None),
            (tbfxt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbix, None),
            (tbixt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
        ],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_tmax(self, tbox, expected):
        assert tbox.tmax() == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [(tbt, True), (tbfx, None), (tbfxt, True), (tbix, None), (tbixt, True)],
        ids=["TBox T", "TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_tmax_inc(self, tbox, expected):
        assert tbox.tmax_inc() == expected


class TestTBoxTransformations(TestTBox):
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")

    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    tbix = TBox("TBOXINT X([1,2])")
    tbixt = TBox("TBOXINT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([0, 3])")),
            (tbfxt, TBox("TBOXFLOAT XT([0,3],[2019-09-01, 2019-09-02])")),
            (tbix, TBox("TBOXINT X([0, 4))")),
            (tbixt, TBox("TBOXINT XT([0,4),[2019-09-01, 2019-09-02])")),
        ],
        ids=["TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_expand_float(self, tbox, expected):
        tb = tbox.expand(1)
        assert isinstance(tb, TBox)
        assert tb == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (tbt, TBox("TBOX T([2019-08-31, 2019-09-03])")),
            (tbfxt, TBox("TBOXFLOAT XT([1,2],[2019-08-31, 2019-09-03])")),
            (tbixt, TBox("TBOXINT XT([1,3),[2019-08-31, 2019-09-03])")),
        ],
        ids=["TBox T", "TBoxFloat XT", "TBoxInt XT"],
    )
    def test_expand_time(self, tbox, expected):
        tb = tbox.expand(timedelta(days=1))
        assert isinstance(tb, TBox)
        assert tb == expected

    @pytest.mark.parametrize(
        "tbox, delta, expected",
        [
            (tbfx, 2.0, TBox("TBOXFLOAT X([3,4])")),
            (tbfx, -2.0, TBox("TBOXFLOAT X([-1,0])")),
            (tbfxt, 2.0, TBox("TBOXFLOAT XT([3,4],[2019-09-01, 2019-09-02])")),
            (tbfxt, -2.0, TBox("TBOXFLOAT XT([-1,0],[2019-09-01, 2019-09-02])")),
            (tbix, 2.0, TBox("TBOXINT X([3,5))")),
            (tbix, -2.0, TBox("TBOXINT X([-1,1))")),
            (tbixt, 2.0, TBox("TBOXINT XT([3,5),[2019-09-01, 2019-09-02])")),
            (tbixt, -2.0, TBox("TBOXINT XT([-1,1),[2019-09-01, 2019-09-02])")),
        ],
        ids=[
            "TBox T positive",
            "TBox T negative",
            "TBoxFloat XT positive",
            "TBoxFloat XT negative",
            "TBoxInt X positive",
            "TBoxInt X negative",
            "TBoxInt XT positive",
            "TBoxInt XT negative",
        ],
    )
    def test_shift_value(self, tbox, delta, expected):
        assert tbox.shift_value(delta) == expected

    @pytest.mark.parametrize(
        "tbox, delta, expected",
        [
            (tbt, timedelta(days=4), TBox("TBOX T([2019-09-05,2019-09-06])")),
            (tbt, timedelta(days=-4), TBox("TBOX T([2019-08-28,2019-08-29])")),
            (
                tbt,
                timedelta(hours=2),
                TBox("TBOX T([2019-09-01 02:00:00,2019-09-02 02:00:00])"),
            ),
            (
                tbt,
                timedelta(hours=-2),
                TBox("TBOX T([2019-08-31 22:00:00,2019-09-01 22:00:00])"),
            ),
            (
                tbfxt,
                timedelta(days=4),
                TBox("TBOXFLOAT XT([1, 2],[2019-09-05, 2019-09-06])"),
            ),
            (
                tbfxt,
                timedelta(days=-4),
                TBox("TBOXFLOAT XT([1, 2],[2019-08-28, 2019-08-29])"),
            ),
            (
                tbfxt,
                timedelta(hours=2),
                TBox(
                    "TBOXFLOAT XT([1, 2],"
                    "[2019-09-01 02:00:00+00, 2019-09-02 02:00:00+00])"
                ),
            ),
            (
                tbfxt,
                timedelta(hours=-2),
                TBox(
                    "TBOXFLOAT XT([1, 2],"
                    "[2019-08-31 22:00:00+00, 2019-09-01 22:00:00+00])"
                ),
            ),
            (
                tbixt,
                timedelta(days=4),
                TBox("TBOXINT XT([1, 3),[2019-09-05, 2019-09-06])"),
            ),
            (
                tbixt,
                timedelta(days=-4),
                TBox("TBOXINT XT([1, 3),[2019-08-28, 2019-08-29])"),
            ),
            (
                tbixt,
                timedelta(hours=2),
                TBox(
                    "TBOXINT XT([1, 3),"
                    "[2019-09-01 02:00:00+00, 2019-09-02 02:00:00+00])"
                ),
            ),
            (
                tbixt,
                timedelta(hours=-2),
                TBox(
                    "TBOXINT XT([1, 3),"
                    "[2019-08-31 22:00:00+00, 2019-09-01 22:00:00+00])"
                ),
            ),
        ],
        ids=[
            "TBox T positive days",
            "TBox T negative days",
            "TBox T positive hours",
            "TBox T negative hours",
            "TBoxFloat XT positive days",
            "TBoxFloat XT negative days",
            "TBoxFloat XT positive hours",
            "TBoxFloat XT negative hours",
            "TBoxInt XT positive days",
            "TBoxInt XT negative days",
            "TBoxInt XT positive hours",
            "TBoxInt XT negative hours",
        ],
    )
    def test_shift_time(self, tbox, delta, expected):
        assert tbox.shift_time(delta) == expected

    @pytest.mark.parametrize(
        "tbox, delta, expected",
        [
            (tbfx, 4.0, TBox("TBOXFLOAT X([1,5])")),
            (tbfxt, 4.0, TBox("TBOXFLOAT XT([1,5],[2019-09-01, 2019-09-02])")),
            (tbix, 4.0, TBox("TBOXINT X([1,6))")),
            (tbixt, 4.0, TBox("TBOXINT XT([1,6),[2019-09-01, 2019-09-02])")),
        ],
        ids=["TBox T", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_scale_value(self, tbox, delta, expected):
        assert tbox.scale_value(delta) == expected

    @pytest.mark.parametrize(
        "tbox, delta, expected",
        [
            (tbt, timedelta(days=4), TBox("TBOX T([2019-09-01,2019-09-05])")),
            (tbt, timedelta(hours=2), TBox("TBOX T([2019-09-01,2019-09-01 02:00:00])")),
            (
                tbfxt,
                timedelta(days=4),
                TBox(
                    "TBOXFLOAT XT([1, 2],"
                    "[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])"
                ),
            ),
            (
                tbfxt,
                timedelta(hours=2),
                TBox(
                    "TBOXFLOAT XT([1, 2],"
                    "[2019-09-01 00:00:00+00, 2019-09-01 02:00:00+00])"
                ),
            ),
            (
                tbixt,
                timedelta(days=4),
                TBox(
                    "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])"
                ),
            ),
            (
                tbixt,
                timedelta(hours=2),
                TBox(
                    "TBOXINT XT([1, 3),[2019-09-01 00:00:00+00, 2019-09-01 02:00:00+00])"
                ),
            ),
        ],
        ids=[
            "TBox T days",
            "TBox T hours",
            "TBoxFloat XT days",
            "TBoxFloat XT hours",
            "TBoxInt XT days",
            "TBoxInt XT hours",
        ],
    )
    def test_scale_time(self, tbox, delta, expected):
        assert tbox.scale_time(delta) == expected

    @pytest.mark.parametrize(
        "tbox, delta, width, expected",
        [
            (tbfx, 2.0, 4.0, TBox("TBOXFLOAT X([3,7])")),
            (tbfx, -2.0, 4.0, TBox("TBOXFLOAT X([-1,3])")),
            (tbfxt, 2.0, 4.0, TBox("TBOXFLOAT XT([3,7],[2019-09-01, 2019-09-02])")),
            (tbfxt, -2.0, 4.0, TBox("TBOXFLOAT XT([-1,3],[2019-09-01, 2019-09-02])")),
            (tbix, 2.0, 4.0, TBox("TBOXINT X([3,8))")),
            (tbix, -2.0, 4.0, TBox("TBOXINT X([-1,4))")),
            (tbixt, 2.0, 4.0, TBox("TBOXINT XT([3,8),[2019-09-01, 2019-09-02])")),
            (tbixt, -2.0, 4.0, TBox("TBOXINT XT([-1,4),[2019-09-01, 2019-09-02])")),
        ],
        ids=[
            "TBoxFloat X positive",
            "TBoxFloat X negative",
            "TBoxFloat XT positive",
            "TBoxFloat XT negative",
            "TBoxInt X positive",
            "TBoxInt X negative",
            "TBoxInt XT positive",
            "TBoxInt XT negative",
        ],
    )
    def test_shift_scale_value(self, tbox, delta, width, expected):
        assert tbox.shift_scale_value(delta, width) == expected

    @pytest.mark.parametrize(
        "tbox, delta, duration, expected",
        [
            (
                tbt,
                timedelta(days=2),
                timedelta(days=4),
                TBox("TBOX T([2019-09-03, 2019-09-07])"),
            ),
            (
                tbt,
                timedelta(days=-2),
                timedelta(days=4),
                TBox("TBOX T([2019-08-30, 2019-09-03])"),
            ),
            (
                tbfxt,
                timedelta(days=2),
                timedelta(days=4),
                TBox("TBOXFLOAT XT([1, 2],[2019-09-03, 2019-09-07])"),
            ),
            (
                tbfxt,
                timedelta(days=-2),
                timedelta(days=4),
                TBox("TBOXFLOAT XT([1, 2],[2019-08-30, 2019-09-03])"),
            ),
            (
                tbixt,
                timedelta(days=2),
                timedelta(days=4),
                TBox("TBOXINT XT([1, 3),[2019-09-03, 2019-09-07])"),
            ),
            (
                tbixt,
                timedelta(days=-2),
                timedelta(days=4),
                TBox("TBOXINT XT([1, 3),[2019-08-30, 2019-09-03])"),
            ),
        ],
        ids=[
            "TBox T positive",
            "TBox T negative",
            "TBoxFloat XT positive",
            "TBoxFloat XT negative",
            "TBoxInt XT positive",
            "TBoxInt XT negative",
        ],
    )
    def test_shift_scale_time(self, tbox, delta, duration, expected):
        assert tbox.shift_scale_time(delta, duration) == expected

    @pytest.mark.parametrize(
        "tbox, expected",
        [
            (
                TBox("TBOXFLOAT X([1.123456789,2.123456789])"),
                TBox("TBOXFLOAT X([1.12,2.12])"),
            ),
            (
                TBox(
                    "TBOXFLOAT XT([1.123456789,2.123456789],[2019-09-01, 2019-09-02])"
                ),
                TBox("TBOXFLOAT XT([1.12,2.12],[2019-09-01, 2019-09-03])"),
            ),
            (
                TBox("TBOXINT X([1,2])"),
                TBox("TBOXINT X([1,2])"),
            ),
            (
                TBox("TBOXINT XT([1,2],[2019-09-01, 2019-09-02])"),
                TBox("TBOXINT XT([1,2],[2019-09-01, 2019-09-03])"),
            ),
        ],
        ids=["TBoxFloat X", "TBoxFloat XT", "TBoxInt X", "TBoxInt XT"],
    )
    def test_round(self, tbox, expected):
        assert tbox.round(max_decimals=2)


class TestTBoxTopologicalFunctions(TestTBox):
    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([1,3])"), False),
            (tbfx, TBox("TBOXFLOAT X((2,3])"), True),
            (tbt, TBox("TBOX T([2019-09-01,2019-09-03])"), False),
            (tbt, TBox("TBOX T((2019-09-02,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT((2,3],[2019-09-02,2019-09-03])"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBox T False",
            "TBox T True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
        ],
    )
    def test_is_adjacent(self, tbox, argument, expected):
        assert tbox.is_adjacent(argument) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([2,3])"), False),
            (tbfx, TBox("TBOXFLOAT X([1,3])"), True),
            (tbt, TBox("TBOX T([2019-09-02,2019-09-03])"), False),
            (tbt, TBox("TBOX T([2019-09-01,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([2,3],[2019-09-02,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBox T False",
            "TBox T True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
        ],
    )
    def test_is_contained_in_contains(self, tbox, argument, expected):
        assert tbox.is_contained_in(argument) == expected
        assert argument.contains(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([3,3])"), False),
            (tbfx, TBox("TBOXFLOAT X([1,3])"), True),
            (tbt, TBox("TBOX T([2019-09-03,2019-09-03])"), False),
            (tbt, TBox("TBOX T([2019-09-01,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([3,3],[2019-09-02,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBox T False",
            "TBox T True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
        ],
    )
    def test_overlaps(self, tbox, argument, expected):
        assert tbox.overlaps(argument) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([3,3])"), False),
            (tbfx, TBox("TBOXFLOAT X([1,2])"), True),
            (tbt, TBox("TBOX T([2019-09-03,2019-09-03])"), False),
            (tbt, TBox("TBOX T([2019-09-01,2019-09-02])"), True),
            (tbfxt, TBox("TBOXFLOAT X([3,3])"), False),
            (tbfxt, TBox("TBOXFLOAT X([1,2])"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBox T False",
            "TBox T True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
        ],
    )
    def test_is_same(self, tbox, argument, expected):
        assert tbox.is_same(argument) == expected


class TestTBoxPositionFunctions(TestTBox):
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")

    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    tbix = TBox("TBOXINT X([1,2])")
    tbixt = TBox("TBOXINT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([1,3])"), False),
            (tbfx, TBox("TBOXFLOAT X([3,4])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-02,2019-09-03])"), True),
            (tbix, TBox("TBOXINT X([1,3])"), False),
            (tbix, TBox("TBOXINT X([3,4])"), True),
            (tbixt, TBox("TBOXINT XT([1,3],[2019-09-01,2019-09-03])"), False),
            (tbixt, TBox("TBOXINT XT([3,4],[2019-09-02,2019-09-03])"), True),
            (tbfx, TFloatSeq("[1@2019-09-01, 3@2019-09-03]"), False),
            (tbfx, TFloatSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbfxt, TFloatSeq("[1@2019-09-01, 3@2019-09-03]"), False),
            (tbfxt, TFloatSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbix, TIntSeq("[1@2019-09-01, 3@2019-09-03]"), False),
            (tbix, TIntSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbixt, TIntSeq("[1@2019-09-01, 3@2019-09-03]"), False),
            (tbixt, TIntSeq("[3@2019-09-01, 4@2019-09-03]"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
            "TBoxInt X False",
            "TBoxInt X True",
            "TBoxInt XT False",
            "TBoxInt XT True",
            "TFloat X False",
            "TFloat X True",
            "TFloat XT False",
            "TFloat XT True",
            "TInt X False",
            "TInt X True",
            "TInt XT False",
            "TInt XT True",
        ],
    )
    def test_is_left_right(self, tbox, argument, expected):
        assert tbox.is_left(argument) == expected
        assert argument.is_right(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([1,1])"), False),
            (tbfx, TBox("TBOXFLOAT X([3,4])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,1],[2019-09-01,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-02,2019-09-03])"), True),
            (tbix, TBox("TBOXINT X([1,1])"), False),
            (tbix, TBox("TBOXINT X([3,4])"), True),
            (tbixt, TBox("TBOXINT XT([1,1],[2019-09-01,2019-09-03])"), False),
            (tbixt, TBox("TBOXINT XT([3,4],[2019-09-02,2019-09-03])"), True),
            (tbfx, TFloatSeq("[1@2019-09-01, 1@2019-09-03]"), False),
            (tbfx, TFloatSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbfxt, TFloatSeq("[1@2019-09-01, 1@2019-09-03]"), False),
            (tbfxt, TFloatSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbix, TIntSeq("[1@2019-09-01, 1@2019-09-03]"), False),
            (tbix, TIntSeq("[3@2019-09-01, 4@2019-09-03]"), True),
            (tbixt, TIntSeq("[1@2019-09-01, 1@2019-09-03]"), False),
            (tbixt, TIntSeq("[3@2019-09-01, 4@2019-09-03]"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
            "TBoxInt X False",
            "TBoxInt X True",
            "TBoxInt XT False",
            "TBoxInt XT True",
            "TFloat X False",
            "TFloat X True",
            "TFloat XT False",
            "TFloat XT True",
            "TInt X False",
            "TInt X True",
            "TInt XT False",
            "TInt XT True",
        ],
    )
    def test_is_over_or_left(self, tbox, argument, expected):
        assert tbox.is_over_or_left(argument) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([0,1])"), False),
            (tbfx, TBox("TBOXFLOAT X([3,4])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([0,1],[2019-09-01,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-02,2019-09-03])"), True),
        ],
        ids=[
            "TBoxFloat X False",
            "TBoxFloat X True",
            "TBoxFloat XT False",
            "TBoxFloat XT True",
        ],
    )
    def test_is_over_or_right(self, tbox, argument, expected):
        assert argument.is_over_or_right(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbt, TBox("TBOX T([2019-09-01,2019-09-03])"), False),
            (tbt, TBox("TBOX T([2019-09-03,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-03,2019-09-03])"), True),
        ],
        ids=["TBox T False", "TBox T True", "TBoxFloat XT False", "TBoxFloat XT True"],
    )
    def test_is_before_after(self, tbox, argument, expected):
        assert tbox.is_before(argument) == expected
        assert argument.is_after(tbox) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbt, TBox("TBOX T([2019-09-01,2019-09-01])"), False),
            (tbt, TBox("TBOX T([2019-09-03,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-01])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-03,2019-09-03])"), True),
        ],
        ids=["TBox T False", "TBox T True", "TBoxFloat XT False", "TBoxFloat XT True"],
    )
    def test_is_over_or_before(self, tbox, argument, expected):
        assert tbox.is_over_or_before(argument) == expected

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbt, TBox("TBOX T([2019-09-03,2019-09-03])"), False),
            (tbt, TBox("TBOX T([2019-09-01,2019-09-03])"), True),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-02,2019-09-03])"), False),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-01,2019-09-03])"), True),
        ],
        ids=["TBox T False", "TBox T True", "TBoxFloat XT False", "TBoxFloat XT True"],
    )
    def test_is_over_or_after(self, tbox, argument, expected):
        assert tbox.is_over_or_after(argument) == expected


class TestTBoxSetFunctions(TestTBox):
    tbx1 = TBox("TBOXFLOAT X([1,2])")
    tbt1 = TBox("TBOX T([2019-09-01,2019-09-02])")
    tbxt1 = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")
    tbx2 = TBox("TBOXFLOAT X([2,3])")
    tbt2 = TBox("TBOX T([2019-09-02,2019-09-03])")
    tbxt2 = TBox("TBOXFLOAT XT([2,3],[2019-09-02,2019-09-03])")

    @pytest.mark.parametrize(
        "tbox1, tbox2, expected",
        [
            (tbx1, tbx2, TBox("TBOXFLOAT X([1,3])")),
            (tbt1, tbt2, TBox("TBOXFLOAT T([2019-09-01,2019-09-03])")),
            (tbxt1, tbxt2, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])")),
        ],
        ids=["TBoxFloat X", "TBox T", "TBoxFloat XT"],
    )
    def test_union(self, tbox1, tbox2, expected):
        assert tbox1.union(tbox2) == expected
        assert tbox1 + tbox2 == expected

    @pytest.mark.parametrize(
        "tbox1, tbox2, expected",
        [
            (tbx1, tbx2, TBox("TBOXFLOAT X([2,2])")),
            (tbt1, tbt2, TBox("TBOX T([2019-09-02,2019-09-02])")),
            (tbxt1, tbxt2, TBox("TBOXFLOAT XT([2,2],[2019-09-02,2019-09-02])")),
        ],
        ids=["TBoxFloat X", "TBpx T", "TBoxFloat XT"],
    )
    def test_intersection(self, tbox1, tbox2, expected):
        assert tbox1.intersection(tbox2) == expected
        assert tbox1 * tbox2 == expected


class TestTBoxDistanceFunctions(TestTBox):
    tbfx = TBox("TBOXFLOAT X([1,2])")
    tbt = TBox("TBOX T([2019-09-01,2019-09-02])")
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "tbox, argument, expected",
        [
            (tbfx, TBox("TBOXFLOAT X([1,3])"), 0),
            (tbfx, TBox("TBOXFLOAT X([3,4])"), 1),
            (tbfxt, TBox("TBOXFLOAT XT([1,3],[2019-09-01,2019-09-03])"), 0),
            (tbfxt, TBox("TBOXFLOAT XT([3,4],[2019-09-01,2019-09-03])"), 1),
        ],
        ids=[
            "TBoxFloat X Intersection",
            "TBoxFloat X Distance",
            "TBoxFloat XT Intersection",
            "TBoxFloat XT Distance",
        ],
    )
    def test_nearest_approach_distance(self, tbox, argument, expected):
        assert tbox.nearest_approach_distance(argument) == expected


class TestTBoxComparisons(TestTBox):
    tbfxt = TBox("TBOXFLOAT XT([1,2],[2019-09-01,2019-09-02])")
    other = TBox("TBOXFLOAT XT([3,4],[2019-09-03,2019-09-04])")

    def test_eq(self):
        _ = self.tbfxt == self.other

    def test_ne(self):
        _ = self.tbfxt != self.other

    def test_lt(self):
        _ = self.tbfxt < self.other

    def test_le(self):
        _ = self.tbfxt <= self.other

    def test_gt(self):
        _ = self.tbfxt > self.other

    def test_ge(self):
        _ = self.tbfxt >= self.other
