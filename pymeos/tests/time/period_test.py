from datetime import datetime, timezone, timedelta

import pytest

from pymeos import Period, PeriodSet, TimestampSet, TBoolSeq, TBox
from tests.conftest import TestPyMEOS


class TestPeriod(TestPyMEOS):

    @staticmethod
    def assert_period_equality(period: Period,
                               lower: datetime = None,
                               upper: datetime = None,
                               lower_inc: bool = None,
                               upper_inc: bool = None):
        if lower is not None:
            assert period.lower() == lower
        if upper is not None:
            assert period.upper() == upper
        if lower_inc is not None:
            assert period.lower_inc() == lower_inc
        if upper_inc is not None:
            assert period.upper_inc() == upper_inc

    pass


class TestPeriodConstructors(TestPeriod):

    @pytest.mark.parametrize(
        'source,params',
        [
            ('(2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0)',
             (datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc), False, False)),
            ('[2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0]',
             (datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc), True, True)),
        ]
    )
    def test_string_constructor(self, source, params):
        period = Period(source)
        self.assert_period_equality(period, *params)

    @pytest.mark.parametrize(
        'input_lower,input_upper,lower,upper',
        [
            ('2019-09-08 00:00:00+0', '2019-09-10 00:00:00+0',
             datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc)),
            (datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc),
             datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc)),
            (datetime(2019, 9, 8, tzinfo=timezone.utc), '2019-09-10 00:00:00+0',
             datetime(2019, 9, 8, tzinfo=timezone.utc), datetime(2019, 9, 10, tzinfo=timezone.utc)),
        ],
        ids=['string', 'datetime', 'mixed']
    )
    def test_constructor_bounds(self, input_lower, input_upper, lower, upper):
        period = Period(lower=lower, upper=upper)
        self.assert_period_equality(period, lower, upper)

    def test_constructor_bound_inclusivity_defaults(self):
        period = Period(lower='2019-09-08 00:00:00+0', upper='2019-09-10 00:00:00+0')
        self.assert_period_equality(period, lower_inc=True, upper_inc=False)

    @pytest.mark.parametrize(
        'lower,upper',
        [
            (True, True),
            (True, False),
            (False, True),
            (False, False),
        ]
    )
    def test_constructor_bound_inclusivity(self, lower, upper):
        period = Period(lower='2019-09-08 00:00:00+0', upper='2019-09-10 00:00:00+0', lower_inc=lower, upper_inc=upper)
        self.assert_period_equality(period, lower_inc=lower, upper_inc=upper)

    def test_hexwkb_constructor(self):
        source = '010A00000040021FFE3402000000B15A26350200'
        period = Period.from_hexwkb(source)
        self.assert_period_equality(period, datetime(2019, 9, 8, tzinfo=timezone.utc),
                                    datetime(2019, 9, 10, tzinfo=timezone.utc), False, False)


class TestPeriodAccessors(TestPeriod):
    period = Period('(2019-09-08 00:00:00+0, 2019-09-10 00:00:00+0)')
    period2 = Period('[2019-09-08 02:03:00+0, 2019-09-10 02:03:00+0]')

    def test_lower(self):
        assert self.period.lower() == datetime(2019, 9, 8, tzinfo=timezone.utc)
        assert self.period2.lower() == datetime(2019, 9, 8, 2, 3, tzinfo=timezone.utc)

    def test_upper(self):
        assert self.period.upper() == datetime(2019, 9, 10, tzinfo=timezone.utc)
        assert self.period2.upper() == datetime(2019, 9, 10, 2, 3, tzinfo=timezone.utc)

    def test_lower_inc(self):
        assert not self.period.lower_inc()
        assert self.period2.lower_inc()

    def test_upper_inc(self):
        assert not self.period.upper_inc()
        assert self.period2.upper_inc()

    def test_duration(self):
        assert self.period.duration() == timedelta(days=2)
        assert self.period2.duration() == timedelta(days=2)

    def test_duration_in_seconds(self):
        assert self.period.duration_in_seconds() == 172800
        assert self.period2.duration_in_seconds() == 172800


class TestPeriodPositionFunctions(TestPeriod):
    period = Period('(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0)')
    periodset = PeriodSet('{(2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0), '
                          '(2021-01-01 00:00:00+0, 2021-01-31 00:00:00+0)}')
    timestamp = datetime(year=2020, month=1, day=1)
    timestampset = TimestampSet('{2020-01-01 00:00:00+0, 2020-01-31 00:00:00+0}')
    temporal = TBoolSeq('(TRUE@2000-01-01, FALSE@2000-01-10, TRUE@2000-01-20, TRUE@2000-01-31)')
    box = TBox('TBox XT([0, 10),[2020-01-01, 2020-01-31])')

    @pytest.mark.parametrize(
        'other',
        [period, periodset, timestamp, timestampset, temporal, box]
    )
    def test_is_adjacent(self, other):
        self.period.is_adjacent(other)
