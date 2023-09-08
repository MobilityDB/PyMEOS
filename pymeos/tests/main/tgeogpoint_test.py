from copy import copy
from operator import not_
from datetime import datetime, timezone, timedelta

import pytest
import numpy as np
from shapely import Point
import shapely.geometry

from pymeos import TBool, TBoolInst, TBoolSeq, TBoolSeqSet, \
    TFloat, TFloatInst, TFloatSeq, TFloatSeqSet, \
    TGeomPoint, TGeomPointInst, TGeomPointSeq, TGeomPointSeqSet, \
    TGeogPoint, TGeogPointInst, TGeogPointSeq, TGeogPointSeqSet, \
    STBox, TInterpolation, TimestampSet, Period, PeriodSet
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
            (TGeogPointInst('Point(1.5 1.5)@2019-09-01'), TGeogPointInst,
                TInterpolation.NONE),
            (TGeogPointSeq('{Point(1.5 1.5)@2019-09-01, Point(2.5 2.5)@2019-09-02}'), 
                TGeogPointSeq, TInterpolation.DISCRETE),
            (TGeogPointSeq('[Point(1.5 1.5)@2019-09-01, Point(2.5 2.5)@2019-09-02]'), 
                TGeogPointSeq, TInterpolation.LINEAR),
            (TGeogPointSeqSet('{[Point(1.5 1.5)@2019-09-01, Point(2.5 2.5)@2019-09-02],'
                '[Point(1.5 1.5)@2019-09-03, Point(1.5 1.5)@2019-09-05]}'),
                TGeogPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_from_base_constructor(self, source, type, interpolation):
        tp = TGeogPoint.from_base_temporal(shapely.set_srid(shapely.Point(1,1), 4326), source)
        assert isinstance(tp, type)
        assert tp.interpolation() == interpolation

    @pytest.mark.parametrize(
        'source, type, interpolation',
        [
            (datetime(2000, 1, 1), TGeogPointInst, TInterpolation.NONE),
            (TimestampSet('{2019-09-01, 2019-09-02}'), TGeogPointSeq, TInterpolation.DISCRETE),
            (Period('[2019-09-01, 2019-09-02]'), TGeogPointSeq, TInterpolation.LINEAR),
            (PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}'), TGeogPointSeqSet, TInterpolation.LINEAR)
        ],
        ids=['Instant', 'Sequence', 'Discrete Sequence', 'SequenceSet']
    )
    def test_from_base_time_constructor(self, source, type, interpolation):
        tp = TGeogPoint.from_base_time(shapely.set_srid(shapely.Point(1,1), 4326), source, interpolation)
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

    @pytest.mark.parametrize(
        'source, type, expected',
        [
            ('[Point(1 1)@2019-09-01, Point(1.249919068145015 1.250040436011492)@2019-09-02, Point(2 2)@2019-09-05]', TGeogPointSeq,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00]'),
            ('{[Point(1 1)@2019-09-01, POINT(1.249919068145015 1.250040436011492)@2019-09-02, Point(2 2)@2019-09-05],'
             '[Point(1 1)@2019-09-07, Point(1 1)@2019-09-08, Point(1 1)@2019-09-09]}', TGeogPointSeqSet,
             '{[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-05 00:00:00+00], '
             '[POINT(1 1)@2019-09-07 00:00:00+00, POINT(1 1)@2019-09-09 00:00:00+00]}'),
        ],
        ids=['Sequence', 'SequenceSet']
    )
    def test_string_constructor_normalization(self, source, type, expected):
        tp = type(source, normalize=True)
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
        tpi = TGeogPointInst(point=value, timestamp=timestamp)
        assert str(tpi) == 'POINT(1 1)@2019-09-01 00:00:00+00'

    @pytest.mark.parametrize(
        'list, interpolation, normalize, expected',
        [
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.DISCRETE, False,
             '{POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00}'),
            (['Point(1 1)@2019-09-01', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, False,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),

            (['Point(1 1)@2019-09-01', 'Point(1.499885736561676 1.500057091479197)@2019-09-02', 'Point(2 2)@2019-09-03'], TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            ([TGeogPointInst('Point(1 1)@2019-09-01'), TGeogPointInst('Point(1.499885736561676 1.500057091479197)@2019-09-02'), TGeogPointInst('Point(2 2)@2019-09-03')],
             TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
            (['Point(1 1)@2019-09-01', 'Point(1.499885736561676 1.500057091479197)@2019-09-02', TGeogPointInst('Point(2 2)@2019-09-03')], TInterpolation.LINEAR, True,
             '[POINT(1 1)@2019-09-01 00:00:00+00, POINT(2 2)@2019-09-03 00:00:00+00]'),
        ],
        ids=['String Discrete', 'String Linear', 'TGeogPointInst Discrete', 'TGeogPointInst Linear',
             'Mixed Discrete',
             'Mixed Linear', 'String Linear Normalized', 'TGeogPointInst Linear Normalized',
             'Mixed Linear Normalized']
    )
    def test_instant_list_sequence_constructor(self, list, interpolation, normalize, expected):
        tps = TGeogPointSeq(instant_list=list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps) == expected
        assert tps.interpolation() == interpolation

        tps2 = TGeogPointSeq.from_instants(list, interpolation=interpolation, normalize=normalize, upper_inc=True)
        assert str(tps2) == expected
        assert tps2.interpolation() == interpolation

    @pytest.mark.parametrize(
        'temporal',
        [tpi, tpds, tps, tpss, tpi3d, tpds3d, tps3d, tpss3d],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet',
             'Instant 3D', 'Discrete Sequence 3D', 'Sequence 3D', 'SequenceSet 3D']
    )
    def test_from_as_constructor(self, temporal):
        assert temporal == temporal.__class__(str(temporal))
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
            (tpi, STBox('GEODSTBOX XT(((1,1),(1,1)),[2019-09-01, 2019-09-01])')),
            (tpds, STBox('GEODSTBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])')),
            (tps, STBox('GEODSTBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])')),
            (tpss, STBox('GEODSTBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-05])')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_bounding_box(self, temporal, expected):
        assert temporal.bounding_box() == expected

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
            (tpds, tpi),
            (tps, tpi),
            (tpss, tpi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_min_instant(self, temporal, expected):
        assert temporal.min_instant() == expected

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
            (tpi, 1181779687),
            (tpds, 1545137628),
            (tps, 1545137628),
            (tpss, 1008965061)
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_hash(self, temporal, expected):
        assert hash(temporal) == expected

    def test_value_timestamp(self):
        assert self.tpi.value() == Point(1,1)
        assert self.tpi.timestamp() == datetime(year=2019, month=9, day=1, tzinfo=timezone.utc)

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

    def test_sequenceset_sequence_functions(self):
        tpss1 =TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],'
            '[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05], [Point(3 3)@2019-09-06]}')
        assert tpss1.num_sequences() == 3
        assert tpss1.start_sequence() == TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
        assert tpss1.end_sequence() == TGeogPointSeq('[Point(3 3)@2019-09-06]')
        assert tpss1.sequence_n(1) == TGeogPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]')
        assert tpss1.sequences() == [TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
            TGeogPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]'), 
            TGeogPointSeq('[Point(3 3)@2019-09-06]')]


class TestTGeogPointTPointAccessors(TestTGeogPoint):
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
        'temporal, expected',
        [
            (tpi, 0),
            (tpds, 0),
            (tps, 156876.1494),
            (tpss, 156876.1494),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_length(self, temporal, expected):
        assert round(temporal.length(),4) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TFloatInst('0@2019-09-01')),
            (tpds, TFloatSeq('{0@2019-09-01, 0@2019-09-02}')),
            (tps, TFloatSeq('[0@2019-09-01, 156876.1494@2019-09-02]')),
            (tpss, TFloatSeqSet('{[0@2019-09-01, 156876.1494@2019-09-02],'
                '[156876.1494@2019-09-03, 156876.1494@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_cumulative_length(self, temporal, expected):
        assert temporal.cumulative_length().round(4) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, None),
            (tpds, None),
            (tps, TFloatSeq('Interp=Step;[1.8157@2019-09-01, 1.8157@2019-09-02]')),
            (tpss, TFloatSeqSet('Interp=Step;{[1.8157@2019-09-01, 1.8157@2019-09-02],'
                '[0@2019-09-03, 0@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_speed(self, temporal, expected):
        if expected is None:
            assert temporal.speed() is None
        else:
            assert temporal.speed().round(4) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TFloatInst('1@2019-09-01')),
            (tpds, TFloatSeq('{1@2019-09-01, 2@2019-09-02}')),
            (tps, TFloatSeq('[1@2019-09-01, 2@2019-09-02]')),
            (tpss, TFloatSeqSet('{[1@2019-09-01, 2@2019-09-02],'
                '[1@2019-09-03, 1@2019-09-05]}')),
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
                '[1@2019-09-03, 1@2019-09-05]}')),
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
            (tpss, False),
            (tpi3d, True),
            (tpds3d, True),
            (tps3d, True),
            (tpss3d, True),
        ],
        ids=['Instant 2D', 'Discrete Sequence 2D', 'Sequence 2D', 'SequenceSet 2D',
             'Instant 3D', 'Discrete Sequence 3D', 'Sequence 3D', 'SequenceSet 3D']
    )
    def test_has_z(self, temporal, expected):
        assert temporal.has_z() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi3d, True),
            (tpds3d, True),
            (tps3d, True),
            (tpss3d, True),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_has_z(self, temporal, expected):
        assert temporal.has_z() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, []),
            (tpds, []),
            (tps, [STBox('GEODSTBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])')]),
            (tpss, [STBox('GEODSTBOX XT(((1,1),(2,2)),[2019-09-01, 2019-09-02])'),
                STBox('GEODSTBOX XT(((1,1),(1,1)),[2019-09-03, 2019-09-05])')]),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_stboxes(self, temporal, expected):
        assert temporal.stboxes() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, True),
            (tpds, True),
            (tps, True),
            (tpss, True),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_is_simple(self, temporal, expected):
        assert temporal.is_simple() == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TFloatInst('0.7846@2019-09-01')),
            (tpds, TFloatSeq('{0.7846@2019-09-01,0.7846@2019-09-02}')),
            (tps, TFloatSeq('[0.7846@2019-09-01,0.7846@2019-09-02]')),
            (tpss, TFloatSeqSet('{[0.7846@2019-09-01,0.7846@2019-09-02],'
                '[0.7846@2019-09-03,0.7846@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_bearing(self, temporal, expected):
        assert temporal.bearing(shapely.set_srid(shapely.Point(3,3), 4326)).round(4) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, None),
            (tpds, 45.1705),
            (tps, 45.1705),
            (tpss, None),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_direction(self, temporal, expected):
        res = temporal.direction()
        result = round(np.rad2deg(res), 4) if res is not None else None
        assert result == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, None),
            (tpds, None),
            (tps, TFloatSeqSet('Interp=Step;{[0.7884@2019-09-01,0.7884@2019-09-02]}')),
            (tpss, TFloatSeqSet('Interp=Step;{[0.7884@2019-09-01,0.7884@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_azimuth(self, temporal, expected):
        res = temporal.azimuth()
        result = res.round(4) if res is not None else None
        assert result == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, None),
            (tpds, None),
            (tps, TFloatSeq('{0@2019-09-01,0@2019-09-02}')),
            (tpss, TFloatSeqSet('{0@2019-09-01,0@2019-09-02}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_angular_difference(self, temporal, expected):
        res = temporal.angular_difference()
        result = res.to_degrees() if res is not None else None
        assert result == expected

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


class TestTGeogPointConversions(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (tpi, TGeomPointInst('Point(1 1)@2019-09-01')),
            (tpds, TGeomPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tps, TGeomPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tpss, TGeomPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],'
                '[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_geometric(self, temporal, expected):
        assert temporal.to_geometric() == expected


class TestTGeogPointTransformations(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    tps_d = TGeogPointSeq('[Point(1 1)@2019-09-01]')
    tpss_d = TGeogPointSeqSet('{[Point(1 1)@2019-09-01],[Point(2 2)@2019-09-03]}')
    tps_s = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02]')
    tpss_s = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02],'
        '[Point(2 2)@2019-09-03, Point(2 2)@2019-09-05]}')
    tps_l = TGeogPointSeq('Interp=Step;[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss_l = TGeogPointSeqSet('Interp=Step;{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],'
        '[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TGeogPointInst('Point(1 1)@2019-09-01'), tpi),
            (TGeogPointSeq('{Point(1 1)@2019-09-01}'), tpi),
            (TGeogPointSeq('[Point(1 1)@2019-09-01]'), tpi),
            (TGeogPointSeqSet('{[Point(1 1)@2019-09-01]}'), tpi),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_instant(self, temporal, expected):
        temp = temporal.to_instant()
        assert isinstance(temp, TGeogPointInst)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, interpolation, expected',
        [
            (TGeogPointInst('Point(1 1)@2019-09-01'), TInterpolation.LINEAR,
                TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}'),
                TInterpolation.DISCRETE,
                TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
                TInterpolation.LINEAR,
                TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}'),
                TInterpolation.LINEAR,
                TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequence(self, temporal, interpolation, expected):
        temp = temporal.to_sequence(interpolation)
        assert isinstance(temp, TGeogPointSeq)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, interpolation, expected',
        [
            (TGeogPointInst('Point(1 1)@2019-09-01'), TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01]}')),
            (TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}'),
                TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01], [Point(2 2)@2019-09-02]}')),
            (TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]'),
                TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}'),
                TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_to_sequenceset(self, temporal, interpolation, expected):
        temp = temporal.to_sequenceset(interpolation)
        assert isinstance(temp, TGeogPointSeqSet)
        assert temp == expected

    @pytest.mark.parametrize(
        'temporal, interpolation, expected',
        [
            (tpi, TInterpolation.DISCRETE,
                TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, TInterpolation.DISCRETE, tpds),
            (tps_d, TInterpolation.DISCRETE,
                TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpss_d, TInterpolation.DISCRETE,
                TGeogPointSeq('{Point(1 1)@2019-09-01,Point(2 2)@2019-09-03}')),

            (tpi, TInterpolation.STEPWISE, 
                TGeogPointSeq('Interp=Step;[Point(1 1)@2019-09-01]')),
            (tpds, TInterpolation.STEPWISE, 
                TGeogPointSeqSet('Interp=Step;{[Point(1 1)@2019-09-01], [Point(2 2)@2019-09-02]}')),
            (tps_s, TInterpolation.STEPWISE,
                TGeogPointSeq('Interp=Step;[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02]')),
            (tpss_s, TInterpolation.STEPWISE,
                TGeogPointSeqSet('Interp=Step;{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02],'
                '[Point(2 2)@2019-09-03, Point(2 2)@2019-09-05]}')),

            (tpi, TInterpolation.LINEAR, 
                TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (tpds, TInterpolation.LINEAR, 
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01], [Point(2 2)@2019-09-02]}')),
            (tps_l, TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02), [Point(2 2)@2019-09-02]}')),
            (tpss_l, TInterpolation.LINEAR,
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(1 1)@2019-09-02),'
                '[Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
        ],
        ids=['Instant to discrete', 'Discrete Sequence to discrete', 'Sequence to discrete', 'SequenceSet to discrete',
             'Instant to step', 'Discrete Sequence to step', 'Sequence to step', 'SequenceSet to step',
             'Instant to linear', 'Discrete Sequence to linear', 'Sequence to linear', 'SequenceSet to linear']
    )
    def test_set_interpolation(self, temporal, interpolation, expected):
        assert temporal.set_interpolation(interpolation) == expected

    @pytest.mark.parametrize(
        'tpoint, delta, expected',
        [(tpi, timedelta(days=4), TGeogPointInst('Point(1 1)@2019-09-05')),
         (tpi, timedelta(days=-4), TGeogPointInst('Point(1 1)@2019-08-28')),
         (tpi, timedelta(hours=2), TGeogPointInst('Point(1 1)@2019-09-01 02:00:00')),
         (tpi, timedelta(hours=-2), TGeogPointInst('Point(1 1)@2019-08-31 22:00:00')), 
         (tpds, timedelta(days=4), TGeogPointSeq('{Point(1 1)@2019-09-05, Point(2 2)@2019-09-06}')),
         (tpds, timedelta(days=-4), TGeogPointSeq('{Point(1 1)@2019-08-28, Point(2 2)@2019-08-29}')),
         (tpds, timedelta(hours=2), TGeogPointSeq('{Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00}')),
         (tpds, timedelta(hours=-2), TGeogPointSeq('{Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00}')),
         (tps, timedelta(days=4), TGeogPointSeq('[Point(1 1)@2019-09-05, Point(2 2)@2019-09-06]')),
         (tps, timedelta(days=-4), TGeogPointSeq('[Point(1 1)@2019-08-28, Point(2 2)@2019-08-29]')),
         (tps, timedelta(hours=2), TGeogPointSeq('[Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00]')),
         (tps, timedelta(hours=-2), TGeogPointSeq('[Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00]')),
         (tpss, timedelta(days=4),
             TGeogPointSeqSet('{[Point(1 1)@2019-09-05, Point(2 2)@2019-09-06],[Point(1 1)@2019-09-07, Point(1 1)@2019-09-09]}')),
         (tpss, timedelta(days=-4),
             TGeogPointSeqSet('{[Point(1 1)@2019-08-28, Point(2 2)@2019-08-29],[Point(1 1)@2019-08-30, Point(1 1)@2019-09-01]}')),
         (tpss, timedelta(hours=2),
             TGeogPointSeqSet('{[Point(1 1)@2019-09-01 02:00:00, Point(2 2)@2019-09-02 02:00:00],'
                         '[Point(1 1)@2019-09-03 02:00:00, Point(1 1)@2019-09-05 02:00:00]}')),
         (tpss, timedelta(hours=-2),
             TGeogPointSeqSet('{[Point(1 1)@2019-08-31 22:00:00, Point(2 2)@2019-09-01 22:00:00],'
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
        [(tpi, timedelta(days=4), TGeogPointInst('Point(1 1)@2019-09-01')),
         (tpi, timedelta(hours=2), TGeogPointInst('Point(1 1)@2019-09-01')),
         (tpds, timedelta(days=4), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-05}')),
         (tpds, timedelta(hours=2), TGeogPointSeq('{Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 02:00:00}')),
         (tps, timedelta(days=4), TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-05]')),
         (tps, timedelta(hours=2), TGeogPointSeq('[Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 02:00:00]')),
         (tpss, timedelta(days=4),
             TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
         (tpss, timedelta(hours=2),
             TGeogPointSeqSet('{[Point(1 1)@2019-09-01 00:00:00, Point(2 2)@2019-09-01 00:30:00],'
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
             TGeogPointSeqSet('{[Point(1 1)@2019-09-05 00:00:00, Point(2 2)@2019-09-05 00:30:00],'
             '[Point(1 1)@2019-09-05 01:00:00, Point(1 1)@2019-09-05 02:00:00]}')

    @pytest.mark.parametrize(
        'tpoint, delta, expected',
        [(tpi, timedelta(days=4), TGeogPointInst('Point(1 1)@2019-09-01')),
         (tpi, timedelta(hours=12), TGeogPointInst('Point(1 1)@2019-09-01')),
         (tpds, timedelta(days=4), TGeogPointSeq('{Point(1 1)@2019-09-01}')),
         (tpds, timedelta(hours=12), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
         (tps, timedelta(days=4), TGeogPointSeq('{Point(1 1)@2019-09-01}')),
         (tps, timedelta(hours=12), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1.5 1.5)@2019-09-01 12:00:00, Point(2 2)@2019-09-02}')),
         (tpss, timedelta(days=4),
             TGeogPointSeq('{Point(1 1)@2019-09-01,Point(1 1)@2019-09-05}')),
         (tpss, timedelta(hours=12),
             TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1.5 1.5)@2019-09-01 12:00:00,'
                'Point(2 2)@2019-09-02, Point(1 1)@2019-09-03, Point(1 1)@2019-09-03 12:00:00, '
                'Point(1 1)@2019-09-04, Point(1 1)@2019-09-04 12:00:00, Point(1 1)@2019-09-05}')),
         ],
        ids=['Instant days', 'Instant hours',
             'Discrete Sequence days', 'Discrete Sequence hours',
             'Sequence days', 'Sequence hours',
             'Sequence Set days', 'Sequence Set hours'
             ]
    )
    def test_temporal_sample(self, tpoint, delta, expected):
        assert tpoint.temporal_sample(delta).round(1) == expected

    @pytest.mark.parametrize(
        'tpoint, delta, expected',
        [(tps, timedelta(days=4), None),
         (tps, timedelta(hours=12), None),
         (tpss, timedelta(days=4), None),
         (tpss, timedelta(hours=12),
             TGeogPointSeq('[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]')),
         ],
        ids=['Sequence days', 'Sequence hours',
             'Sequence Set days', 'Sequence Set hours']
    )
    def test_stops(self, tpoint, delta, expected):
        assert tpoint.stops(0.1, delta) == expected

    @pytest.mark.parametrize(
        'temporal, expected',
        [
            (TGeogPointInst('Point(1.123456789 1.123456789)@2019-09-01'), 
                TGeogPointInst('Point(1.12 1.12)@2019-09-01')),
            (TGeogPointSeq('{Point(1.123456789 1.123456789)@2019-09-01,'
                'Point(2.123456789 2.123456789)@2019-09-02}'), 
                TGeogPointSeq('{Point(1.12 1.12)@2019-09-01,Point(2.12 2.12)@2019-09-02}')),
            (TGeogPointSeq('[Point(1.123456789 1.123456789)@2019-09-01,'
                'Point(2.123456789 2.123456789)@2019-09-02]'), 
                TGeogPointSeq('[Point(1.12 1.12)@2019-09-01,Point(2.12 2.12)@2019-09-02]')),
            (TGeogPointSeqSet('{[Point(1.123456789 1.123456789)@2019-09-01,'
                'Point(2.123456789 2.123456789)@2019-09-02],' 
                '[Point(1.123456789 1.123456789)@2019-09-03,'
                'Point(1.123456789 1.123456789)@2019-09-05]}'), 
                TGeogPointSeq('{[Point(1.12 1.12)@2019-09-01,Point(2.12 2.12)@2019-09-02],'
                '[Point(1.12 1.12)@2019-09-03,Point(1.12 1.12)@2019-09-05]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_round(self, temporal, expected):
        assert temporal.round(maxdd=2)


class TestTGeogPointModifications(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tpi, TGeogPointSeq('{Point(1 1)@2019-09-03}'), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpds, TGeogPointSeq('{Point(1 1)@2019-09-03}'), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeogPointSeq('[Point(1 1)@2019-09-03]'), TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03]}')),
            (tpss, TGeogPointSeq('[Point(1 1)@2019-09-06]'),
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05],[Point(1 1)@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_insert(self, temporal, sequence, expected):
        assert temporal.insert(sequence) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tpi, TGeogPointInst('Point(2 2)@2019-09-01'), TGeogPointInst('Point(2 2)@2019-09-01')),
            (tpds, TGeogPointInst('Point(2 2)@2019-09-01'), TGeogPointSeq('{Point(2 2)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tps, TGeogPointInst('Point(2 2)@2019-09-01'), 
                TGeogPointSeqSet('{[Point(2 2)@2019-09-01], (Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, TGeogPointInst('Point(2 2)@2019-09-01'),
                TGeogPointSeqSet('{[Point(2 2)@2019-09-01], (Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
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
            (tpds, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc), TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tps, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, datetime(year=2019, month=9, day=1, tzinfo=timezone.utc),
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
        ],
        ids=['Instant intersection', 'Instant disjoint', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_delete(self, temporal, time, expected):
        assert temporal.delete(time) == expected

    @pytest.mark.parametrize(
        'temporal, instant, expected',
        [
            (tpi, TGeogPointInst('Point(1 1)@2019-09-02'), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-02}')),
            (tpds, TGeogPointInst('Point(1 1)@2019-09-03'), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeogPointInst('Point(1 1)@2019-09-03'), TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03]')),
            (tpss, TGeogPointInst('Point(1 1)@2019-09-06'),
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-06]}')),
        ],
        ids=['Instant', 'Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_instant(self, temporal, instant, expected):
        assert temporal.append_instant(instant) == expected

    @pytest.mark.parametrize(
        'temporal, sequence, expected',
        [
            (tpds, TGeogPointSeq('{Point(1 1)@2019-09-03}'), TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02, Point(1 1)@2019-09-03}')),
            (tps, TGeogPointSeq('[Point(1 1)@2019-09-03]'), TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02], [Point(1 1)@2019-09-03]}')),
            (tpss, TGeogPointSeq('[Point(1 1)@2019-09-06]'),
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05],[Point(1 1)@2019-09-06]}')),
        ],
        ids=['Discrete Sequence', 'Sequence', 'SequenceSet']
    )
    def test_append_sequence(self, temporal, sequence, expected):
        assert temporal.append_sequence(sequence) == expected


class TestTGeogPointRestrictors(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    timestamp = datetime(2019, 9, 1)
    timestamp_set = TimestampSet('{2019-09-01, 2019-09-03}')
    period = Period('[2019-09-01, 2019-09-02]')
    period_set = PeriodSet('{[2019-09-01, 2019-09-02],[2019-09-03, 2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, restrictor, expected',
        [
            (tpi, timestamp, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, timestamp_set, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, period, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, period_set, TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointInst('Point(1 1)@2019-09-01')),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), None),

            (tpds, timestamp, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, timestamp_set, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, period, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, period_set, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('{Point(2 2)@2019-09-02}')),

            (tps, timestamp, TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, timestamp_set, TGeogPointSeq('{Point(1 1)@2019-09-01}')),
            (tps, period, TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, period_set, TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('[Point(1 1)@2019-09-01]')),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('[Point(2 2)@2019-09-02]')),

            (tpss, timestamp, TGeogPointSeqSet('[Point(1 1)@2019-09-01]')),
            (tpss, timestamp_set, TGeogPointSeq('{Point(1 1)@2019-09-01, Point(1 1)@2019-09-03}')),
            (tpss, period, TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, period_set, TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],'
                '[Point(1 1)@2019-09-03,Point(1 1)@2019-09-05]}')),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeqSet('{[Point(2 2)@2019-09-02]}'))

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
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), None),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointInst('Point(1 1)@2019-09-01')),

            (tpds, timestamp, TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, timestamp_set, TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, period, None),
            (tpds, period_set, None),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), TGeogPointSeq('{Point(2 2)@2019-09-02}')),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), TGeogPointSeq('{Point(1 1)@2019-09-01}')),

            (tps, timestamp, TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, timestamp_set, TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, period, None),
            (tps, period_set, None),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), 
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02)}')),

            (tpss, timestamp,
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, timestamp_set,
             TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],(Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, period, TGeogPointSeqSet('{[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')),
            (tpss, period_set, None),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), 
                TGeogPointSeqSet('{(Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]}')),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326),
                TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02),[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}'))
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
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326)),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326)),

            (tpds, timestamp),
            (tpds, timestamp_set),
            (tpds, period),
            (tpds, period_set),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326)),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326)),

            (tps, timestamp),
            (tps, timestamp_set),
            (tps, period),
            (tps, period_set),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326)),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326)),

            (tpss, timestamp),
            (tpss, timestamp_set),
            (tpss, period),
            (tpss, period_set),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326)),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326)),

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
        assert TGeogPoint.merge(temporal.at(restrictor), temporal.minus(restrictor)) == temporal


class TestTGeogPointComparisons(TestTGeogPoint):
    tp = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    other = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

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


class TestTGeogPointEverAlwaysComparisons(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02], [Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')

    @pytest.mark.parametrize(
        'temporal, argument, expected',
        [
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), True),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), False),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), False),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), False),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), False),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), False),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), False),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326), False),
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
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), True),
            (tpi, shapely.set_srid(shapely.Point(2,2), 4326), False),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), True),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326), True),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), True),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326), True),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), True),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326), True)
        ],
        ids=['Instant Point(1,1)', 'Instant Point(2,2)', 'Discrete Sequence Point(1,1)', 'Discrete Sequence Point(2,2)',
             'Sequence Point(1,1)', 'Sequence Point(2,2)', 'SequenceSet Point(1,1)', 'SequenceSet Point(2,2)']
    )
    def test_ever_equal_always_not_equal(self, temporal, argument, expected):
        assert temporal.ever_equal(argument) == expected
        assert temporal.always_not_equal(argument) == not_(expected)
        assert temporal.never_equal(argument) == not_(expected)


class TestTGeogPointTemporalComparisons(TestTGeogPoint):
    tpi = TGeogPointInst('Point(1 1)@2019-09-01')
    tpds = TGeogPointSeq('{Point(1 1)@2019-09-01, Point(2 2)@2019-09-02}')
    tps = TGeogPointSeq('[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02]')
    tpss = TGeogPointSeqSet('{[Point(1 1)@2019-09-01, Point(2 2)@2019-09-02],[Point(1 1)@2019-09-03, Point(1 1)@2019-09-05]}')
    argument = TGeogPointSeq('[Point(2 2)@2019-09-01, Point(1 1)@2019-09-02, Point(1 1)@2019-09-03]')

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
            (tpi, shapely.set_srid(shapely.Point(1,1), 4326), 
                TBoolInst('True@2019-09-01')),
            (tpds, shapely.set_srid(shapely.Point(1,1), 4326), 
                TBoolSeq('{True@2019-09-01, False@2019-09-02}')),
            (tps, shapely.set_srid(shapely.Point(1,1), 4326), 
                TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02]}')),
            (tpss, shapely.set_srid(shapely.Point(1,1), 4326), 
                TBoolSeqSet('{[True@2019-09-01], (False@2019-09-01, False@2019-09-02],[True@2019-09-03, True@2019-09-05]}')),

            (tpi, shapely.set_srid(shapely.Point(2,2), 4326),
                TBoolInst('False@2019-09-01')),
            (tpds, shapely.set_srid(shapely.Point(2,2), 4326),
                TBoolSeq('{False@2019-09-01, True@2019-09-02}')),
            (tps, shapely.set_srid(shapely.Point(2,2), 4326),
                TBoolSeq('[False@2019-09-01, True@2019-09-02]')),
            (tpss, shapely.set_srid(shapely.Point(2,2), 4326),
                TBoolSeqSet('{[False@2019-09-01, True@2019-09-02],[False@2019-09-03, False@2019-09-05]}')),
        ],
        ids=['Instant Point(1,1)', 'Discrete Sequence Point(1,1)', 'Sequence Point(1,1)', 'SequenceSet Point(1,1)',
             'Instant Point(2,2)', 'Discrete Sequence Point(2,2)', 'Sequence Point(2,2)', 'SequenceSet Point(2,2)']
    )
    def test_temporal_equal_point(self, temporal, argument, expected):
        assert temporal.temporal_equal(argument) == expected
        assert temporal.temporal_not_equal(argument) == expected.temporal_not()


