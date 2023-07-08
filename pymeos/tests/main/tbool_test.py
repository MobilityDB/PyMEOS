from datetime import datetime, timezone

import pytest

from pymeos import TIntInst, TBool, TBoolInst, TIntSeq, TBoolSeq, TIntSeqSet, TBoolSeqSet, TInterpolation, TimestampSet, \
    Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTBool(TestPyMEOS):
    pass


class TestTBoolConstructors(TestTBool):

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TIntInst('1@2000-01-01'), TBoolInst, TInterpolation.NONE),
            (TIntSeq('{1@2000-01-01, 0@2000-01-02}'), TBoolSeq, TInterpolation.DISCRETE),
            (TIntSeq('[1@2000-01-01, 0@2000-01-02]'), TBoolSeq, TInterpolation.STEPWISE),
            (TIntSeqSet('{[1@2000-01-01, 0@2000-01-02],[1@2000-01-03, 1@2000-01-05]}'),
             TBoolSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tb = TBool.from_base(True, source)
        assert isinstance(tb, type)
        assert tb.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TBoolInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TBoolSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TBoolSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TBoolSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
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


class TestTBoolAccessors(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbsd = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, {True}),
            (tbsd, {True, False}),
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
            (tbi, True),
            (tbsd, True),
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
            (tbsd, False),
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
            (tbsd, True),
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
            (tbsd, True),
            (tbs, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected


class TestTBoolEverAlwaysOperations(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbsd = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbsd, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_true(self, temporal, expected):
        assert temporal.always(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbsd, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_false(self, temporal, expected):
        assert temporal.always(False) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbsd, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_true(self, temporal, expected):
        assert temporal.ever(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbsd, True),
            (tbs, True),
            (tbss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_false(self, temporal, expected):
        assert temporal.ever(False) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, False),
            (tbsd, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_true(self, temporal, expected):
        assert temporal.never(True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, True),
            (tbsd, False),
            (tbs, False),
            (tbss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_false(self, temporal, expected):
        assert temporal.never(False) == expected


class TestTBoolBooleanOperations(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbsd = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')
    compared = TBoolSeq('[False@2019-09-01, True@2019-09-02, True@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('False@2019-09-01')),
            (tbsd, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
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
            (tbsd, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
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
        [tbi, tbsd, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_and_bool(self, temporal):
        assert temporal.temporal_and(True) == temporal
        assert (temporal & True) == temporal

        assert temporal.temporal_and(False) == TBool.from_base(False, temporal)
        assert (temporal & False) == TBool.from_base(False, temporal)

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbsd, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
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
        [tbi, tbsd, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_or_bool(self, temporal):
        assert temporal.temporal_or(True) == TBool.from_base(True, temporal)
        assert (temporal | True) == TBool.from_base(True, temporal)

        assert temporal.temporal_or(False) == temporal
        assert (temporal | False) == temporal

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('False@2019-09-01')),
            (tbsd, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tbs, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (tbss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.compared) == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbsd, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_bool(self, temporal):
        assert temporal.temporal_equal(True) == temporal

        assert temporal.temporal_equal(False) == ~temporal

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, TBoolInst('True@2019-09-01')),
            (tbsd, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[False@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.compared) == expected

    @pytest.mark.parametrize(
        'temporal',
        [tbi, tbsd, tbs, tbss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_bool(self, temporal):
        assert temporal.temporal_not_equal(True) == ~temporal

        assert temporal.temporal_not_equal(False) == temporal


class TestTBoolRestrictors(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbsd = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tbsd, PeriodSet('{[2019-09-01, 2019-09-01]}')),
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
            (tbsd, PeriodSet('{[2019-09-02, 2019-09-02]}')),
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
            (tbi, instant, TBoolInst('True@2019-09-01')),
            (tbi, instant_set, TBoolInst('True@2019-09-01')),
            (tbi, sequence, TBoolInst('True@2019-09-01')),
            (tbi, sequence_set, TBoolInst('True@2019-09-01')),
            (tbi, True, TBoolInst('True@2019-09-01')),
            (tbi, False, None),

            (tbsd, instant, TBoolSeq('{True@2019-09-01}')),
            (tbsd, instant_set, TBoolSeq('{True@2019-09-01}')),
            (tbsd, sequence, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tbsd, sequence_set, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tbsd, True, TBoolSeq('{True@2019-09-01}')),
            (tbsd, False, TBoolSeq('{False@2019-09-02}')),

            (tbs, instant, TBoolSeq('[True@2019-09-01]')),
            (tbs, instant_set, TBoolSeq('{True@2019-09-01}')),
            (tbs, sequence, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tbs, sequence_set, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tbs, True, TBoolSeq('[True@2019-09-01, True@2019-09-02)')),
            (tbs, False, TBoolSeq('[False@2019-09-02]')),

            (tbss, instant, TBoolSeqSet('[True@2019-09-01]')),
            (tbss, instant_set, TBoolSeq('{True@2019-09-01, True@2019-09-03}')),
            (tbss, sequence, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02]}')),
            (
                    tbss, sequence_set,
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
            (tbsd, TBoolSeq('{True@2019-09-01}')),
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
            (tbsd, TBoolSeq('{False@2019-09-02}')),
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
            (tbi, instant, None),
            (tbi, instant_set, None),
            (tbi, sequence, None),
            (tbi, sequence_set, None),
            (tbi, True, None),
            (tbi, False, TBoolInst('True@2019-09-01')),

            (tbsd, instant, TBoolSeq('{False@2019-09-02}')),
            (tbsd, instant_set, TBoolSeq('{False@2019-09-02}')),
            (tbsd, sequence, None),
            (tbsd, sequence_set, None),
            (tbsd, True, TBoolSeq('{False@2019-09-02}')),
            (tbsd, False, TBoolSeq('{True@2019-09-01}')),

            (tbs, instant, TBoolSeqSet('{(True@2019-09-01, False@2019-09-02]}')),
            (tbs, instant_set, TBoolSeqSet('{(True@2019-09-01, False@2019-09-02]}')),
            (tbs, sequence, None),
            (tbs, sequence_set, None),
            (tbs, True, TBoolSeqSet('{[False@2019-09-02]}')),
            (tbs, False, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02)}')),

            (
                    tbss, instant,
                    TBoolSeqSet('{(True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),
            (tbss, instant_set,
             TBoolSeqSet('{(True@2019-09-01, False@2019-09-02],(True@2019-09-03, True@2019-09-05]}')),
            (tbss, sequence, TBoolSeqSet('{[True@2019-09-03, True@2019-09-05]}')),
            (tbss, sequence_set, None),
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
            (tbsd, TBoolSeq('{False@2019-09-02}')),
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
            (tbsd, TBoolSeq('{True@2019-09-01}')),
            (tbs, TBoolSeq('[True@2019-09-01, True@2019-09-02)')),
            (tbss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02),[True@2019-09-03, True@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected


class TestTBoolOutputs(TestTBool):
    tbi = TBoolInst('True@2019-09-01')
    tbsd = TBoolSeq('{True@2019-09-01, False@2019-09-02}')
    tbs = TBoolSeq('[True@2019-09-01, False@2019-09-02]')
    tbss = TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tbi, 't@2019-09-01 00:00:00+00'),
            (tbsd, '{t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00}'),
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
            (tbsd, 'TBoolSeq({t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00})'),
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
            (tbsd, '{t@2019-09-01 00:00:00+00, f@2019-09-02 00:00:00+00}'),
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
            (tbsd, '0114000602000000030100A01E4E71340200000000F66B85340200'),
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
                  '  "type": "MovingBoolean",\n'
                  '  "period": {\n'
                  '    "begin": "2019-09-01T00:00:00+00",\n'
                  '    "end": "2019-09-01T00:00:00+00",\n'
                  '    "lower_inc": true,\n'
                  '    "upper_inc": true\n'
                  '  },\n'
                  '  "values": [\n'
                  '    true\n'
                  '  ],\n'
                  '  "datetimes": [\n'
                  '    "2019-09-01T00:00:00+00"\n'
                  '  ],\n'
                  '  "interpolation": "None"\n'
                  '}'),
            (tbsd, '{\n'
                   '  "type": "MovingBoolean",\n'
                   '  "period": {\n'
                   '    "begin": "2019-09-01T00:00:00+00",\n'
                   '    "end": "2019-09-02T00:00:00+00",\n'
                   '    "lower_inc": true,\n'
                   '    "upper_inc": true\n'
                   '  },\n'
                   '  "values": [\n'
                   '    true,\n'
                   '    false\n'
                   '  ],\n'
                   '  "datetimes": [\n'
                   '    "2019-09-01T00:00:00+00",\n'
                   '    "2019-09-02T00:00:00+00"\n'
                   '  ],\n'
                   '  "lower_inc": true,\n'
                   '  "upper_inc": true,\n'
                   '  "interpolation": "Discrete"\n'
                   '}'),
            (tbs, '{\n'
                  '  "type": "MovingBoolean",\n'
                  '  "period": {\n'
                  '    "begin": "2019-09-01T00:00:00+00",\n'
                  '    "end": "2019-09-02T00:00:00+00",\n'
                  '    "lower_inc": true,\n'
                  '    "upper_inc": true\n'
                  '  },\n'
                  '  "values": [\n'
                  '    true,\n'
                  '    false\n'
                  '  ],\n'
                  '  "datetimes": [\n'
                  '    "2019-09-01T00:00:00+00",\n'
                  '    "2019-09-02T00:00:00+00"\n'
                  '  ],\n'
                  '  "lower_inc": true,\n'
                  '  "upper_inc": true,\n'
                  '  "interpolation": "Step"\n'
                  '}'),
            (tbss, '{\n'
                   '  "type": "MovingBoolean",\n'
                   '  "period": {\n'
                   '    "begin": "2019-09-01T00:00:00+00",\n'
                   '    "end": "2019-09-05T00:00:00+00",\n'
                   '    "lower_inc": true,\n'
                   '    "upper_inc": true\n'
                   '  },\n'
                   '  "sequences": [\n'
                   '    {\n'
                   '      "values": [\n'
                   '        true,\n'
                   '        false\n'
                   '      ],\n'
                   '      "datetimes": [\n'
                   '        "2019-09-01T00:00:00+00",\n'
                   '        "2019-09-02T00:00:00+00"\n'
                   '      ],\n'
                   '      "lower_inc": true,\n'
                   '      "upper_inc": true\n'
                   '    },\n'
                   '    {\n'
                   '      "values": [\n'
                   '        true,\n'
                   '        true\n'
                   '      ],\n'
                   '      "datetimes": [\n'
                   '        "2019-09-03T00:00:00+00",\n'
                   '        "2019-09-05T00:00:00+00"\n'
                   '      ],\n'
                   '      "lower_inc": true,\n'
                   '      "upper_inc": true\n'
                   '    }\n'
                   '  ],\n'
                   '  "interpolation": "Step"\n'
                   '}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_mfjson(self, temporal, expected):
        assert temporal.as_mfjson() == expected
