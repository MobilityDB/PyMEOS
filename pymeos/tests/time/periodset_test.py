from copy import copy
from datetime import datetime, timezone, timedelta
from typing import List

import pytest

from pymeos import Period, PeriodSet, TimestampSet, TFloatInst, TFloatSeq, STBox, TFloatSeqSet, TBox
from tests.conftest import TestPyMEOS


class TestPeriodSet(TestPyMEOS):

    @staticmethod
    def assert_periodset_equality(periodset: PeriodSet, periods: List[Period]):
        assert periodset.num_periods() == len(periods)
        assert periodset.periods() == periods


class TestPeriodSetConstructors(TestPeriodSet):
    periodset = PeriodSet('{[2019-01-01, 2019-01-02], [2019-01-03, 2019-01-04]}')

    def test_string_constructor(self):
        self.assert_periodset_equality(self.periodset, [
            Period('[2019-01-01, 2019-01-02]'),
            Period('[2019-01-03, 2019-01-04]')
        ])

    def test_period_list_constructor(self):
        periodset = PeriodSet(period_list=[
            Period('[2019-01-01, 2019-01-02]'),
            Period('[2019-01-03, 2019-01-04]')
        ])
        self.assert_periodset_equality(periodset, [
            Period('[2019-01-01, 2019-01-02]'),
            Period('[2019-01-03, 2019-01-04]')
        ])

    def test_from_as_hexwkb_constructor(self):
        assert self.periodset == self.periodset.from_hexwkb(self.periodset.as_hexwkb())

    def test_copy_constructor(self):
        copied = copy(self.periodset)
        assert self.periodset == copied
        assert self.periodset is not copied


class TestPeriodSetOutputs(TestPeriodSet):
    periodset = PeriodSet('{[2019-01-01, 2019-01-02], [2019-01-03, 2019-01-04]}')

    def test_str(self):
        assert str(self.periodset) == '{[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00], ' \
                                      '[2019-01-03 00:00:00+00, 2019-01-04 00:00:00+00]}'

    def test_repr(self):
        assert repr(self.periodset) == 'PeriodSet({[2019-01-01 00:00:00+00, 2019-01-02 00:00:00+00], ' \
                                       '[2019-01-03 00:00:00+00, 2019-01-04 00:00:00+00]})'

    def test_hexwkb(self):
        assert self.periodset.as_hexwkb() == '01220002000000030080AEFA5821020000E085186D2102000300405D368121020000A0345495210200'

    def test_to_period(self):
        assert self.periodset.to_period() == Period('[2019-01-01, 2019-01-04]')


class TestPeriodSetAccessors(TestPeriodSet):
    periodset = PeriodSet('{[2019-01-01, 2019-01-02], [2019-01-03, 2019-01-04]}')
    periodset2 = PeriodSet('{[2019-01-01, 2019-01-02), (2019-01-02, 2019-01-04]}')

    def test_duration(self):
        assert self.periodset.duration() == timedelta(days=2)

    def test_timespan(self):
        assert self.periodset.timespan() == timedelta(days=3)

    def test_num_timestamps(self):
        assert self.periodset.num_timestamps() == 4
        assert self.periodset2.num_timestamps() == 3

    def test_start_timestamp(self):
        assert self.periodset.start_timestamp() == datetime(2019, 1, 1, tzinfo=timezone.utc)

    def test_end_timestamp(self):
        assert self.periodset.end_timestamp() == datetime(2019, 1, 4, tzinfo=timezone.utc)

    def test_timestamp_n(self):
        assert self.periodset.timestamp_n(0) == datetime(2019, 1, 1, tzinfo=timezone.utc)
        assert self.periodset.timestamp_n(1) == datetime(2019, 1, 2, tzinfo=timezone.utc)
        assert self.periodset.timestamp_n(2) == datetime(2019, 1, 3, tzinfo=timezone.utc)
        assert self.periodset.timestamp_n(3) == datetime(2019, 1, 4, tzinfo=timezone.utc)

    def test_timestamps(self):
        assert self.periodset.timestamps() == [
            datetime(2019, 1, 1, tzinfo=timezone.utc),
            datetime(2019, 1, 2, tzinfo=timezone.utc),
            datetime(2019, 1, 3, tzinfo=timezone.utc),
            datetime(2019, 1, 4, tzinfo=timezone.utc),
        ]

    def test_num_periods(self):
        assert self.periodset.num_periods() == 2

    def test_start_period(self):
        assert self.periodset.start_period() == Period('[2019-01-01, 2019-01-02]')

    def test_end_period(self):
        assert self.periodset.end_period() == Period('[2019-01-03, 2019-01-04]')

    def test_period_n(self):
        assert self.periodset.period_n(0) == Period('[2019-01-01, 2019-01-02]')
        assert self.periodset.period_n(1) == Period('[2019-01-03, 2019-01-04]')

    def test_periods(self):
        assert self.periodset.periods() == [
            Period('[2019-01-01, 2019-01-02]'),
            Period('[2019-01-03, 2019-01-04]')
        ]

    def test_hash(self):
        assert hash(self.periodset) == 942160317


class TestPeriodPositionFunctions(TestPeriodSet):
    period = Period('(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)')
    periodset = PeriodSet(
        '{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}')
    timestamp = datetime(year=2020, month=1, day=1)
    timestampset = TimestampSet('{2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0}')
    instance = TFloatInst('1.0@2020-01-01')
    discrete_sequence = TFloatSeq('{1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31}')
    stepwise_sequence = TFloatSeq('Interp=Step;(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]')
    continuous_sequence = TFloatSeq('(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31]')
    sequence_set = TFloatSeqSet('{(1.0@2020-01-01, 3.0@2020-01-10, 10.0@2020-01-20, 0.0@2020-01-31], '
                                '(1.0@2021-01-01, 3.0@2021-01-10, 10.0@2021-01-20, 0.0@2021-01-31]}')
    tbox = TBox('TBox XT([0, 10),[2020-01-01, 2020-01-31])')
    stbox = STBox('STBOX ZT(((1.0,2.0,3.0),(4.0,5.0,6.0)),[2001-01-01, 2001-01-02])')

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_adjacent(self, other):
        self.periodset.is_adjacent(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, instance, discrete_sequence, stepwise_sequence, continuous_sequence, sequence_set, tbox,
         stbox],
        ids=['period', 'periodset', 'instance', 'discrete_sequence', 'stepwise_sequence', 'continuous_sequence',
             'sequence_set', 'tbox', 'stbox']
    )
    def test_is_contained_in(self, other):
        self.periodset.is_contained_in(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_contains(self, other):
        self.periodset.contains(other)
        _ = other in self.periodset

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_overlaps(self, other):
        self.periodset.overlaps(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_before(self, other):
        self.periodset.is_before(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_over_or_before(self, other):
        self.periodset.is_over_or_before(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_same(self, other):
        self.periodset.is_same(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_over_or_after(self, other):
        self.periodset.is_over_or_after(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_is_after(self, other):
        self.periodset.is_after(other)

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, instance, discrete_sequence, stepwise_sequence, sequence_set,
         continuous_sequence, tbox, stbox],
        ids=['period', 'periodset', 'timestamp', 'timestampset', 'instance', 'discrete_sequence', 'stepwise_sequence',
             'continuous_sequence', 'sequence_set', 'tbox', 'stbox']
    )
    def test_distance(self, other):
        self.periodset.distance(other)


class TestPeriodSetFunctions(TestPeriodSet):
    period = Period('(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)')
    periodset = PeriodSet(
        '{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}')
    timestamp = datetime(year=2020, month=1, day=1)
    timestampset = TimestampSet('{2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0}')

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset],
        ids=['period', 'periodset', 'timestamp', 'timestampset']
    )
    def test_intersection(self, other):
        self.periodset.intersection(other)
        self.periodset * other

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset],
        ids=['period', 'periodset', 'timestamp', 'timestampset']
    )
    def test_union(self, other):
        self.periodset.union(other)
        self.periodset + other

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset],
        ids=['period', 'periodset', 'timestamp', 'timestampset']
    )
    def test_minus(self, other):
        self.periodset.minus(other)
        self.periodset - other


class TestPeriodComparisonFunctions(TestPeriodSet):
    periodset = PeriodSet(
        '{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), (2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}')
    other = PeriodSet(
        '{(2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0), (2022-01-01 00:00:00+0, 2022-01-31 00:00:00+0)}')

    def test_eq(self):
        _ = self.periodset == self.other

    def test_ne(self):
        _ = self.periodset != self.other

    def test_lt(self):
        _ = self.periodset < self.other

    def test_le(self):
        _ = self.periodset <= self.other

    def test_gt(self):
        _ = self.periodset > self.other

    def test_ge(self):
        _ = self.periodset >= self.other


class TestPeriodManipulationFunctions(TestPeriodSet):
    periodset = PeriodSet(
        '{(2020-01-01 00:00:00+0, 2020-01-03 00:00:00+0), (2020-01-05 00:00:00+0, 2020-01-07 00:00:00+0)}')

    @pytest.mark.parametrize(
        'delta,result',
        [(timedelta(days=4),
          [Period('(2020-01-05 00:00:00+0, 2020-01-07 00:00:00+0)'),
           Period('(2020-01-09 00:00:00+0, 2020-01-11 00:00:00+0)')]),
         (timedelta(days=-4),
          [Period('(2019-12-28 00:00:00+0, 2019-12-30 00:00:00+0)'),
           Period('(2020-01-01 00:00:00+00, 2020-01-03 00:00:00+00)')]),
         (timedelta(hours=2),
          [Period('(2020-01-01 02:00:00+0, 2020-01-03 02:00:00+0)'),
           Period('(2020-01-05 02:00:00+0, 2020-01-07 02:00:00+0)')]),
         (timedelta(hours=-2),
          [Period('(2019-12-31 22:00:00+0, 2020-01-02 22:00:00+0)'),
           Period('(2020-01-04 22:00:00+0, 2020-01-06 22:00:00+0)')]),
         ],
        ids=['positive days', 'negative days', 'positive hours', 'negative hours']
    )
    def test_shift(self, delta, result):
        shifted = self.periodset.shift(delta)
        self.assert_periodset_equality(shifted, result)

    @pytest.mark.parametrize(
        'delta,result',
        [(timedelta(days=3),
          [Period('(2020-01-01 00:00:00+0, 2020-01-02 00:00:00+0)'),
           Period('(2020-01-03 00:00:00+0, 2020-01-04 00:00:00+0)')]),
         (timedelta(hours=6),
          [Period('(2020-01-01 00:00:00+0, 2020-01-01 02:00:00+0)'),
           Period('(2020-01-01 04:00:00+0, 2020-01-01 06:00:00+0)'), ]),
         ],
        ids=['days', 'hours']
    )
    def test_tscale(self, delta, result):
        scaled = self.periodset.tscale(delta)
        self.assert_periodset_equality(scaled, result)

    def test_shift_tscale(self):
        shifted_scaled = self.periodset.shift_tscale(timedelta(days=4), timedelta(hours=6))
        self.assert_periodset_equality(shifted_scaled, [Period('(2020-01-05 00:00:00+0, 2020-01-05 02:00:00+0)'),
                                                        Period('(2020-01-05 04:00:00+0, 2020-01-05 06:00:00+0)')])


class TestPeriodMiscFunctions(TestPeriodSet):
    periodset = PeriodSet(
        '{(2020-01-01 00:00:00+0, 2020-01-03 00:00:00+0), (2020-01-05 00:00:00+0, 2020-01-07 00:00:00+0)}')

    def test_hash(self):
        hash(self.periodset)
