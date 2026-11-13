from copy import copy
from datetime import datetime, timezone

import pytest

from pymeos import (
    S2Cell,
    S2CellSet,
    STBox,
    TBoolSeq,
    TFloat,
    TGeogPoint,
    TInt,
    TInterpolation,
    TS2Cell,
    TS2CellInst,
    TS2CellSeq,
    TS2CellSeqSet,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)
from tests.conftest import TestPyMEOS

# As tests/main/tcbuffer_test.py tests the circular buffers. The cells, their
# texts and their binary forms are those of MobilityDB's
# mobilitydb/test/s2cell/expected/600_s2cell, 601_s2cellset and 603_ts2cell.

TI = "47c3c3@2001-01-01"
TDS = "{47c3c3@2001-01-01, 54b5c9@2001-01-02}"
TS = "[47c3c3@2001-01-01, 54b5c9@2001-01-02]"
TSS = "{[47c3c3@2001-01-01, 54b5c9@2001-01-02], [47c3c3@2001-01-03, 47c3c3@2001-01-04]}"


class TestTS2Cell(TestPyMEOS):
    pass


class TestS2Cell(TestPyMEOS):
    c = S2Cell("47c3c444c")

    def test_string_constructor(self):
        assert isinstance(self.c, S2Cell)

    def test_str(self):
        assert str(self.c) == "47c3c444c"
        assert self.c.as_text() == "47c3c444c"
        assert repr(self.c) == "S2Cell(47c3c444c)"

    def test_as_hexwkb(self):
        assert self.c.as_hexwkb("NDR") == "01550000000000C044C4C347"
        assert self.c.as_hexwkb("XDR") == "0000550047C3C444C0000000"
        assert self.c.as_wkb("NDR") == bytes.fromhex("01550000000000C044C4C347")

    def test_from_as_text_wkb_hexwkb(self):
        assert S2Cell.from_text(self.c.as_text()) == self.c
        assert S2Cell.from_wkb(self.c.as_wkb()) == self.c
        assert S2Cell.from_hexwkb(self.c.as_hexwkb("XDR")) == self.c
        assert self.c.as_wkb("NDR") == bytes.fromhex(self.c.as_hexwkb("NDR"))

    def test_copy(self):
        other = copy(self.c)
        assert self.c == other
        assert self.c is not other

    def test_comparisons(self):
        other = S2Cell("54b5c9")
        assert self.c != other
        assert (self.c < other) == (self.c.cmp(other) < 0)
        assert hash(self.c) == self.c.hash()

    def test_accessors(self):
        assert self.c.cell_to_parent(self.c.get_resolution()) == self.c
        assert isinstance(self.c.cell_area(), float)
        assert isinstance(self.c.to_stbox(), STBox)
        assert self.c.to_set() == S2CellSet("{47c3c444c}")


class TestS2CellSet(TestPyMEOS):
    cs = S2CellSet("{47c3c444c000000c, 47c3c444c0000004}")

    def test_str(self):
        assert str(self.cs) == '{"47c3c444c0000004", "47c3c444c000000c"}'
        assert self.cs.as_text() == '{"47c3c444c0000004", "47c3c444c000000c"}'

    def test_from_as_text_wkb_hexwkb(self):
        assert S2CellSet.from_text(self.cs.as_text()) == self.cs
        assert S2CellSet.from_hexwkb(self.cs.as_hexwkb()) == self.cs
        assert S2CellSet.from_wkb(self.cs.as_wkb()) == self.cs

    # As #TestCbufferSet.test_as_ewkt, with the SRID=4326; forms of MobilityDB's outputs.
    def test_as_ewkt(self):
        assert self.cs.as_ewkt() == 'SRID=4326;{"47c3c444c0000004", "47c3c444c000000c"}'
        assert S2CellSet.from_ewkt(self.cs.as_ewkt()) == self.cs

    # As #TestIOForms.test_ewkb_round_trip.
    def test_as_hexewkb(self):
        cs1 = S2CellSet("{47c3c444c000000c}")
        assert cs1.as_hexewkb("XDR") == "00005661000010E60000000147C3C444C000000C"
        assert S2CellSet.from_hexewkb(cs1.as_hexewkb("XDR")) == cs1
        assert S2CellSet.from_ewkb(self.cs.as_ewkb()) == self.cs

    def test_elements(self):
        assert S2CellSet(elements=["47c3c444c000000c", S2Cell("47c3c444c0000004")]) == self.cs
        assert self.cs.start_element() == S2Cell("47c3c444c0000004")
        assert self.cs.end_element() == S2Cell("47c3c444c000000c")
        assert self.cs.element_n(1) == S2Cell("47c3c444c000000c")
        assert self.cs.elements() == [S2Cell("47c3c444c0000004"), S2Cell("47c3c444c000000c")]

    def test_set_operations(self):
        assert self.cs.contains(S2Cell("47c3c444c0000004"))
        assert self.cs.minus(S2Cell("47c3c444c0000004")) == S2CellSet("{47c3c444c000000c}")
        assert self.cs.subtract_from(S2Cell("47c3c444c0000004")) is None
        assert self.cs.intersection(S2Cell("47c3c444c0000004")) == S2CellSet("{47c3c444c0000004}")
        assert self.cs.union(S2Cell("54b5c9")) == S2CellSet("{47c3c444c0000004, 47c3c444c000000c, 54b5c9}")


class TestTS2CellConstructors(TestTS2Cell):
    tci = TS2CellInst(TI)
    tcds = TS2CellSeq(TDS)
    tcs = TS2CellSeq(TS)
    tcss = TS2CellSeqSet(TSS)

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tci, TS2CellInst),
            (tcds, TS2CellSeq),
            (tcs, TS2CellSeq),
            (tcss, TS2CellSeqSet),
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
        assert '"type":"MovingS2Cell"' in temporal.as_mfjson(False, 0, 15)
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
        assert TS2CellInst(value=S2Cell("47c3c3"), timestamp="2001-01-01") == self.tci
        assert TS2CellInst(value="47c3c3", timestamp="2001-01-01") == self.tci


class TestTS2CellOutputs(TestTS2Cell):
    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (TS2CellInst(TI), "47c3c3@2001-01-01 00:00:00+00"),
            (TS2CellSeq(TDS), "{47c3c3@2001-01-01 00:00:00+00, 54b5c9@2001-01-02 00:00:00+00}"),
            (TS2CellSeq(TS), "[47c3c3@2001-01-01 00:00:00+00, 54b5c9@2001-01-02 00:00:00+00]"),
            (
                TS2CellSeqSet(TSS),
                "{[47c3c3@2001-01-01 00:00:00+00, 54b5c9@2001-01-02 00:00:00+00], "
                "[47c3c3@2001-01-03 00:00:00+00, 47c3c3@2001-01-04 00:00:00+00]}",
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected
        assert temporal.as_text() == expected
        assert temporal.as_wkt() == expected
        assert TS2Cell.from_text(expected) == temporal

    # As #TestIOForms.test_as_ewkt and #TestTCbufferAccessors.test_srid.
    def test_as_ewkt(self):
        temporal = TS2CellSeq(TS)
        ewkt = "SRID=4326;[47c3c3@2001-01-01 00:00:00+00, 54b5c9@2001-01-02 00:00:00+00]"
        assert temporal.as_ewkt() == ewkt
        assert TS2Cell.from_ewkt(ewkt) == temporal
        assert temporal.srid() == 4326

    # As #TestIOForms.test_ewkb_round_trip.
    @pytest.mark.parametrize(
        "temporal",
        [TS2CellInst(TI), TS2CellSeq(TDS), TS2CellSeq(TS), TS2CellSeqSet(TSS)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_ewkb(self, temporal):
        assert TS2Cell.from_ewkb(temporal.as_ewkb()) == temporal
        assert TS2Cell.from_hexewkb(temporal.as_hexewkb("XDR")) == temporal
        assert temporal.as_hexewkb("XDR")[:2] == "00"

    def test_repr(self):
        assert repr(TS2CellInst(TI)) == "TS2CellInst(47c3c3@2001-01-01 00:00:00+00)"


class TestTS2CellAccessors(TestTS2Cell):
    tcs = TS2CellSeq(TS)

    def test_interpolation(self):
        assert self.tcs.interpolation() == TInterpolation.STEPWISE

    def test_bounding_box(self):
        assert isinstance(self.tcs.bounding_box(), STBox)

    def test_get_resolution(self):
        resolution = self.tcs.get_resolution()
        assert isinstance(resolution, TInt)
        assert resolution.start_value() == S2Cell("47c3c3").get_resolution()

    def test_is_valid_cell(self):
        assert self.tcs.is_valid_cell() == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_cell_area(self):
        assert isinstance(self.tcs.cell_area(), TFloat)

    def test_cell_to_parent(self):
        resolution = S2Cell("47c3c3").get_resolution()
        parent = S2Cell("47c3c3").cell_to_parent(0 if resolution == 0 else resolution - 1)
        assert self.tcs.cell_to_parent(0 if resolution == 0 else resolution - 1).start_value() == parent

    def test_cell_to_point(self):
        assert isinstance(self.tcs.cell_to_point(), TGeogPoint)


class TestTS2CellValueFunctions(TestTS2Cell):
    value = S2Cell("47c3c3")
    other = S2Cell("54b5c9")
    ts = TS2CellSeq(TS)
    tss = TS2CellSeqSet(TSS)

    @pytest.mark.parametrize(
        "base, expected",
        [
            (datetime(2001, 1, 1, tzinfo=timezone.utc), TS2CellInst("47c3c3@2001-01-01")),
            (
                TsTzSet("{2001-01-01, 2001-01-02}"),
                TS2CellSeq("{47c3c3@2001-01-01, 47c3c3@2001-01-02}"),
            ),
            (
                TsTzSpan("[2001-01-01, 2001-01-02]"),
                TS2CellSeq("[47c3c3@2001-01-01, 47c3c3@2001-01-02]"),
            ),
            (
                TsTzSpanSet("{[2001-01-01, 2001-01-02], [2001-01-03, 2001-01-04]}"),
                TS2CellSeqSet("{[47c3c3@2001-01-01, 47c3c3@2001-01-02], [47c3c3@2001-01-03, 47c3c3@2001-01-04]}"),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, base, expected):
        assert TS2Cell.from_base_time(self.value, base) == expected

    def test_from_base_temporal_constructor(self):
        assert TS2Cell.from_base_temporal(self.value, self.ts) == TS2CellSeq("[47c3c3@2001-01-01, 47c3c3@2001-01-02]")

    def test_start_end_value(self):
        assert self.tss.start_value() == self.value
        assert self.tss.end_value() == S2Cell("47c3c3")

    def test_value_set(self):
        assert self.ts.value_set() == {self.value, self.other}

    def test_value_at_timestamp(self):
        assert self.ts.value_at_timestamp(datetime(2001, 1, 2, tzinfo=timezone.utc)) == self.other


class TestTS2CellGeneratedFamilies(TestTS2Cell):
    ts = TS2CellSeq(TS)
    value = S2Cell("47c3c3")

    def test_ever_always(self):
        assert self.ts.ever_equal(self.value) is True
        assert self.ts.always_equal(self.value) is False
        assert self.ts.ever_not_equal(self.value) is True
        assert self.ts.always_not_equal(self.value) is False
        assert self.ts.never_equal(self.value) is False
        assert self.ts.ever_equal(S2CellSet("{54b5c9}")) is True
        assert self.ts.ever_equal(self.ts) is True

    def test_temporal_comparison(self):
        assert self.ts.temporal_equal(self.value) == TBoolSeq("[t@2001-01-01, f@2001-01-02]")
        assert self.ts.temporal_not_equal(self.value) == TBoolSeq("[f@2001-01-01, t@2001-01-02]")
        assert self.ts.temporal_equal(self.ts) == TBoolSeq("[t@2001-01-01, t@2001-01-02]")

    def test_restriction(self):
        assert self.ts.at(self.value) == TS2CellSeqSet("{[47c3c3@2001-01-01, 47c3c3@2001-01-02)}")
        assert self.ts.minus(self.value) == TS2CellSeqSet("{[54b5c9@2001-01-02]}")
        assert self.ts.at(TsTzSpan("[2001-01-02, 2001-01-03]")) == TS2CellSeq("[54b5c9@2001-01-02]")
