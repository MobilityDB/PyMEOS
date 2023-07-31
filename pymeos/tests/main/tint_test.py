from copy import copy
from operator import not_
from datetime import datetime, timezone, timedelta
from spans.types import intrange, floatrange

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, TInt, \
    TIntInst, TIntSeq, TIntSeqSet, TInterpolation, TBox, TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTInt(TestPyMEOS):
    pass


class TestTIntConstructors(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1.5@2019-09-01'), TIntInst, TInterpolation.NONE),
            (TFloatSeq('{1.5@2019-09-01, 0.5@2019-09-02}'), TIntSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1.5@2019-09-01, 0.5@2019-09-02]'), TIntSeq, TInterpolation.STEPWISE),
            (TFloatSeqSet('{[1.5@2019-09-01, 0.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}'),
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
            (TimestampSet('{2019-09-01, 2019-09-02}'), TIntSeq, TInterpolation.DISCRETE),
            (Period('[2019-09-01, 2019-09-02]'), TIntSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'), TIntSeqSet, TInterpolation.STEPWISE)
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
        [tii, tids, tis, tiss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_as_constructor(self, temporal):
        assert temporal == temporal.from_wkb(temporal.as_wkb())
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())
        assert temporal == temporal.from_mfjson(temporal.as_mfjson())

    @pytest.mark.parametrize(
        'temporal',
        [tii, tids, tis, tiss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
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

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TBox('TBOX XT([1,1],[2019-09-01, 2019-09-01])')),
            (tids, TBox('TBOX XT([1,2],[2019-09-01, 2019-09-02])')),
            (tis, TBox('TBOX XT([1,2],[2019-09-01, 2019-09-02])')),
            (tiss, TBox('TBOX XT([1,2],[2019-09-01, 2019-09-05])')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_bounding_box(self, temporal, expected):
        assert temporal.bounding_box() == expected


class TestTIntTransformations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TIntInst('1@2019-09-01'), tii),
            (TIntSeq('{1@2019-09-01}'), tii),
            (TIntSeq('[1@2019-09-01]'), tii),
            (TIntSeqSet('{[1@2019-09-01]}'), tii),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_instant(self, temporal, expected):
        temp = temporal.to_instant()
        assert isinstance(temp, TIntInst)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TIntInst('1@2019-09-01'), 
                TIntSeq('[1@2019-09-01]')),
            (TIntSeq('{1@2019-09-01, 2@2019-09-02}'),
                TIntSeq('{1@2019-09-01, 2@2019-09-02}')),
            (TIntSeq('[1@2019-09-01, 2@2019-09-02]'),
                TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
            (TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}'),
                TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequence(self, temporal, expected):
        temp = temporal.to_sequence()
        assert isinstance(temp, TIntSeq)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TIntInst('1@2019-09-01'), 
                TIntSeqSet('{[1@2019-09-01]}')),
            (TIntSeq('{1@2019-09-01, 2@2019-09-02}'),
                TIntSeqSet('{[1@2019-09-01], [2@2019-09-02]}')),
            (TIntSeq('[1@2019-09-01, 2@2019-09-02]'),
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}')),
            (TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}'),
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequenceset(self, temporal, expected):
        temp = temporal.to_sequenceset()
        assert isinstance(temp, TIntSeqSet)
        assert temp == expected

    @pytest.mark.parametrize(
        'tint, delta, expected',
        [(tii, timedelta(days=4), TIntInst('1@2019-09-05')),
         (tii, timedelta(days=-4), TIntInst('1@2019-08-28')),
         (tii, timedelta(hours=2), TIntInst('1@2019-09-01 02:00:00')),
         (tii, timedelta(hours=-2), TIntInst('1@2019-08-31 22:00:00')), 
         (tids, timedelta(days=4), TIntSeq('{1@2019-09-05, 2@2019-09-06}')),
         (tids, timedelta(days=-4), TIntSeq('{1@2019-08-28, 2@2019-08-29}')),
         (tids, timedelta(hours=2), TIntSeq('{1@2019-09-01 02:00:00, 2@2019-09-02 02:00:00}')),
         (tids, timedelta(hours=-2), TIntSeq('{1@2019-08-31 22:00:00, 2@2019-09-01 22:00:00}')),
         (tis, timedelta(days=4), TIntSeq('[1@2019-09-05, 2@2019-09-06]')),
         (tis, timedelta(days=-4), TIntSeq('[1@2019-08-28, 2@2019-08-29]')),
         (tis, timedelta(hours=2), TIntSeq('[1@2019-09-01 02:00:00, 2@2019-09-02 02:00:00]')),
         (tis, timedelta(hours=-2), TIntSeq('[1@2019-08-31 22:00:00, 2@2019-09-01 22:00:00]')),
         (tiss, timedelta(days=4),
             TIntSeqSet('{[1@2019-09-05, 2@2019-09-06],[1@2019-09-07, 1@2019-09-09]}')),
         (tiss, timedelta(days=-4),
             TIntSeqSet('{[1@2019-08-28, 2@2019-08-29],[1@2019-08-30, 1@2019-09-01]}')),
         (tiss, timedelta(hours=2),
             TIntSeqSet('{[1@2019-09-01 02:00:00, 2@2019-09-02 02:00:00],'
                         '[1@2019-09-03 02:00:00, 1@2019-09-05 02:00:00]}')),
         (tiss, timedelta(hours=-2),
             TIntSeqSet('{[1@2019-08-31 22:00:00, 2@2019-09-01 22:00:00],'
             '[1@2019-09-02 22:00:00, 1@2019-09-04 22:00:00]}')),
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
    def test_shift(self, tint, delta, expected):
        assert tint.shift(delta) == expected

    @pytest.mark.parametrize(
        'tint, delta, expected',
        [(tii, timedelta(days=4), TIntInst('1@2019-09-01')),
         (tii, timedelta(hours=2), TIntInst('1@2019-09-01')),
         (tids, timedelta(days=4), TIntSeq('{1@2019-09-01, 2@2019-09-05}')),
         (tids, timedelta(hours=2), TIntSeq('{1@2019-09-01 00:00:00, 2@2019-09-01 02:00:00}')),
         (tis, timedelta(days=4), TIntSeq('[1@2019-09-01, 2@2019-09-05]')),
         (tis, timedelta(hours=2), TIntSeq('[1@2019-09-01 00:00:00, 2@2019-09-01 02:00:00]')),
         (tiss, timedelta(days=4),
             TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
         (tiss, timedelta(hours=2),
             TIntSeqSet('{[1@2019-09-01 00:00:00, 2@2019-09-01 00:30:00],'
                         '[1@2019-09-01 01:00:00, 1@2019-09-01 02:00:00]}')),
        ],
        ids=['Instant positive days', 'Instant positive hours',
             'Discrete Sequence positive days', 'Discrete Sequence positive hours',
             'Sequence positive days', 'Sequence positive hours',
             'Sequence Set positive days', 'Sequence Set positive hours']
    )
    def test_scale(self, tint, delta, expected):
        assert tint.tscale(delta) == expected

    def test_shift_tscale(self):
        assert self.tiss.shift_tscale(timedelta(days=4), timedelta(hours=2)) == \
             TIntSeqSet('{[1@2019-09-05 00:00:00, 2@2019-09-05 00:30:00],'
             '[1@2019-09-05 01:00:00, 1@2019-09-05 02:00:00]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, TFloatInst('1@2019-09-01')),
            (tids, TFloatSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tis, TFloatSeq('Interp=Step;[1@2019-09-01, 2@2019-09-02]')),
            # (tiss, TFloatSeqSet('Interp=Step;{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence'] #, 'SequenceSet']
    )
    def test_to_tfloat(self, temporal, expected):
        assert temporal.to_tfloat() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, intrange(1, 1, True, True)),
            (tids, intrange(1, 2, True, True)),
            (tis, intrange(1, 2, True, True)),
            (tiss, intrange(1, 2, True, True)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_intrange(self, temporal, expected):
        assert temporal.to_intrange() == expected

    
class TestTIntModifications(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tii, TIntSeq('{1@2019-09-03}'), TIntSeq('{1@2019-09-01, 1@2019-09-03}')),
            (tids, TIntSeq('{1@2019-09-03}'), TIntSeq('{1@2019-09-01, 2@2019-09-02, 1@2019-09-03}')),
            (tis, TIntSeq('[1@2019-09-03]'), TIntSeqSet('{[1@2019-09-01, 2@2019-09-02, 1@2019-09-03]}')),
            (tiss, TIntSeq('[1@2019-09-06]'),
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05],[1@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_insert(self, temporal, sequence, expected):
        assert temporal.insert(sequence) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tii, TIntInst('2@2019-09-01'), TIntInst('2@2019-09-01')),
            (tids, TIntInst('2@2019-09-01'), TIntSeq('{2@2019-09-01, 2@2019-09-02}')),
            (tis, TIntInst('2@2019-09-01'), 
                TIntSeqSet('{[2@2019-09-01], (1@2019-09-01, 2@2019-09-02]}')),
            (tiss, TIntInst('2@2019-09-01'),
                TIntSeqSet('{[2@2019-09-01], (1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_update(self, temporal, instant, expected):
        assert temporal.update(instant) == expected

    @pytest.mark.parametrize(
        'temporal, time, expected',
        [
            (tii, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), None),
            (tii, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc), tii),
            (tids, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), TIntSeq('{2@2019-09-02}')),
            (tis, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TIntSeqSet('{(1@2019-09-01, 2@2019-09-02]}')),
            (tiss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TIntSeqSet('{(1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
        ],
        ids=['Instant intersection', 'Instant disjoint', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_delete(self, temporal, time, expected):
        assert temporal.delete(time) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tii, TIntInst('1@2019-09-02'), TIntSeq('{1@2019-09-01, 1@2019-09-02}')),
            (tids, TIntInst('1@2019-09-03'), TIntSeq('{1@2019-09-01, 2@2019-09-02, 1@2019-09-03}')),
            (tis, TIntInst('1@2019-09-03'), TIntSeq('[1@2019-09-01, 2@2019-09-02, 1@2019-09-03]')),
            (tiss, TIntInst('1@2019-09-06'),
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_instant(self, temporal, instant, expected):
        assert temporal.append_instant(instant) == expected

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tids, TIntSeq('{1@2019-09-03}'), TIntSeq('{1@2019-09-01, 2@2019-09-02, 1@2019-09-03}')),
            (tis, TIntSeq('[1@2019-09-03]'), TIntSeqSet('{[1@2019-09-01, 2@2019-09-02], [1@2019-09-03]}')),
            (tiss, TIntSeq('[1@2019-09-06]'),
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05],[1@2019-09-06]}')),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_sequence(self, temporal, sequence, expected):
        assert temporal.append_sequence(sequence) == expected


class TestTIntEverAlwaysOperations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, True),
            (tii, 2, False),
            (tids, 1, False),
            (tids, 2, False),
            (tis, 1, False),
            (tis, 2, False),
            (tiss, 1, False),
            (tiss, 2, False),
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_always_equal_ever_not_equal(self, temporal, argument, expected):
        assert temporal.always_equal(argument) == expected
        assert temporal.never_not_equal(argument) == expected
        assert temporal.ever_not_equal(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, True),
            (tii, 2, False),
            (tids, 1, True),
            (tids, 2, True),
            (tis, 1, True),
            (tis, 2, True),
            (tiss, 1, True),
            (tiss, 2, True)
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_ever_equal_always_not_equal(self, temporal, argument, expected):
        assert temporal.ever_equal(argument) == expected
        assert temporal.always_not_equal(argument) == not_(expected)
        assert temporal.never_equal(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, False),
            (tii, 2, True),
            (tids, 1, False),
            (tids, 2, False),
            (tis, 1, False),
            (tis, 2, False),
            (tiss, 1, False),
            (tiss, 2, False),
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_always_less_ever_greater_or_equal(self, temporal, argument, expected):
        assert temporal.always_less(argument) == expected
        # assert temporal.never_greater_or_equal(argument) == expected
        assert temporal.ever_greater_or_equal(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, False),
            (tii, 2, True),
            (tids, 1, False),
            (tids, 2, True),
            (tis, 1, False),
            (tis, 2, True),
            (tiss, 1, False),
            (tiss, 2, True),
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_ever_less_always_greater_or_equal(self, temporal, argument, expected):
        assert temporal.ever_less(argument) == expected
        assert temporal.always_greater_or_equal(argument) == not_(expected)
        assert temporal.never_less(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, True),
            (tii, 2, True),
            (tids, 1, False),
            (tids, 2, True),
            (tis, 1, False),
            (tis, 2, True),
            (tiss, 1, False),
            (tiss, 2, True),
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_always_less_or_equal_ever_greater(self, temporal, argument, expected):
        assert temporal.always_less_or_equal(argument) == expected
        assert temporal.never_greater(argument) == expected
        assert temporal.ever_greater(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, True),
            (tii, 2, True),
            (tids, 1, True),
            (tids, 2, True),
            (tis, 1, True),
            (tis, 2, True),
            (tiss, 1, True),
            (tiss, 2, True),
        ],
        ids=['Instant 1', 'Instant 2', 'Discrete Sequence 1', 'Discrete Sequence 2',
             'Sequence 1', 'Sequence 2', 'SequenceSet 1', 'SequenceSet 2']
    )
    def test_ever_less_or_equal_always_greater(self, temporal, argument, expected):
        assert temporal.ever_less_or_equal(argument) == expected
        assert temporal.always_greater(argument) == not_(expected)
        assert temporal.never_less_or_equal(argument) == not_(expected)


class TestTIntMathematicalOperations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')
    tintarg = TIntSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')
    tfloatarg = TFloatSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, tintarg, TIntInst('3@2019-09-01')),
            (tids, tintarg, TIntSeq('{3@2019-09-01, 3@2019-09-02}')),
            (tis, tintarg, TIntSeq('[3@2019-09-01, 3@2019-09-02]')),
            (tiss, tintarg, TIntSeqSet('{[3@2019-09-01, 3@2019-09-02],[2@2019-09-03]}')),
            (tii, tfloatarg, TFloatInst('3@2019-09-01')),
            (tids, tfloatarg, TFloatSeq('{3@2019-09-01, 3@2019-09-02}')),
            (tis, tfloatarg, TFloatSeqSet('{[3@2019-09-01, 2@2019-09-02),[3@2019-09-02]}')),
            (tiss, tfloatarg, TFloatSeqSet('{[3@2019-09-01, 2@2019-09-02),[3@2019-09-02],[2@2019-09-03]}')),
        ],
        ids=['Instant TInt', 'Discrete Sequence TInt', 'Sequence TInt', 'SequenceSet TInt',
             'Instant TFloat', 'Discrete Sequence TFloat', 'Sequence TFloat', 'SequenceSet TFloat']
    )
    def test_temporal_add_temporal(self, temporal, argument, expected):
        assert temporal.add(argument) == expected
        assert temporal + argument == expected

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, TIntInst('2@2019-09-01')),
            (tids, 1, TIntSeq('{2@2019-09-01, 3@2019-09-02}')),
            (tis, 1, TIntSeq('[2@2019-09-01, 3@2019-09-02]')),
            (tiss, 1, TIntSeqSet('{[2@2019-09-01, 3@2019-09-02],[2@2019-09-03, 2@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_add_int_float(self, temporal, argument, expected):
        assert temporal.add(argument) == expected
        # assert temporal.add(float(argument)) == expected.to_tfloat()
        assert temporal.radd(argument) == expected
        # assert temporal.radd(float(argument)) == expected.to_tfloat()
        assert (temporal + argument) == expected
        # assert (temporal + float(argument)) == expected.to_tfloat()
        assert (argument + temporal) == expected
        # assert (float(argument) + temporal) == expected.to_tfloat()

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, tintarg, TIntInst('-1@2019-09-01')),
            (tids, tintarg, TIntSeq('{-1@2019-09-01, 1@2019-09-02}')),
            (tis, tintarg, TIntSeq('[-1@2019-09-01, 1@2019-09-02]')),
            (tiss, tintarg, TIntSeqSet('{[-1@2019-09-01, 1@2019-09-02],[0@2019-09-03]}')),
            (tii, tfloatarg, TFloatInst('-1@2019-09-01')),
            (tids, tfloatarg, TFloatSeq('{-1@2019-09-01, 1@2019-09-02}')),
            (tis, tfloatarg, TFloatSeqSet('{[-1@2019-09-01, 0@2019-09-02),[1@2019-09-02]}')),
            (tiss, tfloatarg, TFloatSeqSet('{[-1@2019-09-01, 0@2019-09-02),[1@2019-09-02],[0@2019-09-03]}'))
        ],
        ids=['Instant TInt', 'Discrete Sequence TInt', 'Sequence TInt', 'SequenceSet TInt',
             'Instant TFloat', 'Discrete Sequence TFloat', 'Sequence TFloat', 'SequenceSet TFloat']
    )
    def test_temporal_sub_temporal(self, temporal, argument, expected):
        assert temporal.sub(argument) == expected
        assert temporal - argument == expected

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, TIntInst('0@2019-09-01')),
            (tids, 1, TIntSeq('{0@2019-09-01, 1@2019-09-02}')),
            (tis, 1, TIntSeq('[0@2019-09-01, 1@2019-09-02]')),
            (tiss, 1, TIntSeqSet('{[0@2019-09-01, 1@2019-09-02],[0@2019-09-03, 0@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_sub_int_float(self, temporal, argument, expected):
        assert temporal.sub(argument) == expected
        # assert temporal.sub(float(argument)) == expected.to_tfloat()
        assert temporal.rsub(argument) == -1 * expected
        # assert temporal.rsub(float(argument)) == (-1 * expected).to_tfloat()
        assert (temporal - argument) == expected
        # assert (temporal - float(argument)) == expected.to_tfloat()
        assert (argument - temporal) == - 1 * expected
        # assert (float(argument) - temporal) == (- 1 * expected).to_tfloat()

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, tintarg, TIntInst('2@2019-09-01')),
            (tids, tintarg, TIntSeq('{2@2019-09-01, 2@2019-09-02}')),
            (tis, tintarg, TIntSeq('[2@2019-09-01, 2@2019-09-02]')),
            (tiss, tintarg, TIntSeqSet('{[2@2019-09-01, 2@2019-09-02],[1@2019-09-03]}')),
            (tii, tfloatarg, TFloatInst('2@2019-09-01')),
            (tids, tfloatarg, TFloatSeq('{2@2019-09-01, 2@2019-09-02}')),
            (tis, tfloatarg, TFloatSeqSet('{[2@2019-09-01, 1@2019-09-02), [2@2019-09-02]}')),
            (tiss, tfloatarg, TFloatSeqSet('{[2@2019-09-01, 1@2019-09-02), [2@2019-09-02],[1@2019-09-03]}')),
        ],
        ids=['Instant TInt', 'Discrete Sequence TInt', 'Sequence TInt', 'SequenceSet TInt',
             'Instant TFloat', 'Discrete Sequence TFloat', 'Sequence TFloat', 'SequenceSet TFloat']
    )
    def test_temporal_mul_temporal(self, temporal, argument, expected):
        assert temporal.mul(argument) == expected
        assert temporal * argument == expected

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 0, TInt.from_base_temporal(0, tii)),
            (tids, 0, TInt.from_base_temporal(0, tids)),
            (tis, 0, TInt.from_base_temporal(0, tis)),
            (tiss, 0, TInt.from_base_temporal(0, tiss)),

            (tii, 1, tii),
            (tids, 1, tids),
            (tis, 1, tis),
            (tiss, 1, tiss),

            (tii, 2, TIntInst('2@2019-09-01')),
            (tids, 2, TIntSeq('{2@2019-09-01, 4@2019-09-02}')),
            (tis, 2, TIntSeq('[2@2019-09-01, 4@2019-09-02]')),
            (tiss, 2, TIntSeqSet('{[2@2019-09-01, 4@2019-09-02],[2@2019-09-03, 2@2019-09-05]}')),
        ],
        ids=['Instant 0', 'Discrete Sequence 0', 'Sequence 0', 'SequenceSet 0',
             'Instant 1', 'Discrete Sequence 1', 'Sequence 1', 'SequenceSet 1',
             'Instant 2', 'Discrete Sequence 2', 'Sequence 2', 'SequenceSet 2']
    )
    def test_temporal_mul_int_float(self, temporal, argument, expected):
        assert temporal.mul(argument) == expected
        # assert temporal.mul(float(argument)) == expected.to_tfloat()
        assert temporal.rmul(argument) == expected
        # assert temporal.rmul(float(argument)) == expected.to_tfloat()
        assert (temporal * argument) == expected
        # assert (temporal * float(argument)) == expected.to_tfloat()
        assert (argument * temporal) == expected
        # assert (float(argument) * temporal) == expected.to_tfloat()

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, tintarg, TIntInst('0@2019-09-01')),
            (tids, tintarg, TIntSeq('{0@2019-09-01, 2@2019-09-02}')),
            (tis, tintarg, TIntSeq('[0@2019-09-01, 2@2019-09-02]')),
            (tiss, tintarg, TIntSeqSet('{[0@2019-09-01, 2@2019-09-02],[1@2019-09-03]}')),
            (tii, tfloatarg, TFloatInst('0.5@2019-09-01')),
            (tids, tfloatarg, TFloatSeq('{0.5@2019-09-01, 2@2019-09-02}')),
            (tis, tfloatarg, TFloatSeqSet('{[0.5@2019-09-01, 1@2019-09-02), [2@2019-09-02]}')),
            (tiss, tfloatarg, TFloatSeqSet('{[0.5@2019-09-01, 1@2019-09-02), [2@2019-09-02],[1@2019-09-03]}'))
        ],
        ids=['Instant TInt', 'Discrete Sequence TInt', 'Sequence TInt', 'SequenceSet TInt',
             'Instant TFloat', 'Discrete Sequence TFloat', 'Sequence TFloat', 'SequenceSet TFloat']
    )
    def test_temporal_div_temporal(self, temporal, argument, expected):
        assert temporal.div(argument) == expected
        assert temporal / argument == expected

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tii, 1, tii),
            (tids, 1, tids),
            (tis, 1, tis),
            (tiss, 1, tiss),
            (tii, 1.0, TFloatInst('1@2019-09-01')),
            (tids, 1.0, TFloatSeq('{1@2019-09-01, 2@2019-09-02}')),
            # (tis, 1.0, TFloatSeq('[1@2019-09-01, 2@2019-09-02]')),
            # (tiss, 1.0, TFloatSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
            (tii, 2, TIntInst('0@2019-09-01')),
            (tids, 2, TIntSeq('{0@2019-09-01, 1@2019-09-02}')),
            (tis, 2, TIntSeq('[0@2019-09-01, 1@2019-09-02]')),
            (tiss, 2, TIntSeqSet('{[0@2019-09-01, 1@2019-09-02],[0@2019-09-03, 0@2019-09-05]}')),
            (tii, 2.0, TFloatInst('0.5@2019-09-01')),
            (tids, 2.0, TFloatSeq('{0.5@2019-09-01, 1@2019-09-02}')),
            (tis, 2.0, TFloatSeq('Interp=Step;[0.5@2019-09-01, 1@2019-09-02]')),
            (tiss, 2.0, TFloatSeqSet('Interp=Step;{[0.5@2019-09-01, 1@2019-09-02],[0.5@2019-09-03, 0.5@2019-09-05]}')),
        ],
        ids=['Instant 1', 'Discrete Sequence 1', 'Sequence 1', 'SequenceSet 1',
             'Instant 1.0', 'Discrete Sequence 1.0', # 'Sequence 1.0', 'SequenceSet 1.0',
             'Instant 2', 'Discrete Sequence 2', 'Sequence 2', 'SequenceSet 2',
             'Instant 2.0', 'Discrete Sequence 2.0', 'Sequence 2.0', 'SequenceSet 2.0']
    )
    def test_temporal_div_int_float (self, temporal, argument, expected):
        assert temporal.div(argument) == expected
        assert (temporal / argument) == expected

    @pytest.mark.parametrize(
        'temporal',
        [tii, tids, tis, tiss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_abs(self, temporal):
        assert temporal.abs() == temporal
        assert (-1 * temporal).abs() == temporal

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tii, TIntInst('1@2019-09-01')),
            # (tids, TIntSeq('{1@2019-09-01, 1@2019-09-02}')),
            # (tis, TIntSeq('[1@2019-09-01, 1@2019-09-02]')),
            # (tiss, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02],[0@2019-09-03, 0@2019-09-05]}')),
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_delta_value(self, temporal, expected):
        # assert temporal.delta_value() == expected


class TestTIntTemporalComparisons(TestTInt):
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

    timestamp = datetime(2019, 9, 1)
    timestamp_set = TimestampSet('{2019-09-01, 2019-09-03}')
    period = Period('[2019-09-01, 2019-09-02]')
    period_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tii, timestamp, TIntInst('1@2019-09-01')),
            (tii, timestamp_set, TIntInst('1@2019-09-01')),
            (tii, period, TIntInst('1@2019-09-01')),
            (tii, period_set, TIntInst('1@2019-09-01')),
            (tii, 1, TIntInst('1@2019-09-01')),
            (tii, 2, None),
            # (tii, [1,2], TIntInst('1@2019-09-01')),

            (tids, timestamp, TIntSeq('{1@2019-09-01}')),
            (tids, timestamp_set, TIntSeq('{1@2019-09-01}')),
            (tids, period, TIntSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tids, period_set, TIntSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tids, 1, TIntSeq('{1@2019-09-01}')),
            (tids, 2, TIntSeq('{2@2019-09-02}')),
            # (tids, [1,2], TIntSeq('{2@2019-09-02}')),

            (tis, timestamp, TIntSeq('[1@2019-09-01]')),
            (tis, timestamp_set, TIntSeq('{1@2019-09-01}')),
            (tis, period, TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tis, period_set, TIntSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tis, 1, TIntSeq('[1@2019-09-01, 1@2019-09-02)')),
            (tis, 2, TIntSeq('[2@2019-09-02]')),
            # (tis, [1,2], TIntSeq('[2@2019-09-02]')),

            (tiss, timestamp, TIntSeqSet('[1@2019-09-01]')),
            (tiss, timestamp_set, TIntSeq('{1@2019-09-01, 1@2019-09-03}')),
            (tiss, period, TIntSeqSet('{[1@2019-09-01, 2@2019-09-02]}')),
            (tiss, period_set,
                TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, 1, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, 2, TIntSeqSet('{[2@2019-09-02]}')),
            # (tiss, [1,2], TIntSeqSet('{[2@2019-09-02]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period',
             'Instant-PeriodSet', 'Instant-1', 'Instant-2', # 'Instant-[1,2]', 
             'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet',
             'Discrete Sequence-1', 'Discrete Sequence-2', # 'Discrete Sequence-[1,2]', 
             'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-1', 'Sequence-2', # 'Sequence-[1,2]', 
             'SequenceSet-Timestamp', 'SequenceSet-TimestampSet', 'SequenceSet-Period',
             'SequenceSet-PeriodSet', 'SequenceSet-1', 'SequenceSet-2', # 'SequenceSet-[1,2]'
             ]
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

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
        'temporal, restrictor, expected',
        [
            (tii, timestamp, None),
            (tii, timestamp_set, None),
            (tii, period, None),
            (tii, period_set, None),
            (tii, 1, None),
            (tii, 2, TIntInst('1@2019-09-01')),
            # (tii, [1,2], None),

            (tids, timestamp, TIntSeq('{2@2019-09-02}')),
            (tids, timestamp_set, TIntSeq('{2@2019-09-02}')),
            (tids, period, None),
            (tids, period_set, None),
            (tids, 1, TIntSeq('{2@2019-09-02}')),
            (tids, 2, TIntSeq('{1@2019-09-01}')),
            # (tids, [1,2], tids),

            (tis, timestamp, TIntSeqSet('{(1@2019-09-01, 2@2019-09-02]}')),
            (tis, timestamp_set, TIntSeqSet('{(1@2019-09-01, 2@2019-09-02]}')),
            (tis, period, None),
            (tis, period_set, None),
            (tis, 1, TIntSeqSet('{[2@2019-09-02]}')),
            (tis, 2, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02)}')),
            # (tis, [1,2], tis),

            (tiss, timestamp,
                TIntSeqSet('{(1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, timestamp_set,
             TIntSeqSet('{(1@2019-09-01, 2@2019-09-02],(1@2019-09-03, 1@2019-09-05]}')),
            (tiss, period, TIntSeqSet('{[1@2019-09-03, 1@2019-09-05]}')),
            (tiss, period_set, None),
            (tiss, 1, TIntSeqSet('{[2@2019-09-02]}')),
            (tiss, 2, TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}')),
            # (tiss, [1,2], tiss)
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period',
             'Instant-PeriodSet', 'Instant-1', 'Instant-2', # 'Instant-[1,2]', 
             'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet',
             'Discrete Sequence-1', 'Discrete Sequence-2', # 'Discrete Sequence-[1,2]', 
             'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-1', 'Sequence-2', # 'Sequence-[1,2]', 
             'SequenceSet-Timestamp', 'SequenceSet-TimestampSet', 'SequenceSet-Period',
             'SequenceSet-PeriodSet', 'SequenceSet-1', 'SequenceSet-2', # 'SequenceSet-[1,2]'
             ]
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

    @pytest.mark.parametrize(
        'temporal, restrictor',
        [
            (tii, timestamp),
            (tii, timestamp_set),
            (tii, period),
            (tii, period_set),
            (tii, 1),
            (tii, 2),

            (tids, timestamp),
            (tids, timestamp_set),
            (tids, period),
            (tids, period_set),
            (tids, 1),
            (tids, 2),

            (tis, timestamp),
            (tis, timestamp_set),
            (tis, period),
            (tis, period_set),
            (tis, 1),
            (tis, 2),

            (tiss, timestamp),
            (tiss, timestamp_set),
            (tiss, period),
            (tiss, period_set),
            (tiss, 1),
            (tiss, 2),

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-1',
             'Instant-2', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-1',
             'Discrete Sequence-2', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-1', 'Sequence-2', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-1',
             'SequenceSet-2']
    )
    def test_at_minus(self, temporal, restrictor):
        assert TInt.merge(temporal.at(restrictor), temporal.minus(restrictor)) == temporal

    @pytest.mark.parametrize(
        'temporal',
        [tii, tids, tis, tiss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_minus_min_max(self, temporal):
        assert TInt.merge(temporal.at_min(), temporal.minus_min()) == temporal
        assert TInt.merge(temporal.at_max(), temporal.minus_max()) == temporal


class TestTIntSplitOperaations(TestTInt):
    tii = TIntInst('1@2019-09-01')
    tids = TIntSeq('{1@2019-09-01, 2@2019-09-02}')
    tis = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    tiss = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tii, [TIntInst('1@2019-09-01')]),
            (tids, [TIntSeq('{1@2019-09-01}'),TIntSeq('{2@2019-09-02}')]),
            (tis, [TIntSeq('[1@2019-09-01, 1@2019-09-02)'),TIntSeq('[2@2019-09-02]')]),
            (tiss, [TIntSeqSet('{[1@2019-09-01, 1@2019-09-02),[1@2019-09-03, 1@2019-09-05]}'),TIntSeq('[2@2019-09-02]')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_split(self, temporal, expected):
        assert temporal.value_split(2) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tii, [TIntInst('1@2019-09-01')]),
            # (tids, [TIntSeq('{1@2019-09-01}'),TIntSeq('{2@2019-09-02}')]),
            # (tis, [TIntSeq('[1@2019-09-01, 1@2019-09-02)'),TIntSeq('{2@2019-09-02}')]),
            # (tiss, [TIntSeqSet('{[1@2019-09-01, 1@2019-09-02)}'),TIntSeq('[2@2019-09-02]'),
                # TIntSeq('[1@2019-09-03, 1@2019-09-04)'),TIntSeqSet('{[1@2019-09-04, 1@2019-09-05]}')]),
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_time_split(self, temporal, expected):
        # assert temporal.time_split(timedelta(days=2)) == expected


class TestTIntComparisonFunctions(TestTInt):
    ti = TIntSeq('[1@2019-09-01, 2@2019-09-02]')
    other = TIntSeqSet('{[1@2019-09-01, 2@2019-09-02],[1@2019-09-03, 1@2019-09-05]}')

    def test_eq(self):
        _ = self.ti == self.other

    def test_ne(self):
        _ = self.ti != self.other

    def test_lt(self):
        _ = self.ti < self.other

    def test_le(self):
        _ = self.ti <= self.other

    def test_gt(self):
        _ = self.ti > self.other

    def test_ge(self):
        _ = self.ti >= self.other
