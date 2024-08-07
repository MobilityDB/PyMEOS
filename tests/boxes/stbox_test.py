from copy import copy
from datetime import datetime, timezone, timedelta
from shapely import Point, LineString, Polygon
import shapely.geometry

import pytest
import math

from pymeos import (
    STBox,
    TInterpolation,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
    TGeomPointInst,
    TGeomPointSeq,
    TGeomPointSeqSet,
    TGeogPointInst,
    TGeogPointSeq,
    TGeogPointSeqSet,
)

from tests.conftest import TestPyMEOS


class TestSTBox(TestPyMEOS):
    pass


class TestSTBoxConstructors(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "source, type, expected",
        [
            ("STBox X((1,1),(2,2))", STBox, "STBOX X((1,1),(2,2))"),
            (
                "STBox T([2019-09-01,2019-09-02])",
                STBox,
                "STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                "STBox XT(((1,1),(2,2)),[2019-09-01,2019-09-02])",
                STBox,
                "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=["STBox X", "STBox T", "STBox XT"],
    )
    def test_string_constructor(self, source, type, expected):
        stb = type(source)
        assert isinstance(stb, type)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "geometry, expected",
        [
            (Point(1, 1), "STBOX X((1,1),(1,1))"),
            (LineString([(1, 1), (2, 2)]), "STBOX X((1,1),(2,2))"),
            (
                shapely.set_srid(shapely.Point(1, 1), 5676),
                "SRID=5676;STBOX X((1,1),(1,1))",
            ),
            (
                shapely.set_srid(shapely.LineString([(1, 1), (2, 2)]), 5676),
                "SRID=5676;STBOX X((1,1),(2,2))",
            ),
        ],
        ids=["point", "linestring", "srid point", "srid linestring"],
    )
    def test_from_geometry_constructor(self, geometry, expected):
        stb = STBox.from_geometry(geometry)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "params, expected",
        [
            ({"xmin": 0, "xmax": 2, "ymin": "1", "ymax": "3"}, "STBOX X((0,1),(2,3))"),
            (
                {
                    "xmin": 0,
                    "xmax": 2,
                    "ymin": "1",
                    "ymax": "3",
                    "zmin": 10,
                    "zmax": 12,
                },
                "STBOX Z((0,1,10),(2,3,12))",
            ),
            (
                {
                    "xmin": 0,
                    "xmax": 2,
                    "ymin": "1",
                    "ymax": "3",
                    "tmin": "2000-01-01",
                    "tmax": "2000-01-03",
                },
                "STBOX XT(((0,1),(2,3)),[2000-01-01 00:00:00+00, 2000-01-03 00:00:00+00])",
            ),
            (
                {
                    "xmin": 0,
                    "xmax": 2,
                    "ymin": "1",
                    "ymax": "3",
                    "zmin": 10,
                    "zmax": 12,
                    "tmin": datetime(2000, 1, 1),
                    "tmax": datetime(2000, 1, 3),
                },
                "STBOX ZT(((0,1,10),(2,3,12)),[2000-01-01 00:00:00+00, 2000-01-03 00:00:00+00])",
            ),
        ],
        ids=["XY", "XYZ", "XYT", "XYZT"],
    )
    def test_parameters_constructor(self, params, expected):
        stb = STBox(**params)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "time, expected",
        [
            (
                datetime(2019, 9, 1),
                "STBOX T([2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TsTzSet("{2019-09-01, 2019-09-02}"),
                "STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                "STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TsTzSpanSet("{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}"),
                "STBOX T([2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
        ],
        ids=["Timestamp", "TsTzSet", "TsTzSpan", "TsTzSpanSet"],
    )
    def test_from_time_constructor(self, time, expected):
        stb = STBox.from_time(time)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "geometry, time, expected",
        [
            (
                Point(1, 1),
                datetime(2019, 9, 1),
                "STBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                Point(1, 1),
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                "STBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=["geometry-Timestamp", "geometry-TsTzSpan"],
    )
    def test_from_geometry_time_constructor(self, geometry, time, expected):
        stb = STBox.from_geometry_time(geometry, time)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "tpoint, expected",
        [
            (
                TGeomPointInst("Point(1 1)@2019-09-01"),
                "STBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TGeomPointSeq("{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}"),
                "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeomPointSeq("[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]"),
                "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeomPointSeqSet(
                    "{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}"
                ),
                "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
            (
                TGeogPointInst("Point(1 1)@2019-09-01"),
                "SRID=4326;GEODSTBOX XT(((1,1),(1,1)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TGeogPointSeq("{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}"),
                "SRID=4326;GEODSTBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeogPointSeq("[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]"),
                "SRID=4326;GEODSTBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeogPointSeqSet(
                    "{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}"
                ),
                "SRID=4326;GEODSTBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
        ],
        ids=[
            "TGeomPoint Instant",
            "TGeomPoint Discrete Sequence",
            "TGeomPoint Sequence",
            "TGeomPoint Sequence Set",
            "TGeogPoint Instant",
            "TGeogPoint Discrete Sequence",
            "TGeogPoint Sequence",
            "TGeogPoint Sequence Set",
        ],
    )
    def test_from_tpoint_constructor(self, tpoint, expected):
        stb = STBox.from_tpoint(tpoint)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "geo, expected",
        [
            (Point(1, 1), "STBOX X((0,0),(2,2))"),
            (LineString([(1, 1), (2, 2)]), "STBOX X((0,0),(3,3))"),
            (
                shapely.set_srid(shapely.Point(1, 1), 5676),
                "SRID=5676;STBOX X((0,0),(2,2))",
            ),
            (
                shapely.set_srid(shapely.LineString([(1, 1), (2, 2)]), 5676),
                "SRID=5676;STBOX X((0,0),(3,3))",
            ),
        ],
        ids=["Point", "Line string", "Geodetic Point", "Geodetic line string"],
    )
    def test_from_geo_expand_space_constructor(self, geo, expected):
        stb = STBox.from_expanding_bounding_box(geo, 1)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "tpoint, expected",
        [
            (
                TGeomPointInst("Point(1 1)@2019-09-01"),
                "STBOX XT(((0,0),(2,2)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TGeomPointSeq("{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}"),
                "STBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeomPointSeq("[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]"),
                "STBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeomPointSeqSet(
                    "{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}"
                ),
                "STBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
            (
                TGeogPointInst("Point(1 1)@2019-09-01"),
                "SRID=4326;GEODSTBOX XT(((0,0),(2,2)),[2019-09-01 00:00:00+00, 2019-09-01 00:00:00+00])",
            ),
            (
                TGeogPointSeq("{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}"),
                "SRID=4326;GEODSTBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeogPointSeq("[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]"),
                "SRID=4326;GEODSTBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                TGeogPointSeqSet(
                    "{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}"
                ),
                "SRID=4326;GEODSTBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-05 00:00:00+00])",
            ),
        ],
        ids=[
            "TGeomPoint Instant",
            "TGeomPoint Discrete Sequence",
            "TGeomPoint Sequence",
            "TGeomPoint Sequence Set",
            "TGeogPoint Instant",
            "TGeogPoint Discrete Sequence",
            "TGeogPoint Sequence",
            "TGeogPoint Sequence Set",
        ],
    )
    def test_from_tpoint_expand_space_constructor(self, tpoint, expected):
        stb = STBox.from_expanding_bounding_box(tpoint, 1)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (STBox("STBOX X((1,1),(2,2))"), "STBOX X((0,0),(3,3))"),
            (STBox("STBOX Z((1,1,1),(2,2,2))"), "STBOX Z((0,0,0),(3,3,3))"),
            (
                STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])"),
                "STBOX XT(((0,0),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])"),
                "STBOX ZT(((0,0,0),(3,3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_from_stbox_expand_space_constructor(self, stbox, expected):
        stb = STBox.from_expanding_bounding_box(stbox, 1)
        assert isinstance(stb, STBox)
        assert str(stb) == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (
                STBox("STBOX X((1,1),(3,3))"),
                [
                    STBox("STBOX X((1,1),(2,2))"),
                    STBox("STBOX X((2,1),(3,2))"),
                    STBox("STBOX X((1,2),(2,3))"),
                    STBox("STBOX X((2,2),(3,3))"),
                ],
            ),
            (
                STBox("STBOX Z((1,1,1),(3,3,3))"),
                [
                    STBox("STBOX Z((1,1,1),(2,2,2))"),
                    STBox("STBOX Z((2,1,1),(3,2,2))"),
                    STBox("STBOX Z((1,2,1),(2,3,2))"),
                    STBox("STBOX Z((2,2,1),(3,3,2))"),
                    STBox("STBOX Z((1,1,2),(2,2,3))"),
                    STBox("STBOX Z((2,1,2),(3,2,3))"),
                    STBox("STBOX Z((1,2,2),(2,3,3))"),
                    STBox("STBOX Z((2,2,2),(3,3,3))"),
                ],
            ),
            (
                STBox(
                    "STBOX XT(((1,1),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                ),
                [
                    STBox(
                        "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX XT(((2,1),(3,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX XT(((1,2),(2,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX XT(((2,2),(3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                ],
            ),
            (
                STBox(
                    "STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                ),
                [
                    STBox(
                        "STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((2,1,1),(3,2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((1,2,1),(2,3,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((2,2,1),(3,3,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((1,1,2),(2,2,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((2,1,2),(3,2,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((1,2,2),(2,3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                    STBox(
                        "STBOX ZT(((2,2,2),(3,3,3)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"
                    ),
                ],
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_from_quad_split_flat(self, stbox, expected):
        stblist = STBox.quad_split_flat(stbox)
        assert stblist == expected

    @pytest.mark.parametrize(
        "stbox",
        [stbx, stbz, stbt, stbxt, stbzt],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_from_as_constructor(self, stbox):
        assert stbox == STBox(str(stbox))
        assert stbox == stbox.from_wkb(stbox.as_wkb())
        assert stbox == stbox.from_hexwkb(stbox.as_hexwkb())

    @pytest.mark.parametrize(
        "stbox",
        [stbx, stbz, stbt, stbxt, stbzt],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_copy_constructor(self, stbox):
        other = copy(stbox)
        assert stbox == other
        assert stbox is not other


class TestSTBoxOutputs(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, "STBOX X((1,1),(2,2))"),
            (stbz, "STBOX Z((1,1,1),(2,2,2))"),
            (stbt, "STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])"),
            (
                stbxt,
                "STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
            (
                stbzt,
                "STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00])",
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_str(self, stbox, expected):
        assert str(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, "STBox(STBOX X((1,1),(2,2)))"),
            (stbz, "STBox(STBOX Z((1,1,1),(2,2,2)))"),
            (stbt, "STBox(STBOX T([2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))"),
            (
                stbxt,
                "STBox(STBOX XT(((1,1),(2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))",
            ),
            (
                stbzt,
                "STBox(STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00]))",
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_repr(self, stbox, expected):
        assert repr(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (
                stbx,
                "0101000000000000F03F0000000000000040000000000000F03F0000000000000040",
            ),
            (
                stbz,
                "0111000000000000F03F0000000000000040000000000000F03F0000000000000040000000000000F03F0000000000000040",
            ),
            (stbt, "010227000300A01E4E713402000000F66B85340200"),
            (
                stbxt,
                "010327000300A01E4E713402000000F66B85340200000000000000F03F0000000000000040000000000000F03F0000000000000040",
            ),
            (
                stbzt,
                "011327000300A01E4E713402000000F66B85340200000000000000F03F0000000000000040000000000000F03F0000000000000040000000000000F03F0000000000000040",
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_as_hexwkb(self, stbox, expected):
        assert stbox.as_hexwkb() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])),
            (stbxt, Polygon([(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)])),
        ],
        ids=["STBox X", "STBox XT"],
    )
    def test_to_geometry(self, stbox, expected):
        stb = stbox.to_geometry()
        assert isinstance(stb, Polygon)
        assert stb == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbt, TsTzSpan("[2019-09-01, 2019-09-02]")),
            (stbxt, TsTzSpan("[2019-09-01, 2019-09-02]")),
        ],
        ids=["STBox X", "STBox XT"],
    )
    def test_to_tstzspan(self, stbox, expected):
        stb = stbox.to_tstzspan()
        assert isinstance(stb, TsTzSpan)
        assert stb == expected


class TestSTBoxAccessors(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    gstbx = STBox("GEODSTBOX X((1,1),(2,2))")
    gstbz = STBox("GEODSTBOX Z((1,1,1),(2,2,2))")
    gstbt = STBox("GEODSTBOX T([2019-09-01,2019-09-02])")
    gstbxt = STBox("GEODSTBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    gstbzt = STBox("GEODSTBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, True), (stbz, True), (stbt, False), (stbxt, True), (stbzt, True)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_has_xy(self, stbox, expected):
        assert stbox.has_xy() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, False), (stbz, True), (stbt, False), (stbxt, False), (stbzt, True)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_has_z(self, stbox, expected):
        assert stbox.has_z() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, False), (stbz, False), (stbt, True), (stbxt, True), (stbzt, True)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_has_t(self, stbox, expected):
        assert stbox.has_t() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, False),
            (stbz, False),
            (stbt, False),
            (stbxt, False),
            (stbzt, False),
            (gstbx, True),
            (gstbz, True),
            (gstbt, True),
            (gstbxt, True),
            (gstbzt, True),
        ],
        ids=[
            "STBox X",
            "STBox Z",
            "STBox T",
            "STBox XT",
            "STBox ZT",
            "Geodetic STBox X",
            "Geodetic STBox Z",
            "Geodetic STBox T",
            "Geodetic STBox XT",
            "Geodetic STBox ZT",
        ],
    )
    def test_geodetic(self, stbox, expected):
        assert stbox.geodetic() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, 1), (stbz, 1), (stbt, None), (stbxt, 1), (stbzt, 1)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_xmin_ymin(self, stbox, expected):
        assert stbox.xmin() == expected
        assert stbox.ymin() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, None), (stbz, 1), (stbt, None), (stbxt, None), (stbzt, 1)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_zmin(self, stbox, expected):
        assert stbox.zmin() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, 2), (stbz, 2), (stbt, None), (stbxt, 2), (stbzt, 2)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_xmax_ymax(self, stbox, expected):
        assert stbox.xmax() == expected
        assert stbox.ymax() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, None), (stbz, 2), (stbt, None), (stbxt, None), (stbzt, 2)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_zmax(self, stbox, expected):
        assert stbox.zmax() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, None),
            (stbz, None),
            (stbt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (stbxt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (stbzt, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_tmin(self, stbox, expected):
        assert stbox.tmin() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, None),
            (stbz, None),
            (stbt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (stbxt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (stbzt, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_tmax(self, stbox, expected):
        assert stbox.tmax() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [(stbx, None), (stbz, None), (stbt, True), (stbxt, True), (stbzt, True)],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_tmin_tmax_inc(self, stbox, expected):
        assert stbox.tmin_inc() == expected
        assert stbox.tmax_inc() == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, 0),
            (stbz, 0),
            (stbxt, 0),
            (stbzt, 0),
            (gstbx, 4326),
            (gstbz, 4326),
            (gstbxt, 4326),
            (gstbzt, 4326),
        ],
        ids=[
            "STBox X",
            "STBox Z",
            "STBox XT",
            "STBox ZT",
            "Geodetic STBox X",
            "Geodetic STBox Z",
            "Geodetic STBox XT",
            "Geodetic STBox ZT",
        ],
    )
    def test_srid(self, stbox, expected):
        assert stbox.srid() == expected

    @pytest.mark.parametrize(
        "stbox",
        [stbx, stbz, stbxt, stbzt],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_set_srid(self, stbox):
        assert stbox.set_srid(5676).srid() == 5676


class TestSTBoxTransformations(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, STBox("STBOX X((1,1),(2,2))")),
            (stbz, STBox("STBOX Z((1,1,1),(2,2,2))")),
            (stbxt, STBox("STBOX X((1,1),(2,2))")),
            (stbzt, STBox("STBOX Z((1,1,1),(2,2,2))")),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_get_space(self, stbox, expected):
        stb = stbox.get_space()
        assert isinstance(stb, STBox)
        assert stb == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbx, STBox("STBOX X((0,0),(3,3))")),
            (stbz, STBox("STBOX Z((0,0,0),(3,3,3))")),
            (stbxt, STBox("STBOX XT(((0,0),(3,3)),[2019-09-01, 2019-09-02])")),
            (stbzt, STBox("STBOX ZT(((0,0,0),(3,3,3)),[2019-09-01, 2019-09-02])")),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_expand_float(self, stbox, expected):
        stb = stbox.expand(1)
        assert isinstance(stb, STBox)
        assert stb == expected

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (stbt, STBox("STBOX T([2019-08-31, 2019-09-03])")),
            (stbxt, STBox("STBOX XT(((1,1),(2,2)),[2019-08-31, 2019-09-03])")),
            (stbzt, STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-08-31, 2019-09-03])")),
        ],
        ids=["STBox T", "STBox XT", "STBox ZT"],
    )
    def test_expand_time(self, stbox, expected):
        stb = stbox.expand(timedelta(days=1))
        assert isinstance(stb, STBox)
        assert stb == expected

    @pytest.mark.parametrize(
        "stbox, delta, expected",
        [
            (stbt, timedelta(days=4), STBox("STBOX T([2019-09-05,2019-09-06])")),
            (stbt, timedelta(days=-4), STBox("STBOX T([2019-08-28,2019-08-29])")),
            (
                stbt,
                timedelta(hours=2),
                STBox("STBOX T([2019-09-01 02:00:00,2019-09-02 02:00:00])"),
            ),
            (
                stbt,
                timedelta(hours=-2),
                STBox("STBOX T([2019-08-31 22:00:00,2019-09-01 22:00:00])"),
            ),
        ],
        ids=["positive days", "negative days", "positive hours", "negative hours"],
    )
    def test_shift_time(self, stbox, delta, expected):
        assert stbox.shift_time(delta) == expected

    @pytest.mark.parametrize(
        "stbox, delta, expected",
        [
            (stbt, timedelta(days=4), STBox("STBOX T([2019-09-01,2019-09-05])")),
            (
                stbt,
                timedelta(hours=2),
                STBox("STBOX T([2019-09-01,2019-09-01 02:00:00])"),
            ),
        ],
        ids=["positive days", "positive hours"],
    )
    def test_scale_time(self, stbox, delta, expected):
        assert stbox.scale_time(delta) == expected

    def test_shift_scale_time(self):
        assert self.stbt.shift_scale_time(
            timedelta(days=4), timedelta(hours=4)
        ) == STBox("STBOX T([2019-09-05,2019-09-05 04:00:00])")

    @pytest.mark.parametrize(
        "stbox, expected",
        [
            (
                STBox("STBOX X((1.123456789,1.123456789),(2.123456789,2.123456789))"),
                STBox("STBOX X((1.12,1.12),(2.12,2.12))"),
            ),
            (
                STBox(
                    "STBOX Z((1.123456789,1.123456789,1.123456789),(2.123456789,2.123456789,2.123456789))"
                ),
                STBox("STBOX Z((1.12,1.12,1.12),(2.12,2.12,2.12))"),
            ),
            (
                STBox(
                    "STBOX XT(((1.123456789,1.123456789),(2.123456789,2.123456789)),[2019-09-01, 2019-09-02])"
                ),
                STBox("STBOX XT(((1.12,1.12),(2.12,2.12)),[2019-09-01, 2019-09-03])"),
            ),
            (
                STBox(
                    "STBOX ZT(((1.123456789,1.123456789,1.123456789),(2.123456789,2.123456789,2.123456789)),"
                    "[2019-09-01, 2019-09-02])"
                ),
                STBox(
                    "STBOX ZT(((1.12,1.12,1.12),(2.12,2.12,2.12)),[2019-09-01, 2019-09-02])"
                ),
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_round(self, stbox, expected):
        assert stbox.round(max_decimals=2)


class TestSTBoxTopologicalFunctions(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((1,1),(3,3))"), False),
            (stbx, STBox("STBOX X((2,2),(3,3))"), True),
            (stbz, STBox("STBOX Z((1,1,1),(3,3,3))"), False),
            (stbz, STBox("STBOX Z((2,2,2),(3,3,3))"), True),
            (stbt, STBox("STBOX T([2019-09-01,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-02,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((2,2),(3,3)),[2019-09-02,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((2,2,2),(3,3,3)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_adjacent(self, stbox, argument, expected):
        assert stbox.is_adjacent(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((2,2),(3,3))"), False),
            (stbx, STBox("STBOX X((1,1),(3,3))"), True),
            (stbz, STBox("STBOX Z((2,2,2),(3,3,3))"), False),
            (stbz, STBox("STBOX Z((1,1,1),(3,3,3))"), True),
            (stbt, STBox("STBOX T([2019-09-02,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-01,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((2,2),(3,3)),[2019-09-02,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((2,2,2),(3,3,3)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_contained_in_contains(self, stbox, argument, expected):
        assert stbox.is_contained_in(argument) == expected
        assert argument.contains(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((3,3),(3,3))"), False),
            (stbx, STBox("STBOX X((1,1),(3,3))"), True),
            (stbz, STBox("STBOX Z((3,3,3),(3,3,3))"), False),
            (stbz, STBox("STBOX Z((1,1,1),(3,3,3))"), True),
            (stbt, STBox("STBOX T([2019-09-03,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-01,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((3,3),(3,3)),[2019-09-02,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((3,3,3),(3,3,3)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_overlaps(self, stbox, argument, expected):
        assert stbox.overlaps(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((3,3),(3,3))"), False),
            (stbx, STBox("STBOX X((1,1),(2,2))"), True),
            (stbz, STBox("STBOX Z((3,3,3),(3,3,3))"), False),
            (stbz, STBox("STBOX Z((1,1,1),(2,2,2))"), True),
            (stbt, STBox("STBOX T([2019-09-03,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-01,2019-09-02])"), True),
            (stbxt, STBox("STBOX X((3,3),(3,3))"), False),
            (stbxt, STBox("STBOX X((1,1),(2,2))"), True),
            (stbzt, STBox("STBOX Z((3,3,3),(3,3,3))"), False),
            (stbzt, STBox("STBOX Z((1,1,1),(2,2,2))"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_same(self, stbox, argument, expected):
        assert stbox.is_same(argument) == expected


class TestSTBoxPositionFunctions(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((1,1),(3,3))"), False),
            (stbx, STBox("STBOX X((3,3),(4,4))"), True),
            (stbz, STBox("STBOX Z((1,1,1),(3,3,3))"), False),
            (stbz, STBox("STBOX Z((3,3,3),(4,4,4))"), True),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-02,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_left_right(self, stbox, argument, expected):
        assert stbox.is_left(argument) == expected
        assert argument.is_right(stbox) == expected
        assert stbox.is_below(argument) == expected
        assert argument.is_above(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((1,1),(1,1))"), False),
            (stbx, STBox("STBOX X((3,3),(4,4))"), True),
            (stbz, STBox("STBOX Z((1,1,1),(1,1,1))"), False),
            (stbz, STBox("STBOX Z((3,3,3),(4,4,4))"), True),
            (stbxt, STBox("STBOX XT(((1,1),(1,1)),[2019-09-01,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-02,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(1,1,1)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_over_or_left(self, stbox, argument, expected):
        assert stbox.is_over_or_left(argument) == expected
        assert stbox.is_over_or_below(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((0,0),(1,1))"), False),
            (stbx, STBox("STBOX X((3,3),(4,4))"), True),
            (stbz, STBox("STBOX Z((0,0,0),(1,1,1))"), False),
            (stbz, STBox("STBOX Z((3,3,3),(4,4,4))"), True),
            (stbxt, STBox("STBOX XT(((0,0),(1,1)),[2019-09-01,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-02,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((0,0,0),(1,1,1)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox X False",
            "STBox X True",
            "STBox Z False",
            "STBox Z True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_over_or_right(self, stbox, argument, expected):
        assert argument.is_over_or_right(stbox) == expected
        assert argument.is_over_or_above(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbz, STBox("STBOX Z((1,1,1),(1,1,1))"), False),
            (stbz, STBox("STBOX Z((3,3,3),(4,4,4))"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(1,1,1)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=["STBox Z False", "STBox Z True", "STBox ZT False", "STBox ZT True"],
    )
    def test_is_over_or_front(self, stbox, argument, expected):
        assert stbox.is_over_or_front(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbz, STBox("STBOX Z((2,2,2),(2,2,2))"), False),
            (stbz, STBox("STBOX Z((1,1,1),(2,2,2))"), True),
            (
                stbzt,
                STBox("STBOX ZT(((2,2,2),(2,2,2)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=["STBox Z False", "STBox Z True", "STBox ZT False", "STBox ZT True"],
    )
    def test_is_over_or_behind(self, stbox, argument, expected):
        assert stbox.is_over_or_behind(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbt, STBox("STBOX T([2019-09-01,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-03,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-03,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-03,2019-09-03])"), True),
        ],
        ids=[
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_before_after(self, stbox, argument, expected):
        assert stbox.is_before(argument) == expected
        assert argument.is_after(stbox) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbt, STBox("STBOX T([2019-09-01,2019-09-01])"), False),
            (stbt, STBox("STBOX T([2019-09-03,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-01])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-03,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-01])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-03,2019-09-03])"), True),
        ],
        ids=[
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_over_or_before(self, stbox, argument, expected):
        assert stbox.is_over_or_before(argument) == expected

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbt, STBox("STBOX T([2019-09-03,2019-09-03])"), False),
            (stbt, STBox("STBOX T([2019-09-01,2019-09-03])"), True),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-02,2019-09-03])"), False),
            (stbxt, STBox("STBOX XT(((3,3),(4,4)),[2019-09-01,2019-09-03])"), True),
            (
                stbzt,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-02,2019-09-03])"),
                False,
            ),
            (stbzt, STBox("STBOX ZT(((3,3,3),(4,4,4)),[2019-09-01,2019-09-03])"), True),
        ],
        ids=[
            "STBox T False",
            "STBox T True",
            "STBox XT False",
            "STBox XT True",
            "STBox ZT False",
            "STBox ZT True",
        ],
    )
    def test_is_over_or_after(self, stbox, argument, expected):
        assert stbox.is_over_or_after(argument) == expected


class TestSTBoxSetFunctions(TestSTBox):
    stbx1 = STBox("STBOX X((1,1),(2,2))")
    stbz1 = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt1 = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt1 = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt1 = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")
    stbx2 = STBox("STBOX X((2,2),(3,3))")
    stbz2 = STBox("STBOX Z((2,2,2),(3,3,3))")
    stbt2 = STBox("STBOX T([2019-09-02,2019-09-03])")
    stbxt2 = STBox("STBOX XT(((2,2),(3,3)),[2019-09-02,2019-09-03])")
    stbzt2 = STBox("STBOX ZT(((2,2,2),(3,3,3)),[2019-09-02,2019-09-03])")

    @pytest.mark.parametrize(
        "stbox1, argument",
        [
            (stbx1, STBox("STBOX X((1,1),(3,3))")),
            (stbz1, STBox("STBOX Z((1,1,1),(3,3,3))")),
            (stbt1, STBox("STBOX T([2019-09-01,2019-09-03])")),
            (stbxt1, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])")),
            (stbzt1, STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])")),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_in(self, stbox1, argument):
        assert stbox1 in argument

    @pytest.mark.parametrize(
        "stbox1, stbox2, expected",
        [
            (stbx1, stbx2, STBox("STBOX X((1,1),(3,3))")),
            (stbz1, stbz2, STBox("STBOX Z((1,1,1),(3,3,3))")),
            (stbt1, stbt2, STBox("STBOX T([2019-09-01,2019-09-03])")),
            (stbxt1, stbxt2, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])")),
            (
                stbzt1,
                stbzt2,
                STBox("STBOX ZT(((1,1,1),(3,3,3)),[2019-09-01,2019-09-03])"),
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_union(self, stbox1, stbox2, expected):
        assert stbox1.union(stbox2) == expected
        assert stbox1 + stbox2 == expected

    @pytest.mark.parametrize(
        "stbox1, stbox2, expected",
        [
            (stbx1, stbx2, STBox("STBOX X((2,2),(2,2))")),
            (stbz1, stbz2, STBox("STBOX Z((2,2,2),(2,2,2))")),
            (stbt1, stbt2, STBox("STBOX T([2019-09-02,2019-09-02])")),
            (stbxt1, stbxt2, STBox("STBOX XT(((2,2),(2,2)),[2019-09-02,2019-09-02])")),
            (
                stbzt1,
                stbzt2,
                STBox("STBOX ZT(((2,2,2),(2,2,2)),[2019-09-02,2019-09-02])"),
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox T", "STBox XT", "STBox ZT"],
    )
    def test_intersection(self, stbox1, stbox2, expected):
        assert stbox1.intersection(stbox2) == expected
        assert stbox1 * stbox2 == expected


class TestSTBoxDistanceFunctions(TestSTBox):
    stbx = STBox("STBOX X((1,1),(2,2))")
    stbz = STBox("STBOX Z((1,1,1),(2,2,2))")
    stbt = STBox("STBOX T([2019-09-01,2019-09-02])")
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    stbzt = STBox("STBOX ZT(((1,1,1),(2,2,2)),[2019-09-01,2019-09-02])")

    @pytest.mark.parametrize(
        "stbox, argument, expected",
        [
            (stbx, STBox("STBOX X((1,1),(3,3))"), 0),
            (stbz, STBox("STBOX Z((3,3,3),(3,3,3))"), math.sqrt(3)),
            (stbxt, STBox("STBOX XT(((1,1),(3,3)),[2019-09-01,2019-09-03])"), 0),
            (
                stbzt,
                STBox("STBOX ZT(((3,3,3),(3,3,3)),[2019-09-01,2019-09-03])"),
                math.sqrt(3),
            ),
        ],
        ids=["STBox X", "STBox Z", "STBox XT", "STBox ZT"],
    )
    def test_nearest_approach_distance(self, stbox, argument, expected):
        assert stbox.nearest_approach_distance(argument) == expected


class TestSTBoxComparisons(TestSTBox):
    stbxt = STBox("STBOX XT(((1,1),(2,2)),[2019-09-01,2019-09-02])")
    other = STBox("STBOX XT(((3,3),(4,4)),[2019-09-01,2019-09-02])")

    def test_eq(self):
        _ = self.stbxt == self.other

    def test_ne(self):
        _ = self.stbxt != self.other

    def test_lt(self):
        _ = self.stbxt < self.other

    def test_le(self):
        _ = self.stbxt <= self.other

    def test_gt(self):
        _ = self.stbxt > self.other

    def test_ge(self):
        _ = self.stbxt >= self.other
