from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import (
    TBool,
    TBoolInst,
    TBoolSeq,
    TBoolSeqSet,
    TText,
    TTextInst,
    TTextSeq,
    TTextSeqSet,
    TInt,
    TIntInst,
    TIntSeq,
    TIntSeqSet,
    TInterpolation,
    TimestampSet,
    Period,
    PeriodSet,
)
from tests.conftest import TestPyMEOS


class TestTText(TestPyMEOS):
    pass


class TestTTextConstructors(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "source, type, interpolation",
        [
            (TIntInst("1@2019-09-01"), TTextInst, TInterpolation.NONE),
            (
                TIntSeq("{1@2019-09-01, 2@2019-09-02}"),
                TTextSeq,
                TInterpolation.DISCRETE,
            ),
            (
                TIntSeq("[1@2019-09-01, 2@2019-09-02]"),
                TTextSeq,
                TInterpolation.STEPWISE,
            ),
            (
                TIntSeqSet(
                    "{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}"
                ),
                TTextSeqSet,
                TInterpolation.STEPWISE,
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_temporal_constructor(self, source, type, interpolation):
        tt = TText.from_base_temporal("AAA", source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation

    @pytest.mark.parametrize(
        "source, type, interpolation",
        [
            (datetime(2000, 1, 1), TTextInst, TInterpolation.NONE),
            (
                TimestampSet("{2019-09-01, 2019-09-02}"),
                TTextSeq,
                TInterpolation.DISCRETE,
            ),
            (Period("[2019-09-01, 2019-09-02]"), TTextSeq, TInterpolation.STEPWISE),
            (
                PeriodSet("{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}"),
                TTextSeqSet,
                TInterpolation.STEPWISE,
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tt = TText.from_base_time("AAA", source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation

    @pytest.mark.parametrize(
        "source, type, interpolation, expected",
        [
            (
                "AAA@2019-09-01",
                TTextInst,
                TInterpolation.NONE,
                '"AAA"@2019-09-01 00:00:00+00',
            ),
            (
                "{AAA@2019-09-01, BBB@2019-09-02}",
                TTextSeq,
                TInterpolation.DISCRETE,
                '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00}',
            ),
            (
                "[AAA@2019-09-01, BBB@2019-09-02]",
                TTextSeq,
                TInterpolation.STEPWISE,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00]',
            ),
            (
                "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}",
                TTextSeqSet,
                TInterpolation.STEPWISE,
                '{["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00], '
                '["AAA"@2019-09-03 00:00:00+00, "AAA"@2019-09-05 00:00:00+00]}',
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tt = type(source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation
        assert str(tt) == expected

    @pytest.mark.parametrize(
        "source, type, expected",
        [
            (
                "[AAA@2019-09-01, AAA@2019-09-02, AAA@2019-09-03, BBB@2019-09-05]",
                TTextSeq,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-05 00:00:00+00]',
            ),
            (
                "{[AAA@2019-09-01, AAA@2019-09-02, AAA@2019-09-03, BBB@2019-09-05],"
                "[AAA@2019-09-07, AAA@2019-09-08, AAA@2019-09-09]}",
                TTextSeqSet,
                '{["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-05 00:00:00+00], '
                '["AAA"@2019-09-07 00:00:00+00, "AAA"@2019-09-09 00:00:00+00]}',
            ),
        ],
        ids=["Sequence", "SequenceSet"],
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tt = type(source, normalize=True)
        assert isinstance(tt, type)
        assert str(tt) == expected

    @pytest.mark.parametrize(
        "value, timestamp",
        [
            ("AAA", datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ("AAA", "2019-09-01"),
        ],
        ids=["string", "datetime"],
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tti = TTextInst(value=value, timestamp=timestamp)
        assert str(tti) == '"AAA"@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        "list, interpolation, normalize, expected",
        [
            (
                ["AAA@2019-09-01", "BBB@2019-09-03"],
                TInterpolation.DISCRETE,
                False,
                '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00}',
            ),
            (
                ["AAA@2019-09-01", "BBB@2019-09-03"],
                TInterpolation.STEPWISE,
                False,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
            (
                [TTextInst("AAA@2019-09-01"), TTextInst("BBB@2019-09-03")],
                TInterpolation.DISCRETE,
                False,
                '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00}',
            ),
            (
                [TTextInst("AAA@2019-09-01"), TTextInst("BBB@2019-09-03")],
                TInterpolation.STEPWISE,
                False,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
            (
                ["AAA@2019-09-01", TTextInst("BBB@2019-09-03")],
                TInterpolation.DISCRETE,
                False,
                '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00}',
            ),
            (
                ["AAA@2019-09-01", TTextInst("BBB@2019-09-03")],
                TInterpolation.STEPWISE,
                False,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
            (
                ["AAA@2019-09-01", "AAA@2019-09-02", "BBB@2019-09-03"],
                TInterpolation.STEPWISE,
                True,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
            (
                [
                    TTextInst("AAA@2019-09-01"),
                    TTextInst("AAA@2019-09-02"),
                    TTextInst("BBB@2019-09-03"),
                ],
                TInterpolation.STEPWISE,
                True,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
            (
                ["AAA@2019-09-01", "AAA@2019-09-02", TTextInst("BBB@2019-09-03")],
                TInterpolation.STEPWISE,
                True,
                '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-03 00:00:00+00]',
            ),
        ],
        ids=[
            "String Discrete",
            "String Stepwise",
            "TTextInst Discrete",
            "TTextInst Stepwise",
            "Mixed Discrete",
            "Mixed Stepwise",
            "String Stepwise Normalized",
            "TTextInst Stepwise Normalized",
            "Mixed Stepwise Normalized",
        ],
    )
    def test_instant_list_sequence_constructor(
        self, list, interpolation, normalize, expected
    ):
        tts = TTextSeq(
            instant_list=list,
            interpolation=interpolation,
            normalize=normalize,
            upper_inc=True,
        )
        assert str(tts) == expected
        assert tts.interpolation() == interpolation

        tts2 = TTextSeq.from_instants(
            list, interpolation=interpolation, normalize=normalize, upper_inc=True
        )
        assert str(tts2) == expected
        assert tts2.interpolation() == interpolation

    @pytest.mark.parametrize(
        "temporal",
        [tti, ttds, tts, ttss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_from_as_constructor(self, temporal):
        assert temporal == temporal.__class__(str(temporal))
        assert temporal == temporal.from_wkb(temporal.as_wkb())
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())
        assert temporal == temporal.from_mfjson(temporal.as_mfjson())

    @pytest.mark.parametrize(
        "temporal",
        [tti, ttds, tts, ttss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTTextOutputs(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, '"AAA"@2019-09-01 00:00:00+00'),
            (ttds, '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00}'),
            (tts, '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00]'),
            (
                ttss,
                '{["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00], '
                '["AAA"@2019-09-03 00:00:00+00, "AAA"@2019-09-05 00:00:00+00]}',
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, 'TTextInst("AAA"@2019-09-01 00:00:00+00)'),
            (
                ttds,
                'TTextSeq({"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00})',
            ),
            (
                tts,
                'TTextSeq(["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00])',
            ),
            (
                ttss,
                'TTextSeqSet({["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00], '
                '["AAA"@2019-09-03 00:00:00+00, "AAA"@2019-09-05 00:00:00+00]})',
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, '"AAA"@2019-09-01 00:00:00+00'),
            (ttds, '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00}'),
            (tts, '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00]'),
            (
                ttss,
                '{["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00], '
                '["AAA"@2019-09-03 00:00:00+00, "AAA"@2019-09-05 00:00:00+00]}',
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, "0123000104000000000000004141410000A01E4E71340200"),
            (
                ttds,
                "01230006020000000304000000000000004141410000A01E4E713402000400000000000000424242000000F66B85340200",
            ),
            (
                tts,
                "0123000A020000000304000000000000004141410000A01E4E713402000400000000000000424242000000F66B85340200",
            ),
            (
                ttss,
                "0123000B02000000020000000304000000000000004141410000A01E4E713402000400000000000000424242000000F66B85340200"
                "02000000030400000000000000414141000060CD899934020004000000000000004141410000207CC5C1340200",
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (
                tti,
                "{\n"
                '   "type": "MovingText",\n'
                '   "period": {\n'
                '     "begin": "2019-09-01T00:00:00+00",\n'
                '     "end": "2019-09-01T00:00:00+00",\n'
                '     "lower_inc": true,\n'
                '     "upper_inc": true\n'
                "   },\n"
                '   "values": [\n'
                '     "AAA"\n'
                "   ],\n"
                '   "datetimes": [\n'
                '     "2019-09-01T00:00:00+00"\n'
                "   ],\n"
                '   "interpolation": "None"\n'
                " }",
            ),
            (
                ttds,
                "{\n"
                '   "type": "MovingText",\n'
                '   "period": {\n'
                '     "begin": "2019-09-01T00:00:00+00",\n'
                '     "end": "2019-09-02T00:00:00+00",\n'
                '     "lower_inc": true,\n'
                '     "upper_inc": true\n'
                "   },\n"
                '   "values": [\n'
                '     "AAA",\n'
                '     "BBB"\n'
                "   ],\n"
                '   "datetimes": [\n'
                '     "2019-09-01T00:00:00+00",\n'
                '     "2019-09-02T00:00:00+00"\n'
                "   ],\n"
                '   "lower_inc": true,\n'
                '   "upper_inc": true,\n'
                '   "interpolation": "Discrete"\n'
                " }",
            ),
            (
                tts,
                "{\n"
                '   "type": "MovingText",\n'
                '   "period": {\n'
                '     "begin": "2019-09-01T00:00:00+00",\n'
                '     "end": "2019-09-02T00:00:00+00",\n'
                '     "lower_inc": true,\n'
                '     "upper_inc": true\n'
                "   },\n"
                '   "values": [\n'
                '     "AAA",\n'
                '     "BBB"\n'
                "   ],\n"
                '   "datetimes": [\n'
                '     "2019-09-01T00:00:00+00",\n'
                '     "2019-09-02T00:00:00+00"\n'
                "   ],\n"
                '   "lower_inc": true,\n'
                '   "upper_inc": true,\n'
                '   "interpolation": "Step"\n'
                " }",
            ),
            (
                ttss,
                "{\n"
                '   "type": "MovingText",\n'
                '   "period": {\n'
                '     "begin": "2019-09-01T00:00:00+00",\n'
                '     "end": "2019-09-05T00:00:00+00",\n'
                '     "lower_inc": true,\n'
                '     "upper_inc": true\n'
                "   },\n"
                '   "sequences": [\n'
                "     {\n"
                '       "values": [\n'
                '         "AAA",\n'
                '         "BBB"\n'
                "       ],\n"
                '       "datetimes": [\n'
                '         "2019-09-01T00:00:00+00",\n'
                '         "2019-09-02T00:00:00+00"\n'
                "       ],\n"
                '       "lower_inc": true,\n'
                '       "upper_inc": true\n'
                "     },\n"
                "     {\n"
                '       "values": [\n'
                '         "AAA",\n'
                '         "AAA"\n'
                "       ],\n"
                '       "datetimes": [\n'
                '         "2019-09-03T00:00:00+00",\n'
                '         "2019-09-05T00:00:00+00"\n'
                "       ],\n"
                '       "lower_inc": true,\n'
                '       "upper_inc": true\n'
                "     }\n"
                "   ],\n"
                '   "interpolation": "Step"\n'
                " }",
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_as_mfjson(self, temporal, expected):
        assert temporal.as_mfjson() == expected


class TestTTextAccessors(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, Period("[2019-09-01, 2019-09-01]")),
            (ttds, Period("[2019-09-01, 2019-09-02]")),
            (tts, Period("[2019-09-01, 2019-09-02]")),
            (ttss, Period("[2019-09-01, 2019-09-05]")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_bounding_box(self, temporal, expected):
        assert temporal.bounding_box() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TInterpolation.NONE),
            (ttds, TInterpolation.DISCRETE),
            (tts, TInterpolation.STEPWISE),
            (ttss, TInterpolation.STEPWISE),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, {"AAA"}),
            (ttds, {"AAA", "BBB"}),
            (tts, {"AAA", "BBB"}),
            (ttss, {"AAA", "BBB"}),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, ["AAA"]),
            (ttds, ["AAA", "BBB"]),
            (tts, ["AAA", "BBB"]),
            (ttss, ["AAA", "BBB", "AAA", "AAA"]),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, "AAA"), (ttds, "AAA"), (tts, "AAA"), (ttss, "AAA")],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, "AAA"), (ttds, "BBB"), (tts, "BBB"), (ttss, "AAA")],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, "AAA"), (ttds, "AAA"), (tts, "AAA"), (ttss, "AAA")],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_min_value(self, temporal, expected):
        assert temporal.min_value() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, "AAA"), (ttds, "BBB"), (tts, "BBB"), (ttss, "BBB")],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_max_value(self, temporal, expected):
        assert temporal.max_value() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, "AAA"), (ttds, "AAA"), (tts, "AAA"), (ttss, "AAA")],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, PeriodSet("{[2019-09-01, 2019-09-01]}")),
            (ttds, PeriodSet("{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}")),
            (tts, PeriodSet("{[2019-09-01, 2019-09-02]}")),
            (ttss, PeriodSet("{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, timedelta()),
            (ttds, timedelta()),
            (tts, timedelta(days=1)),
            (ttss, timedelta(days=3)),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, timedelta()),
            (ttds, timedelta(days=1)),
            (tts, timedelta(days=1)),
            (ttss, timedelta(days=4)),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, Period("[2019-09-01, 2019-09-01]")),
            (ttds, Period("[2019-09-01, 2019-09-02]")),
            (tts, Period("[2019-09-01, 2019-09-02]")),
            (ttss, Period("[2019-09-01, 2019-09-05]")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, Period("[2019-09-01, 2019-09-01]")),
            (ttds, Period("[2019-09-01, 2019-09-02]")),
            (tts, Period("[2019-09-01, 2019-09-02]")),
            (ttss, Period("[2019-09-01, 2019-09-05]")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, 1),
            (ttds, 2),
            (tts, 2),
            (ttss, 4),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, tti),
            (ttds, tti),
            (tts, tti),
            (ttss, tti),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, tti),
            (ttds, TTextInst("BBB@2019-09-02")),
            (tts, TTextInst("BBB@2019-09-02")),
            (ttss, TTextInst("AAA@2019-09-05")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, tti),
            (ttds, tti),
            (tts, tti),
            (ttss, tti),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, tti),
            (ttds, TTextInst("BBB@2019-09-02")),
            (tts, TTextInst("BBB@2019-09-02")),
            (ttss, TTextInst("BBB@2019-09-02")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        "temporal, n, expected",
        [
            (tti, 0, tti),
            (ttds, 1, TTextInst("BBB@2019-09-02")),
            (tts, 1, TTextInst("BBB@2019-09-02")),
            (ttss, 2, TTextInst("AAA@2019-09-03")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, [tti]),
            (ttds, [tti, TTextInst("BBB@2019-09-02")]),
            (tts, [tti, TTextInst("BBB@2019-09-02")]),
            (
                ttss,
                [
                    tti,
                    TTextInst("BBB@2019-09-02"),
                    TTextInst("AAA@2019-09-03"),
                    TTextInst("AAA@2019-09-05"),
                ],
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, 1),
            (ttds, 2),
            (tts, 2),
            (ttss, 4),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tts, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttds, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tts, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (ttss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        "temporal, n, expected",
        [
            (tti, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttds, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tts, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (ttss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (
                ttds,
                [
                    datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc),
                ],
            ),
            (
                tts,
                [
                    datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc),
                ],
            ),
            (
                ttss,
                [
                    datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=3, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=5, tzinfo=timezone.utc),
                ],
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_timestamps(self, temporal, expected):
        assert temporal.timestamps() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (ttds, [TTextSeq("[AAA@2019-09-01]"), TTextSeq("[BBB@2019-09-02]")]),
            (
                tts,
                [
                    TTextSeq("[AAA@2019-09-01, AAA@2019-09-02)"),
                    TTextSeq("[BBB@2019-09-02]"),
                ],
            ),
            (
                ttss,
                [
                    TTextSeq("[AAA@2019-09-01, AAA@2019-09-02)"),
                    TTextSeq("[BBB@2019-09-02]"),
                    TTextSeq("[AAA@2019-09-03, AAA@2019-09-05]"),
                ],
            ),
        ],
        ids=["Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, 1893808825), (ttds, 1223816819), (tts, 1223816819), (ttss, 2199213310)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected

    def test_value_timestamp(self):
        assert self.tti.value() == "AAA"
        assert self.tti.timestamp() == datetime(
            year=2019, month=9, day=1, tzinfo=timezone.utc
        )

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (ttds, True),
            (tts, True),
        ],
        ids=["Discrete Sequence", "Sequence"],
    )
    def test_lower_upper_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected
        assert temporal.upper_inc() == expected

    def test_sequenceset_sequence_functions(self):
        ttss1 = TTextSeqSet(
            "{[AAA@2019-09-01, BBB@2019-09-02],"
            "[AAA@2019-09-03, AAA@2019-09-05], [CCC@2019-09-06]}"
        )
        assert ttss1.num_sequences() == 3
        assert ttss1.start_sequence() == TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
        assert ttss1.end_sequence() == TTextSeq("[CCC@2019-09-06]")
        assert ttss1.sequence_n(1) == TTextSeq("[AAA@2019-09-03, AAA@2019-09-05]")
        assert ttss1.sequences() == [
            TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]"),
            TTextSeq("[AAA@2019-09-03, AAA@2019-09-05]"),
            TTextSeq("[CCC@2019-09-06]"),
        ]


class TestTTextTransformations(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (TTextInst("AAA@2019-09-01"), tti),
            (TTextSeq("{AAA@2019-09-01}"), tti),
            (TTextSeq("[AAA@2019-09-01]"), tti),
            (TTextSeqSet("{[AAA@2019-09-01]}"), tti),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_to_instant(self, temporal, expected):
        temp = temporal.to_instant()
        assert isinstance(temp, TTextInst)
        assert temp == expected

    @pytest.mark.parametrize(
        "temporal, interpolation, expected",
        [
            (
                TTextInst("AAA@2019-09-01"),
                TInterpolation.STEPWISE,
                TTextSeq("[AAA@2019-09-01]"),
            ),
            (
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}"),
                TInterpolation.DISCRETE,
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}"),
            ),
            (
                TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]"),
                TInterpolation.STEPWISE,
                TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]"),
            ),
            (
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02]}"),
                TInterpolation.STEPWISE,
                TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]"),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_to_sequence(self, temporal, interpolation, expected):
        temp = temporal.to_sequence(interpolation)
        assert isinstance(temp, TTextSeq)
        assert temp == expected

    @pytest.mark.parametrize(
        "temporal, interpolation, expected",
        [
            (
                TTextInst("AAA@2019-09-01"),
                TInterpolation.STEPWISE,
                TTextSeqSet("{[AAA@2019-09-01]}"),
            ),
            (
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}"),
                TInterpolation.STEPWISE,
                TTextSeqSet("{[AAA@2019-09-01], [BBB@2019-09-02]}"),
            ),
            (
                TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]"),
                TInterpolation.STEPWISE,
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02]}"),
            ),
            (
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02]}"),
                TInterpolation.STEPWISE,
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02]}"),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_to_sequenceset(self, temporal, interpolation, expected):
        temp = temporal.to_sequenceset(interpolation)
        assert isinstance(temp, TTextSeqSet)
        assert temp == expected

    @pytest.mark.parametrize(
        "ttext, delta, expected",
        [
            (tti, timedelta(days=4), TTextInst("AAA@2019-09-05")),
            (tti, timedelta(days=-4), TTextInst("AAA@2019-08-28")),
            (tti, timedelta(hours=2), TTextInst("AAA@2019-09-01 02:00:00")),
            (tti, timedelta(hours=-2), TTextInst("AAA@2019-08-31 22:00:00")),
            (ttds, timedelta(days=4), TTextSeq("{AAA@2019-09-05, BBB@2019-09-06}")),
            (ttds, timedelta(days=-4), TTextSeq("{AAA@2019-08-28, BBB@2019-08-29}")),
            (
                ttds,
                timedelta(hours=2),
                TTextSeq("{AAA@2019-09-01 02:00:00, BBB@2019-09-02 02:00:00}"),
            ),
            (
                ttds,
                timedelta(hours=-2),
                TTextSeq("{AAA@2019-08-31 22:00:00, BBB@2019-09-01 22:00:00}"),
            ),
            (tts, timedelta(days=4), TTextSeq("[AAA@2019-09-05, BBB@2019-09-06]")),
            (tts, timedelta(days=-4), TTextSeq("[AAA@2019-08-28, BBB@2019-08-29]")),
            (
                tts,
                timedelta(hours=2),
                TTextSeq("[AAA@2019-09-01 02:00:00, BBB@2019-09-02 02:00:00]"),
            ),
            (
                tts,
                timedelta(hours=-2),
                TTextSeq("[AAA@2019-08-31 22:00:00, BBB@2019-09-01 22:00:00]"),
            ),
            (
                ttss,
                timedelta(days=4),
                TTextSeqSet(
                    "{[AAA@2019-09-05, BBB@2019-09-06],[AAA@2019-09-07, AAA@2019-09-09]}"
                ),
            ),
            (
                ttss,
                timedelta(days=-4),
                TTextSeqSet(
                    "{[AAA@2019-08-28, BBB@2019-08-29],[AAA@2019-08-30, AAA@2019-09-01]}"
                ),
            ),
            (
                ttss,
                timedelta(hours=2),
                TTextSeqSet(
                    "{[AAA@2019-09-01 02:00:00, BBB@2019-09-02 02:00:00],"
                    "[AAA@2019-09-03 02:00:00, AAA@2019-09-05 02:00:00]}"
                ),
            ),
            (
                ttss,
                timedelta(hours=-2),
                TTextSeqSet(
                    "{[AAA@2019-08-31 22:00:00, BBB@2019-09-01 22:00:00],"
                    "[AAA@2019-09-02 22:00:00, AAA@2019-09-04 22:00:00]}"
                ),
            ),
        ],
        ids=[
            "Instant positive days",
            "Instant negative days",
            "Instant positive hours",
            "Instant negative hours",
            "Discrete Sequence positive days",
            "Discrete Sequence negative days",
            "Discrete Sequence positive hours",
            "Discrete Sequence negative hours",
            "Sequence positive days",
            "Sequence negative days",
            "Sequence positive hours",
            "Sequence negative hours",
            "Sequence Set positive days",
            "Sequence Set negative days",
            "Sequence Set positive hours",
            "Sequence Set negative hours",
        ],
    )
    def test_shift_time(self, ttext, delta, expected):
        assert ttext.shift_time(delta) == expected

    @pytest.mark.parametrize(
        "ttext, delta, expected",
        [
            (tti, timedelta(days=4), TTextInst("AAA@2019-09-01")),
            (tti, timedelta(hours=2), TTextInst("AAA@2019-09-01")),
            (ttds, timedelta(days=4), TTextSeq("{AAA@2019-09-01, BBB@2019-09-05}")),
            (
                ttds,
                timedelta(hours=2),
                TTextSeq("{AAA@2019-09-01 00:00:00, BBB@2019-09-01 02:00:00}"),
            ),
            (tts, timedelta(days=4), TTextSeq("[AAA@2019-09-01, BBB@2019-09-05]")),
            (
                tts,
                timedelta(hours=2),
                TTextSeq("[AAA@2019-09-01 00:00:00, BBB@2019-09-01 02:00:00]"),
            ),
            (
                ttss,
                timedelta(days=4),
                TTextSeqSet(
                    "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (
                ttss,
                timedelta(hours=2),
                TTextSeqSet(
                    "{[AAA@2019-09-01 00:00:00, BBB@2019-09-01 00:30:00],"
                    "[AAA@2019-09-01 01:00:00, AAA@2019-09-01 02:00:00]}"
                ),
            ),
        ],
        ids=[
            "Instant positive days",
            "Instant positive hours",
            "Discrete Sequence positive days",
            "Discrete Sequence positive hours",
            "Sequence positive days",
            "Sequence positive hours",
            "Sequence Set positive days",
            "Sequence Set positive hours",
        ],
    )
    def test_scale_time(self, ttext, delta, expected):
        assert ttext.scale_time(delta) == expected

    def test_shift_scale(self):
        assert self.ttss.shift_scale_time(
            timedelta(days=4), timedelta(hours=2)
        ) == TTextSeqSet(
            "{[AAA@2019-09-05 00:00:00, BBB@2019-09-05 00:30:00],"
            "[AAA@2019-09-05 01:00:00, AAA@2019-09-05 02:00:00]}"
        )

    @pytest.mark.parametrize(
        "tint, delta, expected",
        [
            (tti, timedelta(days=4), TTextInst("AAA@2019-09-01")),
            (tti, timedelta(hours=12), TTextInst("AAA@2019-09-01")),
            (ttds, timedelta(days=4), TTextSeq("{AAA@2019-09-01}")),
            (ttds, timedelta(hours=12), TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")),
            (tts, timedelta(days=4), TTextSeq("{AAA@2019-09-01}")),
            (
                tts,
                timedelta(hours=12),
                TTextSeq("{AAA@2019-09-01, AAA@2019-09-01 12:00:00, BBB@2019-09-02}"),
            ),
            (ttss, timedelta(days=4), TTextSeq("{AAA@2019-09-01,AAA@2019-09-05}")),
            (
                ttss,
                timedelta(hours=12),
                TTextSeq(
                    "{AAA@2019-09-01, AAA@2019-09-01 12:00:00, BBB@2019-09-02,"
                    "AAA@2019-09-03, AAA@2019-09-03 12:00:00, AAA@2019-09-04, "
                    "AAA@2019-09-04 12:00:00, AAA@2019-09-05}"
                ),
            ),
        ],
        ids=[
            "Instant days",
            "Instant hours",
            "Discrete Sequence days",
            "Discrete Sequence hours",
            "Sequence days",
            "Sequence hours",
            "Sequence Set days",
            "Sequence Set hours",
        ],
    )
    def test_temporal_sample(self, tint, delta, expected):
        assert tint.temporal_sample(delta, "2019-09-01") == expected


class TestTTextModifications(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, sequence, expected",
        [
            (
                tti,
                TTextSeq("{AAA@2019-09-03}"),
                TTextSeq("{AAA@2019-09-01, AAA@2019-09-03}"),
            ),
            (
                ttds,
                TTextSeq("{AAA@2019-09-03}"),
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02, AAA@2019-09-03}"),
            ),
            (
                tts,
                TTextSeq("[AAA@2019-09-03]"),
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02, AAA@2019-09-03]}"),
            ),
            (
                ttss,
                TTextSeq("[AAA@2019-09-06]"),
                TTextSeqSet(
                    "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05],[AAA@2019-09-06]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_insert(self, temporal, sequence, expected):
        assert temporal.insert(sequence) == expected

    @pytest.mark.parametrize(
        "temporal, instant, expected",
        [
            (tti, TTextInst("BBB@2019-09-01"), TTextInst("BBB@2019-09-01")),
            (
                ttds,
                TTextInst("BBB@2019-09-01"),
                TTextSeq("{BBB@2019-09-01, BBB@2019-09-02}"),
            ),
            (
                tts,
                TTextInst("BBB@2019-09-01"),
                TTextSeqSet("{[BBB@2019-09-01], (AAA@2019-09-01, BBB@2019-09-02]}"),
            ),
            (
                ttss,
                TTextInst("BBB@2019-09-01"),
                TTextSeqSet(
                    "{[BBB@2019-09-01], (AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_update(self, temporal, instant, expected):
        assert temporal.update(instant) == expected

    @pytest.mark.parametrize(
        "temporal, time, expected",
        [
            (tti, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), None),
            (tti, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc), tti),
            (
                ttds,
                datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TTextSeq("{BBB@2019-09-02}"),
            ),
            (
                tts,
                datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TTextSeqSet("{(AAA@2019-09-01, BBB@2019-09-02]}"),
            ),
            (
                ttss,
                datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TTextSeqSet(
                    "{(AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
        ],
        ids=[
            "Instant intersection",
            "Instant disjoint",
            "Discrete Sequence",
            "Sequence",
            "SequenceSet",
        ],
    )
    def test_delete(self, temporal, time, expected):
        assert temporal.delete(time) == expected

    @pytest.mark.parametrize(
        "temporal, instant, expected",
        [
            (
                tti,
                TTextInst("AAA@2019-09-02"),
                TTextSeq("{AAA@2019-09-01, AAA@2019-09-02}"),
            ),
            (
                ttds,
                TTextInst("AAA@2019-09-03"),
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02, AAA@2019-09-03}"),
            ),
            (
                tts,
                TTextInst("AAA@2019-09-03"),
                TTextSeq("[AAA@2019-09-01, BBB@2019-09-02, AAA@2019-09-03]"),
            ),
            (
                ttss,
                TTextInst("AAA@2019-09-06"),
                TTextSeqSet(
                    "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-06]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_append_instant(self, temporal, instant, expected):
        assert temporal.append_instant(instant) == expected

    @pytest.mark.parametrize(
        "temporal, sequence, expected",
        [
            (
                ttds,
                TTextSeq("{AAA@2019-09-03}"),
                TTextSeq("{AAA@2019-09-01, BBB@2019-09-02, AAA@2019-09-03}"),
            ),
            (
                tts,
                TTextSeq("[AAA@2019-09-03]"),
                TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02], [AAA@2019-09-03]}"),
            ),
            (
                ttss,
                TTextSeq("[AAA@2019-09-06]"),
                TTextSeqSet(
                    "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05],[AAA@2019-09-06]}"
                ),
            ),
        ],
        ids=["Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_append_sequence(self, temporal, sequence, expected):
        assert temporal.append_sequence(sequence) == expected


class TestTTextTextOperations(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )
    argument = TTextSeq("[BBB@2019-09-01, AAA@2019-09-02, AAA@2019-09-03]")

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("AAABBB@2019-09-01")),
            (ttds, TTextSeq("{AAABBB@2019-09-01, BBBAAA@2019-09-02}")),
            (tts, TTextSeq("[AAABBB@2019-09-01, BBBAAA@2019-09-02]")),
            (
                ttss,
                TTextSeqSet(
                    "{[AAABBB@2019-09-01, BBBAAA@2019-09-02],[AAAAAA@2019-09-03]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_concat_temporal(self, temporal, expected):
        assert temporal.concatenate(self.argument) == expected
        assert temporal + self.argument == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("AAABBB@2019-09-01")),
            (ttds, TTextSeq("{AAABBB@2019-09-01, BBBBBB@2019-09-02}")),
            (tts, TTextSeq("[AAABBB@2019-09-01, BBBBBB@2019-09-02]")),
            (
                ttss,
                TTextSeqSet(
                    "{[AAABBB@2019-09-01, BBBBBB@2019-09-02],[AAABBB@2019-09-03, AAABBB@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_concat_text(self, temporal, expected):
        assert temporal.concatenate("BBB") == expected
        assert (temporal + "BBB") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("BBBAAA@2019-09-01")),
            (ttds, TTextSeq("{BBBAAA@2019-09-01, BBBBBB@2019-09-02}")),
            (tts, TTextSeq("[BBBAAA@2019-09-01, BBBBBB@2019-09-02]")),
            (
                ttss,
                TTextSeqSet(
                    "{[BBBAAA@2019-09-01, BBBBBB@2019-09-02],[BBBAAA@2019-09-03, BBBAAA@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_radd_text(self, temporal, expected):
        assert ("BBB" + temporal) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("aaa@2019-09-01")),
            (ttds, TTextSeq("{aaa@2019-09-01, bbb@2019-09-02}")),
            (tts, TTextSeq("[aaa@2019-09-01, bbb@2019-09-02]")),
            (
                ttss,
                TTextSeqSet(
                    "{[aaa@2019-09-01, bbb@2019-09-02],[aaa@2019-09-03, aaa@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_lower(self, temporal, expected):
        assert temporal.lower() == expected

    @pytest.mark.parametrize(
        "temporal",
        [tti, ttds, tts, ttss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_upper(self, temporal):
        assert temporal.upper() == temporal


class TestTTextRestrictors(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    timestamp = datetime(2019, 9, 1)
    timestamp_set = TimestampSet("{2019-09-01, 2019-09-03}")
    period = Period("[2019-09-01, 2019-09-02]")
    period_set = PeriodSet("{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}")

    @pytest.mark.parametrize(
        "temporal, restrictor, expected",
        [
            (tti, timestamp, TTextInst("AAA@2019-09-01")),
            (tti, timestamp_set, TTextInst("AAA@2019-09-01")),
            (tti, period, TTextInst("AAA@2019-09-01")),
            (tti, period_set, TTextInst("AAA@2019-09-01")),
            (tti, "AAA", TTextInst("AAA@2019-09-01")),
            (tti, "BBB", None),
            (tti, ["AAA", "BBB"], tti),
            (ttds, timestamp, TTextSeq("{AAA@2019-09-01}")),
            (ttds, timestamp_set, TTextSeq("{AAA@2019-09-01}")),
            (ttds, period, TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")),
            (ttds, period_set, TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")),
            (ttds, "AAA", TTextSeq("{AAA@2019-09-01}")),
            (ttds, "BBB", TTextSeq("{BBB@2019-09-02}")),
            (ttds, ["AAA", "BBB"], ttds),
            (tts, timestamp, TTextSeq("[AAA@2019-09-01]")),
            (tts, timestamp_set, TTextSeq("{AAA@2019-09-01}")),
            (tts, period, TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")),
            (tts, period_set, TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")),
            (tts, "AAA", TTextSeq("[AAA@2019-09-01, AAA@2019-09-02)")),
            (tts, "BBB", TTextSeq("[BBB@2019-09-02]")),
            (tts, ["AAA", "BBB"], tts),
            (ttss, timestamp, TTextSeqSet("[AAA@2019-09-01]")),
            (ttss, timestamp_set, TTextSeq("{AAA@2019-09-01, AAA@2019-09-03}")),
            (ttss, period, TTextSeqSet("{[AAA@2019-09-01, BBB@2019-09-02]}")),
            (
                ttss,
                period_set,
                TTextSeqSet(
                    "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (
                ttss,
                "AAA",
                TTextSeqSet(
                    "{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (ttss, "BBB", TTextSeqSet("{[BBB@2019-09-02]}")),
            (ttss, ["AAA", "BBB"], ttss),
        ],
        ids=[
            "Instant-Timestamp",
            "Instant-TimestampSet",
            "Instant-Period",
            "Instant-PeriodSet",
            "Instant-AAA",
            "Instant-BBB",
            "Instant-[AAA,BBB]",
            "Discrete Sequence-Timestamp",
            "Discrete Sequence-TimestampSet",
            "Discrete Sequence-Period",
            "Discrete Sequence-PeriodSet",
            "Discrete Sequence-AAA",
            "Discrete Sequence-BBB",
            "Discrete Sequence-[AAA,BBB]",
            "Sequence-Timestamp",
            "Sequence-TimestampSet",
            "Sequence-Period",
            "Sequence-PeriodSet",
            "Sequence-AAA",
            "Sequence-BBB",
            "Sequence-[AAA,BBB]",
            "SequenceSet-Timestamp",
            "SequenceSet-TimestampSet",
            "SequenceSet-Period",
            "SequenceSet-PeriodSet",
            "SequenceSet-AAA",
            "SequenceSet-BBB",
            "SequenceSet-[AAA,BBB]",
        ],
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("AAA@2019-09-01")),
            (ttds, TTextSeq("{BBB@2019-09-02}")),
            (tts, TTextSeq("{[BBB@2019-09-02]}")),
            (ttss, TTextSeqSet("{[BBB@2019-09-02]}")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_at_max(self, temporal, expected):
        assert temporal.at_max() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TTextInst("AAA@2019-09-01")),
            (ttds, TTextSeq("{AAA@2019-09-01}")),
            (tts, TTextSeq("{[AAA@2019-09-01, AAA@2019-09-02)}")),
            (
                ttss,
                TTextSeqSet(
                    "{[AAA@2019-09-01, AAA@2019-09-02), [AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_at_min(self, temporal, expected):
        assert temporal.at_min() == expected

    @pytest.mark.parametrize(
        "temporal, restrictor, expected",
        [
            (tti, timestamp, None),
            (tti, timestamp_set, None),
            (tti, period, None),
            (tti, period_set, None),
            (tti, "AAA", None),
            (tti, "BBB", TTextInst("AAA@2019-09-01")),
            (tti, ["AAA", "BBB"], None),
            (ttds, timestamp, TTextSeq("{BBB@2019-09-02}")),
            (ttds, timestamp_set, TTextSeq("{BBB@2019-09-02}")),
            (ttds, period, None),
            (ttds, period_set, None),
            (ttds, "AAA", TTextSeq("{BBB@2019-09-02}")),
            (ttds, "BBB", TTextSeq("{AAA@2019-09-01}")),
            (ttds, ["AAA", "BBB"], None),
            (tts, timestamp, TTextSeqSet("{(AAA@2019-09-01, BBB@2019-09-02]}")),
            (tts, timestamp_set, TTextSeqSet("{(AAA@2019-09-01, BBB@2019-09-02]}")),
            (tts, period, None),
            (tts, period_set, None),
            (tts, "AAA", TTextSeqSet("{[BBB@2019-09-02]}")),
            (tts, "BBB", TTextSeqSet("{[AAA@2019-09-01, AAA@2019-09-02)}")),
            (tts, ["AAA", "BBB"], None),
            (
                ttss,
                timestamp,
                TTextSeqSet(
                    "{(AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (
                ttss,
                timestamp_set,
                TTextSeqSet(
                    "{(AAA@2019-09-01, BBB@2019-09-02],(AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (ttss, period, TTextSeqSet("{[AAA@2019-09-03, AAA@2019-09-05]}")),
            (ttss, period_set, None),
            (ttss, "AAA", TTextSeqSet("{[BBB@2019-09-02]}")),
            (
                ttss,
                "BBB",
                TTextSeqSet(
                    "{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
            (ttss, ["AAA", "BBB"], None),
        ],
        ids=[
            "Instant-Timestamp",
            "Instant-TimestampSet",
            "Instant-Period",
            "Instant-PeriodSet",
            "Instant-AAA",
            "Instant-BBB",
            "Instant-[AAA,BBB]",
            "Discrete Sequence-Timestamp",
            "Discrete Sequence-TimestampSet",
            "Discrete Sequence-Period",
            "Discrete Sequence-PeriodSet",
            "Discrete Sequence-AAA",
            "Discrete Sequence-BBB",
            "Discrete Sequence-[AAA,BBB]",
            "Sequence-Timestamp",
            "Sequence-TimestampSet",
            "Sequence-Period",
            "Sequence-PeriodSet",
            "Sequence-AAA",
            "Sequence-BBB",
            "Sequence-[AAA,BBB]",
            "SequenceSet-Timestamp",
            "SequenceSet-TimestampSet",
            "SequenceSet-Period",
            "SequenceSet-PeriodSet",
            "SequenceSet-AAA",
            "SequenceSet-BBB",
            "SequenceSet-[AAA,BBB]",
        ],
    )
    def test_minus(self, temporal, restrictor, expected):
        if expected is None:
            assert temporal.minus(restrictor) is None
        else:
            assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, None),
            (ttds, TTextSeq("{BBB@2019-09-02}")),
            (tts, TTextSeq("{[BBB@2019-09-02]}")),
            (ttss, TTextSeqSet("{[BBB@2019-09-02]}")),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, None),
            (ttds, TTextSeq("{AAA@2019-09-01}")),
            (tts, TTextSeq("{[AAA@2019-09-01, AAA@2019-09-02)}")),
            (
                ttss,
                TTextSeqSet(
                    "{[AAA@2019-09-01, AAA@2019-09-02), [AAA@2019-09-03, AAA@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_minus_max(self, temporal, expected):
        assert temporal.minus_max() == expected

    @pytest.mark.parametrize(
        "temporal, restrictor",
        [
            (tti, timestamp),
            (tti, timestamp_set),
            (tti, period),
            (tti, period_set),
            (tti, "AAA"),
            (tti, "BBB"),
            (tti, ["AAA", "BBB"]),
            (ttds, timestamp),
            (ttds, timestamp_set),
            (ttds, period),
            (ttds, period_set),
            (ttds, "AAA"),
            (ttds, "BBB"),
            (ttds, ["AAA", "BBB"]),
            (tts, timestamp),
            (tts, timestamp_set),
            (tts, period),
            (tts, period_set),
            (tts, "AAA"),
            (tts, "BBB"),
            (tts, ["AAA", "BBB"]),
            (ttss, timestamp),
            (ttss, timestamp_set),
            (ttss, period),
            (ttss, period_set),
            (ttss, "AAA"),
            (ttss, "BBB"),
            (ttss, ["AAA", "BBB"]),
        ],
        ids=[
            "Instant-Timestamp",
            "Instant-TimestampSet",
            "Instant-Period",
            "Instant-PeriodSet",
            "Instant-AAA",
            "Instant-BBB",
            "Instant-[AAA,BBB]",
            "Discrete Sequence-Timestamp",
            "Discrete Sequence-TimestampSet",
            "Discrete Sequence-Period",
            "Discrete Sequence-PeriodSet",
            "Discrete Sequence-AAA",
            "Discrete Sequence-BBB",
            "Discrete Sequence-[AAA,BBB]",
            "Sequence-Timestamp",
            "Sequence-TimestampSet",
            "Sequence-Period",
            "Sequence-PeriodSet",
            "Sequence-AAA",
            "Sequence-BBB",
            "Sequence-[AAA,BBB]",
            "SequenceSet-Timestamp",
            "SequenceSet-TimestampSet",
            "SequenceSet-Period",
            "SequenceSet-PeriodSet",
            "SequenceSet-AAA",
            "SequenceSet-BBB",
            "SequenceSet-[AAA,BBB]",
        ],
    )
    def test_at_minus(self, temporal, restrictor):
        assert (
            TText.merge(temporal.at(restrictor), temporal.minus(restrictor)) == temporal
        )

    @pytest.mark.parametrize(
        "temporal",
        [tti, ttds, tts, ttss],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_at_minus_min_max(self, temporal):
        assert TText.merge(temporal.at_min(), temporal.minus_min()) == temporal
        assert TText.merge(temporal.at_max(), temporal.minus_max()) == temporal


class TestTTextTopologicalFunctions(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02], [AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-09-02"), False),
            (tti, TTextSeq("(AAA@2019-09-01, BBB@2019-09-02]"), True),
            (ttds, TTextInst("AAA@2019-09-03"), False),
            (ttds, TTextSeq("(AAA@2019-09-02, BBB@2019-09-03]"), True),
            (tts, TTextInst("AAA@2019-09-03"), False),
            (tts, TTextSeq("(AAA@2019-09-02, BBB@2019-09-03]"), True),
            (ttss, TTextInst("AAA@2019-09-08"), False),
            (ttss, TTextSeq("(AAA@2019-09-05, BBB@2019-09-06]"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_is_temporally_adjacent(self, temporal, argument, expected):
        assert temporal.is_adjacent(argument) == expected
        assert temporal.is_temporally_adjacent(argument) == expected

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-09-02"), False),
            (tti, TTextSeq("[AAA@2019-09-01,BBB@2019-09-02]"), True),
            (ttds, TTextInst("AAA@2019-09-02"), False),
            (ttds, TTextSeq("[AAA@2019-09-01,BBB@2019-09-02]"), True),
            (tts, TTextInst("AAA@2019-09-02"), False),
            (tts, TTextSeq("[AAA@2019-09-01,BBB@2019-09-05]"), True),
            (ttss, TTextInst("AAA@2019-09-02"), False),
            (ttss, TTextSeq("[AAA@2019-09-01,BBB@2019-09-05]"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_is_temporally_contained_in_contains(self, temporal, argument, expected):
        assert temporal.is_contained_in(argument) == expected
        assert argument.contains(temporal) == expected
        assert temporal.is_temporally_contained_in(argument) == expected
        assert argument.temporally_contains(temporal) == expected

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-09-02"), False),
            (tti, TTextSeq("[AAA@2019-09-01]"), True),
            (ttds, TTextInst("CCC@2019-09-03"), False),
            (ttds, TTextSeq("[AAA@2019-09-01,BBB@2019-09-02]"), True),
            (tts, TTextInst("CCC@2019-09-03"), False),
            (tts, TTextSeq("[AAA@2019-09-01,BBB@2019-09-02]"), True),
            (ttss, TTextInst("CCC@2019-09-06"), False),
            (ttss, TTextSeq("[AAA@2019-09-01,BBB@2019-09-05]"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_overlaps_is_same(self, temporal, argument, expected):
        assert temporal.overlaps(argument) == expected
        assert temporal.is_same(argument) == expected


class TestTTextPositionFunctions(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02], [AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-09-01"), False),
            (tti, TTextInst("AAA@2019-10-01"), True),
            (ttds, TTextInst("AAA@2019-09-01"), False),
            (ttds, TTextInst("AAA@2019-10-01"), True),
            (tts, TTextInst("AAA@2019-09-01"), False),
            (tts, TTextInst("AAA@2019-10-01"), True),
            (ttss, TTextInst("AAA@2019-09-01"), False),
            (ttss, TTextInst("AAA@2019-10-01"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_is_before_after(self, temporal, argument, expected):
        assert temporal.is_before(argument) == expected
        assert argument.is_after(temporal) == expected

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-08-01"), False),
            (tti, TTextInst("AAA@2019-10-01"), True),
            (ttds, TTextInst("AAA@2019-08-01"), False),
            (ttds, TTextInst("AAA@2019-10-01"), True),
            (tts, TTextInst("AAA@2019-08-01"), False),
            (tts, TTextInst("AAA@2019-10-01"), True),
            (ttss, TTextInst("AAA@2019-08-01"), False),
            (ttss, TTextInst("AAA@2019-10-01"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_is_over_or_before(self, temporal, argument, expected):
        assert temporal.is_over_or_before(argument) == expected

    @pytest.mark.parametrize(
        "temporal, argument, expected",
        [
            (tti, TTextInst("AAA@2019-10-01"), False),
            (tti, TTextInst("AAA@2019-09-01"), True),
            (ttds, TTextInst("AAA@2019-10-01"), False),
            (ttds, TTextInst("AAA@2019-09-01"), True),
            (tts, TTextInst("AAA@2019-10-01"), False),
            (tts, TTextInst("AAA@2019-09-01"), True),
            (ttss, TTextInst("AAA@2019-10-01"), False),
            (ttss, TTextInst("AAA@2019-09-01"), True),
        ],
        ids=[
            "Instant False",
            "Instant True",
            "Discrete Sequence False",
            "Discrete Sequence True",
            "Sequence False",
            "Sequence True",
            "Sequence Set False",
            "Sequence Set True",
        ],
    )
    def test_is_over_or_after(self, temporal, argument, expected):
        assert temporal.is_over_or_after(argument) == expected


class TestTTextComparisons(TestTText):
    tt = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    other = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    def test_eq(self):
        _ = self.tt == self.other

    def test_ne(self):
        _ = self.tt != self.other

    def test_lt(self):
        _ = self.tt < self.other

    def test_le(self):
        _ = self.tt <= self.other

    def test_gt(self):
        _ = self.tt > self.other

    def test_ge(self):
        _ = self.tt >= self.other


class TestTTextEverAlwaysComparisons(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, True), (ttds, False), (tts, False), (ttss, False)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_always_AAA(self, temporal, expected):
        assert temporal.always_equal("AAA") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, False), (ttds, False), (tts, False), (ttss, False)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_always_BBB(self, temporal, expected):
        assert temporal.always_equal("BBB") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, True), (ttds, True), (tts, True), (ttss, True)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_ever_AAA(self, temporal, expected):
        assert temporal.ever_equal("AAA") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, False), (ttds, True), (tts, True), (ttss, True)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_ever_BBB(self, temporal, expected):
        assert temporal.ever_equal("BBB") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, False), (ttds, False), (tts, False), (ttss, False)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_never_AAA(self, temporal, expected):
        assert temporal.never_equal("AAA") == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [(tti, True), (ttds, False), (tts, False), (ttss, False)],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_never_BBB(self, temporal, expected):
        assert temporal.never_equal("BBB") == expected


class TestTTextTemporalComparisons(TestTText):
    tti = TTextInst("AAA@2019-09-01")
    ttds = TTextSeq("{AAA@2019-09-01, BBB@2019-09-02}")
    tts = TTextSeq("[AAA@2019-09-01, BBB@2019-09-02]")
    ttss = TTextSeqSet(
        "{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}"
    )
    argument = TTextSeq("[BBB@2019-09-01, AAA@2019-09-02, AAA@2019-09-03]")

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TBoolInst("False@2019-09-01")),
            (ttds, TBoolSeq("{False@2019-09-01, False@2019-09-02}")),
            (tts, TBoolSeq("[False@2019-09-01, False@2019-09-02]")),
            (
                ttss,
                TBoolSeqSet("{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}"),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.argument) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TBoolInst("True@2019-09-01")),
            (ttds, TBoolSeq("{True@2019-09-01, False@2019-09-02}")),
            (tts, TBoolSeq("[True@2019-09-01, False@2019-09-02]")),
            (
                ttss,
                TBoolSeqSet(
                    "{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_equal_int(self, temporal, expected):
        assert temporal.temporal_equal("AAA") == expected

        assert temporal.temporal_equal("BBB") == ~expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TBoolInst("True@2019-09-01")),
            (ttds, TBoolSeq("{True@2019-09-01, True@2019-09-02}")),
            (tts, TBoolSeq("[True@2019-09-01, True@2019-09-02]")),
            (
                ttss,
                TBoolSeqSet("{[True@2019-09-01, True@2019-09-02],[False@2019-09-03]}"),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.argument) == expected

    @pytest.mark.parametrize(
        "temporal, expected",
        [
            (tti, TBoolInst("False@2019-09-01")),
            (ttds, TBoolSeq("{False@2019-09-01, True@2019-09-02}")),
            (tts, TBoolSeq("[False@2019-09-01, True@2019-09-02]")),
            (
                ttss,
                TBoolSeqSet(
                    "{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}"
                ),
            ),
        ],
        ids=["Instant", "Discrete Sequence", "Sequence", "SequenceSet"],
    )
    def test_temporal_not_equal_int(self, temporal, expected):
        assert temporal.temporal_not_equal("AAA") == expected
        assert temporal.temporal_not_equal("BBB") == ~expected
