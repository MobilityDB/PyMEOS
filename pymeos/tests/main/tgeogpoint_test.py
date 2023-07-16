from copy import copy
from datetime import datetime, timezone, timedelta

import pytest
from shapely import Point
import shapely.geometry

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, TGeogPoint, \
    TGeogPointInst, TGeogPointSeq, TGeogPointSeqSet, TInterpolation, TimestampSet, Period, PeriodSet
from tests.conftest import TestPyMEOS


class TestTGeogPoint(TestPyMEOS):
    pass


class TestTGeogPointConstructors(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    tpi3d = TGeogPointInst('Point(1 1 1)@2019-09-01')
    tpds3d = TGeogPointSeq('{Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02}')
    tps3d = TGeogPointSeq('[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02]')
    tpss3d = TGeogPointSeqSet('{[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02],'
      '[Point(1 1 1)@2019-09-03, Point(1 1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1.5@2000-01-01'), TGeogPointInst, TInterpolation.NONE),
            (TFloatSeq('{1.5@2000-01-01, 0.5@2000-01-02}'), TGeogPointSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1.5@2000-01-01, 0.5@2000-01-02]'), TGeogPointSeq, TInterpolation.LINEAR),
            (TFloatSeqSet('{[1.5@2000-01-01, 0.5@2000-01-02],[1.5@2000-01-03, 1.5@2000-01-05]}'),
             TGeogPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tp = TGeogPoint.from_base_temporal(Point(1,1), source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TGeogPointInst, TInterpolation.NONE),
            (TimestampSet('{2000-01-01, 2000-01-02}'), TGeogPointSeq, TInterpolation.DISCRETE),
            (Period('[2000-01-01, 2000-01-02]'), TGeogPointSeq, TInterpolation.LINEAR),
            (PeriodSet('{[2000-01-01, 2000-01-02],[2000-01-03, 2000-01-05]}'), TGeogPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tp = TGeogPoint.from_base_time(Point(1,1), source, interpolation)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('Point(1 1)@2019-09-01', TGeogPointInst, TInterpolation.NONE, 'POINT(1 1)@2019-09-01 00:00:00+00'),
            ('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}', TGeogPointSeq, TInterpolation.DISCRETE,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00}'),
            ('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]', TGeogPointSeq, TInterpolation.LINEAR,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}', TGeogPointSeqSet,
             TInterpolation.LINEAR, '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00], '
                                      '[POINT(1 1)@2019-09-03 00:00:00+00, POINT(1 1)@2019-09-05 00:00:00+00]}'),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_string_constructor(self, source, type, interpolation, expected):
        tp = type(source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation
        assert str(tp) == expected

    # @pytest.mark.parametrize(
        # 'source, type, expected',
        # [
            # ('[Point(1 1)@2019-09-01, Point(1.25 1.25)@2019-09-02, Point(1.5 1.5)@2019-09-03, Point(2 2)@2019-09-05]', TGeogPointSeq,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00]'),
            # ('{[Point(1 1)@2019-09-01, Point(1.25 1.25)@2019-09-02, Point(1.5 1.5)@2019-09-03, Point(2 2)@2019-09-05],'
             # '[Point(1 1)@2019-09-07, Point(1 1)@2019-09-08, Point(1 1)@2019-09-09]}', TGeogPointSeqSet,
             # '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00], '
             # '[POINT(1 1)@2019-09-07 00:00:00+00, POINT(1 1)@2019-09-09 00:00:00+00]}'),
        # ],
        # ids=['Sequence', 'SequenceSet']
    # )
    # def test_string_constructor_normalization(self, source, type, expected):
        # tp = type(source, normalize=True)
        # assert isinstance(tp, type)
        # assert str(tp) == expected

    @pytest.mark.parametrize(
        'value, timestamp',
        [
            (Point(1,1), datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('POINT(1 1)', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            (Point(1,1), '2019-09-01'),
            ('POINT(1 1)', '2019-09-01'),
        ],
        ids=['point-datetime', 'string-datetime', 'point-string', 'string-string']
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tpi = TGeogPointInst(point=value, timestamp=timestamp)
        assert str(tpi) == 'POINT(1 1)@2019-09-01 00:00:00+00'

    # @pytest.mark.parametrize(
        # 'list, interpolation, normalize, expected',
        # [
            # (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.DISCRETE, False,
             # '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            # (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, False,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            # ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             # '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            # ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            # (['Point(1 1)@2019-09-01', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             # '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            # (['Point(1 1)@2019-09-01', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),

            # (['Point(1 1)@2019-09-01', 'Point(1.5 1.5)@2019-09-02', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, True,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            # ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(1.5 1.5)@2019-09-02'), TGeogPointInst('Point(2 2)@2019-09-03')],
             # TInterpolation.LINEAR, True,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            # (['Point(1 1)@2019-09-01', 'Point(1.5 1.5)@2019-09-02', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, True,
             # '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
        # ],
        # ids=['String Discrete', 'String Linear', 'TGeogPointInst Discrete', 'TGeogPointInst Linear', 'Mixed Discrete',
             # 'Mixed Linear', 'String Linear Normalized', 'TGeogPointInst Linear Normalized',
             # 'Mixed Linear Normalized']
    # )
    # def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        # tps = TGeogPointSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        # assert str(tps) == expected
        # assert tps.interpolation() == interpolation

        # tps2 = TGeogPointSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        # assert str(tps2) == expected
        # assert tps2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tpi, tpds, tps, tpss, tpi3d, tpds3d, tps3d, tpss3d],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Instant 3D', 'Discrete Sequence 3D', 'Sequence 3D', 'SequenceSet 3D']
    )
    def test_from_hexwkb_constructor(self, temporal):
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())

    @pytest.mark.parametrize(
        'temporal',
        [tpi, tpds, tps, tpss, tpi3d, tpds3d, tps3d, tpss3d],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Instant 3D', 'Discrete Sequence 3D', 'Sequence 3D', 'SequenceSet 3D']
    )
    def test_copy_constructor(self, temporal):
        other = copy(temporal)
        assert temporal == other
        assert temporal is not other


class TestTGeogPointOutputs(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'POINT(1 1)@2019-09-01 00:00:00+00'),
            (tpds, '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00}'),
            (tps, '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00]'),
            (tpss, '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00], '
                   '[POINT(1 1)@2019-09-03 00:00:00+00, POINT(1 1)@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_str(self, temporal, expected):
        assert str(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'TGeogPointInst(POINT(1 1)@2019-09-01 00:00:00+00)'),
            (tpds, 'TGeogPointSeq({POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00})'),
            (tps, 'TGeogPointSeq([POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00])'),
            (tpss, 'TGeogPointSeqSet({[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00], '
                   '[POINT(1 1)@2019-09-03 00:00:00+00, POINT(1 1)@2019-09-05 00:00:00+00]})')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_repr(self, temporal, expected):
        assert repr(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 'POINT(1 1)@2019-09-01 00:00:00+00'),
            (tpds, '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00}'),
            (tps, '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00]'),
            (tpss, '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00], '
                   '[POINT(1 1)@2019-09-03 00:00:00+00, POINT(1 1)@2019-09-05 00:00:00+00]}')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_wkt(self, temporal, expected):
        assert temporal.as_wkt() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, '01290061E6100000000000000000F03F000000000000F03F00A01E4E71340200'),
            (tpds, '01290066E61000000200000003000000000000F03F000000000000F03F00A01E4E71340200'
                '000000000000004000000000000000400000F66B85340200'),
            (tps, '0129006EE61000000200000003000000000000F03F000000000000F03F00A01E4E71340200'
                '000000000000004000000000000000400000F66B85340200'),
            (tpss, '0129006FE6100000020000000200000003000000000000F03F000000000000F03F00A01E4E71340200'
                '000000000000004000000000000000400000F66B853402000200000003000000000000F03F000000000'
                '000F03F0060CD8999340200000000000000F03F000000000000F03F00207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, '{\n'
                  '   "type": "MovingGeogPoint",\n'
                  '   "bbox": [\n'
                  '     [\n'
                  '       1,\n'
                  '       1\n'
                  '     ],\n'
                  '     [\n'
                  '       1,\n'
                  '       1\n'
                  '     ]\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-01T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "coordinates": [\n'
                  '     [\n'
                  '       1,\n'
                  '       1\n'
                  '     ]\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00"\n'
                  '   ],\n'
                  '   "interpolation": "None"\n'
                  ' }'),
            (tpds, '{\n'
                   '   "type": "MovingGeogPoint",\n'
                   '   "bbox": [\n'
                   '     [\n'
                   '       1,\n'
                   '       1\n'
                   '     ],\n'
                   '     [\n'
                   '       2,\n'
                   '       2\n'
                   '     ]\n'
                   '   ],\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-02T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "coordinates": [\n'
                   '     [\n'
                   '       1,\n'
                   '       1\n'
                   '     ],\n'
                   '     [\n'
                   '       2,\n'
                   '       2\n'
                   '     ]\n'
                   '   ],\n'
                   '   "datetimes": [\n'
                   '     "2019-09-01T00:00:00+00",\n'
                   '     "2019-09-02T00:00:00+00"\n'
                   '   ],\n'
                   '   "lower_inc": true,\n'
                   '   "upper_inc": true,\n'
                   '   "interpolation": "Discrete"\n'
                   ' }'),
            (tps, '{\n'
                  '   "type": "MovingGeogPoint",\n'
                  '   "bbox": [\n'
                  '     [\n'
                  '       1,\n'
                  '       1\n'
                  '     ],\n'
                  '     [\n'
                  '       2,\n'
                  '       2\n'
                  '     ]\n'
                  '   ],\n'
                  '   "period": {\n'
                  '     "begin": "2019-09-01T00:00:00+00",\n'
                  '     "end": "2019-09-02T00:00:00+00",\n'
                  '     "lower_inc": true,\n'
                  '     "upper_inc": true\n'
                  '   },\n'
                  '   "coordinates": [\n'
                  '     [\n'
                  '       1,\n'
                  '       1\n'
                  '     ],\n'
                  '     [\n'
                  '       2,\n'
                  '       2\n'
                  '     ]\n'
                  '   ],\n'
                  '   "datetimes": [\n'
                  '     "2019-09-01T00:00:00+00",\n'
                  '     "2019-09-02T00:00:00+00"\n'
                  '   ],\n'
                  '   "lower_inc": true,\n'
                  '   "upper_inc": true,\n'
                  '   "interpolation": "Linear"\n'
                  ' }'),
            (tpss, '{\n'
                   '   "type": "MovingGeogPoint",\n'
                   '   "bbox": [\n'
                   '     [\n'
                   '       1,\n'
                   '       1\n'
                   '     ],\n'
                   '     [\n'
                   '       2,\n'
                   '       2\n'
                   '     ]\n'
                   '   ],\n'
                   '   "period": {\n'
                   '     "begin": "2019-09-01T00:00:00+00",\n'
                   '     "end": "2019-09-05T00:00:00+00",\n'
                   '     "lower_inc": true,\n'
                   '     "upper_inc": true\n'
                   '   },\n'
                   '   "sequences": [\n'
                   '     {\n'
                   '       "coordinates": [\n'
                   '         [\n'
                   '           1,\n'
                   '           1\n'
                   '         ],\n'
                   '         [\n'
                   '           2,\n'
                   '           2\n'
                   '         ]\n'
                   '       ],\n'
                   '       "datetimes": [\n'
                   '         "2019-09-01T00:00:00+00",\n'
                   '         "2019-09-02T00:00:00+00"\n'
                   '       ],\n'
                   '       "lower_inc": true,\n'
                   '       "upper_inc": true\n'
                   '     },\n'
                   '     {\n'
                   '       "coordinates": [\n'
                   '         [\n'
                   '           1,\n'
                   '           1\n'
                   '         ],\n'
                   '         [\n'
                   '           1,\n'
                   '           1\n'
                   '         ]\n'
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


class TestTGeogPointAccessors(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TInterpolation.NONE),
            (tpds, TInterpolation.DISCRETE),
            (tps, TInterpolation.LINEAR),
            (tpss, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_interpolation(self, temporal, expected):
        assert temporal.interpolation() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, {Point(1,1)}),
            (tpds, {Point(1,1), Point(2,2)}),
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
            (tpds, [Point(1,1), Point(2,2)]),
            (tps, [Point(1,1), Point(2,2)]),
            (tpss, [Point(1,1), Point(2,2)])
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_values(self, temporal, expected):
        assert temporal.values() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, Point(1,1)),
            (tpds, Point(1,1)),
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
            (tpds, Point(2,2)),
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
            (tpds, Point(1,1)),
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
            (tpds, PeriodSet('{[2019-09-01, 2019-09-01], [2019-09-02, 2019-09-02]}')),
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
            (tpds, timedelta()),
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
            (tpds, timedelta(days=1)),
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
            (tpds, Period('[2019-09-01, 2019-09-02]')),
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
            (tpds, Period('[2019-09-01, 2019-09-02]')),
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
            (tpds, 2),
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
            (tpds, tpi),
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
            (tpds, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tps, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tpss, TGeogPointInst('Point(1 1)@2019-09-05')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_end_instant(self, temporal, expected):
        assert temporal.end_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpds, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tps, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tpss, TGeogPointInst('Point(2 2)@2019-09-02')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_max_instant(self, temporal, expected):
        assert temporal.max_instant() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, tpi),
            (tpds, tpi),
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
            (tpds, 1, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tps, 1, TGeogPointInst('Point(2 2)@2019-09-02')),
            (tpss, 2, TGeogPointInst('Point(1 1)@2019-09-03')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instant_n(self, temporal, n, expected):
        assert temporal.instant_n(n) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, [tpi]),
            (tpds, [tpi, TGeogPointInst('Point(2 2)@2019-09-02')]),
            (tps, [tpi, TGeogPointInst('Point(2 2)@2019-09-02')]),
            (tpss, [tpi, TGeogPointInst('Point(2 2)@2019-09-02'), TGeogPointInst('Point(1 1)@2019-09-03'), TGeogPointInst('Point(1 1)@2019-09-05')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_instants(self, temporal, expected):
        assert temporal.instants() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 1),
            (tpds, 2),
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
            (tpds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)),
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
            (tpds, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
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
            (tpds, 1, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc)),
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
            (tpds, [datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
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
            (tpds, [TGeogPointSeq('[Point(1 1)@2019-09-01]'), TGeogPointSeq('[Point(2 2)@2019-09-02]')]),
            (tps, [TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')]),
            (tpss,
             [TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
              TGeogPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]')]),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_segments(self, temporal, expected):
        assert temporal.segments() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpds, True),
            (tps, True),
        ],
        ids=['Discrete Sequence', 'Sequence']
    )
    def test_lower_upper_inc(self, temporal, expected):
        assert temporal.lower_inc() == expected
        assert temporal.upper_inc() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 4326),
            (tpds, 4326),
            (tps, 4326),
            (tpss, 4326)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_srid(self, temporal, expected):
        assert temporal.srid() == expected


class TestTGeogPointEverAlwaysOperations(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpds, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_p_1_1(self, temporal, expected):
        assert temporal.always_equal(shapely.set_srid(shapely.Point(1,1), 4326)) == expected


    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpds, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_always_p_2_2(self, temporal, expected):
        assert temporal.always_equal(shapely.set_srid(shapely.Point(2,2), 4326)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpds, True),
            (tps, True),
            (tpss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_p_1_1(self, temporal, expected):
        assert temporal.ever_equal(shapely.set_srid(shapely.Point(1,1), 4326)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpds, True),
            (tps, True),
            (tpss, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_ever_p_2_2(self, temporal, expected):
        assert temporal.ever_equal(shapely.set_srid(shapely.Point(2,2), 4326)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, False),
            (tpds, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_p_1_1(self, temporal, expected):
        assert temporal.never_equal(shapely.set_srid(shapely.Point(1,1), 4326)) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpds, False),
            (tps, False),
            (tpss, False)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_never_p_2_2(self, temporal, expected):
        assert temporal.never_equal(shapely.set_srid(shapely.Point(2,2), 4326)) == expected


# class TestTGeogPointBooleanOperations(TestTGeogPoint):
    # tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    # tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    # tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    # tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    # argument = TGeogPointSeq('[Point(2 2)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03]')

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('False@2019-09-01')),
            # (tpds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            # (tps, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
                 # '(False@2019-09-01 12:00:00+00, False@2019-09-02]}')),
            # (tpss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
                 # '(False@2019-09-01 12:00:00+00, False@2019-09-02],[True@2019-09-03]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_equal_temporal(self, temporal, expected):
        # assert temporal.temporal_equal(self.argument) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('True@2019-09-01')),
            # (tpds, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            # (tps, TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02]}')),
            # (tpss, TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_equal_point(self, temporal, expected):
        # assert temporal.temporal_equal(Point(1,1)) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('False@2019-09-01')),
            # (tpds, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            # (tps, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            # (tpss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_equal_point(self, temporal, expected):
        # assert temporal.temporal_equal(Point(2,2)) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('True@2019-09-01')),
            # (tpds, TBoolSeq('{True@2019-09-01, True@2019-09-02}')),
            # (tps, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00+00],'
                # '(True@2019-09-01 12:00:00+00, True@2019-09-02]}')),
            # (tpss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-01 12:00:00+00],'
                # '(True@2019-09-01 12:00:00+00, True@2019-09-02],[False@2019-09-03]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_not_equal_temporal(self, temporal, expected):
        # assert temporal.temporal_not_equal(self.argument) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('False@2019-09-01')),
            # (tpds, TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            # (tps, TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            # (tpss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_not_equal_point(self, temporal, expected):
        # assert temporal.temporal_not_equal(Point(1,1)) == expected

    # @pytest.mark.parametrize(
        # 'temporal, expected',
        # [
            # (tpi, TBoolInst('True@2019-09-01')),
            # (tpds, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            # (tps, TBoolSeq('[True@2019-09-01, False@2019-09-02]')),
            # (tpss, TBoolSeqSet('{[True@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}'))
        # ],
        # ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    # )
    # def test_temporal_not_equal_point(self, temporal, expected):
        # assert temporal.temporal_not_equal(Point(2,2)) == expected


class TestTGeogPointRestrictors(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    instant = datetime(2019, 9, 1)
    instant_set = TimestampSet('{2019-09-01, 2019-09-03}')
    sequence = Period('[2019-09-01, 2019-09-02]')
    sequence_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, instant, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, instant_set, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, sequence, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, sequence_set, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), None),

            (tpds, instant, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, instant_set, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, sequence, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, sequence_set, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('{Point(2 2)@2019-09-02}')),

            (tps, instant, TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, instant_set, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tps, sequence, TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, sequence_set, TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('[Point(2 2)@2019-09-02]')),

            (tpss, instant, TGeogPointSeqSet('[Point(1 1)@2019-09-01]')),
            (tpss, instant_set, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpss, sequence, TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, sequence_set, TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],'
                '[Point(1 1)@2019-09-03,Point(1 1)@2019-09-05]}')),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeqSet('{[Point(2 2)@2019-09-02]}'))

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
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), None),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointInst('Point(1 1)@2019-09-01')),

            (tpds, instant, TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, instant_set, TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, sequence, None),
            (tpds, sequence_set, None),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('{Point(1 1)@2019-09-01}')),

            (tps, instant, TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, instant_set, TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, sequence, None),
            (tps, sequence_set, None),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), 
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02)}')),

            (
                tpss, instant,
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, instant_set,
             TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],(Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, sequence, TGeogPointSeqSet('{[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, sequence_set, None),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326),
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02),[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}'))
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


