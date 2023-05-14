from datetime import datetime, timezone

import pytest

from pymeos import TBoolInst
from tests.main.tbool.tbool_test import TestTBool
from tests.temporal.tinstant_test import TestTInstant


class TestTBoolInst(TestTInstant, TestTBool):
    pass


class TestTBoolInstConstructors(TestTBoolInst):

    def test_string_constructor(self):
        tbi = TBoolInst('True@2019-09-01')
        self.assert_instant_equality(tbi, True, datetime(2019, 9, 1, tzinfo=timezone.utc))

    @pytest.mark.parametrize(
        'value, timestamp',
        [
            (True, datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('TRUE', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            (True, '2019-09-01'),
            ('TRUE', '2019-09-01'),
        ],
        ids=['bool-datetime', 'string-datetime', 'bool-string', 'string-string']
    )
    def test_value_timestamp_constructor(self, value, timestamp):
        tbi = TBoolInst(value=value, timestamp=timestamp)
        self.assert_instant_equality(tbi, True, datetime(2019, 9, 1, tzinfo=timezone.utc))
