from copy import copy
from datetime import datetime, timezone, timedelta
from typing import List

import pytest

from pymeos import (
    TsTzSpan,
    TsTzSpanSet,
    TFloatInst,
    TFloatSeq,
    STBox,
    TFloatSeqSet,
    TBox,
)
from tests.conftest import TestPyMEOS


class TestPeriodSet(TestPyMEOS):
    tstzspanset = TsTzSpanSet("{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-04]}")

    @staticmethod
    def assert_tstzspanset_equality(
        tstzspanset: TsTzSpanSet, tstzspans: List[TsTzSpan]
    ):
        assert tstzspanset.num_tstzspans() == len(tstzspans)
        assert tstzspanset.tstzspans() == tstzspans


class TestPeriodSetConstructors(TestPeriodSet):
    def test_string_constructor(self):
        self.assert_tstzspanset_equality(
            self.tstzspanset,
            [
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                TsTzSpan("[2019-09-03, 2019-09-04]"),
            ],
        )

    def test_span_list_constructor(self):
        tstzspanset = TsTzSpanSet(
            span_list=[
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                TsTzSpan("[2019-09-03, 2019-09-04]"),
            ]
        )
        self.assert_tstzspanset_equality(
            tstzspanset,
            [
                TsTzSpan("[2019-09-01, 2019-09-02]"),
                TsTzSpan("[2019-09-03, 2019-09-04]"),
            ],
        )

    def test_from_as_constructor(self):
        assert self.tstzspanset == TsTzSpanSet(str(self.tstzspanset))
        assert self.tstzspanset == TsTzSpanSet.from_wkb(self.tstzspanset.as_wkb())
        assert self.tstzspanset == TsTzSpanSet.from_hexwkb(self.tstzspanset.as_hexwkb())

    def test_copy_constructor(self):
        copied = copy(self.tstzspanset)
        assert self.tstzspanset == copied
        assert self.tstzspanset is not copied


class TestPeriodSetOutputs(TestPeriodSet):
    def test_str(self):
        assert (
            str(self.tstzspanset)
            == "{[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00], "
            "[2019-09-03 00:00:00+00, 2019-09-04 00:00:00+00]}"
        )

    def test_repr(self):
        assert (
            repr(self.tstzspanset)
            == "TsTzSpanSet({[2019-09-01 00:00:00+00, 2019-09-02 00:00:00+00], "
            "[2019-09-03 00:00:00+00, 2019-09-04 00:00:00+00]})"
        )

    def test_hexwkb(self):
        assert self.tstzspanset == TsTzSpanSet.from_hexwkb(self.tstzspanset.as_hexwkb())


class TestPeriodSetConversions(TestPeriodSet):
    def test_to_tstzspan(self):
        assert self.tstzspanset.to_tstzspan() == TsTzSpan("[2019-09-01, 2019-09-04]")


class TestPeriodSetAccessors(TestPeriodSet):
    tstzspanset2 = TsTzSpanSet("{[2019-09-01, 2019-09-02), (2019-09-02, 2019-09-04]}")

    def test_duration(self):
        assert self.tstzspanset.duration() == timedelta(days=2)
        assert self.tstzspanset.duration(True) == timedelta(days=3)

    def test_num_timestamps(self):
        assert self.tstzspanset.num_timestamps() == 4
        assert self.tstzspanset2.num_timestamps() == 3

    def test_start_timestamp(self):
        assert self.tstzspanset.start_timestamp() == datetime(
            2019, 9, 1, tzinfo=timezone.utc
        )

    def test_end_timestamp(self):
        assert self.tstzspanset.end_timestamp() == datetime(
            2019, 9, 4, tzinfo=timezone.utc
        )

    def test_timestamp_n(self):
        assert self.tstzspanset.timestamp_n(0) == datetime(
            2019, 9, 1, tzinfo=timezone.utc
        )
        assert self.tstzspanset.timestamp_n(1) == datetime(
            2019, 9, 2, tzinfo=timezone.utc
        )
        assert self.tstzspanset.timestamp_n(2) == datetime(
            2019, 9, 3, tzinfo=timezone.utc
        )
        assert self.tstzspanset.timestamp_n(3) == datetime(
            2019, 9, 4, tzinfo=timezone.utc
        )

    def test_timestamps(self):
        assert self.tstzspanset.timestamps() == [
            datetime(2019, 9, 1, tzinfo=timezone.utc),
            datetime(2019, 9, 2, tzinfo=timezone.utc),
            datetime(2019, 9, 3, tzinfo=timezone.utc),
            datetime(2019, 9, 4, tzinfo=timezone.utc),
        ]

    def test_num_tstzspans(self):
        assert self.tstzspanset.num_tstzspans() == 2

    def test_start_tstzspan(self):
        assert self.tstzspanset.start_tstzspan() == TsTzSpan("[2019-09-01, 2019-09-02]")

    def test_end_tstzspan(self):
        assert self.tstzspanset.end_tstzspan() == TsTzSpan("[2019-09-03, 2019-09-04]")

    def test_tstzspan_n(self):
        assert self.tstzspanset.tstzspan_n(0) == TsTzSpan("[2019-09-01, 2019-09-02]")
        assert self.tstzspanset.tstzspan_n(1) == TsTzSpan("[2019-09-03, 2019-09-04]")

    def test_tstzspans(self):
        assert self.tstzspanset.tstzspans() == [
            TsTzSpan("[2019-09-01, 2019-09-02]"),
            TsTzSpan("[2019-09-03, 2019-09-04]"),
        ]

    def test_hash(self):
        assert hash(self.tstzspanset)


class TestPeriodSetTransformations(TestPeriodSet):
    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=4),
                [
                    TsTzSpan("[2019-09-05 00:00:00+0, 2019-09-06 00:00:00+0]"),
                    TsTzSpan("[2019-09-07 00:00:00+0, 2019-09-08 00:00:00+0]"),
                ],
            ),
            (
                timedelta(days=-4),
                [
                    TsTzSpan("[2019-08-28 00:00:00+0, 2019-08-29 00:00:00+0]"),
                    TsTzSpan("[2019-08-30 00:00:00+00, 2019-08-31 00:00:00+00]"),
                ],
            ),
            (
                timedelta(hours=2),
                [
                    TsTzSpan("[2019-09-01 02:00:00+0, 2019-09-02 02:00:00+0]"),
                    TsTzSpan("[2019-09-03 02:00:00+0, 2019-09-04 02:00:00+0]"),
                ],
            ),
            (
                timedelta(hours=-2),
                [
                    TsTzSpan("[2019-08-31 22:00:00+0, 2019-09-01 22:00:00+0]"),
                    TsTzSpan("[2019-09-02 22:00:00+0, 2019-09-03 22:00:00+0]"),
                ],
            ),
        ],
        ids=["positive days", "negative days", "positive hours", "negative hours"],
    )
    def test_shift(self, delta, result):
        shifted = self.tstzspanset.shift(delta)
        self.assert_tstzspanset_equality(shifted, result)

    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=3),
                [
                    TsTzSpan("[2019-09-01 00:00:00+0, 2019-09-02 00:00:00+0]"),
                    TsTzSpan("[2019-09-03 00:00:00+0, 2019-09-04 00:00:00+0]"),
                ],
            ),
            (
                timedelta(hours=6),
                [
                    TsTzSpan("[2019-09-01 00:00:00+0, 2019-09-01 02:00:00+0]"),
                    TsTzSpan("[2019-09-01 04:00:00+0, 2019-09-01 06:00:00+0]"),
                ],
            ),
        ],
        ids=["days", "hours"],
    )
    def test_scale(self, delta, result):
        scaled = self.tstzspanset.scale(delta)
        self.assert_tstzspanset_equality(scaled, result)

    def test_shift_scale(self):
        shifted_scaled = self.tstzspanset.shift_scale(
            timedelta(days=4), timedelta(hours=6)
        )
        self.assert_tstzspanset_equality(
            shifted_scaled,
            [
                TsTzSpan("[2019-09-05 00:00:00+0, 2019-09-05 02:00:00+0]"),
                TsTzSpan("[2019-09-05 04:00:00+0, 2019-09-05 06:00:00+0]"),
            ],
        )


class TestPeriodSetTopologicalPositionFunctions(TestPeriodSet):
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
        self.tstzspanset.is_adjacent(other)

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
        self.tstzspanset.is_contained_in(other)

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
        self.tstzspanset.contains(other)
        _ = other in self.tstzspanset

    @pytest.mark.parametrize(
        "other",
        [
            tstzspan,
            tstzspanset,
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
        self.tstzspanset.overlaps(other)

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
        self.tstzspanset.is_same(other)

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
        self.tstzspanset.is_before(other)

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
        self.tstzspanset.is_over_or_before(other)

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
        self.tstzspanset.is_after(other)

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
        self.tstzspanset.is_over_or_after(other)

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
        self.tstzspanset.distance(other)


class TestPeriodSetSetFunctions(TestPeriodSet):
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
        self.tstzspanset.intersection(other)
        self.tstzspanset * other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp],
        ids=["tstzspan", "tstzspanset", "timestamp"],
    )
    def test_union(self, other):
        self.tstzspanset.union(other)
        self.tstzspanset + other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp],
        ids=["tstzspan", "tstzspanset", "timestamp"],
    )
    def test_minus(self, other):
        self.tstzspanset.minus(other)
        self.tstzspanset - other


class TestPeriodSetComparisons(TestPeriodSet):
    tstzspanset = TsTzSpanSet(
        "{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}"
    )
    other = TsTzSpanSet(
        "{(2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0), (2022-01-01 00:00:00+0, 2022-01-31 00:00:00+0)}"
    )

    def test_eq(self):
        _ = self.tstzspanset == self.other

    def test_ne(self):
        _ = self.tstzspanset != self.other

    def test_lt(self):
        _ = self.tstzspanset < self.other

    def test_le(self):
        _ = self.tstzspanset <= self.other

    def test_gt(self):
        _ = self.tstzspanset > self.other

    def test_ge(self):
        _ = self.tstzspanset >= self.other
