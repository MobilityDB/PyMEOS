import pytest
from pymeos_cffi import meos_get_datestyle, meos_get_intervalstyle

from pymeos import pymeos_initialize
from tests.conftest import TestPyMEOS


# Laid out as #TestTInterpolation; each test restores the styles it changes, since
# every other test runs under the styles conftest initializes.
class TestPyMEOSInitialize(TestPyMEOS):
    @pytest.mark.parametrize(
        "date_style, expected",
        [
            ("SQL, DMY", "SQL, DMY"),
            ("German", "German, DMY"),
            ("Postgres, MDY", "Postgres, MDY"),
        ],
        ids=["SQL DMY", "German", "Postgres MDY"],
    )
    def test_date_style(self, date_style, expected):
        previous = meos_get_datestyle()
        try:
            pymeos_initialize("UTC", date_style=date_style)
            assert meos_get_datestyle() == expected
        finally:
            pymeos_initialize("UTC", date_style=previous)

    @pytest.mark.parametrize(
        "interval_style",
        ["postgres", "postgres_verbose", "sql_standard", "iso_8601"],
    )
    def test_interval_style(self, interval_style):
        previous = meos_get_intervalstyle()
        try:
            pymeos_initialize("UTC", interval_style=interval_style)
            assert meos_get_intervalstyle() == interval_style
        finally:
            pymeos_initialize("UTC", interval_style=previous)
