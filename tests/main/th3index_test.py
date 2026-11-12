from copy import copy
from datetime import datetime, timezone

import pytest

from pymeos import (
    H3Index,
    H3IndexSet,
    STBox,
    TBoolSeq,
    TFloat,
    TGeogPoint,
    TH3Index,
    TH3IndexInst,
    TH3IndexSeq,
    TH3IndexSeqSet,
    TInt,
    TInterpolation,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)
from tests.conftest import TestPyMEOS

# As tests/main/tcbuffer_test.py tests the circular buffers. The cells, their
# texts and their binary forms are those of MobilityDB's
# mobilitydb/test/h3/expected/250_h3index, 251_h3indexset and 270_th3index.

TI = "880326b885fffff@2001-01-01"
TDS = "{880326b885fffff@2001-01-01, 880326b88dfffff@2001-01-02}"
TS = "[880326b885fffff@2001-01-01, 880326b88dfffff@2001-01-02]"
TSS = "{[880326b885fffff@2001-01-01, 880326b88dfffff@2001-01-02], [880326b885fffff@2001-01-03, 880326b885fffff@2001-01-04]}"


class TestTH3Index(TestPyMEOS):
    pass


class TestH3Index(TestPyMEOS):
    c = H3Index("8a2a1072b59ffff")

    def test_string_constructor(self):
        assert isinstance(self.c, H3Index)

    def test_str(self):
        assert str(self.c) == "8a2a1072b59ffff"
        assert self.c.as_text() == "8a2a1072b59ffff"
        assert repr(self.c) == "H3Index(8a2a1072b59ffff)"

    def test_from_as_text_wkb_hexwkb(self):
        assert H3Index.from_text(self.c.as_text()) == self.c
        assert H3Index.from_wkb(self.c.as_wkb()) == self.c
        assert H3Index.from_hexwkb(self.c.as_hexwkb("XDR")) == self.c
        assert self.c.as_wkb("NDR") == bytes.fromhex(self.c.as_hexwkb("NDR"))

    def test_copy(self):
        other = copy(self.c)
        assert self.c == other
        assert self.c is not other

    def test_comparisons(self):
        other = H3Index("880326b885fffff")
        assert self.c != other
        assert (self.c < other) == (self.c.cmp(other) < 0)
        assert hash(self.c) == self.c.hash()

    def test_accessors(self):
        assert self.c.cell_to_parent(self.c.get_resolution()) == self.c
        assert isinstance(self.c.cell_area(), float)
        assert isinstance(self.c.to_stbox(), STBox)
        assert self.c.to_set() == H3IndexSet("{8a2a1072b59ffff}")


class TestH3IndexSet(TestPyMEOS):
    cs = H3IndexSet("{8a2a1072b59ffff, 831c02fffffffff}")

    def test_str(self):
        assert str(self.cs) == '{"831c02fffffffff", "8a2a1072b59ffff"}'
        assert self.cs.as_text() == '{"831c02fffffffff", "8a2a1072b59ffff"}'

    def test_from_as_text_wkb_hexwkb(self):
        assert H3IndexSet.from_text(self.cs.as_text()) == self.cs
        assert H3IndexSet.from_hexwkb(self.cs.as_hexwkb()) == self.cs
        assert H3IndexSet.from_wkb(self.cs.as_wkb()) == self.cs

    # As #TestCbufferSet.test_as_ewkt, with the SRID=4326; forms of MobilityDB's outputs.
    def test_as_ewkt(self):
        assert self.cs.as_ewkt() == 'SRID=4326;{"831c02fffffffff", "8a2a1072b59ffff"}'
        assert H3IndexSet.from_ewkt(self.cs.as_ewkt()) == self.cs

    # As #TestIOForms.test_ewkb_round_trip.
    def test_as_hexewkb(self):
        cs1 = H3IndexSet("{8a2a1072b59ffff}")
        assert cs1.as_hexewkb("XDR") == "00004561000010E60000000108A2A1072B59FFFF"
        assert H3IndexSet.from_hexewkb(cs1.as_hexewkb("XDR")) == cs1
        assert H3IndexSet.from_ewkb(self.cs.as_ewkb()) == self.cs

    def test_elements(self):
        assert H3IndexSet(elements=["8a2a1072b59ffff", H3Index("831c02fffffffff")]) == self.cs
        assert self.cs.start_element() == H3Index("831c02fffffffff")
        assert self.cs.end_element() == H3Index("8a2a1072b59ffff")
        assert self.cs.element_n(1) == H3Index("8a2a1072b59ffff")
        assert self.cs.elements() == [H3Index("831c02fffffffff"), H3Index("8a2a1072b59ffff")]

    def test_set_operations(self):
        assert self.cs.contains(H3Index("831c02fffffffff"))
        assert self.cs.minus(H3Index("831c02fffffffff")) == H3IndexSet("{8a2a1072b59ffff}")
        assert self.cs.subtract_from(H3Index("831c02fffffffff")) is None
        assert self.cs.intersection(H3Index("831c02fffffffff")) == H3IndexSet("{831c02fffffffff}")
        assert self.cs.union(H3Index("880326b885fffff")) == H3IndexSet(
            "{831c02fffffffff, 8a2a1072b59ffff, 880326b885fffff}"
        )


class TestTH3IndexConstructors(TestTH3Index):
    tci = TH3IndexInst(TI)
    tcds = TH3IndexSeq(TDS)
    tcs = TH3IndexSeq(TS)
    tcss = TH3IndexSeqSet(TSS)

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tci, TH3IndexInst),
            (tcds, TH3IndexSeq),
            (tcs, TH3IndexSeq),
            (tcss, TH3IndexSeqSet),
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
        assert temporal == temporal.__class__.from_wkb(temporal.as_wkb("XDR"))

    @pytest.mark.parametrize(
        "temporal",
        [tci, tcds, tcs, tcss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_mfjson_constructor(self, temporal):
        assert '"type":"MovingH3Index"' in temporal.as_mfjson(False, 0, 15)
        assert temporal == temporal.__class__.from_mfjson(temporal.as_mfjson())

    @pytest.mark.parametrize(
        "temporal",
        [tci, tcds, tcs, tcss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other

    def test_instant_value_constructor(self):
        assert TH3IndexInst(value=H3Index("880326b885fffff"), timestamp="2001-01-01") == self.tci
        assert TH3IndexInst(value="880326b885fffff", timestamp="2001-01-01") == self.tci


class TestTH3IndexOutputs(TestTH3Index):
    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (TH3IndexInst(TI), "880326b885fffff@2001-01-01 00:00:00+00"),
            (TH3IndexSeq(TDS), "{880326b885fffff@2001-01-01 00:00:00+00, 880326b88dfffff@2001-01-02 00:00:00+00}"),
            (TH3IndexSeq(TS), "[880326b885fffff@2001-01-01 00:00:00+00, 880326b88dfffff@2001-01-02 00:00:00+00]"),
            (
                TH3IndexSeqSet(TSS),
                "{[880326b885fffff@2001-01-01 00:00:00+00, 880326b88dfffff@2001-01-02 00:00:00+00], "
                "[880326b885fffff@2001-01-03 00:00:00+00, 880326b885fffff@2001-01-04 00:00:00+00]}",
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected
        assert temporal.as_text() == expected
        assert temporal.as_wkt() == expected
        assert TH3Index.from_text(expected) == temporal

    # As #TestIOForms.test_as_ewkt and #TestTCbufferAccessors.test_srid.
    def test_as_ewkt(self):
        temporal = TH3IndexSeq(TS)
        ewkt = "SRID=4326;[880326b885fffff@2001-01-01 00:00:00+00, 880326b88dfffff@2001-01-02 00:00:00+00]"
        assert temporal.as_ewkt() == ewkt
        assert TH3Index.from_ewkt(ewkt) == temporal
        assert temporal.srid() == 4326

    # As #TestIOForms.test_ewkb_round_trip.
    @pytest.mark.parametrize(
        "temporal",
        [TH3IndexInst(TI), TH3IndexSeq(TDS), TH3IndexSeq(TS), TH3IndexSeqSet(TSS)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_ewkb(self, temporal):
        assert TH3Index.from_ewkb(temporal.as_ewkb()) == temporal
        assert TH3Index.from_hexewkb(temporal.as_hexewkb("XDR")) == temporal
        assert temporal.as_hexewkb("XDR")[:2] == "00"

    def test_repr(self):
        assert repr(TH3IndexInst(TI)) == "TH3IndexInst(880326b885fffff@2001-01-01 00:00:00+00)"


class TestTH3IndexAccessors(TestTH3Index):
    tcs = TH3IndexSeq(TS)

    def test_interpolation(self):
        assert self.tcs.interpolation() == TInterpolation.STEPWISE

    def test_bounding_box(self):
        assert isinstance(self.tcs.bounding_box(), STBox)

    def test_get_resolution(self):
        resolution = self.tcs.get_resolution()
        assert isinstance(resolution, TInt)
        assert resolution.start_value() == H3Index("880326b885fffff").get_resolution()

    def test_is_valid_cell(self):
        assert self.tcs.is_valid_cell() == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_cell_area(self):
        assert isinstance(self.tcs.cell_area(), TFloat)

    def test_cell_to_parent(self):
        resolution = H3Index("880326b885fffff").get_resolution()
        parent = H3Index("880326b885fffff").cell_to_parent(0 if resolution == 0 else resolution - 1)
        assert self.tcs.cell_to_parent(0 if resolution == 0 else resolution - 1).start_value() == parent

    def test_cell_to_point(self):
        assert isinstance(self.tcs.cell_to_point(), TGeogPoint)


class TestTH3IndexValueFunctions(TestTH3Index):
    value = H3Index("880326b885fffff")
    other = H3Index("880326b88dfffff")
    ts = TH3IndexSeq(TS)
    tss = TH3IndexSeqSet(TSS)

    @pytest.mark.parametrize(
        "base, expected",
        [
            (datetime(2001, 1, 1, tzinfo=timezone.utc), TH3IndexInst("880326b885fffff@2001-01-01")),
            (
                TsTzSet("{2001-01-01, 2001-01-02}"),
                TH3IndexSeq("{880326b885fffff@2001-01-01, 880326b885fffff@2001-01-02}"),
            ),
            (
                TsTzSpan("[2001-01-01, 2001-01-02]"),
                TH3IndexSeq("[880326b885fffff@2001-01-01, 880326b885fffff@2001-01-02]"),
            ),
            (
                TsTzSpanSet("{[2001-01-01, 2001-01-02], [2001-01-03, 2001-01-04]}"),
                TH3IndexSeqSet(
                    "{[880326b885fffff@2001-01-01, 880326b885fffff@2001-01-02], [880326b885fffff@2001-01-03, 880326b885fffff@2001-01-04]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, base, expected):
        assert TH3Index.from_base_time(self.value, base) == expected

    def test_from_base_temporal_constructor(self):
        assert TH3Index.from_base_temporal(self.value, self.ts) == TH3IndexSeq(
            "[880326b885fffff@2001-01-01, 880326b885fffff@2001-01-02]"
        )

    def test_start_end_value(self):
        assert self.tss.start_value() == self.value
        assert self.tss.end_value() == H3Index("880326b885fffff")

    def test_value_set(self):
        assert self.ts.value_set() == {self.value, self.other}

    def test_value_at_timestamp(self):
        assert self.ts.value_at_timestamp(datetime(2001, 1, 2, tzinfo=timezone.utc)) == self.other


class TestTH3IndexGeneratedFamilies(TestTH3Index):
    ts = TH3IndexSeq(TS)
    value = H3Index("880326b885fffff")

    def test_ever_always(self):
        assert self.ts.ever_equal(self.value) is True
        assert self.ts.always_equal(self.value) is False
        assert self.ts.ever_not_equal(self.value) is True
        assert self.ts.always_not_equal(self.value) is False
        assert self.ts.never_equal(self.value) is False
        assert self.ts.ever_equal(H3IndexSet("{880326b88dfffff}")) is True
        assert self.ts.ever_equal(self.ts) is True

    def test_temporal_comparison(self):
        assert self.ts.temporal_equal(self.value) == TBoolSeq("[t@2001-01-01, f@2001-01-02]")
        assert self.ts.temporal_not_equal(self.value) == TBoolSeq("[f@2001-01-01, t@2001-01-02]")
        assert self.ts.temporal_equal(self.ts) == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_restriction(self):
        assert self.ts.at(self.value) == TH3IndexSeqSet("{[880326b885fffff@2001-01-01, 880326b885fffff@2001-01-02)}")
        assert self.ts.minus(self.value) == TH3IndexSeqSet("{[880326b88dfffff@2001-01-02]}")
        assert self.ts.at(TsTzSpan("[2001-01-02, 2001-01-03]")) == TH3IndexSeq("[880326b88dfffff@2001-01-02]")
