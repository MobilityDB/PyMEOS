from copy import copy

import pytest

from pymeos import IntSpan, IntSpanSet

from tests.conftest import TestPyMEOS


class TestIntSpan(TestPyMEOS):
    intspan = IntSpan("[7, 10)")

    @staticmethod
    def assert_intspan_equality(
        intspan: IntSpan,
        lower: int = None,
        upper: int = None,
        lower_inc: bool = None,
        upper_inc: bool = None,
    ):
        if lower is not None:
            assert intspan.lower() == lower
        if upper is not None:
            assert intspan.upper() == upper
        if lower_inc is not None:
            assert intspan.lower_inc() == lower_inc
        if upper_inc is not None:
            assert intspan.upper_inc() == upper_inc


class TestIntSpanConstructors(TestIntSpan):
    @pytest.mark.parametrize(
        "source, params",
        [
            ("(7, 10)", (8, 10, True, False)),
            ("[7, 10]", (7, 11, True, False)),
        ],
    )
    def test_string_constructor(self, source, params):
        intspan = IntSpan(source)
        self.assert_intspan_equality(intspan, *params)

    @pytest.mark.parametrize(
        "input_lower,input_upper,lower,upper",
        [
            ("7", "10", 7, 10),
            (7, 10, 7, 10),
            (7, "10", 7, 10),
        ],
        ids=["string", "int", "mixed"],
    )
    def test_constructor_bounds(self, input_lower, input_upper, lower, upper):
        intspan = IntSpan(lower=lower, upper=upper)
        self.assert_intspan_equality(intspan, lower, upper)

    def test_constructor_bound_inclusivity_defaults(self):
        intspan = IntSpan(lower="7", upper="10")
        self.assert_intspan_equality(intspan, lower_inc=True, upper_inc=False)

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
        intspan = IntSpan(lower="7", upper="10", lower_inc=lower, upper_inc=upper)
        self.assert_intspan_equality(intspan, lower_inc=True, upper_inc=False)

    def test_hexwkb_constructor(self):
        source = "010D0001070000000A000000"
        intspan = IntSpan.from_hexwkb(source)
        self.assert_intspan_equality(intspan, 7, 10, True, False)

    def test_from_as_constructor(self):
        assert self.intspan == IntSpan(str(self.intspan))
        assert self.intspan == IntSpan.from_wkb(self.intspan.as_wkb())
        assert self.intspan == IntSpan.from_hexwkb(self.intspan.as_hexwkb())

    def test_copy_constructor(self):
        other = copy(self.intspan)
        assert self.intspan == other
        assert self.intspan is not other


class TestIntSpanOutputs(TestIntSpan):
    def test_str(self):
        assert str(self.intspan) == "[7, 10)"

    def test_repr(self):
        assert repr(self.intspan) == "IntSpan([7, 10))"

    def test_hexwkb(self):
        assert self.intspan.as_hexwkb() == "010D0001070000000A000000"


class TestIntSpanConversions(TestIntSpan):
    def test_to_intspanset(self):
        intspanset = self.intspan.to_spanset()
        assert isinstance(intspanset, IntSpanSet)
        assert intspanset.num_spans() == 1
        assert intspanset.start_span() == self.intspan


class TestIntSpanAccessors(TestIntSpan):
    intspan2 = IntSpan("[8, 11]")

    def test_lower(self):
        assert self.intspan.lower() == 7
        assert self.intspan2.lower() == 8

    def test_upper(self):
        assert self.intspan.upper() == 10
        assert self.intspan2.upper() == 12

    def test_lower_inc(self):
        assert self.intspan.lower_inc()
        assert self.intspan2.lower_inc()

    def test_upper_inc(self):
        assert not self.intspan.upper_inc()
        assert not self.intspan2.upper_inc()

    def test_width(self):
        assert self.intspan.width() == 3
        assert self.intspan2.width() == 4

    def test_hash(self):
        assert hash(self.intspan) == 1519224342


class TestIntSpanTransformations(TestIntSpan):
    @pytest.mark.parametrize(
        "delta,result",
        [
            (4, (11, 14, True, False)),
            (-4, (3, 6, True, False)),
        ],
        ids=["positive delta", "negative delta"],
    )
    def test_shift(self, delta, result):
        shifted = self.intspan.shift(delta)
        self.assert_intspan_equality(shifted, *result)

    @pytest.mark.parametrize(
        "delta,result",
        [
            (4, (7, 12, True, False)),
        ],
        ids=["positive"],
    )
    def test_scale(self, delta, result):
        scaled = self.intspan.scale(delta)
        self.assert_intspan_equality(scaled, *result)

    def test_shift_scale(self):
        shifted_scaled = self.intspan.shift_scale(4, 2)
        self.assert_intspan_equality(shifted_scaled, 11, 14, True, False)


class TestIntSpanTopologicalPositionFunctions(TestIntSpan):
    value = 5
    intspan = IntSpan("(1, 20)")
    intspanset = IntSpanSet("{(1, 20), (31, 41)}")

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_adjacent(self, other):
        self.intspan.is_adjacent(other)

    @pytest.mark.parametrize(
        "other", [intspan, intspanset], ids=["intspan", "intspanset"]
    )
    def test_is_contained_in(self, other):
        self.intspan.is_contained_in(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_contains(self, other):
        self.intspan.contains(other)
        _ = other in self.intspan

    @pytest.mark.parametrize(
        "other", [intspan, intspanset], ids=["intspan", "intspanset"]
    )
    def test_overlaps(self, other):
        self.intspan.overlaps(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_same(self, other):
        self.intspan.is_same(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_left(self, other):
        self.intspan.is_left(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_over_or_left(self, other):
        self.intspan.is_over_or_left(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_right(self, other):
        self.intspan.is_right(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_is_over_or_right(self, other):
        self.intspan.is_over_or_right(other)

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_distance(self, other):
        self.intspan.distance(other)


class TestIntSpanSetFunctions(TestIntSpan):
    value = 1
    intspan = IntSpan("(1, 20)")
    intspanset = IntSpanSet("{(1, 20), (31, 41)}")

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_intersection(self, other):
        self.intspan.intersection(other)
        self.intspan * other

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_union(self, other):
        self.intspan.union(other)
        self.intspan + other

    @pytest.mark.parametrize(
        "other", [value, intspan, intspanset], ids=["value", "intspan", "intspanset"]
    )
    def test_minus(self, other):
        self.intspan.minus(other)
        self.intspan - other


class TestIntSpanComparisons(TestIntSpan):
    intspan = IntSpan("(1, 20)")
    other = IntSpan("[5, 10)")

    def test_eq(self):
        _ = self.intspan == self.other

    def test_ne(self):
        _ = self.intspan != self.other

    def test_lt(self):
        _ = self.intspan < self.other

    def test_le(self):
        _ = self.intspan <= self.other

    def test_gt(self):
        _ = self.intspan > self.other

    def test_ge(self):
        _ = self.intspan >= self.other
