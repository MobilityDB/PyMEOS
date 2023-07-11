from datetime import datetime, timezone, timedelta

import pytest

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, TGeomPoint, \
    TGeomPointInst, TGeomPointSeq, TGeomPointSeqSet, TInterpolation, TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTGeomPoint(TestPyMEOS):
    pass


class TestTGeomPointConstructors(TestTGeomPoint):

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1.5@2000-01-01'), TGeomPointInst, TInterpolation.NONE),
            (TFloatSeq('{1.5@2000-01-01, 0.5@2000-01-02}'), TGeomPointSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1.5@2000-01-01, 0.5@2000-01-02]'), TGeomPointSeq, TInterpolation.STEPWISE),
            (TFloatSeqSet('{[1.5@2000-01-01, 0.5@2000-01-02],[1.5@2000-01-03, 1.5@2000-01-05]}'),
             TGeomPointSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tp = TGeomPoint.from_base(1, source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TGeomPointInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TGeomPointSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TGeomPointSeq, TInterpolation.STEPWISE),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TGeomPointSeqSet, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tp = TGeomPoint.from_base_time(Point(1,1), source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('Point(1 1)@2019-09-01', TGeomPointInst, TInterpolation.NONE, 'Point(1 1)@2019-09-01 00:00:00+00'),
            ('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}', TGeomPointSeq, TInterpolation.DISCRETE,
             '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00}'),
            ('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]', TGeomPointSeq, TInterpolation.STEPWISE,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}', TGeomPointSeqSet,
             TInterpolation.STEPWISE, '{[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00], '
                                      '[Point(1 1)@2019-09-03 00:00:00+00, Point(1 1)@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tp = type(source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation
        assert str(tp) == expected

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03, Point(2 2)@2019-09-05]', TGeomPointSeq,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-05 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03, Point(2 2)@2019-09-05],'
             '[Point(1 1)@2019-09-07, Point(1 1)@2019-09-08, Point(1 1)@2019-09-09]}', TGeomPointSeqSet,
             '{[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-05 00:00:00+00], '
             '[Point(1 1)@2019-09-07 00:00:00+00, Point(1 1)@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tp = type(source, normalize=1)
        assert isinstance(tp, type)
        assert str(tp) == expected

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
        tpi = TGeomPointInst(value=value, timestamp=timestamp)
        assert str(tpi) == 'Point(1 1)@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.DISCRETE, False,
             '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.STEPWISE, False,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00}'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.STEPWISE, False,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.STEPWISE, False,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),

            (['Point(1 1)@2019-09-01', 'Point(1 1)@2019-09-02', 'Point(2 2)@2019-09-03'], TInterpolation.STEPWISE, True,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(1 1)@2019-09-02'), TGeomPointInst('Point(2 2)@2019-09-03')],
             TInterpolation.STEPWISE, True,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', 'Point(1 1)@2019-09-02', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.STEPWISE, True,
             '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Stepwise', 'TGeomPointInst Discrete', 'TGeomPointInst Stepwise', 'Mixed Discrete',
             'Mixed Stepwise', 'String Stepwise Normalized', 'TGeomPointInst Stepwise Normalized',
             'Mixed Stepwise Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tps = TGeomPointSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps) == expected
        assert tps.interpolation() == interpolation

        tps2 = TGeomPointSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps2) == expected
        assert tps2.interpolation() == interpolation


class TestTGeomPointAccessors(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpsd = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TInterpolation.NONE),
            (tpsd, TInterpolation.DISCRETE),
            (tps, TInterpolation.STEPWISE),
            (tpss, TInterpolation.STEPWISE)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, {Point(1,1)}),
            (tpsd, {Point(1,1), Point(2,2)}),
            (tps, {Point(1,1), Point(2,2)}),
            (tpss, {Point(1,1), Point(2,2)})
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_set(self, temporal, expected):
        assert temporal.value_set() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, [Point(1,1)]),
            (tpsd, [Point(1,1), Point(2,2)]),
            (tps, [Point(1,1), Point(2,2)]),
            (tpss, [Point(1,1), Point(2,2), Point(1,1), Point(1,1)])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Point(1,1)),
            (tpsd, Point(1,1)),
            (tps, Point(1,1)),
            (tpss, Point(1,1))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_value(self, temporal, expected):
        assert temporal.start_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Point(1,1)),
            (tpsd, Point(2,2)),
            (tps, Point(2,2)),
            (tpss, Point(1,1))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_value(self, temporal, expected):
        assert temporal.end_value() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Point(1,1)),
            (tpsd, Point(1,1)),
            (tps, Point(1,1)),
            (tpss, Point(1,1))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_value_at_timestamp(self, temporal, expected):
        assert temporal.value_at_timestamp(datetime(2019, 9, 1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, PeriodSet('{[2019-09-01, 2019-09-01]}')),
            (tpsd, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
            (tps, PeriodSet('{[2019-09-01, 2019-09-02]}')),
            (tpss, PeriodSet('{[2019-09-01, 2019-09-02], [2019-09-03, 2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_time(self, temporal, expected):
        assert temporal.time() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, timedelta()),
            (tpsd, timedelta()),
            (tps, timedelta(days=1)),
            (tpss, timedelta(days=3)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration(self, temporal, expected):
        assert temporal.duration() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, timedelta()),
            (tpsd, timedelta(days=1)),
            (tps, timedelta(days=1)),
            (tpss, timedelta(days=4)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_duration_ignoring_gaps(self, temporal, expected):
        assert temporal.duration(ignore_gaps=True) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Period('[2019-09-01, 2019-09-01]')),
            (tpsd, Period('[2019-09-01, 2019-09-02]')),
            (tps, Period('[2019-09-01, 2019-09-02]')),
            (tpss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_period(self, temporal, expected):
        assert temporal.period() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Period('[2019-09-01, 2019-09-01]')),
            (tpsd, Period('[2019-09-01, 2019-09-02]')),
            (tps, Period('[2019-09-01, 2019-09-02]')),
            (tpss, Period('[2019-09-01, 2019-09-05]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timespan(self, temporal, expected):
        assert temporal.timespan() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 1),
            (tpsd, 2),
            (tps, 2),
            (tpss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_instants(self, temporal, expected):
        assert temporal.num_instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpsd, tpi),
            (tps, tpi),
            (tpss, tpi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_instant(self, temporal, expected):
        assert temporal.start_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpsd, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tps, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tpss, TGeomPointInst('Point(1 1)@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpsd, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tps, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tpss, TGeomPointInst('Point(2 2)@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpsd, tpi),
            (tps, tpi),
            (tpss, tpi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tpi, 0, tpi),
            (tpsd, 1, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tps, 1, TGeomPointInst('Point(2 2)@2019-09-02')),
            (tpss, 2, TGeomPointInst('Point(1 1)@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, [tpi]),
            (tpsd, [tpi, TGeomPointInst('Point(2 2)@2019-09-02')]),
            (tps, [tpi, TGeomPointInst('Point(2 2)@2019-09-02')]),
            (tpss, [tpi, TGeomPointInst('Point(2 2)@2019-09-02'), TGeomPointInst('Point(1 1)@2019-09-03'), TGeomPointInst('Point(1 1)@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 1),
            (tpsd, 2),
            (tps, 2),
            (tpss, 4),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_num_timestamps(self, temporal, expected):
        assert temporal.num_timestamps() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tpsd, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tps, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tpss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_start_timestamp(self, temporal, expected):
        assert temporal.start_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tpsd, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tps, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tpss, datetime(year=2019, month=9, day=5, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_timestamp(self, temporal, expected):
        assert temporal.end_timestamp() == expected

    @pytest.mark.parametrize(
        'temporal, n, expected',
        [
            (tpi, 0, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
            (tpsd, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tps, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
            (tpss, 2, datetime(year=2019, month=9, day=3, tzinfo=timezone.utc)),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_timestamp_n(self, temporal, n, expected):
        assert temporal.timestamp_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)]),
            (tpsd, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                    datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tps, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                   datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)]),
            (tpss, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
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
            (tpsd, [TGeomPointSeq('[Point(1 1)@2019-09-01]'), TGeomPointSeq('[Point(2 2)@2019-09-02]')]),
            (tps, [TGeomPointSeq('[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02)'),
                   TGeomPointSeq('[Point(2 2)@2019-09-02]')]),
            (tpss,
             [TGeomPointSeq('[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02)'),
              TGeomPointSeq('[Point(2 2)@2019-09-02]'),
              TGeomPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpsd, True),
            (tps, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected


class TestTGeomPointEverAlwaysOperations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpsd = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpsd, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_p_1_1(self, temporal, expected):
        assert temporal.always(Point(1,1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpsd, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_p_2_2(self, temporal, expected):
        assert temporal.always(Point(2,2)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpsd, True),
            (tps, True),
            (tpss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_p_1_1(self, temporal, expected):
        assert temporal.ever(Point(1,1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpsd, True),
            (tps, True),
            (tpss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_p_2_2(self, temporal, expected):
        assert temporal.ever(Point(2,2)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpsd, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_p_1_1(self, temporal, expected):
        assert temporal.never(Point(1,1)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpsd, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_p_2_2(self, temporal, expected):
        assert temporal.never(Point(2,2)) == expected


class TestTGeomPointBooleanOperations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpsd = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    argument = TGeomPointSeq('[Point(2 2)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('False@2019-09-01')),
            (tpsd, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tps, TBoolSeq('[False@2019-09-01, False@2019-09-02]')),
            (tpss, TBoolSeqSet('{[False@2019-09-01, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('True@2019-09-01')),
            (tpsd, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tps, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            (tpss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_int(self, temporal):
        assert temporal.temporal_equal(1) == expected

        assert temporal.temporal_equal(2) == ~expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('True@2019-09-01')),
            (tpsd, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            (tps, TBoolSeq('[True@2019-09-01, True@2019-09-02]')),
            (tpss, TBoolSeqSet('{[True@2019-09-01, True@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_temporal(self, temporal, expected):
        assert temporal.temporal_not_equal(self.argument) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('False@2019-09-01')),
            (tpsd, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tps, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tpss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_not_equal_int(self, temporal):
        assert temporal.temporal_not_equal(1) == expected

        assert temporal.temporal_not_equal(2) == ~expected


class TestTGeomPointRestrictors(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpsd = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, instant, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, instant_set, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, sequence, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, sequence_set, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, Point(1,1), TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, Point(2,2), None),

            (tpsd, instant, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpsd, instant_set, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpsd, sequence, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpsd, sequence_set, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpsd, Point(1,1), TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpsd, Point(2,2), TGeomPointSeq('{Point(2 2)@2019-09-02}')),

            (tps, instant, TGeomPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, instant_set, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tps, sequence, TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, sequence_set, TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, Point(1,1), TGeomPointSeq('[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02)')),
            (tps, Point(2,2), TGeomPointSeq('[Point(2 2)@2019-09-02]')),

            (tpss, instant, TGeomPointSeqSet('[Point(1 1)@2019-09-01]')),
            (tpss, instant_set, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpss, sequence, TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (
                    tpss, sequence_set,
                    TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, Point(1,1), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02),[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, Point(2,2), TGeomPointSeqSet('{[Point(2 2)@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-p-2-2', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-p-2-2', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-p-2-2', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-p-2-2']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected


    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, instant, None),
            (tpi, instant_set, None),
            (tpi, sequence, None),
            (tpi, sequence_set, None),
            (tpi, Point(1,1), None),
            (tpi, Point(2,2), TGeomPointInst('Point(1 1)@2019-09-01')),

            (tpsd, instant, TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpsd, instant_set, TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpsd, sequence, None),
            (tpsd, sequence_set, None),
            (tpsd, Point(1,1), TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpsd, Point(2,2), TGeomPointSeq('{Point(1 1)@2019-09-01}')),

            (tps, instant, TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, instant_set, TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, sequence, None),
            (tps, sequence_set, None),
            (tps, Point(1,1), TGeomPointSeqSet('{[Point(2 2)@2019-09-02]}')),
            (tps, Point(2,2), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02)}')),

            (
                    tpss, instant,
                    TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, instant_set,
             TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],(Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, sequence, TGeomPointSeqSet('{[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, sequence_set, None),
            (tpss, Point(1,1), TGeomPointSeqSet('{[Point(2 2)@2019-09-02]}')),
            (tpss, Point(2,2), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02),[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-p-1-1',
             'Instant-p-2-2', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-p-1-1',
             'Discrete Sequence-p-2-2', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-p-1-1', 'Sequence-p-2-2', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-p-1-1',
             'SequenceSet-p-2-2']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected


class TestTGeomPointOutputs(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpsd = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'Point(1 1)@2019-09-01 00:00:00+00'),
            (tpsd, '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00}'),
            (tps, '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00]'),
            (tpss, '{[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00], '
                   '[Point(1 1)@2019-09-03 00:00:00+00, Point(1 1)@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'TGeomPointInst(Point(1 1)@2019-09-01 00:00:00+00)'),
            (tpsd, 'TGeomPointSeq({Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00})'),
            (tps, 'TGeomPointSeq([Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00])'),
            (tpss, 'TGeomPointSeqSet({[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00], '
                   '[Point(1 1)@2019-09-03 00:00:00+00, Point(1 1)@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'Point(1 1)@2019-09-01 00:00:00+00'),
            (tpsd, '{Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00}'),
            (tps, '[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00]'),
            (tpss, '{[Point(1 1)@2019-09-01 00:00:00+00, Point(2 2)@2019-09-02 00:00:00+00], '
                   '[Point(1 1)@2019-09-03 00:00:00+00, Point(1 1)@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, '011400010100A01E4E71340200'),
            (tpsd, '0114000602000000030100A01E4E71340200000000F66B85340200'),
            (tps, '0114000A02000000030100A01E4E71340200000000F66B85340200'),
            (tpss, '0114000B0200000002000000030100A01E4E71340200000000F'
                   '66B853402000200000003010060CD89993402000100207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, '{\n'
                  '  "type": "MovingGeomPoint",\n'
                  '  "period": {\n'
                  '    "begin": "2019-09-01T00:00:00+00",\n'
                  '    "end": "2019-09-01T00:00:00+00",\n'
                  '    "lower_inc": true,\n'
                  '    "upper_inc": true\n'
                  '  },\n'
                  '  "coordinates": [\n'
                  '    [1,1]\n'
                  '  ],\n'
                  '  "datetimes": [\n'
                  '    "2019-09-01T00:00:00+00"\n'
                  '  ],\n'
                  '  "interpolation": "None"\n'
                  '}'),
            (tpsd, '{\n'
                   '  "type": "MovingGeomPoint",\n'
                   '  "period": {\n'
                   '    "begin": "2019-09-01T00:00:00+00",\n'
                   '    "end": "2019-09-02T00:00:00+00",\n'
                   '    "lower_inc": true,\n'
                   '    "upper_inc": true\n'
                   '  },\n'
                   '  "coordinates": [\n'
                   '    [1,1],\n'
                   '    [2,2]\n'
                   '  ],\n'
                   '  "datetimes": [\n'
                   '    "2019-09-01T00:00:00+00",\n'
                   '    "2019-09-02T00:00:00+00"\n'
                   '  ],\n'
                   '  "lower_inc": true,\n'
                   '  "upper_inc": true,\n'
                   '  "interpolation": "Discrete"\n'
                   '}'),
            (tps, '{\n'
                  '  "type": "MovingGeomPoint",\n'
                  '  "period": {\n'
                  '    "begin": "2019-09-01T00:00:00+00",\n'
                  '    "end": "2019-09-02T00:00:00+00",\n'
                  '    "lower_inc": true,\n'
                  '    "upper_inc": true\n'
                  '  },\n'
                  '  "coordinates": [\n'
                  '    [1,1],\n'
                  '    [2,2]\n'
                  '  ],\n'
                  '  "datetimes": [\n'
                  '    "2019-09-01T00:00:00+00",\n'
                  '    "2019-09-02T00:00:00+00"\n'
                  '  ],\n'
                  '  "lower_inc": true,\n'
                  '  "upper_inc": true,\n'
                  '  "interpolation": "Step"\n'
                  '}'),
            (tpss, '{\n'
                   '  "type": "MovingGeomPoint",\n'
                   '  "period": {\n'
                   '    "begin": "2019-09-01T00:00:00+00",\n'
                   '    "end": "2019-09-05T00:00:00+00",\n'
                   '    "lower_inc": true,\n'
                   '    "upper_inc": true\n'
                   '  },\n'
                   '  "sequences": [\n'
                   '    {\n'
                   '      "coordinates": [\n'
                   '        [1,1],\n'
                   '        [2,2]\n'
                   '      ],\n'
                   '      "datetimes": [\n'
                   '        "2019-09-01T00:00:00+00",\n'
                   '        "2019-09-02T00:00:00+00"\n'
                   '      ],\n'
                   '      "lower_inc": true,\n'
                   '      "upper_inc": true\n'
                   '    },\n'
                   '    {\n'
                   '      "coordinates": [\n'
                   '        [1,1],\n'
                   '        [1,1]\n'
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
