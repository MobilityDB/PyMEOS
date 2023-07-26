from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, \
    TIntInst, TIntSeq, TIntSeqSet, TInterpolation, \
    TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTBool(TestPyMEOS):
    pass


class TestTBoolConstructors(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TIntInst('1@2019-09-01'), TBoolInst, TInterpolation.NONE),
            (TIntSeq('{1@2019-09-01, 0@2019-09-02}'), TBoolSeq, TInterpolation.DISCRETE),
            (TIntSeq('[1@2019-09-01, 0@2019-09-02]'), TBoolSeq, TInterpolation.STEPWISE),
            (TIntSeqSet('{[1@2019-09-01, 0@2019-09-02],[1@2019-09-03, 1@2019-09-05]}'),
             TBoolSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tb = TBool.from_base_temporal(True, source)
        assert isinstance(tb, type)
        assert tb.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TBoolInst, TInterpolation.NONE),
            (TimestampSet('{2019-09-01, 2019-09-02}'), TBoolSeq, TInterpolation.DISCRETE),
            (Period('[2019-09-01, 2019-09-02]'), TBoolSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'), TBoolSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tb = TBool.from_base_time(True, source)
        assert isinstance(tb, type)
        assert tb.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('True@2019-09-01', TBoolInst, TInterpolation.NONE, 't@2019-09-01 00:00:00+00'),
            ('{True@2019-09-01, False@2019-09-02}', TBoolSeq, TInterpolation.DISCRETE,
             '{t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00}'),
            ('[True@2019-09-01, False@2019-09-02]', TBoolSeq, TInterpolation.STEPWISE,
             '[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00]'),
            ('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}', TBoolSeqSet,
             TInterpolation.STEPWISE, '{[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00], '
                                      '[t@2019-09-03 00:00:00+00, t@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tb = type(source)
        assert isinstance(tb, type)
        assert tb.interpolation() == interpolation
        assert str(tb) == expected

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[True@2019-09-01, True@2019-09-02, True@2019-09-03, False@2019-09-05]', TBoolSeq,
             '[t@2019-09-01 00:00:00+00, f@2019-09-05 00:00:00+00]'),
            ('{[True@2019-09-01, True@2019-09-02, True@2019-09-03, False@2019-09-05],'
             '[True@2019-09-07, True@2019-09-08, True@2019-09-09]}', TBoolSeqSet,
             '{[t@2019-09-01 00:00:00+00, f@2019-09-05 00:00:00+00], '
             '[t@2019-09-07 00:00:00+00, t@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tb = type(source, normalize=True)
        assert isinstance(tb, type)
        assert str(tb) == expected

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
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tbi = TBoolInst(value=value, timestamp=timestamp)
        assert str(tbi) == 't@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['True@2019-09-01', 'False@2019-09-03'], TInterpolation.DISCRETE, False,
             '{t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00}'),
            (['True@2019-09-01', 'False@2019-09-03'], TInterpolation.STEPWISE, False,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),
            ([TBoolInst('True@2019-09-01'), TBoolInst('False@2019-09-03')], TInterpolation.DISCRETE, False,
             '{t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00}'),
            ([TBoolInst('True@2019-09-01'), TBoolInst('False@2019-09-03')], TInterpolation.STEPWISE, False,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),
            (['True@2019-09-01', TBoolInst('False@2019-09-03')], TInterpolation.DISCRETE, False,
             '{t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00}'),
            (['True@2019-09-01', TBoolInst('False@2019-09-03')], TInterpolation.STEPWISE, False,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),

            (['True@2019-09-01', 'True@2019-09-02', 'False@2019-09-03'], TInterpolation.STEPWISE, True,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),
            ([TBoolInst('True@2019-09-01'), TBoolInst('True@2019-09-02'), TBoolInst('False@2019-09-03')],
             TInterpolation.STEPWISE, True,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),
            (['True@2019-09-01', 'True@2019-09-02', TBoolInst('False@2019-09-03')], TInterpolation.STEPWISE, True,
             '[t@2019-09-01 00:00:00+00, f@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Stepwise', 'TBoolInst Discrete', 'TBoolInst Stepwise', 'Mixed Discrete',
             'Mixed Stepwise', 'String Stepwise Normalized', 'TBoolInst Stepwise Normalized',
             'Mixed Stepwise Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tbs = TBoolSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tbs) == expected
        assert tbs.interpolation() == interpolation

        tbs2 = TBoolSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tbs2) == expected
        assert tbs2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_as_constructor(self, temporal):
        # assert temporal == temporal.from_wkt(temporal.as_wkt())
        assert temporal == temporal.from_wkb(temporal.as_wkb())
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())
        assert temporal == temporal.from_mfjson(temporal.as_mfjson())

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTBoolOutputs(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 't@2019-09-01 00:00:00+00'),
            (tbds, '{t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00}'),
            (tbs, '[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00]'),
            (tbss, '{[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00], '
                   '[t@2019-09-03 00:00:00+00, t@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 'TBoolInst(t@2019-09-01 00:00:00+00)'),
            (tbds, 'TBoolSeq({t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00})'),
            (tbs, 'TBoolSeq([t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00])'),
            (tbss, 'TBoolSeqSet({[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00], '
                   '[t@2019-09-03 00:00:00+00, t@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 't@2019-09-01 00:00:00+00'),
            (tbds, '{t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00}'),
            (tbs, '[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00]'),
            (tbss, '{[t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00], '
                   '[t@2019-09-03 00:00:00+00, t@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, '011400010100A01E4E71340200'),
            (tbds, '0114000602000000030100A01E4E71340200000000F66B85340200'),
            (tbs, '0114000A02000000030100A01E4E71340200000000F66B85340200'),
            (tbss, '0114000B0200000002000000030100A01E4E71340200000000F'
                   '66B853402000200000003010060CD89993402000100207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, '{\n'
                  '   "type": "MovingBoolean",\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-01T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     true\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00"\n'
                  '   ],\n'
                  '   "interpolation": "None"\n'
                  ' }'),
            (tbds, '{\n'
                   '   "type": "MovingBoolean",\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-02T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "values": [\n'
                   '     true,\n'
                   '     false\n'
                   '   ],\n'
                   '   "datetimes": [\n'
                   '     "2019-09-01T00:00:00+00",\n'
                   '     "2019-09-02T00:00:00+00"\n'
                   '   ],\n'
                   '   "lower_inc": true,\n'
                   '   "upper_inc": true,\n'
                   '   "interpolation": "Discrete"\n'
                   ' }'),
            (tbs, '{\n'
                  '   "type": "MovingBoolean",\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-02T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     true,\n'
                  '     false\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00",\n'
                  '     "2019-09-02T00:00:00+00"\n'
                  '   ],\n'
                  '   "lower_inc": true,\n'
                  '   "upper_inc": true,\n'
                  '   "interpolation": "Step"\n'
                  ' }'),
            (tbss, '{\n'
                   '   "type": "MovingBoolean",\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-05T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "sequences": [\n'
                   '     {\n'
                   '       "values": [\n'
                   '         true,\n'
                   '         false\n'
                   '       ],\n'
                   '       "datetimes": [\n'
                   '         "2019-09-01T00:00:00+00",\n'
                   '         "2019-09-02T00:00:00+00"\n'
                   '       ],\n'
                   '       "lower_inc": true,\n'
                   '       "upper_inc": true\n'
                   '     },\n'
                   '     {\n'
                   '       "values": [\n'
                   '         true,\n'
                   '         true\n'
                   '       ],\n'
                   '       "datetimes": [\n'
                   '         "2019-09-03T00:00:00+00",\n'
                   '         "2019-09-05T00:00:00+00"\n'
                   '       ],\n'
                   '       "lower_inc": true,\n'
                   '       "upper_inc": true\n'
                   '     }\n'
                   '   ],\n'
                   '   "interpolation": "Step"\n'
                   ' }')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_mfjson(self, temporal, expected):
        assert temporal.as_mfjson() == expected


class TestTBoolAccessors(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TInterpolation.NONE),
            (tbds, TInterpolation.DISCRETE),
            (tbs, TInterpolation.STEPWISE),
            (tbss, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, {True}),
            (tbds, {True, False}),
            (tbs, {True, False}),
            (tbss, {True, False})
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, [True]),
            (tbds, [True, False]),
            (tbs, [True, False]),
            (tbss, [True, False, True, True])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, False),
            (tbs, False),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_value(self, temporal, expected):
        assert temporal.min_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_value(self, temporal, expected):
        assert temporal.max_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tbds, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
            (tbs, PeriodSet('{[2019-09-01, 2019-09-02]}')),
            (tbss, PeriodSet('{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, timedelta()),
            (tbds, timedelta()),
            (tbs, timedelta(days=1)),
            (tbss, timedelta(days=3)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, timedelta()),
            (tbds, timedelta(days=1)),
            (tbs, timedelta(days=1)),
            (tbss, timedelta(days=4)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, Period('[2019-09-01, 2019-09-01]')),
            (tbds, Period('[2019-09-01, 2019-09-02]')),
            (tbs, Period('[2019-09-01, 2019-09-02]')),
            (tbss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, Period('[2019-09-01, 2019-09-01]')),
            (tbds, Period('[2019-09-01, 2019-09-02]')),
            (tbs, Period('[2019-09-01, 2019-09-02]')),
            (tbss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 1),
            (tbds, 2),
            (tbs, 2),
            (tbss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, tbi),
            (tbds, tbi),
            (tbs, tbi),
            (tbss, tbi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, tbi),
            (tbds, TBoolInst('False@2019-09-02')),
            (tbs, TBoolInst('False@2019-09-02')),
            (tbss, TBoolInst('True@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, tbi),
            (tbds, tbi),
            (tbs, tbi),
            (tbss, tbi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, tbi),
            (tbds, TBoolInst('False@2019-09-02')),
            (tbs, TBoolInst('False@2019-09-02')),
            (tbss, TBoolInst('False@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tbi, 0, tbi),
            (tbds, 1, TBoolInst('False@2019-09-02')),
            (tbs, 1, TBoolInst('False@2019-09-02')),
            (tbss, 2, TBoolInst('True@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, [tbi]),
            (tbds, [tbi, TBoolInst('False@2019-09-02')]),
            (tbs, [tbi, TBoolInst('False@2019-09-02')]),
            (tbss, [tbi, TBoolInst('False@2019-09-02'), TBoolInst('True@2019-09-03'), TBoolInst('True@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 1),
            (tbds, 2),
            (tbs, 2),
            (tbss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbs, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbds, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbs, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tbi, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tbds, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbs, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tbss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (tbds, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tbs, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                   datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tbss, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=3, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamps(self, temporal, expected):
        assert temporal.timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbds, [TBoolSeq('[t@2019-09-01]'), TBoolSeq('[f@2019-09-02]')]),
            (tbs, [TBoolSeq('[t@2019-09-01, t@2019-09-02)'),
                   TBoolSeq('[f@2019-09-02]')]),
            (tbss,
             [TBoolSeq('[t@2019-09-01, t@2019-09-02)'),
              TBoolSeq('[f@2019-09-02]'),
              TBoolSeq('[t@2019-09-03, t@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbds, True),
            (tbs, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_upper_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected
        assert temporal.upper_inc() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 440045287),
            (tbds, 2385901957),
            (tbs, 2385901957),
            (tbss, 1543175996)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected


class TestTBoolTransformations(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TBoolInst('True@2019-09-01'), tbi),
            (TBoolSeq('{True@2019-09-01}'), tbi),
            (TBoolSeq('[True@2019-09-01]'), tbi),
            (TBoolSeqSet('{[True@2019-09-01]}'), tbi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_instant(self, temporal, expected):
        temp = temporal.to_instant()
        assert isinstance(temp, TBoolInst)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TBoolInst('True@2019-09-01'), 
                TBoolSeq('[True@2019-09-01]')),
            (TBoolSeq('{True@2019-09-01, False@2019-09-02}'),
                TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (TBoolSeq('[True@2019-09-01, False@2019-09-02]'),
                TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}'),
                TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequence(self, temporal, expected):
        temp = temporal.to_sequence()
        assert isinstance(temp, TBoolSeq)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TBoolInst('True@2019-09-01'), 
                TBoolSeqSet('{[True@2019-09-01]}')),
            (TBoolSeq('{True@2019-09-01, False@2019-09-02}'),
                TBoolSeqSet('{[True@2019-09-01], [False@2019-09-02]}')),
            (TBoolSeq('[True@2019-09-01, False@2019-09-02]'),
                TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}')),
            (TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}'),
                TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequenceset(self, temporal, expected):
        temp = temporal.to_sequenceset()
        assert isinstance(temp, TBoolSeqSet)
        assert temp == expected

    @pytest.mark.parametrize(
        'tbool, delta, expected',
        [(tbi, timedelta(days=4), TBoolInst('True@2019-09-05')),
         (tbi, timedelta(days=-4), TBoolInst('True@2019-08-28')),
         (tbi, timedelta(hours=2), TBoolInst('True@2019-09-01 02:00:00')),
         (tbi, timedelta(hours=-2), TBoolInst('True@2019-08-31 22:00:00')), 
         (tbds, timedelta(days=4), TBoolSeq('{True@2019-09-05, False@2019-09-06}')),
         (tbds, timedelta(days=-4), TBoolSeq('{True@2019-08-28, False@2019-08-29}')),
         (tbds, timedelta(hours=2), TBoolSeq('{True@2019-09-01 02:00:00, False@2019-09-02 02:00:00}')),
         (tbds, timedelta(hours=-2), TBoolSeq('{True@2019-08-31 22:00:00, False@2019-09-01 22:00:00}')),
         (tbs, timedelta(days=4), TBoolSeq('[True@2019-09-05, False@2019-09-06]')),
         (tbs, timedelta(days=-4), TBoolSeq('[True@2019-08-28, False@2019-08-29]')),
         (tbs, timedelta(hours=2), TBoolSeq('[True@2019-09-01 02:00:00, False@2019-09-02 02:00:00]')),
         (tbs, timedelta(hours=-2), TBoolSeq('[True@2019-08-31 22:00:00, False@2019-09-01 22:00:00]')),
         (tbss, timedelta(days=4),
             TBoolSeqSet('{[True@2019-09-05, False@2019-09-06],[True@2019-09-07, True@2019-09-09]}')),
         (tbss, timedelta(days=-4),
             TBoolSeqSet('{[True@2019-08-28, False@2019-08-29],[True@2019-08-30, True@2019-09-01]}')),
         (tbss, timedelta(hours=2),
             TBoolSeqSet('{[True@2019-09-01 02:00:00, False@2019-09-02 02:00:00],'
                         '[True@2019-09-03 02:00:00, True@2019-09-05 02:00:00]}')),
         (tbss, timedelta(hours=-2),
             TBoolSeqSet('{[True@2019-08-31 22:00:00, False@2019-09-01 22:00:00],'
             '[True@2019-09-02 22:00:00, True@2019-09-04 22:00:00]}')),
         ],
        ids=['Instant positive days', 'Instant negative days',
             'Instant positive hours', 'Instant negative hours',
             'Discrete Sequence positive days', 'Discrete Sequence negative days', 
             'Discrete Sequence positive hours', 'Discrete Sequence negative hours',
             'Sequence positive days', 'Sequence negative days', 
             'Sequence positive hours', 'Sequence negative hours',
             'Sequence Set positive days', 'Sequence Set negative days', 
             'Sequence Set positive hours', 'Sequence Set negative hours']
    )
    def test_shift(self, tbool, delta, expected):
        assert tbool.shift(delta) == expected

    @pytest.mark.parametrize(
        'tbool, delta, expected',
        [(tbi, timedelta(days=4), TBoolInst('True@2019-09-01')),
         (tbi, timedelta(hours=2), TBoolInst('True@2019-09-01')),
         (tbds, timedelta(days=4), TBoolSeq('{True@2019-09-01, False@2019-09-05}')),
         (tbds, timedelta(hours=2), TBoolSeq('{True@2019-09-01 00:00:00, False@2019-09-01 02:00:00}')),
         (tbs, timedelta(days=4), TBoolSeq('[True@2019-09-01, False@2019-09-05]')),
         (tbs, timedelta(hours=2), TBoolSeq('[True@2019-09-01 00:00:00, False@2019-09-01 02:00:00]')),
         (tbss, timedelta(days=4),
             TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
         (tbss, timedelta(hours=2),
             TBoolSeqSet('{[True@2019-09-01 00:00:00, False@2019-09-01 00:30:00],'
                         '[True@2019-09-01 01:00:00, True@2019-09-01 02:00:00]}')),
        ],
        ids=['Instant positive days', 'Instant positive hours',
             'Discrete Sequence positive days', 'Discrete Sequence positive hours',
             'Sequence positive days', 'Sequence positive hours',
             'Sequence Set positive days', 'Sequence Set positive hours']
    )
    def test_scale(self, tbool, delta, expected):
        assert tbool.tscale(delta) == expected

    def test_shift_tscale(self):
        assert self.tbss.shift_tscale(timedelta(days=4), timedelta(hours=2)) == \
             TBoolSeqSet('{[True@2019-09-05 00:00:00, False@2019-09-05 00:30:00],'
             '[True@2019-09-05 01:00:00, True@2019-09-05 02:00:00]}')


class TestTBoolModifications(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tbi, TBoolSeq('{True@2019-09-03}'), TBoolSeq('{True@2019-09-01, True@2019-09-03}')),
            (tbds, TBoolSeq('{True@2019-09-03}'), TBoolSeq('{True@2019-09-01, False@2019-09-02, True@2019-09-03}')),
            (tbs, TBoolSeq('[True@2019-09-03]'), TBoolSeqSet('{[True@2019-09-01, False@2019-09-02, True@2019-09-03]}')),
            (tbss, TBoolSeq('[True@2019-09-06]'),
                TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05],[True@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_insert(self, temporal, sequence, expected):
        assert temporal.insert(sequence) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tbi, TBoolInst('False@2019-09-01'), TBoolInst('False@2019-09-01')),
            (tbds, TBoolInst('False@2019-09-01'), TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tbs, TBoolInst('False@2019-09-01'), 
                TBoolSeqSet('{[False@2019-09-01], (True@2019-09-01, False@2019-09-02]}')),
            (tbss, TBoolInst('False@2019-09-01'),
                TBoolSeqSet('{[False@2019-09-01], (True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_update(self, temporal, instant, expected):
        assert temporal.update(instant) == expected

    @pytest.mark.parametrize(
        'temporal, time, expected',
        [
            (tbi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), None),
            (tbi, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc), tbi),
            (tbds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), TBoolSeq('{False@2019-09-02}')),
            (tbs, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TBoolSeqSet('{(True@2019-09-01, False@2019-09-02]}')),
            (tbss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TBoolSeqSet('{(True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
        ],
        ids=['Instant intersection', 'Instant disjoint', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_delete(self, temporal, time, expected):
        assert temporal.delete(time) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tbi, TBoolInst('True@2019-09-02'), TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tbds, TBoolInst('True@2019-09-03'), TBoolSeq('{True@2019-09-01, False@2019-09-02, True@2019-09-03}')),
            (tbs, TBoolInst('True@2019-09-03'), TBoolSeq('[True@2019-09-01, False@2019-09-02, True@2019-09-03]')),
            (tbss, TBoolInst('True@2019-09-06'),
                TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_instant(self, temporal, instant, expected):
        assert temporal.append_instant(instant) == expected

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tbds, TBoolSeq('{True@2019-09-03}'), TBoolSeq('{True@2019-09-01, False@2019-09-02, True@2019-09-03}')),
            (tbs, TBoolSeq('[True@2019-09-03]'), TBoolSeqSet('{[True@2019-09-01, False@2019-09-02], [True@2019-09-03]}')),
            (tbss, TBoolSeq('[True@2019-09-06]'),
                TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05],[True@2019-09-06]}')),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_sequence(self, temporal, sequence, expected):
        assert temporal.append_sequence(sequence) == expected


class TestTBoolEverAlwaysOperations(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_true(self, temporal, expected):
        assert temporal.always_eq(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbds, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_false(self, temporal, expected):
        assert temporal.always_eq(False) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_true(self, temporal, expected):
        assert temporal.ever_eq(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbds, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_false(self, temporal, expected):
        assert temporal.ever_eq(False) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbds, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_true(self, temporal, expected):
        assert temporal.never_eq(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbds, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_false(self, temporal, expected):
        assert temporal.never_eq(False) == expected


class TestTBoolBooleanOperations(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')
    compared = TBoolSeq('[False@2019-09-01, True@2019-09-02, True@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('False@2019-09-01')),
            (tbds, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not(self, temporal, expected):
        assert temporal.temporal_not() == expected
        assert -temporal == expected
        assert ~temporal == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('False@2019-09-01')),
            (tbds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_and_temporal(self, temporal, expected):
        assert temporal.temporal_and(self.compared) == expected
        assert temporal & self.compared == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_and_bool(self, temporal):
        assert temporal.temporal_and(True) == temporal
        assert (temporal & True) == temporal

        assert temporal.temporal_and(False) == TBool.from_base_temporal(False, temporal)
        assert (temporal & False) == TBool.from_base_temporal(False, temporal)

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbds, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_or_temporal(self, temporal, expected):
        assert temporal.temporal_or(self.compared) == expected
        assert temporal | self.compared == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_or_bool(self, temporal):
        assert temporal.temporal_or(True) == TBool.from_base_temporal(True, temporal)
        assert (temporal | True) == TBool.from_base_temporal(True, temporal)

        assert temporal.temporal_or(False) == temporal
        assert (temporal | False) == temporal

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('False@2019-09-01')),
            (tbds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.compared) == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_bool(self, temporal):
        assert temporal.temporal_equal(True) == temporal

        assert temporal.temporal_equal(False) == ~temporal

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbds, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[False@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.compared) == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_bool(self, temporal):
        assert temporal.temporal_not_equal(True) == ~temporal

        assert temporal.temporal_not_equal(False) == temporal


class TestTBoolManipulationFunctions(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')
    compared = TBoolSeq('[False@2019-09-01, True@2019-09-02, True@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, shift, expected',
        [
            (tbi, timedelta(days=1), TBoolInst('True@2019-09-02')),
            (tbds, timedelta(days=1), TBoolSeq('{True@2019-09-02, False@2019-09-03}')),
            (tbs, timedelta(days=1), TBoolSeq('[True@2019-09-02, False@2019-09-03]')),
            (tbss, timedelta(days=1),
                TBoolSeqSet('{[True@2019-09-02, False@2019-09-03],[True@2019-09-04, True@2019-09-06]}')),
            (tbi, timedelta(days=-1), TBoolInst('True@2019-08-31')),
            (tbds, timedelta(days=-1), TBoolSeq('{True@2019-08-31, False@2019-09-01}')),
            (tbs, timedelta(days=-1), TBoolSeq('[True@2019-08-31, False@2019-09-01]')),
            (tbss, timedelta(days=-1),
                TBoolSeqSet('{[True@2019-08-31, False@2019-09-01],[True@2019-09-02, True@2019-09-04]}')),
        ],
        ids=['Instant positive', 'Discrete Sequence positive', 'Sequence positive', 'SequenceSet positive',
             'Instant negative', 'Discrete Sequence negative', 'Sequence negative', 'SequenceSet negative'],
    )
    def test_shift(self, temporal, shift, expected):
        assert temporal.shift(shift) == expected

    @pytest.mark.parametrize(
        'temporal, scale, expected',
        [
            (tbi, timedelta(days=10), TBoolInst('True@2019-09-01')),
            (tbds, timedelta(days=10), TBoolSeq('{True@2019-09-01, False@2019-09-11}')),
            (tbs, timedelta(days=10), TBoolSeq('[True@2019-09-01, False@2019-09-11]')),
            (tbss, timedelta(days=10),
             TBoolSeqSet('{[True@2019-09-01, False@2019-09-03 12:00:00],[True@2019-09-06, True@2019-09-11]}')),
        ],
        ids=['Instant positive', 'Discrete Sequence positive', 'Sequence positive', 'SequenceSet positive'],
    )
    def test_tscale(self, temporal, scale, expected):
        assert temporal.tscale(scale) == expected

    @pytest.mark.parametrize(
        'temporal, shift, scale, expected',
        [
            (tbi, timedelta(days=1), timedelta(days=10), TBoolInst('True@2019-09-02')),
            (tbds, timedelta(days=1), timedelta(days=10), TBoolSeq('{True@2019-09-02, False@2019-09-12}')),
            (tbs, timedelta(days=1), timedelta(days=10), TBoolSeq('[True@2019-09-02, False@2019-09-12]')),
            (tbss, timedelta(days=1), timedelta(days=10),
                TBoolSeqSet('{[True@2019-09-02, False@2019-09-04 12:00:00],[True@2019-09-07, True@2019-09-12]}')),
            (tbi, timedelta(days=-1), timedelta(days=10), TBoolInst('True@2019-08-31')),
            (tbds, timedelta(days=-1), timedelta(days=10), TBoolSeq('{True@2019-08-31, False@2019-09-10}')),
            (tbs, timedelta(days=-1), timedelta(days=10), TBoolSeq('[True@2019-08-31, False@2019-09-10]')),
            (tbss, timedelta(days=-1), timedelta(days=10),
                TBoolSeqSet('{[True@2019-08-31, False@2019-09-02 12:00:00],[True@2019-09-05, True@2019-09-010]}')),
        ],
        ids=['Instant positive', 'Discrete Sequence positive', 'Sequence positive', 'SequenceSet positive',
             'Instant negative', 'Discrete Sequence negative', 'Sequence negative', 'SequenceSet negative'],
    )
    def test_shift_tscale(self, temporal, shift, scale, expected):
        assert temporal.shift_tscale(shift, scale) == expected


class TestTBoolRestrictors(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbds = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    timestamp = datetime(2019, 9, 1)
    timestamp_set = TimestampSet('{2019-09-01, 2019-09-03}')
    period = Period('[2019-09-01, 2019-09-02]')
    period_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tbds, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tbs, PeriodSet('{[2019-09-01, 2019-09-02)}')),
            (tbss, PeriodSet('{[2019-09-01, 2019-09-02),[2019-09-03, 2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_when_true(self, temporal, expected):
        assert temporal.when_true() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, None),
            (tbds, PeriodSet('{[2019-09-02, 2019-09-02]}')),
            (tbs, PeriodSet('{[2019-09-02, 2019-09-02]}')),
            (tbss, PeriodSet('{[2019-09-02, 2019-09-02]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_when_false(self, temporal, expected):
        assert temporal.when_false() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tbi, timestamp, TBoolInst('True@2019-09-01')),
            (tbi, timestamp_set, TBoolInst('True@2019-09-01')),
            (tbi, period, TBoolInst('True@2019-09-01')),
            (tbi, period_set, TBoolInst('True@2019-09-01')),
            (tbi, True, TBoolInst('True@2019-09-01')),
            (tbi, False, None),

            (tbds, timestamp, TBoolSeq('{True@2019-09-01}')),
            (tbds, timestamp_set, TBoolSeq('{True@2019-09-01}')),
            (tbds, period, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tbds, period_set, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tbds, True, TBoolSeq('{True@2019-09-01}')),
            (tbds, False, TBoolSeq('{False@2019-09-02}')),

            (tbs, timestamp, TBoolSeq('[True@2019-09-01]')),
            (tbs, timestamp_set, TBoolSeq('{True@2019-09-01}')),
            (tbs, period, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tbs, period_set, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tbs, True, TBoolSeq('[True@2019-09-01, True@2019-09-02)')),
            (tbs, False, TBoolSeq('[False@2019-09-02]')),

            (tbss, timestamp, TBoolSeqSet('[True@2019-09-01]')),
            (tbss, timestamp_set, TBoolSeq('{True@2019-09-01, True@2019-09-03}')),
            (tbss, period, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}')),
            (tbss, period_set,
                 TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
            (tbss, True, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02),[True@2019-09-03, True@2019-09-05]}')),
            (tbss, False, TBoolSeqSet('{[False@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-False', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-False', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-False', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-False']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbds, TBoolSeq('{True@2019-09-01}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02)')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02),[True@2019-09-03, True@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_max(self, temporal, expected):
        assert temporal.at_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbds, TBoolSeq('{False@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_min(self, temporal, expected):
        assert temporal.at_min() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tbi, timestamp, None),
            (tbi, timestamp_set, None),
            (tbi, period, None),
            (tbi, period_set, None),
            (tbi, True, None),
            (tbi, False, TBoolInst('True@2019-09-01')),

            (tbds, timestamp, TBoolSeq('{False@2019-09-02}')),
            (tbds, timestamp_set, TBoolSeq('{False@2019-09-02}')),
            (tbds, period, None),
            (tbds, period_set, None),
            (tbds, True, TBoolSeq('{False@2019-09-02}')),
            (tbds, False, TBoolSeq('{True@2019-09-01}')),

            (tbs, timestamp, TBoolSeqSet('{(True@2019-09-01, False@2019-09-02]}')),
            (tbs, timestamp_set, TBoolSeqSet('{(True@2019-09-01, False@2019-09-02]}')),
            (tbs, period, None),
            (tbs, period_set, None),
            (tbs, True, TBoolSeqSet('{[False@2019-09-02]}')),
            (tbs, False, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02)}')),

            (tbss, timestamp,
                TBoolSeqSet('{(True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
            (tbss, timestamp_set,
                TBoolSeqSet('{(True@2019-09-01, False@2019-09-02],(True@2019-09-03, True@2019-09-05]}')),
            (tbss, period, TBoolSeqSet('{[True@2019-09-03, True@2019-09-05]}')),
            (tbss, period_set, None),
            (tbss, True, TBoolSeqSet('{[False@2019-09-02]}')),
            (tbss, False, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02),[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-False', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-False', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-False', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-False']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, None),
            (tbds, TBoolSeq('{False@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_max(self, temporal, expected):
        assert temporal.minus_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, None),
            (tbds, TBoolSeq('{True@2019-09-01}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02)')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02),[True@2019-09-03, True@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor',
        [
            (tbi, timestamp),
            (tbi, timestamp_set),
            (tbi, period),
            (tbi, period_set),
            (tbi, True),
            (tbi, False),

            (tbds, timestamp),
            (tbds, timestamp_set),
            (tbds, period),
            (tbds, period_set),
            (tbds, True),
            (tbds, False),

            (tbs, timestamp),
            (tbs, timestamp_set),
            (tbs, period),
            (tbs, period_set),
            (tbs, True),
            (tbs, False),

            (tbss, timestamp),
            (tbss, timestamp_set),
            (tbss, period),
            (tbss, period_set),
            (tbss, True),
            (tbss, False),

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-False', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-False', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-False', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-False']
    )
    def test_at_minus(self, temporal, restrictor):
        assert TBool.merge(temporal.at(restrictor), temporal.minus(restrictor)) == temporal

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbds, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_minus_min_max(self, temporal):
        assert TBool.merge(temporal.at_min(), temporal.minus_min()) == temporal
        assert TBool.merge(temporal.at_max(), temporal.minus_max()) == temporal

class TestTBoolComparisonFunctions(TestTBool):
    tb = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    other = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    def test_eq(self):
        _ = self.tb == self.other

    def test_ne(self):
        _ = self.tb != self.other

    def test_lt(self):
        _ = self.tb < self.other

    def test_le(self):
        _ = self.tb <= self.other

    def test_gt(self):
        _ = self.tb > self.other

    def test_ge(self):
        _ = self.tb >= self.other
