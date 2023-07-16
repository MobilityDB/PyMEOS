from copy import copy
from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, \
    TInt, TIntInst, TIntSeq, TIntSeqSet, TInterpolation, TimestampSet, Period, PeriodSet

from tests.conftest import TestPyMEOS


class TestTFloat(TestPyMEOS):
    pass


class TestTFloatConstructors(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')
    tfsts = TFloatSeq('Interp=Step;[1.5@2019-09-01, 2.5@2019-09-02]')
    tfstss = TFloatSeqSet('Interp=Step;{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TIntInst('1@2000-01-01'), TFloatInst, TInterpolation.NONE),
            (TIntSeq('{1@2000-01-01, 2@2000-01-02}'), TFloatSeq, TInterpolation.DISCRETE),
            (TIntSeq('[1@2000-01-01, 2@2000-01-02]'), TFloatSeq, TInterpolation.STEPWISE),
            (TIntSeqSet('{[1@2000-01-01, 2@2000-01-02],[1@2000-01-03, 1@2000-01-05]}'),
             TFloatSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tf = TFloat.from_base_temporal(1.5, source)
        assert isinstance(tf, type)
        assert tf.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1@2000-01-01'), TFloatInst, TInterpolation.NONE),
            (TFloatSeq('{1@2000-01-01, 2@2000-01-02}'), TFloatSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1@2000-01-01, 2@2000-01-02]'), TFloatSeq, TInterpolation.LINEAR),
            (TFloatSeqSet('{[1@2000-01-01, 2@2000-01-02],[1@2000-01-03, 1@2000-01-05]}'),
             TFloatSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tf = TFloat.from_base_temporal(1.5, source)
        assert isinstance(tf, type)
        assert tf.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TFloatInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TFloatSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TFloatSeq, TInterpolation.LINEAR),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TFloatSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tf = TFloat.from_base_time(1.5, source, interpolation)
        assert isinstance(tf, type)
        assert tf.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('1.5@2019-09-01', TFloatInst, TInterpolation.NONE, '1.5@2019-09-01 00:00:00+00'),
            ('{1.5@2019-09-01, 2.5@2019-09-02}', TFloatSeq, TInterpolation.DISCRETE,
             '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00}'),
            ('[1.5@2019-09-01, 2.5@2019-09-02]', TFloatSeq, TInterpolation.LINEAR,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00]'),
            ('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}', TFloatSeqSet,
             TInterpolation.LINEAR, '{[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00], '
                                      '[1.5@2019-09-03 00:00:00+00, 1.5@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tf = type(source)
        assert isinstance(tf, type)
        assert tf.interpolation() == interpolation
        assert str(tf) == expected

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[1.5@2019-09-01, 1.75@2019-09-02, 2@2019-09-03, 2.5@2019-09-05]', TFloatSeq,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-05 00:00:00+00]'),
            ('{[1.5@2019-09-01, 1.75@2019-09-02, 2@2019-09-03, 2.5@2019-09-05],'
             '[1.5@2019-09-07, 1.5@2019-09-08, 1.5@2019-09-09]}', TFloatSeqSet,
             '{[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-05 00:00:00+00], '
             '[1.5@2019-09-07 00:00:00+00, 1.5@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tf = type(source, normalize=1)
        assert isinstance(tf, type)
        assert str(tf) == expected

    @pytest.mark.parametrize(
        'value, timestamp',
        [
            (1.5, datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('1.5', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            (1.5, '2019-09-01'),
            ('1.5', '2019-09-01'),
        ],
        ids=['float-datetime', 'string-datetime', 'float-string', 'string-string']
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tfi = TFloatInst(value=value, timestamp=timestamp)
        assert str(tfi) == '1.5@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['1.5@2019-09-01', '2.5@2019-09-03'], TInterpolation.DISCRETE, False,
             '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00}'),
            (['1.5@2019-09-01', '2.5@2019-09-03'], TInterpolation.LINEAR, False,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),
            ([TFloatInst('1.5@2019-09-01'), TFloatInst('2.5@2019-09-03')], TInterpolation.DISCRETE, False,
             '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00}'),
            ([TFloatInst('1.5@2019-09-01'), TFloatInst('2.5@2019-09-03')], TInterpolation.LINEAR, False,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),
            (['1.5@2019-09-01', TFloatInst('2.5@2019-09-03')], TInterpolation.DISCRETE, False,
             '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00}'),
            (['1.5@2019-09-01', TFloatInst('2.5@2019-09-03')], TInterpolation.LINEAR, False,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),

            (['1.5@2019-09-01', '2@2019-09-02', '2.5@2019-09-03'], TInterpolation.LINEAR, True,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),
            ([TFloatInst('1.5@2019-09-01'), TFloatInst('2@2019-09-02'), TFloatInst('2.5@2019-09-03')],
             TInterpolation.LINEAR, True,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),
            (['1.5@2019-09-01', '2@2019-09-02', TFloatInst('2.5@2019-09-03')], TInterpolation.LINEAR, True,
             '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Linear', 'TFloatInst Discrete', 'TFloatInst Linear', 'Mixed Discrete',
             'Mixed Linear', 'String Linear Normalized', 'TFloatInst Linear Normalized',
             'Mixed Linear Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tfs = TFloatSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tfs) == expected
        assert tfs.interpolation() == interpolation

        tfs2 = TFloatSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tfs2) == expected
        assert tfs2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tfi, tfds, tfs, tfss, tfsts, tfstss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Stepwise Sequence', 'Stepwise SequenceSet']
    )
    def test_from_hexwkb_constructor(self, temporal):
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        'temporal',
        [tfi, tfds, tfs, tfss, tfsts, tfstss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Stepwise Sequence', 'Stepwise SequenceSet']
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTFloatOutputs(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, '1.5@2019-09-01 00:00:00+00'),
            (tfds, '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00}'),
            (tfs, '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00]'),
            (tfss, '{[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00], '
                   '[1.5@2019-09-03 00:00:00+00, 1.5@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 'TFloatInst(1.5@2019-09-01 00:00:00+00)'),
            (tfds, 'TFloatSeq({1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00})'),
            (tfs, 'TFloatSeq([1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00])'),
            (tfss, 'TFloatSeqSet({[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00], '
                   '[1.5@2019-09-03 00:00:00+00, 1.5@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, '1.5@2019-09-01 00:00:00+00'),
            (tfds, '{1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00}'),
            (tfs, '[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00]'),
            (tfss, '{[1.5@2019-09-01 00:00:00+00, 2.5@2019-09-02 00:00:00+00], '
                   '[1.5@2019-09-03 00:00:00+00, 1.5@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, '011B0001000000000000F83F00A01E4E71340200'),
            (tfds, '011B00060200000003000000000000F83F00A01E4E7134020000000000000004400000F66B85340200'),
            (tfs, '011B000E0200000003000000000000F83F00A01E4E7134020000000000000004400000F66B85340200'),
            (tfss, '011B000F020000000200000003000000000000F83F00A01E4E7134020000000000000004400000F66B85340200'
                '0200000003000000000000F83F0060CD8999340200000000000000F83F00207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, '{\n'
                  '   "type": "MovingFloat",\n'
                  '   "bbox": [\n'
                  '     1.5,\n'
                  '     1.5\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-01T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     1.5\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00"\n'
                  '   ],\n'
                  '   "interpolation": "None"\n'
                  ' }'),
            (tfds, '{\n'
                   '   "type": "MovingFloat",\n'
                   '   "bbox": [\n'
                   '     1.5,\n'
                   '     2.5\n'
                   '   ],\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-02T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "values": [\n'
                   '     1.5,\n'
                   '     2.5\n'
                   '   ],\n'
                   '   "datetimes": [\n'
                   '     "2019-09-01T00:00:00+00",\n'
                   '     "2019-09-02T00:00:00+00"\n'
                   '   ],\n'
                   '   "lower_inc": true,\n'
                   '   "upper_inc": true,\n'
                   '   "interpolation": "Discrete"\n'
                   ' }'),
            (tfs, '{\n'
                  '   "type": "MovingFloat",\n'
                  '   "bbox": [\n'
                  '     1.5,\n'
                  '     2.5\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-02T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     1.5,\n'
                  '     2.5\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00",\n'
                  '     "2019-09-02T00:00:00+00"\n'
                  '   ],\n'
                  '   "lower_inc": true,\n'
                  '   "upper_inc": true,\n'
                  '   "interpolation": "Linear"\n'
                  ' }'),
            (tfss, '{\n'
                   '   "type": "MovingFloat",\n'
                   '   "bbox": [\n'
                   '     1.5,\n'
                   '     2.5\n'
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
                   '         1.5,\n'
                   '         2.5\n'
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
                   '         1.5,\n'
                   '         1.5\n'
                   '       ],\n'
                   '       "datetimes": [\n'
                   '         "2019-09-03T00:00:00+00",\n'
                   '         "2019-09-05T00:00:00+00"\n'
                   '       ],\n'
                   '       "lower_inc": true,\n'
                   '       "upper_inc": true\n'
                   '     }\n'
                   '   ],\n'
                   '   "interpolation": "Linear"\n'
                   ' }')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_mfjson(self, temporal, expected):
        assert temporal.as_mfjson() == expected


class TestTFloatAccessors(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TInterpolation.NONE),
            (tfds, TInterpolation.DISCRETE),
            (tfs, TInterpolation.LINEAR),
            (tfss, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, {1.5}),
            (tfds, {1.5, 2.5}),
            (tfs, {1.5, 2.5}),
            (tfss, {1.5, 2.5})
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, [1.5]),
            (tfds, [1.5, 2.5]),
            (tfs, [1.5, 2.5]),
            (tfss, [1.5, 2.5, 1.5, 1.5])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1.5),
            (tfds, 1.5),
            (tfs, 1.5),
            (tfss, 1.5)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1.5),
            (tfds, 2.5),
            (tfs, 2.5),
            (tfss, 1.5)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1.5),
            (tfds, 1.5),
            (tfs, 1.5),
            (tfss, 1.5)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_value(self, temporal, expected):
        assert temporal.min_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1.5),
            (tfds, 2.5),
            (tfs, 2.5),
            (tfss, 2.5)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_value(self, temporal, expected):
        assert temporal.max_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1.5),
            (tfds, 1.5),
            (tfs, 1.5),
            (tfss, 1.5)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tfds, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
            (tfs, PeriodSet('{[2019-09-01, 2019-09-02]}')),
            (tfss, PeriodSet('{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, timedelta()),
            (tfds, timedelta()),
            (tfs, timedelta(days=1)),
            (tfss, timedelta(days=3)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, timedelta()),
            (tfds, timedelta(days=1)),
            (tfs, timedelta(days=1)),
            (tfss, timedelta(days=4)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, Period('[2019-09-01, 2019-09-01]')),
            (tfds, Period('[2019-09-01, 2019-09-02]')),
            (tfs, Period('[2019-09-01, 2019-09-02]')),
            (tfss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, Period('[2019-09-01, 2019-09-01]')),
            (tfds, Period('[2019-09-01, 2019-09-02]')),
            (tfs, Period('[2019-09-01, 2019-09-02]')),
            (tfss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1),
            (tfds, 2),
            (tfs, 2),
            (tfss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, tfi),
            (tfds, tfi),
            (tfs, tfi),
            (tfss, tfi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, tfi),
            (tfds, TFloatInst('2.5@2019-09-02')),
            (tfs, TFloatInst('2.5@2019-09-02')),
            (tfss, TFloatInst('1.5@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, tfi),
            (tfds, TFloatInst('2.5@2019-09-02')),
            (tfs, TFloatInst('2.5@2019-09-02')),
            (tfss, TFloatInst('2.5@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, tfi),
            (tfds, tfi),
            (tfs, tfi),
            (tfss, tfi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tfi, 0, tfi),
            (tfds, 1, TFloatInst('2.5@2019-09-02')),
            (tfs, 1, TFloatInst('2.5@2019-09-02')),
            (tfss, 2, TFloatInst('1.5@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, [tfi]),
            (tfds, [tfi, TFloatInst('2.5@2019-09-02')]),
            (tfs, [tfi, TFloatInst('2.5@2019-09-02')]),
            (tfss, [tfi, TFloatInst('2.5@2019-09-02'), TFloatInst('1.5@2019-09-03'), TFloatInst('1.5@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1),
            (tfds, 2),
            (tfs, 2),
            (tfss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tfds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tfs, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tfss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tfds, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tfs, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tfss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tfi, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tfds, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tfs, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tfss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (tfds, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tfs, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                   datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tfss, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
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
            (tfds, [TFloatSeq('[1.5@2019-09-01]'), TFloatSeq('[2.5@2019-09-02]')]),
            (tfs, [TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')]),
            (tfss,
             [TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]'),
              TFloatSeq('[1.5@2019-09-03, 1.5@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfds, True),
            (tfs, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_upper_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected
        assert temporal.upper_inc() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, 1307112078),
            (tfds, 1935376725),
            (tfs, 1935376725),
            (tfss, 4247071962)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected


class TestTFloatEverAlwaysOperations(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, True),
            (tfds, False),
            (tfs, False),
            (tfss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_1_5(self, temporal, expected):
        assert temporal.always_equal(1.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, False),
            (tfds, False),
            (tfs, False),
            (tfss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_2_5(self, temporal, expected):
        assert temporal.always_equal(2.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, True),
            (tfds, True),
            (tfs, True),
            (tfss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_1_5(self, temporal, expected):
        assert temporal.ever_equal(1.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, False),
            (tfds, True),
            (tfs, True),
            (tfss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_2_5(self, temporal, expected):
        assert temporal.ever_equal(2.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, False),
            (tfds, False),
            (tfs, False),
            (tfss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_1_5(self, temporal, expected):
        assert temporal.never_equal(1.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, True),
            (tfds, False),
            (tfs, False),
            (tfss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_2_5(self, temporal, expected):
        assert temporal.never_equal(2.5) == expected


class TestTFloatArithmeticOperations(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')
    intarg = TIntSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')
    floatarg = TFloatSeq('[2.5@2019-09-01, 1.5@2019-09-02, 1.5@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('3.5@2019-09-01')),
            (tfds, TFloatSeq('{3.5@2019-09-01, 3.5@2019-09-02}')),
            (tfs, TFloatSeqSet('{[3.5@2019-09-01, 4.5@2019-09-02),[3.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{[3.5@2019-09-01, 4.5@2019-09-02),[3.5@2019-09-02],[2.5@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_add_temporal(self, temporal, expected):
        assert temporal.add(self.intarg) == expected
        assert temporal + self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('2.5@2019-09-01')),
            (tfds, TFloatSeq('{2.5@2019-09-01, 3.5@2019-09-02}')),
            (tfs, TFloatSeq('[2.5@2019-09-01, 3.5@2019-09-02]')),
            (tfss, TFloatSeqSet('{[2.5@2019-09-01, 3.5@2019-09-02],[2.5@2019-09-03, 2.5@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_add_int(self, temporal, expected):
        assert temporal.add(1) == expected
        assert (temporal + 1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('-0.5@2019-09-01')),
            (tfds, TFloatSeq('{-0.5@2019-09-01, 1.5@2019-09-02}')),
            (tfs, TFloatSeqSet('{[-0.5@2019-09-01, 0.5@2019-09-02), [1.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{[-0.5@2019-09-01, 0.5@2019-09-02), [1.5@2019-09-02],[0.5@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_sub_temporal(self, temporal, expected):
        assert temporal.sub(self.intarg) == expected
        assert temporal - self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('0.5@2019-09-01')),
            (tfds, TFloatSeq('{0.5@2019-09-01, 1.5@2019-09-02}')),
            (tfs, TFloatSeq('[0.5@2019-09-01, 1.5@2019-09-02]')),
            (tfss, TFloatSeqSet('{[0.5@2019-09-01, 1.5@2019-09-02],[0.5@2019-09-03, 0.5@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_sub_int(self, temporal, expected):
        assert temporal.sub(1) == expected
        assert (temporal - 1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('3@2019-09-01')),
            (tfds, TFloatSeq('{3@2019-09-01, 2.5@2019-09-02}')),
            (tfs, TFloatSeqSet('{[3@2019-09-01, 5@2019-09-02 00:00:00+00), [2.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{[3@2019-09-01, 5@2019-09-02 00:00:00+00), [2.5@2019-09-02],[1.5@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_mul_temporal(self, temporal, expected):
        assert temporal.mul(self.intarg) == expected
        assert temporal * self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('3@2019-09-01')),
            (tfds, TFloatSeq('{3@2019-09-01, 5@2019-09-02}')),
            (tfs, TFloatSeq('[3@2019-09-01, 5@2019-09-02]')),
            (tfss, TFloatSeqSet('{[3@2019-09-01, 5@2019-09-02],[3@2019-09-03, 3@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_mul_int(self, temporal, expected):
        assert temporal.mul(0) == TFloat.from_base_temporal(0, temporal)
        assert (temporal * 0) == TFloat.from_base_temporal(0, temporal)

        assert temporal.mul(1) == temporal
        assert (temporal * 1) == temporal

        assert temporal.mul(2) == expected
        assert (temporal * 2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('0.75@2019-09-01')),
            (tfds, TFloatSeq('{0.75@2019-09-01, 2.5@2019-09-02}')),
            (tfs, TFloatSeqSet('{[0.75@2019-09-01, 1.25@2019-09-02 00:00:00+00), [2.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{[0.75@2019-09-01, 1.25@2019-09-02 00:00:00+00), [2.5@2019-09-02], [1.5@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_temporal(self, temporal, expected):
        assert temporal.div(self.intarg) == expected
        assert temporal / self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('0.75@2019-09-01')),
            (tfds, TFloatSeq('{0.75@2019-09-01, 1.25@2019-09-02}')),
            (tfs, TFloatSeq('[0.75@2019-09-01, 1.25@2019-09-02]')),
            (tfss, TFloatSeqSet('{[0.75@2019-09-01, 1.25@2019-09-02],[0.75@2019-09-03, 0.75@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_div_int(self, temporal, expected):
        assert temporal.div(1) == temporal
        assert (temporal / 1) == temporal

        assert temporal.div(2) == expected
        assert (temporal / 2) == expected


class TestTFloatBooleanOperations(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')
    intarg = TIntSeq('[2@2019-09-01, 1@2019-09-02, 1@2019-09-03]')
    floatarg = TFloatSeq('[2.5@2019-09-01, 1.5@2019-09-02, 1.5@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('False@2019-09-01')),
            (tfds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tfs, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
              '(False@2019-09-01 12:00:00+00, False@2019-09-02]}')),
            (tfss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
              '(False@2019-09-01 12:00:00+00, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.floatarg) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('False@2019-09-01')),
            (tfds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tfs, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tfss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_int(self, temporal, expected):
        assert temporal.temporal_equal(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('False@2019-09-01')),
            (tfds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tfs, TBoolSeq('{[False@2019-09-01, True@2019-09-01 12:00:00], (False@2019-09-01 12:00:00, False@2019-09-02]}')),
            (tfss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00],'
              '(False@2019-09-01 12:00:00, False@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_int(self, temporal, expected):
        assert temporal.temporal_equal(2) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('True@2019-09-01')),
            (tfds, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tfs, TBoolSeq('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02]}')),
            (tfss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_float(self, temporal, expected):
        assert temporal.temporal_equal(1.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('False@2019-09-01')),
            (tfds, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tfs, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tfss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_float(self, temporal, expected):
        assert temporal.temporal_equal(2.5) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('True@2019-09-01')),
            (tfds, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tfs, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00+00],'
                 '(True@2019-09-01 12:00:00+00, True@2019-09-02]}')),
            (tfss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00+00],'
                 '(True@2019-09-01 12:00:00+00, True@2019-09-02],[False@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.floatarg) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('False@2019-09-01')),
            (tfds, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tfs, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tfss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_int(self, temporal, expected):
        assert temporal.temporal_not_equal(1) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TBoolInst('True@2019-09-01')),
            (tfds, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tfs, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00],'
                '(True@2019-09-01 12:00:00, True@2019-09-02]}')),
            (tfss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00],'
                '(True@2019-09-01 12:00:00, True@2019-09-02], [True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_int(self, temporal, expected):
        assert temporal.temporal_not_equal(2) == expected


class TestTFloatRestrictors(TestTFloat):
    tfi = TFloatInst('1.5@2019-09-01')
    tfds = TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')
    tfs = TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')
    tfss = TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tfi, instant, TFloatInst('1.5@2019-09-01')),
            (tfi, instant_set, TFloatInst('1.5@2019-09-01')),
            (tfi, sequence, TFloatInst('1.5@2019-09-01')),
            (tfi, sequence_set, TFloatInst('1.5@2019-09-01')),
            (tfi, 1.5, TFloatInst('1.5@2019-09-01')),
            (tfi, 2.5, None),

            (tfds, instant, TFloatSeq('{1.5@2019-09-01}')),
            (tfds, instant_set, TFloatSeq('{1.5@2019-09-01}')),
            (tfds, sequence, TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')),
            (tfds, sequence_set, TFloatSeq('{1.5@2019-09-01, 2.5@2019-09-02}')),
            (tfds, 1.5, TFloatSeq('{1.5@2019-09-01}')),
            (tfds, 2.5, TFloatSeq('{2.5@2019-09-02}')),

            (tfs, instant, TFloatSeq('[1.5@2019-09-01]')),
            (tfs, instant_set, TFloatSeq('{1.5@2019-09-01}')),
            (tfs, sequence, TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')),
            (tfs, sequence_set, TFloatSeq('[1.5@2019-09-01, 2.5@2019-09-02]')),
            (tfs, 1.5, TFloatSeq('[1.5@2019-09-01]')),
            (tfs, 2.5, TFloatSeq('[2.5@2019-09-02]')),

            (tfss, instant, TFloatSeqSet('[1.5@2019-09-01]')),
            (tfss, instant_set, TFloatSeq('{1.5@2019-09-01, 1.5@2019-09-03}')),
            (tfss, sequence, TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02]}')),
            (
                    tfss, sequence_set,
                    TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')),
            (tfss, 1.5, TFloatSeqSet('{[1.5@2019-09-01],[1.5@2019-09-03, 1.5@2019-09-05]}')),
            (tfss, 2.5, TFloatSeqSet('{[2.5@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-2-5', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-2-5', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-2-5', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-2-5']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('1.5@2019-09-01')),
            (tfds, TFloatSeq('{2.5@2019-09-02}')),
            (tfs, TFloatSeq('{[2.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{[2.5@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_max(self, temporal, expected):
        assert temporal.at_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, TFloatInst('1.5@2019-09-01')),
            (tfds, TFloatSeq('{1.5@2019-09-01}')),
            (tfs, TFloatSeq('{[1.5@2019-09-01]}')),
            (tfss, TFloatSeqSet('{[1.5@2019-09-01],[1.5@2019-09-03, 1.5@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_min(self, temporal, expected):
        assert temporal.at_min() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tfi, instant, None),
            (tfi, instant_set, None),
            (tfi, sequence, None),
            (tfi, sequence_set, None),
            (tfi, 1.5, None),
            (tfi, 2.5, TFloatInst('1.5@2019-09-01')),

            (tfds, instant, TFloatSeq('{2.5@2019-09-02}')),
            (tfds, instant_set, TFloatSeq('{2.5@2019-09-02}')),
            (tfds, sequence, None),
            (tfds, sequence_set, None),
            (tfds, 1.5, TFloatSeq('{2.5@2019-09-02}')),
            (tfds, 2.5, TFloatSeq('{1.5@2019-09-01}')),

            (tfs, instant, TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
            (tfs, instant_set, TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
            (tfs, sequence, None),
            (tfs, sequence_set, None),
            (tfs, 1.5, TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
            (tfs, 2.5, TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02)}')),

            (
                    tfss, instant,
                    TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}')),
            (tfss, instant_set,
             TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02],(1.5@2019-09-03, 1.5@2019-09-05]}')),
            (tfss, sequence, TFloatSeqSet('{[1.5@2019-09-03, 1.5@2019-09-05]}')),
            (tfss, sequence_set, None),
            (tfss, 1.5, TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
            (tfss, 2.5, TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02),[1.5@2019-09-03, 1.5@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-1-5',
             'Instant-2-5', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-1-5',
             'Discrete Sequence-2-5', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-1-5', 'Sequence-2-5', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-1-5',
             'SequenceSet-2-5']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, None),
            (tfds, TFloatSeq('{1.5@2019-09-01}')),
            (tfs, TFloatSeq('{[1.5@2019-09-01, 2.5@2019-09-02)}')),
            (tfss, TFloatSeqSet('{[1.5@2019-09-01, 2.5@2019-09-02), [1.5@2019-09-03, 1.5@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_max(self, temporal, expected):
        assert temporal.minus_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tfi, None),
            (tfds, TFloatSeq('{2.5@2019-09-02}')),
            (tfs, TFloatSeq('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
            (tfss, TFloatSeqSet('{(1.5@2019-09-01, 2.5@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected

