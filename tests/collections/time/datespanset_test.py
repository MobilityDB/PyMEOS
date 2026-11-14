from datetime import date, timedelta

import pytest

from pymeos import DateSpan, DateSpanSet
from tests.conftest import TestPyMEOS


class TestDateSpanSet(TestPyMEOS):
    date_spanset = DateSpanSet("{[2019-09-08, 2019-09-10], [2019-09-12, 2019-09-14]}")


class TestDateSpanSetTransformations(TestDateSpanSet):
    # The shifts of a date span set and of a date span, as
    # #TestDateSetFunctionsFunctions.test_shift_zero and
    # #TestDateSetFunctionsFunctions.test_shift_scale_below_a_day shift a date set
    date_span = DateSpan("[2019-09-08, 2019-09-14]")

    @pytest.mark.parametrize("delta", [timedelta(0), 0], ids=["timedelta", "int"])
    def test_shift_zero(self, delta):
        assert self.date_spanset.shift(delta) == self.date_spanset
        assert self.date_span.shift(delta) == self.date_span

    @pytest.mark.parametrize(
        "delta",
        [timedelta(hours=12), timedelta(hours=-1), timedelta(days=1, hours=23)],
        ids=["half a day", "minus one hour", "one day and 23 hours"],
    )
    def test_shift_scale_below_a_day(self, delta):
        for value in (self.date_spanset, self.date_span):
            with pytest.raises(ValueError):
                value.shift(delta)
            with pytest.raises(ValueError):
                value.scale(delta)


class TestDateSpanSetConversions(TestDateSpanSet):
    # The span of a date span set, as #TestCollectionConversions.test_to_span of
    # dateset_test.py checks the span of a date set
    def test_to_span(self):
        assert self.date_spanset.to_span() == DateSpan("[2019-09-08, 2019-09-14]")


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

    # The n-th date answers what #test_dates lists, as
    # #TestDateSetAccessors.test_element_n checks a date set
    def test_date_n(self):
        assert [self.date_spanset.date_n(i) for i in range(4)] == self.date_spanset.dates()
