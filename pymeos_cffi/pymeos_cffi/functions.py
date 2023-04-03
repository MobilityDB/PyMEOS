from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List, Union

import _meos_cffi
import postgis as pg
import shapely.geometry as spg
from dateutil.parser import parse
from shapely import wkt, wkb
from shapely.geometry.base import BaseGeometry
from spans.types import floatrange, intrange

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


def create_pointer(object: 'Any', type: str) -> 'Any *':
    return _ffi.new(f'{type} *', object)
    

def get_address(value: 'Any') -> 'Any *':
    return _ffi.addressof(value)


def datetime_to_timestamptz(dt: datetime) -> int:
    return _lib.pg_timestamptz_in(dt.strftime('%Y-%m-%d %H:%M:%S%z').encode('utf-8'), -1)


def timestamptz_to_datetime(ts: int) -> datetime:
    return parse(pg_timestamptz_out(ts))


def timedelta_to_interval(td: timedelta) -> Any:
    return _ffi.new('Interval *', {'time': td.microseconds + td.seconds * 1000000, 'day': td.days, 'month': 0})


def interval_to_timedelta(interval: Any) -> timedelta:
    # TODO fix for months/years
    return timedelta(days=interval.day, microseconds=interval.time)


def geometry_to_gserialized(geom: Union[pg.Geometry, BaseGeometry]) -> 'GSERIALIZED *':
    if isinstance(geom, pg.Geometry):
        text = geom.to_ewkb()
    elif isinstance(geom, BaseGeometry):
        text = wkb.dumps(geom, hex=True)
    else:
        raise TypeError('Parameter geom must be either a PostGIS Geometry or a Shapely BaseGeometry')
    return gserialized_in(text, -1)


def gserialized_to_shapely_point(geom: 'const GSERIALIZED *', precision: int = 6) -> spg.Point:
    return wkt.loads(gserialized_as_text(geom, precision))


def gserialized_to_shapely_geometry(geom: 'const GSERIALIZED *', precision: int = 6) -> BaseGeometry:
    return wkt.loads(gserialized_as_text(geom, precision))


def intrange_to_intspan(irange: intrange) -> 'Span *':
    return intspan_make(irange.lower, irange.upper, irange.lower_inc, irange.upper_inc)


def intspan_to_intrange(ispan: 'Span *') -> intrange:
    return intrange(intspan_lower(ispan), intspan_upper(ispan), ispan.lower_inc, ispan.upper_inc)


def floatrange_to_floatspan(frange: floatrange) -> 'Span *':
    return floatspan_make(frange.lower, frange.upper, frange.lower_inc, frange.upper_inc)


def floatspan_to_floatrange(fspan: 'Span *') -> floatrange:
    return floatrange(floatspan_lower(fspan), floatspan_upper(fspan), fspan.lower_inc, fspan.upper_inc)


def as_tinstant(temporal: 'Temporal *') -> 'TInstant *':
    return _ffi.cast('TInstant *', temporal)


def as_tsequence(temporal: 'Temporal *') -> 'TSequence *':
    return _ffi.cast('TSequence *', temporal)


def as_tsequenceset(temporal: 'Temporal *') -> 'TSequenceSet *':
    return _ffi.cast('TSequenceSet *', temporal)


# -----------------------------------------------------------------------------
# ----------------------End of manually-defined functions----------------------
# -----------------------------------------------------------------------------


def lwpoint_make(srid: 'int32_t', hasz: int, hasm: int, p: 'const POINT4D *') -> 'LWPOINT *':
    srid_converted = _ffi.cast('int32_t', srid)
    p_converted = _ffi.cast('const POINT4D *', p)
    result = _lib.lwpoint_make(srid_converted, hasz, hasm, p_converted)
    return result if result != _ffi.NULL else None


def lwgeom_from_gserialized(g: 'const GSERIALIZED *') -> 'LWGEOM *':
    g_converted = _ffi.cast('const GSERIALIZED *', g)
    result = _lib.lwgeom_from_gserialized(g_converted)
    return result if result != _ffi.NULL else None


def gserialized_from_lwgeom(geom: 'LWGEOM *') -> 'GSERIALIZED *':
    geom_converted = _ffi.cast('LWGEOM *', geom)
    size_converted = _ffi.NULL
    result = _lib.gserialized_from_lwgeom(geom_converted, size_converted)
    return result if result != _ffi.NULL else None


def lwgeom_get_srid(geom: 'const LWGEOM *') -> 'int32_t':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_get_srid(geom_converted)
    return result if result != _ffi.NULL else None


def lwpoint_get_x(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_x(point_converted)
    return result if result != _ffi.NULL else None


def lwpoint_get_y(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_y(point_converted)
    return result if result != _ffi.NULL else None


def lwpoint_get_z(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_z(point_converted)
    return result if result != _ffi.NULL else None


def lwpoint_get_m(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_m(point_converted)
    return result if result != _ffi.NULL else None


def lwgeom_has_z(geom: 'const LWGEOM *') -> 'int':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_has_z(geom_converted)
    return result if result != _ffi.NULL else None


def lwgeom_has_m(geom: 'const LWGEOM *') -> 'int':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_has_m(geom_converted)
    return result if result != _ffi.NULL else None


def meos_initialize(tz_str: "Optional[str]") -> None:
    tz_str_converted = tz_str.encode('utf-8') if tz_str is not None else _ffi.NULL
    _lib.meos_initialize(tz_str_converted)


def meos_finalize() -> None:
    _lib.meos_finalize()


def bool_in(in_str: str) -> 'bool':
    in_str_converted = in_str.encode('utf-8')
    result = _lib.bool_in(in_str_converted)
    return result if result != _ffi.NULL else None


def bool_out(b: bool) -> str:
    result = _lib.bool_out(b)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_date_in(string: str) -> 'DateADT':
    string_converted = string.encode('utf-8')
    result = _lib.pg_date_in(string_converted)
    return result if result != _ffi.NULL else None


def pg_date_out(date: 'DateADT') -> str:
    date_converted = _ffi.cast('DateADT', date)
    result = _lib.pg_date_out(date_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_interval_cmp(interval1: 'const Interval *', interval2: 'const Interval *') -> 'int':
    interval1_converted = _ffi.cast('const Interval *', interval1)
    interval2_converted = _ffi.cast('const Interval *', interval2)
    result = _lib.pg_interval_cmp(interval1_converted, interval2_converted)
    return result if result != _ffi.NULL else None


def pg_interval_in(string: str, typmod: int) -> 'Interval *':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_interval_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_interval_make(years: int, months: int, weeks: int, days: int, hours: int, mins: int, secs: float) -> 'Interval *':
    years_converted = _ffi.cast('int32', years)
    months_converted = _ffi.cast('int32', months)
    weeks_converted = _ffi.cast('int32', weeks)
    days_converted = _ffi.cast('int32', days)
    hours_converted = _ffi.cast('int32', hours)
    mins_converted = _ffi.cast('int32', mins)
    result = _lib.pg_interval_make(years_converted, months_converted, weeks_converted, days_converted, hours_converted, mins_converted, secs)
    return result if result != _ffi.NULL else None


def pg_interval_mul(span: 'const Interval *', factor: float) -> 'Interval *':
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_interval_mul(span_converted, factor)
    return result if result != _ffi.NULL else None


def pg_interval_out(span: 'const Interval *') -> str:
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_interval_out(span_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_interval_pl(span1: 'const Interval *', span2: 'const Interval *') -> 'Interval *':
    span1_converted = _ffi.cast('const Interval *', span1)
    span2_converted = _ffi.cast('const Interval *', span2)
    result = _lib.pg_interval_pl(span1_converted, span2_converted)
    return result if result != _ffi.NULL else None


def pg_time_in(string: str, typmod: int) -> 'TimeADT':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_time_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_time_out(time: 'TimeADT') -> str:
    time_converted = _ffi.cast('TimeADT', time)
    result = _lib.pg_time_out(time_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamp_in(string: str, typmod: int) -> 'Timestamp':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamp_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_timestamp_mi(dt1: int, dt2: int) -> 'Interval *':
    dt1_converted = _ffi.cast('TimestampTz', dt1)
    dt2_converted = _ffi.cast('TimestampTz', dt2)
    result = _lib.pg_timestamp_mi(dt1_converted, dt2_converted)
    return result if result != _ffi.NULL else None


def pg_timestamp_mi_interval(timestamp: int, span: 'const Interval *') -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_timestamp_mi_interval(timestamp_converted, span_converted)
    return result if result != _ffi.NULL else None


def pg_timestamp_out(dt: int) -> str:
    dt_converted = _ffi.cast('Timestamp', dt)
    result = _lib.pg_timestamp_out(dt_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamp_pl_interval(timestamp: int, span: 'const Interval *') -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_timestamp_pl_interval(timestamp_converted, span_converted)
    return result if result != _ffi.NULL else None


def pg_timestamptz_in(string: str, typmod: int) -> 'TimestampTz':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamptz_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_timestamptz_out(dt: int) -> str:
    dt_converted = _ffi.cast('TimestampTz', dt)
    result = _lib.pg_timestamptz_out(dt_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_ewkb(geom: 'const GSERIALIZED *', type: str) -> 'bytea *':
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    type_converted = type.encode('utf-8')
    result = _lib.gserialized_as_ewkb(geom_converted, type_converted)
    return result if result != _ffi.NULL else None


def gserialized_as_ewkt(geom: 'const GSERIALIZED *', precision: int) -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    result = _lib.gserialized_as_ewkt(geom_converted, precision)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_geojson(geom: 'const GSERIALIZED *', option: int, precision: int, srs: "Optional[str]") -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    srs_converted = srs.encode('utf-8') if srs is not None else _ffi.NULL
    result = _lib.gserialized_as_geojson(geom_converted, option, precision, srs_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_hexewkb(geom: 'const GSERIALIZED *', type: str) -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    type_converted = type.encode('utf-8')
    result = _lib.gserialized_as_hexewkb(geom_converted, type_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_text(geom: 'const GSERIALIZED *', precision: int) -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    result = _lib.gserialized_as_text(geom_converted, precision)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_from_ewkb(bytea_wkb: 'const bytea *', srid: int) -> 'GSERIALIZED *':
    bytea_wkb_converted = _ffi.cast('const bytea *', bytea_wkb)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.gserialized_from_ewkb(bytea_wkb_converted, srid_converted)
    return result if result != _ffi.NULL else None


def gserialized_from_geojson(geojson: str) -> 'GSERIALIZED *':
    geojson_converted = geojson.encode('utf-8')
    result = _lib.gserialized_from_geojson(geojson_converted)
    return result if result != _ffi.NULL else None


def gserialized_from_hexewkb(wkt: str) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.gserialized_from_hexewkb(wkt_converted)
    return result if result != _ffi.NULL else None


def gserialized_from_text(wkt: str, srid: int) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.gserialized_from_text(wkt_converted, srid)
    return result if result != _ffi.NULL else None


def gserialized_in(input: str, geom_typmod: int) -> 'GSERIALIZED *':
    input_converted = input.encode('utf-8')
    geom_typmod_converted = _ffi.cast('int32', geom_typmod)
    result = _lib.gserialized_in(input_converted, geom_typmod_converted)
    return result if result != _ffi.NULL else None


def gserialized_out(geom: 'const GSERIALIZED *') -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    result = _lib.gserialized_out(geom_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pgis_gserialized_same(geom1: 'const GSERIALIZED *', geom2: 'const GSERIALIZED *') -> 'bool':
    geom1_converted = _ffi.cast('const GSERIALIZED *', geom1)
    geom2_converted = _ffi.cast('const GSERIALIZED *', geom2)
    result = _lib.pgis_gserialized_same(geom1_converted, geom2_converted)
    return result if result != _ffi.NULL else None


def bigintset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintset_in(string_converted)
    return result if result != _ffi.NULL else None


def bigintset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.bigintset_out(set_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintspan_in(string_converted)
    return result if result != _ffi.NULL else None


def bigintspan_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_out(s_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintspanset_in(string_converted)
    return result if result != _ffi.NULL else None


def bigintspanset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_out(ss_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.floatset_in(string_converted)
    return result if result != _ffi.NULL else None


def floatset_out(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.floatset_out(set_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.floatspan_in(string_converted)
    return result if result != _ffi.NULL else None


def floatspan_out(s: 'const Span *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_out(s_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.floatspanset_in(string_converted)
    return result if result != _ffi.NULL else None


def floatspanset_out(ss: 'const SpanSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_out(ss_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geogset_out(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geogset_out(set_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geomset_out(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geomset_out(set_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geoset_as_text(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_as_text(set_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geoset_as_ewkt(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_as_ewkt(set_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.intset_in(string_converted)
    return result if result != _ffi.NULL else None


def intset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.intset_out(set_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.intspan_in(string_converted)
    return result if result != _ffi.NULL else None


def intspan_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_out(s_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.intspanset_in(string_converted)
    return result if result != _ffi.NULL else None


def intspanset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_out(ss_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def period_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.period_in(string_converted)
    return result if result != _ffi.NULL else None


def period_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_out(s_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def periodset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.periodset_in(string_converted)
    return result if result != _ffi.NULL else None


def periodset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.periodset_out(ss_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def set_as_wkb(s: 'const Set *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    s_converted = _ffi.cast('const Set *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.set_as_wkb(s_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def set_as_hexwkb(s: 'const Set *', variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast('const Set *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.set_as_hexwkb(s_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def set_from_hexwkb(hexwkb: str) -> 'Set *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.set_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def set_from_wkb(wkb: 'const uint8_t *', size: int) -> 'Set *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.set_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def set_out(s: 'const Set *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_out(s_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def span_as_wkb(s: 'const Span *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_wkb(s_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def span_as_hexwkb(s: 'const Span *', variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_hexwkb(s_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def span_from_hexwkb(hexwkb: str) -> 'Span *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.span_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def span_from_wkb(wkb: 'const uint8_t *', size: int) -> 'Span *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.span_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def span_out(s: 'const Span *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_out(s_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def spanset_as_wkb(ss: 'const SpanSet *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    ss_converted = _ffi.cast('const SpanSet *', ss)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.spanset_as_wkb(ss_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def spanset_as_hexwkb(ss: 'const SpanSet *', variant: int) -> "Tuple[str, 'size_t *']":
    ss_converted = _ffi.cast('const SpanSet *', ss)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.spanset_as_hexwkb(ss_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def spanset_from_hexwkb(hexwkb: str) -> 'SpanSet *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.spanset_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def spanset_from_wkb(wkb: 'const uint8_t *', size: int) -> 'SpanSet *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.spanset_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def spanset_out(ss: 'const SpanSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_out(ss_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def textset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.textset_in(string_converted)
    return result if result != _ffi.NULL else None


def textset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.textset_out(set_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tstzset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.tstzset_in(string_converted)
    return result if result != _ffi.NULL else None


def tstzset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.tstzset_out(set_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    lower_converted = _ffi.cast('int64', lower)
    upper_converted = _ffi.cast('int64', upper)
    result = _lib.bigintspan_make(lower_converted, upper_converted, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def floatspan_make(lower: float, upper: float, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.floatspan_make(lower, upper, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def intspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.intspan_make(lower, upper, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def set_copy(ts: 'const Set *') -> 'Set *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.set_copy(ts_converted)
    return result if result != _ffi.NULL else None


def tstzspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    lower_converted = _ffi.cast('TimestampTz', lower)
    upper_converted = _ffi.cast('TimestampTz', upper)
    result = _lib.tstzspan_make(lower_converted, upper_converted, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def span_copy(s: 'const Span *') -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_copy(s_converted)
    return result if result != _ffi.NULL else None


def spanset_copy(ps: 'const SpanSet *') -> 'SpanSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.spanset_copy(ps_converted)
    return result if result != _ffi.NULL else None


def spanset_make(spans: 'Span *', count: int, normalize: bool) -> 'SpanSet *':
    spans_converted = _ffi.cast('Span *', spans)
    result = _lib.spanset_make(spans_converted, count, normalize)
    return result if result != _ffi.NULL else None


def spanset_make_exp(spans: 'Span *', count: int, maxcount: int, normalize: bool, ordered: bool) -> 'SpanSet *':
    spans_converted = _ffi.cast('Span *', spans)
    result = _lib.spanset_make_exp(spans_converted, count, maxcount, normalize, ordered)
    return result if result != _ffi.NULL else None


def spanset_make_free(spans: 'Span *', count: int, normalize: bool) -> 'SpanSet *':
    spans_converted = _ffi.cast('Span *', spans)
    result = _lib.spanset_make_free(spans_converted, count, normalize)
    return result if result != _ffi.NULL else None


def tstzset_make(times: List[int], count: int) -> 'Set *':
    times_converted = [_ffi.cast('const TimestampTz', x) for x in times]
    result = _lib.tstzset_make(times_converted, count)
    return result if result != _ffi.NULL else None


def bigint_to_bigintset(i: int) -> 'Set *':
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_to_bigintset(i_converted)
    return result if result != _ffi.NULL else None


def bigint_to_bigintspan(i: int) -> 'Span *':
    result = _lib.bigint_to_bigintspan(i)
    return result if result != _ffi.NULL else None


def float_to_floaspan(d: float) -> 'Span *':
    result = _lib.float_to_floaspan(d)
    return result if result != _ffi.NULL else None


def float_to_floatset(d: float) -> 'Set *':
    result = _lib.float_to_floatset(d)
    return result if result != _ffi.NULL else None


def int_to_intset(i: int) -> 'Set *':
    result = _lib.int_to_intset(i)
    return result if result != _ffi.NULL else None


def int_to_intspan(i: int) -> 'Span *':
    result = _lib.int_to_intspan(i)
    return result if result != _ffi.NULL else None


def set_set_span(os: 'const Set *', s: 'Span *') -> None:
    os_converted = _ffi.cast('const Set *', os)
    s_converted = _ffi.cast('Span *', s)
    _lib.set_set_span(os_converted, s_converted)


def set_to_span(s: 'const Set *') -> 'Span *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_to_span(s_converted)
    return result if result != _ffi.NULL else None


def set_to_spanset(s: 'const Set *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_to_spanset(s_converted)
    return result if result != _ffi.NULL else None


def span_to_spanset(s: 'const Span *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_to_spanset(s_converted)
    return result if result != _ffi.NULL else None


def spanset_to_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_to_span(ss_converted)
    return result if result != _ffi.NULL else None


def spatialset_set_stbox(set: 'const Set *', box: 'STBox *') -> None:
    set_converted = _ffi.cast('const Set *', set)
    box_converted = _ffi.cast('STBox *', box)
    _lib.spatialset_set_stbox(set_converted, box_converted)


def spatialset_to_stbox(s: 'const Set *') -> 'STBox *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.spatialset_to_stbox(s_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_period(t: int) -> 'Span *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_period(t_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_periodset(t: int) -> 'SpanSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_periodset(t_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_tstzset(t: int) -> 'Set *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_tstzset(t_converted)
    return result if result != _ffi.NULL else None


def bigintset_end_value(s: 'const Set *') -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_end_value(s_converted)
    return result if result != _ffi.NULL else None


def bigintset_start_value(s: 'const Set *') -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_start_value(s_converted)
    return result if result != _ffi.NULL else None


def bigintset_value_n(s: 'const Set *', n: int) -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int64 *')
    result = _lib.bigintset_value_n(s_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def bigintset_values(s: 'const Set *') -> 'int64 *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_values(s_converted)
    return result if result != _ffi.NULL else None


def bigintspan_lower(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_lower(s_converted)
    return result if result != _ffi.NULL else None


def bigintspan_upper(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_upper(s_converted)
    return result if result != _ffi.NULL else None


def bigintspanset_lower(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_lower(ss_converted)
    return result if result != _ffi.NULL else None


def bigintspanset_upper(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_upper(ss_converted)
    return result if result != _ffi.NULL else None


def floatset_end_value(s: 'const Set *') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_end_value(s_converted)
    return result if result != _ffi.NULL else None


def floatset_start_value(s: 'const Set *') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_start_value(s_converted)
    return result if result != _ffi.NULL else None


def floatset_value_n(s: 'const Set *', n: int) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('double *')
    result = _lib.floatset_value_n(s_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def floatset_values(s: 'const Set *') -> 'double *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_values(s_converted)
    return result if result != _ffi.NULL else None


def floatspan_lower(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_lower(s_converted)
    return result if result != _ffi.NULL else None


def floatspan_upper(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_upper(s_converted)
    return result if result != _ffi.NULL else None


def floatspanset_lower(ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_lower(ss_converted)
    return result if result != _ffi.NULL else None


def floatspanset_upper(ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_upper(ss_converted)
    return result if result != _ffi.NULL else None


def intset_end_value(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_end_value(s_converted)
    return result if result != _ffi.NULL else None


def intset_start_value(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_start_value(s_converted)
    return result if result != _ffi.NULL else None


def intset_value_n(s: 'const Set *', n: int) -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int *')
    result = _lib.intset_value_n(s_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intset_values(s: 'const Set *') -> 'int *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_values(s_converted)
    return result if result != _ffi.NULL else None


def intspan_lower(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_lower(s_converted)
    return result if result != _ffi.NULL else None


def intspan_upper(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_upper(s_converted)
    return result if result != _ffi.NULL else None


def intspanset_lower(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_lower(ss_converted)
    return result if result != _ffi.NULL else None


def intspanset_upper(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_upper(ss_converted)
    return result if result != _ffi.NULL else None


def set_end_value(s: 'const Set *') -> 'Datum':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_end_value(s_converted)
    return result if result != _ffi.NULL else None


def set_hash(s: 'const Set *') -> 'uint32':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_hash(s_converted)
    return result if result != _ffi.NULL else None


def set_hash_extended(s: 'const Set *', seed: int) -> 'uint64':
    s_converted = _ffi.cast('const Set *', s)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.set_hash_extended(s_converted, seed_converted)
    return result if result != _ffi.NULL else None


def set_mem_size(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_mem_size(s_converted)
    return result if result != _ffi.NULL else None


def set_num_values(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_num_values(s_converted)
    return result if result != _ffi.NULL else None


def set_start_value(s: 'const Set *') -> 'Datum':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_start_value(s_converted)
    return result if result != _ffi.NULL else None


def set_value_n(s: 'const Set *', n: int) -> 'Datum *':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('Datum *')
    result = _lib.set_value_n(s_converted, n, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def set_values(s: 'const Set *') -> 'Datum *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_values(s_converted)
    return result if result != _ffi.NULL else None


def period_duration(s: 'const Span *') -> 'Interval *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_duration(s_converted)
    return result if result != _ffi.NULL else None


def period_lower(p: 'const Span *') -> 'TimestampTz':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_lower(p_converted)
    return result if result != _ffi.NULL else None


def period_upper(p: 'const Span *') -> 'TimestampTz':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_upper(p_converted)
    return result if result != _ffi.NULL else None


def periodset_duration(ps: 'const SpanSet *', boundspan: bool) -> 'Interval *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_duration(ps_converted, boundspan)
    return result if result != _ffi.NULL else None


def periodset_end_timestamp(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_end_timestamp(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_lower(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_lower(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_num_timestamps(ps: 'const SpanSet *') -> 'int':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_num_timestamps(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_start_timestamp(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_start_timestamp(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_timestamp_n(ps: 'const SpanSet *', n: int) -> int:
    ps_converted = _ffi.cast('const SpanSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.periodset_timestamp_n(ps_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def periodset_timestamps(ps: 'const SpanSet *') -> "Tuple['TimestampTz *', 'int']":
    ps_converted = _ffi.cast('const SpanSet *', ps)
    count = _ffi.new('int *')
    result = _lib.periodset_timestamps(ps_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def periodset_upper(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_upper(ps_converted)
    return result if result != _ffi.NULL else None


def span_hash(s: 'const Span *') -> 'uint32':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_hash(s_converted)
    return result if result != _ffi.NULL else None


def span_hash_extended(s: 'const Span *', seed: 'Datum') -> 'uint64':
    s_converted = _ffi.cast('const Span *', s)
    seed_converted = _ffi.cast('Datum', seed)
    result = _lib.span_hash_extended(s_converted, seed_converted)
    return result if result != _ffi.NULL else None


def span_lower_inc(s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_lower_inc(s_converted)
    return result if result != _ffi.NULL else None


def span_upper_inc(s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_upper_inc(s_converted)
    return result if result != _ffi.NULL else None


def span_width(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_width(s_converted)
    return result if result != _ffi.NULL else None


def spanset_end_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_end_span(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_hash(ps: 'const SpanSet *') -> 'uint32':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.spanset_hash(ps_converted)
    return result if result != _ffi.NULL else None


def spanset_hash_extended(ps: 'const SpanSet *', seed: int) -> 'uint64':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.spanset_hash_extended(ps_converted, seed_converted)
    return result if result != _ffi.NULL else None


def spanset_lower_inc(ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_lower_inc(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_mem_size(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_mem_size(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_num_spans(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_num_spans(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_span_n(ss: 'const SpanSet *', i: int) -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_span_n(ss_converted, i)
    return result if result != _ffi.NULL else None


def spanset_spans(ss: 'const SpanSet *') -> 'const Span **':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_spans(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_start_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_start_span(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_upper_inc(ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_upper_inc(ss_converted)
    return result if result != _ffi.NULL else None


def spanset_width(ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_width(ss_converted)
    return result if result != _ffi.NULL else None


def tstzset_end_timestamp(ts: 'const Set *') -> 'TimestampTz':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tstzset_end_timestamp(ts_converted)
    return result if result != _ffi.NULL else None


def tstzset_start_timestamp(ts: 'const Set *') -> 'TimestampTz':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tstzset_start_timestamp(ts_converted)
    return result if result != _ffi.NULL else None


def tstzset_timestamp_n(ts: 'const Set *', n: int) -> int:
    ts_converted = _ffi.cast('const Set *', ts)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tstzset_timestamp_n(ts_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tstzset_values(ts: 'const Set *') -> 'TimestampTz *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tstzset_values(ts_converted)
    return result if result != _ffi.NULL else None


def geoset_srid(set: 'const Set *') -> 'int':
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_srid(set_converted)
    return result if result != _ffi.NULL else None


def floatspan_set_intspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.floatspan_set_intspan(s1_converted, s2_converted)


def intspan_set_floatspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.intspan_set_floatspan(s1_converted, s2_converted)


def numspan_set_floatspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.numspan_set_floatspan(s1_converted, s2_converted)


def period_tprecision(s: 'const Span *', duration: 'const Interval *', torigin: int) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.period_tprecision(s_converted, duration_converted, torigin_converted)
    return result if result != _ffi.NULL else None


def periodset_tprecision(ss: 'const SpanSet *', duration: 'const Interval *', torigin: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.periodset_tprecision(ss_converted, duration_converted, torigin_converted)
    return result if result != _ffi.NULL else None


def period_shift_tscale(p: 'Span *', shift: 'const Interval *', duration: "Optional['const Interval *']", delta: "Optional[int]", scale: "Optional['double *']") -> None:
    p_converted = _ffi.cast('Span *', p)
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    delta_converted = _ffi.cast('TimestampTz *', delta) if delta is not None else _ffi.NULL
    scale_converted = _ffi.cast('double *', scale) if scale is not None else _ffi.NULL
    _lib.period_shift_tscale(p_converted, shift_converted, duration_converted, delta_converted, scale_converted)


def periodset_shift_tscale(ps: 'const SpanSet *', shift: 'const Interval *', duration: "Optional['const Interval *']") -> 'SpanSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.periodset_shift_tscale(ps_converted, shift_converted, duration_converted)
    return result if result != _ffi.NULL else None


def set_shift(s: 'const Set *', shift: 'Datum') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    shift_converted = _ffi.cast('Datum', shift)
    result = _lib.set_shift(s_converted, shift_converted)
    return result if result != _ffi.NULL else None


def span_expand(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.span_expand(s1_converted, s2_converted)


def timestamp_tprecision(t: int, duration: 'const Interval *', torigin: int) -> 'TimestampTz':
    t_converted = _ffi.cast('TimestampTz', t)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.timestamp_tprecision(t_converted, duration_converted, torigin_converted)
    return result if result != _ffi.NULL else None


def tstzset_shift_tscale(ts: 'const Set *', shift: 'const Interval *', duration: 'const Interval *') -> 'Set *':
    ts_converted = _ffi.cast('const Set *', ts)
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration)
    result = _lib.tstzset_shift_tscale(ts_converted, shift_converted, duration_converted)
    return result if result != _ffi.NULL else None


def adjacent_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.adjacent_bigintspan_bigint(s_converted, i_converted)
    return result if result != _ffi.NULL else None


def adjacent_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.adjacent_bigintspanset_bigint(ss_converted, i_converted)
    return result if result != _ffi.NULL else None


def adjacent_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def adjacent_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def adjacent_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def adjacent_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.adjacent_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def adjacent_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def adjacent_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.adjacent_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def contained_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_bigint_bigintset(i_converted, s_converted)
    return result if result != _ffi.NULL else None


def contained_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_bigint_bigintspan(i_converted, s_converted)
    return result if result != _ffi.NULL else None


def contained_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_bigint_bigintspanset(i_converted, ss_converted)
    return result if result != _ffi.NULL else None


def contained_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_float_floatset(d, s_converted)
    return result if result != _ffi.NULL else None


def contained_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def contained_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_float_floatspanset(d, ss_converted)
    return result if result != _ffi.NULL else None


def contained_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_int_intset(i, s_converted)
    return result if result != _ffi.NULL else None


def contained_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def contained_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contained_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contained_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contained_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contained_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def contained_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def contained_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.contained_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def contained_timestamp_period(t: int, p: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.contained_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def contained_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.contained_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contains_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def contains_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contains_floatspanset_float(ss_converted, d)
    return result if result != _ffi.NULL else None


def contains_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def contains_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contains_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contains_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contains_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contains_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contains_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def contains_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def contains_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.contains_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def contains_timestampset_timestamp(ts: 'const Set *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const Set *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def overlaps_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overlaps_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overlaps_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overlaps_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overlaps_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overlaps_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def overlaps_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overlaps_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def after_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.after_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def before_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def before_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.before_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def left_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def left_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def left_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def left_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def left_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.left_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def left_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.left_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def left_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def left_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def left_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.left_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def overafter_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_period(t: int, p: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.overafter_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_periodset(t: int, ps: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.overafter_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.overafter_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overbefore_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_period(t: int, p: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.overbefore_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_periodset(t: int, ps: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.overbefore_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.overbefore_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overleft_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def overleft_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def overleft_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def overleft_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def overleft_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overleft_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overleft_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overleft_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overleft_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def overleft_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def overleft_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overleft_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def overright_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def overright_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def overright_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def overright_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def overright_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overright_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overright_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overright_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overright_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def overright_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def overright_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overright_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def right_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def right_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def right_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def right_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def right_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.right_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def right_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.right_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def right_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def right_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def right_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.right_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def bbox_union_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    out_result = _ffi.new('Span *')
    _lib.bbox_union_span_span(s1_converted, s2_converted, out_result)
    return out_result if out_result!= _ffi.NULL else None



def intersection_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.intersection_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def intersection_period_timestamp(p: 'const Span *', t: int) -> int:
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_period_timestamp(p_converted, t_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_periodset_timestamp(ps: 'const SpanSet *', t: int) -> int:
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_periodset_timestamp(ps_converted, t_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.intersection_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def intersection_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intersection_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def intersection_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.intersection_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def intersection_timestampset_timestamp(ts: 'const Set *', t: int) -> int:
    ts_converted = _ffi.cast('const Set *', ts)
    t_converted = _ffi.cast('const TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestampset_timestamp(ts_converted, t_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.minus_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def minus_period_timestamp(p: 'const Span *', t: int) -> 'SpanSet *':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def minus_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'SpanSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def minus_span_span(s1: 'const Span *', s2: 'const Span *') -> 'SpanSet *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.minus_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def minus_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.minus_span_spanset(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def minus_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.minus_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def minus_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.minus_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def minus_timestamp_period(t: int, p: 'const Span *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Span *', p)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_period(t_converted, p_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestamp_periodset(t: int, ps: 'const SpanSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_periodset(t_converted, ps_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestampset_timestamp(ts: 'const Set *', t: int) -> 'Set *':
    ts_converted = _ffi.cast('const Set *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.union_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def union_period_timestamp(p: 'const Span *', t: int) -> 'SpanSet *':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_periodset_timestamp(ps: 'SpanSet *', t: int) -> 'SpanSet *':
    ps_converted = _ffi.cast('SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_span_span(s1: 'const Span *', s2: 'const Span *') -> 'SpanSet *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.union_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def union_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.union_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def union_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.union_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def union_timestamp_timestampset(t: int, ts: 'const Set *') -> 'Set *':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.union_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def union_timestampset_timestamp(ts: 'const Set *', t: int) -> 'Set *':
    ts_converted = _ffi.cast('const Set *', ts)
    t_converted = _ffi.cast('const TimestampTz', t)
    result = _lib.union_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_floatspan_float(s: 'const Span *', d: float) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def distance_intspan_int(s: 'const Span *', i: int) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def distance_set_set(s1: 'const Set *', s2: 'const Set *') -> 'double':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.distance_set_set(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def distance_period_timestamp(p: 'const Span *', t: int) -> 'double':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'double':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_span_span(s1: 'const Span *', s2: 'const Span *') -> 'double':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.distance_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def distance_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_spanset_span(ss_converted, s_converted)
    return result if result != _ffi.NULL else None


def distance_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'double':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.distance_spanset_spanset(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def distance_timestampset_timestamp(ts: 'const Set *', t: int) -> 'double':
    ts_converted = _ffi.cast('const Set *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def bigint_extent_transfn(s: 'Span *', i: int) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_extent_transfn(s_converted, i_converted)
    return result if result != _ffi.NULL else None


def bigint_union_transfn(state: 'Set *', i: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_union_transfn(state_converted, i_converted)
    return result if result != _ffi.NULL else None


def int_extent_transfn(s: 'Span *', i: int) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.int_extent_transfn(s_converted, i)
    return result if result != _ffi.NULL else None


def int_union_transfn(state: 'Set *', i: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.int_union_transfn(state_converted, i)
    return result if result != _ffi.NULL else None


def float_extent_transfn(s: 'Span *', d: float) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.float_extent_transfn(s_converted, d)
    return result if result != _ffi.NULL else None


def float_union_transfn(state: 'Set *', d: float) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.float_union_transfn(state_converted, d)
    return result if result != _ffi.NULL else None


def period_tcount_transfn(state: "Optional['SkipList *']", p: 'const Span *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_tcount_transfn(state_converted, p_converted)
    return result if result != _ffi.NULL else None


def periodset_tcount_transfn(state: "Optional['SkipList *']", ps: 'const SpanSet *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_tcount_transfn(state_converted, ps_converted)
    return result if result != _ffi.NULL else None


def set_union_finalfn(state: 'Set *') -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.set_union_finalfn(state_converted)
    return result if result != _ffi.NULL else None


def set_union_transfn(state: 'Set *', set: 'Set *') -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    set_converted = _ffi.cast('Set *', set)
    result = _lib.set_union_transfn(state_converted, set_converted)
    return result if result != _ffi.NULL else None


def span_extent_transfn(s1: 'Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_extent_transfn(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def spanset_extent_transfn(s: 'Span *', ss: 'const SpanSet *') -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_extent_transfn(s_converted, ss_converted)
    return result if result != _ffi.NULL else None


def text_union_transfn(state: 'Set *', txt: str) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    txt_converted = cstring2text(txt)
    result = _lib.text_union_transfn(state_converted, txt_converted)
    return result if result != _ffi.NULL else None


def timestamp_extent_transfn(p: "Optional['Span *']", t: int) -> 'Span *':
    p_converted = _ffi.cast('Span *', p) if p is not None else _ffi.NULL
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_extent_transfn(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def timestamp_tcount_transfn(state: "Optional['SkipList *']", t: int) -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_tcount_transfn(state_converted, t_converted)
    return result if result != _ffi.NULL else None


def timestamp_union_transfn(state: 'Set *', t: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_union_transfn(state_converted, t_converted)
    return result if result != _ffi.NULL else None


def set_extent_transfn(span: 'Span *', set: 'const Set *') -> 'Span *':
    span_converted = _ffi.cast('Span *', span)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.set_extent_transfn(span_converted, set_converted)
    return result if result != _ffi.NULL else None


def tstzset_tcount_transfn(state: 'SkipList *', ts: 'const Set *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tstzset_tcount_transfn(state_converted, ts_converted)
    return result if result != _ffi.NULL else None


def set_cmp(s1: 'const Set *', s2: 'const Set *') -> 'int':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_cmp(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_eq(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_eq(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_ge(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_ge(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_gt(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_gt(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_le(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_le(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_lt(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_lt(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def set_ne(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_ne(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_cmp(s1: 'const Span *', s2: 'const Span *') -> 'int':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_cmp(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_eq(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_eq(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_ge(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_ge(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_gt(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_gt(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_le(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_le(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_lt(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_lt(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_ne(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_ne(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def spanset_cmp(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'int':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_cmp(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_eq(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_eq(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_ge(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_ge(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_gt(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_gt(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_le(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_le(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_lt(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_lt(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def spanset_ne(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_ne(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def tbox_in(string: str) -> 'TBox *':
    string_converted = string.encode('utf-8')
    result = _lib.tbox_in(string_converted)
    return result if result != _ffi.NULL else None


def tbox_out(box: 'const TBox *', maxdd: int) -> str:
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_out(box_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbox_from_wkb(wkb: 'const uint8_t *', size: int) -> 'TBox *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.tbox_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def tbox_from_hexwkb(hexwkb: str) -> 'TBox *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.tbox_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def stbox_from_wkb(wkb: 'const uint8_t *', size: int) -> 'STBox *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.stbox_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def stbox_from_hexwkb(hexwkb: str) -> 'STBox *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.stbox_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def tbox_as_wkb(box: 'const TBox *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    box_converted = _ffi.cast('const TBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.tbox_as_wkb(box_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def tbox_as_hexwkb(box: 'const TBox *', variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast('const TBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size = _ffi.new('size_t *')
    result = _lib.tbox_as_hexwkb(box_converted, variant_converted, size)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size[0]


def stbox_as_wkb(box: 'const STBox *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    box_converted = _ffi.cast('const STBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.stbox_as_wkb(box_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def stbox_as_hexwkb(box: 'const STBox *', variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast('const STBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size = _ffi.new('size_t *')
    result = _lib.stbox_as_hexwkb(box_converted, variant_converted, size)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size[0]


def stbox_in(string: str) -> 'STBox *':
    string_converted = string.encode('utf-8')
    result = _lib.stbox_in(string_converted)
    return result if result != _ffi.NULL else None


def stbox_out(box: 'const STBox *', maxdd: int) -> str:
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_out(box_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbox_make(p: "Optional['const Span *']", s: "Optional['const Span *']") -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p) if p is not None else _ffi.NULL
    s_converted = _ffi.cast('const Span *', s) if s is not None else _ffi.NULL
    result = _lib.tbox_make(p_converted, s_converted)
    return result if result != _ffi.NULL else None


def tbox_set(p: 'const Span *', s: 'const Span *', box: 'TBox *') -> None:
    p_converted = _ffi.cast('const Span *', p)
    s_converted = _ffi.cast('const Span *', s)
    box_converted = _ffi.cast('TBox *', box)
    _lib.tbox_set(p_converted, s_converted, box_converted)


def tbox_copy(box: 'const TBox *') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_copy(box_converted)
    return result if result != _ffi.NULL else None


def stbox_make(hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, p: "Optional['const Span *']") -> 'STBox *':
    srid_converted = _ffi.cast('int32', srid)
    p_converted = _ffi.cast('const Span *', p) if p is not None else _ffi.NULL
    result = _lib.stbox_make(hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, p_converted)
    return result if result != _ffi.NULL else None


def stbox_set(hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, p: 'const Span *', box: 'STBox *') -> None:
    srid_converted = _ffi.cast('int32', srid)
    p_converted = _ffi.cast('const Span *', p)
    box_converted = _ffi.cast('STBox *', box)
    _lib.stbox_set(hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, p_converted, box_converted)


def stbox_copy(box: 'const STBox *') -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_copy(box_converted)
    return result if result != _ffi.NULL else None


def int_to_tbox(i: int) -> 'TBox *':
    result = _lib.int_to_tbox(i)
    return result if result != _ffi.NULL else None


def float_to_tbox(d: float) -> 'TBox *':
    result = _lib.float_to_tbox(d)
    return result if result != _ffi.NULL else None


def timestamp_to_tbox(t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_tbox(t_converted)
    return result if result != _ffi.NULL else None


def tstzset_to_tbox(ss: 'const Set *') -> 'TBox *':
    ss_converted = _ffi.cast('const Set *', ss)
    result = _lib.tstzset_to_tbox(ss_converted)
    return result if result != _ffi.NULL else None


def period_to_tbox(p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_to_tbox(p_converted)
    return result if result != _ffi.NULL else None


def periodset_to_tbox(ps: 'const SpanSet *') -> 'TBox *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_to_tbox(ps_converted)
    return result if result != _ffi.NULL else None


def int_timestamp_to_tbox(i: int, t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.int_timestamp_to_tbox(i, t_converted)
    return result if result != _ffi.NULL else None


def float_period_to_tbox(d: float, p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.float_period_to_tbox(d, p_converted)
    return result if result != _ffi.NULL else None


def float_timestamp_to_tbox(d: float, t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.float_timestamp_to_tbox(d, t_converted)
    return result if result != _ffi.NULL else None


def geo_period_to_stbox(gs: 'const GSERIALIZED *', p: 'const Span *') -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.geo_period_to_stbox(gs_converted, p_converted)
    return result if result != _ffi.NULL else None


def geo_timestamp_to_stbox(gs: 'const GSERIALIZED *', t: int) -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.geo_timestamp_to_stbox(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


def geo_to_stbox(gs: 'const GSERIALIZED *') -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_to_stbox(gs_converted)
    return result if result != _ffi.NULL else None


def int_period_to_tbox(i: int, p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.int_period_to_tbox(i, p_converted)
    return result if result != _ffi.NULL else None


def numspan_to_tbox(s: 'const Span *') -> 'TBox *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.numspan_to_tbox(s_converted)
    return result if result != _ffi.NULL else None


def span_timestamp_to_tbox(span: 'const Span *', t: int) -> 'TBox *':
    span_converted = _ffi.cast('const Span *', span)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.span_timestamp_to_tbox(span_converted, t_converted)
    return result if result != _ffi.NULL else None


def span_period_to_tbox(span: 'const Span *', p: 'const Span *') -> 'TBox *':
    span_converted = _ffi.cast('const Span *', span)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.span_period_to_tbox(span_converted, p_converted)
    return result if result != _ffi.NULL else None


def tbox_to_floatspan(box: 'const TBox *') -> 'Span *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_to_floatspan(box_converted)
    return result if result != _ffi.NULL else None


def tbox_to_period(box: 'const TBox *') -> 'Span *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_to_period(box_converted)
    return result if result != _ffi.NULL else None


def stbox_to_period(box: 'const STBox *') -> 'Span *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_to_period(box_converted)
    return result if result != _ffi.NULL else None


def tnumber_to_tbox(temp: 'const Temporal *') -> 'TBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_to_tbox(temp_converted)
    return result if result != _ffi.NULL else None


def stbox_to_geo(box: 'const STBox *') -> 'GSERIALIZED *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_to_geo(box_converted)
    return result if result != _ffi.NULL else None


def tpoint_to_stbox(temp: 'const Temporal *') -> 'STBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_to_stbox(temp_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_stbox(t: int) -> 'STBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_stbox(t_converted)
    return result if result != _ffi.NULL else None


def tstzset_to_stbox(ts: 'const Set *') -> 'STBox *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tstzset_to_stbox(ts_converted)
    return result if result != _ffi.NULL else None


def period_to_stbox(p: 'const Span *') -> 'STBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_to_stbox(p_converted)
    return result if result != _ffi.NULL else None


def periodset_to_stbox(ps: 'const SpanSet *') -> 'STBox *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_to_stbox(ps_converted)
    return result if result != _ffi.NULL else None


def tbox_hasx(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_hasx(box_converted)
    return result if result != _ffi.NULL else None


def tbox_hast(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_hast(box_converted)
    return result if result != _ffi.NULL else None


def tbox_xmin(box: 'const TBox *') -> 'double':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_xmax(box: 'const TBox *') -> 'double':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_tmin(box: 'const TBox *') -> int:
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_tmax(box: 'const TBox *') -> int:
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_hasx(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hasx(box_converted)
    return result if result != _ffi.NULL else None


def stbox_hasz(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hasz(box_converted)
    return result if result != _ffi.NULL else None


def stbox_hast(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hast(box_converted)
    return result if result != _ffi.NULL else None


def stbox_isgeodetic(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_isgeodetic(box_converted)
    return result if result != _ffi.NULL else None


def stbox_xmin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_xmax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_ymin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_ymax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_zmin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_zmax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_tmin(box: 'const STBox *') -> int:
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_tmax(box: 'const STBox *') -> int:
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_srid(box: 'const STBox *') -> 'int32':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_srid(box_converted)
    return result if result != _ffi.NULL else None


def tbox_expand(box1: 'const TBox *', box2: 'TBox *') -> None:
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('TBox *', box2)
    _lib.tbox_expand(box1_converted, box2_converted)


def tbox_expand_value(box: 'const TBox *', d: 'const double') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    d_converted = _ffi.cast('const double', d)
    result = _lib.tbox_expand_value(box_converted, d_converted)
    return result if result != _ffi.NULL else None


def tbox_expand_time(box: 'const TBox *', interval: 'const Interval *') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.tbox_expand_time(box_converted, interval_converted)
    return result if result != _ffi.NULL else None


def stbox_expand(box1: 'const STBox *', box2: 'STBox *') -> None:
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('STBox *', box2)
    _lib.stbox_expand(box1_converted, box2_converted)


def stbox_set_srid(box: 'const STBox *', srid: int) -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.stbox_set_srid(box_converted, srid_converted)
    return result if result != _ffi.NULL else None


def stbox_expand_space(box: 'const STBox *', d: float) -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_expand_space(box_converted, d)
    return result if result != _ffi.NULL else None


def stbox_expand_time(box: 'const STBox *', interval: 'const Interval *') -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.stbox_expand_time(box_converted, interval_converted)
    return result if result != _ffi.NULL else None


def contains_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.contains_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contained_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.contained_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overlaps_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overlaps_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def same_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.same_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def adjacent_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.adjacent_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contains_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.contains_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contained_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.contained_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overlaps_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overlaps_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def same_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.same_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def adjacent_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.adjacent_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def left_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.left_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overleft_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overleft_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def right_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.right_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overright_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overright_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def before_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.before_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbefore_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overbefore_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def after_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.after_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overafter_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overafter_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def left_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.left_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overleft_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overleft_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def right_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.right_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overright_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overright_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def below_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.below_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbelow_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overbelow_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def above_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.above_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overabove_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overabove_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def front_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.front_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overfront_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overfront_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def back_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.back_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overback_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overback_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def before_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.before_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbefore_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overbefore_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def after_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.after_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overafter_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overafter_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def union_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.union_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def inter_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    out_result = _ffi.new('TBox *')
    result = _lib.inter_tbox_tbox(box1_converted, box2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.intersection_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def union_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *', strict: bool) -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.union_stbox_stbox(box1_converted, box2_converted, strict)
    return result if result != _ffi.NULL else None


def inter_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    out_result = _ffi.new('STBox *')
    result = _lib.inter_stbox_stbox(box1_converted, box2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.intersection_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_eq(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_eq(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_ne(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_ne(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_cmp(box1: 'const TBox *', box2: 'const TBox *') -> 'int':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_cmp(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_lt(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_lt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_le(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_le(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_ge(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_ge(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_gt(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_gt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_eq(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_eq(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_ne(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_ne(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_cmp(box1: 'const STBox *', box2: 'const STBox *') -> 'int':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_cmp(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_lt(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_lt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_le(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_le(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_ge(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_ge(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_gt(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_gt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def cstring2text(cstring: str) -> 'text *':
    cstring_converted = cstring.encode('utf-8')
    result = _lib.cstring2text(cstring_converted)
    return result


def text2cstring(textptr: 'text *') -> str:
    result = _lib.text2cstring(textptr)
    result = _ffi.string(result).decode('utf-8')
    return result


def tbool_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tbool_in(string_converted)
    return result if result != _ffi.NULL else None


def tbool_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_out(temp_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_as_hexwkb(temp: 'const Temporal *', variant: int) -> "Tuple[str, 'size_t *']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.temporal_as_hexwkb(temp_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def temporal_as_mfjson(temp: 'const Temporal *', with_bbox: bool, flags: int, precision: int, srs: "Optional[str]") -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    srs_converted = srs.encode('utf-8') if srs is not None else _ffi.NULL
    result = _lib.temporal_as_mfjson(temp_converted, with_bbox, flags, precision, srs_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_as_wkb(temp: 'const Temporal *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.temporal_as_wkb(temp_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out[0]


def temporal_from_hexwkb(hexwkb: str) -> 'Temporal *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.temporal_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def temporal_from_mfjson(mfjson: str) -> 'Temporal *':
    mfjson_converted = mfjson.encode('utf-8')
    result = _lib.temporal_from_mfjson(mfjson_converted)
    return result if result != _ffi.NULL else None


def temporal_from_wkb(wkb: 'const uint8_t *', size: int) -> 'Temporal *':
    wkb_converted = _ffi.cast('const uint8_t *', wkb)
    result = _lib.temporal_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def tfloat_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tfloat_in(string_converted)
    return result if result != _ffi.NULL else None


def tfloat_out(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_out(temp_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tgeogpoint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeogpoint_in(string_converted)
    return result if result != _ffi.NULL else None


def tgeompoint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeompoint_in(string_converted)
    return result if result != _ffi.NULL else None


def tint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tint_in(string_converted)
    return result if result != _ffi.NULL else None


def tint_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_out(temp_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_as_ewkt(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_as_ewkt(temp_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_as_text(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_as_text(temp_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_out(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_out(temp_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttext_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.ttext_in(string_converted)
    return result if result != _ffi.NULL else None


def ttext_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_out(temp_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbool_from_base(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_from_base(b, temp_converted)
    return result if result != _ffi.NULL else None


def tboolinst_make(b: bool, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tboolinst_make(b, t_converted)
    return result if result != _ffi.NULL else None


def tbooldiscseq_from_base_time(b: bool, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tbooldiscseq_from_base_time(b, ts_converted)
    return result if result != _ffi.NULL else None


def tboolseq_from_base(b: bool, seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tboolseq_from_base(b, seq_converted)
    return result if result != _ffi.NULL else None


def tboolseq_from_base_time(b: bool, p: 'const Span *') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tboolseq_from_base_time(b, p_converted)
    return result if result != _ffi.NULL else None


def tboolseqset_from_base(b: bool, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tboolseqset_from_base(b, ss_converted)
    return result if result != _ffi.NULL else None


def tboolseqset_from_base_time(b: bool, ps: 'const SpanSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tboolseqset_from_base_time(b, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_copy(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_copy(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_from_base(d: float, temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloat_from_base(d, temp_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tfloatinst_make(d: float, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tfloatinst_make(d, t_converted)
    return result if result != _ffi.NULL else None


def tfloatdiscseq_from_base_time(d: float, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tfloatdiscseq_from_base_time(d, ts_converted)
    return result if result != _ffi.NULL else None


def tfloatseq_from_base(d: float, seq: 'const TSequence *', interp: 'interpType') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseq_from_base(d, seq_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_time(d: float, p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseq_from_base_time(d, p_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base(d: float, ss: 'const TSequenceSet *', interp: 'interpType') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseqset_from_base(d, ss_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base_time(d: float, ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseqset_from_base_time(d, ps_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeogpoint_from_base(gs: 'const GSERIALIZED *', temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpoint_from_base(gs_converted, temp_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeogpointinst_make(gs: 'const GSERIALIZED *', t: int) -> 'TInstant *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tgeogpointinst_make(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


def tgeogpointdiscseq_from_base_time(gs: 'const GSERIALIZED *', ts: 'const Set *') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tgeogpointdiscseq_from_base_time(gs_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_base(gs: 'const GSERIALIZED *', seq: 'const TSequence *', interp: 'interpType') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseq_from_base(gs_converted, seq_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_base_time(gs: 'const GSERIALIZED *', p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseq_from_base_time(gs_converted, p_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_base(gs: 'const GSERIALIZED *', ss: 'const TSequenceSet *', interp: 'interpType') -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseqset_from_base(gs_converted, ss_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_base_time(gs: 'const GSERIALIZED *', ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseqset_from_base_time(gs_converted, ps_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeompoint_from_base(gs: 'const GSERIALIZED *', temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompoint_from_base(gs_converted, temp_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeompointinst_make(gs: 'const GSERIALIZED *', t: int) -> 'TInstant *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tgeompointinst_make(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


def tgeompointdiscseq_from_base_time(gs: 'const GSERIALIZED *', ts: 'const Set *') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tgeompointdiscseq_from_base_time(gs_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tgeompointseq_from_base(gs: 'const GSERIALIZED *', seq: 'const TSequence *', interp: 'interpType') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseq_from_base(gs_converted, seq_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeompointseq_from_base_time(gs: 'const GSERIALIZED *', p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseq_from_base_time(gs_converted, p_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_base(gs: 'const GSERIALIZED *', ss: 'const TSequenceSet *', interp: 'interpType') -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseqset_from_base(gs_converted, ss_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_base_time(gs: 'const GSERIALIZED *', ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseqset_from_base_time(gs_converted, ps_converted, interp_converted)
    return result if result != _ffi.NULL else None


def tint_from_base(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_from_base(i, temp_converted)
    return result if result != _ffi.NULL else None


def tintinst_make(i: int, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tintinst_make(i, t_converted)
    return result if result != _ffi.NULL else None


def tintdiscseq_from_base_time(i: int, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tintdiscseq_from_base_time(i, ts_converted)
    return result if result != _ffi.NULL else None


def tintseq_from_base(i: int, seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tintseq_from_base(i, seq_converted)
    return result if result != _ffi.NULL else None


def tintseq_from_base_time(i: int, p: 'const Span *') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tintseq_from_base_time(i, p_converted)
    return result if result != _ffi.NULL else None


def tintseqset_from_base(i: int, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tintseqset_from_base(i, ss_converted)
    return result if result != _ffi.NULL else None


def tintseqset_from_base_time(i: int, ps: 'const SpanSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tintseqset_from_base_time(i, ps_converted)
    return result if result != _ffi.NULL else None


def tsequence_make(instants: 'const TInstant **', count: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make(instants_converted, count, lower_inc, upper_inc, interp_converted, normalize)
    return result if result != _ffi.NULL else None


def tsequence_make_exp(instants: 'const TInstant **', count: int, maxcount: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make_exp(instants_converted, count, maxcount, lower_inc, upper_inc, interp_converted, normalize)
    return result if result != _ffi.NULL else None


def tpointseq_make_coords(xcoords: 'const double *', ycoords: 'const double *', zcoords: "Optional['const double *']", times: 'const TimestampTz *', count: int, srid: int, geodetic: bool, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    zcoords_converted = zcoords if zcoords is not None else _ffi.NULL
    srid_converted = _ffi.cast('int32', srid)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tpointseq_make_coords(xcoords, ycoords, zcoords_converted, times, count, srid_converted, geodetic, lower_inc, upper_inc, interp_converted, normalize)
    return result if result != _ffi.NULL else None


def tsequence_make_free(instants: 'TInstant **', count: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make_free(instants_converted, count, lower_inc, upper_inc, interp_converted, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make(sequences: 'const TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make(sequences_converted, count, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make_exp(sequences: 'const TSequence **', count: int, maxcount: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make_exp(sequences_converted, count, maxcount, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make_free(sequences: 'TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make_free(sequences_converted, count, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make_gaps(instants: 'const TInstant **', count: int, interp: 'interpType', maxt: 'Interval *', maxdist: float) -> 'TSequenceSet *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    maxt_converted = _ffi.cast('Interval *', maxt)
    result = _lib.tsequenceset_make_gaps(instants_converted, count, interp_converted, maxt_converted, maxdist)
    return result if result != _ffi.NULL else None


def ttext_from_base(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_from_base(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def ttextinst_make(txt: str, t: int) -> 'TInstant *':
    txt_converted = cstring2text(txt)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.ttextinst_make(txt_converted, t_converted)
    return result if result != _ffi.NULL else None


def ttextdiscseq_from_base_time(txt: str, ts: 'const Set *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.ttextdiscseq_from_base_time(txt_converted, ts_converted)
    return result if result != _ffi.NULL else None


def ttextseq_from_base(txt: str, seq: 'const TSequence *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.ttextseq_from_base(txt_converted, seq_converted)
    return result if result != _ffi.NULL else None


def ttextseq_from_base_time(txt: str, p: 'const Span *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.ttextseq_from_base_time(txt_converted, p_converted)
    return result if result != _ffi.NULL else None


def ttextseqset_from_base(txt: str, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    txt_converted = cstring2text(txt)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.ttextseqset_from_base(txt_converted, ss_converted)
    return result if result != _ffi.NULL else None


def ttextseqset_from_base_time(txt: str, ps: 'const SpanSet *') -> 'TSequenceSet *':
    txt_converted = cstring2text(txt)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.ttextseqset_from_base_time(txt_converted, ps_converted)
    return result if result != _ffi.NULL else None


def tfloat_to_tint(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_to_tint(temp_converted)
    return result if result != _ffi.NULL else None


def tint_to_tfloat(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_to_tfloat(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_to_span(temp: 'const Temporal *') -> 'Span *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_to_span(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_period(temp: 'const Temporal *') -> 'Span *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_period(temp_converted)
    return result if result != _ffi.NULL else None


def tbool_end_value(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_end_value(temp_converted)
    return result if result != _ffi.NULL else None


def tbool_start_value(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_start_value(temp_converted)
    return result if result != _ffi.NULL else None


def tbool_values(temp: 'const Temporal *') -> "Tuple['bool *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tbool_values(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_duration(temp: 'const Temporal *', boundspan: bool) -> 'Interval *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_duration(temp_converted, boundspan)
    return result if result != _ffi.NULL else None


def temporal_end_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_instant(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_end_sequence(temp: 'const Temporal *') -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_sequence(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_end_timestamp(temp: 'const Temporal *') -> 'TimestampTz':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_timestamp(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_hash(temp: 'const Temporal *') -> 'uint32':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_hash(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_instant_n(temp: 'const Temporal *', n: int) -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_instant_n(temp_converted, n)
    return result if result != _ffi.NULL else None


def temporal_instants(temp: 'const Temporal *') -> "Tuple['const TInstant **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_instants(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_interpolation(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_interpolation(temp_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_max_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_max_instant(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_min_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_min_instant(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_num_instants(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_instants(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_num_sequences(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_sequences(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_num_timestamps(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_timestamps(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_segments(temp: 'const Temporal *') -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_segments(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_sequence_n(temp: 'const Temporal *', i: int) -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_sequence_n(temp_converted, i)
    return result if result != _ffi.NULL else None


def temporal_sequences(temp: 'const Temporal *') -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_sequences(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_start_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_instant(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_start_sequence(temp: 'const Temporal *') -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_sequence(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_start_timestamp(temp: 'const Temporal *') -> 'TimestampTz':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_timestamp(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_subtype(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_subtype(temp_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_time(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_time(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_timestamp_n(temp: 'const Temporal *', n: int) -> int:
    temp_converted = _ffi.cast('const Temporal *', temp)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.temporal_timestamp_n(temp_converted, n, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def temporal_timestamps(temp: 'const Temporal *') -> "Tuple['TimestampTz *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_timestamps(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tfloat_end_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_end_value(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_max_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_max_value(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_min_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_min_value(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_start_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_start_value(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_values(temp: 'const Temporal *') -> "Tuple['double *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tfloat_values(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tint_end_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_end_value(temp_converted)
    return result if result != _ffi.NULL else None


def tint_max_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_max_value(temp_converted)
    return result if result != _ffi.NULL else None


def tint_min_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_min_value(temp_converted)
    return result if result != _ffi.NULL else None


def tint_start_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_start_value(temp_converted)
    return result if result != _ffi.NULL else None


def tint_values(temp: 'const Temporal *') -> "Tuple['int *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tint_values(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tnumber_values(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_values(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_end_value(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_end_value(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_start_value(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_start_value(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_values(temp: 'const Temporal *') -> "Tuple['GSERIALIZED **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_values(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def ttext_end_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_end_value(temp_converted)
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_max_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_max_value(temp_converted)
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_min_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_min_value(temp_converted)
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_start_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_start_value(temp_converted)
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_values(temp: 'const Temporal *') -> "Tuple['text **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.ttext_values(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_append_tinstant(temp: 'Temporal *', inst: 'const TInstant *', maxdist: float, maxt: 'Interval *', expand: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('Temporal *', temp)
    inst_converted = _ffi.cast('const TInstant *', inst)
    maxt_converted = _ffi.cast('Interval *', maxt)
    result = _lib.temporal_append_tinstant(temp_converted, inst_converted, maxdist, maxt_converted, expand)
    return result if result != _ffi.NULL else None


def temporal_append_tsequence(temp: 'Temporal *', seq: 'const TSequence *', expand: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('Temporal *', temp)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.temporal_append_tsequence(temp_converted, seq_converted, expand)
    return result if result != _ffi.NULL else None


def temporal_merge(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_merge(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_merge_array(temparr: 'Temporal **', count: int) -> 'Temporal *':
    temparr_converted = [_ffi.cast('Temporal *', x) for x in temparr]
    result = _lib.temporal_merge_array(temparr_converted, count)
    return result if result != _ffi.NULL else None


def temporal_shift(temp: 'const Temporal *', shift: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('const Interval *', shift)
    result = _lib.temporal_shift(temp_converted, shift_converted)
    return result if result != _ffi.NULL else None


def temporal_shift_tscale(temp: 'const Temporal *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.temporal_shift_tscale(temp_converted, shift_converted, duration_converted)
    return result if result != _ffi.NULL else None


def temporal_step_to_linear(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_step_to_linear(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tinstant(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tinstant(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tdiscseq(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tdiscseq(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tcontseq(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tcontseq(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tsequenceset(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tsequenceset(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_tscale(temp: 'const Temporal *', duration: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    result = _lib.temporal_tscale(temp_converted, duration_converted)
    return result if result != _ffi.NULL else None


def temporal_tprecision(temp: 'const Temporal *', duration: 'const Interval *', origin: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.temporal_tprecision(temp_converted, duration_converted, origin_converted)
    return result if result != _ffi.NULL else None


def temporal_tsample(temp: 'const Temporal *', duration: 'const Interval *', origin: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.temporal_tsample(temp_converted, duration_converted, origin_converted)
    return result if result != _ffi.NULL else None


def tbool_at_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_at_value(temp_converted, b)
    return result if result != _ffi.NULL else None


def tbool_minus_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_minus_value(temp_converted, b)
    return result if result != _ffi.NULL else None


def tbool_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('bool *')
    result = _lib.tbool_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def temporal_at_max(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_at_max(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_at_min(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_at_min(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_at_period(temp: 'const Temporal *', p: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_at_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def temporal_at_periodset(temp: 'const Temporal *', ps: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_at_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_at_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_at_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def temporal_at_timestampset(temp: 'const Temporal *', ts: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_at_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_max(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_minus_max(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_min(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_minus_min(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_period(temp: 'const Temporal *', p: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_minus_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_periodset(temp: 'const Temporal *', ps: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_minus_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_minus_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_timestampset(temp: 'const Temporal *', ts: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_minus_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tfloat_at_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_at_value(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_minus_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_minus_value(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('double *')
    result = _lib.tfloat_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tint_at_value(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_at_value(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_minus_value(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_minus_value(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('int *')
    result = _lib.tint_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tnumber_at_span(temp: 'const Temporal *', span: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_at_span(temp_converted, span_converted)
    return result if result != _ffi.NULL else None


def tnumber_at_spanset(temp: 'const Temporal *', ss: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumber_at_spanset(temp_converted, ss_converted)
    return result if result != _ffi.NULL else None


def tnumber_at_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tnumber_at_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tnumber_minus_span(temp: 'const Temporal *', span: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_minus_span(temp_converted, span_converted)
    return result if result != _ffi.NULL else None


def tnumber_minus_spanset(temp: 'const Temporal *', ss: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumber_minus_spanset(temp_converted, ss_converted)
    return result if result != _ffi.NULL else None


def tnumber_minus_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tnumber_minus_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_geometry(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_at_geometry(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_stbox(temp: 'const Temporal *', box: 'const STBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpoint_at_stbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_at_value(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_geometry(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_minus_geometry(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_stbox(temp: 'const Temporal *', box: 'const STBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpoint_minus_stbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_minus_value(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'GSERIALIZED **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.tpoint_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tsequence_at_period(seq: 'const TSequence *', p: 'const Span *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequence_at_period(seq_converted, p_converted)
    return result if result != _ffi.NULL else None


def ttext_at_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_at_value(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_minus_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_minus_value(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'text **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('text **')
    result = _lib.ttext_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tand_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tand_bool_tbool(b, temp_converted)
    return result if result != _ffi.NULL else None


def tand_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tand_tbool_bool(temp_converted, b)
    return result if result != _ffi.NULL else None


def tand_tbool_tbool(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tand_tbool_tbool(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tnot_tbool(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnot_tbool(temp_converted)
    return result if result != _ffi.NULL else None


def tor_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tor_bool_tbool(b, temp_converted)
    return result if result != _ffi.NULL else None


def tor_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tor_tbool_bool(temp_converted, b)
    return result if result != _ffi.NULL else None


def tor_tbool_tbool(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tor_tbool_tbool(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tbool_when_true(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_when_true(temp_converted)
    return result if result != _ffi.NULL else None


def add_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def add_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def add_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def add_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def add_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.add_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def float_degrees(value: float, normalize: bool) -> 'double':
    result = _lib.float_degrees(value, normalize)
    return result if result != _ffi.NULL else None


def div_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def div_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def div_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def div_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def div_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.div_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def mult_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def mult_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def mult_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def mult_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def mult_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.mult_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def sub_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def sub_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def sub_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def sub_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def sub_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.sub_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def tfloat_degrees(temp: 'const Temporal *', normalize: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_degrees(temp_converted, normalize)
    return result if result != _ffi.NULL else None


def tfloat_radians(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_radians(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_derivative(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_derivative(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_abs(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_abs(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_delta_value(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_delta_value(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_angular_difference(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_angular_difference(temp_converted)
    return result if result != _ffi.NULL else None


def textcat_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.textcat_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def textcat_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.textcat_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def textcat_ttext_ttext(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.textcat_ttext_ttext(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def ttext_upper(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_upper(temp_converted)
    return result if result != _ffi.NULL else None


def ttext_lower(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_lower(temp_converted)
    return result if result != _ffi.NULL else None


def distance_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.distance_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def distance_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.distance_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def distance_tnumber_tnumber(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.distance_tnumber_tnumber(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def distance_tpoint_geo(temp: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.distance_tpoint_geo(temp_converted, geo_converted)
    return result if result != _ffi.NULL else None


def distance_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.distance_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def nad_stbox_geo(box: 'const STBox *', gs: 'const GSERIALIZED *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_stbox_geo(box_converted, gs_converted)
    return result if result != _ffi.NULL else None


def nad_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'double':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.nad_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def nad_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'double':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.nad_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def nad_tfloat_float(temp: 'const Temporal *', d: float) -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.nad_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def nad_tfloat_tfloat(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tfloat_tfloat(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def nad_tint_int(temp: 'const Temporal *', i: int) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.nad_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def nad_tint_tint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tint_tint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def nad_tnumber_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.nad_tnumber_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def nad_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def nad_tpoint_stbox(temp: 'const Temporal *', box: 'const STBox *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.nad_tpoint_stbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def nad_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def nai_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nai_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def nai_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'TInstant *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nai_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def shortestline_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'GSERIALIZED **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.shortestline_tpoint_geo(temp_converted, gs_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def shortestline_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'GSERIALIZED **':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.shortestline_tpoint_tpoint(temp1_converted, temp2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbool_always_eq(temp: 'const Temporal *', b: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_always_eq(temp_converted, b)
    return result if result != _ffi.NULL else None


def tbool_ever_eq(temp: 'const Temporal *', b: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_ever_eq(temp_converted, b)
    return result if result != _ffi.NULL else None


def tfloat_always_eq(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_eq(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_always_le(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_le(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_always_lt(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_lt(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_ever_eq(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_eq(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_ever_le(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_le(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_ever_lt(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_lt(temp_converted, d)
    return result if result != _ffi.NULL else None


def tgeogpoint_always_eq(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tgeogpoint_always_eq(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tgeogpoint_ever_eq(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tgeogpoint_ever_eq(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tgeompoint_always_eq(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tgeompoint_always_eq(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tgeompoint_ever_eq(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tgeompoint_ever_eq(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tint_always_eq(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_eq(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_always_le(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_le(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_always_lt(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_lt(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_ever_eq(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_eq(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_ever_le(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_le(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_ever_lt(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_lt(temp_converted, i)
    return result if result != _ffi.NULL else None


def ttext_always_eq(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_eq(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_always_le(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_le(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_always_lt(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_lt(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_ever_eq(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_eq(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_ever_le(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_le(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_ever_lt(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_lt(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def temporal_cmp(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_cmp(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_eq(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_eq(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_ge(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_ge(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_gt(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_gt(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_le(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_le(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_lt(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_lt(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_ne(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_ne(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def teq_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_bool_tbool(b, temp_converted)
    return result if result != _ffi.NULL else None


def teq_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def teq_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'Temporal *':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.teq_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def teq_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def teq_point_tgeogpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_point_tgeogpoint(gs_converted, temp_converted)
    return result if result != _ffi.NULL else None


def teq_point_tgeompoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_point_tgeompoint(gs_converted, temp_converted)
    return result if result != _ffi.NULL else None


def teq_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tbool_bool(temp_converted, b)
    return result if result != _ffi.NULL else None


def teq_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.teq_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def teq_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def teq_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def teq_tgeogpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.teq_tgeogpoint_point(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def teq_tgeompoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.teq_tgeompoint_point(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def teq_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def teq_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'Temporal *':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.teq_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def teq_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.teq_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def tge_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def tge_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def tge_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tge_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tge_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tge_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def tge_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def tge_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tge_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def tgt_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def tgt_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def tgt_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tgt_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tgt_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tgt_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def tgt_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def tgt_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tgt_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def tle_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def tle_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def tle_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tle_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tle_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tle_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def tle_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def tle_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tle_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def tlt_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def tlt_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def tlt_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tlt_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tlt_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tlt_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def tlt_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def tlt_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tlt_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def tne_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_bool_tbool(b, temp_converted)
    return result if result != _ffi.NULL else None


def tne_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_float_tfloat(d, temp_converted)
    return result if result != _ffi.NULL else None


def tne_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'Temporal *':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.tne_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def tne_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_int_tint(i, temp_converted)
    return result if result != _ffi.NULL else None


def tne_point_tgeogpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_point_tgeogpoint(gs_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tne_point_tgeompoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_point_tgeompoint(gs_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tne_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tbool_bool(temp_converted, b)
    return result if result != _ffi.NULL else None


def tne_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tne_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tne_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_text_ttext(txt_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tne_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tfloat_float(temp_converted, d)
    return result if result != _ffi.NULL else None


def tne_tgeogpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tne_tgeogpoint_point(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tne_tgeompoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tne_tgeompoint_point(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tne_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tint_int(temp_converted, i)
    return result if result != _ffi.NULL else None


def tne_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'Temporal *':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.tne_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def tne_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tne_ttext_text(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def bearing_point_point(geo1: 'const GSERIALIZED *', geo2: 'const GSERIALIZED *') -> 'double':
    geo1_converted = _ffi.cast('const GSERIALIZED *', geo1)
    geo2_converted = _ffi.cast('const GSERIALIZED *', geo2)
    out_result = _ffi.new('double *')
    result = _lib.bearing_point_point(geo1_converted, geo2_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def bearing_tpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *', invert: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.bearing_tpoint_point(temp_converted, gs_converted, invert)
    return result if result != _ffi.NULL else None


def bearing_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.bearing_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def tpoint_angular_difference(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_angular_difference(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_azimuth(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_azimuth(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_convex_hull(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_convex_hull(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_cumulative_length(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_cumulative_length(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_direction(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    out_result = _ffi.new('double *')
    result = _lib.tpoint_direction(temp_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tpoint_get_coord(temp: 'const Temporal *', coord: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_get_coord(temp_converted, coord)
    return result if result != _ffi.NULL else None


def tpoint_is_simple(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_is_simple(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_length(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_length(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_speed(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_speed(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_srid(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_srid(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_stboxes(temp: 'const Temporal *') -> "Tuple['STBox *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_stboxes(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tpoint_trajectory(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_trajectory(temp_converted)
    return result if result != _ffi.NULL else None


def geo_expand_space(gs: 'const GSERIALIZED *', d: float) -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_expand_space(gs_converted, d)
    return result if result != _ffi.NULL else None


def tgeompoint_tgeogpoint(temp: 'const Temporal *', oper: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeompoint_tgeogpoint(temp_converted, oper)
    return result if result != _ffi.NULL else None


def tpoint_expand_space(temp: 'const Temporal *', d: float) -> 'STBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_expand_space(temp_converted, d)
    return result if result != _ffi.NULL else None


def tpoint_make_simple(temp: 'const Temporal *') -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_make_simple(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tpoint_set_srid(temp: 'const Temporal *', srid: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.tpoint_set_srid(temp_converted, srid_converted)
    return result if result != _ffi.NULL else None


def econtains_geo_tpoint(geo: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'int':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.econtains_geo_tpoint(geo_converted, temp_converted)
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.edisjoint_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.edisjoint_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def edwithin_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', dist: float) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.edwithin_tpoint_geo(temp_converted, gs_converted, dist)
    return result if result != _ffi.NULL else None


def edwithin_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *', dist: float) -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.edwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist)
    return result if result != _ffi.NULL else None


def eintersects_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.eintersects_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def eintersects_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.eintersects_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def etouches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.etouches_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tcontains_geo_tpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *', restr: bool, atvalue: bool) -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tcontains_geo_tpoint(gs_converted, temp_converted, restr, atvalue)
    return result if result != _ffi.NULL else None


def tdisjoint_tpoint_geo(temp: 'const Temporal *', geo: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.tdisjoint_tpoint_geo(temp_converted, geo_converted, restr, atvalue)
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', dist: float, restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tdwithin_tpoint_geo(temp_converted, gs_converted, dist, restr, atvalue)
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *', dist: float, restr: bool, atvalue: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tdwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist, restr, atvalue)
    return result if result != _ffi.NULL else None


def tintersects_tpoint_geo(temp: 'const Temporal *', geo: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.tintersects_tpoint_geo(temp_converted, geo_converted, restr, atvalue)
    return result if result != _ffi.NULL else None


def ttouches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.ttouches_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    return result if result != _ffi.NULL else None


def temporal_insert(temp1: 'const Temporal *', temp2: 'const Temporal *', connect: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_insert(temp1_converted, temp2_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_update(temp1: 'const Temporal *', temp2: 'const Temporal *', connect: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_update(temp1_converted, temp2_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_delete_timestamp(temp: 'const Temporal *', t: int, connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_delete_timestamp(temp_converted, t_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_delete_timestampset(temp: 'const Temporal *', ts: 'const Set *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_delete_timestampset(temp_converted, ts_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_delete_period(temp: 'const Temporal *', p: 'const Span *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_delete_period(temp_converted, p_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_delete_periodset(temp: 'const Temporal *', ps: 'const SpanSet *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_delete_periodset(temp_converted, ps_converted, connect)
    return result if result != _ffi.NULL else None


def temporal_stops(temp: 'const Temporal *', mindist: float, minduration: 'const Interval *') -> 'TSequenceSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    minduration_converted = _ffi.cast('const Interval *', minduration)
    result = _lib.temporal_stops(temp_converted, mindist, minduration_converted)
    return result if result != _ffi.NULL else None


def tbool_tand_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_tand_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tbool_tor_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_tor_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def temporal_extent_transfn(p: "Optional['Span *']", temp: 'const Temporal *') -> 'Span *':
    p_converted = _ffi.cast('Span *', p) if p is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_extent_transfn(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def temporal_tagg_finalfn(state: 'SkipList *') -> 'Temporal *':
    state_converted = _ffi.cast('SkipList *', state)
    result = _lib.temporal_tagg_finalfn(state_converted)
    return result if result != _ffi.NULL else None


def temporal_tcount_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_tcount_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tmax_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tmin_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_tsum_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tsum_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tint_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tmax_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tint_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tmin_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tint_tsum_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tsum_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_integral(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_integral(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_extent_transfn(box: "Optional['TBox *']", temp: 'const Temporal *') -> 'TBox *':
    box_converted = _ffi.cast('TBox *', box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_extent_transfn(box_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_tavg_finalfn(state: 'SkipList *') -> 'Temporal *':
    state_converted = _ffi.cast('SkipList *', state)
    result = _lib.tnumber_tavg_finalfn(state_converted)
    return result if result != _ffi.NULL else None


def tnumber_tavg_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_tavg_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_twavg(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_twavg(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_extent_transfn(box: "Optional['STBox *']", temp: 'const Temporal *') -> 'STBox *':
    box_converted = _ffi.cast('STBox *', box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_extent_transfn(box_converted, temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_twcentroid(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_twcentroid(temp_converted)
    return result if result != _ffi.NULL else None


def ttext_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_tmax_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def ttext_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_tmin_transfn(state_converted, temp_converted)
    return result if result != _ffi.NULL else None


def int_bucket(value: int, size: int, origin: int) -> 'int':
    result = _lib.int_bucket(value, size, origin)
    return result if result != _ffi.NULL else None


def float_bucket(value: float, size: float, origin: float) -> 'double':
    result = _lib.float_bucket(value, size, origin)
    return result if result != _ffi.NULL else None


def timestamptz_bucket(timestamp: int, duration: 'const Interval *', origin: int) -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.timestamptz_bucket(timestamp_converted, duration_converted, origin_converted)
    return result if result != _ffi.NULL else None


def intspan_bucket_list(bounds: 'const Span *', size: int, origin: int, newcount: 'int *') -> 'Span *':
    bounds_converted = _ffi.cast('const Span *', bounds)
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.intspan_bucket_list(bounds_converted, size, origin, newcount_converted)
    return result if result != _ffi.NULL else None


def floatspan_bucket_list(bounds: 'const Span *', size: float, origin: float, newcount: 'int *') -> 'Span *':
    bounds_converted = _ffi.cast('const Span *', bounds)
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.floatspan_bucket_list(bounds_converted, size, origin, newcount_converted)
    return result if result != _ffi.NULL else None


def period_bucket_list(bounds: 'const Span *', duration: 'const Interval *', origin: int, newcount: 'int *') -> 'Span *':
    bounds_converted = _ffi.cast('const Span *', bounds)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.period_bucket_list(bounds_converted, duration_converted, origin_converted, newcount_converted)
    return result if result != _ffi.NULL else None


def tbox_tile_list(bounds: 'const TBox *', xsize: float, duration: 'const Interval *', xorigin: 'Optional[float]', torigin: "Optional[int]") -> "Tuple['TBox *', 'int', 'int']":
    bounds_converted = _ffi.cast('const TBox *', bounds)
    duration_converted = _ffi.cast('const Interval *', duration)
    xorigin_converted = xorigin if xorigin is not None else _ffi.NULL
    torigin_converted = _ffi.cast('TimestampTz', torigin) if torigin is not None else _ffi.NULL
    rows = _ffi.new('int *')
    columns = _ffi.new('int *')
    result = _lib.tbox_tile_list(bounds_converted, xsize, duration_converted, xorigin_converted, torigin_converted, rows, columns)
    return result if result != _ffi.NULL else None, rows[0], columns[0]


def tint_value_split(temp: 'Temporal *', size: int, origin: int) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    newcount = _ffi.new('int *')
    result = _lib.tint_value_split(temp_converted, size, origin, newcount)
    return result if result != _ffi.NULL else None, newcount[0]


def tfloat_value_split(temp: 'Temporal *', size: float, origin: float) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    newcount = _ffi.new('int *')
    result = _lib.tfloat_value_split(temp_converted, size, origin, newcount)
    return result if result != _ffi.NULL else None, newcount[0]


def temporal_time_split(temp: 'Temporal *', duration: 'Interval *', torigin: int) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    newcount = _ffi.new('int *')
    result = _lib.temporal_time_split(temp_converted, duration_converted, torigin_converted, newcount)
    return result if result != _ffi.NULL else None, newcount[0]


def tint_value_time_split(temp: 'Temporal *', size: int, vorigin: int, duration: 'Interval *', torigin: int) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    newcount = _ffi.new('int *')
    result = _lib.tint_value_time_split(temp_converted, size, vorigin, duration_converted, torigin_converted, newcount)
    return result if result != _ffi.NULL else None, newcount[0]


def tfloat_value_time_split(temp: 'Temporal *', size: float, vorigin: float, duration: 'Interval *', torigin: int) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    newcount = _ffi.new('int *')
    result = _lib.tfloat_value_time_split(temp_converted, size, vorigin, duration_converted, torigin_converted, newcount)
    return result if result != _ffi.NULL else None, newcount[0]


def stbox_tile_list(bounds: 'STBox *', size: float, duration: "Optional['const Interval *']", sorigin: 'GSERIALIZED *', torigin: int) -> "Tuple['STBox *', 'int *']":
    bounds_converted = _ffi.cast('STBox *', bounds)
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    sorigin_converted = _ffi.cast('GSERIALIZED *', sorigin)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    cellcount = _ffi.new('int **')
    result = _lib.stbox_tile_list(bounds_converted, size, duration_converted, sorigin_converted, torigin_converted, cellcount)
    return result if result != _ffi.NULL else None, cellcount[0]


def temporal_frechet_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_frechet_distance(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_dyntimewarp_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_dyntimewarp_distance(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def temporal_frechet_path(temp1: 'const Temporal *', temp2: 'const Temporal *') -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    count = _ffi.new('int *')
    result = _lib.temporal_frechet_path(temp1_converted, temp2_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_dyntimewarp_path(temp1: 'const Temporal *', temp2: 'const Temporal *') -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    count = _ffi.new('int *')
    result = _lib.temporal_dyntimewarp_path(temp1_converted, temp2_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def temporal_hausdorff_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_hausdorff_distance(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def geo_to_tpoint(geo: 'const GSERIALIZED *') -> 'Temporal *':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.geo_to_tpoint(geo_converted)
    return result if result != _ffi.NULL else None


def temporal_simplify_min_dist(temp: 'const Temporal *', dist: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_min_dist(temp_converted, dist)
    return result if result != _ffi.NULL else None


def temporal_simplify_min_tdelta(temp: 'const Temporal *', mint: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    mint_converted = _ffi.cast('const Interval *', mint)
    result = _lib.temporal_simplify_min_tdelta(temp_converted, mint_converted)
    return result if result != _ffi.NULL else None


def temporal_simplify_dp(temp: 'const Temporal *', eps_dist: float, synchronized: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_dp(temp_converted, eps_dist, synchronized)
    return result if result != _ffi.NULL else None


def temporal_simplify_max_dist(temp: 'const Temporal *', eps_dist: float, synchronized: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_max_dist(temp_converted, eps_dist, synchronized)
    return result if result != _ffi.NULL else None


def tpoint_AsMVTGeom(temp: 'const Temporal *', bounds: 'const STBox *', extent: 'int32_t', buffer: 'int32_t', clip_geom: bool, geom: 'GSERIALIZED **', timesarr: 'int64 **') -> "Tuple['bool', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    bounds_converted = _ffi.cast('const STBox *', bounds)
    extent_converted = _ffi.cast('int32_t', extent)
    buffer_converted = _ffi.cast('int32_t', buffer)
    geom_converted = [_ffi.cast('GSERIALIZED *', x) for x in geom]
    timesarr_converted = [_ffi.cast('int64 *', x) for x in timesarr]
    count = _ffi.new('int *')
    result = _lib.tpoint_AsMVTGeom(temp_converted, bounds_converted, extent_converted, buffer_converted, clip_geom, geom_converted, timesarr_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tpoint_to_geo_measure(tpoint: 'const Temporal *', measure: 'const Temporal *', segmentize: bool) -> 'GSERIALIZED **':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    measure_converted = _ffi.cast('const Temporal *', measure)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.tpoint_to_geo_measure(tpoint_converted, measure_converted, segmentize, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


