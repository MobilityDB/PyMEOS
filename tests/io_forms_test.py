import pytest

from pymeos import (
    Cbuffer,
    CbufferSet,
    FloatSet,
    FloatSpan,
    GeometrySet,
    IntSet,
    IntSpan,
    IntSpanSet,
    Npoint,
    NpointSet,
    Nsegment,
    Pose,
    PoseSet,
    STBox,
    TBoolInst,
    TBox,
    TCbufferInst,
    TextSet,
    TFloatSeq,
    TGeogPointInst,
    TGeomPointSeq,
    TIntSeq,
    TNpointInst,
    TPoseInst,
    TRgeometryInst,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
    TTextInst,
)
from tests.conftest import TestPyMEOS

# Every value with the text its as_text writes, which str returns.
TEXT = [
    (TFloatSeq("[1.5@2001-01-01, 2.5@2001-01-02]"), "[1.5@2001-01-01 00:00:00+00, 2.5@2001-01-02 00:00:00+00]"),
    (TIntSeq("[1@2001-01-01, 2@2001-01-02]"), "[1@2001-01-01 00:00:00+00, 2@2001-01-02 00:00:00+00]"),
    (TBoolInst("t@2001-01-01"), "t@2001-01-01 00:00:00+00"),
    (TTextInst("AAA@2001-01-01"), '"AAA"@2001-01-01 00:00:00+00'),
    (
        TGeomPointSeq("SRID=4326;[Point(1 1)@2001-01-01, Point(2 2)@2001-01-02]"),
        "[POINT(1 1)@2001-01-01 00:00:00+00, POINT(2 2)@2001-01-02 00:00:00+00]",
    ),
    (TGeogPointInst("SRID=4326;Point(1 1)@2001-01-01"), "POINT(1 1)@2001-01-01 00:00:00+00"),
    (TCbufferInst("SRID=3812;Cbuffer(Point(1 1),0.5)@2001-01-01"), "Cbuffer(POINT(1 1),0.5)@2001-01-01 00:00:00+00"),
    (TPoseInst("SRID=3812;Pose(Point(1 1),0.5)@2001-01-01"), "Pose(POINT(1 1),0.5)@2001-01-01 00:00:00+00"),
    (TNpointInst("NPoint(1,0.5)@2001-01-01"), "NPoint(1,0.5)@2001-01-01 00:00:00+00"),
    (
        TRgeometryInst("SRID=3812;Polygon((0 0,1 0,0 1,0 0));Pose(Point(1 1),0.5)@2001-01-01"),
        "POLYGON((0 0,1 0,0 1,0 0));Pose(POINT(1 1),0.5)@2001-01-01 00:00:00+00",
    ),
    (IntSet("{1, 2}"), "{1, 2}"),
    (FloatSet("{1.5, 2.5}"), "{1.5, 2.5}"),
    (TextSet('{"a", "b"}'), '{"a", "b"}'),
    (TsTzSet("{2001-01-01, 2001-01-02}"), '{"2001-01-01 00:00:00+00", "2001-01-02 00:00:00+00"}'),
    (GeometrySet("SRID=4326;{Point(1 1), Point(2 2)}"), '{"POINT(1 1)", "POINT(2 2)"}'),
    (PoseSet('SRID=3812;{"Pose(Point(1 1),0.5)"}'), '{"Pose(POINT(1 1),0.5)"}'),
    (CbufferSet('SRID=3812;{"Cbuffer(Point(1 1),0.5)"}'), '{"Cbuffer(POINT(1 1),0.5)"}'),
    (NpointSet('{"NPoint(1,0.5)"}'), '{"NPoint(1,0.5)"}'),
    (IntSpan("[1, 3)"), "[1, 3)"),
    (FloatSpan("[1.5, 2.5]"), "[1.5, 2.5]"),
    (TsTzSpan("[2001-01-01, 2001-01-02]"), "[2001-01-01 00:00:00+00, 2001-01-02 00:00:00+00]"),
    (IntSpanSet("{[1, 3), [4, 5)}"), "{[1, 3), [4, 5)}"),
    (TsTzSpanSet("{[2001-01-01, 2001-01-02]}"), "{[2001-01-01 00:00:00+00, 2001-01-02 00:00:00+00]}"),
    (
        TBox("TBOXFLOAT XT([1.5, 2.5],[2001-01-01, 2001-01-02])"),
        "TBOXFLOAT XT([1.5, 2.5],[2001-01-01 00:00:00+00, 2001-01-02 00:00:00+00])",
    ),
    (
        STBox("SRID=4326;STBOX XT(((1,1),(2,2)),[2001-01-01, 2001-01-02])"),
        "SRID=4326;STBOX XT(((1,1),(2,2)),[2001-01-01 00:00:00+00, 2001-01-02 00:00:00+00])",
    ),
    (Pose("SRID=3812;Pose(Point(1 1),0.5)"), "Pose(POINT(1 1),0.5)"),
    (Cbuffer("SRID=3812;Cbuffer(Point(1 1),0.5)"), "Cbuffer(POINT(1 1),0.5)"),
    (Npoint("NPoint(1,0.5)"), "NPoint(1,0.5)"),
    (Nsegment("NSegment(1,0.2,0.5)"), "NSegment(1,0.2,0.5)"),
]
IDS = [type(v).__name__ for v, _ in TEXT]

# Every value carrying an SRID with the EWKT its as_ewkt writes.
EWKT = [
    (TEXT[i][0], srid + TEXT[i][1])
    for i, srid in (
        (4, "SRID=4326;"),
        (5, "SRID=4326;"),
        (6, "SRID=3812;"),
        (7, "SRID=3812;"),
        (8, "SRID=5676;"),
        (9, "SRID=3812;"),
        (14, "SRID=4326;"),
        (15, "SRID=3812;"),
        (16, "SRID=3812;"),
        (17, "SRID=5676;"),
        (25, "SRID=3812;"),
        (26, "SRID=3812;"),
        (27, "SRID=5676;"),
        (28, "SRID=5676;"),
    )
]
EWKT_IDS = [type(v).__name__ for v, _ in EWKT]
# The values whose binary forms carry an SRID: those of EWKT, and STBox, whose
# text carries it.
EWKB = [v for v, _ in EWKT] + [TEXT[24][0]]
EWKB_IDS = [type(v).__name__ for v in EWKB]


class TestIOForms(TestPyMEOS):
    """
    The portable readers and writers of every class, as #TestPose states
    ``test_str`` and ``test_from_as_hexwkb`` for a pose: ``str`` is ``as_text``,
    the plain forms carry no SRID and the E forms carry it, as the SQL
    ``asText``, ``asBinary``, ``asEWKT`` and ``asEWKB`` write them.
    """

    @pytest.mark.parametrize("value, text", TEXT, ids=IDS)
    def test_str_is_as_text(self, value, text):
        assert value.as_text() == text
        assert str(value) == text

    @pytest.mark.parametrize("value, text", TEXT, ids=IDS)
    def test_from_text(self, value, text):
        assert type(value).from_text(text).as_text() == text

    @pytest.mark.parametrize("value, text", TEXT, ids=IDS)
    def test_wkb_endian(self, value, text):
        assert value.as_hexwkb("NDR")[:2] == "01"
        assert value.as_hexwkb("XDR")[:2] == "00"
        assert value.as_wkb("NDR") == bytes.fromhex(value.as_hexwkb("NDR"))
        reread = type(value).from_hexwkb(value.as_hexwkb("XDR"))
        assert reread.as_hexwkb("NDR") == value.as_hexwkb("NDR")

    @pytest.mark.parametrize("value, ewkt", EWKT, ids=EWKT_IDS)
    def test_as_ewkt(self, value, ewkt):
        assert value.as_ewkt() == ewkt
        assert type(value).from_ewkt(ewkt) == value

    @pytest.mark.parametrize("value", EWKB, ids=EWKB_IDS)
    def test_ewkb_round_trip(self, value):
        cls = type(value)
        assert cls.from_ewkb(value.as_ewkb()) == value
        assert cls.from_hexewkb(value.as_hexewkb()) == value
        assert cls.from_hexewkb(value.as_hexewkb("XDR")) == value

    def test_plain_wkb_carries_no_srid(self):
        value = TGeomPointSeq("SRID=4326;[Point(1 1)@2001-01-01, Point(2 2)@2001-01-02]")
        assert TGeomPointSeq.from_hexwkb(value.as_hexwkb()).srid() == 0
        assert TGeomPointSeq.from_hexewkb(value.as_hexewkb()).srid() == 4326
        assert value.as_hexwkb() != value.as_hexewkb()
