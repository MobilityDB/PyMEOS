from copy import copy
from datetime import datetime, timezone, timedelta
from shapely import Point, LineString

import pytest

from pymeos import STBox, TInterpolation, TimestampSet, Period, PeriodSet

from tests.conftest import TestPyMEOS


class TestSTBox(TestPyMEOS):
    pass


class TestSTBoxConstructors(TestSTBox):
    stbx = STBox('STBOX X((1,1),(2,2))')
    stbz = STBox('STBOX Z((1,1,1),(2,2,2))')
    stbt = STBox('STBOX T([2019-09-01,2019-09-02])')
    stbxt = STBox('STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])')
    stbzt = STBox('STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])')

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('STBox X((1,1),(2,2))', STBox, 'STBOX X((1,1),(2,2))'),
            ('STBox T([2019-09-01,2019-09-02])', STBox, 
             'STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            ('STBox XT(((1,1),(2,2)),[2019-09-01,2019-09-02])', STBox, 
             'STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])')
        ],
        ids=['STBox X', 'STBox T', 'STBox XT']
    )
    def test_string_constructor(self, source, type, expected):
        stb = type(source)
        assert isinstance(stb, type)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        'geometry, expected',
        [
            (Point(1,1), 'STBOX T((1,1),(1,1))'),
            (LineString([(1,1), (2,2)]), 'STBOX T((1,1),(2,2))'),
        ],
        ids=['point', 'linestring']
    )
    def test_from_geometry_time_constructor(self, geometry, expected):
        stb = STBox.from_geometry(geometry)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    # @pytest.mark.parametrize(
        # 'time, expected',
        # [
            # (datetime(2019, 9, 1),
                # 'STBOX T([2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            # (TimestampSet('{2019-09-01, 2019-09-02}'),
                # 'STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (Period('[2019-09-01, 2019-09-02]'),
                # 'STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
            # (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'),
                # 'STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        # ],
        # ids=['Timestamp', 'TimestampSet', 'Period', 'PeriodSet']
    # )
    # def test_from_time_constructor(self, time, expected):
        # stb = STBox.from_time(time)
        # assert isinstance(stb, STBox)
        # assert str(stb) == expected

    @pytest.mark.parametrize(
        'geometry, time, expected',
        [
            (Point(1,1), datetime(2019, 9, 1),
                'STBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])'),
            (Point(1,1), Period('[2019-09-01, 2019-09-02]'),
                'STBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])'),
        ],
        ids=['geometry-Timestamp', 'geometry-Period']
    )
    def test_from_geometry_time_constructor(self, geometry, time, expected):
        stb = STBox.from_geometry_time(geometry, time)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        'stbox',
        [stbx, stbz, stbt, stbxt, stbzt],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_from_hexwkb_constructor(self, stbox):
        assert stbox == stbox.from_hexwkb(stbox.as_hexwkb())

    @pytest.mark.parametrize(
        'stbox',
        [stbx, stbz, stbt, stbxt, stbzt],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_copy_constructor(self, stbox):
        other = copy(stbox)
        assert stbox == other
        assert stbox is not other


class TestSTBoxOutputs(TestSTBox):
    stbx = STBox('STBOX X((1,1),(2,2))')
    stbz = STBox('STBOX Z((1,1,1),(2,2,2))')
    stbt = STBox('STBOX T([2019-01-01,2019-01-02])')
    stbxt = STBox('STBOX XT(((1,1),(2,2)),[2019-01-01,2019-01-02])')
    stbzt = STBox('STBOX ZT(((1,1,1),(2,2,2)),[2019-01-01,2019-01-02])')
                                                                  
    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (stbx, 'STBOX X((1,1),(2,2))'),
            (stbz, 'STBOX Z((1,1,1),(2,2,2))'),
            (stbt, 'STBOX T([2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00])'),
            (stbxt, 'STBOX XT(((1,1),(2,2)),[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00])'),
            (stbzt, 'STBOX ZT(((1,1,1),(2,2,2)),[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00])'),
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_str(self, tbox, expected):
        assert str(tbox) == expected

    @pytest.mark.parametrize(
        'tbox, expected',
        [
            (stbx, 'STBox(STBOX X((1,1),(2,2)))'),
            (stbz, 'STBox(STBOX Z((1,1,1),(2,2,2)))'),
            (stbt, 'STBox(STBOX T([2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00]))'),
            (stbxt, 'STBox(STBOX XT(((1,1),(2,2)),[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00]))'),
            (stbzt, 'STBox(STBOX ZT(((1,1,1),(2,2,2)),[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00]))'),
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_repr(self, tbox, expected):
        assert repr(tbox) == expected

    @pytest.mark.parametrize(
        'stbox, expected',
        [
            (stbx, '0101000000000000F03F0000000000000040000000000000F03F0000000000000040'),
            (stbz, '0111000000000000F03F0000000000000040000000000000F03F0000000000000040000000000000F03F0000000000000040'),
            (stbt, '01022100030080AEFA5821020000E085186D210200'),
            (stbxt, '01032100030080AEFA5821020000E085186D210200000000000000F03F0000000000000040000000000000F03F0000000000000040'),
            (stbzt, '01132100030080AEFA5821020000E085186D210200000000000000F03F0000000000000040000000000000F03F0000000000000040'
                '000000000000F03F0000000000000040'),
        ],
        ids=['STBox X', 'STBox Z', 'STBox T', 'STBox XT', 'STBox ZT']
    )
    def test_as_hexwkb(self, stbox, expected):
        assert stbox.as_hexwkb() == expected


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
    def test_xmin_ymin(self, stbox, expected):
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
    def test_zmin(self, stbox, expected):
        assert stbox.zmin() == expected

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
    def test_xmax_ymax(self, stbox, expected):
        assert stbox.xmax() == expected
        assert stbox.ymax() == expected

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
    def test_zmax(self, stbox, expected):
        assert stbox.zmax() == expected

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

