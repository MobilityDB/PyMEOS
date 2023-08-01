from copy import copy
from operator import not_
from datetime import datetime, timezone, timedelta

import pytest
import math
from shapely import Point, Polygon

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, TGeomPoint, \
    TGeomPointInst, TGeomPointSeq, TGeomPointSeqSet, TInterpolation, TimestampSet, Period, PeriodSet, STBox
from tests.conftest import TestPyMEOS


class TestTGeomPoint(TestPyMEOS):
    pass


class TestTGeomPointConstructors(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    tpi3d = TGeomPointInst('Point(1 1 1)@2019-09-01')
    tpds3d = TGeomPointSeq('{Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02}')
    tps3d = TGeomPointSeq('[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02]')
    tpss3d = TGeomPointSeqSet('{[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02],'
      '[Point(1 1 1)@2019-09-03, Point(1 1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (TFloatInst('1.5@2019-09-01'), TGeomPointInst, TInterpolation.NONE),
            (TFloatSeq('{1.5@2019-09-01, 0.5@2019-09-02}'), TGeomPointSeq, TInterpolation.DISCRETE),
            (TFloatSeq('[1.5@2019-09-01, 0.5@2019-09-02]'), TGeomPointSeq, TInterpolation.LINEAR),
            (TFloatSeqSet('{[1.5@2019-09-01, 0.5@2019-09-02],[1.5@2019-09-03, 1.5@2019-09-05]}'),
             TGeomPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tp = TGeomPoint.from_base_temporal(Point(1,1), source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TGeomPointInst, TInterpolation.NONE),
            (TimestampSet('{2019-09-01, 2019-09-02}'), TGeomPointSeq, TInterpolation.DISCRETE),
            (Period('[2019-09-01, 2019-09-02]'), TGeomPointSeq, TInterpolation.LINEAR),
            (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'), TGeomPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tp = TGeomPoint.from_base_time(Point(1,1), source, interpolation)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation, expected',
        [
            ('Point(1 1)@2019-09-01', TGeomPointInst, TInterpolation.NONE, 'POINT(1 1)@2019-09-01 00:00:00+00'),
            ('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}', TGeomPointSeq, TInterpolation.DISCRETE,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00}'),
            ('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]', TGeomPointSeq, TInterpolation.LINEAR,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}', TGeomPointSeqSet,
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

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[Point(1 1)@2019-09-01, Point(1.25 1.25)@2019-09-02, Point(1.5 1.5)@2019-09-03, Point(2 2)@2019-09-05]', TGeomPointSeq,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, Point(1.25 1.25)@2019-09-02, Point(1.5 1.5)@2019-09-03, Point(2 2)@2019-09-05],'
             '[Point(1 1)@2019-09-07, Point(1 1)@2019-09-08, Point(1 1)@2019-09-09]}', TGeomPointSeqSet,
             '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00], '
             '[POINT(1 1)@2019-09-07 00:00:00+00, POINT(1 1)@2019-09-09 00:00:00+00]}'),
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
            (Point(1,1), datetime(2019, 9, 1, tzinfo=timezone.utc)),
            ('POINT(1 1)', datetime(2019, 9, 1, tzinfo=timezone.utc)),
            (Point(1,1), '2019-09-01'),
            ('POINT(1 1)', '2019-09-01'),
        ],
        ids=['point-datetime', 'string-datetime', 'point-string', 'string-string']
    )
    def test_value_timestamp_instant_constructor(self, value, timestamp):
        tpi = TGeomPointInst(point=value, timestamp=timestamp)
        assert str(tpi) == 'POINT(1 1)@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),

            (['Point(1 1)@2019-09-01', 'Point(1.5 1.5)@2019-09-02', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeomPointInst('Point(1 1)@2019-09-01'), TGeomPointInst('Point(1.5 1.5)@2019-09-02'), TGeomPointInst('Point(2 2)@2019-09-03')],
             TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', 'Point(1.5 1.5)@2019-09-02', TGeomPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Linear', 'TGeomPointInst Discrete', 'TGeomPointInst Linear', 'Mixed Discrete',
             'Mixed Linear', 'String Linear Normalized', 'TGeomPointInst Linear Normalized',
             'Mixed Linear Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tps = TGeomPointSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps) == expected
        assert tps.interpolation() == interpolation

        tps2 = TGeomPointSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps2) == expected
        assert tps2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tpi, tpds, tps, tpss, tpi3d, tpds3d, tps3d, tpss3d],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Instant 3D', 'Discrete Sequence 3D', 'Sequence 3D', 'SequenceSet 3D']
    )
    def test_from_as_constructor(self, temporal):
        assert temporal == temporal.from_wkb(temporal.as_wkb())
        assert temporal == temporal.from_hexwkb(temporal.as_hexwkb())
        assert temporal == temporal.from_mfjson(temporal.as_mfjson())

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


class TestTGeomPointOutputs(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

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
            (tpi, 'TGeomPointInst(POINT(1 1)@2019-09-01 00:00:00+00)'),
            (tpds, 'TGeomPointSeq({POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00})'),
            (tps, 'TGeomPointSeq([POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00])'),
            (tpss, 'TGeomPointSeqSet({[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-02 00:00:00+00], '
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
            (tpi, '01280001000000000000F03F000000000000F03F00A01E4E71340200'),
            (tpds, '012800060200000003000000000000F03F000000000000F03F00A01E4E71340200'
                '000000000000004000000000000000400000F66B85340200'),
            (tps, '0128000E0200000003000000000000F03F000000000000F03F00A01E4E71340200'
                '000000000000004000000000000000400000F66B85340200'),
            (tpss, '0128000F020000000200000003000000000000F03F000'
                '000000000F03F00A01E4E7134020000000000000000400'
                '0000000000000400000F66B853402000200000003000000'
                '000000F03F000000000000F03F0060CD8999340200000000000000F03F000000000000F03F00207CC5C1340200')
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_as_hexwkb(self, temporal, expected):
        assert temporal.as_hexwkb() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, '{\n'
                  '   "type": "MovingGeomPoint",\n'
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
                   '   "type": "MovingGeomPoint",\n'
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
                  '   "type": "MovingGeomPoint",\n'
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
                   '   "type": "MovingGeomPoint",\n'
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


class TestTGeomPointAccessors(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    tpi3d = TGeomPointInst('Point(1 1 1)@2019-09-01')
    tpds3d = TGeomPointSeq('{Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02}')
    tps3d = TGeomPointSeq('[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02]')
    tpss3d = TGeomPointSeqSet('{[Point(1 1 1)@2019-09-01, Point(2 2 2)@2019-09-02],'
      '[Point(1 1 1)@2019-09-03, Point(1 1 1)@2019-09-05]}')

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
            (tpi, 0),
            (tpds, 0),
            (tps, math.sqrt(2)),
            (tpss, math.sqrt(2))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_length(self, temporal, expected):
        assert temporal.length() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TFloatInst('0@2019-09-01')),
            (tpds, TFloatSeq('{0@2019-09-01, 0@2019-09-02}')),
            (tps, TFloatSeq('[0@2019-09-01, 1.4142135623730951@2019-09-02]')),
            (tpss, TFloatSeqSet('{[0@2019-09-01, 1.4142135623730951@2019-09-02],'
                '[1.4142135623730951@2019-09-03, 1.4142135623730951@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_cumulative_length(self, temporal, expected):
        assert temporal.cumulative_length() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, None),
            (tpds, None),
            (tps, TFloatSeq('Interp=Step;[1.4142135623730951@2019-09-01, 1.4142135623730951@2019-09-02]') / 3600 / 24),
            (tpss, TFloatSeqSet('Interp=Step;{[1.4142135623730951@2019-09-01, 1.4142135623730951@2019-09-02],'
                '[0@2019-09-03, 0@2019-09-05]}') / 3600 / 24)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_speed(self, temporal, expected):
        assert temporal.speed() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TFloatInst('1@2019-09-01')),
            (tpds, TFloatSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tps, TFloatSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tpss, TFloatSeqSet('{[1@2019-09-01, 2@2019-09-02],'
                '[1@2019-09-03, 1@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_x_y(self, temporal, expected):
        assert temporal.x() == expected
        assert temporal.y() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi3d, TFloatInst('1@2019-09-01')),
            (tpds3d, TFloatSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tps3d, TFloatSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tpss3d, TFloatSeqSet('{[1@2019-09-01, 2@2019-09-02],'
                '[1@2019-09-03, 1@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_x_y_z(self, temporal, expected):
        assert temporal.x() == expected
        assert temporal.y() == expected
        assert temporal.z() == expected

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
    def test_has_z(self, temporal, expected):
        assert temporal.has_z() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi3d, True),
            (tpds3d, True),
            (tps3d, True),
            (tpss3d, True)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_has_z(self, temporal, expected):
        assert temporal.has_z() == expected

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
            (tpds, TGeomPointInst('Point(2 2)@2019-09-02')),
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
            (tpds, TGeomPointInst('Point(2 2)@2019-09-02')),
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
            (tpds, 1, TGeomPointInst('Point(2 2)@2019-09-02')),
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
            (tpds, [tpi, TGeomPointInst('Point(2 2)@2019-09-02')]),
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
            (tpds, [TGeomPointSeq('[Point(1 1)@2019-09-01]'), TGeomPointSeq('[Point(2 2)@2019-09-02]')]),
            (tps, [TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')]),
            (tpss,
             [TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
              TGeomPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]')]),
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
            (tpi, 382694564),
            (tpds, 1664033448),
            (tps, 1664033448),
            (tpss, 2878566103)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 0),
            (tpds, 0),
            (tps, 0),
            (tpss, 0)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_srid(self, temporal, expected):
        assert temporal.srid() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, 5676),
            (tpds, 5676),
            (tps, 5676),
            (tpss, 5676)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_set_srid(self, temporal, expected):
        assert temporal.set_srid(5676).srid() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, STBox('STBOX XT(((1,1),(1,1)),[2019-09-01, 2019-09-01])')),
            (tpds, STBox('STBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])')),
            (tps, STBox('STBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])')),
            (tpss, STBox('STBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-05])')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_bounding_box(self, temporal, expected):
        assert temporal.bounding_box() == expected


class TestTGeomPointTransformations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TGeomPointInst('Point(1 1)@2019-09-01'), tpi),
            (TGeomPointSeq('{Point(1 1)@2019-09-01}'), tpi),
            (TGeomPointSeq('[Point(1 1)@2019-09-01]'), tpi),
            (TGeomPointSeqSet('{[Point(1 1)@2019-09-01]}'), tpi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_instant(self, temporal, expected):
        temp = temporal.to_instant()
        assert isinstance(temp, TGeomPointInst)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TGeomPointInst('Point(1 1)@2019-09-01'), 
                TGeomPointSeq('[Point(1 1)@2019-09-01]')),
            (TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}'),
                TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
                TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}'),
                TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequence(self, temporal, expected):
        temp = temporal.to_sequence()
        assert isinstance(temp, TGeomPointSeq)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TGeomPointInst('Point(1 1)@2019-09-01'), 
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01]}')),
            (TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01], [Point(2 2)@2019-09-02]}')),
            (TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequenceset(self, temporal, expected):
        temp = temporal.to_sequenceset()
        assert isinstance(temp, TGeomPointSeqSet)
        assert temp == expected

    @pytest.mark.parametrize(
        'tpoint, delta, expected',
        [(tpi, timedelta(days=4), TGeomPointInst('Point(1 1)@2019-09-05')),
         (tpi, timedelta(days=-4), TGeomPointInst('Point(1 1)@2019-08-28')),
         (tpi, timedelta(hours=2), TGeomPointInst('Point(1 1)@2019-09-01 02:00:00')),
         (tpi, timedelta(hours=-2), TGeomPointInst('Point(1 1)@2019-08-31 22:00:00')), 
         (tpds, timedelta(days=4), TGeomPointSeq('{Point(1 1)@2019-09-05, Point(2 2)@2019-09-06}')),
         (tpds, timedelta(days=-4), TGeomPointSeq('{Point(1 1)@2019-08-28, Point(2 2)@2019-08-29}')),
         (tpds, timedelta(hours=2), TGeomPointSeq('{Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00}')),
         (tpds, timedelta(hours=-2), TGeomPointSeq('{Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00}')),
         (tps, timedelta(days=4), TGeomPointSeq('[Point(1 1)@2019-09-05, Point(2 2)@2019-09-06]')),
         (tps, timedelta(days=-4), TGeomPointSeq('[Point(1 1)@2019-08-28, Point(2 2)@2019-08-29]')),
         (tps, timedelta(hours=2), TGeomPointSeq('[Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00]')),
         (tps, timedelta(hours=-2), TGeomPointSeq('[Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00]')),
         (tpss, timedelta(days=4),
             TGeomPointSeqSet('{[Point(1 1)@2019-09-05, Point(2 2)@2019-09-06],[Point(1 1)@2019-09-07, Point(1 1)@2019-09-09]}')),
         (tpss, timedelta(days=-4),
             TGeomPointSeqSet('{[Point(1 1)@2019-08-28, Point(2 2)@2019-08-29],[Point(1 1)@2019-08-30, Point(1 1)@2019-09-01]}')),
         (tpss, timedelta(hours=2),
             TGeomPointSeqSet('{[Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00],'
                         '[Point(1 1)@2019-09-03 02:00:00, Point(1 1)@2019-09-05 02:00:00]}')),
         (tpss, timedelta(hours=-2),
             TGeomPointSeqSet('{[Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00],'
             '[Point(1 1)@2019-09-02 22:00:00, Point(1 1)@2019-09-04 22:00:00]}')),
         ],
        ids=['Instant posi(tpve days', 'Instant nega(tpve days',
             'Instant posi(tpve hours', 'Instant nega(tpve hours',
             'Discrete Sequence posi(tpve days', 'Discrete Sequence nega(tpve days', 
             'Discrete Sequence posi(tpve hours', 'Discrete Sequence nega(tpve hours',
             'Sequence posi(tpve days', 'Sequence nega(tpve days', 
             'Sequence posi(tpve hours', 'Sequence nega(tpve hours',
             'Sequence Set posi(tpve days', 'Sequence Set nega(tpve days', 
             'Sequence Set posi(tpve hours', 'Sequence Set nega(tpve hours']
    )
    def test_shift(self, tpoint, delta, expected):
        assert tpoint.shift(delta) == expected

    @pytest.mark.parametrize(
        'tpoint, delta, expected',
        [(tpi, timedelta(days=4), TGeomPointInst('Point(1 1)@2019-09-01')),
         (tpi, timedelta(hours=2), TGeomPointInst('Point(1 1)@2019-09-01')),
         (tpds, timedelta(days=4), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-05}')),
         (tpds, timedelta(hours=2), TGeomPointSeq('{Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 02:00:00}')),
         (tps, timedelta(days=4), TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-05]')),
         (tps, timedelta(hours=2), TGeomPointSeq('[Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 02:00:00]')),
         (tpss, timedelta(days=4),
             TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
         (tpss, timedelta(hours=2),
             TGeomPointSeqSet('{[Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 00:30:00],'
                         '[Point(1 1)@2019-09-01 01:00:00, Point(1 1)@2019-09-01 02:00:00]}')),
        ],
        ids=['Instant posi(tpve days', 'Instant posi(tpve hours',
             'Discrete Sequence posi(tpve days', 'Discrete Sequence posi(tpve hours',
             'Sequence posi(tpve days', 'Sequence posi(tpve hours',
             'Sequence Set posi(tpve days', 'Sequence Set posi(tpve hours']
    )
    def test_scale(self, tpoint, delta, expected):
        assert tpoint.tscale(delta) == expected

    def test_shift_tscale(self):
        assert self.tpss.shift_tscale(timedelta(days=4), timedelta(hours=2)) == \
             TGeomPointSeqSet('{[Point(1 1)@2019-09-05 00:00:00, Point(2 2)@2019-09-05 00:30:00],'
             '[Point(1 1)@2019-09-05 01:00:00, Point(1 1)@2019-09-05 02:00:00]}')


class TestTGeomPointModifications(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tpi, TGeomPointSeq('{Point(1 1)@2019-09-03}'), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpds, TGeomPointSeq('{Point(1 1)@2019-09-03}'), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeomPointSeq('[Point(1 1)@2019-09-03]'), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03]}')),
            (tpss, TGeomPointSeq('[Point(1 1)@2019-09-06]'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05],[Point(1 1)@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_insert(self, temporal, sequence, expected):
        assert temporal.insert(sequence) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tpi, TGeomPointInst('Point(2 2)@2019-09-01'), TGeomPointInst('Point(2 2)@2019-09-01')),
            (tpds, TGeomPointInst('Point(2 2)@2019-09-01'), TGeomPointSeq('{Point(2 2)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tps, TGeomPointInst('Point(2 2)@2019-09-01'), 
                TGeomPointSeqSet('{[Point(2 2)@2019-09-01], (Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, TGeomPointInst('Point(2 2)@2019-09-01'),
                TGeomPointSeqSet('{[Point(2 2)@2019-09-01], (Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_update(self, temporal, instant, expected):
        assert temporal.update(instant) == expected

    @pytest.mark.parametrize(
        'temporal, time, expected',
        [
            (tpi, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), None),
            (tpi, datetime(year=2019, month=9, day=2, tzinfo=timezone.utc), tpi),
            (tpds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tps, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
        ],
        ids=['Instant intersection', 'Instant disjoint', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_delete(self, temporal, time, expected):
        assert temporal.delete(time) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tpi, TGeomPointInst('Point(1 1)@2019-09-02'), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-02}')),
            (tpds, TGeomPointInst('Point(1 1)@2019-09-03'), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeomPointInst('Point(1 1)@2019-09-03'), TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03]')),
            (tpss, TGeomPointInst('Point(1 1)@2019-09-06'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_instant(self, temporal, instant, expected):
        assert temporal.append_instant(instant) == expected

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tpds, TGeomPointSeq('{Point(1 1)@2019-09-03}'), TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeomPointSeq('[Point(1 1)@2019-09-03]'), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02], [Point(1 1)@2019-09-03]}')),
            (tpss, TGeomPointSeq('[Point(1 1)@2019-09-06]'),
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05],[Point(1 1)@2019-09-06]}')),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_sequence(self, temporal, sequence, expected):
        assert temporal.append_sequence(sequence) == expected


class TestTGeomPointEverAlwaysOperations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02], [Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tpi, Point(1,1), True),
            (tpi, Point(2,2), False),
            (tpds, Point(1,1), False),
            (tpds, Point(2,2), False),
            (tps, Point(1,1), False),
            (tps, Point(2,2), False),
            (tpss, Point(1,1), False),
            (tpss, Point(2,2), False),
        ],
        ids=['Instant Point(1,1)', 'Instant Point(2,2)', 'Discrete Sequence Point(1,1)', 'Discrete Sequence Point(2,2)',
             'Sequence Point(1,1)', 'Sequence Point(2,2)', 'SequenceSet Point(1,1)', 'SequenceSet Point(2,2)']
    )
    def test_always_equal_ever_not_equal(self, temporal, argument, expected):
        assert temporal.always_equal(argument) == expected
        assert temporal.never_not_equal(argument) == expected
        assert temporal.ever_not_equal(argument) == not_(expected)

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tpi, Point(1,1), True),
            (tpi, Point(2,2), False),
            (tpds, Point(1,1), True),
            (tpds, Point(2,2), True),
            (tps, Point(1,1), True),
            (tps, Point(2,2), True),
            (tpss, Point(1,1), True),
            (tpss, Point(2,2), True)
        ],
        ids=['Instant Point(1,1)', 'Instant Point(2,2)', 'Discrete Sequence Point(1,1)', 'Discrete Sequence Point(2,2)',
             'Sequence Point(1,1)', 'Sequence Point(2,2)', 'SequenceSet Point(1,1)', 'SequenceSet Point(2,2)']
    )
    def test_ever_equal_always_not_equal(self, temporal, argument, expected):
        assert temporal.ever_equal(argument) == expected
        assert temporal.always_not_equal(argument) == not_(expected)
        assert temporal.never_equal(argument) == not_(expected)


class TestTGeomPointTemporalComparisons(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    argument = TGeomPointSeq('[Point(2 2)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03]')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('False@2019-09-01')),
            (tpds, TBoolSeq('{False@2019-09-01, False@2019-09-02}')),
            (tps, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
                 '(False@2019-09-01 12:00:00+00, False@2019-09-02]}')),
            (tpss, TBoolSeqSet('{[False@2019-09-01, True@2019-09-01 12:00:00+00],'
                 '(False@2019-09-01 12:00:00+00, False@2019-09-02],[True@2019-09-03]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_equal_temporal(self, temporal, expected):
        assert temporal.temporal_equal(self.argument) == expected
        assert temporal.temporal_not_equal(self.argument) == expected.temporal_not()

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tpi, Point(1,1), TBoolInst('True@2019-09-01')),
            (tpds, Point(1,1), TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tps, Point(1,1), TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02]}')),
            (tpss, Point(1,1), TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),

            (tpi, Point(2,2), TBoolInst('False@2019-09-01')),
            (tpds, Point(2,2), TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tps, Point(2,2), TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tpss, Point(2,2), TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}')),
        ],
        ids=['Instant Point(1,1)', 'Discrete Sequence Point(1,1)', 'Sequence Point(1,1)', 'SequenceSet Point(1,1)',
             'Instant Point(2,2)', 'Discrete Sequence Point(2,2)', 'Sequence Point(2,2)', 'SequenceSet Point(2,2)']
    )
    def test_temporal_equal_point(self, temporal, argument, expected):
        assert temporal.temporal_equal(argument) == expected
        assert temporal.temporal_not_equal(argument) == expected.temporal_not()


class TestTGeomPointRestrictors(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    timestamp = datetime(2019, 9, 1)
    timestamp_set = TimestampSet('{2019-09-01, 2019-09-03}')
    period = Period('[2019-09-01, 2019-09-02]')
    period_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, timestamp, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, timestamp_set, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, period, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, period_set, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, Point(1,1), TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpi, Point(2,2), None),

            (tpds, timestamp, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, timestamp_set, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, period, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, period_set, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, Point(1,1), TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, Point(2,2), TGeomPointSeq('{Point(2 2)@2019-09-02}')),

            (tps, timestamp, TGeomPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, timestamp_set, TGeomPointSeq('{Point(1 1)@2019-09-01}')),
            (tps, period, TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, period_set, TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, Point(1,1), TGeomPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, Point(2,2), TGeomPointSeq('[Point(2 2)@2019-09-02]')),

            (tpss, timestamp, TGeomPointSeqSet('[Point(1 1)@2019-09-01]')),
            (tpss, timestamp_set, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpss, period, TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, period_set,
                TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, Point(1,1), TGeomPointSeqSet('{[Point(1 1)@2019-09-01],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, Point(2,2), TGeomPointSeqSet('{[Point(2 2)@2019-09-02]}'))

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-True',
             'Instant-Point(2,2)', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-True',
             'Discrete Sequence-Point(2,2)', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-True', 'Sequence-Point(2,2)', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-True',
             'SequenceSet-Point(2,2)']
    )
    def test_at(self, temporal, restrictor, expected):
        assert temporal.at(restrictor) == expected


    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, timestamp, None),
            (tpi, timestamp_set, None),
            (tpi, period, None),
            (tpi, period_set, None),
            (tpi, Point(1,1), None),
            (tpi, Point(2,2), TGeomPointInst('Point(1 1)@2019-09-01')),

            (tpds, timestamp, TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, timestamp_set, TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, period, None),
            (tpds, period_set, None),
            (tpds, Point(1,1), TGeomPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, Point(2,2), TGeomPointSeq('{Point(1 1)@2019-09-01}')),

            (tps, timestamp, TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, timestamp_set, TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, period, None),
            (tps, period_set, None),
            (tps, Point(1,1), TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, Point(2,2), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02)}')),

            (tpss, timestamp,
                TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, timestamp_set,
             TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],(Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, period, TGeomPointSeqSet('{[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, period_set, None),
            (tpss, Point(1,1), TGeomPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, Point(2,2), TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02),[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}'))
        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-Point(1,1)',
             'Instant-Point(2,2)', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-Point(1,1)',
             'Discrete Sequence-Point(2,2)', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-Point(1,1)', 'Sequence-Point(2,2)', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-Point(1,1)',
             'SequenceSet-Point(2,2)']
    )
    def test_minus(self, temporal, restrictor, expected):
        assert temporal.minus(restrictor) == expected

    @pytest.mark.parametrize(
        'temporal, restrictor',
        [
            (tpi, timestamp),
            (tpi, timestamp_set),
            (tpi, period),
            (tpi, period_set),
            (tpi, Point(1,1)),
            (tpi, Point(2,2)),

            (tpds, timestamp),
            (tpds, timestamp_set),
            (tpds, period),
            (tpds, period_set),
            (tpds, Point(1,1)),
            (tpds, Point(2,2)),

            (tps, timestamp),
            (tps, timestamp_set),
            (tps, period),
            (tps, period_set),
            (tps, Point(1,1)),
            (tps, Point(2,2)),

            (tpss, timestamp),
            (tpss, timestamp_set),
            (tpss, period),
            (tpss, period_set),
            (tpss, Point(1,1)),
            (tpss, Point(2,2)),

        ],
        ids=['Instant-Timestamp', 'Instant-TimestampSet', 'Instant-Period', 'Instant-PeriodSet', 'Instant-Point(1,1)',
             'Instant-Point(2,2)', 'Discrete Sequence-Timestamp', 'Discrete Sequence-TimestampSet',
             'Discrete Sequence-Period', 'Discrete Sequence-PeriodSet', 'Discrete Sequence-Point(1,1)',
             'Discrete Sequence-Point(2,2)', 'Sequence-Timestamp', 'Sequence-TimestampSet', 'Sequence-Period',
             'Sequence-PeriodSet', 'Sequence-Point(1,1)', 'Sequence-Point(2,2)', 'SequenceSet-Timestamp',
             'SequenceSet-TimestampSet', 'SequenceSet-Period', 'SequenceSet-PeriodSet', 'SequenceSet-Point(1,1)',
             'SequenceSet-Point(2,2)']
    )
    def test_at_minus(self, temporal, restrictor):
        assert TGeomPoint.merge(temporal.at(restrictor), temporal.minus(restrictor)) == temporal


class TestTGeomPointEverSpatialOperations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

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
    def test_temporal_ever_intersects_disjoint(self, temporal, expected):
        assert temporal.is_ever_within_distance(Point(1,1)) == expected
        assert temporal.ever_intersects(Point(1,1)) == expected
        assert temporal.ever_touches(Point(1,1)) == expected

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
    def test_temporal_ever_intersects_disjoint(self, temporal, expected):
        assert temporal.is_ever_disjoint(Point(1,1)) == expected


class TestTGeomPointTemporalSpatialOperations(TestTGeomPoint):
    tpi = TGeomPointInst('Point(1 1)@2019-09-01')
    tpds = TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TBoolInst('True@2019-09-01')),
            (tpds, TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tps, TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02]}')),
            (tpss, TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02],'
                '[True@2019-09-03, True@2019-09-05]}'))
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_temporal_intersects_disjoint(self, temporal, expected):
        assert temporal.intersects(Point(1,1)) == expected
        assert temporal.disjoint(Point(1,1)) == ~expected


class TestTGeomPointComparisonFunctions(TestTGeomPoint):
    tp = TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    other = TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    def test_eq(self):
        _ = self.tp == self.other

    def test_ne(self):
        _ = self.tp != self.other

    def test_lt(self):
        _ = self.tp < self.other

    def test_le(self):
        _ = self.tp <= self.other

    def test_gt(self):
        _ = self.tp > self.other

    def test_ge(self):
        _ = self.tp >= self.other
