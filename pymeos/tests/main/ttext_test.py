from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TText, TTextInst, TTextSeq, TTextSeqSet, \
    TInt, TIntInst, TIntSeq, TIntSeqSet, TInterpolation, TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTText(TestPyMEOS):
    pass


class TestTTextConstructors(TestTText):

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TIntInst('1@2000-01-01'), TTextInst, TInterpolation.NONE),
            (TIntSeq('{1@2000-01-01, 2@2000-01-02}'), TTextSeq, TInterpolation.DISCRETE),
            (TIntSeq('[1@2000-01-01, 2@2000-01-02]'), TTextSeq, TInterpolation.STEPWISE),
            (TIntSeqSet('{[1@2000-01-01, 2@2000-01-02],[1@2000-01-03, 1@2000-01-05]}'),
             TTextSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tt = TText.from_base('AAA', source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TTextInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TTextSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TTextSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TTextSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tt = TText.from_base_time('AAA', source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('AAA@2019-09-01', TTextInst, TInterpolation.NONE, 'AAA@2019-09-01 00:00:00+00'),
            ('{AAA@2019-09-01, BBB@2019-09-02}', TTextSeq, TInterpolation.DISCRETE,
             '{AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00}'),
            ('[AAA@2019-09-01, BBB@2019-09-02]', TTextSeq, TInterpolation.STEPWISE,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00]'),
            ('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}', TTextSeqSet,
             TInterpolation.STEPWISE, '{[AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00], '
                                      '[AAA@2019-09-03 00:00:00+00, AAA@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tt = type(source)
        assert isinstance(tt, type)
        assert tt.interpolation() == interpolation
        assert str(tt) == expected

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[AAA@2019-09-01, AAA@2019-09-02, AAA@2019-09-03, BBB@2019-09-05]', TTextSeq,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-05 00:00:00+00]'),
            ('{[AAA@2019-09-01, AAA@2019-09-02, AAA@2019-09-03, BBB@2019-09-05],'
             '[AAA@2019-09-07, AAA@2019-09-08, AAA@2019-09-09]}', TTextSeqSet,
             '{[AAA@2019-09-01 00:00:00+00, BBB@2019-09-05 00:00:00+00], '
             '[AAA@2019-09-07 00:00:00+00, AAA@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tt = type(source, normalize=1)
        assert isinstance(tt, type)
        assert str(tt) == expected

    @pytest.mark.parametrize(
        'value, timestamp',
        [
            ('AAA', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('AAA', '2019-09-01'),
        ],
        ids=['string', 'datetime']
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tti = TTextInst(value=value, timestamp=timestamp)
        assert str(tti) == 'AAA@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['AAA@2019-09-01', 'BBB@2019-09-03'], TInterpolation.DISCRETE, False,
             '{AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00}'),
            (['AAA@2019-09-01', 'BBB@2019-09-03'], TInterpolation.STEPWISE, False,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),
            ([TTextInst('AAA@2019-09-01'), TTextInst('BBB@2019-09-03')], TInterpolation.DISCRETE, False,
             '{AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00}'),
            ([TTextInst('AAA@2019-09-01'), TTextInst('BBB@2019-09-03')], TInterpolation.STEPWISE, False,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),
            (['AAA@2019-09-01', TTextInst('BBB@2019-09-03')], TInterpolation.DISCRETE, False,
             '{AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00}'),
            (['AAA@2019-09-01', TTextInst('BBB@2019-09-03')], TInterpolation.STEPWISE, False,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),

            (['AAA@2019-09-01', 'AAA@2019-09-02', 'BBB@2019-09-03'], TInterpolation.STEPWISE, True,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),
            ([TTextInst('AAA@2019-09-01'), TTextInst('AAA@2019-09-02'), TTextInst('BBB@2019-09-03')],
             TInterpolation.STEPWISE, True,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),
            (['AAA@2019-09-01', 'AAA@2019-09-02', TTextInst('BBB@2019-09-03')], TInterpolation.STEPWISE, True,
             '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Stepwise', 'TTextInst Discrete', 'TTextInst Stepwise', 'Mixed Discrete',
             'Mixed Stepwise', 'String Stepwise Normalized', 'TTextInst Stepwise Normalized',
             'Mixed Stepwise Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tts = TTextSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tts) == expected
        assert tts.interpolation() == interpolation

        tts2 = TTextSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tts2) == expected
        assert tts2.interpolation() == interpolation


class TestTTextAccessors(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TInterpolation.NONE),
            (ttsd, TInterpolation.DISCRETE),
            (tts, TInterpolation.STEPWISE),
            (ttss, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, {'AAA'}),
            (ttsd, {'AAA', 'BBB'}),
            (tts, {'AAA', 'BBB'}),
            (ttss, {'AAA', 'BBB'})
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, ['AAA']),
            (ttsd, ['AAA', 'BBB']),
            (tts, ['AAA', 'BBB']),
            (ttss, ['AAA', 'BBB', 'AAA', 'AAA'])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA'),
            (ttsd, 'AAA'),
            (tts, 'AAA'),
            (ttss, 'AAA')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA'),
            (ttsd, 'BBB'),
            (tts, 'BBB'),
            (ttss, 'AAA')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA'),
            (ttsd, 'AAA'),
            (tts, 'AAA'),
            (ttss, 'AAA')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_value(self, temporal, expected):
        assert temporal.min_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA'),
            (ttsd, 'BBB'),
            (tts, 'BBB'),
            (ttss, 'BBB')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_value(self, temporal, expected):
        assert temporal.max_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA'),
            (ttsd, 'AAA'),
            (tts, 'AAA'),
            (ttss, 'AAA')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (ttsd, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
            (tts, PeriodSet('{[2019-09-01, 2019-09-02]}')),
            (ttss, PeriodSet('{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, timedelta()),
            (ttsd, timedelta()),
            (tts, timedelta(days=1)),
            (ttss, timedelta(days=3)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, timedelta()),
            (ttsd, timedelta(days=1)),
            (tts, timedelta(days=1)),
            (ttss, timedelta(days=4)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, Period('[2019-09-01, 2019-09-01]')),
            (ttsd, Period('[2019-09-01, 2019-09-02]')),
            (tts, Period('[2019-09-01, 2019-09-02]')),
            (ttss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, Period('[2019-09-01, 2019-09-01]')),
            (ttsd, Period('[2019-09-01, 2019-09-02]')),
            (tts, Period('[2019-09-01, 2019-09-02]')),
            (ttss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 1),
            (ttsd, 2),
            (tts, 2),
            (ttss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, tti),
            (ttsd, tti),
            (tts, tti),
            (ttss, tti),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, tti),
            (ttsd, TTextInst('BBB@2019-09-02')),
            (tts, TTextInst('BBB@2019-09-02')),
            (ttss, TTextInst('AAA@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, tti),
            (ttsd, TTextInst('BBB@2019-09-02')),
            (tts, TTextInst('BBB@2019-09-02')),
            (ttss, TTextInst('BBB@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, tti),
            (ttsd, tti),
            (tts, tti),
            (ttss, tti),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tti, 0, tti),
            (ttsd, 1, TTextInst('BBB@2019-09-02')),
            (tts, 1, TTextInst('BBB@2019-09-02')),
            (ttss, 2, TTextInst('AAA@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, [tti]),
            (ttsd, [tti, TTextInst('BBB@2019-09-02')]),
            (tts, [tti, TTextInst('BBB@2019-09-02')]),
            (ttss, [tti, TTextInst('BBB@2019-09-02'), TTextInst('AAA@2019-09-03'), TTextInst('AAA@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 1),
            (ttsd, 2),
            (tts, 2),
            (ttss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttsd, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tts, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttsd, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tts, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (ttss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tti, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (ttsd, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tts, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (ttss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (ttsd, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tts, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                   datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (ttss, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
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
            (ttsd, [TTextSeq('[AAA@2019-09-01]'), TTextSeq('[BBB@2019-09-02]')]),
            (tts, [TTextSeq('[AAA@2019-09-01, AAA@2019-09-02)'),
                   TTextSeq('[BBB@2019-09-02]')]),
            (ttss,
             [TTextSeq('[AAA@2019-09-01, AAA@2019-09-02)'),
              TTextSeq('[BBB@2019-09-02]'),
              TTextSeq('[AAA@2019-09-03, AAA@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (ttsd, True),
            (tts, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected


class TestTTextEverAlwaysOperations(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, True),
            (ttsd, False),
            (tts, False),
            (ttss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_AAA(self, temporal, expected):
        assert temporal.always('AAA') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, False),
            (ttsd, False),
            (tts, False),
            (ttss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_BBB(self, temporal, expected):
        assert temporal.always('BBB') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, True),
            (ttsd, True),
            (tts, True),
            (ttss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_AAA(self, temporal, expected):
        assert temporal.ever('AAA') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, False),
            (ttsd, True),
            (tts, True),
            (ttss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_BBB(self, temporal, expected):
        assert temporal.ever('BBB') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, False),
            (ttsd, False),
            (tts, False),
            (ttss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_AAA(self, temporal, expected):
        assert temporal.never('AAA') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, True),
            (ttsd, False),
            (tts, False),
            (ttss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_BBB(self, temporal, expected):
        assert temporal.never('BBB') == expected


class TestTTextTextOperations(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')
    argument = TTextSeq('[BBB@2019-09-01, AAA@2019-09-02, AAA@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TTextInst('AAABBB@2019-09-01')),
            (ttsd, TTextSeq('{AAABBB@2019-09-01, BBBAAA@2019-09-02}')),
            (tts, TTextSeq('[AAABBB@2019-09-01, BBBAAA@2019-09-02]')),
            (ttss, TTextSeqSet('{[AAABBB@2019-09-01, BBBAAA@2019-09-02],[AAAAAA@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_concat_temporal(self, temporal, expected):
        assert temporal.temporal_add(self.intarg) == expected
        assert temporal + self.intarg == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TTextInst('AAABBB@2019-09-01')),
            (ttsd, TTextSeq('{AAABBB@2019-09-01, BBBBBB@2019-09-02}')),
            (tts, TTextSeq('[AAABBB@2019-09-01, BBBBBB@2019-09-02]')),
            (ttss, TTextSeqSet('{[AAABBB@2019-09-01, BBBBBB@2019-09-02],[AAABBB@2019-09-03, AAABBB@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_concat_text(self, temporal, expected):
        assert temporal.concatenate('BBB') == expected
        assert (temporal + 'BBB') == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TTextInst('aaa@2019-09-01')),
            (ttsd, TTextSeq('{aaa@2019-09-01, bbb@2019-09-02}')),
            (tts, TTextSeq('[aaa@2019-09-01, bbb@2019-09-02]')),
            (ttss, TTextSeqSet('{[aaa@2019-09-01, bbb@2019-09-02],[aaa@2019-09-03, aaa@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_lowercase(self, temporal, expected):
        assert temporal.temporal_lowercase() == expected

    @pytest.mark.parametrize(
        'temporal',
        [tti, ttsd, tts, ttss],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_uppercase(self, temporal):
        assert temporal.temporal_uppercase() == temporal


class TestTTextBooleanOperations(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')
    argument = TTextSeq('[BBB@2019-09-01, AAA@2019-09-02, AAA@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TBoolInst('False@2019-09-01')),
            (ttsd, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tts, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (ttss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TBoolInst('True@2019-09-01')),
            (ttsd, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tts, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (ttss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_int(self, temporal, expected):
        assert temporal.temporal_equal('AAA') == expected

        assert temporal.temporal_equal('BBB') == ~expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TBoolInst('True@2019-09-01')),
            (ttsd, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tts, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (ttss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TBoolInst('False@2019-09-01')),
            (ttsd, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tts, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (ttss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_int(self, temporal, expected):
        assert temporal.temporal_not_equal(1) == expected

        assert temporal.temporal_not_equal(2) == ~expected


class TestTTextRestrictors(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tti, instant, TTextInst('AAA@2019-09-01')),
            (tti, instant_set, TTextInst('AAA@2019-09-01')),
            (tti, sequence, TTextInst('AAA@2019-09-01')),
            (tti, sequence_set, TTextInst('AAA@2019-09-01')),
            (tti, 'AAA', TTextInst('AAA@2019-09-01')),
            (tti, 'BBB', None),

            (ttsd, instant, TTextSeq('{AAA@2019-09-01}')),
            (ttsd, instant_set, TTextSeq('{AAA@2019-09-01}')),
            (ttsd, sequence, TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')),
            (ttsd, sequence_set, TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')),
            (ttsd, 'AAA', TTextSeq('{AAA@2019-09-01}')),
            (ttsd, 'BBB', TTextSeq('{BBB@2019-09-02}')),

            (tts, instant, TTextSeq('[AAA@2019-09-01]')),
            (tts, instant_set, TTextSeq('{AAA@2019-09-01}')),
            (tts, sequence, TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')),
            (tts, sequence_set, TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')),
            (tts, 'AAA', TTextSeq('[AAA@2019-09-01, AAA@2019-09-02)')),
            (tts, 'BBB', TTextSeq('[BBB@2019-09-02]')),

            (ttss, instant, TTextSeqSet('[AAA@2019-09-01]')),
            (ttss, instant_set, TTextSeq('{AAA@2019-09-01, AAA@2019-09-03}')),
            (ttss, sequence, TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02]}')),
            (
                    ttss, sequence_set,
                    TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')),
            (ttss, 'AAA', TTextSeqSet('{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}')),
            (ttss, 'BBB', TTextSeqSet('{[BBB@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-BBB', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-BBB', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-BBB', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-BBB']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TTextInst('AAA@2019-09-01')),
            (ttsd, TTextSeq('{AAA@2019-09-01}')),
            (tts, TTextSeq('[AAA@2019-09-01, AAA@2019-09-02)')),
            (ttss, TTextSeqSet('{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_max(self, temporal, expected):
        assert temporal.at_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, TTextInst('AAA@2019-09-01')),
            (ttsd, TTextSeq('{BBB@2019-09-02}')),
            (tts, TTextSeq('[BBB@2019-09-02]')),
            (ttss, TTextSeqSet('{[BBB@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_at_min(self, temporal, expected):
        assert temporal.at_min() == expected

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tti, instant, None),
            (tti, instant_set, None),
            (tti, sequence, None),
            (tti, sequence_set, None),
            (tti, 'AAA', None),
            (tti, 'BBB', TTextInst('AAA@2019-09-01')),

            (ttsd, instant, TTextSeq('{BBB@2019-09-02}')),
            (ttsd, instant_set, TTextSeq('{BBB@2019-09-02}')),
            (ttsd, sequence, None),
            (ttsd, sequence_set, None),
            (ttsd, 'AAA', TTextSeq('{BBB@2019-09-02}')),
            (ttsd, 'BBB', TTextSeq('{AAA@2019-09-01}')),

            (tts, instant, TTextSeqSet('{(AAA@2019-09-01, BBB@2019-09-02]}')),
            (tts, instant_set, TTextSeqSet('{(AAA@2019-09-01, BBB@2019-09-02]}')),
            (tts, sequence, None),
            (tts, sequence_set, None),
            (tts, 'AAA', TTextSeqSet('{[BBB@2019-09-02]}')),
            (tts, 'BBB', TTextSeqSet('{[AAA@2019-09-01, AAA@2019-09-02)}')),

            (
                    ttss, instant,
                    TTextSeqSet('{(AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')),
            (ttss, instant_set,
             TTextSeqSet('{(AAA@2019-09-01, BBB@2019-09-02],(AAA@2019-09-03, AAA@2019-09-05]}')),
            (ttss, sequence, TTextSeqSet('{[AAA@2019-09-03, AAA@2019-09-05]}')),
            (ttss, sequence_set, None),
            (ttss, 'AAA', TTextSeqSet('{[BBB@2019-09-02]}')),
            (ttss, 'BBB', TTextSeqSet('{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-AAA',
             'Instant-BBB', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-AAA',
             'Discrete Sequence-BBB', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-AAA', 'Sequence-BBB', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-AAA',
             'SequenceSet-BBB']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, None),
            (ttsd, TTextSeq('{BBB@2019-09-02}')),
            (tts, TTextSeq('[BBB@2019-09-02]')),
            (ttss, TTextSeqSet('{[BBB@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_max(self, temporal, expected):
        assert temporal.minus_max() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, None),
            (ttsd, TTextSeq('{AAA@2019-09-01}')),
            (tts, TTextSeq('[AAA@2019-09-01, AAA@2019-09-02)')),
            (ttss, TTextSeqSet('{[AAA@2019-09-01, AAA@2019-09-02),[AAA@2019-09-03, AAA@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_minus_min(self, temporal, expected):
        assert temporal.minus_min() == expected


class TestTTextOutputs(TestTText):
    tti = TTextInst('AAA@2019-09-01')
    ttsd = TTextSeq('{AAA@2019-09-01, BBB@2019-09-02}')
    tts = TTextSeq('[AAA@2019-09-01, BBB@2019-09-02]')
    ttss = TTextSeqSet('{[AAA@2019-09-01, BBB@2019-09-02],[AAA@2019-09-03, AAA@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'AAA@2019-09-01 00:00:00+00'),
            (ttsd, '{AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00}'),
            (tts, '[AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00]'),
            (ttss, '{[AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00], '
                   '[AAA@2019-09-03 00:00:00+00, AAA@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, 'TTextInst(AAA@2019-09-01 00:00:00+00)'),
            (ttsd, 'TTextSeq({AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00})'),
            (tts, 'TTextSeq([AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00])'),
            (ttss, 'TTextSeqSet({[AAA@2019-09-01 00:00:00+00, BBB@2019-09-02 00:00:00+00], '
                   '[AAA@2019-09-03 00:00:00+00, AAA@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, '"AAA"@2019-09-01 00:00:00+00'),
            (ttsd, '{"AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00}'),
            (tts, '["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00]'),
            (ttss, '{["AAA"@2019-09-01 00:00:00+00, "BBB"@2019-09-02 00:00:00+00], '
                   '["AAA"@2019-09-03 00:00:00+00, "AAA"@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, '011400010100A01E4E71340200'),
            (ttsd, '0114000602000000030100A01E4E71340200000000F66B85340200'),
            (tts, '0114000A02000000030100A01E4E71340200000000F66B85340200'),
            (ttss, '0114000B0200000002000000030100A01E4E71340200000000F'
                   '66B853402000200000003010060CD89993402000100207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tti, '{\n'
                  '   "type": "MovingText",\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-01T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     "AAA"\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00"\n'
                  '   ],\n'
                  '   "interpolation": "None"\n'
                  ' }'),
            (ttsd, '{\n'
                   '   "type": "MovingText",\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-02T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "values": [\n'
                   '     "AAA",\n'
                   '     "BBB"\n'
                   '   ],\n'
                   '   "datetimes": [\n'
                   '     "2019-09-01T00:00:00+00",\n'
                   '     "2019-09-02T00:00:00+00"\n'
                   '   ],\n'
                   '   "lower_inc": true,\n'
                   '   "upper_inc": true,\n'
                   '   "interpolation": "Discrete"\n'
                   ' }'),
            (tts, '{\n'
                  '   "type": "MovingText",\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-02T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "values": [\n'
                  '     "AAA",\n'
                  '     "BBB"\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00",\n'
                  '     "2019-09-02T00:00:00+00"\n'
                  '   ],\n'
                  '   "lower_inc": true,\n'
                  '   "upper_inc": true,\n'
                  '   "interpolation": "Step"\n'
                  ' }'),
            (ttss, '{\n'
                   '   "type": "MovingText",\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-05T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "sequences": [\n'
                   '     {\n'
                   '       "values": [\n'
                   '         "AAA",\n'
                   '         "BBB"\n'
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
                   '         "AAA",\n'
                   '         "AAA"\n'
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
