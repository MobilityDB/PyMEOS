from datetime import datetime, timezone, timedelta

import pytest

from pymeos import STBox, TInterpolation, TimestampSet, Period, PeriodSet

from tests.conftest import TestPyMEOS


class TestSTBox(TestPyMEOS):
    pass


class TestSTBoxAccessors(TestSTBox):
    stbx = STBox('STBOX X((1,1),(2,2))')
    stbz = STBox('STBOX Z((1,1,1),(2,2,2))')
    stbt = STBox('STBOX T([2019-09-01,2019-09-02])')
    stbxt = STBox('STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])')
    stbzt = STBox('STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])')

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, True),
            (stbz, True),
            (stbt, False),
            (stbxt, True),
            (stbzt, True)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_has_xy(self, stbox, expected):
        assert stbox.has_xy() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, False),
            (stbz, True),
            (stbt, False),
            (stbxt, False),
            (stbzt, True)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_has_z(self, stbox, expected):
        assert stbox.has_z() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, 1),
            (stbz, 1),
            (stbt, None),
            (stbxt, 1),
            (stbzt, 1)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_xmin(self, stbox, expected):
        assert stbox.xmin() == expected
        assert stbox.ymin() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, None),
            (stbz, 1),
            (stbt, None),
            (stbxt, None),
            (stbzt, 1)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_xmin(self, stbox, expected):
        assert stbox.zmin() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, None),
            (stbz, 2),
            (stbt, None),
            (stbxt, None),
            (stbzt, 2)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_xmin(self, stbox, expected):
        assert stbox.zmax() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, 2),
            (stbz, 2),
            (stbt, None),
            (stbxt, 2),
            (stbzt, 2)
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_xmax(self, stbox, expected):
        assert stbox.xmax() == expected
        assert stbox.ymax() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, None),
            (stbz, None),
            (stbt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (stbxt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (stbzt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc))
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_tmin(self, stbox, expected):
        assert stbox.tmin() == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, None),
            (stbz, None),
            (stbt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (stbxt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (stbzt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc))
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_tmax(self, stbox, expected):
        assert stbox.tmax() == expected
