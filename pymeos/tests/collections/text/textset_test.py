from copy import copy
from datetime import datetime, timezone, timedelta
from typing import List

import pytest

from pymeos import TextSet
from tests.conftest import TestPyMEOS


class TestTextSet(TestPyMEOS):
    tset = TextSet('{A, BB, ccc}')

    @staticmethod
    def assert_textset_equality(tset: TextSet,
                                elements: List[str]):
        assert tset.num_elements() == len(elements)
        assert tset.elements() == elements


class TestTextSetConstructors(TestTextSet):

    def test_string_constructor(self):
        self.assert_textset_equality(self.tset, ['A', 'BB', 'ccc'])

    def test_list_constructor(self):
        ts_set = TextSet(elements=['A', 'BB', 'ccc'])
        self.assert_textset_equality(ts_set, ['A', 'BB', 'ccc'])

    def test_hexwkb_constructor(self):
        ts_set = TextSet.from_hexwkb(
            '011A000103000000020000000000000041000300000000000000424200040000000000000063636300')
        self.assert_textset_equality(ts_set, ['A', 'BB', 'ccc'])

    def test_from_as_constructor(self):
        assert self.tset == TextSet(str(self.tset))
        assert self.tset == TextSet.from_wkb(self.tset.as_wkb())
        assert self.tset == TextSet.from_hexwkb(self.tset.as_hexwkb())

    def test_copy_constructor(self):
        ts_set_copy = copy(self.tset)
        assert self.tset == ts_set_copy
        assert self.tset is not ts_set_copy


class TestTextSetOutputs(TestTextSet):

    def test_str(self):
        assert str(self.tset) == '{"A", "BB", "ccc"}'

    def test_repr(self):
        assert repr(self.tset) == 'TextSet({"A", "BB", "ccc"})'

    def test_as_hexwkb(self):
        assert self.tset.as_hexwkb() == ('011A00010300000002000000000000004'
                                         '1000300000000000000424200040000000000000063636300')


class TestTimestampConversions(TestTextSet):

    def test_to_spanset(self):
        with pytest.raises(NotImplementedError):
            self.tset.to_spanset()

    def test_to_span(self):
        with pytest.raises(NotImplementedError):
            self.tset.to_span()


class TestTextSetAccessors(TestTextSet):

    def test_num_elements(self):
        assert self.tset.num_elements() == 3
        assert len(self.tset) == 3

    def test_start_element(self):
        assert self.tset.start_element() == 'A'

    def test_end_element(self):
        assert self.tset.end_element() == 'ccc'

    def test_element_n(self):
        assert self.tset.element_n(1) == 'BB'

    def test_element_n_out_of_range(self):
        with pytest.raises(IndexError):
            self.tset.element_n(3)

    def test_elements(self):
        assert self.tset.elements() == ['A', 'BB', 'ccc', ]

    def test_hash(self):
        assert hash(self.tset) == 3145376687


class TestTextSetPositionFunctions(TestTextSet):
    string = 'A'
    other = TextSet('{a, BB, ccc}')
    # period = Period('(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)')
    # periodset = PeriodSet(
    #     '{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}')
    # timestamp = datetime(year=2020, month=1, day=1)
    # TextSet = TextSet('{2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0}')
    # instant = TFloatInst('1.0@2020-01-01')
    # discrete_sequence = TFloatSeq('{1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31}')
    # stepwise_sequence = TFloatSeq('Interp=Step;(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]')
    # continuous_sequence = TFloatSeq('(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]')
    # sequence_set = TFloatSeqSet('{(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31], '
    #                             '(1.0@2021-01-01, 3.0@2021-01-10, 10.0@2021-01-20, 0.0@2021-01-31]}')

    @pytest.mark.parametrize(
        'other',
        [string, other],
        ids=['string', 'TextSet']
    )
    def test_is_adjacent(self, other):
        self.tset.is_adjacent(other)

    # @pytest.mark.parametrize(
    #     'other',
    #     [TextSet, period, periodset, instant, discrete_sequence, stepwise_sequence, continuous_sequence,
    #      sequence_set],
    #     ids=['TextSet', 'period', 'periodset', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence',
    #          'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_contained_in(self, other):
    #     self.tset.is_contained_in(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set']
    # )
    # def test_contains(self, other):
    #     self.tset.contains(other)
    #     _ = other in self.tset
    #
    # #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_overlaps(self, other):
    #     self.tset.overlaps(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_same(self, other):
    #     self.periodset.is_same(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_before(self, other):
    #     self.tset.is_before(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_over_or_before(self, other):
    #     self.tset.is_over_or_before(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_after(self, other):
    #     self.tset.is_after(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_is_over_or_after(self, other):
    #     self.tset.is_over_or_after(other)
    #
    # @pytest.mark.parametrize(
    #     'other',
    #     [period, periodset, timestamp, TextSet, instant, discrete_sequence, stepwise_sequence, sequence_set,
    #      continuous_sequence],
    #     ids=['period', 'periodset', 'timestamp', 'TextSet', 'instant', 'discrete_sequence', 'stepwise_sequence',
    #          'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    # )
    # def test_distance(self, other):
    #     self.tset.distance(other)


class TestTextSetSetFunctions(TestTextSet):
    string = 'A'
    other = TextSet('{a, BB, ccc}')

    @pytest.mark.parametrize(
        'other, expected',
        [(string, 'A'),
         (other, TextSet('{BB, ccc}'))],
        ids=['string', 'TextSet']
    )
    def test_intersection(self, other, expected):
        assert self.tset.intersection(other) == expected
        assert self.tset * other == expected

    @pytest.mark.parametrize(
        'other, expected',
        [(string, TextSet('{A, BB, ccc}')),
         (other, TextSet('{A, a, BB, ccc}'))],
        ids=['string', 'TextSet']
    )
    def test_union(self, other, expected):
        assert self.tset.union(other) == expected
        assert self.tset + other == expected

    @pytest.mark.parametrize(
        'other, expected',
        [(string, TextSet('{BB, ccc}')),
         (other, TextSet('{A}'))],
        ids=['string', 'TextSet']
    )
    def test_minus(self, other, expected):
        assert self.tset.minus(other) == expected
        assert self.tset - other == expected


class TestTextSetComparisons(TestTextSet):
    other = TextSet('{2020-01-02 00:00:00+0, 2020-03-31 00:00:00+0}')

    def test_eq(self):
        _ = self.tset == self.other

    def test_ne(self):
        _ = self.tset != self.other

    def test_lt(self):
        _ = self.tset < self.other

    def test_le(self):
        _ = self.tset <= self.other

    def test_gt(self):
        _ = self.tset > self.other

    def test_ge(self):
        _ = self.tset >= self.other


class TestTextSetMiscFunctions(TestTextSet):

    def test_hash(self):
        hash(self.tset)
