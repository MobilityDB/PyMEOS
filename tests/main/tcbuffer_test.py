from copy import copy
from datetime import datetime, timezone

import pytest
from shapely import Point

from pymeos import (
    Cbuffer,
    CbufferSet,
    TBool,
    TCbuffer,
    TCbufferInst,
    TCbufferSeq,
    TCbufferSeqSet,
    TInterpolation,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)
from tests.conftest import TestPyMEOS


class TestTCbuffer(TestPyMEOS):
    pass


class TestTCbufferConstructors(TestTCbuffer):
    tci = TCbufferInst("Cbuffer(Point(1 1), 0.5)@2019-09-01")
    tcds = TCbufferSeq("{Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02}")
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")
    tcss = TCbufferSeqSet(
        "{[Cbuffer(Point(1 1), 0.5)@2019-09-01,"
        " Cbuffer(Point(2 2), 0.3)@2019-09-02],"
        "[Cbuffer(Point(1 1), 0.5)@2019-09-03,"
        " Cbuffer(Point(1 1), 0.5)@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tci, TCbufferInst),
            (tcds, TCbufferSeq),
            (tcs, TCbufferSeq),
            (tcss, TCbufferSeqSet),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_string_constructor(self, temporal, expected_type):
        assert isinstance(temporal, expected_type)

    @pytest.mark.parametrize(
        "temporal",
        [tci, tcds, tcs, tcss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_hexwkb_constructor(self, temporal):
        assert temporal == temporal.__class__.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        "temporal",
        [tci, tcds, tcs, tcss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTCbufferOutputs(TestTCbuffer):
    tci = TCbufferInst("Cbuffer(Point(1 1), 0.5)@2019-09-01")
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")

    def test_repr(self):
        assert isinstance(repr(self.tci), str)

    def test_as_wkt(self):
        assert isinstance(self.tcs.as_wkt(), str)


class TestTCbufferAccessors(TestTCbuffer):
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")

    def test_interpolation(self):
        assert self.tcs.interpolation() == TInterpolation.LINEAR

    def test_srid(self):
        assert isinstance(self.tcs.srid(), int)

    def test_to_tfloat(self):
        assert self.tcs.to_tfloat() is not None

    def test_to_tgeompoint(self):
        assert self.tcs.to_tgeompoint() is not None


class TestTCbufferEverAlways(TestTCbuffer):
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")

    def test_ever_equal(self):
        assert isinstance(self.tcs.ever_equal(Cbuffer("Cbuffer(Point(1 1), 0.5)")), bool)

    def test_never_not_equal(self):
        assert isinstance(self.tcs.never_not_equal(Cbuffer("Cbuffer(Point(1 1), 0.5)")), bool)


class TestTCbufferDistance(TestTCbuffer):
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")

    def test_nearest_approach_distance(self):
        assert isinstance(
            self.tcs.nearest_approach_distance(Cbuffer("Cbuffer(Point(0 0), 0.0)")),
            float,
        )


class TestTCbufferSpatialRelationships(TestTCbuffer):
    tcs = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")
    other = Cbuffer("Cbuffer(Point(1 1), 0.5)")

    def test_ever_relationships(self):
        assert isinstance(self.tcs.ever_intersects(self.other), bool)
        assert isinstance(self.tcs.is_ever_disjoint(self.other), bool)
        assert isinstance(self.tcs.ever_intersects(Point(1, 1)), bool)
        assert isinstance(self.tcs.is_ever_within_distance(self.other, 1.0), bool)

    def test_always_relationships(self):
        assert isinstance(self.tcs.always_intersects(self.other), bool)
        assert isinstance(self.tcs.is_always_disjoint(self.other), bool)

    # As #TestTRgeometrySpatialRelationships.test_ever_relationships, values
    # decided by a buffer around the whole motion and a motion far from it.
    def test_containment_and_temporal_arms(self):
        around = Cbuffer("Cbuffer(Point(1.5 1.5), 10)")
        far = TCbufferSeq("[Cbuffer(Point(100 100), 0.5)@2019-09-01, Cbuffer(Point(101 101), 0.5)@2019-09-02]")
        assert self.tcs.is_ever_contained_in(around) is True
        assert self.tcs.is_always_contained_in(around) is True
        assert self.tcs.is_ever_contained_in(Point(100, 100)) is False
        assert self.tcs.is_always_contained_in(Point(100, 100)) is False
        assert self.tcs.is_ever_coveredby(around) is True
        assert self.tcs.is_always_coveredby(around) is True
        assert self.tcs.is_ever_coveredby(Point(100, 100)) is False
        assert self.tcs.is_always_coveredby(Point(100, 100)) is False
        assert self.tcs.is_ever_contains(far) is False
        assert self.tcs.is_always_contains(far) is False
        assert self.tcs.is_always_covers(far) is False
        assert self.tcs.is_ever_disjoint(far) is True

    def test_temporal_relationships(self):
        r = self.tcs.intersects(self.other)
        assert r is None or isinstance(r, TBool)
        r = self.tcs.within_distance(self.other, 1.0)
        assert r is None or isinstance(r, TBool)
        r = self.tcs.disjoint(Point(1, 1))
        assert r is None or isinstance(r, TBool)


class TestCbuffer(TestPyMEOS):
    c = Cbuffer("Cbuffer(Point(1 1), 0.5)")

    def test_string_constructor(self):
        assert isinstance(self.c, Cbuffer)

    def test_str(self):
        assert str(self.c) == "Cbuffer(POINT(1 1),0.5)"

    def test_from_as_hexwkb(self):
        assert self.c == Cbuffer.from_hexwkb(self.c.as_hexwkb())

    def test_copy(self):
        other = copy(self.c)
        assert self.c == other
        assert self.c is not other


class TestCbufferSet(TestPyMEOS):
    cs = CbufferSet('{"Cbuffer(Point(1 1),0.5)", "Cbuffer(Point(2 2),0.3)"}')
    cs_srid = CbufferSet('SRID=4326;{"Cbuffer(Point(1 1),0.5)"}')

    def test_str(self):
        assert str(self.cs) == '{"Cbuffer(POINT(1 1),0.5)", "Cbuffer(POINT(2 2),0.3)"}'

    def test_as_text(self):
        assert self.cs.as_text() == '{"Cbuffer(POINT(1 1),0.5)", "Cbuffer(POINT(2 2),0.3)"}'
        assert self.cs.as_wkt() == self.cs.as_text()

    def test_as_ewkt(self):
        assert self.cs_srid.as_ewkt() == 'SRID=4326;{"Cbuffer(POINT(1 1),0.5)"}'
        assert self.cs_srid.as_text() == '{"Cbuffer(POINT(1 1),0.5)"}'


class TestTCbufferValueFunctions(TestTCbuffer):
    value = Cbuffer("Cbuffer(Point(1 1), 0.5)")
    other = Cbuffer("Cbuffer(Point(2 2), 0.3)")
    ti = TCbufferInst("Cbuffer(Point(1 1), 0.5)@2019-09-01")
    ts = TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02]")
    tss = TCbufferSeqSet(
        "{[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(2 2), 0.3)@2019-09-02], [Cbuffer(Point(1 1), 0.5)@2019-09-03, Cbuffer(Point(1 1), 0.5)@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "base, expected",
        [
            (datetime(2019, 9, 1, tzinfo=timezone.utc), TCbufferInst("Cbuffer(Point(1 1), 0.5)@2019-09-01")),
            (
                TsTzSet("{2019-09-01, 2019-09-02}"),
                TCbufferSeq("{Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(1 1), 0.5)@2019-09-02}"),
            ),
            (
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                TCbufferSeq("[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(1 1), 0.5)@2019-09-02]"),
            ),
            (
                TsTzSpanSet("{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}"),
                TCbufferSeqSet(
                    "{[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(1 1), 0.5)@2019-09-02], [Cbuffer(Point(1 1), 0.5)@2019-09-03, Cbuffer(Point(1 1), 0.5)@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, base, expected):
        assert TCbuffer.from_base_time(self.value, base, TInterpolation.LINEAR) == expected

    def test_from_base_temporal_constructor(self):
        assert TCbuffer.from_base_temporal(self.value, self.tss) == TCbufferSeqSet(
            "{[Cbuffer(Point(1 1), 0.5)@2019-09-01, Cbuffer(Point(1 1), 0.5)@2019-09-02], [Cbuffer(Point(1 1), 0.5)@2019-09-03, Cbuffer(Point(1 1), 0.5)@2019-09-05]}"
        )

    @pytest.mark.parametrize("temporal", [ti, ts, tss], ids=["Instant", "Sequence", "SequenceSet"])
    def test_from_as_mfjson_constructor(self, temporal):
        assert temporal.__class__.from_mfjson(temporal.as_mfjson()) == temporal

    def test_start_value(self):
        assert self.tss.start_value() == self.value

    def test_end_value(self):
        assert self.tss.end_value() == self.value

    def test_value_set(self):
        assert self.tss.value_set() == {self.value, self.other}

    def test_value_at_timestamp(self):
        assert self.ts.value_at_timestamp(datetime(2019, 9, 2, tzinfo=timezone.utc)) == self.other
