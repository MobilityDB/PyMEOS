from copy import copy
from datetime import date, timezone, timedelta
from typing import List

import pytest

from pymeos import (
    DateSpan,
    DateSpanSet,
    DateSet,
)
from tests.conftest import TestPyMEOS


class TestDateSet(TestPyMEOS):
    date_set = DateSet("{2019-09-25, 2019-09-26, 2019-09-27}")


class TestDateSetConstructors(TestDateSet):
    def test_string_constructor(self):
        assert isinstance(self.date_set, DateSet)
        assert self.date_set.elements() == [
            date(2019, 9, 25),
            date(2019, 9, 26),
            date(2019, 9, 27),
        ]

    def test_list_constructor(self):
        d_set = DateSet(
            elements=[
                date(2019, 9, 25),
                date(2019, 9, 26),
                date(2019, 9, 27),
            ]
        )
        assert self.date_set == d_set

    def test_from_as_constructor(self):
        assert self.date_set == DateSet(str(self.date_set))
        assert self.date_set == DateSet.from_wkb(self.date_set.as_wkb())
        assert self.date_set == DateSet.from_hexwkb(self.date_set.as_hexwkb())

    def test_copy_constructor(self):
        date_set_copy = copy(self.date_set)
        assert self.date_set == date_set_copy
        assert self.date_set is not date_set_copy


class TestDateSetOutputs(TestDateSet):
    def test_str(self):
        assert str(self.date_set) == '{"2019-09-25", "2019-09-26", "2019-09-27"}'

    def test_repr(self):
        assert (
            repr(self.date_set) == 'TsTzSet({"2019-09-25", "2019-09-26", "2019-09-27"})'
        )

    def test_as_hexwkb(self):
        assert self.date_set == DateSet.from_hexwkb(self.date_set.as_hexwkb())


class TestCollectionConversions(TestDateSet):
    def test_to_span(self):
        assert self.date_set.to_span() == DateSpan("[2019-09-01, 2019-09-03]")

    def test_to_spanset(self):
        assert self.date_set.to_spanset() == DateSpanSet(
            "{[2019-09-01, 2019-09-01], "
            "[2019-09-02, 2019-09-02], "
            "[2019-09-03, 2019-09-03]}"
        )


class TestDateSetAccessors(TestDateSet):
    def test_duration(self):
        assert self.date_set.duration() == timedelta(days=2)

    def test_num_elements(self):
        assert self.date_set.num_elements() == 3
        assert len(self.date_set) == 3

    def test_start_element(self):
        assert self.date_set.start_element() == date(2019, 9, 1)

    def test_end_element(self):
        assert self.date_set.end_element() == date(2019, 9, 3)

    def test_element_n(self):
        assert self.date_set.element_n(1) == date(2019, 9, 2)

    def test_element_n_out_of_range(self):
        with pytest.raises(IndexError):
            self.date_set.element_n(3)

    def test_elements(self):
        assert self.date_set.elements() == [
            date(2019, 9, 1),
            date(2019, 9, 2),
            date(2019, 9, 3),
        ]


class TestDateSetPositionFunctions(TestDateSet):
    date_value = date(year=2020, month=1, day=1)
    other_date_set = DateSet("{2020-01-01, 2020-01-31}")

    @pytest.mark.parametrize("other, expected", [(other_date_set, False)], ids=["tstzset"])
    def test_is_contained_in(self, other, expected):
        assert self.date_set.is_contained_in(other) == expected

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_contains(self, other):
        self.date_set.contains(other)
        _ = other in self.tstzset

    @pytest.mark.parametrize("other", [tstzset], ids=["tstzset"])
    def test_overlaps(self, other):
        self.date_set.overlaps(other)

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_is_before(self, other):
        self.date_set.is_before(other)

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_is_over_or_before(self, other):
        self.date_set.is_over_or_before(other)

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_is_after(self, other):
        self.date_set.is_after(other)

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_is_over_or_after(self, other):
        self.date_set.is_over_or_after(other)

    @pytest.mark.parametrize(
        "other", [timestamp, tstzset], ids=["timestamp", "tstzset"]
    )
    def test_distance(self, other):
        self.date_set.distance(other)


class TestDateSetSetFunctions(TestDateSet):
    timestamp = datetime(year=2020, month=1, day=1)
    tstzset = TsTzSet("{2020-01-01, 2020-01-31}")
    tstzspan = TsTzSpan("(2020-01-01, 2020-01-31)")
    tstzspanset = TsTzSpanSet("{(2020-01-01, 2020-01-31), (2021-01-01, 2021-01-31)}")

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp, tstzset],
        ids=["tstzspan", "tstzspanset", "timestamp", "tstzset"],
    )
    def test_intersection(self, other):
        self.tstzset.intersection(other)
        self.tstzset * other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp, tstzset],
        ids=["tstzspan", "tstzspanset", "timestamp", "tstzset"],
    )
    def test_union(self, other):
        self.tstzset.union(other)
        self.tstzset + other

    @pytest.mark.parametrize(
        "other",
        [tstzspan, tstzspanset, timestamp, tstzset],
        ids=["tstzspan", "tstzspanset", "timestamp", "tstzset"],
    )
    def test_minus(self, other):
        self.tstzset.minus(other)
        self.tstzset - other


class TestDateSetComparisons(TestDateSet):
    tstzset = TsTzSet("{2020-01-01, 2020-01-31}")
    other = TsTzSet("{2020-01-02, 2020-03-31}")

    def test_eq(self):
        _ = self.tstzset == self.other

    def test_ne(self):
        _ = self.tstzset != self.other

    def test_lt(self):
        _ = self.tstzset < self.other

    def test_le(self):
        _ = self.tstzset <= self.other

    def test_gt(self):
        _ = self.tstzset > self.other

    def test_ge(self):
        _ = self.tstzset >= self.other


class TestDateSetFunctionsFunctions(TestDateSet):
    tstzset = TsTzSet("{2020-01-01, 2020-01-02, 2020-01-04}")

    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=4),
                [
                    datetime(2020, 1, 5, tzinfo=timezone.utc),
                    datetime(2020, 1, 6, tzinfo=timezone.utc),
                    datetime(2020, 1, 8, tzinfo=timezone.utc),
                ],
            ),
            (
                timedelta(days=-4),
                [
                    datetime(2019, 12, 28, tzinfo=timezone.utc),
                    datetime(2019, 12, 29, tzinfo=timezone.utc),
                    datetime(2019, 12, 31, tzinfo=timezone.utc),
                ],
            ),
            (
                timedelta(hours=2),
                [
                    datetime(2020, 1, 1, 2, tzinfo=timezone.utc),
                    datetime(2020, 1, 2, 2, tzinfo=timezone.utc),
                    datetime(2020, 1, 4, 2, tzinfo=timezone.utc),
                ],
            ),
            (
                timedelta(hours=-2),
                [
                    datetime(2019, 12, 31, 22, tzinfo=timezone.utc),
                    datetime(2020, 1, 1, 22, tzinfo=timezone.utc),
                    datetime(2020, 1, 3, 22, tzinfo=timezone.utc),
                ],
            ),
        ],
        ids=["positive days", "negative days", "positive hours", "negative hours"],
    )
    def test_shift(self, delta, result):
        shifted = self.tstzset.shift(delta)
        self.assert_tstzset_equality(shifted, result)

    @pytest.mark.parametrize(
        "delta,result",
        [
            (
                timedelta(days=6),
                [
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                    datetime(2020, 1, 3, tzinfo=timezone.utc),
                    datetime(2020, 1, 7, tzinfo=timezone.utc),
                ],
            ),
            (
                timedelta(hours=3),
                [
                    datetime(2020, 1, 1, tzinfo=timezone.utc),
                    datetime(2020, 1, 1, 1, tzinfo=timezone.utc),
                    datetime(2020, 1, 1, 3, tzinfo=timezone.utc),
                ],
            ),
        ],
        ids=["days", "hours"],
    )
    def test_scale(self, delta, result):
        scaled = self.tstzset.scale(delta)
        self.assert_tstzset_equality(scaled, result)

    def test_shift_scale(self):
        shifted_scaled = self.tstzset.shift_scale(timedelta(days=4), timedelta(hours=3))
        self.assert_tstzset_equality(
            shifted_scaled,
            [
                datetime(2020, 1, 5, tzinfo=timezone.utc),
                datetime(2020, 1, 5, 1, tzinfo=timezone.utc),
                datetime(2020, 1, 5, 3, tzinfo=timezone.utc),
            ],
        )


class TestDateSetMiscFunctions(TestDateSet):
    dateset = DateSet("{2020-01-01, 2020-01-02, 2020-01-04}")

    def test_hash(self):
        assert hash(self.dateset)
