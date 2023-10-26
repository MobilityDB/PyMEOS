import os
from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List, Union

import _meos_cffi
from .errors import raise_meos_exception
import shapely.geometry as spg
from dateutil.parser import parse
from shapely import wkt, get_srid, set_srid
from shapely.geometry.base import BaseGeometry

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib

_error: Optional[int] = None
_error_level: Optional[int] = None
_error_message: Optional[str] = None

_debug = os.environ.get('MEOS_DEBUG', '0') == '1'


def meos_set_debug(debug: bool) -> None:
    global _debug
    _debug = debug


def _check_error() -> None:
    global _error, _error_level, _error_message
    if _error is not None:
        error = _error
        error_level = _error_level
        error_message = _error_message
        _error = None
        _error_level = None
        _error_message = None
        raise_meos_exception(error_level, error, error_message)


@_ffi.def_extern()
def py_error_handler(error_level, error_code, error_msg):
    global _error, _error_level, _error_message
    _error = error_code
    _error_level = error_level
    _error_message = _ffi.string(error_msg).decode('utf-8')
    if _debug:
        print(f'ERROR Handler called: Level: {_error} | Code: {_error_level} | Message: {_error_message}')


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


def geo_to_gserialized(geom: BaseGeometry, geodetic: bool) -> 'GSERIALIZED *':
    if geodetic:
        return geography_to_gserialized(geom)
    else:
        return geometry_to_gserialized(geom)


def geometry_to_gserialized(geom: BaseGeometry) -> 'GSERIALIZED *':
    text = wkt.dumps(geom)
    if get_srid(geom) > 0:
        text = f'SRID={get_srid(geom)};{text}'
    gs = pgis_geometry_in(text, -1)
    return gs


def geography_to_gserialized(geom: BaseGeometry) -> 'GSERIALIZED *':
    text = wkt.dumps(geom)
    if get_srid(geom) > 0:
        text = f'SRID={get_srid(geom)};{text}'
    gs = pgis_geography_in(text, -1)
    return gs


def gserialized_to_shapely_point(geom: 'const GSERIALIZED *', precision: int = 15) -> spg.Point:
    text = gserialized_as_text(geom, precision)
    geometry = wkt.loads(text)
    srid = lwgeom_get_srid(geom)
    if srid > 0:
        geometry = set_srid(geometry, srid)
    return geometry


def gserialized_to_shapely_geometry(geom: 'const GSERIALIZED *', precision: int = 15) -> BaseGeometry:
    text = gserialized_as_text(geom, precision)
    geometry = wkt.loads(text)
    srid = lwgeom_get_srid(geom)
    if srid > 0:
        geometry = set_srid(geometry, srid)
    return geometry


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
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_from_gserialized(g: 'const GSERIALIZED *') -> 'LWGEOM *':
    g_converted = _ffi.cast('const GSERIALIZED *', g)
    result = _lib.lwgeom_from_gserialized(g_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def gserialized_from_lwgeom(geom: 'LWGEOM *') -> 'GSERIALIZED *':
    geom_converted = _ffi.cast('LWGEOM *', geom)
    size_converted = _ffi.NULL
    result = _lib.gserialized_from_lwgeom(geom_converted, size_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_get_srid(geom: 'const LWGEOM *') -> 'int32_t':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_get_srid(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_x(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_x(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_y(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_y(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_z(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_z(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_m(point: 'const LWPOINT *') -> 'double':
    point_converted = _ffi.cast('const LWPOINT *', point)
    result = _lib.lwpoint_get_m(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_has_z(geom: 'const LWGEOM *') -> 'int':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_has_z(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_has_m(geom: 'const LWGEOM *') -> 'int':
    geom_converted = _ffi.cast('const LWGEOM *', geom)
    result = _lib.lwgeom_has_m(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno() -> 'int':
    result = _lib.meos_errno()
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_set(err: int) -> 'int':
    result = _lib.meos_errno_set(err)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_restore(err: int) -> 'int':
    result = _lib.meos_errno_restore(err)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_reset() -> 'int':
    result = _lib.meos_errno_reset()
    _check_error()
    return result if result != _ffi.NULL else None


def meos_initialize(tz_str: "Optional[str]") -> None:
    tz_str_converted = tz_str.encode('utf-8') if tz_str is not None else _ffi.NULL
    _lib.meos_initialize(tz_str_converted, _lib.py_error_handler)


def meos_finalize() -> None:
    _lib.meos_finalize()
    _check_error()


def bool_in(in_str: str) -> 'bool':
    in_str_converted = in_str.encode('utf-8')
    result = _lib.bool_in(in_str_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bool_out(b: bool) -> str:
    result = _lib.bool_out(b)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def cstring2text(cstring: str) -> 'text *':
    cstring_converted = cstring.encode('utf-8')
    result = _lib.cstring2text(cstring_converted)
    return result


def pg_date_in(string: str) -> 'DateADT':
    string_converted = string.encode('utf-8')
    result = _lib.pg_date_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_date_out(date: 'DateADT') -> str:
    date_converted = _ffi.cast('DateADT', date)
    result = _lib.pg_date_out(date_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_interval_cmp(interval1: 'const Interval *', interval2: 'const Interval *') -> 'int':
    interval1_converted = _ffi.cast('const Interval *', interval1)
    interval2_converted = _ffi.cast('const Interval *', interval2)
    result = _lib.pg_interval_cmp(interval1_converted, interval2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_in(string: str, typmod: int) -> 'Interval *':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_interval_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_make(years: int, months: int, weeks: int, days: int, hours: int, mins: int, secs: float) -> 'Interval *':
    years_converted = _ffi.cast('int32', years)
    months_converted = _ffi.cast('int32', months)
    weeks_converted = _ffi.cast('int32', weeks)
    days_converted = _ffi.cast('int32', days)
    hours_converted = _ffi.cast('int32', hours)
    mins_converted = _ffi.cast('int32', mins)
    result = _lib.pg_interval_make(years_converted, months_converted, weeks_converted, days_converted, hours_converted, mins_converted, secs)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_mul(span: 'const Interval *', factor: float) -> 'Interval *':
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_interval_mul(span_converted, factor)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_out(span: 'const Interval *') -> str:
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_interval_out(span_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_interval_to_char(it: 'Interval *', fmt: str) -> str:
    it_converted = _ffi.cast('Interval *', it)
    fmt_converted = cstring2text(fmt)
    result = _lib.pg_interval_to_char(it_converted, fmt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def pg_interval_pl(span1: 'const Interval *', span2: 'const Interval *') -> 'Interval *':
    span1_converted = _ffi.cast('const Interval *', span1)
    span2_converted = _ffi.cast('const Interval *', span2)
    result = _lib.pg_interval_pl(span1_converted, span2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_time_in(string: str, typmod: int) -> 'TimeADT':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_time_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_time_out(time: 'TimeADT') -> str:
    time_converted = _ffi.cast('TimeADT', time)
    result = _lib.pg_time_out(time_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamp_in(string: str, typmod: int) -> 'Timestamp':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamp_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamp_mi(dt1: int, dt2: int) -> 'Interval *':
    dt1_converted = _ffi.cast('TimestampTz', dt1)
    dt2_converted = _ffi.cast('TimestampTz', dt2)
    result = _lib.pg_timestamp_mi(dt1_converted, dt2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamp_mi_interval(timestamp: int, span: 'const Interval *') -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_timestamp_mi_interval(timestamp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamp_out(dt: int) -> str:
    dt_converted = _ffi.cast('Timestamp', dt)
    result = _lib.pg_timestamp_out(dt_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamp_pl_interval(timestamp: int, span: 'const Interval *') -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    span_converted = _ffi.cast('const Interval *', span)
    result = _lib.pg_timestamp_pl_interval(timestamp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamp_to_char(dt: int, fmt: str) -> str:
    dt_converted = _ffi.cast('Timestamp', dt)
    fmt_converted = cstring2text(fmt)
    result = _lib.pg_timestamp_to_char(dt_converted, fmt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def pg_timestamptz_in(string: str, typmod: int) -> 'TimestampTz':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamptz_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamptz_out(dt: int) -> str:
    dt_converted = _ffi.cast('TimestampTz', dt)
    result = _lib.pg_timestamptz_out(dt_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamptz_to_char(dt: int, fmt: str) -> str:
    dt_converted = _ffi.cast('TimestampTz', dt)
    fmt_converted = cstring2text(fmt)
    result = _lib.pg_timestamptz_to_char(dt_converted, fmt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def pg_to_date(date_txt: str, fmt: str) -> 'DateADT':
    date_txt_converted = cstring2text(date_txt)
    fmt_converted = cstring2text(fmt)
    result = _lib.pg_to_date(date_txt_converted, fmt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_to_timestamp(date_txt: str, fmt: str) -> 'TimestampTz':
    date_txt_converted = cstring2text(date_txt)
    fmt_converted = cstring2text(fmt)
    result = _lib.pg_to_timestamp(date_txt_converted, fmt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text2cstring(textptr: 'text *') -> str:
    result = _lib.text2cstring(textptr)
    result = _ffi.string(result).decode('utf-8')
    return result


def geography_from_hexewkb(wkt: str) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.geography_from_hexewkb(wkt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geography_from_text(wkt: str, srid: int) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.geography_from_text(wkt_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def geometry_from_hexewkb(wkt: str) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.geometry_from_hexewkb(wkt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geometry_from_text(wkt: str, srid: int) -> 'GSERIALIZED *':
    wkt_converted = wkt.encode('utf-8')
    result = _lib.geometry_from_text(wkt_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def gserialized_as_ewkb(gs: 'const GSERIALIZED *', type: str) -> 'bytea *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    type_converted = type.encode('utf-8')
    result = _lib.gserialized_as_ewkb(gs_converted, type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def gserialized_as_ewkt(gs: 'const GSERIALIZED *', precision: int) -> str:
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.gserialized_as_ewkt(gs_converted, precision)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_geojson(gs: 'const GSERIALIZED *', option: int, precision: int, srs: "Optional[str]") -> str:
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    srs_converted = srs.encode('utf-8') if srs is not None else _ffi.NULL
    result = _lib.gserialized_as_geojson(gs_converted, option, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_hexewkb(gs: 'const GSERIALIZED *', type: str) -> str:
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    type_converted = type.encode('utf-8')
    result = _lib.gserialized_as_hexewkb(gs_converted, type_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_as_text(gs: 'const GSERIALIZED *', precision: int) -> str:
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.gserialized_as_text(gs_converted, precision)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_from_ewkb(bytea_wkb: 'const bytea *', srid: int) -> 'GSERIALIZED *':
    bytea_wkb_converted = _ffi.cast('const bytea *', bytea_wkb)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.gserialized_from_ewkb(bytea_wkb_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def gserialized_from_geojson(geojson: str) -> 'GSERIALIZED *':
    geojson_converted = geojson.encode('utf-8')
    result = _lib.gserialized_from_geojson(geojson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def gserialized_out(gs: 'const GSERIALIZED *') -> str:
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.gserialized_out(gs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pgis_geography_in(input: str, geom_typmod: int) -> 'GSERIALIZED *':
    input_converted = input.encode('utf-8')
    geom_typmod_converted = _ffi.cast('int32', geom_typmod)
    result = _lib.pgis_geography_in(input_converted, geom_typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pgis_geometry_in(input: str, geom_typmod: int) -> 'GSERIALIZED *':
    input_converted = input.encode('utf-8')
    geom_typmod_converted = _ffi.cast('int32', geom_typmod)
    result = _lib.pgis_geometry_in(input_converted, geom_typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pgis_gserialized_same(gs1: 'const GSERIALIZED *', gs2: 'const GSERIALIZED *') -> 'bool':
    gs1_converted = _ffi.cast('const GSERIALIZED *', gs1)
    gs2_converted = _ffi.cast('const GSERIALIZED *', gs2)
    result = _lib.pgis_gserialized_same(gs1_converted, gs2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.bigintset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.bigintspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.floatset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_out(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.floatset_out(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.floatspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_out(s: 'const Span *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.floatspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_out(ss: 'const SpanSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geogset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.geogset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geomset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.geomset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_as_ewkt(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_as_ewkt(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geoset_as_text(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_as_text(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def geoset_out(set: 'const Set *', maxdd: int) -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_out(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.intset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.intset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.intspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def intspanset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.intspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def period_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.period_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def periodset_in(string: str) -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    result = _lib.periodset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_out(ss: 'const SpanSet *') -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.periodset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def set_as_hexwkb(s: 'const Set *', variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast('const Set *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.set_as_hexwkb(s_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def set_as_wkb(s: 'const Set *', variant: int) -> bytes:
    s_converted = _ffi.cast('const Set *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.set_as_wkb(s_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def set_from_hexwkb(hexwkb: str) -> 'Set *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.set_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_from_wkb(wkb: bytes) -> 'Set *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.set_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def span_as_hexwkb(s: 'const Span *', variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_hexwkb(s_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def span_as_wkb(s: 'const Span *', variant: int) -> bytes:
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_wkb(s_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def span_from_hexwkb(hexwkb: str) -> 'Span *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.span_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_from_wkb(wkb: bytes) -> 'Span *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.span_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def spanset_as_hexwkb(ss: 'const SpanSet *', variant: int) -> "Tuple[str, 'size_t *']":
    ss_converted = _ffi.cast('const SpanSet *', ss)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.spanset_as_hexwkb(ss_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def spanset_as_wkb(ss: 'const SpanSet *', variant: int) -> bytes:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.spanset_as_wkb(ss_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def spanset_from_hexwkb(hexwkb: str) -> 'SpanSet *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.spanset_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_from_wkb(wkb: bytes) -> 'SpanSet *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.spanset_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def textset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.textset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.textset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def timestampset_in(string: str) -> 'Set *':
    string_converted = string.encode('utf-8')
    result = _lib.timestampset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_out(set: 'const Set *') -> str:
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.timestampset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def bigintset_make(values: 'List[const int64]') -> 'Set *':
    values_converted = _ffi.new('const int64 []', values)
    result = _lib.bigintset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    lower_converted = _ffi.cast('int64', lower)
    upper_converted = _ffi.cast('int64', upper)
    result = _lib.bigintspan_make(lower_converted, upper_converted, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_make(values: 'List[const double]') -> 'Set *':
    values_converted = _ffi.new('const double []', values)
    result = _lib.floatset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_make(lower: float, upper: float, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.floatspan_make(lower, upper, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_make(values: 'const GSERIALIZED **') -> 'Set *':
    values_converted = [_ffi.cast('const GSERIALIZED *', x) for x in values]
    result = _lib.geoset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def intset_make(values: 'List[const int]') -> 'Set *':
    values_converted = _ffi.new('const int []', values)
    result = _lib.intset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.intspan_make(lower, upper, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def period_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    lower_converted = _ffi.cast('TimestampTz', lower)
    upper_converted = _ffi.cast('TimestampTz', upper)
    result = _lib.period_make(lower_converted, upper_converted, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def set_copy(s: 'const Set *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_copy(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_copy(s: 'const Span *') -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_copy(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_copy(ps: 'const SpanSet *') -> 'SpanSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.spanset_copy(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make(spans: 'List[Span *]', normalize: bool) -> 'SpanSet *':
    spans_converted = _ffi.new('Span []', spans)
    result = _lib.spanset_make(spans_converted, len(spans), normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_make(values: List[str]) -> 'Set *':
    values_converted = [cstring2text(x) for x in values]
    result = _lib.textset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_make(values: List[int]) -> 'Set *':
    values_converted = [_ffi.cast('const TimestampTz', x) for x in values]
    result = _lib.timestampset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_bigintset(i: int) -> 'Set *':
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_to_bigintset(i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_bigintspan(i: int) -> 'Span *':
    result = _lib.bigint_to_bigintspan(i)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_bigintspanset(i: int) -> 'SpanSet *':
    result = _lib.bigint_to_bigintspanset(i)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_floatset(d: float) -> 'Set *':
    result = _lib.float_to_floatset(d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_floatspan(d: float) -> 'Span *':
    result = _lib.float_to_floatspan(d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_floatspanset(d: float) -> 'SpanSet *':
    result = _lib.float_to_floatspanset(d)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_to_geoset(gs: 'GSERIALIZED *') -> 'Set *':
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.geo_to_geoset(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_intset(i: int) -> 'Set *':
    result = _lib.int_to_intset(i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_intspan(i: int) -> 'Span *':
    result = _lib.int_to_intspan(i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_intspanset(i: int) -> 'SpanSet *':
    result = _lib.int_to_intspanset(i)
    _check_error()
    return result if result != _ffi.NULL else None


def set_to_spanset(s: 'const Set *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_to_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_to_spanset(s: 'const Span *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_to_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text_to_textset(txt: str) -> 'Set *':
    txt_converted = cstring2text(txt)
    result = _lib.text_to_textset(txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_to_period(t: int) -> 'Span *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_period(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_to_periodset(t: int) -> 'SpanSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_periodset(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_to_tstzset(t: int) -> 'Set *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_tstzset(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_end_value(s: 'const Set *') -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_start_value(s: 'const Set *') -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_value_n(s: 'const Set *', n: int) -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int64 *')
    result = _lib.bigintset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def bigintset_values(s: 'const Set *') -> 'int64 *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.bigintset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_lower(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_upper(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.bigintspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_lower(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_upper(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.bigintspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_end_value(s: 'const Set *') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_start_value(s: 'const Set *') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_value_n(s: 'const Set *', n: int) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('double *')
    result = _lib.floatset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def floatset_values(s: 'const Set *') -> 'double *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_lower(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_upper(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_lower(ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_upper(ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_end_value(s: 'const Set *') -> 'GSERIALIZED *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.geoset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_srid(set: 'const Set *') -> 'int':
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.geoset_srid(set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_start_value(s: 'const Set *') -> 'GSERIALIZED *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.geoset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_value_n(s: 'const Set *', n: int) -> 'GSERIALIZED **':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.geoset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def geoset_values(s: 'const Set *') -> 'GSERIALIZED **':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.geoset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_end_value(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_start_value(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_value_n(s: 'const Set *', n: int) -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int *')
    result = _lib.intset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intset_values(s: 'const Set *') -> 'int *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_lower(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_upper(s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_lower(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_upper(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_duration(s: 'const Span *') -> 'Interval *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_duration(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_lower(p: 'const Span *') -> 'TimestampTz':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_lower(p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_upper(p: 'const Span *') -> 'TimestampTz':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_upper(p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_duration(ps: 'const SpanSet *', boundspan: bool) -> 'Interval *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_duration(ps_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_end_timestamp(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_end_timestamp(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_lower(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_lower(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_num_timestamps(ps: 'const SpanSet *') -> 'int':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_num_timestamps(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_start_timestamp(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_start_timestamp(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_timestamp_n(ps: 'const SpanSet *', n: int) -> int:
    ps_converted = _ffi.cast('const SpanSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.periodset_timestamp_n(ps_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def periodset_timestamps(ps: 'const SpanSet *') -> "Tuple['TimestampTz *', 'int']":
    ps_converted = _ffi.cast('const SpanSet *', ps)
    count = _ffi.new('int *')
    result = _lib.periodset_timestamps(ps_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def periodset_upper(ps: 'const SpanSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_upper(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_hash(s: 'const Set *') -> 'uint32':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_hash(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_hash_extended(s: 'const Set *', seed: int) -> 'uint64':
    s_converted = _ffi.cast('const Set *', s)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.set_hash_extended(s_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_num_values(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_num_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_span(s: 'const Set *') -> 'Span *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_span(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_hash(s: 'const Span *') -> 'uint32':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_hash(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_hash_extended(s: 'const Span *', seed: int) -> 'uint64':
    s_converted = _ffi.cast('const Span *', s)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.span_hash_extended(s_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_lower_inc(s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_lower_inc(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_upper_inc(s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_upper_inc(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_width(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_width(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_end_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_end_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_hash(ps: 'const SpanSet *') -> 'uint32':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.spanset_hash(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_hash_extended(ps: 'const SpanSet *', seed: int) -> 'uint64':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.spanset_hash_extended(ps_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_lower_inc(ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_lower_inc(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_num_spans(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_num_spans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_span_n(ss: 'const SpanSet *', i: int) -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_span_n(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_spans(ss: 'const SpanSet *') -> 'const Span **':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_spans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_start_span(ss: 'const SpanSet *') -> 'Span *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_start_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_upper_inc(ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_upper_inc(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_width(ss: 'const SpanSet *', boundspan: bool) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_width(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def spatialset_stbox(s: 'const Set *') -> 'STBox *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.spatialset_stbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_end_value(s: 'const Set *') -> str:
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.textset_end_value(s_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def textset_start_value(s: 'const Set *') -> str:
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.textset_start_value(s_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def textset_value_n(s: 'const Set *', n: int) -> 'text **':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('text **')
    result = _lib.textset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def textset_values(s: 'const Set *') -> 'text **':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.textset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_end_timestamp(ts: 'const Set *') -> 'TimestampTz':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.timestampset_end_timestamp(ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_start_timestamp(ts: 'const Set *') -> 'TimestampTz':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.timestampset_start_timestamp(ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_timestamp_n(ts: 'const Set *', n: int) -> int:
    ts_converted = _ffi.cast('const Set *', ts)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.timestampset_timestamp_n(ts_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def timestampset_values(ts: 'const Set *') -> 'TimestampTz *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.timestampset_values(ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_shift_scale(s: 'const Set *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    shift_converted = _ffi.cast('int64', shift)
    width_converted = _ffi.cast('int64', width)
    result = _lib.bigintset_shift_scale(s_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_shift_scale(s: 'const Span *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    shift_converted = _ffi.cast('int64', shift)
    width_converted = _ffi.cast('int64', width)
    result = _lib.bigintspan_shift_scale(s_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_shift_scale(ss: 'const SpanSet *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    shift_converted = _ffi.cast('int64', shift)
    width_converted = _ffi.cast('int64', width)
    result = _lib.bigintspanset_shift_scale(ss_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_round(s: 'const Set *', maxdd: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_shift_scale(s: 'const Set *', shift: float, width: float, hasshift: bool, haswidth: bool) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.floatset_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_intspan(s: 'const Span *') -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_intspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_round(s: 'const Span *', maxdd: int) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_shift_scale(s: 'const Span *', shift: float, width: float, hasshift: bool, haswidth: bool) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.floatspan_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_intspanset(ss: 'const SpanSet *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_intspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_round(ss: 'const SpanSet *', maxdd: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_round(ss_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_shift_scale(ss: 'const SpanSet *', shift: float, width: float, hasshift: bool, haswidth: bool) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.floatspanset_shift_scale(ss_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_round(s: 'const Set *', maxdd: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.geoset_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_shift_scale(s: 'const Set *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.intset_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_floatspan(s: 'const Span *') -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_floatspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_shift_scale(s: 'const Span *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_floatspanset(ss: 'const SpanSet *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_floatspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_shift_scale(ss: 'const SpanSet *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.intspanset_shift_scale(ss_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def period_shift_scale(p: 'const Span *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'Span *':
    p_converted = _ffi.cast('const Span *', p)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.period_shift_scale(p_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_tprecision(s: 'const Span *', duration: 'const Interval *', torigin: int) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.period_tprecision(s_converted, duration_converted, torigin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_shift_scale(ss: 'const SpanSet *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.periodset_shift_scale(ss_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_tprecision(ss: 'const SpanSet *', duration: 'const Interval *', torigin: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.periodset_tprecision(ss_converted, duration_converted, torigin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_lower(s: 'const Set *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.textset_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_upper(s: 'const Set *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.textset_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_tprecision(t: int, duration: 'const Interval *', torigin: int) -> 'TimestampTz':
    t_converted = _ffi.cast('TimestampTz', t)
    duration_converted = _ffi.cast('const Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    result = _lib.timestamp_tprecision(t_converted, duration_converted, torigin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_shift_scale(ts: 'const Set *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'Set *':
    ts_converted = _ffi.cast('const Set *', ts)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.timestampset_shift_scale(ts_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_bigintset_bigint(s: 'const Set *', i: int) -> 'int64':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    out_result = _ffi.new('int64 *')
    result = _lib.intersection_bigintset_bigint(s_converted, i_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_bigintspan_bigint(s: 'const Span *', i: int) -> 'int64':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    out_result = _ffi.new('int64 *')
    result = _lib.intersection_bigintspan_bigint(s_converted, i_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'int64':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    out_result = _ffi.new('int64 *')
    result = _lib.intersection_bigintspanset_bigint(ss_converted, i_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_floatset_float(s: 'const Set *', d: float) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('double *')
    result = _lib.intersection_floatset_float(s_converted, d, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_floatspan_float(s: 'const Span *', d: float) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('double *')
    result = _lib.intersection_floatspan_float(s_converted, d, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('double *')
    result = _lib.intersection_floatspanset_float(ss_converted, d, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_geoset_geo(s: 'const Set *', gs: 'const GSERIALIZED *') -> 'GSERIALIZED **':
    s_converted = _ffi.cast('const Set *', s)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.intersection_geoset_geo(s_converted, gs_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_intset_int(s: 'const Set *', i: int) -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int *')
    result = _lib.intersection_intset_int(s_converted, i, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_intspan_int(s: 'const Span *', i: int) -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('int *')
    result = _lib.intersection_intspan_int(s_converted, i, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_intspanset_int(ss: 'const SpanSet *', i: int) -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('int *')
    result = _lib.intersection_intspanset_int(ss_converted, i, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_period_timestamp(s: 'const Span *', t: int) -> int:
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_period_timestamp(s_converted, t_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_periodset_timestamp(ss: 'const SpanSet *', t: int) -> int:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_periodset_timestamp(ss_converted, t_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intersection_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.intersection_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.intersection_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intersection_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.intersection_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_textset_text(s: 'const Set *', txt: str) -> 'text **':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    out_result = _ffi.new('text **')
    result = _lib.intersection_textset_text(s_converted, txt_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_timestampset_timestamp(s: 'const Set *', t: int) -> int:
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestampset_timestamp(s_converted, t_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_bigint_bigintset(i: int, s: 'const Set *') -> 'int64':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int64 *')
    result = _lib.minus_bigint_bigintset(i_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_bigint_bigintspan(i: int, s: 'const Span *') -> 'int64':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('int64 *')
    result = _lib.minus_bigint_bigintspan(i_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'int64':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('int64 *')
    result = _lib.minus_bigint_bigintspanset(i_converted, ss_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_bigintset_bigint(s: 'const Set *', i: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.minus_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_bigintspan_bigint(s: 'const Span *', i: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.minus_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.minus_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_float_floatset(d: float, s: 'const Set *') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('double *')
    result = _lib.minus_float_floatset(d, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_float_floatspan(d: float, s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('double *')
    result = _lib.minus_float_floatspan(d, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('double *')
    result = _lib.minus_float_floatspanset(d, ss_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_floatset_float(s: 'const Set *', d: float) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.minus_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_floatspan_float(s: 'const Span *', d: float) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.minus_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.minus_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_geo_geoset(gs: 'const GSERIALIZED *', s: 'const Set *') -> 'GSERIALIZED **':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.minus_geo_geoset(gs_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def minus_geoset_geo(s: 'const Set *', gs: 'const GSERIALIZED *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.minus_geoset_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_int_intset(i: int, s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('int *')
    result = _lib.minus_int_intset(i, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_int_intspan(i: int, s: 'const Span *') -> 'int':
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('int *')
    result = _lib.minus_int_intspan(i, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_int_intspanset(i: int, ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('int *')
    result = _lib.minus_int_intspanset(i, ss_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_intset_int(s: 'const Set *', i: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.minus_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_intspan_int(s: 'const Span *', i: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.minus_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_intspanset_int(ss: 'const SpanSet *', i: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.minus_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_period_timestamp(s: 'const Span *', t: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.minus_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_span(s1: 'const Span *', s2: 'const Span *') -> 'SpanSet *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.minus_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.minus_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.minus_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.minus_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_text_textset(txt: str, s: 'const Set *') -> 'text **':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('text **')
    result = _lib.minus_text_textset(txt_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def minus_textset_text(s: 'const Set *', txt: str) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.minus_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamp_period(t: int, s: 'const Span *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_period(t_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_timestamp_periodset(t: int, ss: 'const SpanSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_periodset(t_converted, ss_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_timestamp_timestampset(t: int, s: 'const Set *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_timestampset(t_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def minus_timestampset_timestamp(s: 'const Set *', t: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigintset_bigint(s: 'const Set *', i: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.union_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigintspan_bigint(s: 'const Span *', i: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.union_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.union_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_floatset_float(s: 'const Set *', d: float) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.union_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_floatspan_float(s: 'const Span *', d: float) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.union_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.union_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_geoset_geo(s: 'const Set *', gs: 'const GSERIALIZED *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.union_geoset_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_intset_int(s: 'const Set *', i: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.union_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_intspan_int(s: 'const Span *', i: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.union_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_intspanset_int(ss: 'const SpanSet *', i: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.union_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_period_timestamp(s: 'const Span *', t: int) -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_periodset_timestamp(ss: 'SpanSet *', t: int) -> 'SpanSet *':
    ss_converted = _ffi.cast('SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_set(s1: 'const Set *', s2: 'const Set *') -> 'Set *':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.union_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_span(s1: 'const Span *', s2: 'const Span *') -> 'SpanSet *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.union_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.union_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'SpanSet *':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.union_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_textset_text(s: 'const Set *', txt: str) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.union_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_timestampset_timestamp(s: 'const Set *', t: int) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('const TimestampTz', t)
    result = _lib.union_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.adjacent_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.adjacent_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.adjacent_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.adjacent_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_period_timestamp(p_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_periodset_timestamp(ps_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.adjacent_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.adjacent_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_bigint_bigintset(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_bigint_bigintspan(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_bigint_bigintspanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_float_floatset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_float_floatspan(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_float_floatspanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_int_intset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_int_intspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_intspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_int_intspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contained_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contained_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.contained_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_text_textset(txt: str, s: 'const Set *') -> 'bool':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamp_period(t: int, p: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.contained_timestamp_period(t_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamp_periodset(t: int, ss: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_timestamp_periodset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.contained_timestamp_timestampset(t_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_bigintset_bigint(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.contains_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.contains_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.contains_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_floatset_float(s: 'const Set *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contains_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contains_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_intset_int(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contains_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contains_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_period_timestamp(p: 'const Span *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Span *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_period_timestamp(p_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_periodset_timestamp(ps: 'const SpanSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_periodset_timestamp(ps_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contains_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contains_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contains_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.contains_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_textset_text(s: 'const Set *', t: str) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = cstring2text(t)
    result = _lib.contains_textset_text(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_timestampset_timestamp(s: 'const Set *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overlaps_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overlaps_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overlaps_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overlaps_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_period_timestamp(s: 'const Span *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamp_period(t: int, s: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.after_timestamp_period(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamp_periodset(t: int, ss: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.after_timestamp_periodset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.after_timestamp_timestampset(t_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestampset_timestamp(s: 'const Set *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_period_timestamp(s: 'const Span *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamp_period(t: int, s: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.before_timestamp_period(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamp_periodset(t: int, ss: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.before_timestamp_periodset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.before_timestamp_timestampset(t_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestampset_timestamp(s: 'const Set *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_bigint_bigintset(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_bigint_bigintspan(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_bigint_bigintspanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigintset_bigint(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.left_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.left_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.left_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_float_floatset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_float_floatspan(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_float_floatspanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_floatset_float(s: 'const Set *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_int_intset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_int_intspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_intspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_int_intspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_intset_int(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.left_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.left_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.left_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_text_textset(txt: str, s: 'const Set *') -> 'bool':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_textset_text(s: 'const Set *', txt: str) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.left_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_period_timestamp(s: 'const Span *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamp_period(t: int, s: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overafter_timestamp_period(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamp_periodset(t: int, ss: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overafter_timestamp_periodset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.overafter_timestamp_timestampset(t_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestampset_timestamp(s: 'const Set *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_period_timestamp(s: 'const Span *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamp_period(t: int, s: 'const Span *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overbefore_timestamp_period(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamp_periodset(t: int, ss: 'const SpanSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overbefore_timestamp_periodset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamp_timestampset(t: int, ts: 'const Set *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.overbefore_timestamp_timestampset(t_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestampset_timestamp(s: 'const Set *', t: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_bigint_bigintset(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_bigint_bigintspan(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_bigint_bigintspanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigintset_bigint(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overleft_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overleft_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overleft_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_float_floatset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_float_floatspan(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_float_floatspanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_floatset_float(s: 'const Set *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_int_intset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_int_intspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_intspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_int_intspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_intset_int(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overleft_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overleft_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overleft_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_text_textset(txt: str, s: 'const Set *') -> 'bool':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_textset_text(s: 'const Set *', txt: str) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.overleft_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_bigint_bigintset(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_bigint_bigintspan(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_bigint_bigintspanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigintset_bigint(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overright_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overright_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.overright_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_float_floatset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_float_floatspan(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_float_floatspanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_floatset_float(s: 'const Set *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_int_intset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_int_intspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_intspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_int_intspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_intset_int(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overright_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overright_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.overright_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_text_textset(txt: str, s: 'const Set *') -> 'bool':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_textset_text(s: 'const Set *', txt: str) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.overright_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_bigintset(i: int, s: 'const Set *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_bigint_bigintset(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_bigintspan(i: int, s: 'const Span *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_bigint_bigintspan(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_bigintspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    i_converted = _ffi.cast('int64', i)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_bigint_bigintspanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigintset_bigint(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.right_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigintspan_bigint(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.right_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.right_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_floatset(d: float, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_float_floatset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_float_floatspan(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_floatspanset(d: float, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_float_floatspanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_floatset_float(s: 'const Set *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_intset(i: int, s: 'const Set *') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_int_intset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_int_intspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_intspanset(i: int, ss: 'const SpanSet *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_int_intspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_intset_int(s: 'const Set *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_intspanset_int(ss: 'const SpanSet *', i: int) -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.right_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.right_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_spanset(s: 'const Span *', ss: 'const SpanSet *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.right_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_text_textset(txt: str, s: 'const Set *') -> 'bool':
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_textset_text(s: 'const Set *', txt: str) -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    txt_converted = cstring2text(txt)
    result = _lib.right_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintset_bigint(s: 'const Set *', i: int) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.distance_bigintset_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintspan_bigint(s: 'const Span *', i: int) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.distance_bigintspan_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintspanset_bigint(ss: 'const SpanSet *', i: int) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    i_converted = _ffi.cast('int64', i)
    result = _lib.distance_bigintspanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatset_float(s: 'const Set *', d: float) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.distance_floatset_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatspan_float(s: 'const Span *', d: float) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_floatspan_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatspanset_float(ss: 'const SpanSet *', d: float) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.distance_floatspanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intset_int(s: 'const Set *', i: int) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.distance_intset_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intspan_int(s: 'const Span *', i: int) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_intspan_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intspanset_int(ss: 'const SpanSet *', i: int) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.distance_intspanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_period_timestamp(s: 'const Span *', t: int) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_period_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_periodset_timestamp(ss: 'const SpanSet *', t: int) -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_periodset_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_set(s1: 'const Set *', s2: 'const Set *') -> 'double':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.distance_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_span(s1: 'const Span *', s2: 'const Span *') -> 'double':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.distance_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_span(ss: 'const SpanSet *', s: 'const Span *') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_spanset(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'double':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.distance_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_timestampset_timestamp(s: 'const Set *', t: int) -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_timestampset_timestamp(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_cmp(s1: 'const Set *', s2: 'const Set *') -> 'int':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_cmp(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_eq(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_eq(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_ge(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_ge(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_gt(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_gt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_le(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_le(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_lt(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_lt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_ne(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.set_ne(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_cmp(s1: 'const Span *', s2: 'const Span *') -> 'int':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_cmp(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_eq(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_eq(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_ge(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_ge(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_gt(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_gt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_le(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_le(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_lt(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_lt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_ne(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_ne(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_cmp(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'int':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_cmp(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_eq(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_eq(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_ge(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_ge(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_gt(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_gt(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_le(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_le(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_lt(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_lt(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_ne(ss1: 'const SpanSet *', ss2: 'const SpanSet *') -> 'bool':
    ss1_converted = _ffi.cast('const SpanSet *', ss1)
    ss2_converted = _ffi.cast('const SpanSet *', ss2)
    result = _lib.spanset_ne(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_extent_transfn(s: 'Span *', i: int) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_extent_transfn(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_union_transfn(state: 'Set *', i: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    i_converted = _ffi.cast('int64', i)
    result = _lib.bigint_union_transfn(state_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_extent_transfn(s: 'Span *', d: float) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.float_extent_transfn(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_union_transfn(state: 'Set *', d: float) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.float_union_transfn(state_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def int_extent_transfn(s: 'Span *', i: int) -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.int_extent_transfn(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_union_transfn(state: 'Set *', i: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.int_union_transfn(state_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def period_tcount_transfn(state: "Optional['SkipList *']", p: 'const Span *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_tcount_transfn(state_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_tcount_transfn(state: "Optional['SkipList *']", ps: 'const SpanSet *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_tcount_transfn(state_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_extent_transfn(span: 'Span *', set: 'const Set *') -> 'Span *':
    span_converted = _ffi.cast('Span *', span)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.set_extent_transfn(span_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_union_finalfn(state: 'Set *') -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    result = _lib.set_union_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_union_transfn(state: 'Set *', set: 'Set *') -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    set_converted = _ffi.cast('Set *', set)
    result = _lib.set_union_transfn(state_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_extent_transfn(s1: 'Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_extent_transfn(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_union_transfn(state: 'SpanSet *', span: 'const Span *') -> 'SpanSet *':
    state_converted = _ffi.cast('SpanSet *', state)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.span_union_transfn(state_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_extent_transfn(s: 'Span *', ss: 'const SpanSet *') -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_extent_transfn(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_union_finalfn(state: 'SpanSet *') -> 'SpanSet *':
    state_converted = _ffi.cast('SpanSet *', state)
    result = _lib.spanset_union_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_union_transfn(state: 'SpanSet *', ss: 'const SpanSet *') -> 'SpanSet *':
    state_converted = _ffi.cast('SpanSet *', state)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_union_transfn(state_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text_union_transfn(state: 'Set *', txt: str) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    txt_converted = cstring2text(txt)
    result = _lib.text_union_transfn(state_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_extent_transfn(p: "Optional['Span *']", t: int) -> 'Span *':
    p_converted = _ffi.cast('Span *', p) if p is not None else _ffi.NULL
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_extent_transfn(p_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_tcount_transfn(state: "Optional['SkipList *']", t: int) -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_tcount_transfn(state_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_union_transfn(state: 'Set *', t: int) -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_union_transfn(state_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_tcount_transfn(state: "Optional['SkipList *']", ts: 'const Set *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.timestampset_tcount_transfn(state_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_in(string: str) -> 'TBox *':
    string_converted = string.encode('utf-8')
    result = _lib.tbox_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_out(box: 'const TBox *', maxdd: int) -> str:
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_out(box_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbox_from_wkb(wkb: bytes) -> 'TBOX *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.tbox_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def tbox_from_hexwkb(hexwkb: str) -> 'TBox *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.tbox_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_from_wkb(wkb: bytes) -> 'STBOX *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.stbox_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def stbox_from_hexwkb(hexwkb: str) -> 'STBox *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.stbox_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_as_wkb(box: 'const TBox *', variant: int) -> bytes:
    box_converted = _ffi.cast('const TBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.tbox_as_wkb(box_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def tbox_as_hexwkb(box: 'const TBox *', variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast('const TBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size = _ffi.new('size_t *')
    result = _lib.tbox_as_hexwkb(box_converted, variant_converted, size)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size[0]


def stbox_as_wkb(box: 'const STBox *', variant: int) -> bytes:
    box_converted = _ffi.cast('const STBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.stbox_as_wkb(box_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def stbox_as_hexwkb(box: 'const STBox *', variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast('const STBox *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size = _ffi.new('size_t *')
    result = _lib.stbox_as_hexwkb(box_converted, variant_converted, size)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size[0]


def stbox_in(string: str) -> 'STBox *':
    string_converted = string.encode('utf-8')
    result = _lib.stbox_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_out(box: 'const STBox *', maxdd: int) -> str:
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_out(box_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def float_period_to_tbox(d: float, p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.float_period_to_tbox(d, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_timestamp_to_tbox(d: float, t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.float_timestamp_to_tbox(d, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_period_to_stbox(gs: 'const GSERIALIZED *', p: 'const Span *') -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.geo_period_to_stbox(gs_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_timestamp_to_stbox(gs: 'const GSERIALIZED *', t: int) -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.geo_timestamp_to_stbox(gs_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_period_to_tbox(i: int, p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.int_period_to_tbox(i, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_timestamp_to_tbox(i: int, t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.int_timestamp_to_tbox(i, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_period_to_tbox(span: 'const Span *', p: 'const Span *') -> 'TBox *':
    span_converted = _ffi.cast('const Span *', span)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.span_period_to_tbox(span_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_timestamp_to_tbox(span: 'const Span *', t: int) -> 'TBox *':
    span_converted = _ffi.cast('const Span *', span)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.span_timestamp_to_tbox(span_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_copy(box: 'const STBox *') -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_copy(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_make(hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, p: "Optional['const Span *']") -> 'STBox *':
    srid_converted = _ffi.cast('int32', srid)
    p_converted = _ffi.cast('const Span *', p) if p is not None else _ffi.NULL
    result = _lib.stbox_make(hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_copy(box: 'const TBox *') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_copy(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_make(s: "Optional['const Span *']", p: "Optional['const Span *']") -> 'TBox *':
    s_converted = _ffi.cast('const Span *', s) if s is not None else _ffi.NULL
    p_converted = _ffi.cast('const Span *', p) if p is not None else _ffi.NULL
    result = _lib.tbox_make(s_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_tbox(d: float) -> 'TBox *':
    result = _lib.float_to_tbox(d)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_to_stbox(gs: 'const GSERIALIZED *') -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_to_stbox(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_tbox(i: int) -> 'TBox *':
    result = _lib.int_to_tbox(i)
    _check_error()
    return result if result != _ffi.NULL else None


def numset_to_tbox(s: 'const Set *') -> 'TBox *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.numset_to_tbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_to_tbox(s: 'const Span *') -> 'TBox *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.numspan_to_tbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_to_tbox(ss: 'const SpanSet *') -> 'TBox *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.numspanset_to_tbox(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_to_stbox(p: 'const Span *') -> 'STBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_to_stbox(p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def period_to_tbox(p: 'const Span *') -> 'TBox *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.period_to_tbox(p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_to_stbox(ps: 'const SpanSet *') -> 'STBox *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_to_stbox(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def periodset_to_tbox(ps: 'const SpanSet *') -> 'TBox *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.periodset_to_tbox(ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_geo(box: 'const STBox *') -> 'GSERIALIZED *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_to_geo(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_period(box: 'const STBox *') -> 'Span *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_to_period(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_to_floatspan(box: 'const TBox *') -> 'Span *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_to_floatspan(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_to_period(box: 'const TBox *') -> 'Span *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_to_period(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_to_stbox(t: int) -> 'STBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_stbox(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamp_to_tbox(t: int) -> 'TBox *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_tbox(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_to_stbox(ts: 'const Set *') -> 'STBox *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.timestampset_to_stbox(ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestampset_to_tbox(ss: 'const Set *') -> 'TBox *':
    ss_converted = _ffi.cast('const Set *', ss)
    result = _lib.timestampset_to_tbox(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_to_tbox(temp: 'const Temporal *') -> 'TBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_to_tbox(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_to_stbox(temp: 'const Temporal *') -> 'STBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_to_stbox(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hast(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hast(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hasx(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hasx(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hasz(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_hasz(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_isgeodetic(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_isgeodetic(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_srid(box: 'const STBox *') -> 'int32':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_srid(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_tmax(box: 'const STBox *') -> int:
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmax_inc(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.stbox_tmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmin(box: 'const STBox *') -> int:
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmin_inc(box: 'const STBox *') -> 'bool':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.stbox_tmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_xmax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_xmin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_ymax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_ymin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_zmax(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_zmin(box: 'const STBox *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_hast(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_hast(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_hasx(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_hasx(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_tmax(box: 'const TBox *') -> int:
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmax_inc(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.tbox_tmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmin(box: 'const TBox *') -> int:
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmin_inc(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.tbox_tmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmax(box: 'const TBox *') -> 'double':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmax_inc(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.tbox_xmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmin(box: 'const TBox *') -> 'double':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmin_inc(box: 'const TBox *') -> 'bool':
    box_converted = _ffi.cast('const TBox *', box)
    out_result = _ffi.new('bool *')
    result = _lib.tbox_xmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_expand_space(box: 'const STBox *', d: float) -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_expand_space(box_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_expand_time(box: 'const STBox *', interval: 'const Interval *') -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.stbox_expand_time(box_converted, interval_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_get_space(box: 'const STBox *') -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_get_space(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_round(box: 'const STBox *', maxdd: int) -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.stbox_round(box_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_set_srid(box: 'const STBox *', srid: int) -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.stbox_set_srid(box_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_shift_scale_time(box: 'const STBox *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'STBox *':
    box_converted = _ffi.cast('const STBox *', box)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.stbox_shift_scale_time(box_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_expand_time(box: 'const TBox *', interval: 'const Interval *') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.tbox_expand_time(box_converted, interval_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_expand_value(box: 'const TBox *', d: 'const double') -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    d_converted = _ffi.cast('const double', d)
    result = _lib.tbox_expand_value(box_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_round(box: 'const TBox *', maxdd: int) -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_round(box_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_float(box: 'const TBox *', shift: float, width: float, hasshift: bool, haswidth: bool) -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_shift_scale_float(box_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_int(box: 'const TBox *', shift: int, width: int, hasshift: bool, haswidth: bool) -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tbox_shift_scale_int(box_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_time(box: 'const TBox *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.tbox_shift_scale_time(box_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *', strict: bool) -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.union_tbox_tbox(box1_converted, box2_converted, strict)
    _check_error()
    return result if result != _ffi.NULL else None


def inter_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    out_result = _ffi.new('TBox *')
    result = _lib.inter_tbox_tbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.intersection_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *', strict: bool) -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.union_stbox_stbox(box1_converted, box2_converted, strict)
    _check_error()
    return result if result != _ffi.NULL else None


def inter_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    out_result = _ffi.new('STBox *')
    result = _lib.inter_stbox_stbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.intersection_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.contains_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.contained_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overlaps_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.same_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.adjacent_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.contains_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.contained_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overlaps_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.same_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.adjacent_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.left_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overleft_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.right_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overright_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.before_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overbefore_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.after_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.overafter_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.left_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overleft_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.right_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overright_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def below_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.below_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbelow_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overbelow_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def above_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.above_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overabove_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overabove_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def front_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.front_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overfront_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overfront_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def back_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.back_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overback_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overback_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.before_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overbefore_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.after_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.overafter_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_quad_split(box: 'const STBox *') -> "Tuple['STBox *', 'int']":
    box_converted = _ffi.cast('const STBox *', box)
    count = _ffi.new('int *')
    result = _lib.stbox_quad_split(box_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tbox_eq(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_eq(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_ne(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_ne(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_cmp(box1: 'const TBox *', box2: 'const TBox *') -> 'int':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_cmp(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_lt(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_lt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_le(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_le(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_ge(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_ge(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_gt(box1: 'const TBox *', box2: 'const TBox *') -> 'bool':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.tbox_gt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_eq(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_eq(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_ne(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_ne(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_cmp(box1: 'const STBox *', box2: 'const STBox *') -> 'int':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_cmp(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_lt(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_lt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_le(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_le(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_ge(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_ge(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_gt(box1: 'const STBox *', box2: 'const STBox *') -> 'bool':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.stbox_gt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tbool_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_as_hexwkb(temp: 'const Temporal *', variant: int) -> "Tuple[str, 'size_t *']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.temporal_as_hexwkb(temp_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out[0]


def temporal_as_mfjson(temp: 'const Temporal *', with_bbox: bool, flags: int, precision: int, srs: "Optional[str]") -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    srs_converted = srs.encode('utf-8') if srs is not None else _ffi.NULL
    result = _lib.temporal_as_mfjson(temp_converted, with_bbox, flags, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_as_wkb(temp: 'const Temporal *', variant: int) -> bytes:
    temp_converted = _ffi.cast('const Temporal *', temp)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.temporal_as_wkb(temp_converted, variant_converted, size_out)
    _check_error()
    result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    return result_converted


def temporal_from_hexwkb(hexwkb: str) -> 'Temporal *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.temporal_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_mfjson(mfjson: str) -> 'Temporal *':
    mfjson_converted = mfjson.encode('utf-8')
    result = _lib.temporal_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_wkb(wkb: bytes) -> 'Temporal *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.temporal_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def tfloat_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tfloat_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_out(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tgeogpoint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeogpoint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeompoint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.tint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_as_ewkt(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_as_ewkt(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_as_text(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_as_text(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpoint_out(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttext_in(string: str) -> 'Temporal *':
    string_converted = string.encode('utf-8')
    result = _lib.ttext_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_out(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbool_from_base_temp(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_from_base_temp(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_make(b: bool, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tboolinst_make(b, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_from_base_period(b: bool, p: 'const Span *') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tboolseq_from_base_period(b, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_from_base_timestampset(b: bool, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tboolseq_from_base_timestampset(b, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_from_base_periodset(b: bool, ps: 'const SpanSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tboolseqset_from_base_periodset(b, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_copy(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_copy(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_from_base_temp(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_from_base_temp(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_make(d: float, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tfloatinst_make(d, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_period(d: float, p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseq_from_base_period(d, p_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_timestampset(d: float, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tfloatseq_from_base_timestampset(d, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base_periodset(d: float, ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseqset_from_base_periodset(d, ps_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_from_base_temp(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_from_base_temp(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintinst_make(i: int, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tintinst_make(i, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_from_base_period(i: int, p: 'const Span *') -> 'TSequence *':
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tintseq_from_base_period(i, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_from_base_timestampset(i: int, ts: 'const Set *') -> 'TSequence *':
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tintseq_from_base_timestampset(i, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_from_base_periodset(i: int, ps: 'const SpanSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tintseqset_from_base_periodset(i, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_from_base_temp(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_from_base_temp(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_make(gs: 'const GSERIALIZED *', t: int) -> 'TInstant *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tpointinst_make(gs_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_from_base_period(gs: 'const GSERIALIZED *', p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tpointseq_from_base_period(gs_converted, p_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_from_base_timestampset(gs: 'const GSERIALIZED *', ts: 'const Set *') -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tpointseq_from_base_timestampset(gs_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_from_base_periodset(gs: 'const GSERIALIZED *', ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tpointseqset_from_base_periodset(gs_converted, ps_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make(instants: 'const TInstant **', count: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make(instants_converted, count, lower_inc, upper_inc, interp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make(sequences: 'const TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make(sequences_converted, count, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_gaps(instants: 'const TInstant **', count: int, interp: 'interpType', maxt: 'Interval *', maxdist: float) -> 'TSequenceSet *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    maxt_converted = _ffi.cast('Interval *', maxt)
    result = _lib.tsequenceset_make_gaps(instants_converted, count, interp_converted, maxt_converted, maxdist)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_from_base_temp(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_from_base_temp(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextinst_make(txt: str, t: int) -> 'TInstant *':
    txt_converted = cstring2text(txt)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.ttextinst_make(txt_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_from_base_period(txt: str, p: 'const Span *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.ttextseq_from_base_period(txt_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_from_base_timestampset(txt: str, ts: 'const Set *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.ttextseq_from_base_timestampset(txt_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_from_base_periodset(txt: str, ps: 'const SpanSet *') -> 'TSequenceSet *':
    txt_converted = cstring2text(txt)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.ttextseqset_from_base_periodset(txt_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_period(temp: 'const Temporal *') -> 'Span *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_period(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_to_tint(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_to_tint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_to_tfloat(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_to_tfloat(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_to_span(temp: 'const Temporal *') -> 'Span *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_to_span(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_end_value(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_start_value(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_values(temp: 'const Temporal *') -> "Tuple['bool *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tbool_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_duration(temp: 'const Temporal *', boundspan: bool) -> 'Interval *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_duration(temp_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_sequence(temp: 'const Temporal *') -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_sequence(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_timestamp(temp: 'const Temporal *') -> 'TimestampTz':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_timestamp(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_hash(temp: 'const Temporal *') -> 'uint32':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_hash(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_instant_n(temp: 'const Temporal *', n: int) -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_instant_n(temp_converted, n)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_instants(temp: 'const Temporal *') -> "Tuple['const TInstant **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_instants(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_interp(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_interp(temp_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_max_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_max_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_min_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_min_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_instants(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_instants(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_sequences(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_sequences(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_timestamps(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_num_timestamps(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_segments(temp: 'const Temporal *') -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_segments(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_sequence_n(temp: 'const Temporal *', i: int) -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_sequence_n(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_sequences(temp: 'const Temporal *') -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_sequences(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_start_instant(temp: 'const Temporal *') -> 'const TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_start_sequence(temp: 'const Temporal *') -> 'TSequence *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_sequence(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_start_timestamp(temp: 'const Temporal *') -> 'TimestampTz':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_timestamp(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_stops(temp: 'const Temporal *', maxdist: float, minduration: 'const Interval *') -> 'TSequenceSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    minduration_converted = _ffi.cast('const Interval *', minduration)
    result = _lib.temporal_stops(temp_converted, maxdist, minduration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_subtype(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_subtype(temp_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_time(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_time(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_timestamp_n(temp: 'const Temporal *', n: int) -> int:
    temp_converted = _ffi.cast('const Temporal *', temp)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.temporal_timestamp_n(temp_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def temporal_timestamps(temp: 'const Temporal *') -> "Tuple['TimestampTz *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_timestamps(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tfloat_end_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_max_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_min_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_start_value(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_values(temp: 'const Temporal *') -> "Tuple['double *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tfloat_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tint_end_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_max_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_min_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_start_value(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_values(temp: 'const Temporal *') -> "Tuple['int *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tint_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tnumber_valuespans(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_valuespans(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_end_value(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_start_value(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_values(temp: 'const Temporal *') -> "Tuple['GSERIALIZED **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def ttext_end_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_end_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_max_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_max_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_min_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_min_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_start_value(temp: 'const Temporal *') -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_start_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_values(temp: 'const Temporal *') -> "Tuple['text **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.ttext_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_scale_time(temp: 'const Temporal *', duration: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    result = _lib.temporal_scale_time(temp_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_set_interp(temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.temporal_set_interp(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_shift_scale_time(temp: 'const Temporal *', shift: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('const Interval *', shift) if shift is not None else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    result = _lib.temporal_shift_scale_time(temp_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_shift_time(temp: 'const Temporal *', shift: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('const Interval *', shift)
    result = _lib.temporal_shift_time(temp_converted, shift_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tinstant(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tinstant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tsequence(temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.temporal_to_tsequence(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tsequenceset(temp: 'const Temporal *', interp: 'interpType') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.temporal_to_tsequenceset(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_scale_value(temp: 'const Temporal *', width: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_scale_value(temp_converted, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_shift_scale_value(temp: 'const Temporal *', shift: float, width: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_shift_scale_value(temp_converted, shift, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_shift_value(temp: 'const Temporal *', shift: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_shift_value(temp_converted, shift)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_scale_value(temp: 'const Temporal *', width: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_scale_value(temp_converted, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_shift_scale_value(temp: 'const Temporal *', shift: int, width: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_shift_scale_value(temp_converted, shift, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_shift_value(temp: 'const Temporal *', shift: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_shift_value(temp_converted, shift)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_append_tinstant(temp: 'Temporal *', inst: 'const TInstant *', maxdist: float, maxt: "Optional['Interval *']", expand: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('Temporal *', temp)
    inst_converted = _ffi.cast('const TInstant *', inst)
    maxt_converted = _ffi.cast('Interval *', maxt) if maxt is not None else _ffi.NULL
    result = _lib.temporal_append_tinstant(temp_converted, inst_converted, maxdist, maxt_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_append_tsequence(temp: 'Temporal *', seq: 'const TSequence *', expand: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('Temporal *', temp)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.temporal_append_tsequence(temp_converted, seq_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_period(temp: 'const Temporal *', p: 'const Span *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_delete_period(temp_converted, p_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_periodset(temp: 'const Temporal *', ps: 'const SpanSet *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_delete_periodset(temp_converted, ps_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_timestamp(temp: 'const Temporal *', t: int, connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_delete_timestamp(temp_converted, t_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_timestampset(temp: 'const Temporal *', ts: 'const Set *', connect: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_delete_timestampset(temp_converted, ts_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_insert(temp1: 'const Temporal *', temp2: 'const Temporal *', connect: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_insert(temp1_converted, temp2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_merge(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_merge(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_merge_array(temparr: 'Temporal **', count: int) -> 'Temporal *':
    temparr_converted = [_ffi.cast('Temporal *', x) for x in temparr]
    result = _lib.temporal_merge_array(temparr_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_update(temp1: 'const Temporal *', temp2: 'const Temporal *', connect: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_update(temp1_converted, temp2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_at_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_at_value(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_minus_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_minus_value(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('bool *')
    result = _lib.tbool_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def temporal_at_max(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_at_max(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_min(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_at_min(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_period(temp: 'const Temporal *', p: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_at_period(temp_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_periodset(temp: 'const Temporal *', ps: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_at_periodset(temp_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_at_timestamp(temp_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_timestampset(temp: 'const Temporal *', ts: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_at_timestampset(temp_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_values(temp: 'const Temporal *', set: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.temporal_at_values(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_max(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_minus_max(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_min(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_minus_min(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_period(temp: 'const Temporal *', p: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_minus_period(temp_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_periodset(temp: 'const Temporal *', ps: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_minus_periodset(temp_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_minus_timestamp(temp_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_timestampset(temp: 'const Temporal *', ts: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_minus_timestampset(temp_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_values(temp: 'const Temporal *', set: 'const Set *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.temporal_minus_values(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_at_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_at_value(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_minus_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_minus_value(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('double *')
    result = _lib.tfloat_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tint_at_value(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_at_value(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_minus_value(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_minus_value(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('int *')
    result = _lib.tint_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tnumber_at_span(temp: 'const Temporal *', span: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_at_span(temp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_at_spanset(temp: 'const Temporal *', ss: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumber_at_spanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_at_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tnumber_at_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_span(temp: 'const Temporal *', span: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_minus_span(temp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_spanset(temp: 'const Temporal *', ss: 'const SpanSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumber_minus_spanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.tnumber_minus_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_geom_time(temp: 'const Temporal *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpoint_at_geom_time(temp_converted, gs_converted, zspan_converted, period_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_stbox(temp: 'const Temporal *', box: 'const STBox *', border_inc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpoint_at_stbox(temp_converted, box_converted, border_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_at_value(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_geom_time(temp: 'const Temporal *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpoint_minus_geom_time(temp_converted, gs_converted, zspan_converted, period_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_stbox(temp: 'const Temporal *', box: 'const STBox *', border_inc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpoint_minus_stbox(temp_converted, box_converted, border_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_minus_value(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'GSERIALIZED **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.tpoint_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def ttext_at_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_at_value(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_minus_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_minus_value(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'text **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('text **')
    result = _lib.ttext_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def temporal_cmp(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_cmp(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_eq(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_eq(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ge(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_ge(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_gt(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_gt(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_le(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_le(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_lt(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_lt(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ne(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_ne(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_always_eq(temp: 'const Temporal *', b: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_always_eq(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_ever_eq(temp: 'const Temporal *', b: bool) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_ever_eq(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_always_eq(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_eq(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_always_le(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_le(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_always_lt(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_always_lt(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_ever_eq(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_eq(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_ever_le(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_le(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_ever_lt(temp: 'const Temporal *', d: float) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_ever_lt(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_always_eq(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_eq(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_always_le(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_le(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_always_lt(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_always_lt(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_ever_eq(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_eq(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_ever_le(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_le(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_ever_lt(temp: 'const Temporal *', i: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_ever_lt(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_always_eq(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_always_eq(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_ever_eq(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_ever_eq(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_always_eq(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_eq(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_always_le(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_le(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_always_lt(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_always_lt(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_ever_eq(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_eq(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_ever_le(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_le(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_ever_lt(temp: 'const Temporal *', txt: str) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_ever_lt(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_point_tpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.teq_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.teq_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.teq_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.teq_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tge_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tge_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tge_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tgt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tgt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tle_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tle_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tle_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tlt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tlt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tlt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_float_tfloat(d: float, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_int_tint(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_point_tpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tne_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tne_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tne_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.tne_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tand_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tand_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_tbool_tbool(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tand_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_when_true(temp: 'const Temporal *') -> 'SpanSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_when_true(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnot_tbool(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnot_tbool(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_bool_tbool(b: bool, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tor_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_tbool_bool(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tor_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_tbool_tbool(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tor_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.add_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.add_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.div_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.div_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_degrees(value: float, normalize: bool) -> 'double':
    result = _lib.float_degrees(value, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.mult_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.mult_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_int_tint(i: int, tnumber: 'const Temporal *') -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tint_int(tnumber: 'const Temporal *', i: int) -> 'Temporal *':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.sub_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'Temporal *':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.sub_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_round(temp: 'const Temporal *', maxdd: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_round(temp_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatarr_round(temp: 'const Temporal **', count: int, maxdd: int) -> 'Temporal **':
    temp_converted = [_ffi.cast('const Temporal *', x) for x in temp]
    result = _lib.tfloatarr_round(temp_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_degrees(temp: 'const Temporal *', normalize: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_degrees(temp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_derivative(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_derivative(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_radians(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_radians(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_abs(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_abs(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_angular_difference(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_angular_difference(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_delta_value(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_delta_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_text_ttext(txt: str, temp: 'const Temporal *') -> 'Temporal *':
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.textcat_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_ttext_text(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.textcat_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_ttext_ttext(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.textcat_ttext_ttext(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_upper(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_upper(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_lower(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_lower(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tfloat_float(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.distance_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tint_int(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.distance_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tnumber_tnumber(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.distance_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.distance_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.distance_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_stbox_geo(box: 'const STBox *', gs: 'const GSERIALIZED *') -> 'double':
    box_converted = _ffi.cast('const STBox *', box)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_stbox_geo(box_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'double':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    result = _lib.nad_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'double':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    result = _lib.nad_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tfloat_float(temp: 'const Temporal *', d: float) -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.nad_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tfloat_tfloat(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tfloat_tfloat(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tint_int(temp: 'const Temporal *', i: int) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.nad_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tint_tint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tint_tint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tnumber_tbox(temp: 'const Temporal *', box: 'const TBox *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBox *', box)
    result = _lib.nad_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_stbox(temp: 'const Temporal *', box: 'const STBox *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.nad_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nad_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nai_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'TInstant *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nai_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nai_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'TInstant *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.nai_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def shortestline_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'GSERIALIZED **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.shortestline_tpoint_geo(temp_converted, gs_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def shortestline_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'GSERIALIZED **':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.shortestline_tpoint_tpoint(temp1_converted, temp2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def bearing_point_point(gs1: 'const GSERIALIZED *', gs2: 'const GSERIALIZED *') -> 'double':
    gs1_converted = _ffi.cast('const GSERIALIZED *', gs1)
    gs2_converted = _ffi.cast('const GSERIALIZED *', gs2)
    out_result = _ffi.new('double *')
    result = _lib.bearing_point_point(gs1_converted, gs2_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def bearing_tpoint_point(temp: 'const Temporal *', gs: 'const GSERIALIZED *', invert: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.bearing_tpoint_point(temp_converted, gs_converted, invert)
    _check_error()
    return result if result != _ffi.NULL else None


def bearing_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.bearing_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_angular_difference(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_angular_difference(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_azimuth(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_azimuth(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_convex_hull(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_convex_hull(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_cumulative_length(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_cumulative_length(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_direction(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    out_result = _ffi.new('double *')
    result = _lib.tpoint_direction(temp_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tpoint_get_x(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_get_x(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_y(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_get_y(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_z(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_get_z(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_is_simple(temp: 'const Temporal *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_is_simple(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_length(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_length(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_speed(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_speed(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_srid(temp: 'const Temporal *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_srid(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_stboxes(temp: 'const Temporal *') -> "Tuple['STBox *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_stboxes(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_trajectory(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_trajectory(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_expand_space(gs: 'const GSERIALIZED *', d: float) -> 'STBox *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_expand_space(gs_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_to_tpoint(gs: 'const GSERIALIZED *') -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_to_tpoint(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpoint_to_tgeompoint(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeogpoint_to_tgeompoint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_to_tgeogpoint(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeompoint_to_tgeogpoint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_AsMVTGeom(temp: 'const Temporal *', bounds: 'const STBox *', extent: 'int32_t', buffer: 'int32_t', clip_geom: bool, gsarr: 'GSERIALIZED **', timesarr: 'int64 **') -> "Tuple['bool', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    bounds_converted = _ffi.cast('const STBox *', bounds)
    extent_converted = _ffi.cast('int32_t', extent)
    buffer_converted = _ffi.cast('int32_t', buffer)
    gsarr_converted = [_ffi.cast('GSERIALIZED *', x) for x in gsarr]
    timesarr_converted = [_ffi.cast('int64 *', x) for x in timesarr]
    count = _ffi.new('int *')
    result = _lib.tpoint_AsMVTGeom(temp_converted, bounds_converted, extent_converted, buffer_converted, clip_geom, gsarr_converted, timesarr_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_expand_space(temp: 'const Temporal *', d: float) -> 'STBox *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_expand_space(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_make_simple(temp: 'const Temporal *') -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_make_simple(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_round(temp: 'const Temporal *', maxdd: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_round(temp_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointarr_round(temp: 'const Temporal **', count: int, maxdd: int) -> 'Temporal **':
    temp_converted = [_ffi.cast('const Temporal *', x) for x in temp]
    result = _lib.tpointarr_round(temp_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_set_srid(temp: 'const Temporal *', srid: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.tpoint_set_srid(temp_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_to_geo_meas(tpoint: 'const Temporal *', measure: 'const Temporal *', segmentize: bool) -> 'GSERIALIZED **':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    measure_converted = _ffi.cast('const Temporal *', measure)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.tpoint_to_geo_meas(tpoint_converted, measure_converted, segmentize, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def econtains_geo_tpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'int':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.econtains_geo_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.edisjoint_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.edisjoint_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edwithin_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', dist: float) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.edwithin_tpoint_geo(temp_converted, gs_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def edwithin_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *', dist: float) -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.edwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def eintersects_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.eintersects_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def eintersects_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.eintersects_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def etouches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.etouches_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tcontains_geo_tpoint(gs: 'const GSERIALIZED *', temp: 'const Temporal *', restr: bool, atvalue: bool) -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tcontains_geo_tpoint(gs_converted, temp_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tdisjoint_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tdisjoint_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', dist: float, restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tdwithin_tpoint_geo(temp_converted, gs_converted, dist, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *', dist: float, restr: bool, atvalue: bool) -> 'Temporal *':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.tdwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tintersects_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tintersects_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def ttouches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.ttouches_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_tand_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_tand_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_tor_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_tor_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_extent_transfn(p: "Optional['Span *']", temp: 'const Temporal *') -> 'Span *':
    p_converted = _ffi.cast('Span *', p) if p is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_extent_transfn(p_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tagg_finalfn(state: 'SkipList *') -> 'Temporal *':
    state_converted = _ffi.cast('SkipList *', state)
    result = _lib.temporal_tagg_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tcount_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_tcount_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tsum_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_tsum_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tsum_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_tsum_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_extent_transfn(box: "Optional['TBox *']", temp: 'const Temporal *') -> 'TBox *':
    box_converted = _ffi.cast('TBox *', box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_extent_transfn(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_integral(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_integral(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_tavg_finalfn(state: 'SkipList *') -> 'Temporal *':
    state_converted = _ffi.cast('SkipList *', state)
    result = _lib.tnumber_tavg_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_tavg_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_tavg_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_twavg(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_twavg(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_extent_transfn(box: "Optional['STBox *']", temp: 'const Temporal *') -> 'STBox *':
    box_converted = _ffi.cast('STBox *', box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_extent_transfn(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_tcentroid_finalfn(state: 'SkipList *') -> 'Temporal *':
    state_converted = _ffi.cast('SkipList *', state)
    result = _lib.tpoint_tcentroid_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_tcentroid_transfn(state: 'SkipList *', temp: 'Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state)
    temp_converted = _ffi.cast('Temporal *', temp)
    result = _lib.tpoint_tcentroid_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_twcentroid(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_twcentroid(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_tmax_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_tmin_transfn(state: "Optional['SkipList *']", temp: 'const Temporal *') -> 'SkipList *':
    state_converted = _ffi.cast('SkipList *', state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.ttext_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_min_dist(temp: 'const Temporal *', dist: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_min_dist(temp_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_min_tdelta(temp: 'const Temporal *', mint: 'const Interval *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    mint_converted = _ffi.cast('const Interval *', mint)
    result = _lib.temporal_simplify_min_tdelta(temp_converted, mint_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_dp(temp: 'const Temporal *', eps_dist: float, synchronized: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_dp(temp_converted, eps_dist, synchronized)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_max_dist(temp: 'const Temporal *', eps_dist: float, synchronized: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify_max_dist(temp_converted, eps_dist, synchronized)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tprecision(temp: 'const Temporal *', duration: 'const Interval *', origin: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.temporal_tprecision(temp_converted, duration_converted, origin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tsample(temp: 'const Temporal *', duration: 'const Interval *', origin: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.temporal_tsample(temp_converted, duration_converted, origin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_dyntimewarp_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_dyntimewarp_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_dyntimewarp_path(temp1: 'const Temporal *', temp2: 'const Temporal *') -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    count = _ffi.new('int *')
    result = _lib.temporal_dyntimewarp_path(temp1_converted, temp2_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_frechet_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_frechet_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_frechet_path(temp1: 'const Temporal *', temp2: 'const Temporal *') -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    count = _ffi.new('int *')
    result = _lib.temporal_frechet_path(temp1_converted, temp2_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_hausdorff_distance(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'double':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.temporal_hausdorff_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_bucket(value: float, size: float, origin: float) -> 'double':
    result = _lib.float_bucket(value, size, origin)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_bucket_list(bounds: 'const Span *', size: float, origin: float) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast('const Span *', bounds)
    count = _ffi.new('int *')
    result = _lib.floatspan_bucket_list(bounds_converted, size, origin, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def int_bucket(value: int, size: int, origin: int) -> 'int':
    result = _lib.int_bucket(value, size, origin)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_bucket_list(bounds: 'const Span *', size: int, origin: int) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast('const Span *', bounds)
    count = _ffi.new('int *')
    result = _lib.intspan_bucket_list(bounds_converted, size, origin, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def period_bucket_list(bounds: 'const Span *', duration: 'const Interval *', origin: int) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast('const Span *', bounds)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    count = _ffi.new('int *')
    result = _lib.period_bucket_list(bounds_converted, duration_converted, origin_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def stbox_tile_list(bounds: 'const STBox *', xsize: float, ysize: float, zsize: float, duration: "Optional['const Interval *']", sorigin: 'GSERIALIZED *', torigin: int) -> "Tuple['STBox *', 'int']":
    bounds_converted = _ffi.cast('const STBox *', bounds)
    duration_converted = _ffi.cast('const Interval *', duration) if duration is not None else _ffi.NULL
    sorigin_converted = _ffi.cast('GSERIALIZED *', sorigin)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    count = _ffi.new('int *')
    result = _lib.stbox_tile_list(bounds_converted, xsize, ysize, zsize, duration_converted, sorigin_converted, torigin_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tintbox_tile_list(box: 'const TBox *', xsize: int, duration: 'const Interval *', xorigin: 'Optional[int]', torigin: "Optional[int]") -> "Tuple['TBox *', 'int']":
    box_converted = _ffi.cast('const TBox *', box)
    duration_converted = _ffi.cast('const Interval *', duration)
    xorigin_converted = xorigin if xorigin is not None else _ffi.NULL
    torigin_converted = _ffi.cast('TimestampTz', torigin) if torigin is not None else _ffi.NULL
    count = _ffi.new('int *')
    result = _lib.tintbox_tile_list(box_converted, xsize, duration_converted, xorigin_converted, torigin_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tfloatbox_tile_list(box: 'const TBox *', xsize: float, duration: 'const Interval *', xorigin: 'Optional[float]', torigin: "Optional[int]") -> "Tuple['TBox *', 'int']":
    box_converted = _ffi.cast('const TBox *', box)
    duration_converted = _ffi.cast('const Interval *', duration)
    xorigin_converted = xorigin if xorigin is not None else _ffi.NULL
    torigin_converted = _ffi.cast('TimestampTz', torigin) if torigin is not None else _ffi.NULL
    count = _ffi.new('int *')
    result = _lib.tfloatbox_tile_list(box_converted, xsize, duration_converted, xorigin_converted, torigin_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_time_split(temp: 'Temporal *', duration: 'Interval *', torigin: int) -> "Tuple['Temporal **', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    time_buckets = _ffi.new('TimestampTz **')
    count = _ffi.new('int *')
    result = _lib.temporal_time_split(temp_converted, duration_converted, torigin_converted, time_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, time_buckets[0], count[0]


def tfloat_value_split(temp: 'Temporal *', size: float, origin: float) -> "Tuple['Temporal **', 'double *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    value_buckets = _ffi.new('double **')
    count = _ffi.new('int *')
    result = _lib.tfloat_value_split(temp_converted, size, origin, value_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], count[0]


def tfloat_value_time_split(temp: 'Temporal *', size: float, duration: 'Interval *', vorigin: float, torigin: int) -> "Tuple['Temporal **', 'double *', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    value_buckets = _ffi.new('double **')
    time_buckets = _ffi.new('TimestampTz **')
    count = _ffi.new('int *')
    result = _lib.tfloat_value_time_split(temp_converted, size, duration_converted, vorigin, torigin_converted, value_buckets, time_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], time_buckets[0], count[0]


def timestamptz_bucket(timestamp: int, duration: 'const Interval *', origin: int) -> 'TimestampTz':
    timestamp_converted = _ffi.cast('TimestampTz', timestamp)
    duration_converted = _ffi.cast('const Interval *', duration)
    origin_converted = _ffi.cast('TimestampTz', origin)
    result = _lib.timestamptz_bucket(timestamp_converted, duration_converted, origin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_value_split(temp: 'Temporal *', size: int, origin: int) -> "Tuple['Temporal **', 'int *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    value_buckets = _ffi.new('int **')
    count = _ffi.new('int *')
    result = _lib.tint_value_split(temp_converted, size, origin, value_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], count[0]


def tint_value_time_split(temp: 'Temporal *', size: int, duration: 'Interval *', vorigin: int, torigin: int) -> "Tuple['Temporal **', 'int *', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    duration_converted = _ffi.cast('Interval *', duration)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    value_buckets = _ffi.new('int **')
    time_buckets = _ffi.new('TimestampTz **')
    count = _ffi.new('int *')
    result = _lib.tint_value_time_split(temp_converted, size, duration_converted, vorigin, torigin_converted, value_buckets, time_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], time_buckets[0], count[0]


def tpoint_space_split(temp: 'Temporal *', xsize: 'float', ysize: 'float', zsize: 'float', sorigin: 'GSERIALIZED *', bitmatrix: bool) -> "Tuple['Temporal **', 'GSERIALIZED ***', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    xsize_converted = _ffi.cast('float', xsize)
    ysize_converted = _ffi.cast('float', ysize)
    zsize_converted = _ffi.cast('float', zsize)
    sorigin_converted = _ffi.cast('GSERIALIZED *', sorigin)
    space_buckets = _ffi.new('GSERIALIZED ***')
    count = _ffi.new('int *')
    result = _lib.tpoint_space_split(temp_converted, xsize_converted, ysize_converted, zsize_converted, sorigin_converted, bitmatrix, space_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, space_buckets[0], count[0]


def tpoint_space_time_split(temp: 'Temporal *', xsize: 'float', ysize: 'float', zsize: 'float', duration: 'Interval *', sorigin: 'GSERIALIZED *', torigin: int, bitmatrix: bool) -> "Tuple['Temporal **', 'GSERIALIZED ***', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast('Temporal *', temp)
    xsize_converted = _ffi.cast('float', xsize)
    ysize_converted = _ffi.cast('float', ysize)
    zsize_converted = _ffi.cast('float', zsize)
    duration_converted = _ffi.cast('Interval *', duration)
    sorigin_converted = _ffi.cast('GSERIALIZED *', sorigin)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    space_buckets = _ffi.new('GSERIALIZED ***')
    time_buckets = _ffi.new('TimestampTz **')
    count = _ffi.new('int *')
    result = _lib.tpoint_space_time_split(temp_converted, xsize_converted, ysize_converted, zsize_converted, duration_converted, sorigin_converted, torigin_converted, bitmatrix, space_buckets, time_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, space_buckets[0], time_buckets[0], count[0]


def meostype_name(temptype: 'meosType') -> str:
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.meostype_name(temptype_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temptype_basetype(temptype: 'meosType') -> 'meosType':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.temptype_basetype(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def settype_basetype(settype: 'meosType') -> 'meosType':
    settype_converted = _ffi.cast('meosType', settype)
    result = _lib.settype_basetype(settype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spantype_basetype(spantype: 'meosType') -> 'meosType':
    spantype_converted = _ffi.cast('meosType', spantype)
    result = _lib.spantype_basetype(spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spantype_spansettype(spantype: 'meosType') -> 'meosType':
    spantype_converted = _ffi.cast('meosType', spantype)
    result = _lib.spantype_spansettype(spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spansettype_spantype(spansettype: 'meosType') -> 'meosType':
    spansettype_converted = _ffi.cast('meosType', spansettype)
    result = _lib.spansettype_spantype(spansettype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_spantype(basetype: 'meosType') -> 'meosType':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.basetype_spantype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_settype(basetype: 'meosType') -> 'meosType':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.basetype_settype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meostype_internal(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.meostype_internal(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_basetype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.meos_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alpha_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.alpha_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def number_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.number_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alphanum_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.alphanum_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.geo_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatial_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.spatial_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def time_type(timetype: 'meosType') -> 'bool':
    timetype_converted = _ffi.cast('meosType', timetype)
    result = _lib.time_type(timetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.set_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.set_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.numset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_numset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_numset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timeset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.timeset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_spantype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.set_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_set_spantype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_set_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alphanumset_type(settype: 'meosType') -> 'bool':
    settype_converted = _ffi.cast('meosType', settype)
    result = _lib.alphanumset_type(settype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.geoset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_geoset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_geoset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatialset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.spatialset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_spatialset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_spatialset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_basetype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.span_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_canon_basetype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.span_canon_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.span_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_bbox_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.span_bbox_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_basetype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.numspan_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.numspan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_numspan_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_numspan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespan_basetype(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.timespan_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespan_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.timespan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.spanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.numspanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespanset_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.timespanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.temporal_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.temporal_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temptype_continuous(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.temptype_continuous(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_byvalue(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.basetype_byvalue(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_varlength(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.basetype_varlength(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_length(basetype: 'meosType') -> 'int16':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.basetype_length(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def talphanum_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.talphanum_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def talpha_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.talpha_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.tnumber_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tnumber_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.ensure_tnumber_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.tnumber_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_settype(settype: 'meosType') -> 'bool':
    settype_converted = _ffi.cast('meosType', settype)
    result = _lib.tnumber_settype(settype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_spantype(settype: 'meosType') -> 'bool':
    settype_converted = _ffi.cast('meosType', settype)
    result = _lib.tnumber_spantype(settype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_spansettype(spansettype: 'meosType') -> 'bool':
    spansettype_converted = _ffi.cast('meosType', spansettype)
    result = _lib.tnumber_spansettype(spansettype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tspatial_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.tspatial_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tspatial_type(temptype: 'meosType') -> 'bool':
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.ensure_tspatial_type(temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tspatial_basetype(basetype: 'meosType') -> 'bool':
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.tspatial_basetype(basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeo_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tgeo_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tnumber_tgeo_type(type: 'meosType') -> 'bool':
    type_converted = _ffi.cast('meosType', type)
    result = _lib.ensure_tnumber_tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash(d: 'Datum', basetype: 'meosType') -> 'uint32':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.datum_hash(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash_extended(d: 'Datum', basetype: 'meosType', seed: int) -> 'uint64':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.datum_hash_extended(d_converted, basetype_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_in(string: str, basetype: 'meosType') -> 'Set *':
    string_converted = string.encode('utf-8')
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.set_in(string_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_out(s: 'const Set *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def span_in(string: str, spantype: 'meosType') -> 'Span *':
    string_converted = string.encode('utf-8')
    spantype_converted = _ffi.cast('meosType', spantype)
    result = _lib.span_in(string_converted, spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_out(s: 'const Span *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def spanset_in(string: str, spantype: 'meosType') -> 'SpanSet *':
    string_converted = string.encode('utf-8')
    spantype_converted = _ffi.cast('meosType', spantype)
    result = _lib.spanset_in(string_converted, spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_out(ss: 'const SpanSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def set_compact(s: 'const Set *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_compact(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_make(values: 'const Datum *', count: int, basetype: 'meosType', ordered: bool) -> 'Set *':
    values_converted = _ffi.cast('const Datum *', values)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.set_make(values_converted, count, basetype_converted, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def set_make_exp(values: 'const Datum *', count: int, maxcount: int, basetype: 'meosType', ordered: bool) -> 'Set *':
    values_converted = _ffi.cast('const Datum *', values)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.set_make_exp(values_converted, count, maxcount, basetype_converted, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def set_make_free(values: 'Datum *', count: int, basetype: 'meosType', ordered: bool) -> 'Set *':
    values_converted = _ffi.cast('Datum *', values)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.set_make_free(values_converted, count, basetype_converted, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def set_out(s: 'const Set *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def span_make(lower: 'Datum', upper: 'Datum', lower_inc: bool, upper_inc: bool, basetype: 'meosType') -> 'Span *':
    lower_converted = _ffi.cast('Datum', lower)
    upper_converted = _ffi.cast('Datum', upper)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.span_make(lower_converted, upper_converted, lower_inc, upper_inc, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_out(s: 'const Span *', maxdd: int) -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def span_set(lower: 'Datum', upper: 'Datum', lower_inc: bool, upper_inc: bool, basetype: 'meosType', s: 'Span *') -> None:
    lower_converted = _ffi.cast('Datum', lower)
    upper_converted = _ffi.cast('Datum', upper)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('Span *', s)
    _lib.span_set(lower_converted, upper_converted, lower_inc, upper_inc, basetype_converted, s_converted)
    _check_error()


def spanset_compact(ss: 'SpanSet *') -> 'SpanSet *':
    ss_converted = _ffi.cast('SpanSet *', ss)
    result = _lib.spanset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make_exp(spans: 'Span *', count: int, maxcount: int, normalize: bool, ordered: bool) -> 'SpanSet *':
    spans_converted = _ffi.cast('Span *', spans)
    result = _lib.spanset_make_exp(spans_converted, count, maxcount, normalize, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make_free(spans: 'Span *', count: int, normalize: bool) -> 'SpanSet *':
    spans_converted = _ffi.cast('Span *', spans)
    result = _lib.spanset_make_free(spans_converted, count, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_out(ss: 'const SpanSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def value_to_set(d: 'Datum', basetype: 'meosType') -> 'Set *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.value_to_set(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_to_span(d: 'Datum', basetype: 'meosType') -> 'Span *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.value_to_span(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_to_spanset(d: 'Datum', basetype: 'meosType') -> 'SpanSet *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.value_to_spanset(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_end_value(s: 'const Set *') -> 'Datum':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_mem_size(s: 'const Set *') -> 'int':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_mem_size(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_set_span(os: 'const Set *', s: 'Span *') -> None:
    os_converted = _ffi.cast('const Set *', os)
    s_converted = _ffi.cast('Span *', s)
    _lib.set_set_span(os_converted, s_converted)
    _check_error()


def set_start_value(s: 'const Set *') -> 'Datum':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_value_n(s: 'const Set *', n: int) -> 'Datum *':
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('Datum *')
    result = _lib.set_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def set_values(s: 'const Set *') -> 'Datum *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_mem_size(ss: 'const SpanSet *') -> 'int':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.spanset_mem_size(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatialset_set_stbox(set: 'const Set *', box: 'STBox *') -> None:
    set_converted = _ffi.cast('const Set *', set)
    box_converted = _ffi.cast('STBox *', box)
    _lib.spatialset_set_stbox(set_converted, box_converted)
    _check_error()


def value_set_span(d: 'Datum', basetype: 'meosType', s: 'Span *') -> None:
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('Span *', s)
    _lib.value_set_span(d_converted, basetype_converted, s_converted)
    _check_error()


def floatspan_round_int(span: 'const Span *', size: 'Datum') -> 'Span *':
    span_converted = _ffi.cast('const Span *', span)
    size_converted = _ffi.cast('Datum', size)
    out_result = _ffi.new('Span *')
    _lib.floatspan_round_int(span_converted, size_converted, out_result)
    _check_error()
    return out_result if out_result!= _ffi.NULL else None



def floatspan_set_intspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.floatspan_set_intspan(s1_converted, s2_converted)
    _check_error()


def floatspan_set_numspan(s1: 'const Span *', s2: 'Span *', basetype: 'meosType') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    basetype_converted = _ffi.cast('meosType', basetype)
    _lib.floatspan_set_numspan(s1_converted, s2_converted, basetype_converted)
    _check_error()


def intspan_set_floatspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.intspan_set_floatspan(s1_converted, s2_converted)
    _check_error()


def numset_shift_scale(s: 'const Set *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.numset_shift_scale(s_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_set_floatspan(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.numspan_set_floatspan(s1_converted, s2_converted)
    _check_error()


def numspan_shift_scale(s: 'const Span *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.numspan_shift_scale(s_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_shift_scale(ss: 'const SpanSet *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.numspanset_shift_scale(ss_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def set_compact(s: 'const Set *') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.set_compact(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_shift(s: 'const Set *', shift: 'Datum') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    shift_converted = _ffi.cast('Datum', shift)
    result = _lib.set_shift(s_converted, shift_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_expand(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.span_expand(s1_converted, s2_converted)
    _check_error()


def span_shift(s: 'Span *', value: 'Datum') -> None:
    s_converted = _ffi.cast('Span *', s)
    value_converted = _ffi.cast('Datum', value)
    _lib.span_shift(s_converted, value_converted)
    _check_error()


def spanset_shift(s: 'SpanSet *', value: 'Datum') -> None:
    s_converted = _ffi.cast('SpanSet *', s)
    value_converted = _ffi.cast('Datum', value)
    _lib.spanset_shift(s_converted, value_converted)
    _check_error()


def spanbase_extent_transfn(s: 'Span *', d: 'Datum', basetype: 'meosType') -> 'Span *':
    s_converted = _ffi.cast('Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.spanbase_extent_transfn(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_union_transfn(state: 'Set *', d: 'Datum', basetype: 'meosType') -> 'Set *':
    state_converted = _ffi.cast('Set *', state)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.value_union_transfn(state_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.adjacent_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.adjacent_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.contains_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.contains_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.contains_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contains_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.contained_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.contained_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.contained_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overlaps_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overlaps_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overlaps_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overlaps_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overlaps_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.left_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.left_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.left_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.left_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.left_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.left_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.left_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.right_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.right_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.right_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.right_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.right_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.right_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.right_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overleft_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overleft_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overleft_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overleft_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overleft_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overleft_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overleft_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.overright_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overright_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_set(s1: 'const Set *', s2: 'const Set *') -> 'bool':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.overright_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.overright_value_span(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'bool':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.overright_value_spanset(d_converted, basetype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overright_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'bool':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.overright_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def inter_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    out_result = _ffi.new('Span *')
    result = _lib.inter_span_span(s1_converted, s2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'Datum *':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    out_result = _ffi.new('Datum *')
    result = _lib.intersection_set_value(s_converted, d_converted, basetype_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'Datum *':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    out_result = _ffi.new('Datum *')
    result = _lib.intersection_span_value(s_converted, d_converted, basetype_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'Datum *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    out_result = _ffi.new('Datum *')
    result = _lib.intersection_spanset_value(ss_converted, d_converted, basetype_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def minus_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.minus_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.minus_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.minus_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'Datum *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    out_result = _ffi.new('Datum *')
    result = _lib.minus_value_set(d_converted, basetype_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def minus_value_span(d: 'Datum', basetype: 'meosType', s: 'const Span *') -> 'Datum *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Span *', s)
    out_result = _ffi.new('Datum *')
    result = _lib.minus_value_span(d_converted, basetype_converted, s_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def minus_value_spanset(d: 'Datum', basetype: 'meosType', ss: 'const SpanSet *') -> 'Datum *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    out_result = _ffi.new('Datum *')
    result = _lib.minus_value_spanset(d_converted, basetype_converted, ss_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def union_set_value(s: 'const Set *', d: 'const Datum', basetype: 'meosType') -> 'Set *':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('const Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.union_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_value(s: 'const Span *', v: 'Datum', basetype: 'meosType') -> 'SpanSet *':
    s_converted = _ffi.cast('const Span *', s)
    v_converted = _ffi.cast('Datum', v)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.union_span_value(s_converted, v_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'SpanSet *':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.union_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_value_value(l: 'Datum', r: 'Datum', basetype: 'meosType') -> 'double':
    l_converted = _ffi.cast('Datum', l)
    r_converted = _ffi.cast('Datum', r)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.distance_value_value(l_converted, r_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_value(s: 'const Span *', d: 'Datum', basetype: 'meosType') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.distance_span_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_value(ss: 'const SpanSet *', d: 'Datum', basetype: 'meosType') -> 'double':
    ss_converted = _ffi.cast('const SpanSet *', ss)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.distance_spanset_value(ss_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_value_set(d: 'Datum', basetype: 'meosType', s: 'const Set *') -> 'double':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    s_converted = _ffi.cast('const Set *', s)
    result = _lib.distance_value_set(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_value(s: 'const Set *', d: 'Datum', basetype: 'meosType') -> 'double':
    s_converted = _ffi.cast('const Set *', s)
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.distance_set_value(s_converted, d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_set(s1: 'const Set *', s2: 'const Set *') -> 'double':
    s1_converted = _ffi.cast('const Set *', s1)
    s2_converted = _ffi.cast('const Set *', s2)
    result = _lib.distance_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash(d: 'Datum', basetype: 'meosType') -> 'uint32':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.datum_hash(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash_extended(d: 'Datum', basetype: 'meosType', seed: int) -> 'uint64':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.datum_hash_extended(d_converted, basetype_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def number_period_to_tbox(d: 'Datum', basetype: 'meosType', p: 'const Span *') -> 'TBox *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.number_period_to_tbox(d_converted, basetype_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def number_timestamp_to_tbox(d: 'Datum', basetype: 'meosType', t: int) -> 'TBox *':
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.number_timestamp_to_tbox(d_converted, basetype_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_set(hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, p: 'const Span *', box: 'STBox *') -> None:
    srid_converted = _ffi.cast('int32', srid)
    p_converted = _ffi.cast('const Span *', p)
    box_converted = _ffi.cast('STBox *', box)
    _lib.stbox_set(hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, p_converted, box_converted)
    _check_error()


def tbox_set(s: 'const Span *', p: 'const Span *', box: 'TBox *') -> None:
    s_converted = _ffi.cast('const Span *', s)
    p_converted = _ffi.cast('const Span *', p)
    box_converted = _ffi.cast('TBox *', box)
    _lib.tbox_set(s_converted, p_converted, box_converted)
    _check_error()


def float_set_tbox(d: float, box: 'TBox *') -> None:
    box_converted = _ffi.cast('TBox *', box)
    _lib.float_set_tbox(d, box_converted)
    _check_error()


def geo_set_stbox(gs: 'const GSERIALIZED *', box: 'STBox *') -> 'bool':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    box_converted = _ffi.cast('STBox *', box)
    result = _lib.geo_set_stbox(gs_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoarr_set_stbox(values: 'const Datum *', count: int, box: 'STBox *') -> None:
    values_converted = _ffi.cast('const Datum *', values)
    box_converted = _ffi.cast('STBox *', box)
    _lib.geoarr_set_stbox(values_converted, count, box_converted)
    _check_error()


def int_set_tbox(i: int, box: 'TBox *') -> None:
    box_converted = _ffi.cast('TBox *', box)
    _lib.int_set_tbox(i, box_converted)
    _check_error()


def number_set_tbox(d: 'Datum', basetype: 'meosType', box: 'TBox *') -> None:
    d_converted = _ffi.cast('Datum', d)
    basetype_converted = _ffi.cast('meosType', basetype)
    box_converted = _ffi.cast('TBox *', box)
    _lib.number_set_tbox(d_converted, basetype_converted, box_converted)
    _check_error()


def numset_set_tbox(s: 'const Set *', box: 'TBox *') -> None:
    s_converted = _ffi.cast('const Set *', s)
    box_converted = _ffi.cast('TBox *', box)
    _lib.numset_set_tbox(s_converted, box_converted)
    _check_error()


def numspan_set_tbox(span: 'const Span *', box: 'TBox *') -> None:
    span_converted = _ffi.cast('const Span *', span)
    box_converted = _ffi.cast('TBox *', box)
    _lib.numspan_set_tbox(span_converted, box_converted)
    _check_error()


def numspanset_set_tbox(ss: 'const SpanSet *', box: 'TBox *') -> None:
    ss_converted = _ffi.cast('const SpanSet *', ss)
    box_converted = _ffi.cast('TBox *', box)
    _lib.numspanset_set_tbox(ss_converted, box_converted)
    _check_error()


def period_set_stbox(p: 'const Span *', box: 'STBox *') -> None:
    p_converted = _ffi.cast('const Span *', p)
    box_converted = _ffi.cast('STBox *', box)
    _lib.period_set_stbox(p_converted, box_converted)
    _check_error()


def period_set_tbox(p: 'const Span *', box: 'TBox *') -> None:
    p_converted = _ffi.cast('const Span *', p)
    box_converted = _ffi.cast('TBox *', box)
    _lib.period_set_tbox(p_converted, box_converted)
    _check_error()


def periodset_set_stbox(ps: 'const SpanSet *', box: 'STBox *') -> None:
    ps_converted = _ffi.cast('const SpanSet *', ps)
    box_converted = _ffi.cast('STBox *', box)
    _lib.periodset_set_stbox(ps_converted, box_converted)
    _check_error()


def periodset_set_tbox(ps: 'const SpanSet *', box: 'TBox *') -> None:
    ps_converted = _ffi.cast('const SpanSet *', ps)
    box_converted = _ffi.cast('TBox *', box)
    _lib.periodset_set_tbox(ps_converted, box_converted)
    _check_error()


def stbox_set_box3d(box: 'const STBox *', box3d: 'BOX3D *') -> None:
    box_converted = _ffi.cast('const STBox *', box)
    box3d_converted = _ffi.cast('BOX3D *', box3d)
    _lib.stbox_set_box3d(box_converted, box3d_converted)
    _check_error()


def stbox_set_gbox(box: 'const STBox *', gbox: 'GBOX *') -> None:
    box_converted = _ffi.cast('const STBox *', box)
    gbox_converted = _ffi.cast('GBOX *', gbox)
    _lib.stbox_set_gbox(box_converted, gbox_converted)
    _check_error()


def timestamp_set_stbox(t: int, box: 'STBox *') -> None:
    t_converted = _ffi.cast('TimestampTz', t)
    box_converted = _ffi.cast('STBox *', box)
    _lib.timestamp_set_stbox(t_converted, box_converted)
    _check_error()


def timestamp_set_tbox(t: int, box: 'TBox *') -> None:
    t_converted = _ffi.cast('TimestampTz', t)
    box_converted = _ffi.cast('TBox *', box)
    _lib.timestamp_set_tbox(t_converted, box_converted)
    _check_error()


def timestampset_set_stbox(ts: 'const Set *', box: 'STBox *') -> None:
    ts_converted = _ffi.cast('const Set *', ts)
    box_converted = _ffi.cast('STBox *', box)
    _lib.timestampset_set_stbox(ts_converted, box_converted)
    _check_error()


def timestampset_set_tbox(ts: 'const Set *', box: 'TBox *') -> None:
    ts_converted = _ffi.cast('const Set *', ts)
    box_converted = _ffi.cast('TBox *', box)
    _lib.timestampset_set_tbox(ts_converted, box_converted)
    _check_error()


def tbox_shift_scale_value(box: 'const TBox *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'TBox *':
    box_converted = _ffi.cast('const TBox *', box)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.tbox_shift_scale_value(box_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_expand(box1: 'const STBox *', box2: 'STBox *') -> None:
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('STBox *', box2)
    _lib.stbox_expand(box1_converted, box2_converted)
    _check_error()


def tbox_expand(box1: 'const TBox *', box2: 'TBox *') -> None:
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('TBox *', box2)
    _lib.tbox_expand(box1_converted, box2_converted)
    _check_error()


def bbox_union_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    out_result = _ffi.new('Span *')
    _lib.bbox_union_span_span(s1_converted, s2_converted, out_result)
    _check_error()
    return out_result if out_result!= _ffi.NULL else None



def inter_stbox_stbox(box1: 'const STBox *', box2: 'const STBox *') -> 'STBox *':
    box1_converted = _ffi.cast('const STBox *', box1)
    box2_converted = _ffi.cast('const STBox *', box2)
    out_result = _ffi.new('STBox *')
    result = _lib.inter_stbox_stbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def inter_tbox_tbox(box1: 'const TBox *', box2: 'const TBox *') -> 'TBox *':
    box1_converted = _ffi.cast('const TBox *', box1)
    box2_converted = _ffi.cast('const TBox *', box2)
    out_result = _ffi.new('TBox *')
    result = _lib.inter_tbox_tbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def geoarr_as_text(geoarr: 'const Datum *', count: int, maxdd: int, extended: bool) -> 'char **':
    geoarr_converted = _ffi.cast('const Datum *', geoarr)
    result = _lib.geoarr_as_text(geoarr_converted, count, maxdd, extended)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_as_mfjson(inst: 'const TInstant *', with_bbox: bool) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tboolinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tboolinst_from_mfjson(mfjson: 'json_object *') -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tboolinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.tboolinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_as_mfjson(seq: 'const TSequence *', with_bbox: bool) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tboolseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tboolseq_from_mfjson(mfjson: 'json_object *') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tboolseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tboolseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_as_mfjson(ss: 'const TSequenceSet *', with_bbox: bool) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tboolseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tboolseqset_from_mfjson(mfjson: 'json_object *') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tboolseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.tboolseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_in(string: str, temptype: 'meosType') -> 'Temporal *':
    string_converted = string.encode('utf-8')
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.temporal_in(string_converted, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_out(temp: 'const Temporal *', maxdd: int) -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_values(temp: 'const Temporal *') -> "Tuple['Datum *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.temporal_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporalarr_out(temparr: 'const Temporal **', count: int, maxdd: int) -> 'char **':
    temparr_converted = [_ffi.cast('const Temporal *', x) for x in temparr]
    result = _lib.temporalarr_out(temparr_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_as_mfjson(inst: 'const TInstant *', with_bbox: bool, precision: int) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tfloatinst_as_mfjson(inst_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tfloatinst_from_mfjson(mfjson: 'json_object *') -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tfloatinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.tfloatinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_as_mfjson(seq: 'const TSequence *', with_bbox: bool, precision: int) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tfloatseq_as_mfjson(seq_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tfloatseq_from_mfjson(mfjson: 'json_object *', interp: 'interpType') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseq_from_mfjson(mfjson_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_as_mfjson(ss: 'const TSequenceSet *', with_bbox: bool, precision: int) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tfloatseqset_as_mfjson(ss_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tfloatseqset_from_mfjson(mfjson: 'json_object *', interp: 'interpType') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tfloatseqset_from_mfjson(mfjson_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.tfloatseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointinst_from_mfjson(mfjson: 'json_object *', srid: int) -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tgeogpointinst_from_mfjson(mfjson_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeogpointinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_mfjson(mfjson: 'json_object *', srid: int, interp: 'interpType') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseq_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_mfjson(mfjson: 'json_object *', srid: int, interp: 'interpType') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeogpointseqset_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeogpointseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_from_mfjson(mfjson: 'json_object *', srid: int) -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tgeompointinst_from_mfjson(mfjson_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeompointinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_from_mfjson(mfjson: 'json_object *', srid: int, interp: 'interpType') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseq_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_mfjson(mfjson: 'json_object *', srid: int, interp: 'interpType') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tgeompointseqset_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.tgeompointseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_as_mfjson(inst: 'const TInstant *', precision: int, with_bbox: bool, srs: str) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    srs_converted = srs.encode('utf-8')
    result = _lib.tinstant_as_mfjson(inst_converted, precision, with_bbox, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tinstant_from_mfjson(mfjson: 'json_object *', isgeo: bool, srid: int, temptype: 'meosType') -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.tinstant_from_mfjson(mfjson_converted, isgeo, srid, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_in(string: str, temptype: 'meosType') -> 'TInstant *':
    string_converted = string.encode('utf-8')
    temptype_converted = _ffi.cast('meosType', temptype)
    result = _lib.tinstant_in(string_converted, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_out(inst: 'const TInstant *', maxdd: int) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_out(inst_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tintinst_as_mfjson(inst: 'const TInstant *', with_bbox: bool) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tintinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tintinst_from_mfjson(mfjson: 'json_object *') -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tintinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.tintinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_as_mfjson(seq: 'const TSequence *', with_bbox: bool) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tintseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tintseq_from_mfjson(mfjson: 'json_object *') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tintseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tintseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_as_mfjson(ss: 'const TSequenceSet *', with_bbox: bool) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tintseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tintseqset_from_mfjson(mfjson: 'json_object *') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.tintseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.tintseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointarr_as_text(temparr: 'const Temporal **', count: int, maxdd: int, extended: bool) -> 'char **':
    temparr_converted = [_ffi.cast('const Temporal *', x) for x in temparr]
    result = _lib.tpointarr_as_text(temparr_converted, count, maxdd, extended)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_as_mfjson(inst: 'const TInstant *', with_bbox: bool, precision: int, srs: str) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    srs_converted = srs.encode('utf-8')
    result = _lib.tpointinst_as_mfjson(inst_converted, with_bbox, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpointseq_as_mfjson(seq: 'const TSequence *', with_bbox: bool, precision: int, srs: str) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    srs_converted = srs.encode('utf-8')
    result = _lib.tpointseq_as_mfjson(seq_converted, with_bbox, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tpointseqset_as_mfjson(ss: 'const TSequenceSet *', with_bbox: bool, precision: int, srs: str) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    srs_converted = srs.encode('utf-8')
    result = _lib.tpointseqset_as_mfjson(ss_converted, with_bbox, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tsequence_as_mfjson(seq: 'const TSequence *', precision: int, with_bbox: bool, srs: str) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    srs_converted = srs.encode('utf-8')
    result = _lib.tsequence_as_mfjson(seq_converted, precision, with_bbox, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tsequence_from_mfjson(mfjson: 'json_object *', isgeo: bool, srid: int, temptype: 'meosType', interp: 'interpType') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    temptype_converted = _ffi.cast('meosType', temptype)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_from_mfjson(mfjson_converted, isgeo, srid, temptype_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_in(string: str, temptype: 'meosType', interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    temptype_converted = _ffi.cast('meosType', temptype)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_in(string_converted, temptype_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_out(seq: 'const TSequence *', maxdd: int) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_out(seq_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tsequenceset_as_mfjson(ss: 'const TSequenceSet *', precision: int, with_bbox: bool, srs: str) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    srs_converted = srs.encode('utf-8')
    result = _lib.tsequenceset_as_mfjson(ss_converted, precision, with_bbox, srs_converted)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tsequenceset_from_mfjson(mfjson: 'json_object *', isgeo: bool, srid: int, temptype: 'meosType', interp: 'interpType') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    temptype_converted = _ffi.cast('meosType', temptype)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequenceset_from_mfjson(mfjson_converted, isgeo, srid, temptype_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_in(string: str, temptype: 'meosType', interp: 'interpType') -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    temptype_converted = _ffi.cast('meosType', temptype)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequenceset_in(string_converted, temptype_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_out(ss: 'const TSequenceSet *', maxdd: int) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttextinst_as_mfjson(inst: 'const TInstant *', with_bbox: bool) -> str:
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.ttextinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttextinst_from_mfjson(mfjson: 'json_object *') -> 'TInstant *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.ttextinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextinst_in(string: str) -> 'TInstant *':
    string_converted = string.encode('utf-8')
    result = _lib.ttextinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_as_mfjson(seq: 'const TSequence *', with_bbox: bool) -> str:
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.ttextseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttextseq_from_mfjson(mfjson: 'json_object *') -> 'TSequence *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.ttextseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_in(string: str, interp: 'interpType') -> 'TSequence *':
    string_converted = string.encode('utf-8')
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.ttextseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_as_mfjson(ss: 'const TSequenceSet *', with_bbox: bool) -> str:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.ttextseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def ttextseqset_from_mfjson(mfjson: 'json_object *') -> 'TSequenceSet *':
    mfjson_converted = _ffi.cast('json_object *', mfjson)
    result = _lib.ttextseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_in(string: str) -> 'TSequenceSet *':
    string_converted = string.encode('utf-8')
    result = _lib.ttextseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_base_temp(value: 'Datum', temptype: 'meosType', temp: 'const Temporal *') -> 'Temporal *':
    value_converted = _ffi.cast('Datum', value)
    temptype_converted = _ffi.cast('meosType', temptype)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_from_base_temp(value_converted, temptype_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_copy(inst: 'const TInstant *') -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_copy(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_make(value: 'Datum', temptype: 'meosType', t: int) -> 'TInstant *':
    value_converted = _ffi.cast('Datum', value)
    temptype_converted = _ffi.cast('meosType', temptype)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tinstant_make(value_converted, temptype_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_make_coords(xcoords: 'const double *', ycoords: 'const double *', zcoords: 'const double *', times: int, count: int, srid: int, geodetic: bool, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    xcoords_converted = _ffi.cast('const double *', xcoords)
    ycoords_converted = _ffi.cast('const double *', ycoords)
    zcoords_converted = _ffi.cast('const double *', zcoords)
    times_converted = _ffi.cast('const TimestampTz *', times)
    srid_converted = _ffi.cast('int32', srid)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tpointseq_make_coords(xcoords_converted, ycoords_converted, zcoords_converted, times_converted, count, srid_converted, geodetic, lower_inc, upper_inc, interp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_from_base_timestampset(value: 'Datum', temptype: 'meosType', ss: 'const Set *') -> 'TSequence *':
    value_converted = _ffi.cast('Datum', value)
    temptype_converted = _ffi.cast('meosType', temptype)
    ss_converted = _ffi.cast('const Set *', ss)
    result = _lib.tsequence_from_base_timestampset(value_converted, temptype_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make_exp(instants: 'const TInstant **', count: int, maxcount: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make_exp(instants_converted, count, maxcount, lower_inc, upper_inc, interp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_compact(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_compact(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restart(seq: 'TSequence *', last: int) -> None:
    seq_converted = _ffi.cast('TSequence *', seq)
    _lib.tsequence_restart(seq_converted, last)
    _check_error()


def tsequence_subseq(seq: 'const TSequence *', from_: int, to: int, lower_inc: bool, upper_inc: bool) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_subseq(seq_converted, from_, to, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_copy(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_copy(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_from_base_period(value: 'Datum', temptype: 'meosType', p: 'const Span *', interp: 'interpType') -> 'TSequence *':
    value_converted = _ffi.cast('Datum', value)
    temptype_converted = _ffi.cast('meosType', temptype)
    p_converted = _ffi.cast('const Span *', p)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_from_base_period(value_converted, temptype_converted, p_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make_free(instants: 'TInstant **', count: int, lower_inc: bool, upper_inc: bool, interp: 'interpType', normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('TInstant *', x) for x in instants]
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_make_free(instants_converted, count, lower_inc, upper_inc, interp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_exp(sequences: 'const TSequence **', count: int, maxcount: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make_exp(sequences_converted, count, maxcount, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_compact(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_free(sequences: 'TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make_free(sequences_converted, count, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restart(ss: 'TSequenceSet *', last: int) -> None:
    ss_converted = _ffi.cast('TSequenceSet *', ss)
    _lib.tsequenceset_restart(ss_converted, last)
    _check_error()


def tsequenceset_copy(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_copy(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tseqsetarr_to_tseqset(seqsets: 'TSequenceSet **', count: int, totalseqs: int) -> 'TSequenceSet *':
    seqsets_converted = [_ffi.cast('TSequenceSet *', x) for x in seqsets]
    result = _lib.tseqsetarr_to_tseqset(seqsets_converted, count, totalseqs)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_from_base_periodset(value: 'Datum', temptype: 'meosType', ps: 'const SpanSet *', interp: 'interpType') -> 'TSequenceSet *':
    value_converted = _ffi.cast('Datum', value)
    temptype_converted = _ffi.cast('meosType', temptype)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequenceset_from_base_periodset(value_converted, temptype_converted, ps_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_set_period(temp: 'const Temporal *', p: 'Span *') -> None:
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('Span *', p)
    _lib.temporal_set_period(temp_converted, p_converted)
    _check_error()


def tinstant_set_period(inst: 'const TInstant *', p: 'Span *') -> None:
    inst_converted = _ffi.cast('const TInstant *', inst)
    p_converted = _ffi.cast('Span *', p)
    _lib.tinstant_set_period(inst_converted, p_converted)
    _check_error()


def tsequence_set_period(seq: 'const TSequence *', p: 'Span *') -> None:
    seq_converted = _ffi.cast('const TSequence *', seq)
    p_converted = _ffi.cast('Span *', p)
    _lib.tsequence_set_period(seq_converted, p_converted)
    _check_error()


def tsequenceset_set_period(ss: 'const TSequenceSet *', p: 'Span *') -> None:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    p_converted = _ffi.cast('Span *', p)
    _lib.tsequenceset_set_period(ss_converted, p_converted)
    _check_error()


def temporal_end_value(temp: 'const Temporal *') -> 'Datum':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_max_value(temp: 'const Temporal *') -> 'Datum':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_mem_size(temp: 'const Temporal *') -> 'size_t':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_mem_size(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_min_value(temp: 'const Temporal *') -> 'Datum':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_set_bbox(temp: 'const Temporal *', box: 'void *') -> None:
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('void *', box)
    _lib.temporal_set_bbox(temp_converted, box_converted)
    _check_error()


def tfloatseq_derivative(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tfloatseq_derivative(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_derivative(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tfloatseqset_derivative(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_set_span(temp: 'const Temporal *', span: 'Span *') -> None:
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('Span *', span)
    _lib.tnumber_set_span(temp_converted, span_converted)
    _check_error()


def temporal_start_value(temp: 'const Temporal *') -> 'Datum':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_abs(inst: 'const TInstant *') -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tnumberinst_abs(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_abs(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_abs(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_abs(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_abs(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_angular_difference(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_angular_difference(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_angular_difference(ss: 'const TSequenceSet *') -> 'TSequence *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_angular_difference(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_delta_value(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_delta_value(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_delta_value(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_delta_value(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_valuespans(inst: 'const TInstant *') -> 'SpanSet *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tnumberinst_valuespans(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_valuespans(seq: 'const TSequence *') -> 'SpanSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_valuespans(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_valuespans(ss: 'const TSequenceSet *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_valuespans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_hash(inst: 'const TInstant *') -> 'uint32':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_hash(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_instants(inst: 'const TInstant *') -> "Tuple['const TInstant **', 'int']":
    inst_converted = _ffi.cast('const TInstant *', inst)
    count = _ffi.new('int *')
    result = _lib.tinstant_instants(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_set_bbox(inst: 'const TInstant *', box: 'void *') -> None:
    inst_converted = _ffi.cast('const TInstant *', inst)
    box_converted = _ffi.cast('void *', box)
    _lib.tinstant_set_bbox(inst_converted, box_converted)
    _check_error()


def tinstant_time(inst: 'const TInstant *') -> 'SpanSet *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_time(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_timestamps(inst: 'const TInstant *') -> "Tuple['TimestampTz *', 'int']":
    inst_converted = _ffi.cast('const TInstant *', inst)
    count = _ffi.new('int *')
    result = _lib.tinstant_timestamps(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_value(inst: 'const TInstant *') -> 'Datum':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_value(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_value_at_timestamp(inst: 'const TInstant *', t: int) -> 'Datum *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('Datum *')
    result = _lib.tinstant_value_at_timestamp(inst_converted, t_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tinstant_value_copy(inst: 'const TInstant *') -> 'Datum':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tinstant_value_copy(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_values(inst: 'const TInstant *') -> "Tuple['Datum *', 'int']":
    inst_converted = _ffi.cast('const TInstant *', inst)
    count = _ffi.new('int *')
    result = _lib.tinstant_values(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_duration(seq: 'const TSequence *') -> 'Interval *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_duration(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_end_timestamp(seq: 'const TSequence *') -> 'TimestampTz':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_end_timestamp(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_hash(seq: 'const TSequence *') -> 'uint32':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_hash(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_instants(seq: 'const TSequence *') -> 'const TInstant **':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_instants(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_max_instant(seq: 'const TSequence *') -> 'const TInstant *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_max_instant(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_max_value(seq: 'const TSequence *') -> 'Datum':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_max_value(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_min_instant(seq: 'const TSequence *') -> 'const TInstant *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_min_instant(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_min_value(seq: 'const TSequence *') -> 'Datum':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_min_value(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_segments(seq: 'const TSequence *') -> "Tuple['TSequence **', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tsequence_segments(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_sequences(seq: 'const TSequence *') -> "Tuple['TSequence **', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tsequence_sequences(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_set_bbox(seq: 'const TSequence *', box: 'void *') -> None:
    seq_converted = _ffi.cast('const TSequence *', seq)
    box_converted = _ffi.cast('void *', box)
    _lib.tsequence_set_bbox(seq_converted, box_converted)
    _check_error()


def tsequence_expand_bbox(seq: 'TSequence *', inst: 'const TInstant *') -> None:
    seq_converted = _ffi.cast('TSequence *', seq)
    inst_converted = _ffi.cast('const TInstant *', inst)
    _lib.tsequence_expand_bbox(seq_converted, inst_converted)
    _check_error()


def tsequenceset_expand_bbox(ss: 'TSequenceSet *', seq: 'const TSequence *') -> None:
    ss_converted = _ffi.cast('TSequenceSet *', ss)
    seq_converted = _ffi.cast('const TSequence *', seq)
    _lib.tsequenceset_expand_bbox(ss_converted, seq_converted)
    _check_error()


def tsequence_start_timestamp(seq: 'const TSequence *') -> 'TimestampTz':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_start_timestamp(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_time(seq: 'const TSequence *') -> 'SpanSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_time(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_timestamps(seq: 'const TSequence *') -> "Tuple['TimestampTz *', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tsequence_timestamps(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_value_at_timestamp(seq: 'const TSequence *', t: int, strict: bool) -> 'Datum *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('Datum *')
    result = _lib.tsequence_value_at_timestamp(seq_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tsequence_values(seq: 'const TSequence *') -> "Tuple['Datum *', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tsequence_values(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_duration(ss: 'const TSequenceSet *', boundspan: bool) -> 'Interval *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_duration(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_end_timestamp(ss: 'const TSequenceSet *') -> 'TimestampTz':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_end_timestamp(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_hash(ss: 'const TSequenceSet *') -> 'uint32':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_hash(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_inst_n(ss: 'const TSequenceSet *', n: int) -> 'const TInstant *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_inst_n(ss_converted, n)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_instants(ss: 'const TSequenceSet *') -> 'const TInstant **':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_instants(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_max_instant(ss: 'const TSequenceSet *') -> 'const TInstant *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_max_instant(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_max_value(ss: 'const TSequenceSet *') -> 'Datum':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_max_value(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_min_instant(ss: 'const TSequenceSet *') -> 'const TInstant *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_min_instant(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_min_value(ss: 'const TSequenceSet *') -> 'Datum':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_min_value(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_num_instants(ss: 'const TSequenceSet *') -> 'int':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_num_instants(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_num_timestamps(ss: 'const TSequenceSet *') -> 'int':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_num_timestamps(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_segments(ss: 'const TSequenceSet *') -> "Tuple['TSequence **', 'int']":
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    count = _ffi.new('int *')
    result = _lib.tsequenceset_segments(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_sequences(ss: 'const TSequenceSet *') -> 'TSequence **':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_sequences(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_sequences_p(ss: 'const TSequenceSet *') -> 'const TSequence **':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_sequences_p(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_set_bbox(ss: 'const TSequenceSet *', box: 'void *') -> None:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    box_converted = _ffi.cast('void *', box)
    _lib.tsequenceset_set_bbox(ss_converted, box_converted)
    _check_error()


def tsequenceset_start_timestamp(ss: 'const TSequenceSet *') -> 'TimestampTz':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_start_timestamp(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_time(ss: 'const TSequenceSet *') -> 'SpanSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_time(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_timespan(ss: 'const TSequenceSet *') -> 'Interval *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_timespan(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_timestamp_n(ss: 'const TSequenceSet *', n: int) -> int:
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tsequenceset_timestamp_n(ss_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tsequenceset_timestamps(ss: 'const TSequenceSet *') -> "Tuple['TimestampTz *', 'int']":
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    count = _ffi.new('int *')
    result = _lib.tsequenceset_timestamps(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_value_at_timestamp(ss: 'const TSequenceSet *', t: int, strict: bool) -> 'Datum *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('Datum *')
    result = _lib.tsequenceset_value_at_timestamp(ss_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tsequenceset_values(ss: 'const TSequenceSet *') -> "Tuple['Datum *', 'int']":
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    count = _ffi.new('int *')
    result = _lib.tsequenceset_values(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_merge(inst1: 'const TInstant *', inst2: 'const TInstant *') -> 'Temporal *':
    inst1_converted = _ffi.cast('const TInstant *', inst1)
    inst2_converted = _ffi.cast('const TInstant *', inst2)
    result = _lib.tinstant_merge(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_merge_array(instants: 'const TInstant **', count: int) -> 'Temporal *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    result = _lib.tinstant_merge_array(instants_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_shift_time(inst: 'const TInstant *', interval: 'const Interval *') -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.tinstant_shift_time(inst_converted, interval_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_to_tsequence(inst: 'const TInstant *', interp: 'interpType') -> 'TSequence *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tinstant_to_tsequence(inst_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_to_tsequenceset(inst: 'const TInstant *', interp: 'interpType') -> 'TSequenceSet *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tinstant_to_tsequenceset(inst_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_shift_scale_value(temp: 'const Temporal *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.tnumber_shift_scale_value(temp_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tnuminst_shift_value(inst: 'const TInstant *', shift: 'Datum') -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    shift_converted = _ffi.cast('Datum', shift)
    result = _lib.tnuminst_shift_value(inst_converted, shift_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_shift_scale_value(seq: 'const TSequence *', shift: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    shift_converted = _ffi.cast('Datum', shift)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.tnumberseq_shift_scale_value(seq_converted, shift_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_append_tinstant(seq: 'TSequence *', inst: 'const TInstant *', maxdist: float, maxt: 'const Interval *', expand: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('TSequence *', seq)
    inst_converted = _ffi.cast('const TInstant *', inst)
    maxt_converted = _ffi.cast('const Interval *', maxt)
    result = _lib.tsequence_append_tinstant(seq_converted, inst_converted, maxdist, maxt_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_append_tsequence(seq1: 'TSequence *', seq2: 'const TSequence *', expand: bool) -> 'Temporal *':
    seq1_converted = _ffi.cast('TSequence *', seq1)
    seq2_converted = _ffi.cast('const TSequence *', seq2)
    result = _lib.tsequence_append_tsequence(seq1_converted, seq2_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_merge(seq1: 'const TSequence *', seq2: 'const TSequence *') -> 'Temporal *':
    seq1_converted = _ffi.cast('const TSequence *', seq1)
    seq2_converted = _ffi.cast('const TSequence *', seq2)
    result = _lib.tsequence_merge(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_merge_array(sequences: 'const TSequence **', count: int) -> 'Temporal *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequence_merge_array(sequences_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_set_interp(seq: 'const TSequence *', interp: 'interpType') -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_set_interp(seq_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_shift_scale_time(seq: 'const TSequence *', shift: 'const Interval *', duration: 'const Interval *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration)
    result = _lib.tsequence_shift_scale_time(seq_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tinstant(seq: 'const TSequence *') -> 'TInstant *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_to_tinstant(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tdiscseq(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_to_tdiscseq(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tcontseq(seq: 'const TSequence *', interp: 'interpType') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_to_tcontseq(seq_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tsequenceset(seq: 'const TSequence *') -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_to_tsequenceset(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tsequenceset_interp(seq: 'const TSequence *', interp: 'interpType') -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequence_to_tsequenceset_interp(seq_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_append_tinstant(ss: 'TSequenceSet *', inst: 'const TInstant *', maxdist: float, maxt: 'const Interval *', expand: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('TSequenceSet *', ss)
    inst_converted = _ffi.cast('const TInstant *', inst)
    maxt_converted = _ffi.cast('const Interval *', maxt)
    result = _lib.tsequenceset_append_tinstant(ss_converted, inst_converted, maxdist, maxt_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_append_tsequence(ss: 'TSequenceSet *', seq: 'const TSequence *', expand: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('TSequenceSet *', ss)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequenceset_append_tsequence(ss_converted, seq_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_merge(ss1: 'const TSequenceSet *', ss2: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss1_converted = _ffi.cast('const TSequenceSet *', ss1)
    ss2_converted = _ffi.cast('const TSequenceSet *', ss2)
    result = _lib.tsequenceset_merge(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_merge_array(seqsets: 'const TSequenceSet **', count: int) -> 'TSequenceSet *':
    seqsets_converted = [_ffi.cast('const TSequenceSet *', x) for x in seqsets]
    result = _lib.tsequenceset_merge_array(seqsets_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_set_interp(ss: 'const TSequenceSet *', interp: 'interpType') -> 'Temporal *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    interp_converted = _ffi.cast('interpType', interp)
    result = _lib.tsequenceset_set_interp(ss_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_shift_scale_value(ss: 'const TSequenceSet *', start: 'Datum', width: 'Datum', hasshift: bool, haswidth: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    start_converted = _ffi.cast('Datum', start)
    width_converted = _ffi.cast('Datum', width)
    result = _lib.tnumberseqset_shift_scale_value(ss_converted, start_converted, width_converted, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_shift_scale_time(ss: 'const TSequenceSet *', start: 'const Interval *', duration: 'const Interval *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    start_converted = _ffi.cast('const Interval *', start)
    duration_converted = _ffi.cast('const Interval *', duration)
    result = _lib.tsequenceset_shift_scale_time(ss_converted, start_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_tinstant(ss: 'const TSequenceSet *') -> 'TInstant *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_to_tinstant(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_discrete(ss: 'const TSequenceSet *') -> 'TSequence *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_to_discrete(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_step(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_to_step(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_linear(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_to_linear(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_tsequence(ss: 'const TSequenceSet *') -> 'TSequence *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_to_tsequence(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_bbox_restrict_set(temp: 'const Temporal *', set: 'const Set *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.temporal_bbox_restrict_set(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_minmax(temp: 'const Temporal *', min: bool, atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_restrict_minmax(temp_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_period(temp: 'const Temporal *', p: 'const Span *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.temporal_restrict_period(temp_converted, p_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_periodset(temp: 'const Temporal *', ps: 'const SpanSet *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.temporal_restrict_periodset(temp_converted, ps_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_timestamp(temp: 'const Temporal *', t: int, atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_restrict_timestamp(temp_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_timestampset(temp: 'const Temporal *', ts: 'const Set *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.temporal_restrict_timestampset(temp_converted, ts_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_value(temp: 'const Temporal *', value: 'Datum', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_restrict_value(temp_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_values(temp: 'const Temporal *', set: 'const Set *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.temporal_restrict_values(temp_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'Datum *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('Datum *')
    result = _lib.temporal_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tinstant_restrict_period(inst: 'const TInstant *', period: 'const Span *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tinstant_restrict_period(inst_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_periodset(inst: 'const TInstant *', ps: 'const SpanSet *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tinstant_restrict_periodset(inst_converted, ps_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_timestamp(inst: 'const TInstant *', t: int, atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tinstant_restrict_timestamp(inst_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_timestampset(inst: 'const TInstant *', ts: 'const Set *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tinstant_restrict_timestampset(inst_converted, ts_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_value(inst: 'const TInstant *', value: 'Datum', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_restrict_value(inst_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_values(inst: 'const TInstant *', set: 'const Set *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.tinstant_restrict_values(inst_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_restrict_span(temp: 'const Temporal *', span: 'const Span *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_restrict_span(temp_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_restrict_spanset(temp: 'const Temporal *', ss: 'const SpanSet *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumber_restrict_spanset(temp_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_restrict_span(inst: 'const TInstant *', span: 'const Span *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumberinst_restrict_span(inst_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_restrict_spanset(inst: 'const TInstant *', ss: 'const SpanSet *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    ss_converted = _ffi.cast('const SpanSet *', ss)
    result = _lib.tnumberinst_restrict_spanset(inst_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_restrict_span(ss: 'const TSequenceSet *', span: 'const Span *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumberseqset_restrict_span(ss_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_restrict_spanset(ss: 'const TSequenceSet *', spanset: 'const SpanSet *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    spanset_converted = _ffi.cast('const SpanSet *', spanset)
    result = _lib.tnumberseqset_restrict_spanset(ss_converted, spanset_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_restrict_geom_time(temp: 'const Temporal *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *', atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpoint_restrict_geom_time(temp_converted, gs_converted, zspan_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_restrict_stbox(temp: 'const Temporal *', box: 'const STBox *', border_inc: bool, atfunc: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpoint_restrict_stbox(temp_converted, box_converted, border_inc, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_restrict_geom_time(inst: 'const TInstant *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *', atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpointinst_restrict_geom_time(inst_converted, gs_converted, zspan_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_restrict_stbox(inst: 'const TInstant *', box: 'const STBox *', border_inc: bool, atfunc: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpointinst_restrict_stbox(inst_converted, box_converted, border_inc, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_restrict_geom_time(seq: 'const TSequence *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *', atfunc: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpointseq_restrict_geom_time(seq_converted, gs_converted, zspan_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_restrict_stbox(seq: 'const TSequence *', box: 'const STBox *', border_inc: bool, atfunc: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpointseq_restrict_stbox(seq_converted, box_converted, border_inc, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_restrict_geom_time(ss: 'const TSequenceSet *', gs: 'const GSERIALIZED *', zspan: 'const Span *', period: 'const Span *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    zspan_converted = _ffi.cast('const Span *', zspan)
    period_converted = _ffi.cast('const Span *', period)
    result = _lib.tpointseqset_restrict_geom_time(ss_converted, gs_converted, zspan_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_restrict_stbox(ss: 'const TSequenceSet *', box: 'const STBox *', border_inc: bool, atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    box_converted = _ffi.cast('const STBox *', box)
    result = _lib.tpointseqset_restrict_stbox(ss_converted, box_converted, border_inc, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_at_period(seq: 'const TSequence *', p: 'const Span *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequence_at_period(seq_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_at_timestamp(seq: 'const TSequence *', t: int) -> 'TInstant *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tsequence_at_timestamp(seq_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_minmax(seq: 'const TSequence *', min: bool, atfunc: bool) -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_restrict_minmax(seq_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_period(seq: 'const TSequence *', p: 'const Span *', atfunc: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequence_restrict_period(seq_converted, p_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_periodset(seq: 'const TSequence *', ps: 'const SpanSet *', atfunc: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tsequence_restrict_periodset(seq_converted, ps_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_timestamp(seq: 'const TSequence *', t: int, atfunc: bool) -> 'TInstant *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tsequence_restrict_timestamp(seq_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_timestampset(seq: 'const TSequence *', ts: 'const Set *', atfunc: bool) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tsequence_restrict_timestampset(seq_converted, ts_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_value(seq: 'const TSequence *', value: 'Datum', atfunc: bool) -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_restrict_value(seq_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_values(seq: 'const TSequence *', set: 'const Set *', atfunc: bool) -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.tsequence_restrict_values(seq_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_minmax(ss: 'const TSequenceSet *', min: bool, atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_restrict_minmax(ss_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_period(ss: 'const TSequenceSet *', p: 'const Span *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequenceset_restrict_period(ss_converted, p_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_periodset(ss: 'const TSequenceSet *', ps: 'const SpanSet *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tsequenceset_restrict_periodset(ss_converted, ps_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_timestamp(ss: 'const TSequenceSet *', t: int, atfunc: bool) -> 'Temporal *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tsequenceset_restrict_timestamp(ss_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_timestampset(ss: 'const TSequenceSet *', ts: 'const Set *', atfunc: bool) -> 'Temporal *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tsequenceset_restrict_timestampset(ss_converted, ts_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_value(ss: 'const TSequenceSet *', value: 'Datum', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_restrict_value(ss_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_values(ss: 'const TSequenceSet *', set: 'const Set *', atfunc: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    set_converted = _ffi.cast('const Set *', set)
    result = _lib.tsequenceset_restrict_values(ss_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_derivative(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_derivative(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_derivative(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_derivative(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tnumber_number(temp: 'const Temporal *', value: 'Datum', valuetype: 'meosType', restype: 'meosType') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    valuetype_converted = _ffi.cast('meosType', valuetype)
    restype_converted = _ffi.cast('meosType', restype)
    result = _lib.distance_tnumber_number(temp_converted, value_converted, valuetype_converted, restype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tnumber_number(temp: 'const Temporal *', value: 'Datum', basetype: 'meosType') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    basetype_converted = _ffi.cast('meosType', basetype)
    result = _lib.nad_tnumber_number(temp_converted, value_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_always_eq(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_always_eq(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_always_le(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_always_le(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_always_lt(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_always_lt(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ever_eq(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_ever_eq(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ever_le(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_ever_le(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ever_lt(temp: 'const Temporal *', value: 'Datum') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.temporal_ever_lt(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_always_eq(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_always_eq(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_always_le(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_always_le(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_always_lt(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_always_lt(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_ever_eq(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_ever_eq(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_ever_le(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_ever_le(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_ever_lt(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tinstant_ever_lt(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_always_eq(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointinst_always_eq(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_ever_eq(inst: 'const TInstant *', value: 'Datum') -> 'bool':
    inst_converted = _ffi.cast('const TInstant *', inst)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointinst_ever_eq(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_always_eq(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointseq_always_eq(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_ever_eq(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointseq_ever_eq(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_always_eq(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointseqset_always_eq(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_ever_eq(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tpointseqset_ever_eq(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_always_eq(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_always_eq(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_always_le(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_always_le(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_always_lt(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_always_lt(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_ever_eq(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_ever_eq(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_ever_le(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_ever_le(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_ever_lt(seq: 'const TSequence *', value: 'Datum') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequence_ever_lt(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_always_eq(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_always_eq(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_always_le(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_always_le(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_always_lt(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_always_lt(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_ever_eq(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_ever_eq(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_ever_le(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_ever_le(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_ever_lt(ss: 'const TSequenceSet *', value: 'Datum') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    value_converted = _ffi.cast('Datum', value)
    result = _lib.tsequenceset_ever_lt(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_cmp(inst1: 'const TInstant *', inst2: 'const TInstant *') -> 'int':
    inst1_converted = _ffi.cast('const TInstant *', inst1)
    inst2_converted = _ffi.cast('const TInstant *', inst2)
    result = _lib.tinstant_cmp(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_eq(inst1: 'const TInstant *', inst2: 'const TInstant *') -> 'bool':
    inst1_converted = _ffi.cast('const TInstant *', inst1)
    inst2_converted = _ffi.cast('const TInstant *', inst2)
    result = _lib.tinstant_eq(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_cmp(seq1: 'const TSequence *', seq2: 'const TSequence *') -> 'int':
    seq1_converted = _ffi.cast('const TSequence *', seq1)
    seq2_converted = _ffi.cast('const TSequence *', seq2)
    result = _lib.tsequence_cmp(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_eq(seq1: 'const TSequence *', seq2: 'const TSequence *') -> 'bool':
    seq1_converted = _ffi.cast('const TSequence *', seq1)
    seq2_converted = _ffi.cast('const TSequence *', seq2)
    result = _lib.tsequence_eq(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_cmp(ss1: 'const TSequenceSet *', ss2: 'const TSequenceSet *') -> 'int':
    ss1_converted = _ffi.cast('const TSequenceSet *', ss1)
    ss2_converted = _ffi.cast('const TSequenceSet *', ss2)
    result = _lib.tsequenceset_cmp(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_eq(ss1: 'const TSequenceSet *', ss2: 'const TSequenceSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TSequenceSet *', ss1)
    ss2_converted = _ffi.cast('const TSequenceSet *', ss2)
    result = _lib.tsequenceset_eq(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_srid(inst: 'const TInstant *') -> 'int':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tpointinst_srid(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_trajectory(seq: 'const TSequence *') -> 'GSERIALIZED *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_trajectory(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_azimuth(seq: 'const TSequence *') -> 'TSequenceSet *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_azimuth(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_cumulative_length(seq: 'const TSequence *', prevlength: float) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_cumulative_length(seq_converted, prevlength)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_is_simple(seq: 'const TSequence *') -> 'bool':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_is_simple(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_length(seq: 'const TSequence *') -> 'double':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_length(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_speed(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_speed(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_srid(seq: 'const TSequence *') -> 'int':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_srid(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_stboxes(seq: 'const TSequence *') -> "Tuple['STBox *', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tpointseq_stboxes(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_azimuth(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_azimuth(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_cumulative_length(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_cumulative_length(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_is_simple(ss: 'const TSequenceSet *') -> 'bool':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_is_simple(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_length(ss: 'const TSequenceSet *') -> 'double':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_length(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_speed(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_speed(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_srid(ss: 'const TSequenceSet *') -> 'int':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_srid(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_stboxes(ss: 'const TSequenceSet *') -> "Tuple['STBox *', 'int']":
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    count = _ffi.new('int *')
    result = _lib.tpointseqset_stboxes(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_trajectory(ss: 'const TSequenceSet *') -> 'GSERIALIZED *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_trajectory(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_coord(temp: 'const Temporal *', coord: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_get_coord(temp_converted, coord)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_tgeogpointinst(inst: 'const TInstant *', oper: bool) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.tgeompointinst_tgeogpointinst(inst_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_tgeogpointseq(seq: 'const TSequence *', oper: bool) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tgeompointseq_tgeogpointseq(seq_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_tgeogpointseqset(ss: 'const TSequenceSet *', oper: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tgeompointseqset_tgeogpointseqset(ss_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_tgeogpoint(temp: 'const Temporal *', oper: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeompoint_tgeogpoint(temp_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_set_srid(inst: 'const TInstant *', srid: int) -> 'TInstant *':
    inst_converted = _ffi.cast('const TInstant *', inst)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.tpointinst_set_srid(inst_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_make_simple(seq: 'const TSequence *') -> "Tuple['TSequence **', 'int']":
    seq_converted = _ffi.cast('const TSequence *', seq)
    count = _ffi.new('int *')
    result = _lib.tpointseq_make_simple(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseq_set_srid(seq: 'const TSequence *', srid: int) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.tpointseq_set_srid(seq_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_make_simple(ss: 'const TSequenceSet *') -> "Tuple['TSequence **', 'int']":
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    count = _ffi.new('int *')
    result = _lib.tpointseqset_make_simple(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_set_srid(ss: 'const TSequenceSet *', srid: int) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.tpointseqset_set_srid(ss_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_insert(seq1: 'const TSequence *', seq2: 'const TSequence *', connect: bool) -> 'Temporal *':
    seq1_converted = _ffi.cast('const TSequence *', seq1)
    seq2_converted = _ffi.cast('const TSequence *', seq2)
    result = _lib.tsequence_insert(seq1_converted, seq2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_insert(ss1: 'const TSequenceSet *', ss2: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss1_converted = _ffi.cast('const TSequenceSet *', ss1)
    ss2_converted = _ffi.cast('const TSequenceSet *', ss2)
    result = _lib.tsequenceset_insert(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_timestamp(seq: 'const TSequence *', t: int, connect: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tsequence_delete_timestamp(seq_converted, t_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_timestampset(seq: 'const TSequence *', ts: 'const Set *', connect: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tsequence_delete_timestampset(seq_converted, ts_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_period(seq: 'const TSequence *', p: 'const Span *', connect: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequence_delete_period(seq_converted, p_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_periodset(seq: 'const TSequence *', ps: 'const SpanSet *', connect: bool) -> 'Temporal *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tsequence_delete_periodset(seq_converted, ps_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_timestamp(ss: 'const TSequenceSet *', t: int) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tsequenceset_delete_timestamp(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_timestampset(ss: 'const TSequenceSet *', ts: 'const Set *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    ts_converted = _ffi.cast('const Set *', ts)
    result = _lib.tsequenceset_delete_timestampset(ss_converted, ts_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_period(ss: 'const TSequenceSet *', p: 'const Span *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    p_converted = _ffi.cast('const Span *', p)
    result = _lib.tsequenceset_delete_period(ss_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_periodset(ss: 'const TSequenceSet *', ps: 'const SpanSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    ps_converted = _ffi.cast('const SpanSet *', ps)
    result = _lib.tsequenceset_delete_periodset(ss_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_integral(seq: 'const TSequence *') -> 'double':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_integral(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_twavg(seq: 'const TSequence *') -> 'double':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tnumberseq_twavg(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_integral(ss: 'const TSequenceSet *') -> 'double':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_integral(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_twavg(ss: 'const TSequenceSet *') -> 'double':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tnumberseqset_twavg(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_twcentroid(seq: 'const TSequence *') -> 'GSERIALIZED *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tpointseq_twcentroid(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_twcentroid(ss: 'const TSequenceSet *') -> 'GSERIALIZED *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tpointseqset_twcentroid(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_compact(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_compact(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_compact(seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tsequence_compact(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_compact(ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tsequenceset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_value_split(temp: 'const Temporal *', size: 'Datum', origin: 'Datum', buckets: 'Datum **') -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    size_converted = _ffi.cast('Datum', size)
    origin_converted = _ffi.cast('Datum', origin)
    buckets_converted = [_ffi.cast('Datum *', x) for x in buckets]
    count = _ffi.new('int *')
    result = _lib.tnumber_value_split(temp_converted, size_converted, origin_converted, buckets_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


