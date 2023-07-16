from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, TInt, \
    TIntInst, TIntSeq, TIntSeqSet, TInterpolation, TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTInt(TestPyMEOS):
    pass


class TestTIntConstructors(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')
    tists = TIntSeq('Interp=Step;[1@2019-09-01, 2@2019-09-02]')
    tistss = TIntSeqSet('Interp=Step;{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1.5@2000-01-01'), TIntInst, TInterpolation.NONE),
            (TFloatSeq('{1.5@2000-01-01, 0.5@2000-01-02}'), TIntSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1.5@2000-01-01, 0.5@2000-01-02]'), TIntSeq, TInterpolation.STEPWISE),
            (TFloatSeqSet('{[1.5@2000-01-01, 0.5@2000-01-02],[1.5@2000-01-03, 1.5@2000-01-05]}'),
             TIntSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        ti = TInt.from_base_temporal(1, source)
        assert isinstance(ti, type)
        assert ti.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TIntInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TIntSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TIntSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TIntSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence',    'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        ti = TInt.from_base_time(1, source)
        assert isinstance(ti, type)
        assert ti.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('1@2019-09-01', TIntInst, TInterpolation.NONE, '1@2019-09-01 00:00:00+00'),
            ('{1@2019-09-01, 2@2019-09-02}', TIntSeq, TInterpolation.DISCRETE,
             '{1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00}'),
            ('[1@2019-09-01, 2@2019-09-02]', TIntSeq, TInterpolation.STEPWISE,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00]'),
            ('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}', TIntSeqSet,
             TInterpolation.STEPWISE, '{[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00], '
                                      '[1@2019-09-03 00:00:00+00, 1@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        ti = type(source)
        assert isinstance(ti, type)
        assert ti.interpolation() == interpolation
        assert str(ti) == expected

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[1@2019-09-01, 1@2019-09-02, 1@2019-09-03, 2@2019-09-05]', TIntSeq,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-05 00:00:00+00]'),
            ('{[1@2019-09-01, 1@2019-09-02, 1@2019-09-03, 2@2019-09-05],'
             '[1@2019-09-07, 1@2019-09-08, 1@2019-09-09]}', TIntSeqSet,
             '{[1@2019-09-01 00:00:00+00, 2@2019-09-05 00:00:00+00], '
             '[1@2019-09-07 00:00:00+00, 1@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        ti = type(source, normalize=1)
        assert isinstance(ti, type)
        assert str(ti) == expected

    @pytest.mark.parametrize(
        'value, timestamp',
        [
            (1, datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('1', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            (1, '2019-09-01'),
            ('1', '2019-09-01'),
        ],
        ids=['int-datetime', 'string-datetime', 'int-string', 'string-string']
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tii = TIntInst(value=value, timestamp=timestamp)
        assert str(tii) == '1@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['1@2019-09-01', '2@2019-09-03'], TInterpolation.DISCRETE, False,
             '{1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00}'),
            (['1@2019-09-01', '2@2019-09-03'], TInterpolation.STEPWISE, False,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),
            ([TIntInst('1@2019-09-01'), TIntInst('2@2019-09-03')], TInterpolation.DISCRETE, False,
             '{1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00}'),
            ([TIntInst('1@2019-09-01'), TIntInst('2@2019-09-03')], TInterpolation.STEPWISE, False,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),
            (['1@2019-09-01', TIntInst('2@2019-09-03')], TInterpolation.DISCRETE, False,
             '{1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00}'),
            (['1@2019-09-01', TIntInst('2@2019-09-03')], TInterpolation.STEPWISE, False,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),

            (['1@2019-09-01', '1@2019-09-02', '2@2019-09-03'], TInterpolation.STEPWISE, True,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),
            ([TIntInst('1@2019-09-01'), TIntInst('1@2019-09-02'), TIntInst('2@2019-09-03')],
             TInterpolation.STEPWISE, True,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),
            (['1@2019-09-01', '1@2019-09-02', TIntInst('2@2019-09-03')], TInterpolation.STEPWISE, True,
             '[1@2019-09-01 00:00:00+00, 2@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Stepwise', 'TIntInst Discrete', 'TIntInst Stepwise', 'Mixed Discrete',
             'Mixed Stepwise', 'String Stepwise Normalized', 'TIntInst Stepwise Normalized',
             'Mixed Stepwise Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tis = TIntSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tis) == expected
        assert tis.interpolation() == interpolation

        tis2 = TIntSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tis2) == expected
        assert tis2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tii, tids, tis, tiss, tists, tistss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Stepwise Sequence', 'Stepwise SequenceSet']
    )
    def test_from_hexwkb_constructor(self, temporal):
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        'temporal',
        [tii, tids, tis, tiss, tists, tistss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Stepwise Sequence', 'Stepwise SequenceSet']
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTIntOutputs(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, '1@2019-09-01 00:00:00+00'),
            (tids, '{1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00}'),
            (tis, '[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00]'),
            (tiss, '{[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00], '
                   '[1@2019-09-03 00:00:00+00, 1@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 'TIntInst(1@2019-09-01 00:00:00+00)'),
            (tids, 'TIntSeq({1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00})'),
            (tis, 'TIntSeq([1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00])'),
            (tiss, 'TIntSeqSet({[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00], '
                   '[1@2019-09-03 00:00:00+00, 1@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, '1@2019-09-01 00:00:00+00'),
            (tids, '{1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00}'),
            (tis, '[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00]'),
            (tiss, '{[1@2019-09-01 00:00:00+00, 2@2019-09-02 00:00:00+00], '
                   '[1@2019-09-03 00:00:00+00, 1@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, '011D00010100000000A01E4E71340200'),
            (tids, '011D000602000000030100000000A01E4E71340200020000000000F66B85340200'),
            (tis, '011D000A02000000030100000000A01E4E71340200020000000000F66B85340200'),
            (tiss, '011D000B0200000002000000030100000000A01E4E71340200020000000000F66B85340200'
                '0200000003010000000060CD89993402000100000000207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, '{\n'
                  '   "type": "MovingInteger",\n'
                  '   "bbox": [\n'
                  '     1,\n'
                  '     1\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-01T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     1\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00"\n'
                  '   ],\n'
                  '   "interpolation": "None"\n'
                  ' }'),
            (tids, '{\n'
                   '   "type": "MovingInteger",\n'
                   '   "bbox": [\n'
                   '     1,\n'
                   '     2\n'
                   '   ],\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-02T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "values": [\n'
                   '     1,\n'
                   '     2\n'
                   '   ],\n'
                   '   "datetimes": [\n'
                   '     "2019-09-01T00:00:00+00",\n'
                   '     "2019-09-02T00:00:00+00"\n'
                   '   ],\n'
                   '   "lower_inc": true,\n'
                   '   "upper_inc": true,\n'
                   '   "interpolation": "Discrete"\n'
                   ' }'),
            (tis, '{\n'
                  '   "type": "MovingInteger",\n'
                  '   "bbox": [\n'
                  '     1,\n'
                  '     2\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-02T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     1,\n'
                  '     2\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00",\n'
                  '     "2019-09-02T00:00:00+00"\n'
                  '   ],\n'
                  '   "lower_inc": true,\n'
                  '   "upper_inc": true,\n'
                  '   "interpolation": "Step"\n'
                  ' }'),
            (tiss, '{\n'
                   '   "type": "MovingInteger",\n'
                   '   "bbox": [\n'
                   '     1,\n'
                   '     2\n'
                   '   ],\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-05T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "sequences": [\n'
                   '     {\n'
                   '       "values": [\n'
                   '         1,\n'
                   '         2\n'
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
                   '         1,\n'
                   '         1\n'
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
        

class TestTIntAccessors(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TInterpolation.NONE),
            (tids, TInterpolation.DISCRETE),
            (tis, TInterpolation.STEPWISE),
            (tiss, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, {1}),
            (tids, {1, 2}),
            (tis, {1, 2}),
            (tiss, {1, 2})
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, [1]),
            (tids, [1, 2]),
            (tis, [1, 2]),
            (tiss, [1, 2, 1, 1])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 1),
            (tis, 1),
            (tiss, 1)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 2),
            (tis, 2),
            (tiss, 1)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 1),
            (tis, 1),
            (tiss, 1)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_value(self, temporal, expected):
        assert temporal.min_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 2),
            (tis, 2),
            (tiss, 2)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_value(self, temporal, expected):
        assert temporal.max_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 1),
            (tis, 1),
            (tiss, 1)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tids, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
            (tis, PeriodSet('{[2019-09-01, 2019-09-02]}')),
            (tiss, PeriodSet('{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, timedelta()),
            (tids, timedelta()),
            (tis, timedelta(days=1)),
            (tiss, timedelta(days=3)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, timedelta()),
            (tids, timedelta(days=1)),
            (tis, timedelta(days=1)),
            (tiss, timedelta(days=4)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, Period('[2019-09-01, 2019-09-01]')),
            (tids, Period('[2019-09-01, 2019-09-02]')),
            (tis, Period('[2019-09-01, 2019-09-02]')),
            (tiss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, Period('[2019-09-01, 2019-09-01]')),
            (tids, Period('[2019-09-01, 2019-09-02]')),
            (tis, Period('[2019-09-01, 2019-09-02]')),
            (tiss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 2),
            (tis, 2),
            (tiss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, tii),
            (tids, tii),
            (tis, tii),
            (tiss, tii),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, tii),
            (tids, TIntInst('2@2019-09-02')),
            (tis, TIntInst('2@2019-09-02')),
            (tiss, TIntInst('1@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, tii),
            (tids, TIntInst('2@2019-09-02')),
            (tis, TIntInst('2@2019-09-02')),
            (tiss, TIntInst('2@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, tii),
            (tids, tii),
            (tis, tii),
            (tiss, tii),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tii, 0, tii),
            (tids, 1, TIntInst('2@2019-09-02')),
            (tis, 1, TIntInst('2@2019-09-02')),
            (tiss, 2, TIntInst('1@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, [tii]),
            (tids, [tii, TIntInst('2@2019-09-02')]),
            (tis, [tii, TIntInst('2@2019-09-02')]),
            (tiss, [tii, TIntInst('2@2019-09-02'), TIntInst('1@2019-09-03'), TIntInst('1@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 1),
            (tids, 2),
            (tis, 2),
            (tiss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tids, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tis, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tiss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tids, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tis, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tiss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tii, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tids, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tis, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tiss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (tids, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tis, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                   datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tiss, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
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
            (tids, [TIntSeq('[1@2019-09-01]'), TIntSeq('[2@2019-09-02]')]),
            (tis, [TIntSeq('[1@2019-09-01, 1@2019-09-02)'),
                   TIntSeq('[2@2019-09-02]')]),
            (tiss,
             [TIntSeq('[1@2019-09-01, 1@2019-09-02)'),
              TIntSeq('[2@2019-09-02]'),
              TIntSeq('[1@2019-09-03, 1@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tids, True),
            (tis, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_upper_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected
        assert temporal.upper_inc() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, 440045287),
            (tids, 3589664982),
            (tis, 3589664982),
            (tiss, 205124107)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected


class TestTIntEverAlwaysOperations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_equal_1(self, temporal, expected):
        assert temporal.always_equal(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_equal_2(self, temporal, expected):
        assert temporal.always_equal(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, True),
            (tis, True),
            (tiss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_equal_1(self, temporal, expected):
        assert temporal.ever_equal(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, True),
            (tis, True),
            (tiss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_equal_2(self, temporal, expected):
        assert temporal.ever_equal(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_equal_1(self, temporal, expected):
        assert temporal.never_equal(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_equal_2(self, temporal, expected):
        assert temporal.never_equal(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_less_1(self, temporal, expected):
        assert temporal.always_less(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_less_2(self, temporal, expected):
        assert temporal.always_less(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_less_1(self, temporal, expected):
        assert temporal.ever_less(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, True),
            (tis, True),
            (tiss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_less_2(self, temporal, expected):
        assert temporal.ever_less(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, True),
            (tids, True),
            (tis, True),
            (tiss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_less_1(self, temporal, expected):
        assert temporal.never_less(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, False),
            (tids, False),
            (tis, False),
            (tiss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_less_2(self, temporal, expected):
        assert temporal.never_less(2) == expected


class TestTIntArithmeticOperations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')
    intarg = TIntSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')
    floatarg = TFloatSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('3@2019-09-01')),
            (tids, TIntSeq('{3@2019-09-01, 3@2019-09-02}')),
            (tis, TIntSeq('[3@2019-09-01, 3@2019-09-02]')),
            (tiss, TIntSeqSet('{[3@2019-09-01, 3@2019-09-02],[2@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_add_temporal(self, temporal, expected):
        assert temporal.add(self.intarg) == expected
        assert temporal + self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('2@2019-09-01')),
            (tids, TIntSeq('{2@2019-09-01, 3@2019-09-02}')),
            (tis, TIntSeq('[2@2019-09-01, 3@2019-09-02]')),
            (tiss, TIntSeqSet('{[2@2019-09-01, 3@2019-09-02],[2@2019-09-03, 2@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_add_int(self, temporal, expected):
        assert temporal.add(1) == expected
        assert (temporal + 1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('-1@2019-09-01')),
            (tids, TIntSeq('{-1@2019-09-01, 1@2019-09-02}')),
            (tis, TIntSeq('[-1@2019-09-01, 1@2019-09-02]')),
            (tiss, TIntSeqSet('{[-1@2019-09-01, 1@2019-09-02],[0@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_sub_temporal(self, temporal, expected):
        assert temporal.sub(self.intarg) == expected
        assert temporal - self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('0@2019-09-01')),
            (tids, TIntSeq('{0@2019-09-01, 1@2019-09-02}')),
            (tis, TIntSeq('[0@2019-09-01, 1@2019-09-02]')),
            (tiss, TIntSeqSet('{[0@2019-09-01, 1@2019-09-02],[0@2019-09-03, 0@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_sub_int(self, temporal, expected):
        assert temporal.sub(1) == expected
        assert (temporal - 1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('2@2019-09-01')),
            (tids, TIntSeq('{2@2019-09-01, 2@2019-09-02}')),
            (tis, TIntSeq('[2@2019-09-01, 2@2019-09-02]')),
            (tiss, TIntSeqSet('{[2@2019-09-01, 2@2019-09-02],[1@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_mul_temporal(self, temporal, expected):
        assert temporal.mul(self.intarg) == expected
        assert temporal * self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('2@2019-09-01')),
            (tids, TIntSeq('{2@2019-09-01, 4@2019-09-02}')),
            (tis, TIntSeq('[2@2019-09-01, 4@2019-09-02]')),
            (tiss, TIntSeqSet('{[2@2019-09-01, 4@2019-09-02],[2@2019-09-03, 2@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_mul_int(self, temporal, expected):
        assert temporal.mul(0) == TInt.from_base_temporal(0, temporal)
        assert (temporal * 0) == TInt.from_base_temporal(0, temporal)

        assert temporal.mul(1) == temporal
        assert (temporal * 1) == temporal

        assert temporal.mul(2) == expected
        assert (temporal * 2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('0@2019-09-01')),
            (tids, TIntSeq('{0@2019-09-01, 1@2019-09-02}')),
            (tis, TIntSeq('[0@2019-09-01, 1@2019-09-02]')),
            (tiss, TIntSeqSet('{[0@2019-09-01, 1@2019-09-02],[1@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_temporal(self, temporal, expected):
        assert temporal.div(self.intarg) == expected
        assert temporal / self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TFloatInst('0.5@2019-09-01')),
            (tids, TFloatSeq('{0.5@2019-09-01, 2@2019-09-02}')),
            (tis, TFloatSeqSet('{[0.5@2019-09-01, 1@2019-09-02), [2@2019-09-02]}')),
            (tiss, TFloatSeqSet('{[0.5@2019-09-01, 1@2019-09-02), [2@2019-09-02],[1@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_temporal(self, temporal, expected):
        assert temporal.div(self.floatarg) == expected
        assert temporal / self.floatarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('0@2019-09-01')),
            (tids, TIntSeq('{0@2019-09-01, 1@2019-09-02}')),
            (tis, TIntSeq('[0@2019-09-01, 1@2019-09-02]')),
            (tiss, TIntSeqSet('{[0@2019-09-01, 1@2019-09-02],[0@2019-09-03, 0@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_int(self, temporal, expected):
        assert temporal.div(1) == temporal
        assert (temporal / 1) == temporal

        assert temporal.div(2) == expected
        assert (temporal / 2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TFloatInst('0.5@2019-09-01')),
            (tids, TFloatSeq('{0.5@2019-09-01, 1@2019-09-02}')),
            (tis, TFloatSeq('[0.5@2019-09-01, 1@2019-09-02]')),
            (tiss, TFloatSeqSet('{[0.5@2019-09-01, 1@2019-09-02],[0.5@2019-09-03, 0.5@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_float(self, temporal, expected):
        assert temporal.div(1.0) == expected
        assert (temporal / 1.0) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TFloatInst('0.5@2019-09-01')),
            (tids, TFloatSeq('{0.5@2019-09-01, 1@2019-09-02}')),
            (tis, TFloatSeq('Interp=Step;[0.5@2019-09-01, 1@2019-09-02]')),
            (tiss, TFloatSeqSet('Interp=Step;{[0.5@2019-09-01, 1@2019-09-02],[0.5@2019-09-03, 0.5@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_float(self, temporal, expected):
        assert temporal.div(2.0) == expected
        assert (temporal / 2.0) == expected

class TestTIntBooleanOperations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')
    argument = TIntSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TBoolInst('False@2019-09-01')),
            (tids, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tis, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (tiss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TBoolInst('True@2019-09-01')),
            (tids, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tis, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tiss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_int(self, temporal, expected):
        assert temporal.temporal_equal(1) == expected

        assert temporal.temporal_equal(2) == ~expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TBoolInst('True@2019-09-01')),
            (tids, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tis, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (tiss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[False@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TBoolInst('False@2019-09-01')),
            (tids, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tis, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tiss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_int(self, temporal, expected):
        assert temporal.temporal_not_equal(1) == expected

        assert temporal.temporal_not_equal(2) == ~expected


class TestTIntRestrictors(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tii, instant, TIntInst('1@2019-09-01')),
            (tii, instant_set, TIntInst('1@2019-09-01')),
            (tii, sequence, TIntInst('1@2019-09-01')),
            (tii, sequence_set, TIntInst('1@2019-09-01')),
            (tii, 1, TIntInst('1@2019-09-01')),
            (tii, 2, None),

            (tids, instant, TIntSeq('{1@2019-09-01}')),
            (tids, instant_set, TIntSeq('{1@2019-09-01}')),
            (tids, sequence, TIntSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tids, sequence_set, TIntSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tids, 1, TIntSeq('{1@2019-09-01}')),
            (tids, 2, TIntSeq('{2@2019-09-02}')),

            (tis, instant, TIntSeq('[1@2019-09-01]')),
            (tis, instant_set, TIntSeq('{1@2019-09-01}')),
            (tis, sequence, TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tis, sequence_set, TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tis, 1, TIntSeq('[1@2019-09-01, 1@2019-09-02)')),
            (tis, 2, TIntSeq('[2@2019-09-02]')),

            (tiss, instant, TIntSeqSet('[1@2019-09-01]')),
            (tiss, instant_set, TIntSeq('{1@2019-09-01, 1@2019-09-03}')),
            (tiss, sequence, TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}')),
            (
                tiss, sequence_set,
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, 1, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, 2, TIntSeqSet('{[2@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-2', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-2', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-2', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-2']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('1@2019-09-01')),
            (tids, TIntSeq('{2@2019-09-02}')),
            (tis, TIntSeq('{[2@2019-09-02]}')),
            (tiss, TIntSeqSet('{[2@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_max(self, temporal, expected):
        assert temporal.at_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TIntInst('1@2019-09-01')),
            (tids, TIntSeq('{1@2019-09-01}')),
            (tis, TIntSeq('{[1@2019-09-01, 1@2019-09-02)}')),
            (tiss, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_min(self, temporal, expected):
        assert temporal.at_min() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tii, instant, None),
            (tii, instant_set, None),
            (tii, sequence, None),
            (tii, sequence_set, None),
            (tii, 1, None),
            (tii, 2, TIntInst('1@2019-09-01')),

            (tids, instant, TIntSeq('{2@2019-09-02}')),
            (tids, instant_set, TIntSeq('{2@2019-09-02}')),
            (tids, sequence, None),
            (tids, sequence_set, None),
            (tids, 1, TIntSeq('{2@2019-09-02}')),
            (tids, 2, TIntSeq('{1@2019-09-01}')),

            (tis, instant, TIntSeqSet('{(1@2019-09-01, 2@2019-09-02]}')),
            (tis, instant_set, TIntSeqSet('{(1@2019-09-01, 2@2019-09-02]}')),
            (tis, sequence, None),
            (tis, sequence_set, None),
            (tis, 1, TIntSeqSet('{[2@2019-09-02]}')),
            (tis, 2, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02)}')),

            (
                tiss, instant,
                TIntSeqSet('{(1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, instant_set,
             TIntSeqSet('{(1@2019-09-01, 2@2019-09-02],(1@2019-09-03, 1@2019-09-05]}')),
            (tiss, sequence, TIntSeqSet('{[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, sequence_set, None),
            (tiss, 1, TIntSeqSet('{[2@2019-09-02]}')),
            (tiss, 2, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-1',
             'Instant-2', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-1',
             'Discrete Sequence-2', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-1', 'Sequence-2', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-1',
             'SequenceSet-2']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, None),
            (tids, TIntSeq('{1@2019-09-01}')),
            (tis, TIntSeq('[1@2019-09-01, 1@2019-09-02)')),
            (tiss, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_max(self, temporal, expected):
        assert temporal.minus_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, None),
            (tids, TIntSeq('{2@2019-09-02}')),
            (tis, TIntSeq('[2@2019-09-02]')),
            (tiss, TIntSeqSet('{[2@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected



