from copy import copy
from datetime import datetime, timezone

import pytest

from pymeos import (
    TFloat,
    TNpoint,
    TNpointInst,
    TNpointSeq,
    TNpointSeqSet,
    TInterpolation,
    Npoint,
    NpointSet,
    Nsegment,
)
from tests.conftest import TestPyMEOS


class TestTNpoint(TestPyMEOS):
    pass


class TestTNpointConstructors(TestTNpoint):
    tpi = TNpointInst("NPoint(1, 0.5)@2019-09-01")
    tpds = TNpointSeq("{NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02}")
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")
    tpss = TNpointSeqSet(
        "{[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02],"
        "[NPoint(1, 0.5)@2019-09-03, NPoint(1, 0.5)@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "source, type, interpolation",
        [
            (tpi, TNpointInst, TInterpolation.NONE),
            (tpds, TNpointSeq, TInterpolation.DISCRETE),
            (tps, TNpointSeq, TInterpolation.LINEAR),
            (tpss, TNpointSeqSet, TInterpolation.LINEAR),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_string_constructor(self, source, type, interpolation):
        assert isinstance(source, type)
        assert source.interpolation() == interpolation

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tpds, tps, tpss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_constructor(self, temporal):
        assert temporal == temporal.from_wkb(temporal.as_wkb())
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tpds, tps, tpss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other

    def test_instant_value_timestamp_constructor(self):
        tpi = TNpointInst(value=Npoint(1, 0.5), timestamp="2019-09-01")
        assert isinstance(tpi, TNpointInst)
        assert tpi.route() == 1


class TestTNpointOutputs(TestTNpoint):
    tpi = TNpointInst("NPoint(1, 0.5)@2019-09-01")
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tps],
        ids=["Instant", "Sequence"],
    )
    def test_str_round_trip(self, temporal):
        assert isinstance(str(temporal), str)
        assert temporal == temporal.__class__(str(temporal))

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tps],
        ids=["Instant", "Sequence"],
    )
    def test_as_wkt(self, temporal):
        assert isinstance(temporal.as_wkt(), str)

    @pytest.mark.parametrize(
        "temporal",
        [tpi, tps],
        ids=["Instant", "Sequence"],
    )
    def test_repr_round_trip(self, temporal):
        assert temporal == temporal.__class__(repr(temporal))


class TestTNpointAccessors(TestTNpoint):
    tpi = TNpointInst("NPoint(1, 0.5)@2019-09-01")
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")

    def test_route(self):
        assert self.tpi.route() == 1
        assert self.tps.route() == 1

    def test_srid(self):
        assert isinstance(self.tps.srid(), int)

    def test_length(self):
        assert isinstance(self.tps.length(), float)

    def test_cumulative_length(self):
        assert isinstance(self.tps.cumulative_length(), TFloat)

    def test_speed(self):
        assert isinstance(self.tps.speed(), TFloat)

    def test_bounding_box(self):
        from pymeos import STBox

        assert isinstance(self.tps.bounding_box(), STBox)

    def test_to_tgeompoint(self):
        from pymeos import TGeomPoint

        assert isinstance(self.tps.to_tgeompoint(), TGeomPoint)


class TestTNpointComparisons(TestTNpoint):
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")
    other = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")

    def test_eq(self):
        assert self.tps == self.other

    def test_ever_equal(self):
        assert self.tps.ever_equal(Npoint(1, 0.5))

    def test_never_not_equal(self):
        assert isinstance(self.tps.never_not_equal(Npoint(1, 0.5)), bool)

    def test_temporal_equal(self):
        from pymeos import TBool

        assert isinstance(self.tps.temporal_equal(Npoint(1, 0.5)), TBool)

    def test_distance(self):
        assert isinstance(self.tps.distance(self.other), TFloat)

    def test_nearest_approach_distance(self):
        assert isinstance(
            self.tps.nearest_approach_distance(self.other), float
        )

    def test_nearest_approach_instant(self):
        assert isinstance(
            self.tps.nearest_approach_instant(self.other), TNpointInst
        )


class TestTNpointRestrictions(TestTNpoint):
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")

    def test_at_timestamp(self):
        result = self.tps.at(
            datetime(2019, 9, 1, tzinfo=timezone.utc)
        )
        assert isinstance(result, TNpoint)

    def test_minus_timestamp(self):
        result = self.tps.minus(
            datetime(2019, 9, 1, tzinfo=timezone.utc)
        )
        assert isinstance(result, TNpoint)


class TestNpoint(TestTNpoint):
    np = Npoint("NPoint(1, 0.5)")

    def test_string_constructor(self):
        assert isinstance(self.np, Npoint)

    def test_route_position(self):
        assert self.np.route() == 1
        assert self.np.position() == 0.5

    def test_make_constructor(self):
        assert Npoint(route=1, position=0.5) == self.np

    def test_from_as_wkb(self):
        assert self.np == Npoint.from_wkb(self.np.as_wkb())
        assert self.np == Npoint.from_hexwkb(self.np.as_hexwkb())

    def test_str_round_trip(self):
        assert self.np == Npoint(str(self.np))

    def test_hash(self):
        assert isinstance(hash(self.np), int)

    def test_to_stbox(self):
        from pymeos import STBox

        assert isinstance(self.np.to_stbox(), STBox)


class TestNpointSet(TestTNpoint):
    nps = NpointSet("{NPoint(1, 0.5), NPoint(2, 0.3)}")

    def test_string_constructor(self):
        assert isinstance(self.nps, NpointSet)

    def test_elements_constructor(self):
        other = NpointSet(elements=[Npoint(1, 0.5), Npoint(2, 0.3)])
        assert other == self.nps

    def test_start_end_element(self):
        assert isinstance(self.nps.start_element(), Npoint)
        assert isinstance(self.nps.end_element(), Npoint)

    def test_element_n(self):
        assert isinstance(self.nps.element_n(0), Npoint)

    def test_elements(self):
        elems = self.nps.elements()
        assert all(isinstance(e, Npoint) for e in elems)

    def test_str_round_trip(self):
        assert self.nps == NpointSet(str(self.nps))


class TestTNpointPositions(TestTNpoint):
    tps = TNpointSeq("[NPoint(1, 0.5)@2019-09-01, NPoint(1, 0.7)@2019-09-02]")

    def test_positions(self):
        pos = self.tps.positions()
        assert all(isinstance(p, Nsegment) for p in pos)


class TestNsegment(TestPyMEOS):
    ns = Nsegment("NSegment(1, 0.2, 0.6)")

    def test_constructors(self):
        assert isinstance(self.ns, Nsegment)
        assert isinstance(Nsegment(rid=1, pos1=0.2, pos2=0.6), Nsegment)

    def test_accessors(self):
        assert isinstance(self.ns.route(), int)
        assert isinstance(self.ns.start_position(), float)
        assert isinstance(self.ns.end_position(), float)
        assert isinstance(self.ns.srid(), int)

    def test_copy_eq(self):
        other = copy(self.ns)
        assert self.ns == other

    def test_round(self):
        assert isinstance(self.ns.round(2), Nsegment)
