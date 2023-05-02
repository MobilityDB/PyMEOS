from datetime import datetime, timezone, timedelta
import pytest

from pymeos import Period, PeriodSet, TimestampSet, TFloatInst, TFloatSeq, STBox, TFloatSeqSet, TBox
from tests.conftest import TestPyMEOS


class TestPeriodSet(TestPyMEOS):

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


class TestPeriodSetConstructors(TestPeriodSet):
    pass
