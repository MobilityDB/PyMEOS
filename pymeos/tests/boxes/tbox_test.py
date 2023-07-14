from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBox, TInterpolation, TimestampSet, Period, PeriodSet

from tests.conftest import TestPyMEOS


class TestTBox(TestPyMEOS):
    pass


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

