import pytest

from pymeos import (
    STBox,
    TBoolSeq,
    TBoolSeqSet,
    TBox,
    TFloatSeq,
    TFloatSeqSet,
    TGeomPointSeq,
    TIntSeq,
    TIntSeqSet,
    TsTzSet,
    TsTzSpan,
    TTextSeq,
    TTextSeqSet,
)
from pymeos.aggregators import (
    TemporalAndAggregator,
    TemporalAverageAggregator,
    TemporalExtentAggregator,
    TemporalFloatMaxAggregator,
    TemporalFloatMinAggregator,
    TemporalFloatSumAggregator,
    TemporalInstantCountAggregator,
    TemporalIntMaxAggregator,
    TemporalIntMinAggregator,
    TemporalIntSumAggregator,
    TemporalNumberExtentAggregator,
    TemporalOrAggregator,
    TemporalPeriodCountAggregator,
    TemporalPointExtentAggregator,
    TemporalTextMaxAggregator,
    TemporalTextMinAggregator,
    TimeInstantaneousUnionAggregator,
)
from tests.conftest import TestPyMEOS


class TestAggregators(TestPyMEOS):
    """Every aggregator on two overlapping inputs, laid out as #TestTBoxConstructors is."""

    ints = [TIntSeq("[1@2000-01-01, 3@2000-01-03]"), TIntSeq("[2@2000-01-02, 2@2000-01-04]")]
    floats = [TFloatSeq("[1@2000-01-01, 3@2000-01-03]"), TFloatSeq("[2@2000-01-02, 2@2000-01-04]")]
    bools = [TBoolSeq("[t@2000-01-01, f@2000-01-03]"), TBoolSeq("[t@2000-01-02, t@2000-01-04]")]
    texts = [TTextSeq('["a"@2000-01-01, "c"@2000-01-03]'), TTextSeq('["b"@2000-01-02, "b"@2000-01-04]')]
    points = [
        TGeomPointSeq("[POINT(0 0)@2000-01-01, POINT(2 2)@2000-01-03]"),
        TGeomPointSeq("[POINT(1 3)@2000-01-02, POINT(1 3)@2000-01-04]"),
    ]
    spans = [TsTzSpan("[2000-01-01, 2000-01-03]"), TsTzSpan("[2000-01-02, 2000-01-04]")]
    sets = [TsTzSet("{2000-01-01, 2000-01-03}"), TsTzSet("{2000-01-02, 2000-01-03}")]

    @pytest.mark.parametrize(
        "aggregator, inputs, expected",
        [
            (
                TemporalAndAggregator,
                bools,
                TBoolSeqSet("{[t@2000-01-01, f@2000-01-03], (t@2000-01-03, t@2000-01-04]}"),
            ),
            (TemporalOrAggregator, bools, TBoolSeqSet("{[t@2000-01-01, t@2000-01-04]}")),
            (
                TemporalIntMaxAggregator,
                ints,
                TIntSeqSet("{[1@2000-01-01, 2@2000-01-02, 3@2000-01-03], (2@2000-01-03, 2@2000-01-04]}"),
            ),
            (
                TemporalIntMinAggregator,
                ints,
                TIntSeqSet("{[1@2000-01-01, 2@2000-01-03, 2@2000-01-04]}"),
            ),
            (
                TemporalIntSumAggregator,
                ints,
                TIntSeqSet("{[1@2000-01-01, 3@2000-01-02, 5@2000-01-03], (2@2000-01-03, 2@2000-01-04]}"),
            ),
            (
                TemporalFloatMaxAggregator,
                floats,
                TFloatSeqSet("{[1@2000-01-01, 3@2000-01-03], (2@2000-01-03, 2@2000-01-04]}"),
            ),
            (
                TemporalFloatMinAggregator,
                floats,
                TFloatSeqSet("{[1@2000-01-01, 2@2000-01-02, 2@2000-01-04]}"),
            ),
            (
                TemporalFloatSumAggregator,
                floats,
                TFloatSeqSet(
                    "{[1@2000-01-01, 2@2000-01-02), [4@2000-01-02, 5@2000-01-03], (2@2000-01-03, 2@2000-01-04]}"
                ),
            ),
            (
                TemporalAverageAggregator,
                floats,
                TFloatSeqSet("{[1@2000-01-01, 2@2000-01-02, 2.5@2000-01-03], (2@2000-01-03, 2@2000-01-04]}"),
            ),
            (
                TemporalTextMaxAggregator,
                texts,
                TTextSeqSet('{["a"@2000-01-01, "b"@2000-01-02, "c"@2000-01-03], ("b"@2000-01-03, "b"@2000-01-04]}'),
            ),
            (
                TemporalTextMinAggregator,
                texts,
                TTextSeqSet('{["a"@2000-01-01, "b"@2000-01-03, "b"@2000-01-04]}'),
            ),
            (
                TemporalInstantCountAggregator,
                sets,
                TIntSeq("{1@2000-01-01, 1@2000-01-02, 2@2000-01-03}"),
            ),
            (
                TemporalPeriodCountAggregator,
                spans,
                TIntSeqSet("{[1@2000-01-01, 2@2000-01-02, 2@2000-01-03], (1@2000-01-03, 1@2000-01-04]}"),
            ),
            (
                TimeInstantaneousUnionAggregator,
                sets,
                TsTzSet("{2000-01-01, 2000-01-02, 2000-01-03}"),
            ),
        ],
        ids=[
            "And",
            "Or",
            "IntMax",
            "IntMin",
            "IntSum",
            "FloatMax",
            "FloatMin",
            "FloatSum",
            "Average",
            "TextMax",
            "TextMin",
            "InstantCount",
            "PeriodCount",
            "InstantaneousUnion",
        ],
    )
    def test_aggregate(self, aggregator, inputs, expected):
        assert aggregator.aggregate(inputs) == expected

    @pytest.mark.parametrize(
        "aggregator, inputs, expected",
        [
            (
                TemporalNumberExtentAggregator,
                floats,
                TBox("TBOXFLOAT XT([1, 3],[2000-01-01, 2000-01-04])"),
            ),
            (
                TemporalPointExtentAggregator,
                points,
                STBox("STBOX XT(((0,0),(2,3)),[2000-01-01, 2000-01-04])"),
            ),
            (TemporalExtentAggregator, ints, TsTzSpan("[2000-01-01, 2000-01-04]")),
        ],
        ids=["NumberExtent", "PointExtent", "TimeExtent"],
    )
    def test_extent(self, aggregator, inputs, expected):
        assert aggregator.aggregate(inputs) == expected

    def test_incremental_aggregation(self):
        aggregation = TemporalIntSumAggregator.start_aggregation()
        for temporal in self.ints:
            aggregation.add(temporal)
        assert aggregation.aggregation() == TemporalIntSumAggregator.aggregate(self.ints)
