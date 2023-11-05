from pymeos import TInterpolation
from tests.conftest import TestPyMEOS
import pytest


class TestTInterpolation(TestPyMEOS):
    @pytest.mark.parametrize(
        "source, result",
        [
            ("discrete", TInterpolation.DISCRETE),
            ("linear", TInterpolation.LINEAR),
            ("stepwise", TInterpolation.STEPWISE),
            ("step", TInterpolation.STEPWISE),
            ("none", TInterpolation.NONE),
        ],
        ids=["discrete", "linear", "stepwise", "step", "none"],
    )
    def test_from_string(self, source, result):
        assert TInterpolation.from_string(source) == result

    def test_from_string_invalid(self):
        assert TInterpolation.from_string("invalid") == TInterpolation.NONE

    def test_from_string_invalid_none(self):
        with pytest.raises(ValueError):
            TInterpolation.from_string("invalid", none=False)
