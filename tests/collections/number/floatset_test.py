from copy import copy
from typing import List

import pytest

from pymeos import FloatSet, FloatSpan, FloatSpanSet
from tests.conftest import TestPyMEOS


class TestFloatSet(TestPyMEOS):
    floatset = FloatSet("{1, 2, 3}")

    @staticmethod
    def assert_intset_equality(floatset: FloatSet, values: List[int]):
        assert floatset.num_elements() == len(values)
        assert floatset.elements() == values


class TestFloatSetConstructors(TestFloatSet):
    def test_string_constructor(self):
        self.assert_intset_equality(self.floatset, [1, 2, 3])

    def test_list_constructor(self):
        floatset = FloatSet(elements=[1, 2, 3])
        self.assert_intset_equality(floatset, [1, 2, 3])

    def test_hexwkb_constructor(self):
        floatset = FloatSet.from_hexwkb(FloatSet(elements=[1, 2, 3]).as_hexwkb())
        self.assert_intset_equality(floatset, [1, 2, 3])

    def test_from_as_constructor(self):
        assert self.floatset == FloatSet(str(self.floatset))
        assert self.floatset == FloatSet.from_wkb(self.floatset.as_wkb())
        assert self.floatset == FloatSet.from_hexwkb(self.floatset.as_hexwkb())

    def test_copy_constructor(self):
        intset_copy = copy(self.floatset)
        assert self.floatset == intset_copy
        assert self.floatset is not intset_copy


class TestFloatSetOutputs(TestFloatSet):
    def test_str(self):
        assert str(self.floatset) == "{1, 2, 3}"

    def test_repr(self):
        assert repr(self.floatset) == "FloatSet({1, 2, 3})"

    def test_as_hexwkb(self):
        assert self.floatset == FloatSet.from_hexwkb(self.floatset.as_hexwkb())


# class TestIntConversions(TestFloatSet):

# def test_to_spanset(self):
# assert self.floatset.to_spanset() == FloatSpanSet(
# '{[1, 1], [2, 2], [3, 3]}')


class TestFloatSetAccessors(TestFloatSet):
    def test_to_span(self):
        assert self.floatset.to_span() == FloatSpan("[1, 3]")

    def test_num_elements(self):
        assert self.floatset.num_elements() == 3

    def test_start_element(self):
        assert self.floatset.start_element() == 1

    def test_end_element(self):
        assert self.floatset.end_element() == 3

    def test_element_n(self):
        assert self.floatset.element_n(1) == 2

    def test_element_n_out_of_range(self):
        with pytest.raises(IndexError):
            self.floatset.element_n(3)

    def test_elements(self):
        assert self.floatset.elements() == [1, 2, 3]

    def test_hash(self):
        assert hash(self.floatset) == 2419122126


class TestFloatSetTopologicalFunctions(TestFloatSet):
    value = 5.0
    other = FloatSet("{5, 10}")

    @pytest.mark.parametrize(
        "arg, result",
        [
            (other, False),
        ],
        ids=["other"],
    )
    def test_is_contained_in(self, arg, result):
        assert self.floatset.is_contained_in(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_contains(self, arg, result):
        assert self.floatset.contains(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (other, False),
        ],
        ids=["other"],
    )
    def test_overlaps(self, arg, result):
        assert self.floatset.overlaps(arg) == result


class TestFloatSetPositionFunctions(TestFloatSet):
    value = 5.0
    other = FloatSet("{5, 10}")

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, True),
            (other, True),
        ],
        ids=["value", "other"],
    )
    def test_is_left(self, arg, result):
        assert self.floatset.is_left(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, True),
            (other, True),
        ],
        ids=["value", "other"],
    )
    def test_is_over_or_left(self, arg, result):
        assert self.floatset.is_over_or_left(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_is_right(self, arg, result):
        assert self.floatset.is_right(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, False),
            (other, False),
        ],
        ids=["value", "other"],
    )
    def test_is_over_or_right(self, arg, result):
        assert self.floatset.is_over_or_right(arg) == result

    @pytest.mark.parametrize(
        "arg, result",
        [
            (value, 2.0),
            (other, 2.0),
        ],
        ids=["value", "other"],
    )
    def test_distance(self, arg, result):
        assert self.floatset.distance(arg) == result


class TestFloatSetSetFunctions(TestFloatSet):
    value = 5.0
    floatset = FloatSet("{1, 10}")

    @pytest.mark.parametrize("other", [value, floatset], ids=["value", "floatset"])
    def test_intersection(self, other):
        self.floatset.intersection(other)
        self.floatset * other

    @pytest.mark.parametrize("other", [value, floatset], ids=["value", "floatset"])
    def test_union(self, other):
        self.floatset.union(other)
        self.floatset + other

    @pytest.mark.parametrize("other", [value, floatset], ids=["value", "floatset"])
    def test_minus(self, other):
        self.floatset.minus(other)
        self.floatset - other


class TestFloatSetComparisons(TestFloatSet):
    floatset = FloatSet("{1, 10}")
    other = FloatSet("{2, 10}")

    def test_eq(self):
        _ = self.floatset == self.other

    def test_ne(self):
        _ = self.floatset != self.other

    def test_lt(self):
        _ = self.floatset < self.other

    def test_le(self):
        _ = self.floatset <= self.other

    def test_gt(self):
        _ = self.floatset > self.other

    def test_ge(self):
        _ = self.floatset >= self.other


# class TestFloatSetTransformationFunctions(TestFloatSet):

# @pytest.mark.parametrize(
# 'delta,result',
# [(4, [5, 6, 8]),
# (-4, [-3, -1, 0]),
# ],
# ids=['positive delta', 'negative delta']
# )
# def test_shift(self, delta, result):
# shifted = self.floatset.shift(delta)
# self.assert_intset_equality(shifted, result)

# @pytest.mark.parametrize(
# 'delta,result',
# [(6, [1, 4, 7])],
# ids=['positive']
# )
# def test_scale(self, delta, result):
# scaled = self.floatset.scale(delta)
# self.assert_intset_equality(scaled, result)

# def test_shift_scale(self):
# shifted_scaled = self.floatset.shift_scale(4, 4)
# self.assert_intset_equality(shifted_scaled, [5, 7, 9])
