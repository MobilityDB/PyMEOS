from copy import copy
from datetime import datetime, timezone

import pytest
from shapely import Point, Polygon

from pymeos import (
    Pose,
    TInterpolation,
    TPoseInst,
    TPoseSeq,
    TRgeometry,
    TRgeometryInst,
    TRgeometrySeq,
    TRgeometrySeqSet,
)
from tests.conftest import TestPyMEOS


class TestTRgeometry(TestPyMEOS):
    pass


class TestTRgeometryConstructors(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tpi = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    tri = TRgeometry.from_geometry_tpose(geometry, tpi)
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    @pytest.mark.parametrize(
        "temporal, expected_type",
        [
            (tri, TRgeometryInst),
            (trs, TRgeometrySeq),
        ],
        ids=["Instant", "Sequence"],
    )
    def test_from_geometry_tpose_constructor(self, temporal, expected_type):
        assert isinstance(temporal, expected_type)

    @pytest.mark.parametrize(
        "source, expected_type",
        [
            ("Polygon((0 0,1 0,1 1,0 1,0 0));Pose(Point(1 1), 0.5)@2019-09-01", TRgeometryInst),
            (
                "Polygon((0 0,1 0,1 1,0 1,0 0));[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]",
                TRgeometrySeq,
            ),
            (
                "Polygon((0 0,1 0,1 1,0 1,0 0));{[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]}",
                TRgeometrySeqSet,
            ),
        ],
        ids=["Instant", "Sequence", "SequenceSet"],
    )
    def test_string_constructor(self, source, expected_type):
        temporal = expected_type(source)
        assert isinstance(temporal, expected_type)
        assert temporal == expected_type(str(temporal))

    def test_instant_constructor(self):
        inst = TRgeometryInst(
            geometry=self.geometry,
            pose=Pose("Pose(Point(1 1), 0.5)"),
            timestamp="2019-09-01",
        )
        assert isinstance(inst, TRgeometryInst)

    @pytest.mark.parametrize(
        "temporal",
        [tri, trs],
        ids=["Instant", "Sequence"],
    )
    def test_from_as_hexwkb_constructor(self, temporal):
        assert temporal == temporal.__class__.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        "temporal",
        [tri, trs],
        ids=["Instant", "Sequence"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTRgeometryOutputs(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tpi = TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    tri = TRgeometry.from_geometry_tpose(geometry, tpi)
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_str(self):
        assert str(self.tri) == "POLYGON((0 0,1 0,1 1,0 1,0 0));Pose(POINT(1 1),0.5)@2019-09-01 00:00:00+00"

    def test_repr(self):
        assert isinstance(repr(self.tri), str)

    def test_as_wkt(self):
        assert self.trs.as_wkt() == (
            "POLYGON((0 0,1 0,1 1,0 1,0 0));[Pose(POINT(1 1),0.5)@2019-09-01 00:00:00+00, "
            "Pose(POINT(2 2),0.3)@2019-09-02 00:00:00+00]"
        )

    def test_as_ewkt(self):
        assert self.trs.as_ewkt() == self.trs.as_wkt()


class TestTRgeometryAccessors(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_interpolation(self):
        assert self.trs.interpolation() == TInterpolation.LINEAR

    def test_start_value(self):
        assert self.trs.start_value() is not None

    def test_end_value(self):
        assert self.trs.end_value() is not None

    def test_values(self):
        assert self.trs.values() is not None

    def test_geometry(self):
        assert self.trs.geometry() is not None

    def test_value_at_timestamp(self):
        value = self.trs.value_at_timestamp(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert value is not None

    def test_srid(self):
        assert isinstance(self.trs.srid(), int)

    def test_to_tpose(self):
        assert self.trs.to_tpose() is not None

    def test_to_tpoint(self):
        assert self.trs.to_tpoint() is not None

    def test_yaw(self):
        assert self.trs.yaw() is not None


class TestTRgeometryEverAlways(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_never_not_equal(self):
        assert isinstance(self.trs.never_not_equal(self.geometry), bool)


# As #TestTCbufferSpatialRelationships, with values decided by a polygon around
# the whole motion and a point far from it.
class TestTRgeometrySpatialRelationships(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)
    around = Polygon([(-10, -10), (10, -10), (10, 10), (-10, 10)])
    far = Point(100, 100)
    far_trs = TRgeometry.from_geometry_tpose(
        geometry, TPoseSeq("[Pose(Point(100 100), 0)@2019-09-01, Pose(Point(101 101), 0)@2019-09-02]")
    )

    def test_ever_relationships(self):
        assert self.trs.is_ever_contained_in(self.around) is True
        assert self.trs.is_ever_coveredby(self.around) is True
        assert self.trs.is_ever_coveredby(self.far) is False
        assert self.trs.is_ever_covers(self.far) is False
        assert self.trs.is_ever_disjoint(self.far) is True
        assert self.trs.is_ever_disjoint(self.far_trs) is True
        assert self.trs.is_ever_within_distance(self.far, 1.0) is False
        assert self.trs.is_ever_within_distance(self.far_trs, 1000.0) is True
        assert self.trs.ever_intersects(self.around) is True
        assert self.trs.ever_intersects(self.far_trs) is False
        assert self.trs.ever_touches(self.far) is False

    def test_always_relationships(self):
        assert self.trs.is_always_contained_in(self.around) is True
        assert self.trs.is_always_coveredby(self.around) is True
        assert self.trs.is_always_coveredby(self.far) is False
        assert self.trs.is_always_covers(self.far) is False
        assert self.trs.is_always_disjoint(self.far) is True
        assert self.trs.is_always_disjoint(self.far_trs) is True
        assert self.trs.is_always_within_distance(self.far, 1.0) is False
        assert self.trs.is_always_within_distance(self.far_trs, 1000.0) is True
        assert self.trs.always_intersects(self.around) is True
        assert self.trs.always_intersects(self.far_trs) is False
        assert self.trs.always_touches(self.far) is False


class TestTRgeometryRestrictions(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_at_timestamp(self):
        result = self.trs.at(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert result is None or isinstance(result, TRgeometry)

    def test_minus_timestamp(self):
        result = self.trs.minus(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert result is None or isinstance(result, TRgeometry)


class TestTRgeometryDistance(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_nearest_approach_distance(self):
        assert isinstance(
            self.trs.nearest_approach_distance(Polygon([(5, 5), (6, 5), (6, 6), (5, 6)])),
            float,
        )


class TestTRgeometryGapMethods(TestTRgeometry):
    geometry = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    tps = TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01, Pose(Point(2 2), 0.3)@2019-09-02]")
    trs = TRgeometry.from_geometry_tpose(geometry, tps)

    def test_segments(self):
        assert isinstance(self.trs.segments(), list)

    # As #TestTGeomPointTransformations.test_to_instant, over values of one instant.
    @pytest.mark.parametrize(
        "temporal",
        [
            TRgeometry.from_geometry_tpose(geometry, TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01")),
            TRgeometry.from_geometry_tpose(geometry, TPoseSeq("[Pose(Point(1 1), 0.5)@2019-09-01]")),
        ],
        ids=["Instant", "Sequence"],
    )
    def test_to_instant(self, temporal):
        expected = TRgeometry.from_geometry_tpose(self.geometry, TPoseInst("Pose(Point(1 1), 0.5)@2019-09-01"))
        temp = temporal.to_instant()
        assert isinstance(temp, TRgeometryInst)
        assert temp == expected

    def test_delete(self):
        r = self.trs.delete(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert r is None or isinstance(r, TRgeometry)

    def test_before_after(self):
        b = self.trs.before(datetime(2019, 9, 2, tzinfo=timezone.utc))
        a = self.trs.after(datetime(2019, 9, 1, tzinfo=timezone.utc))
        assert b is None or isinstance(b, TRgeometry)
        assert a is None or isinstance(a, TRgeometry)
