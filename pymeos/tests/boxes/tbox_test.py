from datetime import datetime, timezone, timedelta
from spans.types import intrange, floatrange

import pytest

from pymeos import TBox, TInterpolation, TimestampSet, Period, PeriodSet

from tests.conftest import TestPyMEOS


class TestTBox(TestPyMEOS):
    pass

class TestTBoxConstructors(TestTBox):

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('TBox X([1,2])', TBox, 'TBOX X([1, 2])'),
            ('TBox T([2019-09-01,2019-09-02])', TBox, 
             'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            ('TBox XT([1, 2],[2019-09-01,2019-09-02])', TBox, 
             'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])')
        ],
        ids=['TBox X', 'TBox T', 'TBox XT']
    )
    def test_string_constructor(self, source, type, expected):
        tb = type(source)
        assert isinstance(tb, type)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        'time, expected',
        [
            (datetime(2019, 9, 1), 
                'TBOX T([2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (TimestampSet('{2019-09-01, 2000-09-02}'),
                'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (Period('[2019-09-01, 2019-09-02]'),
                'TBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'),
                'TBOX T([2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])')
        ],
        ids=['Timestamp', 'TimestampSet', 'Period', 'PeriodSet']
    )
    def test_from_time_constructor(self, time, expected):
        tb = TBox.from_time(time)
        assert isinstance(tb, TBox)
        assert str(tb) == expected

    @pytest.mark.parametrize(
        'value, time, expected',
        [
            (1, datetime(2019, 9, 1),
                'TBOX XT([1, 1],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (1.5, datetime(2019, 9, 1),
                'TBOX XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (intrange(1, 2, True, True), datetime(2019, 9, 1),
                'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (floatrange(1.5, 2.5, True, True), datetime(2019, 9, 1),
                'TBOX XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (1, Period('[2019-09-01, 2019-09-02]'),
                'TBOX XT([1, 1],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (1.5, Period('[2019-09-01, 2019-09-02]'),
                'TBOX XT([1.5, 1.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (intrange(1, 2, True, True), Period('[2019-09-01, 2019-09-02]'),
                'TBOX XT([1, 2],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            (floatrange(1.5, 2.5, True, True), Period('[2019-09-01, 2019-09-02]'),
                'TBOX XT([1.5, 2.5],[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        ],
        ids=['int-Timestamp', 'float-Timestamp', 'intrange-Timestamp', 'floatrange-Timestamp',
             'int-Period', 'float-Period', 'intrange-Period', 'floatrange-Period',]
    )
    def test_from_value_time_constructor(self, value, time, expected):
        tb = TBox.from_value_time(value, time)
        assert isinstance(tb, TBox)
        assert str(tb) == expected


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

