from copy import copy
from typing import List

import pytest

from pymeos import IntSet, IntSpan, IntSpanSet
from tests.conftest import TestPyMEOS


class TestIntSet(TestPyMEOS):
    intset = IntSet("{1, 2, 3}")

    @staticmethod
    def assert_intset_equality(intset: IntSet, values: List[int]):
        assert intset.num_elements() == len(values)
        assert intset.elements() == values


class TestIntSetConstructors(TestIntSet):
    def test_string_constructor(self):
        self.assert_intset_equality(self.intset, [1, 2, 3])

    def test_list_constructor(self):
        intset = IntSet(elements=[1, 2, 3])
        self.assert_intset_equality(intset, [1, 2, 3])

    def test_hexwkb_constructor(self):
        intset = IntSet.from_hexwkb("010C000103000000010000000200000003000000")
        self.assert_intset_equality(intset, [1, 2, 3])

    def test_from_as_constructor(self):
        assert self.intset == IntSet(str(self.intset))
        assert self.intset == IntSet.from_wkb(self.intset.as_wkb())
        assert self.intset == IntSet.from_hexwkb(self.intset.as_hexwkb())

    def test_copy_constructor(self):
        intset_copy = copy(self.intset)
        assert self.intset == intset_copy
        assert self.intset is not intset_copy


class TestIntSetOutputs(TestIntSet):
    def test_str(self):
        assert str(self.intset) == "{1, 2, 3}"

    def test_repr(self):
        assert repr(self.intset) == "IntSet({1, 2, 3})"

    def test_as_hexwkb(self):
        assert self.intset.as_hexwkb() == "010C000103000000010000000200000003000000"


# class TestIntConversions(TestIntSet):

# def test_to_spanset(self):
# assert self.intset.to_spanset() == IntSpanSet(
# '{[1, 1], [2, 2], [3, 3]}')


class TestIntSetAccessors(TestIntSet):
    def test_to_span(self):
        assert self.intset.to_span() == IntSpan("[1, 3]")

    def test_num_elements(self):
        assert self.intset.num_elements() == 3

    def test_start_element(self):
        assert self.intset.start_element() == 1

    def test_end_element(self):
        assert self.intset.end_element() == 3

    def test_element_n(self):
        assert self.intset.element_n(1) == 2

    def test_element_n_out_of_range(self):
        with pytest.raises(IndexError):
            self.intset.element_n(3)

    def test_elements(self):
        assert self.intset.elements() == [1, 2, 3]

    def test_hash(self):
        assert hash(self.intset) == 3969573766


class TestIntSetTopologicalFunctions(TestIntSet):
    value = 5
    other = IntSet("{5, 10}")

    @pytest.mark.parametrize(
        "arg, result",
        [
            (other, False),
        ],
        ids=["other"],
    )
    def test_is_contained_in(self, arg, result):
        assert self.intset.is_contained_in(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_contains(self, arg, result):
        assert self.intset.contains(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (other, False),
        ],
        ids=["other"],
    )
    def test_overlaps(self, arg, result):
        assert self.intset.overlaps(arg) == result


class TestIntSetPositionFunctions(TestIntSet):
    value = 5
    other = IntSet("{5, 10}")

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, True),
            (other, True),
        ],
        ids=["value", "other"],
    )
    def test_is_left(self, arg, result):
        assert self.intset.is_left(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, True),
            (other, True),
        ],
        ids=["value", "other"],
    )
    def test_is_over_or_left(self, arg, result):
        assert self.intset.is_over_or_left(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_is_right(self, arg, result):
        assert self.intset.is_right(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_is_over_or_right(self, arg, result):
        assert self.intset.is_over_or_right(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, 2),
            (other, 2),
        ],
        ids=["value", "other"],
    )
    def test_distance(self, arg, result):
        assert self.intset.distance(arg) == result


class TestIntSetSetFunctions(TestIntSet):
    value = 1
    intset = IntSet("{1, 10}")

    @pytest.mark.parametrize("other", [value, intset], ids=["value", "intset"])
    def test_intersection(self, other):
        self.intset.intersection(other)
        self.intset * other

    @pytest.mark.parametrize("other", [value, intset], ids=["value", "intset"])
    def test_union(self, other):
        self.intset.union(other)
        self.intset + other

    @pytest.mark.parametrize("other", [value, intset], ids=["value", "intset"])
    def test_minus(self, other):
        self.intset.minus(other)
        self.intset - other


class TestIntSetComparisons(TestIntSet):
    intset = IntSet("{1, 10}")
    other = IntSet("{2, 10}")

    def test_eq(self):
        _ = self.intset == self.other

    def test_ne(self):
        _ = self.intset != self.other

    def test_lt(self):
        _ = self.intset < self.other

    def test_le(self):
        _ = self.intset <= self.other

    def test_gt(self):
        _ = self.intset > self.other

    def test_ge(self):
        _ = self.intset >= self.other


# class TestIntSetTransformationFunctions(TestIntSet):

# @pytest.mark.parametrize(
# 'delta,result',
# [(4, [5, 6, 8]),
# (-4, [-3, -1, 0]),
# ],
# ids=['positive delta', 'negative delta']
# )
# def test_shift(self, delta, result):
# shifted = self.intset.shift(delta)
# self.assert_intset_equality(shifted, result)

# @pytest.mark.parametrize(
# 'delta,result',
# [(6, [1, 4, 7])],
# ids=['positive']
# )
# def test_scale(self, delta, result):
# scaled = self.intset.scale(delta)
# self.assert_intset_equality(scaled, result)

# def test_shift_scale(self):
# shifted_scaled = self.intset.shift_scale(4, 4)
# self.assert_intset_equality(shifted_scaled, [5, 7, 9])
