from datetime import date

from pymeos import DateSpanSet
from tests.conftest import TestPyMEOS


class TestDateSpanSet(TestPyMEOS):
    date_spanset = DateSpanSet("{[2019-09-08, 2019-09-10], [2019-09-12, 2019-09-14]}")


class TestDateSpanSetAccessors(TestDateSpanSet):
    # The dates of a date span set are the bounds of its spans, answered as a
    # list as #TestDateSetAccessors.test_elements answers the elements of a set
    def test_num_dates(self):
        assert self.date_spanset.num_dates() == 4

    def test_dates(self):
        assert self.date_spanset.dates() == [
            date(2019, 9, 8),
            date(2019, 9, 11),
            date(2019, 9, 12),
            date(2019, 9, 15),
        ]
