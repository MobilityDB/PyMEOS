from tests.conftest import TestPyMEOS


class TestTInstant(TestPyMEOS):
    @staticmethod
    def assert_instant_equality(instant, expected_value, expected_timestamp):
        assert instant.value() == expected_value
        assert instant.timestamp() == expected_timestamp
