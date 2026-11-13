import pytest

from pymeos import (
    Cbuffer,
    CbufferSet,
    FloatSet,
    FloatSpan,
    GeometrySet,
    H3Index,
    H3IndexSet,
    IntSet,
    IntSpan,
    IntSpanSet,
    Npoint,
    NpointSet,
    Nsegment,
    Pose,
    PoseSet,
    Quadbin,
    QuadbinSet,
    S2Cell,
    S2CellSet,
    STBox,
    TBoolInst,
    TBox,
    TCbufferInst,
    TextSet,
    TFloatSeq,
    TGeogPointInst,
    TGeomPointSeq,
    TH3IndexInst,
    TIntSeq,
    TNpointInst,
    TPoseInst,
    TQuadbinInst,
    TRgeometryInst,
    TS2CellSeq,
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
    # The cells, which carry no SRID, as MobilityDB's 350_quadbin, 600_s2cell,
    # 250_h3index, 351_quadbinset, 352_tquadbin and 603_ts2cell write them.
    (Quadbin("48427fffffffffff"), "48427fffffffffff"),
    (S2Cell("47c3c444c"), "47c3c444c"),
    (H3Index("8a2a1072b59ffff"), "8a2a1072b59ffff"),
    (QuadbinSet("{480fffffffffffff, 48427fffffffffff}"), '{"480fffffffffffff", "48427fffffffffff"}'),
    (S2CellSet("{47c3c444c000000c, 47c3c444c0000004}"), '{"47c3c444c0000004", "47c3c444c000000c"}'),
    (H3IndexSet("{8a2a1072b59ffff, 831c02fffffffff}"), '{"831c02fffffffff", "8a2a1072b59ffff"}'),
    (TQuadbinInst("480fffffffffffff@2001-01-01"), "480fffffffffffff@2001-01-01 00:00:00+00"),
    (
        TS2CellSeq("[47c3c3@2001-01-01, 54b5c9@2001-01-02]"),
        "[47c3c3@2001-01-01 00:00:00+00, 54b5c9@2001-01-02 00:00:00+00]",
    ),
    (TH3IndexInst("880326b885fffff@2001-01-01"), "880326b885fffff@2001-01-01 00:00:00+00"),
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
        # A cell set or temporal cell carries the SRID of its grid in its
        # bounding box, as MobilityDB's 351_quadbinset, 601_s2cellset,
        # 251_h3indexset, 352_tquadbin, 603_ts2cell and 270_th3index write it.
        (32, "SRID=4326;"),
        (33, "SRID=4326;"),
        (34, "SRID=4326;"),
        (35, "SRID=4326;"),
        (36, "SRID=4326;"),
        (37, "SRID=4326;"),
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
