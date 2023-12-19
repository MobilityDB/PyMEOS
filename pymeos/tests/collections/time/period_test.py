from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import (
    TsTzSpan,
    TsTzSpanSet,
    TsTzSet,
    TBox,
    STBox,
    TFloatInst,
    TFloatSeq,
    TFloatSeqSet,
)

from tests.conftest import TestPyMEOS


class TestPeriod(TestPyMEOS):
    tstzspan = TsTzSpan("(2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0)")

    @staticmethod
    def assert_tstzspan_equality(
        tstzspan: TsTzSpan,
        lower: datetime = None,
        upper: datetime = None,
        lower_inc: bool = None,
        upper_inc: bool = None,
    ):
        if lower is not None:
            assert tstzspan.lower() == lower
        if upper is not None:
            assert tstzspan.upper() == upper
        if lower_inc is not None:
            assert tstzspan.lower_inc() == lower_inc
        if upper_inc is not None:
            assert tstzspan.upper_inc() == upper_inc


class TestPeriodConstructors(TestPeriod):
    @pytest.mark.parametrize(
        "source, params",
        [
            (
                "(2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0)",
                (
                    datetime(2019, 9, 8, tzinfo=timezone.utc),
                    datetime(2019, 9, 10, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
            (
                "[2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0]",
                (
                    datetime(2019, 9, 8, tzinfo=timezone.utc),
                    datetime(2019, 9, 10, tzinfo=timezone.utc),
                    True,
                    True,
                ),
            ),
        ],
    )
    def test_string_constructor(self, source, params):
        tstzspan = TsTzSpan(source)
        self.assert_tstzspan_equality(tstzspan, *params)

    @pytest.mark.parametrize(
        "input_lower,input_upper,lower,upper",
        [
            (
                "2019-09-08 00:00:00+0",
                "2019-09-10 00:00:00+0",
                datetime(2019, 9, 8, tzinfo=timezone.utc),
                datetime(2019, 9, 10, tzinfo=timezone.utc),
            ),
            (
                datetime(2019, 9, 8, tzinfo=timezone.utc),
                datetime(2019, 9, 10, tzinfo=timezone.utc),
                datetime(2019, 9, 8, tzinfo=timezone.utc),
                datetime(2019, 9, 10, tzinfo=timezone.utc),
            ),
            (
                datetime(2019, 9, 8, tzinfo=timezone.utc),
                "2019-09-10 00:00:00+0",
                datetime(2019, 9, 8, tzinfo=timezone.utc),
                datetime(2019, 9, 10, tzinfo=timezone.utc),
            ),
        ],
        ids=["string", "datetime", "mixed"],
    )
    def test_constructor_bounds(self, input_lower, input_upper, lower, upper):
        tstzspan = TsTzSpan(lower=lower, upper=upper)
        self.assert_tstzspan_equality(tstzspan, lower, upper)

    def test_constructor_bound_inclusivity_defaults(self):
        tstzspan = TsTzSpan(lower="2019-09-08 00:00:00+0", upper="2019-09-10 00:00:00+0")
        self.assert_tstzspan_equality(tstzspan, lower_inc=True, upper_inc=False)

    @pytest.mark.parametrize(
        "lower,upper",
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ],
    )
    def test_constructor_bound_inclusivity(self, lower, upper):
        tstzspan = TsTzSpan(
            lower="2019-09-08 00:00:00+0",
            upper="2019-09-10 00:00:00+0",
            lower_inc=lower,
            upper_inc=upper,
        )
        self.assert_tstzspan_equality(tstzspan, lower_inc=lower, upper_inc=upper)

    def test_hexwkb_constructor(self):
        assert self.tstzspan == TsTzSpan.from_hexwkb(self.tstzspan.as_hexwkb())

    def test_from_as_constructor(self):
        assert self.tstzspan == TsTzSpan(str(self.tstzspan))
        assert self.tstzspan == TsTzSpan.from_wkb(self.tstzspan.as_wkb())

    def test_copy_constructor(self):
        other = copy(self.tstzspan)
        assert self.tstzspan == other
        assert self.tstzspan is not other


class TestPeriodOutputs(TestPeriod):
    def test_str(self):
        assert str(self.tstzspan) == "(2019-09-08 00:00:00+00, 2019-09-10 00:00:00+00)"

    def test_repr(self):
        assert (
            repr(self.tstzspan)
            == "TsTzSpan((2019-09-08 00:00:00+00, 2019-09-10 00:00:00+00))"
        )

    def test_hexwkb(self):
        assert self.tstzspan == TsTzSpan.from_hexwkb(self.tstzspan.as_hexwkb())


class TestPeriodConversions(TestPeriod):
    def test_to_tstzspanset(self):
        tstzspanset = self.tstzspan.to_tstzspanset()
        assert isinstance(tstzspanset, TsTzSpanSet)
        assert tstzspanset.num_tstzspans() == 1
        assert tstzspanset.start_tstzspan() == self.tstzspan


class TestPeriodAccessors(TestPeriod):
    tstzspan2 = TsTzSpan("[2019-09-08 02:03:00+0, 2019-09-10 02:03:00+0]")

    def test_lower(self):
        assert self.tstzspan.lower() == datetime(2019, 9, 8, tzinfo=timezone.utc)
        assert self.tstzspan2.lower() == datetime(2019, 9, 8, 2, 3, tzinfo=timezone.utc)

    def test_upper(self):
        assert self.tstzspan.upper() == datetime(2019, 9, 10, tzinfo=timezone.utc)
        assert self.tstzspan2.upper() == datetime(2019, 9, 10, 2, 3, tzinfo=timezone.utc)

    def test_lower_inc(self):
        assert not self.tstzspan.lower_inc()
        assert self.tstzspan2.lower_inc()

    def test_upper_inc(self):
        assert not self.tstzspan.upper_inc()
        assert self.tstzspan2.upper_inc()

    def test_duration(self):
        assert self.tstzspan.duration() == timedelta(days=2)
        assert self.tstzspan2.duration() == timedelta(days=2)

    def test_duration_in_seconds(self):
        assert self.tstzspan.duration_in_seconds() == 172800
        assert self.tstzspan2.duration_in_seconds() == 172800

    def test_hash(self):
        assert hash(self.tstzspan)


class TestPeriodTransformations(TestPeriod):
    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=4),
                (
                    datetime(2019, 9, 12, tzinfo=timezone.utc),
                    datetime(2019, 9, 14, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
            (
                timedelta(days=-4),
                (
                    datetime(2019, 9, 4, tzinfo=timezone.utc),
                    datetime(2019, 9, 6, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
            (
                timedelta(hours=2),
                (
                    datetime(2019, 9, 8, 2, tzinfo=timezone.utc),
                    datetime(2019, 9, 10, 2, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
            (
                timedelta(hours=-2),
                (
                    datetime(2019, 9, 7, 22, tzinfo=timezone.utc),
                    datetime(2019, 9, 9, 22, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
        ],
        ids=["positive days", "negative days", "positive hours", "negative hours"],
    )
    def test_shift(self, delta, result):
        shifted = self.tstzspan.shift(delta)
        self.assert_tstzspan_equality(shifted, *result)

    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=4),
                (
                    datetime(2019, 9, 8, tzinfo=timezone.utc),
                    datetime(2019, 9, 12, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
            (
                timedelta(hours=2),
                (
                    datetime(2019, 9, 8, tzinfo=timezone.utc),
                    datetime(2019, 9, 8, 2, tzinfo=timezone.utc),
                    False,
                    False,
                ),
            ),
        ],
        ids=["days", "hours"],
    )
    def test_scale(self, delta, result):
        scaled = self.tstzspan.scale(delta)
        self.assert_tstzspan_equality(scaled, *result)

    def test_shift_scale(self):
        shifted_scaled = self.tstzspan.shift_scale(timedelta(days=4), timedelta(hours=4))
        self.assert_tstzspan_equality(
            shifted_scaled,
            datetime(2019, 9, 12, 0, tzinfo=timezone.utc),
            datetime(2019, 9, 12, 4, tzinfo=timezone.utc),
            False,
            False,
        )


class TestPeriodTopologicalPositionFunctions(TestPeriod):
    tstzspan = TsTzSpan("(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)")
    tstzspanset = TsTzSpanSet(
        "{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}"
    )
    timestamp = datetime(year=2020, month=1, day=1)
    instant = TFloatInst("1.0@2020-01-01")
    discrete_sequence = TFloatSeq(
        "{1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31}"
    )
    stepwise_sequence = TFloatSeq(
        "Interp=Step;(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]"
    )
    continuous_sequence = TFloatSeq(
        "(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]"
    )
    sequence_set = TFloatSeqSet(
        "{(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31], "
        "(1.0@2021-01-01, 3.0@2021-01-10, 10.0@2021-01-20, 0.0@2021-01-31]}"
    )
    tbox = TBox("TBox XT([0, 10),[2020-01-01, 2020-01-31])")
    stbox = STBox("STBOX ZT(((1.0,2.0,3.0),(4.0,5.0,6.0)),[2001-01-01, 2001-01-02])")

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_adjacent(self, other):
        self.tstzspan.is_adjacent(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            instant,
            discrete_sequence,
            stepwise_sequence,
            continuous_sequence,
            sequence_set,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_contained_in(self, other):
        self.tstzspan.is_contained_in(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_contains(self, other):
        self.tstzspan.contains(other)
        _ = other in self.tstzspan

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_overlaps(self, other):
        self.tstzspan.overlaps(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_same(self, other):
        self.tstzspan.is_same(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_before(self, other):
        self.tstzspan.is_before(other)
        self.tstzspan.is_left(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_over_or_before(self, other):
        self.tstzspan.is_over_or_before(other)
        self.tstzspan.is_over_or_left(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_after(self, other):
        self.tstzspan.is_after(other)
        self.tstzspan.is_right(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_is_over_or_after(self, other):
        self.tstzspan.is_over_or_after(other)
        self.tstzspan.is_over_or_right(other)

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
            timestamp,
            instant,
            discrete_sequence,
            stepwise_sequence,
            sequence_set,
            continuous_sequence,
            tbox,
            stbox,
        ],
        ids=[
            "tstzspan",
            "tstzspanset",
            "timestamp",
            "instant",
            "discrete_sequence",
            "stepwise_sequence",
            "continuous_sequence",
            "sequence_set",
            "tbox",
            "stbox",
        ],
    )
    def test_distance(self, other):
        self.tstzspan.distance(other)


class TestPeriodSetFunctions(TestPeriod):
    tstzspan = TsTzSpan("(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)")
    tstzspanset = TsTzSpanSet(
        "{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}"
    )
    timestamp = datetime(year=2020, month=1, day=1)

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp],
        ids=["tstzspan", "tstzspanset", "timestamp"],
    )
    def test_intersection(self, other):
        self.tstzspan.intersection(other)
        self.tstzspan * other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp],
        ids=["tstzspan", "tstzspanset", "timestamp"],
    )
    def test_union(self, other):
        self.tstzspan.union(other)
        self.tstzspan + other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp],
        ids=["tstzspan", "tstzspanset", "timestamp"],
    )
    def test_minus(self, other):
        self.tstzspan.minus(other)
        self.tstzspan - other


class TestPeriodComparisons(TestPeriod):
    tstzspan = TsTzSpan("(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)")
    other = TsTzSpan("(2020-01-02 00:00:00+0, 2020-03-31 00:00:00+0)")

    def test_eq(self):
        _ = self.tstzspan == self.other

    def test_ne(self):
        _ = self.tstzspan != self.other

    def test_lt(self):
        _ = self.tstzspan < self.other

    def test_le(self):
        _ = self.tstzspan <= self.other

    def test_gt(self):
        _ = self.tstzspan > self.other

    def test_ge(self):
        _ = self.tstzspan >= self.other
