from copy import copy
from datetime import date, timedelta

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
        assert str(self.date_set) == '{2019-09-25, 2019-09-26, 2019-09-27}'

    def test_repr(self):
        assert (
            repr(self.date_set) == 'DateSet({2019-09-25, 2019-09-26, 2019-09-27})'
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
        assert self.date_set.start_element() == date(2019, 9, 25)

    def test_end_element(self):
        assert self.date_set.end_element() == date(2019, 9, 27)

    def test_element_n(self):
        assert self.date_set.element_n(1) == date(2019, 9, 26)

    def test_element_n_out_of_range(self):
        with pytest.raises(IndexError):
            self.date_set.element_n(3)

    def test_elements(self):
        assert self.date_set.elements() == [
            date(2019, 9, 25),
            date(2019, 9, 26),
            date(2019, 9, 27),
        ]


class TestDateSetPositionFunctions(TestDateSet):
    date_value = date(year=2020, month=1, day=25)
    other_date_set = DateSet("{2020-01-01, 2020-01-31}")

    @pytest.mark.parametrize(
        "other, expected",
        [(other_date_set, False)],
        ids=["dateset"],
    )
    def test_is_contained_in(self, other, expected):
        assert self.date_set.is_contained_in(other) == expected

    @pytest.mark.parametrize(
        "other, expected",
        [(date_value, True), (other_date_set, False)],
        ids=["date", "dateset"],
    )
    def test_contains(self, other, expected):
        assert self.date_set.contains(other) == expected
        assert other in self.date_set == expected

    @pytest.mark.parametrize(
        "other",
        [other_date_set],
        ids=["dateset"],
    )
    def test_overlaps(self, other):
        self.date_set.overlaps(other)

    @pytest.mark.parametrize(
        "other", [date_value, other_date_set], ids=["date", "dateset"]
    )
    def test_is_before(self, other):
        self.date_set.is_before(other)

    @pytest.mark.parametrize(
        "other", [date_value, other_date_set], ids=["date", "dateset"]
    )
    def test_is_over_or_before(self, other):
        self.date_set.is_over_or_before(other)

    @pytest.mark.parametrize(
        "other", [date_value, other_date_set], ids=["date", "dateset"]
    )
    def test_is_after(self, other):
        self.date_set.is_after(other)

    @pytest.mark.parametrize(
        "other", [date_value, other_date_set], ids=["date", "dateset"]
    )
    def test_is_over_or_after(self, other):
        self.date_set.is_over_or_after(other)

    @pytest.mark.parametrize(
        "other", [date_value, other_date_set], ids=["date", "dateset"]
    )
    def test_distance(self, other):
        self.date_set.distance(other)


class TestDateSetSetFunctions(TestDateSet):
    date_value = date(year=2020, month=1, day=1)
    dateset = DateSet("{2020-01-01, 2020-01-31}")
    datespan = DateSpan("(2020-01-01, 2020-01-31)")
    datespanset = DateSpanSet("{(2020-01-01, 2020-01-31), (2021-01-01, 2021-01-31)}")

    @pytest.mark.parametrize(
        "other",
        [datespan, datespanset, date_value, dateset],
        ids=["datespan", "datespanset", "date", "dateset"],
    )
    def test_intersection(self, other):
        self.dateset.intersection(other)
        self.dateset * other

    @pytest.mark.parametrize(
        "other",
        [datespan, datespanset, date_value, dateset],
        ids=["datespan", "datespanset", "date", "dateset"],
    )
    def test_union(self, other):
        self.dateset.union(other)
        self.dateset + other

    @pytest.mark.parametrize(
        "other",
        [datespan, datespanset, date_value, dateset],
        ids=["datespan", "datespanset", "date", "dateset"],
    )
    def test_minus(self, other):
        self.dateset.minus(other)
        self.dateset - other


class TestDateSetComparisons(TestDateSet):
    dateset = DateSet("{2020-01-01, 2020-01-31}")
    other = DateSet("{2020-01-02, 2020-03-31}")

    def test_eq(self):
        assert not self.dateset == self.other

    def test_ne(self):
        assert self.dateset != self.other

    def test_lt(self):
        assert self.dateset < self.other

    def test_le(self):
        assert self.dateset <= self.other

    def test_gt(self):
        assert not self.dateset > self.other

    def test_ge(self):
        assert not self.dateset >= self.other


class TestDateSetFunctionsFunctions(TestDateSet):
    dateset = DateSet("{2020-01-01, 2020-01-02, 2020-01-04}")

    @pytest.mark.parametrize(
        "delta,expected",
        [
            (
                timedelta(days=4),
                DateSet("{2020-1-5, 2020-1-6, 2020-1-8}"),
            ),
            (
                timedelta(days=-4),
                DateSet("{2019-12-28,2019-12-29, 2019-12-31}"),
            ),
            (
                4,
                DateSet("{2020-1-5, 2020-1-6, 2020-1-8}"),
            ),
            (
                -4,
                DateSet("{2019-12-28,2019-12-29, 2019-12-31}"),
            ),
        ],
        ids=[
            "positive timedelta",
            "negative timedelta",
            "positive int",
            "negative int",
        ],
    )
    def test_shift(self, delta, expected):
        shifted = self.dateset.shift(delta)
        assert shifted == expected

    @pytest.mark.parametrize(
        "delta",
        [timedelta(days=6), 6],
        ids=["timedelta", "int"],
    )
    def test_scale(self, delta):
        expected = DateSet("{2020-1-1, 2020-1-3, 2020-1-7}")

        scaled = self.dateset.scale(delta)

        assert scaled == expected

    @pytest.mark.parametrize(
        "shift, scale",
        [
            (timedelta(days=4), timedelta(days=4)),
            (timedelta(days=4), 4),
            (4, timedelta(days=4)),
            (4, 4),
        ],
        ids=[
            "timedelta timedelta",
            "timedelta int",
            "int timedelta",
            "int int",
        ],
    )
    def test_shift_scale(self, shift, scale):
        shifted_scaled = self.dateset.shift_scale(shift, scale)
        assert shifted_scaled == DateSet("{2020-01-05, 2020-01-06, 2020-01-10}")


class TestDateSetMiscFunctions(TestDateSet):
    dateset = DateSet("{2020-01-01, 2020-01-02, 2020-01-04}")

    def test_hash(self):
        assert hash(self.dateset)
