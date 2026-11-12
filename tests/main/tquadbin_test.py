from copy import copy
from datetime import datetime, timezone

import pytest

from pymeos import (
    Quadbin,
    QuadbinSet,
    STBox,
    TBoolSeq,
    TFloat,
    TGeomPoint,
    TInt,
    TInterpolation,
    TQuadbin,
    TQuadbinInst,
    TQuadbinSeq,
    TQuadbinSeqSet,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)
from tests.conftest import TestPyMEOS

# As tests/main/tcbuffer_test.py tests the circular buffers. The cells, their
# texts and their binary forms are those of MobilityDB's
# mobilitydb/test/quadbin/expected/350_quadbin, 351_quadbinset and 352_tquadbin.

TI = "480fffffffffffff@2001-01-01"
TDS = "{480fffffffffffff@2001-01-01, 48427fffffffffff@2001-01-02}"
TS = "[480fffffffffffff@2001-01-01, 48427fffffffffff@2001-01-02]"
TSS = "{[480fffffffffffff@2001-01-01, 48427fffffffffff@2001-01-02], [48a6227affffffff@2001-01-03, 48a6227affffffff@2001-01-04]}"


class TestTQuadbin(TestPyMEOS):
    pass


class TestQuadbin(TestPyMEOS):
    c = Quadbin("48427fffffffffff")

    def test_string_constructor(self):
        assert isinstance(self.c, Quadbin)

    def test_str(self):
        assert str(self.c) == "48427fffffffffff"
        assert self.c.as_text() == "48427fffffffffff"
        assert repr(self.c) == "Quadbin(48427fffffffffff)"

    def test_as_hexwkb(self):
        assert self.c.as_hexwkb("NDR") == "01470000FFFFFFFFFF7F4248"
        assert self.c.as_hexwkb("XDR") == "0000470048427FFFFFFFFFFF"
        assert self.c.as_wkb("NDR") == bytes.fromhex("01470000FFFFFFFFFF7F4248")

    def test_from_as_text_wkb_hexwkb(self):
        assert Quadbin.from_text(self.c.as_text()) == self.c
        assert Quadbin.from_wkb(self.c.as_wkb()) == self.c
        assert Quadbin.from_hexwkb(self.c.as_hexwkb("XDR")) == self.c
        assert self.c.as_wkb("NDR") == bytes.fromhex(self.c.as_hexwkb("NDR"))

    def test_copy(self):
        other = copy(self.c)
        assert self.c == other
        assert self.c is not other

    def test_comparisons(self):
        other = Quadbin("48a6227affffffff")
        assert self.c != other
        assert (self.c < other) == (self.c.cmp(other) < 0)
        assert hash(self.c) == self.c.hash()

    def test_accessors(self):
        assert self.c.cell_to_parent(self.c.get_resolution()) == self.c
        assert isinstance(self.c.cell_area(), float)
        assert isinstance(self.c.to_stbox(), STBox)
        assert self.c.to_set() == QuadbinSet("{48427fffffffffff}")


class TestQuadbinSet(TestPyMEOS):
    cs = QuadbinSet("{480fffffffffffff, 48427fffffffffff}")

    def test_str(self):
        assert str(self.cs) == '{"480fffffffffffff", "48427fffffffffff"}'
        assert self.cs.as_text() == '{"480fffffffffffff", "48427fffffffffff"}'

    def test_from_as_text_wkb_hexwkb(self):
        assert QuadbinSet.from_text(self.cs.as_text()) == self.cs
        assert QuadbinSet.from_hexwkb(self.cs.as_hexwkb()) == self.cs
        assert QuadbinSet.from_wkb(self.cs.as_wkb()) == self.cs

    # As #TestCbufferSet.test_as_ewkt, with the SRID=4326; forms of MobilityDB's outputs.
    def test_as_ewkt(self):
        assert self.cs.as_ewkt() == 'SRID=4326;{"480fffffffffffff", "48427fffffffffff"}'
        assert QuadbinSet.from_ewkt(self.cs.as_ewkt()) == self.cs

    # As #TestIOForms.test_ewkb_round_trip.
    def test_as_hexewkb(self):
        cs1 = QuadbinSet("{480fffffffffffff}")
        assert cs1.as_hexewkb("XDR") == "00004841000010E600000001480FFFFFFFFFFFFF"
        assert QuadbinSet.from_hexewkb(cs1.as_hexewkb("XDR")) == cs1
        assert QuadbinSet.from_ewkb(self.cs.as_ewkb()) == self.cs

    def test_elements(self):
        assert QuadbinSet(elements=["48427fffffffffff", Quadbin("480fffffffffffff")]) == self.cs
        assert self.cs.start_element() == Quadbin("480fffffffffffff")
        assert self.cs.end_element() == Quadbin("48427fffffffffff")
        assert self.cs.element_n(1) == Quadbin("48427fffffffffff")
        assert self.cs.elements() == [Quadbin("480fffffffffffff"), Quadbin("48427fffffffffff")]

    def test_set_operations(self):
        assert self.cs.contains(Quadbin("480fffffffffffff"))
        assert self.cs.minus(Quadbin("480fffffffffffff")) == QuadbinSet("{48427fffffffffff}")
        assert self.cs.subtract_from(Quadbin("480fffffffffffff")) is None
        assert self.cs.intersection(Quadbin("480fffffffffffff")) == QuadbinSet("{480fffffffffffff}")
        assert self.cs.union(Quadbin("48a6227affffffff")) == QuadbinSet(
            "{480fffffffffffff, 48427fffffffffff, 48a6227affffffff}"
        )


class TestTQuadbinConstructors(TestTQuadbin):
    tci = TQuadbinInst(TI)
    tcds = TQuadbinSeq(TDS)
    tcs = TQuadbinSeq(TS)
    tcss = TQuadbinSeqSet(TSS)

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tci, TQuadbinInst),
            (tcds, TQuadbinSeq),
            (tcs, TQuadbinSeq),
            (tcss, TQuadbinSeqSet),
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
        assert '"type":"MovingQuadbin"' in temporal.as_mfjson(False, 0, 15)
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
        assert TQuadbinInst(value=Quadbin("480fffffffffffff"), timestamp="2001-01-01") == self.tci
        assert TQuadbinInst(value="480fffffffffffff", timestamp="2001-01-01") == self.tci


class TestTQuadbinOutputs(TestTQuadbin):
    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (TQuadbinInst(TI), "480fffffffffffff@2001-01-01 00:00:00+00"),
            (TQuadbinSeq(TDS), "{480fffffffffffff@2001-01-01 00:00:00+00, 48427fffffffffff@2001-01-02 00:00:00+00}"),
            (TQuadbinSeq(TS), "[480fffffffffffff@2001-01-01 00:00:00+00, 48427fffffffffff@2001-01-02 00:00:00+00]"),
            (
                TQuadbinSeqSet(TSS),
                "{[480fffffffffffff@2001-01-01 00:00:00+00, 48427fffffffffff@2001-01-02 00:00:00+00], "
                "[48a6227affffffff@2001-01-03 00:00:00+00, 48a6227affffffff@2001-01-04 00:00:00+00]}",
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected
        assert temporal.as_text() == expected
        assert temporal.as_wkt() == expected
        assert TQuadbin.from_text(expected) == temporal

    # As #TestIOForms.test_as_ewkt and #TestTCbufferAccessors.test_srid.
    def test_as_ewkt(self):
        temporal = TQuadbinSeq(TS)
        ewkt = "SRID=4326;[480fffffffffffff@2001-01-01 00:00:00+00, 48427fffffffffff@2001-01-02 00:00:00+00]"
        assert temporal.as_ewkt() == ewkt
        assert TQuadbin.from_ewkt(ewkt) == temporal
        assert temporal.srid() == 4326

    # As #TestIOForms.test_ewkb_round_trip.
    @pytest.mark.parametrize(
        "temporal",
        [TQuadbinInst(TI), TQuadbinSeq(TDS), TQuadbinSeq(TS), TQuadbinSeqSet(TSS)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_ewkb(self, temporal):
        assert TQuadbin.from_ewkb(temporal.as_ewkb()) == temporal
        assert TQuadbin.from_hexewkb(temporal.as_hexewkb("XDR")) == temporal
        assert temporal.as_hexewkb("XDR")[:2] == "00"

    def test_repr(self):
        assert repr(TQuadbinInst(TI)) == "TQuadbinInst(480fffffffffffff@2001-01-01 00:00:00+00)"


class TestTQuadbinAccessors(TestTQuadbin):
    tcs = TQuadbinSeq(TS)

    def test_interpolation(self):
        assert self.tcs.interpolation() == TInterpolation.STEPWISE

    def test_bounding_box(self):
        assert isinstance(self.tcs.bounding_box(), STBox)

    def test_get_resolution(self):
        resolution = self.tcs.get_resolution()
        assert isinstance(resolution, TInt)
        assert resolution.start_value() == Quadbin("480fffffffffffff").get_resolution()

    def test_is_valid_cell(self):
        assert self.tcs.is_valid_cell() == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_cell_area(self):
        assert isinstance(self.tcs.cell_area(), TFloat)

    def test_cell_to_parent(self):
        resolution = Quadbin("480fffffffffffff").get_resolution()
        parent = Quadbin("480fffffffffffff").cell_to_parent(0 if resolution == 0 else resolution - 1)
        assert self.tcs.cell_to_parent(0 if resolution == 0 else resolution - 1).start_value() == parent

    def test_cell_to_point(self):
        assert isinstance(self.tcs.cell_to_point(), TGeomPoint)


class TestTQuadbinValueFunctions(TestTQuadbin):
    value = Quadbin("480fffffffffffff")
    other = Quadbin("48427fffffffffff")
    ts = TQuadbinSeq(TS)
    tss = TQuadbinSeqSet(TSS)

    @pytest.mark.parametrize(
        "base, expected",
        [
            (datetime(2001, 1, 1, tzinfo=timezone.utc), TQuadbinInst("480fffffffffffff@2001-01-01")),
            (
                TsTzSet("{2001-01-01, 2001-01-02}"),
                TQuadbinSeq("{480fffffffffffff@2001-01-01, 480fffffffffffff@2001-01-02}"),
            ),
            (
                TsTzSpan("[2001-01-01, 2001-01-02]"),
                TQuadbinSeq("[480fffffffffffff@2001-01-01, 480fffffffffffff@2001-01-02]"),
            ),
            (
                TsTzSpanSet("{[2001-01-01, 2001-01-02], [2001-01-03, 2001-01-04]}"),
                TQuadbinSeqSet(
                    "{[480fffffffffffff@2001-01-01, 480fffffffffffff@2001-01-02], [480fffffffffffff@2001-01-03, 480fffffffffffff@2001-01-04]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, base, expected):
        assert TQuadbin.from_base_time(self.value, base) == expected

    def test_from_base_temporal_constructor(self):
        assert TQuadbin.from_base_temporal(self.value, self.ts) == TQuadbinSeq(
            "[480fffffffffffff@2001-01-01, 480fffffffffffff@2001-01-02]"
        )

    def test_start_end_value(self):
        assert self.tss.start_value() == self.value
        assert self.tss.end_value() == Quadbin("48a6227affffffff")

    def test_value_set(self):
        assert self.ts.value_set() == {self.value, self.other}

    def test_value_at_timestamp(self):
        assert self.ts.value_at_timestamp(datetime(2001, 1, 2, tzinfo=timezone.utc)) == self.other


class TestTQuadbinGeneratedFamilies(TestTQuadbin):
    ts = TQuadbinSeq(TS)
    value = Quadbin("480fffffffffffff")

    def test_ever_always(self):
        assert self.ts.ever_equal(self.value) is True
        assert self.ts.always_equal(self.value) is False
        assert self.ts.ever_not_equal(self.value) is True
        assert self.ts.always_not_equal(self.value) is False
        assert self.ts.never_equal(self.value) is False
        assert self.ts.ever_equal(QuadbinSet("{48427fffffffffff}")) is True
        assert self.ts.ever_equal(self.ts) is True

    def test_temporal_comparison(self):
        assert self.ts.temporal_equal(self.value) == TBoolSeq("[t@2001-01-01, f@2001-01-02]")
        assert self.ts.temporal_not_equal(self.value) == TBoolSeq("[f@2001-01-01, t@2001-01-02]")
        assert self.ts.temporal_equal(self.ts) == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_restriction(self):
        assert self.ts.at(self.value) == TQuadbinSeqSet("{[480fffffffffffff@2001-01-01, 480fffffffffffff@2001-01-02)}")
        assert self.ts.minus(self.value) == TQuadbinSeqSet("{[48427fffffffffff@2001-01-02]}")
        assert self.ts.at(TsTzSpan("[2001-01-02, 2001-01-03]")) == TQuadbinSeq("[48427fffffffffff@2001-01-02]")
