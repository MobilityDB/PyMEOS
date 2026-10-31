from copy import copy
from datetime import datetime, timezone

import pytest

from pymeos import (
    Pose,
    PoseSet,
    TInterpolation,
    TPose,
    TPoseInst,
    TPoseSeq,
    TPoseSeqSet,
    TsTzSet,
    TsTzSpan,
    TsTzSpanSet,
)
from tests.conftest import TestPyMEOS


class TestTPose(TestPyMEOS):
    pass


class TestTPoseConstructors(TestTPose):
    tpi = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    tpds = TPoseSeq("{Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02}")
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    tpss = TPoseSeqSet(
        "{[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02],"
        "[Pose(Point(1 1), 0.5)@2019-09-03, Pose(Point(1 1), 0.5)@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tpi, TPoseInst),
            (tpds, TPoseSeq),
            (tps, TPoseSeq),
            (tpss, TPoseSeqSet),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_string_constructor(self, temporal, expected_type):
        assert isinstance(temporal, expected_type)

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tpds, tps, tpss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_hexwkb_constructor(self, temporal):
        assert temporal == temporal.__class__.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tpds, tps, tpss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTPoseOutputs(TestTPose):
    tpi = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")

    def test_str(self):
        assert str(self.tpi) == "Pose(POINT(1 1),0.5)@2019-09-01 00:00:00+00"

    def test_repr(self):
        assert isinstance(repr(self.tpi), str)

    def test_as_wkt(self):
        assert isinstance(self.tps.as_wkt(), str)


class TestTPoseAccessors(TestTPose):
    tpi = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")

    def test_interpolation(self):
        assert self.tps.interpolation() == TInterpolation.LINEAR

    def test_start_value(self):
        assert isinstance(self.tps.start_value(), Pose)

    def test_end_value(self):
        assert isinstance(self.tps.end_value(), Pose)

    def test_values(self):
        values = self.tps.values()
        assert all(isinstance(v, Pose) for v in values)

    def test_value_at_timestamp(self):
        value = self.tps.value_at_timestamp(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert isinstance(value, Pose)

    def test_srid(self):
        assert isinstance(self.tpi.srid(), int)

    def test_to_tpoint(self):
        assert self.tps.to_tpoint() is not None


class TestTPoseEverAlways(TestTPose):
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")

    def test_ever_equal(self):
        assert self.tps.ever_equal(Pose("Pose(Point(1 1), 0.5)"))

    def test_never_not_equal(self):
        assert isinstance(self.tps.never_not_equal(Pose("Pose(Point(1 1), 0.5)")), bool)


class TestTPoseRestrictions(TestTPose):
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")

    def test_at_pose(self):
        result = self.tps.at(Pose("Pose(Point(1 1), 0.5)"))
        assert result is None or isinstance(result, TPose)

    def test_minus_pose(self):
        result = self.tps.minus(Pose("Pose(Point(1 1), 0.5)"))
        assert result is None or isinstance(result, TPose)


class TestTPoseDistance(TestTPose):
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")

    def test_nearest_approach_distance(self):
        assert isinstance(
            self.tps.nearest_approach_distance(Pose("Pose(Point(0 0), 0.0)")),
            float,
        )


class TestPose(TestPyMEOS):
    p = Pose("Pose(Point(1 1), 0.5)")

    def test_string_constructor(self):
        assert isinstance(self.p, Pose)

    def test_str(self):
        assert str(self.p) == "Pose(POINT(1 1),0.5)"

    def test_from_as_hexwkb(self):
        assert self.p == Pose.from_hexwkb(self.p.as_hexwkb())

    def test_copy(self):
        other = copy(self.p)
        assert self.p == other
        assert self.p is not other

    def test_yaw(self):
        assert isinstance(self.p.yaw(), float)

    def test_srid(self):
        assert isinstance(self.p.srid(), int)

    def test_round(self):
        assert isinstance(self.p.round(2), Pose)

    def test_comparisons(self):
        other = Pose("Pose(Point(2 2), 0.3)")
        assert self.p != other
        assert self.p == copy(self.p)
        assert isinstance(self.p.cmp(other), int)


class TestTPoseValueFunctions(TestTPose):
    value = Pose("Pose(Point(1 1), 0.5)")
    other = Pose("Pose(Point(2 2), 0.3)")
    ti = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    ts = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    tss = TPoseSeqSet(
        "{[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02], [Pose(Point(1 1), 0.5)@2019-09-03, Pose(Point(1 1), 0.5)@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "base, expected",
        [
            (datetime(2019, 9, 1, tzinfo=timezone.utc), TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")),
            (
                TsTzSet("{2019-09-01, 2019-09-02}"),
                TPoseSeq("{Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(1 1), 0.5)@2019-09-02}"),
            ),
            (
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(1 1), 0.5)@2019-09-02]"),
            ),
            (
                TsTzSpanSet("{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}"),
                TPoseSeqSet(
                    "{[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(1 1), 0.5)@2019-09-02], [Pose(Point(1 1), 0.5)@2019-09-03, Pose(Point(1 1), 0.5)@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, base, expected):
        assert TPose.from_base_time(self.value, base, TInterpolation.LINEAR) == expected

    def test_from_base_temporal_constructor(self):
        assert TPose.from_base_temporal(self.value, self.tss) == TPoseSeqSet(
            "{[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(1 1), 0.5)@2019-09-02], [Pose(Point(1 1), 0.5)@2019-09-03, Pose(Point(1 1), 0.5)@2019-09-05]}"
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


class TestPoseSet(TestPyMEOS):
    ps = PoseSet('{"Pose(Point(1 1),0.5)", "Pose(Point(2 2),0.3)"}')
    ps_srid = PoseSet('SRID=3812;{"Pose(Point(1 1),0.5)"}')

    def test_str(self):
        assert str(self.ps) == '{"Pose(POINT(1 1),0.5)", "Pose(POINT(2 2),0.3)"}'

    def test_as_text(self):
        assert self.ps.as_text() == '{"Pose(POINT(1 1),0.5)", "Pose(POINT(2 2),0.3)"}'
        assert self.ps.as_wkt() == self.ps.as_text()

    def test_as_ewkt(self):
        assert self.ps_srid.as_ewkt() == 'SRID=3812;{"Pose(POINT(1 1),0.5)"}'
        assert self.ps_srid.as_text() == '{"Pose(POINT(1 1),0.5)"}'
