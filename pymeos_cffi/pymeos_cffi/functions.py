from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List

import _meos_cffi
import shapely.geometry as spg
from dateutil.parser import parse
from postgis import Point

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


def create_pointer(object: 'Any', type: str) -> 'Any *':
    return _ffi.new(f'{type} *', object)


def datetime_to_timestamptz(dt: datetime) -> int:
    return _lib.pg_timestamptz_in(dt.strftime('%Y-%m-%d %H:%M:%S%z').encode('utf-8'), -1)


def timestamptz_to_datetime(ts: int) -> datetime:
    return parse(pg_timestamptz_out(ts))


def timedelta_to_interval(td: timedelta) -> Any:
    return _ffi.new('Interval *', {'time': td.microseconds + td.seconds * 1000000, 'day': td.days, 'month': 0})


def interval_to_timedelta(interval: Any) -> timedelta:
    # TODO fix for months/years
    return timedelta(days=interval.day, microseconds=interval.time)


def lwpoint_to_point(lwpoint: Any) -> Point:
    return Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint),
                 lwpoint_get_z(lwpoint) if lwgeom_has_z(lwpoint) else None,
                 lwpoint_get_m(lwpoint) if lwgeom_has_m(lwpoint) else None,
                 lwgeom_get_srid(lwpoint))


def lwpoint_to_shapely_point(lwpoint: Any) -> spg.Point:
    return spg.Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint),lwpoint_get_z(lwpoint)) if lwgeom_has_z(lwpoint) \
        else spg.Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint))


def text2cstring(textptr: 'text *') -> str:
    result = _lib.text2cstring(textptr)
    result = _ffi.string(result).decode('utf-8')
    return result


def cstring2text(cstring: str) -> 'text *':
    cstring_converted = cstring.encode('utf-8')
    result = _lib.cstring2text(cstring_converted)
    return result


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


def lwgeom_as_lwpoint(lwgeom: 'const LWGEOM *') -> 'LWPOINT *':
    lwgeom_converted = _ffi.cast('const LWGEOM *', lwgeom)
    result = _lib.lwgeom_as_lwpoint(lwgeom_converted)
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


def meos_initialize() -> None:
    _lib.meos_initialize()


def meos_finish() -> None:
    _lib.meos_finish()


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


def gserialized_as_hexwkb(geom: 'const GSERIALIZED *', type: str) -> str:
    geom_converted = _ffi.cast('const GSERIALIZED *', geom)
    type_converted = type.encode('utf-8')
    result = _lib.gserialized_as_hexwkb(geom_converted, type_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def gserialized_from_ewkb(bytea_wkb: 'const bytea *', srid: int) -> 'GSERIALIZED *':
    bytea_wkb_converted = _ffi.cast('const bytea *', bytea_wkb)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.gserialized_from_ewkb(bytea_wkb_converted, srid_converted)
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


def pg_timestamptz_in(string: str, typmod: int) -> 'TimestampTz':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamptz_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_timestamp_in(string: str, typmod: int) -> 'Timestamp':
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamp_in(string_converted, typmod_converted)
    return result if result != _ffi.NULL else None


def pg_timestamptz_out(dt: int) -> str:
    dt_converted = _ffi.cast('TimestampTz', dt)
    result = _lib.pg_timestamptz_out(dt_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def pg_timestamp_out(dt: int) -> str:
    dt_converted = _ffi.cast('Timestamp', dt)
    result = _lib.pg_timestamp_out(dt_converted)
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


def intspan_in(string: str) -> 'Span *':
    string_converted = string.encode('utf-8')
    result = _lib.intspan_in(string_converted)
    return result if result != _ffi.NULL else None


def intspan_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.intspan_out(s_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def period_in(string: str) -> 'Period *':
    string_converted = string.encode('utf-8')
    result = _lib.period_in(string_converted)
    return result if result != _ffi.NULL else None


def period_out(s: 'const Span *') -> str:
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_out(s_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def periodset_as_hexwkb(ps: 'const PeriodSet *', variant: int) -> "Tuple[str, 'size_t *']":
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.periodset_as_hexwkb(ps_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out


def periodset_as_wkb(ps: 'const PeriodSet *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.periodset_as_wkb(ps_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def periodset_from_hexwkb(hexwkb: str) -> 'PeriodSet *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.periodset_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def periodset_from_wkb(wkb: 'uint8_t *', size: int) -> 'PeriodSet *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
    result = _lib.periodset_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def periodset_in(string: str) -> 'PeriodSet *':
    string_converted = string.encode('utf-8')
    result = _lib.periodset_in(string_converted)
    return result if result != _ffi.NULL else None


def periodset_out(ps: 'const PeriodSet *') -> str:
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_out(ps_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def span_as_hexwkb(s: 'const Span *', variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_hexwkb(s_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out


def span_as_wkb(s: 'const Span *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    s_converted = _ffi.cast('const Span *', s)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.span_as_wkb(s_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def span_from_hexwkb(hexwkb: str) -> 'Span *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.span_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def span_from_wkb(wkb: 'uint8_t *', size: int) -> 'Span *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
    result = _lib.span_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def span_out(s: 'const Span *', arg: 'Datum') -> str:
    s_converted = _ffi.cast('const Span *', s)
    arg_converted = _ffi.cast('Datum', arg)
    result = _lib.span_out(s_converted, arg_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def timestampset_as_hexwkb(ts: 'const TimestampSet *', variant: int) -> "Tuple[str, 'size_t *']":
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.timestampset_as_hexwkb(ts_converted, variant_converted, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None, size_out


def timestampset_as_wkb(ts: 'const TimestampSet *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.timestampset_as_wkb(ts_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def timestampset_from_hexwkb(hexwkb: str) -> 'TimestampSet *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.timestampset_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def timestampset_from_wkb(wkb: 'uint8_t *', size: int) -> 'TimestampSet *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
    result = _lib.timestampset_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def timestampset_in(string: str) -> 'TimestampSet *':
    string_converted = string.encode('utf-8')
    result = _lib.timestampset_in(string_converted)
    return result if result != _ffi.NULL else None


def timestampset_out(ts: 'const TimestampSet *') -> str:
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.timestampset_out(ts_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def floatspan_make(lower: float, upper: float, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.floatspan_make(lower, upper, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def intspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Span *':
    result = _lib.intspan_make(lower, upper, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def period_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> 'Period *':
    lower_converted = _ffi.cast('TimestampTz', lower)
    upper_converted = _ffi.cast('TimestampTz', upper)
    result = _lib.period_make(lower_converted, upper_converted, lower_inc, upper_inc)
    return result if result != _ffi.NULL else None


def periodset_copy(ps: 'const PeriodSet *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_copy(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_make(periods: 'const Period **', count: int, normalize: bool) -> 'PeriodSet *':
    periods_converted = [_ffi.cast('const Period *', x) for x in periods]
    result = _lib.periodset_make(periods_converted, count, normalize)
    return result if result != _ffi.NULL else None


def periodset_make_free(periods: 'Period **', count: int, normalize: bool) -> 'PeriodSet *':
    periods_converted = [_ffi.cast('Period *', x) for x in periods]
    result = _lib.periodset_make_free(periods_converted, count, normalize)
    return result if result != _ffi.NULL else None


def span_copy(s: 'const Span *') -> 'Span *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_copy(s_converted)
    return result if result != _ffi.NULL else None


def timestampset_copy(ts: 'const TimestampSet *') -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.timestampset_copy(ts_converted)
    return result if result != _ffi.NULL else None


def timestampset_make(times: List[int], count: int) -> 'TimestampSet *':
    times_converted = [_ffi.cast('const TimestampTz', x) for x in times]
    result = _lib.timestampset_make(times_converted, count)
    return result if result != _ffi.NULL else None


def timestampset_make_free(times: int, count: int) -> 'TimestampSet *':
    times_converted = _ffi.cast('TimestampTz *', times)
    result = _lib.timestampset_make_free(times_converted, count)
    return result if result != _ffi.NULL else None


def float_to_floaspan(d: float) -> 'Span *':
    result = _lib.float_to_floaspan(d)
    return result if result != _ffi.NULL else None


def int_to_intspan(i: int) -> 'Span *':
    result = _lib.int_to_intspan(i)
    return result if result != _ffi.NULL else None


def period_to_periodset(period: 'const Period *') -> 'PeriodSet *':
    period_converted = _ffi.cast('const Period *', period)
    result = _lib.period_to_periodset(period_converted)
    return result if result != _ffi.NULL else None


def periodset_to_period(ps: 'const PeriodSet *') -> 'Period *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_to_period(ps_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_period(t: int) -> 'Period *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_period(t_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_periodset(t: int) -> 'PeriodSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_periodset(t_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_timestampset(t: int) -> 'TimestampSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_timestampset(t_converted)
    return result if result != _ffi.NULL else None


def timestampset_to_periodset(ts: 'const TimestampSet *') -> 'PeriodSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.timestampset_to_periodset(ts_converted)
    return result if result != _ffi.NULL else None


def floatspan_lower(s: 'Span *') -> 'double':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.floatspan_lower(s_converted)
    return result if result != _ffi.NULL else None


def floatspan_upper(s: 'Span *') -> 'double':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.floatspan_upper(s_converted)
    return result if result != _ffi.NULL else None


def intspan_lower(s: 'Span *') -> 'int':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.intspan_lower(s_converted)
    return result if result != _ffi.NULL else None


def intspan_upper(s: 'Span *') -> 'int':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.intspan_upper(s_converted)
    return result if result != _ffi.NULL else None


def period_duration(s: 'const Span *') -> 'Interval *':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.period_duration(s_converted)
    return result if result != _ffi.NULL else None


def period_lower(p: 'Period *') -> 'TimestampTz':
    p_converted = _ffi.cast('Period *', p)
    result = _lib.period_lower(p_converted)
    return result if result != _ffi.NULL else None


def period_upper(p: 'Period *') -> 'TimestampTz':
    p_converted = _ffi.cast('Period *', p)
    result = _lib.period_upper(p_converted)
    return result if result != _ffi.NULL else None


def periodset_duration(ps: 'const PeriodSet *') -> 'Interval *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_duration(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_end_period(ps: 'const PeriodSet *') -> 'Period *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_end_period(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_end_timestamp(ps: 'const PeriodSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_end_timestamp(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_hash(ps: 'const PeriodSet *') -> 'uint32':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_hash(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_hash_extended(ps: 'const PeriodSet *', seed: int) -> 'uint64':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.periodset_hash_extended(ps_converted, seed_converted)
    return result if result != _ffi.NULL else None


def periodset_mem_size(ps: 'const PeriodSet *') -> 'int':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_mem_size(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_num_periods(ps: 'const PeriodSet *') -> 'int':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_num_periods(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_num_timestamps(ps: 'const PeriodSet *') -> 'int':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_num_timestamps(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_period_n(ps: 'const PeriodSet *', i: int) -> 'Period *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_period_n(ps_converted, i)
    return result if result != _ffi.NULL else None


def periodset_periods(ps: 'const PeriodSet *') -> "Tuple['const Period **', 'int']":
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    count = _ffi.new('int *')
    result = _lib.periodset_periods(ps_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def periodset_start_period(ps: 'const PeriodSet *') -> 'Period *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_start_period(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_start_timestamp(ps: 'const PeriodSet *') -> 'TimestampTz':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_start_timestamp(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_timespan(ps: 'const PeriodSet *') -> 'Interval *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_timespan(ps_converted)
    return result if result != _ffi.NULL else None


def periodset_timestamp_n(ps: 'const PeriodSet *', n: int) -> int:
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.periodset_timestamp_n(ps_converted, n, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def periodset_timestamps(ps: 'const PeriodSet *') -> "Tuple['TimestampTz *', 'int']":
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    count = _ffi.new('int *')
    result = _lib.periodset_timestamps(ps_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def span_hash(s: 'const Span *') -> 'uint32':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_hash(s_converted)
    return result if result != _ffi.NULL else None


def span_hash_extended(s: 'const Span *', seed: int) -> 'uint64':
    s_converted = _ffi.cast('const Span *', s)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.span_hash_extended(s_converted, seed_converted)
    return result if result != _ffi.NULL else None


def span_lower_inc(s: 'Span *') -> 'bool':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.span_lower_inc(s_converted)
    return result if result != _ffi.NULL else None


def span_upper_inc(s: 'Span *') -> 'bool':
    s_converted = _ffi.cast('Span *', s)
    result = _lib.span_upper_inc(s_converted)
    return result if result != _ffi.NULL else None


def span_width(s: 'const Span *') -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.span_width(s_converted)
    return result if result != _ffi.NULL else None


def timestampset_end_timestamp(ss: 'const TimestampSet *') -> 'TimestampTz':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_end_timestamp(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_hash(ss: 'const TimestampSet *') -> 'uint32':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_hash(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_hash_extended(ss: 'const TimestampSet *', seed: int) -> 'uint64':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.timestampset_hash_extended(ss_converted, seed_converted)
    return result if result != _ffi.NULL else None


def timestampset_mem_size(ss: 'const TimestampSet *') -> 'int':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_mem_size(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_num_timestamps(ss: 'const TimestampSet *') -> 'int':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_num_timestamps(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_start_timestamp(ss: 'const TimestampSet *') -> 'TimestampTz':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_start_timestamp(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_timespan(ss: 'const TimestampSet *') -> 'Interval *':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_timespan(ss_converted)
    return result if result != _ffi.NULL else None


def timestampset_timestamp_n(ss: 'const TimestampSet *', n: int) -> int:
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.timestampset_timestamp_n(ss_converted, n, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def timestampset_timestamps(ss: 'const TimestampSet *') -> 'TimestampTz *':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_timestamps(ss_converted)
    return result if result != _ffi.NULL else None


def periodset_shift_tscale(ps: 'const PeriodSet *', start: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    start_converted = _ffi.cast('const Interval *', start) if start else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration else _ffi.NULL
    result = _lib.periodset_shift_tscale(ps_converted, start_converted, duration_converted)
    return result if result != _ffi.NULL else None


def span_expand(s1: 'const Span *', s2: 'Span *') -> None:
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('Span *', s2)
    _lib.span_expand(s1_converted, s2_converted)


def lower_upper_shift_tscale(shift: 'const Interval *', duration: 'const Interval *', lower: int, upper: int) -> None:
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration)
    lower_converted = _ffi.cast('TimestampTz *', lower)
    upper_converted = _ffi.cast('TimestampTz *', upper)
    _lib.lower_upper_shift_tscale(shift_converted, duration_converted, lower_converted, upper_converted)


def period_shift_tscale(start: "Optional['const Interval *']", duration: "Optional['const Interval *']", result: "Optional['Period *']") -> 'Period *':
    start_converted = _ffi.cast('const Interval *', start) if start else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration else _ffi.NULL
    out_result = _ffi.cast('Period *', result)
    _lib.period_shift_tscale(start_converted, duration_converted, out_result)
    return out_result if out_result!= _ffi.NULL else None



def timestampset_shift_tscale(ss: 'const TimestampSet *', start: "Optional['const Interval *']", duration: "Optional['const Interval *']") -> 'TimestampSet *':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    start_converted = _ffi.cast('const Interval *', start) if start else _ffi.NULL
    duration_converted = _ffi.cast('const Interval *', duration) if duration else _ffi.NULL
    result = _lib.timestampset_shift_tscale(ss_converted, start_converted, duration_converted)
    return result if result != _ffi.NULL else None


def adjacent_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def adjacent_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.adjacent_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def adjacent_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.adjacent_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def adjacent_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def adjacent_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.adjacent_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.adjacent_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.adjacent_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.adjacent_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def adjacent_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.adjacent_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def adjacent_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.adjacent_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def adjacent_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.adjacent_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def adjacent_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.adjacent_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def adjacent_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.adjacent_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contained_float_floatspan(d: float, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_float_floatspan(d, s_converted)
    return result if result != _ffi.NULL else None


def contained_int_intspan(i: int, s: 'const Span *') -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contained_int_intspan(i, s_converted)
    return result if result != _ffi.NULL else None


def contained_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contained_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contained_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contained_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def contained_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.contained_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def contained_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contained_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contained_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contained_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def contained_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contained_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contained_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.contained_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contained_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contained_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def contained_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contained_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contained_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.contained_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def contains_floatspan_float(s: 'const Span *', d: float) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def contains_intspan_int(s: 'const Span *', i: int) -> 'bool':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.contains_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def contains_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contains_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contains_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.contains_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contains_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.contains_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.contains_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contains_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.contains_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def contains_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.contains_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def overlaps_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overlaps_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overlaps_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overlaps_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overlaps_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overlaps_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def overlaps_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.overlaps_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def overlaps_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overlaps_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overlaps_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overlaps_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overlaps_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overlaps_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def overlaps_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overlaps_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overlaps_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.overlaps_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def after_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.after_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def after_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def after_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.after_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def after_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.after_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def after_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.after_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def after_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def after_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.after_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def after_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.after_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def after_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.after_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def after_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.after_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def after_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.after_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def after_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.after_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def after_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def after_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.after_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def before_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.before_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def before_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def before_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.before_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def before_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.before_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def before_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.before_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def before_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def before_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.before_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def before_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.before_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def before_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.before_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def before_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.before_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def before_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.before_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def before_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.before_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def before_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def before_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.before_timestampset_timestampset(ts1_converted, ts2_converted)
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


def left_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.left_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def overafter_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overafter_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overafter_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overafter_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overafter_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.overafter_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overafter_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overafter_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overafter_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overafter_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overafter_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overafter_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def overafter_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overafter_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overafter_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.overafter_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def overbefore_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overbefore_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overbefore_period_timestamp(p: 'const Period *', t: int) -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overbefore_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overbefore_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.overbefore_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overbefore_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_period(t: int, p: 'const Period *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overbefore_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overbefore_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overbefore_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overbefore_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overbefore_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'bool':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.overbefore_timestampset_timestampset(ts1_converted, ts2_converted)
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


def overleft_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overleft_span_span(s1_converted, s2_converted)
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


def overright_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.overright_span_span(s1_converted, s2_converted)
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


def right_span_span(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.right_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def intersection_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.intersection_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def intersection_period_timestamp(p: 'const Period *', t: int) -> int:
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_period_timestamp(p_converted, t_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_period_timestampset(ps: 'const Period *', ts: 'const TimestampSet *') -> 'TimestampSet *':
    ps_converted = _ffi.cast('const Period *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.intersection_period_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def intersection_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.intersection_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def intersection_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'PeriodSet *':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.intersection_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def intersection_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> int:
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_periodset_timestamp(ps_converted, t_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'TimestampSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.intersection_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def intersection_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.intersection_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def intersection_timestamp_period(t: int, p: 'const Period *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestamp_period(t_converted, p_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestamp_periodset(t_converted, ps_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_timestamp_timestamp(t1: int, t2: int) -> int:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestamp_timestamp(t1_converted, t2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestamp_timestampset(t_converted, ts_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.intersection_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def intersection_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.intersection_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def intersection_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> int:
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('const TimestampTz', t)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.intersection_timestampset_timestamp(ts_converted, t_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'TimestampSet *':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.intersection_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def minus_period_period(p1: 'const Period *', p2: 'const Period *') -> 'PeriodSet *':
    p1_converted = _ffi.cast('const Period *', p1)
    p2_converted = _ffi.cast('const Period *', p2)
    result = _lib.minus_period_period(p1_converted, p2_converted)
    return result if result != _ffi.NULL else None


def minus_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.minus_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def minus_period_timestamp(p: 'const Period *', t: int) -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def minus_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.minus_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def minus_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.minus_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def minus_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'PeriodSet *':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.minus_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def minus_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def minus_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.minus_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def minus_span_span(s1: 'const Span *', s2: 'const Span *') -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.minus_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def minus_timestamp_period(t: int, p: 'const Period *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_period(t_converted, p_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_periodset(t_converted, ps_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestamp_timestamp(t1: int, t2: int) -> int:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_timestamp(t1_converted, t2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> int:
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.minus_timestamp_timestampset(t_converted, ts_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def minus_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.minus_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def minus_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.minus_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def minus_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.minus_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def minus_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'TimestampSet *':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.minus_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def union_period_period(p1: 'const Period *', p2: 'const Period *') -> 'PeriodSet *':
    p1_converted = _ffi.cast('const Period *', p1)
    p2_converted = _ffi.cast('const Period *', p2)
    result = _lib.union_period_period(p1_converted, p2_converted)
    return result if result != _ffi.NULL else None


def union_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.union_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def union_period_timestamp(p: 'const Period *', t: int) -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'PeriodSet *':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.union_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def union_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.union_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def union_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'PeriodSet *':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.union_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def union_periodset_timestamp(ps: 'PeriodSet *', t: int) -> 'PeriodSet *':
    ps_converted = _ffi.cast('PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.union_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_periodset_timestampset(ps: 'PeriodSet *', ts: 'TimestampSet *') -> 'PeriodSet *':
    ps_converted = _ffi.cast('PeriodSet *', ps)
    ts_converted = _ffi.cast('TimestampSet *', ts)
    result = _lib.union_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def union_span_span(s1: 'const Span *', s2: 'const Span *', strict: bool) -> 'Span *':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.union_span_span(s1_converted, s2_converted, strict)
    return result if result != _ffi.NULL else None


def union_timestamp_period(t: int, p: 'const Period *') -> 'PeriodSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.union_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def union_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'PeriodSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.union_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def union_timestamp_timestamp(t1: int, t2: int) -> 'TimestampSet *':
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    result = _lib.union_timestamp_timestamp(t1_converted, t2_converted)
    return result if result != _ffi.NULL else None


def union_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'TimestampSet *':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.union_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def union_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'PeriodSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.union_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def union_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'PeriodSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.union_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def union_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'TimestampSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('const TimestampTz', t)
    result = _lib.union_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def union_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'TimestampSet *':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.union_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def distance_floatspan_float(s: 'const Span *', d: float) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_floatspan_float(s_converted, d)
    return result if result != _ffi.NULL else None


def distance_intspan_int(s: 'const Span *', i: int) -> 'double':
    s_converted = _ffi.cast('const Span *', s)
    result = _lib.distance_intspan_int(s_converted, i)
    return result if result != _ffi.NULL else None


def distance_period_periodset(p: 'const Period *', ps: 'const PeriodSet *') -> 'double':
    p_converted = _ffi.cast('const Period *', p)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.distance_period_periodset(p_converted, ps_converted)
    return result if result != _ffi.NULL else None


def distance_period_timestamp(p: 'const Period *', t: int) -> 'double':
    p_converted = _ffi.cast('const Period *', p)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_period_timestamp(p_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_period_timestampset(p: 'const Period *', ts: 'const TimestampSet *') -> 'double':
    p_converted = _ffi.cast('const Period *', p)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.distance_period_timestampset(p_converted, ts_converted)
    return result if result != _ffi.NULL else None


def distance_periodset_period(ps: 'const PeriodSet *', p: 'const Period *') -> 'double':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.distance_periodset_period(ps_converted, p_converted)
    return result if result != _ffi.NULL else None


def distance_periodset_periodset(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'double':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.distance_periodset_periodset(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def distance_periodset_timestamp(ps: 'const PeriodSet *', t: int) -> 'double':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_periodset_timestamp(ps_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_periodset_timestampset(ps: 'const PeriodSet *', ts: 'const TimestampSet *') -> 'double':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.distance_periodset_timestampset(ps_converted, ts_converted)
    return result if result != _ffi.NULL else None


def distance_span_span(s1: 'const Span *', s2: 'const Span *') -> 'double':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.distance_span_span(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def distance_timestamp_period(t: int, p: 'const Period *') -> 'double':
    t_converted = _ffi.cast('TimestampTz', t)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.distance_timestamp_period(t_converted, p_converted)
    return result if result != _ffi.NULL else None


def distance_timestamp_periodset(t: int, ps: 'const PeriodSet *') -> 'double':
    t_converted = _ffi.cast('TimestampTz', t)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.distance_timestamp_periodset(t_converted, ps_converted)
    return result if result != _ffi.NULL else None


def distance_timestamp_timestamp(t1: int, t2: int) -> 'double':
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    result = _lib.distance_timestamp_timestamp(t1_converted, t2_converted)
    return result if result != _ffi.NULL else None


def distance_timestamp_timestampset(t: int, ts: 'const TimestampSet *') -> 'double':
    t_converted = _ffi.cast('TimestampTz', t)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.distance_timestamp_timestampset(t_converted, ts_converted)
    return result if result != _ffi.NULL else None


def distance_timestampset_period(ts: 'const TimestampSet *', p: 'const Period *') -> 'double':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.distance_timestampset_period(ts_converted, p_converted)
    return result if result != _ffi.NULL else None


def distance_timestampset_periodset(ts: 'const TimestampSet *', ps: 'const PeriodSet *') -> 'double':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.distance_timestampset_periodset(ts_converted, ps_converted)
    return result if result != _ffi.NULL else None


def distance_timestampset_timestamp(ts: 'const TimestampSet *', t: int) -> 'double':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.distance_timestampset_timestamp(ts_converted, t_converted)
    return result if result != _ffi.NULL else None


def distance_timestampset_timestampset(ts1: 'const TimestampSet *', ts2: 'const TimestampSet *') -> 'double':
    ts1_converted = _ffi.cast('const TimestampSet *', ts1)
    ts2_converted = _ffi.cast('const TimestampSet *', ts2)
    result = _lib.distance_timestampset_timestampset(ts1_converted, ts2_converted)
    return result if result != _ffi.NULL else None


def periodset_eq(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_eq(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_ne(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_ne(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_cmp(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'int':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_cmp(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_lt(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_lt(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_le(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_le(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_ge(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_ge(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def periodset_gt(ps1: 'const PeriodSet *', ps2: 'const PeriodSet *') -> 'bool':
    ps1_converted = _ffi.cast('const PeriodSet *', ps1)
    ps2_converted = _ffi.cast('const PeriodSet *', ps2)
    result = _lib.periodset_gt(ps1_converted, ps2_converted)
    return result if result != _ffi.NULL else None


def span_eq(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_eq(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_ne(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_ne(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_cmp(s1: 'const Span *', s2: 'const Span *') -> 'int':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_cmp(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_lt(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_lt(s1_converted, s2_converted)
    return result if result != _ffi.NULL else None


def span_le(s1: 'const Span *', s2: 'const Span *') -> 'bool':
    s1_converted = _ffi.cast('const Span *', s1)
    s2_converted = _ffi.cast('const Span *', s2)
    result = _lib.span_le(s1_converted, s2_converted)
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


def timestampset_eq(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_eq(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_ne(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_ne(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_cmp(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'int':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_cmp(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_lt(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_lt(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_le(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_le(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_ge(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_ge(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def timestampset_gt(ss1: 'const TimestampSet *', ss2: 'const TimestampSet *') -> 'bool':
    ss1_converted = _ffi.cast('const TimestampSet *', ss1)
    ss2_converted = _ffi.cast('const TimestampSet *', ss2)
    result = _lib.timestampset_gt(ss1_converted, ss2_converted)
    return result if result != _ffi.NULL else None


def tbox_in(string: str) -> 'TBOX *':
    string_converted = string.encode('utf-8')
    result = _lib.tbox_in(string_converted)
    return result if result != _ffi.NULL else None


def tbox_out(box: 'const TBOX *', maxdd: int) -> str:
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_out(box_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbox_from_wkb(wkb: 'uint8_t *', size: int) -> 'TBOX *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
    result = _lib.tbox_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def tbox_from_hexwkb(hexwkb: str) -> 'TBOX *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.tbox_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def stbox_from_wkb(wkb: 'uint8_t *', size: int) -> 'STBOX *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
    result = _lib.stbox_from_wkb(wkb_converted, size)
    return result if result != _ffi.NULL else None


def stbox_from_hexwkb(hexwkb: str) -> 'STBOX *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.stbox_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def tbox_as_wkb(box: 'const TBOX *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    box_converted = _ffi.cast('const TBOX *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.tbox_as_wkb(box_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def tbox_as_hexwkb(box: 'const TBOX *', variant: int, size: 'size_t *') -> str:
    box_converted = _ffi.cast('const TBOX *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_converted = _ffi.cast('size_t *', size)
    result = _lib.tbox_as_hexwkb(box_converted, variant_converted, size_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def stbox_as_wkb(box: 'const STBOX *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    box_converted = _ffi.cast('const STBOX *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.stbox_as_wkb(box_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def stbox_as_hexwkb(box: 'const STBOX *', variant: int, size: 'size_t *') -> str:
    box_converted = _ffi.cast('const STBOX *', box)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_converted = _ffi.cast('size_t *', size)
    result = _lib.stbox_as_hexwkb(box_converted, variant_converted, size_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def stbox_in(string: str) -> 'STBOX *':
    string_converted = string.encode('utf-8')
    result = _lib.stbox_in(string_converted)
    return result if result != _ffi.NULL else None


def stbox_out(box: 'const STBOX *', maxdd: int) -> str:
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_out(box_converted, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def tbox_make(p: "Optional['const Period *']", s: "Optional['const Span *']") -> 'TBOX *':
    p_converted = _ffi.cast('const Period *', p) if p else _ffi.NULL
    s_converted = _ffi.cast('const Span *', s) if s else _ffi.NULL
    result = _lib.tbox_make(p_converted, s_converted)
    return result if result != _ffi.NULL else None


def tbox_set(p: 'const Period *', s: 'const Span *', box: 'TBOX *') -> None:
    p_converted = _ffi.cast('const Period *', p)
    s_converted = _ffi.cast('const Span *', s)
    box_converted = _ffi.cast('TBOX *', box)
    _lib.tbox_set(p_converted, s_converted, box_converted)


def tbox_copy(box: 'const TBOX *') -> 'TBOX *':
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_copy(box_converted)
    return result if result != _ffi.NULL else None


def stbox_make(p: "Optional['const Period *']", hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float) -> 'STBOX *':
    p_converted = _ffi.cast('const Period *', p) if p else _ffi.NULL
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.stbox_make(p_converted, hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax)
    return result if result != _ffi.NULL else None


def stbox_set(p: 'const Period *', hasx: bool, hasz: bool, geodetic: bool, srid: int, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, box: 'STBOX *') -> None:
    p_converted = _ffi.cast('const Period *', p)
    srid_converted = _ffi.cast('int32', srid)
    box_converted = _ffi.cast('STBOX *', box)
    _lib.stbox_set(p_converted, hasx, hasz, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, box_converted)


def stbox_copy(box: 'const STBOX *') -> 'STBOX *':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_copy(box_converted)
    return result if result != _ffi.NULL else None


def int_to_tbox(i: int) -> 'TBOX *':
    result = _lib.int_to_tbox(i)
    return result if result != _ffi.NULL else None


def float_to_tbox(d: float) -> 'TBOX *':
    result = _lib.float_to_tbox(d)
    return result if result != _ffi.NULL else None


def span_to_tbox(span: 'const Span *') -> 'TBOX *':
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.span_to_tbox(span_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_tbox(t: int) -> 'TBOX *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_tbox(t_converted)
    return result if result != _ffi.NULL else None


def timestampset_to_tbox(ss: 'const TimestampSet *') -> 'TBOX *':
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.timestampset_to_tbox(ss_converted)
    return result if result != _ffi.NULL else None


def period_to_tbox(p: 'const Period *') -> 'TBOX *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.period_to_tbox(p_converted)
    return result if result != _ffi.NULL else None


def periodset_to_tbox(ps: 'const PeriodSet *') -> 'TBOX *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_to_tbox(ps_converted)
    return result if result != _ffi.NULL else None


def int_timestamp_to_tbox(i: int, t: int) -> 'TBOX *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.int_timestamp_to_tbox(i, t_converted)
    return result if result != _ffi.NULL else None


def float_timestamp_to_tbox(d: float, t: int) -> 'TBOX *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.float_timestamp_to_tbox(d, t_converted)
    return result if result != _ffi.NULL else None


def int_period_to_tbox(i: int, p: 'const Period *') -> 'TBOX *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.int_period_to_tbox(i, p_converted)
    return result if result != _ffi.NULL else None


def float_period_to_tbox(d: float, p: 'const Period *') -> 'TBOX *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.float_period_to_tbox(d, p_converted)
    return result if result != _ffi.NULL else None


def span_timestamp_to_tbox(span: 'const Span *', t: int) -> 'TBOX *':
    span_converted = _ffi.cast('const Span *', span)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.span_timestamp_to_tbox(span_converted, t_converted)
    return result if result != _ffi.NULL else None


def span_period_to_tbox(span: 'const Span *', p: 'const Period *') -> 'TBOX *':
    span_converted = _ffi.cast('const Span *', span)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.span_period_to_tbox(span_converted, p_converted)
    return result if result != _ffi.NULL else None


def tbox_to_floatspan(box: 'const TBOX *') -> 'Span *':
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_to_floatspan(box_converted)
    return result if result != _ffi.NULL else None


def tbox_to_period(box: 'const TBOX *') -> 'Period *':
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_to_period(box_converted)
    return result if result != _ffi.NULL else None


def stbox_to_period(box: 'const STBOX *') -> 'Period *':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_to_period(box_converted)
    return result if result != _ffi.NULL else None


def tnumber_to_tbox(temp: 'const Temporal *') -> 'TBOX *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_to_tbox(temp_converted)
    return result if result != _ffi.NULL else None


def stbox_to_geo(box: 'const STBOX *') -> 'GSERIALIZED *':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_to_geo(box_converted)
    return result if result != _ffi.NULL else None


def tpoint_to_stbox(temp: 'const Temporal *') -> 'STBOX *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_to_stbox(temp_converted)
    return result if result != _ffi.NULL else None


def geo_to_stbox(gs: 'const GSERIALIZED *') -> 'STBOX *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_to_stbox(gs_converted)
    return result if result != _ffi.NULL else None


def timestamp_to_stbox(t: int) -> 'STBOX *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.timestamp_to_stbox(t_converted)
    return result if result != _ffi.NULL else None


def timestampset_to_stbox(ts: 'const TimestampSet *') -> 'STBOX *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.timestampset_to_stbox(ts_converted)
    return result if result != _ffi.NULL else None


def period_to_stbox(p: 'const Period *') -> 'STBOX *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.period_to_stbox(p_converted)
    return result if result != _ffi.NULL else None


def periodset_to_stbox(ps: 'const PeriodSet *') -> 'STBOX *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.periodset_to_stbox(ps_converted)
    return result if result != _ffi.NULL else None


def geo_timestamp_to_stbox(gs: 'const GSERIALIZED *', t: int) -> 'STBOX *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.geo_timestamp_to_stbox(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


def geo_period_to_stbox(gs: 'const GSERIALIZED *', p: 'const Period *') -> 'STBOX *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.geo_period_to_stbox(gs_converted, p_converted)
    return result if result != _ffi.NULL else None


def tbox_hasx(box: 'const TBOX *') -> 'bool':
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_hasx(box_converted)
    return result if result != _ffi.NULL else None


def tbox_hast(box: 'const TBOX *') -> 'bool':
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tbox_hast(box_converted)
    return result if result != _ffi.NULL else None


def tbox_xmin(box: 'const TBOX *') -> 'double':
    box_converted = _ffi.cast('const TBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_xmax(box: 'const TBOX *') -> 'double':
    box_converted = _ffi.cast('const TBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.tbox_xmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_tmin(box: 'const TBOX *') -> int:
    box_converted = _ffi.cast('const TBOX *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmin(box_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def tbox_tmax(box: 'const TBOX *') -> int:
    box_converted = _ffi.cast('const TBOX *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.tbox_tmax(box_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_hasx(box: 'const STBOX *') -> 'bool':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_hasx(box_converted)
    return result if result != _ffi.NULL else None


def stbox_hasz(box: 'const STBOX *') -> 'bool':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_hasz(box_converted)
    return result if result != _ffi.NULL else None


def stbox_hast(box: 'const STBOX *') -> 'bool':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_hast(box_converted)
    return result if result != _ffi.NULL else None


def stbox_isgeodetic(box: 'const STBOX *') -> 'bool':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_isgeodetic(box_converted)
    return result if result != _ffi.NULL else None


def stbox_xmin(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_xmax(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_xmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_ymin(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_ymax(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_ymax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_zmin(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmin(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_zmax(box: 'const STBOX *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('double *')
    result = _lib.stbox_zmax(box_converted, out_result)
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_tmin(box: 'const STBOX *') -> int:
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmin(box_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_tmax(box: 'const STBOX *') -> int:
    box_converted = _ffi.cast('const STBOX *', box)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.stbox_tmax(box_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def stbox_get_srid(box: 'const STBOX *') -> 'int32':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_get_srid(box_converted)
    return result if result != _ffi.NULL else None


def tbox_expand(box1: 'const TBOX *', box2: 'TBOX *') -> None:
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('TBOX *', box2)
    _lib.tbox_expand(box1_converted, box2_converted)


def tbox_shift_tscale(start: 'const Interval *', duration: 'const Interval *', box: 'TBOX *') -> None:
    start_converted = _ffi.cast('const Interval *', start)
    duration_converted = _ffi.cast('const Interval *', duration)
    box_converted = _ffi.cast('TBOX *', box)
    _lib.tbox_shift_tscale(start_converted, duration_converted, box_converted)


def tbox_expand_value(box: 'const TBOX *', d: 'const double') -> 'TBOX *':
    box_converted = _ffi.cast('const TBOX *', box)
    d_converted = _ffi.cast('const double', d)
    result = _lib.tbox_expand_value(box_converted, d_converted)
    return result if result != _ffi.NULL else None


def tbox_expand_temporal(box: 'const TBOX *', interval: 'const Interval *') -> 'TBOX *':
    box_converted = _ffi.cast('const TBOX *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.tbox_expand_temporal(box_converted, interval_converted)
    return result if result != _ffi.NULL else None


def stbox_expand(box1: 'const STBOX *', box2: 'STBOX *') -> None:
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('STBOX *', box2)
    _lib.stbox_expand(box1_converted, box2_converted)


def stbox_shift_tscale(start: 'const Interval *', duration: 'const Interval *', box: 'STBOX *') -> None:
    start_converted = _ffi.cast('const Interval *', start)
    duration_converted = _ffi.cast('const Interval *', duration)
    box_converted = _ffi.cast('STBOX *', box)
    _lib.stbox_shift_tscale(start_converted, duration_converted, box_converted)


def stbox_set_srid(box: 'const STBOX *', srid: int) -> 'STBOX *':
    box_converted = _ffi.cast('const STBOX *', box)
    srid_converted = _ffi.cast('int32', srid)
    result = _lib.stbox_set_srid(box_converted, srid_converted)
    return result if result != _ffi.NULL else None


def stbox_expand_spatial(box: 'const STBOX *', d: float) -> 'STBOX *':
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.stbox_expand_spatial(box_converted, d)
    return result if result != _ffi.NULL else None


def stbox_expand_temporal(box: 'const STBOX *', interval: 'const Interval *') -> 'STBOX *':
    box_converted = _ffi.cast('const STBOX *', box)
    interval_converted = _ffi.cast('const Interval *', interval)
    result = _lib.stbox_expand_temporal(box_converted, interval_converted)
    return result if result != _ffi.NULL else None


def contains_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.contains_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contained_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.contained_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overlaps_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.overlaps_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def same_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.same_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def adjacent_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.adjacent_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contains_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.contains_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def contained_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.contained_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overlaps_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overlaps_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def same_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.same_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def adjacent_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.adjacent_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def left_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.left_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overleft_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.overleft_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def right_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.right_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overright_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.overright_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def before_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.before_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbefore_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.overbefore_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def after_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.after_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overafter_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.overafter_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def left_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.left_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overleft_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overleft_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def right_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.right_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overright_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overright_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def below_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.below_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbelow_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overbelow_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def above_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.above_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overabove_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overabove_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def front_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.front_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overfront_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overfront_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def back_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.back_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overback_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overback_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def before_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.before_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overbefore_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overbefore_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def after_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.after_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def overafter_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.overafter_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def union_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'TBOX *':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.union_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def inter_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'TBOX *':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    out_result = _ffi.new('TBOX *')
    result = _lib.inter_tbox_tbox(box1_converted, box2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'TBOX *':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.intersection_tbox_tbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def union_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *', strict: bool) -> 'STBOX *':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.union_stbox_stbox(box1_converted, box2_converted, strict)
    return result if result != _ffi.NULL else None


def inter_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'STBOX *':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    out_result = _ffi.new('STBOX *')
    result = _lib.inter_stbox_stbox(box1_converted, box2_converted, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def intersection_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'STBOX *':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.intersection_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_eq(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_eq(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_ne(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_ne(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_cmp(box1: 'const TBOX *', box2: 'const TBOX *') -> 'int':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_cmp(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_lt(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_lt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_le(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_le(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_ge(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_ge(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def tbox_gt(box1: 'const TBOX *', box2: 'const TBOX *') -> 'bool':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
    result = _lib.tbox_gt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_eq(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_eq(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_ne(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_ne(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_cmp(box1: 'const STBOX *', box2: 'const STBOX *') -> 'int':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_cmp(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_lt(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_lt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_le(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_le(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_ge(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_ge(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def stbox_gt(box1: 'const STBOX *', box2: 'const STBOX *') -> 'bool':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.stbox_gt(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


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
    return result if result != _ffi.NULL else None, size_out


def temporal_as_mfjson(temp: 'const Temporal *', with_bbox: bool, flags: int, precision: int, srs: "Optional[str]") -> str:
    temp_converted = _ffi.cast('const Temporal *', temp)
    srs_converted = srs.encode('utf-8') if srs else _ffi.NULL
    result = _lib.temporal_as_mfjson(temp_converted, with_bbox, flags, precision, srs_converted)
    result = _ffi.string(result).decode('utf-8')
    return result if result != _ffi.NULL else None


def temporal_as_wkb(temp: 'const Temporal *', variant: int) -> "Tuple['uint8_t *', 'size_t *']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    variant_converted = _ffi.cast('uint8_t', variant)
    size_out = _ffi.new('size_t *')
    result = _lib.temporal_as_wkb(temp_converted, variant_converted, size_out)
    return result if result != _ffi.NULL else None, size_out


def temporal_from_hexwkb(hexwkb: str) -> 'Temporal *':
    hexwkb_converted = hexwkb.encode('utf-8')
    result = _lib.temporal_from_hexwkb(hexwkb_converted)
    return result if result != _ffi.NULL else None


def temporal_from_mfjson(mfjson: str) -> 'Temporal *':
    mfjson_converted = mfjson.encode('utf-8')
    result = _lib.temporal_from_mfjson(mfjson_converted)
    return result if result != _ffi.NULL else None


def temporal_from_wkb(wkb: 'uint8_t *', size: int) -> 'Temporal *':
    wkb_converted = _ffi.cast('uint8_t *', wkb)
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


def tboolinstset_from_base(b: bool, iset: 'const TInstantSet *') -> 'TInstantSet *':
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.tboolinstset_from_base(b, iset_converted)
    return result if result != _ffi.NULL else None


def tboolinstset_from_base_time(b: bool, ts: 'const TimestampSet *') -> 'TInstantSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.tboolinstset_from_base_time(b, ts_converted)
    return result if result != _ffi.NULL else None


def tboolseq_from_base(b: bool, seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tboolseq_from_base(b, seq_converted)
    return result if result != _ffi.NULL else None


def tboolseq_from_base_time(b: bool, p: 'const Period *') -> 'TSequence *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.tboolseq_from_base_time(b, p_converted)
    return result if result != _ffi.NULL else None


def tboolseqset_from_base(b: bool, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tboolseqset_from_base(b, ss_converted)
    return result if result != _ffi.NULL else None


def tboolseqset_from_base_time(b: bool, ps: 'const PeriodSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.tboolseqset_from_base_time(b, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_copy(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_copy(temp_converted)
    return result if result != _ffi.NULL else None


def tfloat_from_base(b: bool, temp: 'const Temporal *', linear: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_from_base(b, temp_converted, linear)
    return result if result != _ffi.NULL else None


def tfloatinst_make(d: float, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tfloatinst_make(d, t_converted)
    return result if result != _ffi.NULL else None


def tfloatinstset_from_base(b: bool, iset: 'const TInstantSet *') -> 'TInstantSet *':
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.tfloatinstset_from_base(b, iset_converted)
    return result if result != _ffi.NULL else None


def tfloatinstset_from_base_time(b: bool, ts: 'const TimestampSet *') -> 'TInstantSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.tfloatinstset_from_base_time(b, ts_converted)
    return result if result != _ffi.NULL else None


def tfloatseq_from_base(b: bool, seq: 'const TSequence *', linear: bool) -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tfloatseq_from_base(b, seq_converted, linear)
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_time(b: bool, p: 'const Period *', linear: bool) -> 'TSequence *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.tfloatseq_from_base_time(b, p_converted, linear)
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base(b: bool, ss: 'const TSequenceSet *', linear: bool) -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tfloatseqset_from_base(b, ss_converted, linear)
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base_time(b: bool, ps: 'const PeriodSet *', linear: bool) -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.tfloatseqset_from_base_time(b, ps_converted, linear)
    return result if result != _ffi.NULL else None


def tgeogpoint_from_base(gs: 'const GSERIALIZED *', temp: 'const Temporal *', linear: bool) -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeogpoint_from_base(gs_converted, temp_converted, linear)
    return result if result != _ffi.NULL else None


def tgeogpointinst_make(gs: 'const GSERIALIZED *', t: int) -> 'TInstant *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tgeogpointinst_make(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


# def tgeogpointinst_make_source(srid: 'int32_t', hasz: int, hasm: int, p: 'const POINT4D *', t: int) -> 'TInstant *':
#     srid_converted = _ffi.cast('int32_t', srid)
#     p_converted = _ffi.cast('const POINT4D *', p)
#     t_converted = _ffi.cast('TimestampTz', t)
#     result = _lib.tgeogpointinst_make_source(srid_converted, hasz, hasm, p_converted, t_converted)
#     return result if result != _ffi.NULL else None
#

def tgeogpointinstset_from_base(gs: 'const GSERIALIZED *', iset: 'const TInstantSet *') -> 'TInstantSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.tgeogpointinstset_from_base(gs_converted, iset_converted)
    return result if result != _ffi.NULL else None


def tgeogpointinstset_from_base_time(gs: 'const GSERIALIZED *', ts: 'const TimestampSet *') -> 'TInstantSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.tgeogpointinstset_from_base_time(gs_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_base(gs: 'const GSERIALIZED *', seq: 'const TSequence *', linear: bool) -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tgeogpointseq_from_base(gs_converted, seq_converted, linear)
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_base_time(gs: 'const GSERIALIZED *', p: 'const Period *', linear: bool) -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.tgeogpointseq_from_base_time(gs_converted, p_converted, linear)
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_base(gs: 'const GSERIALIZED *', ss: 'const TSequenceSet *', linear: bool) -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tgeogpointseqset_from_base(gs_converted, ss_converted, linear)
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_base_time(gs: 'const GSERIALIZED *', ps: 'const PeriodSet *', linear: bool) -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.tgeogpointseqset_from_base_time(gs_converted, ps_converted, linear)
    return result if result != _ffi.NULL else None


def tgeompoint_from_base(gs: 'const GSERIALIZED *', temp: 'const Temporal *', linear: bool) -> 'Temporal *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeompoint_from_base(gs_converted, temp_converted, linear)
    return result if result != _ffi.NULL else None


def tgeompointinst_make(gs: 'const GSERIALIZED *', t: int) -> 'TInstant *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tgeompointinst_make(gs_converted, t_converted)
    return result if result != _ffi.NULL else None


def tgeompointinstset_from_base(gs: 'const GSERIALIZED *', iset: 'const TInstantSet *') -> 'TInstantSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.tgeompointinstset_from_base(gs_converted, iset_converted)
    return result if result != _ffi.NULL else None


def tgeompointinstset_from_base_time(gs: 'const GSERIALIZED *', ts: 'const TimestampSet *') -> 'TInstantSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.tgeompointinstset_from_base_time(gs_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tgeompointseq_from_base(gs: 'const GSERIALIZED *', seq: 'const TSequence *', linear: bool) -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tgeompointseq_from_base(gs_converted, seq_converted, linear)
    return result if result != _ffi.NULL else None


def tgeompointseq_from_base_time(gs: 'const GSERIALIZED *', p: 'const Period *', linear: bool) -> 'TSequence *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.tgeompointseq_from_base_time(gs_converted, p_converted, linear)
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_base(gs: 'const GSERIALIZED *', ss: 'const TSequenceSet *', linear: bool) -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tgeompointseqset_from_base(gs_converted, ss_converted, linear)
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_base_time(gs: 'const GSERIALIZED *', ps: 'const PeriodSet *', linear: bool) -> 'TSequenceSet *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.tgeompointseqset_from_base_time(gs_converted, ps_converted, linear)
    return result if result != _ffi.NULL else None


def tinstantset_make(instants: 'const TInstant **', count: int, merge: bool) -> 'TInstantSet *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    result = _lib.tinstantset_make(instants_converted, count, merge)
    return result if result != _ffi.NULL else None


def tinstantset_make_free(instants: 'TInstant **', count: int, merge: bool) -> 'TInstantSet *':
    instants_converted = [_ffi.cast('TInstant *', x) for x in instants]
    result = _lib.tinstantset_make_free(instants_converted, count, merge)
    return result if result != _ffi.NULL else None


def tint_from_base(i: int, temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_from_base(i, temp_converted)
    return result if result != _ffi.NULL else None


def tintinst_make(i: int, t: int) -> 'TInstant *':
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.tintinst_make(i, t_converted)
    return result if result != _ffi.NULL else None


def tintinstset_from_base(i: int, iset: 'const TInstantSet *') -> 'TInstantSet *':
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.tintinstset_from_base(i, iset_converted)
    return result if result != _ffi.NULL else None


def tintinstset_from_base_time(i: int, ts: 'const TimestampSet *') -> 'TInstantSet *':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.tintinstset_from_base_time(i, ts_converted)
    return result if result != _ffi.NULL else None


def tintseq_from_base(i: int, seq: 'const TSequence *') -> 'TSequence *':
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.tintseq_from_base(i, seq_converted)
    return result if result != _ffi.NULL else None


def tintseq_from_base_time(i: int, p: 'const Period *') -> 'TSequence *':
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.tintseq_from_base_time(i, p_converted)
    return result if result != _ffi.NULL else None


def tintseqset_from_base(i: int, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.tintseqset_from_base(i, ss_converted)
    return result if result != _ffi.NULL else None


def tintseqset_from_base_time(i: int, ps: 'const PeriodSet *') -> 'TSequenceSet *':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.tintseqset_from_base_time(i, ps_converted)
    return result if result != _ffi.NULL else None


def tsequence_make(instants: 'const TInstant **', count: int, lower_inc: bool, upper_inc: bool, linear: bool, normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    result = _lib.tsequence_make(instants_converted, count, lower_inc, upper_inc, linear, normalize)
    return result if result != _ffi.NULL else None


def tsequence_make_free(instants: 'TInstant **', count: int, lower_inc: bool, upper_inc: bool, linear: bool, normalize: bool) -> 'TSequence *':
    instants_converted = [_ffi.cast('TInstant *', x) for x in instants]
    result = _lib.tsequence_make_free(instants_converted, count, lower_inc, upper_inc, linear, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make(sequences: 'const TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('const TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make(sequences_converted, count, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make_free(sequences: 'TSequence **', count: int, normalize: bool) -> 'TSequenceSet *':
    sequences_converted = [_ffi.cast('TSequence *', x) for x in sequences]
    result = _lib.tsequenceset_make_free(sequences_converted, count, normalize)
    return result if result != _ffi.NULL else None


def tsequenceset_make_gaps(instants: 'const TInstant **', count: int, linear: bool, maxdist: 'float', maxt: 'Interval *') -> 'TSequenceSet *':
    instants_converted = [_ffi.cast('const TInstant *', x) for x in instants]
    maxdist_converted = _ffi.cast('float', maxdist)
    maxt_converted = _ffi.cast('Interval *', maxt)
    result = _lib.tsequenceset_make_gaps(instants_converted, count, linear, maxdist_converted, maxt_converted)
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


def ttextinstset_from_base(txt: str, iset: 'const TInstantSet *') -> 'TInstantSet *':
    txt_converted = cstring2text(txt)
    iset_converted = _ffi.cast('const TInstantSet *', iset)
    result = _lib.ttextinstset_from_base(txt_converted, iset_converted)
    return result if result != _ffi.NULL else None


def ttextinstset_from_base_time(txt: str, ts: 'const TimestampSet *') -> 'TInstantSet *':
    txt_converted = cstring2text(txt)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.ttextinstset_from_base_time(txt_converted, ts_converted)
    return result if result != _ffi.NULL else None


def ttextseq_from_base(txt: str, seq: 'const TSequence *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    seq_converted = _ffi.cast('const TSequence *', seq)
    result = _lib.ttextseq_from_base(txt_converted, seq_converted)
    return result if result != _ffi.NULL else None


def ttextseq_from_base_time(txt: str, p: 'const Period *') -> 'TSequence *':
    txt_converted = cstring2text(txt)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.ttextseq_from_base_time(txt_converted, p_converted)
    return result if result != _ffi.NULL else None


def ttextseqset_from_base(txt: str, ss: 'const TSequenceSet *') -> 'TSequenceSet *':
    txt_converted = cstring2text(txt)
    ss_converted = _ffi.cast('const TSequenceSet *', ss)
    result = _lib.ttextseqset_from_base(txt_converted, ss_converted)
    return result if result != _ffi.NULL else None


def ttextseqset_from_base_time(txt: str, ps: 'const PeriodSet *') -> 'TSequenceSet *':
    txt_converted = cstring2text(txt)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
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


def temporal_duration(temp: 'const Temporal *') -> 'Interval *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_duration(temp_converted)
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


def temporal_time(temp: 'const Temporal *') -> 'PeriodSet *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_time(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_timespan(temp: 'const Temporal *') -> 'Interval *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_timespan(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_timestamp_n(temp: 'const Temporal *', n: int) -> int:
    temp_converted = _ffi.cast('const Temporal *', temp)
    out_result = _ffi.new('TimestampTz *')
    result = _lib.temporal_timestamp_n(temp_converted, n, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
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


def tfloat_spans(temp: 'const Temporal *') -> "Tuple['Span **', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tfloat_spans(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


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


def temporal_append_tinstant(temp: 'const Temporal *', inst: 'const TInstant *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    inst_converted = _ffi.cast('const TInstant *', inst)
    result = _lib.temporal_append_tinstant(temp_converted, inst_converted)
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


def temporal_shift_tscale(temp: 'const Temporal *', shift: 'const Interval *', duration: "Optional['const Interval *']") -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    shift_converted = _ffi.cast('const Interval *', shift)
    duration_converted = _ffi.cast('const Interval *', duration) if duration else _ffi.NULL
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


def temporal_to_tinstantset(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tinstantset(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tsequence(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tsequence(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_to_tsequenceset(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_to_tsequenceset(temp_converted)
    return result if result != _ffi.NULL else None


def tbool_at_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_at_value(temp_converted, b)
    return result if result != _ffi.NULL else None


def tbool_at_values(temp: 'const Temporal *', values: 'bool *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('bool *', values)
    result = _lib.tbool_at_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def tbool_minus_value(temp: 'const Temporal *', b: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tbool_minus_value(temp_converted, b)
    return result if result != _ffi.NULL else None


def tbool_minus_values(temp: 'const Temporal *', values: 'bool *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('bool *', values)
    result = _lib.tbool_minus_values(temp_converted, values_converted, count)
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


def temporal_at_period(temp: 'const Temporal *', p: 'const Period *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.temporal_at_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def temporal_at_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.temporal_at_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_at_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_at_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def temporal_at_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
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


def temporal_minus_period(temp: 'const Temporal *', p: 'const Period *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.temporal_minus_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.temporal_minus_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_timestamp(temp: 'const Temporal *', t: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_minus_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def temporal_minus_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.temporal_minus_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def tfloat_at_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_at_value(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_at_values(temp: 'const Temporal *', values: 'double *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('double *', values)
    result = _lib.tfloat_at_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def tfloat_minus_value(temp: 'const Temporal *', d: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tfloat_minus_value(temp_converted, d)
    return result if result != _ffi.NULL else None


def tfloat_minus_values(temp: 'const Temporal *', values: 'double *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('double *', values)
    result = _lib.tfloat_minus_values(temp_converted, values_converted, count)
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


def tint_at_values(temp: 'const Temporal *', values: 'int *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('int *', values)
    result = _lib.tint_at_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def tint_minus_value(temp: 'const Temporal *', i: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tint_minus_value(temp_converted, i)
    return result if result != _ffi.NULL else None


def tint_minus_values(temp: 'const Temporal *', values: 'int *', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = _ffi.cast('int *', values)
    result = _lib.tint_minus_values(temp_converted, values_converted, count)
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


def tnumber_at_spans(temp: 'const Temporal *', spans: 'Span **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    spans_converted = [_ffi.cast('Span *', x) for x in spans]
    result = _lib.tnumber_at_spans(temp_converted, spans_converted, count)
    return result if result != _ffi.NULL else None


def tnumber_at_tbox(temp: 'const Temporal *', box: 'const TBOX *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tnumber_at_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tnumber_minus_span(temp: 'const Temporal *', span: 'const Span *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.tnumber_minus_span(temp_converted, span_converted)
    return result if result != _ffi.NULL else None


def tnumber_minus_spans(temp: 'const Temporal *', spans: 'Span **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    spans_converted = [_ffi.cast('Span *', x) for x in spans]
    result = _lib.tnumber_minus_spans(temp_converted, spans_converted, count)
    return result if result != _ffi.NULL else None


def tnumber_minus_tbox(temp: 'const Temporal *', box: 'const TBOX *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.tnumber_minus_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_geometry(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_at_geometry(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_stbox(temp: 'const Temporal *', box: 'const STBOX *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.tpoint_at_stbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_at_value(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_at_values(temp: 'const Temporal *', values: 'GSERIALIZED **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = [_ffi.cast('GSERIALIZED *', x) for x in values]
    result = _lib.tpoint_at_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def tpoint_minus_geometry(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.tpoint_minus_geometry(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_stbox(temp: 'const Temporal *', box: 'const STBOX *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBOX *', box)
    result = _lib.tpoint_minus_stbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_value(temp: 'const Temporal *', gs: 'GSERIALIZED *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('GSERIALIZED *', gs)
    result = _lib.tpoint_minus_value(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def tpoint_minus_values(temp: 'const Temporal *', values: 'GSERIALIZED **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = [_ffi.cast('GSERIALIZED *', x) for x in values]
    result = _lib.tpoint_minus_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def tpoint_value_at_timestamp(temp: 'const Temporal *', t: int, strict: bool) -> 'GSERIALIZED **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    out_result = _ffi.new('GSERIALIZED **')
    result = _lib.tpoint_value_at_timestamp(temp_converted, t_converted, strict, out_result)
    if result:
        return out_result if out_result != _ffi.NULL else None
    raise Exception(f'C call went wrong: {result}')


def ttext_at_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_at_value(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_at_values(temp: 'const Temporal *', values: 'text **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = [_ffi.cast('text *', x) for x in values]
    result = _lib.ttext_at_values(temp_converted, values_converted, count)
    return result if result != _ffi.NULL else None


def ttext_minus_value(temp: 'const Temporal *', txt: str) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_minus_value(temp_converted, txt_converted)
    return result if result != _ffi.NULL else None


def ttext_minus_values(temp: 'const Temporal *', values: 'text **', count: int) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    values_converted = [_ffi.cast('text *', x) for x in values]
    result = _lib.ttext_minus_values(temp_converted, values_converted, count)
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


def tnumber_degrees(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_degrees(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_derivative(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_derivative(temp_converted)
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


def adjacent_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def adjacent_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.adjacent_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def adjacent_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def adjacent_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.adjacent_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def adjacent_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.adjacent_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def adjacent_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def adjacent_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.adjacent_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def adjacent_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def adjacent_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.adjacent_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def adjacent_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.adjacent_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def adjacent_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.adjacent_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def adjacent_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.adjacent_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def adjacent_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.adjacent_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def adjacent_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def adjacent_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.adjacent_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def adjacent_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.adjacent_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def adjacent_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.adjacent_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def adjacent_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.adjacent_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def adjacent_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.adjacent_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def adjacent_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.adjacent_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def adjacent_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.adjacent_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def adjacent_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.adjacent_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def adjacent_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.adjacent_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def contained_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def contained_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.contained_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def contained_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def contained_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contained_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contained_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contained_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contained_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def contained_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.contained_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def contained_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def contained_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contained_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def contained_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contained_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contained_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.contained_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def contained_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contained_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def contained_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.contained_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contained_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def contained_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contained_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contained_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contained_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contained_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contained_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def contained_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.contained_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def contained_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.contained_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def contained_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.contained_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def contained_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.contained_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def contained_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.contained_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def contained_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.contained_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def contains_bbox_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.contains_bbox_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def contains_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def contains_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def contains_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contains_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contains_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contains_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contains_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def contains_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.contains_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def contains_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def contains_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.contains_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def contains_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.contains_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def contains_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.contains_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def contains_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.contains_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def contains_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.contains_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def contains_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def contains_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contains_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contains_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contains_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def contains_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.contains_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def contains_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.contains_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def contains_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.contains_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def contains_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.contains_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def contains_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.contains_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def contains_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.contains_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def contains_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.contains_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def left_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def left_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def left_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def left_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def overlaps_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def overlaps_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overlaps_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overlaps_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def overlaps_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overlaps_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overlaps_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overlaps_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overlaps_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overlaps_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overlaps_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overlaps_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overlaps_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overlaps_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def overlaps_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overlaps_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overlaps_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.overlaps_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def overlaps_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overlaps_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def overlaps_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overlaps_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overlaps_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def overlaps_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overlaps_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overlaps_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overlaps_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overlaps_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overlaps_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def overlaps_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.overlaps_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def overlaps_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.overlaps_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def overlaps_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.overlaps_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def overlaps_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overlaps_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overlaps_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overlaps_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overlaps_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overlaps_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overleft_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def overleft_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def overleft_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def overleft_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def overright_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def overright_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def overright_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def overright_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def right_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def right_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def right_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def right_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def same_float_tfloat(d: float, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_float_tfloat(d, tnumber_converted)
    return result if result != _ffi.NULL else None


def same_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.same_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def same_int_tint(i: int, tnumber: 'const Temporal *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_int_tint(i, tnumber_converted)
    return result if result != _ffi.NULL else None


def same_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.same_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def same_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.same_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def same_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def same_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.same_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def same_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def same_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.same_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def same_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.same_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def same_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.same_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def same_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.same_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def same_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.same_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def same_tfloat_float(tnumber: 'const Temporal *', d: float) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_tfloat_float(tnumber_converted, d)
    return result if result != _ffi.NULL else None


def same_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.same_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def same_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.same_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def same_tint_int(tnumber: 'const Temporal *', i: int) -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.same_tint_int(tnumber_converted, i)
    return result if result != _ffi.NULL else None


def same_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.same_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def same_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.same_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def same_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.same_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def same_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.same_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def same_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.same_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def same_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.same_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def above_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.above_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def above_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.above_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def above_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.above_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def above_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.above_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def above_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.above_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def after_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.after_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def after_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.after_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def after_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.after_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def after_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.after_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def after_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.after_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def after_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.after_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def after_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.after_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def after_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.after_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def after_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.after_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def after_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.after_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def after_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.after_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def after_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.after_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def after_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.after_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def after_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.after_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def after_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.after_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def back_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.back_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def back_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.back_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def back_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.back_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def back_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.back_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def back_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.back_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def before_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.before_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def before_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.before_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def before_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.before_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def before_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.before_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def before_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.before_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def before_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.before_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def before_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.before_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def before_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.before_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def before_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.before_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def before_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.before_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def before_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.before_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def before_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.before_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def before_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.before_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def before_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.before_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def before_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.before_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def below_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.below_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def below_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.below_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def below_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.below_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def below_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.below_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def below_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.below_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def front_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.front_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def front_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.front_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def front_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.front_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def front_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.front_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def front_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.front_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def left_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.left_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def left_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def left_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.left_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def left_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.left_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def left_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.left_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def left_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.left_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def left_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.left_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def left_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.left_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def left_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.left_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def left_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.left_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overabove_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overabove_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overabove_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overabove_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overabove_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overabove_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overabove_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overabove_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overabove_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overabove_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overafter_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overafter_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overafter_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overafter_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overafter_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overafter_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overafter_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overafter_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overafter_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overafter_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def overafter_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overafter_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overafter_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.overafter_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def overafter_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overafter_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def overafter_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overafter_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overafter_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overafter_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overafter_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overafter_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overafter_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.overafter_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def overafter_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.overafter_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def overafter_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overafter_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overafter_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overafter_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overback_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overback_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overback_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overback_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overback_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overback_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overback_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overback_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overback_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overback_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overbefore_period_temporal(p: 'const Period *', temp: 'const Temporal *') -> 'bool':
    p_converted = _ffi.cast('const Period *', p)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overbefore_period_temporal(p_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overbefore_periodset_temporal(ps: 'const PeriodSet *', temp: 'const Temporal *') -> 'bool':
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overbefore_periodset_temporal(ps_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overbefore_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overbefore_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overbefore_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overbefore_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overbefore_temporal_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.overbefore_temporal_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def overbefore_temporal_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.overbefore_temporal_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def overbefore_temporal_temporal(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'bool':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.overbefore_temporal_temporal(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def overbefore_temporal_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.overbefore_temporal_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def overbefore_temporal_timestampset(temp: 'const Temporal *', ts: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    result = _lib.overbefore_temporal_timestampset(temp_converted, ts_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestamp_temporal(t: int, temp: 'const Temporal *') -> 'bool':
    t_converted = _ffi.cast('TimestampTz', t)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overbefore_timestamp_temporal(t_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overbefore_timestampset_temporal(ts: 'const TimestampSet *', temp: 'const Temporal *') -> 'bool':
    ts_converted = _ffi.cast('const TimestampSet *', ts)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.overbefore_timestampset_temporal(ts_converted, temp_converted)
    return result if result != _ffi.NULL else None


def overbefore_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.overbefore_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def overbefore_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.overbefore_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def overbefore_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overbefore_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overbefore_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overbefore_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overbelow_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overbelow_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overbelow_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overbelow_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overbelow_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overbelow_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overbelow_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overbelow_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overbelow_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overbelow_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overfront_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overfront_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overfront_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overfront_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overfront_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overfront_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overfront_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overfront_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overfront_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overfront_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overleft_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overleft_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overleft_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overleft_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overleft_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overleft_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overleft_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overleft_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.overleft_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def overleft_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.overleft_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def overleft_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.overleft_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def overleft_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overleft_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overleft_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overleft_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overleft_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overleft_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def overright_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overright_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overright_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overright_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.overright_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def overright_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.overright_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def overright_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.overright_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def overright_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.overright_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def overright_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.overright_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def overright_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.overright_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def overright_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.overright_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def overright_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.overright_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
    return result if result != _ffi.NULL else None


def right_geo_tpoint(geo: 'const GSERIALIZED *', tpoint: 'const Temporal *') -> 'bool':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.right_geo_tpoint(geo_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def right_span_tnumber(span: 'const Span *', tnumber: 'const Temporal *') -> 'bool':
    span_converted = _ffi.cast('const Span *', span)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_span_tnumber(span_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def right_stbox_tpoint(stbox: 'const STBOX *', tpoint: 'const Temporal *') -> 'bool':
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    result = _lib.right_stbox_tpoint(stbox_converted, tpoint_converted)
    return result if result != _ffi.NULL else None


def right_tbox_tnumber(tbox: 'const TBOX *', tnumber: 'const Temporal *') -> 'bool':
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    result = _lib.right_tbox_tnumber(tbox_converted, tnumber_converted)
    return result if result != _ffi.NULL else None


def right_tnumber_span(tnumber: 'const Temporal *', span: 'const Span *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    span_converted = _ffi.cast('const Span *', span)
    result = _lib.right_tnumber_span(tnumber_converted, span_converted)
    return result if result != _ffi.NULL else None


def right_tnumber_tbox(tnumber: 'const Temporal *', tbox: 'const TBOX *') -> 'bool':
    tnumber_converted = _ffi.cast('const Temporal *', tnumber)
    tbox_converted = _ffi.cast('const TBOX *', tbox)
    result = _lib.right_tnumber_tbox(tnumber_converted, tbox_converted)
    return result if result != _ffi.NULL else None


def right_tnumber_tnumber(tnumber1: 'const Temporal *', tnumber2: 'const Temporal *') -> 'bool':
    tnumber1_converted = _ffi.cast('const Temporal *', tnumber1)
    tnumber2_converted = _ffi.cast('const Temporal *', tnumber2)
    result = _lib.right_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    return result if result != _ffi.NULL else None


def right_tpoint_geo(tpoint: 'const Temporal *', geo: 'const GSERIALIZED *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.right_tpoint_geo(tpoint_converted, geo_converted)
    return result if result != _ffi.NULL else None


def right_tpoint_stbox(tpoint: 'const Temporal *', stbox: 'const STBOX *') -> 'bool':
    tpoint_converted = _ffi.cast('const Temporal *', tpoint)
    stbox_converted = _ffi.cast('const STBOX *', stbox)
    result = _lib.right_tpoint_stbox(tpoint_converted, stbox_converted)
    return result if result != _ffi.NULL else None


def right_tpoint_tpoint(tpoint1: 'const Temporal *', tpoint2: 'const Temporal *') -> 'bool':
    tpoint1_converted = _ffi.cast('const Temporal *', tpoint1)
    tpoint2_converted = _ffi.cast('const Temporal *', tpoint2)
    result = _lib.right_tpoint_tpoint(tpoint1_converted, tpoint2_converted)
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


def nad_stbox_geo(box: 'const STBOX *', gs: 'const GSERIALIZED *') -> 'double':
    box_converted = _ffi.cast('const STBOX *', box)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_stbox_geo(box_converted, gs_converted)
    return result if result != _ffi.NULL else None


def nad_stbox_stbox(box1: 'const STBOX *', box2: 'const STBOX *') -> 'double':
    box1_converted = _ffi.cast('const STBOX *', box1)
    box2_converted = _ffi.cast('const STBOX *', box2)
    result = _lib.nad_stbox_stbox(box1_converted, box2_converted)
    return result if result != _ffi.NULL else None


def nad_tbox_tbox(box1: 'const TBOX *', box2: 'const TBOX *') -> 'double':
    box1_converted = _ffi.cast('const TBOX *', box1)
    box2_converted = _ffi.cast('const TBOX *', box2)
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


def nad_tnumber_tbox(temp: 'const Temporal *', box: 'const TBOX *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const TBOX *', box)
    result = _lib.nad_tnumber_tbox(temp_converted, box_converted)
    return result if result != _ffi.NULL else None


def nad_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.nad_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def nad_tpoint_stbox(temp: 'const Temporal *', box: 'const STBOX *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    box_converted = _ffi.cast('const STBOX *', box)
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


def tpoint_azimuth(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_azimuth(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_cumulative_length(temp: 'const Temporal *') -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_cumulative_length(temp_converted)
    return result if result != _ffi.NULL else None


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


def tpoint_stboxes(temp: 'const Temporal *') -> "Tuple['STBOX *', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    count = _ffi.new('int *')
    result = _lib.tpoint_stboxes(temp_converted, count)
    return result if result != _ffi.NULL else None, count[0]


def tpoint_trajectory(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_trajectory(temp_converted)
    return result if result != _ffi.NULL else None


def geo_expand_spatial(gs: 'const GSERIALIZED *', d: float) -> 'STBOX *':
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.geo_expand_spatial(gs_converted, d)
    return result if result != _ffi.NULL else None


def tgeompoint_tgeogpoint(temp: 'const Temporal *', oper: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tgeompoint_tgeogpoint(temp_converted, oper)
    return result if result != _ffi.NULL else None


def tpoint_expand_spatial(temp: 'const Temporal *', d: float) -> 'STBOX *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_expand_spatial(temp_converted, d)
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


def contains_geo_tpoint(geo: 'const GSERIALIZED *', temp: 'const Temporal *') -> 'int':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.contains_geo_tpoint(geo_converted, temp_converted)
    return result if result != _ffi.NULL else None


def disjoint_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.disjoint_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def disjoint_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.disjoint_tpoint_tpoint(temp1_converted, temp2_converted)
    return result if result != _ffi.NULL else None


def dwithin_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', dist: float) -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.dwithin_tpoint_geo(temp_converted, gs_converted, dist)
    return result if result != _ffi.NULL else None


def dwithin_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *', dist: float) -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.dwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist)
    return result if result != _ffi.NULL else None


def intersects_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.intersects_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def intersects_tpoint_tpoint(temp1: 'const Temporal *', temp2: 'const Temporal *') -> 'int':
    temp1_converted = _ffi.cast('const Temporal *', temp1)
    temp2_converted = _ffi.cast('const Temporal *', temp2)
    result = _lib.intersects_tpoint_tpoint(temp1_converted, temp2_converted)
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


def touches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *') -> 'int':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.touches_tpoint_geo(temp_converted, gs_converted)
    return result if result != _ffi.NULL else None


def ttouches_tpoint_geo(temp: 'const Temporal *', gs: 'const GSERIALIZED *', restr: bool, atvalue: bool) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    gs_converted = _ffi.cast('const GSERIALIZED *', gs)
    result = _lib.ttouches_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    return result if result != _ffi.NULL else None


def temporal_intersects_period(temp: 'const Temporal *', p: 'const Period *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    p_converted = _ffi.cast('const Period *', p)
    result = _lib.temporal_intersects_period(temp_converted, p_converted)
    return result if result != _ffi.NULL else None


def temporal_intersects_periodset(temp: 'const Temporal *', ps: 'const PeriodSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ps_converted = _ffi.cast('const PeriodSet *', ps)
    result = _lib.temporal_intersects_periodset(temp_converted, ps_converted)
    return result if result != _ffi.NULL else None


def temporal_intersects_timestamp(temp: 'const Temporal *', t: int) -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    t_converted = _ffi.cast('TimestampTz', t)
    result = _lib.temporal_intersects_timestamp(temp_converted, t_converted)
    return result if result != _ffi.NULL else None


def temporal_intersects_timestampset(temp: 'const Temporal *', ss: 'const TimestampSet *') -> 'bool':
    temp_converted = _ffi.cast('const Temporal *', temp)
    ss_converted = _ffi.cast('const TimestampSet *', ss)
    result = _lib.temporal_intersects_timestampset(temp_converted, ss_converted)
    return result if result != _ffi.NULL else None


def tnumber_integral(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_integral(temp_converted)
    return result if result != _ffi.NULL else None


def tnumber_twavg(temp: 'const Temporal *') -> 'double':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tnumber_twavg(temp_converted)
    return result if result != _ffi.NULL else None


def tpoint_twcentroid(temp: 'const Temporal *') -> 'GSERIALIZED *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.tpoint_twcentroid(temp_converted)
    return result if result != _ffi.NULL else None


def temporal_time_split(temp: 'const Temporal *', start: int, end: int, tunits: int, torigin: int, count: int, buckets: 'TimestampTz **', newcount: 'int *') -> 'Temporal **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    start_converted = _ffi.cast('TimestampTz', start)
    end_converted = _ffi.cast('TimestampTz', end)
    tunits_converted = _ffi.cast('int64', tunits)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    buckets_converted = [_ffi.cast('TimestampTz *', x) for x in buckets]
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.temporal_time_split(temp_converted, start_converted, end_converted, tunits_converted, torigin_converted, count, buckets_converted, newcount_converted)
    return result if result != _ffi.NULL else None


def tint_value_split(temp: 'const Temporal *', start_bucket: int, size: int, count: int, buckets: 'int **', newcount: 'int *') -> 'Temporal **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    buckets_converted = [_ffi.cast('int *', x) for x in buckets]
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.tint_value_split(temp_converted, start_bucket, size, count, buckets_converted, newcount_converted)
    return result if result != _ffi.NULL else None


def tfloat_value_split(temp: 'const Temporal *', start_bucket: float, size: float, count: int, buckets: 'float **', newcount: 'int *') -> 'Temporal **':
    temp_converted = _ffi.cast('const Temporal *', temp)
    buckets_converted = [_ffi.cast('float *', x) for x in buckets]
    newcount_converted = _ffi.cast('int *', newcount)
    result = _lib.tfloat_value_split(temp_converted, start_bucket, size, count, buckets_converted, newcount_converted)
    return result if result != _ffi.NULL else None


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


def geo_to_tpoint(geo: 'const GSERIALIZED *') -> 'Temporal *':
    geo_converted = _ffi.cast('const GSERIALIZED *', geo)
    result = _lib.geo_to_tpoint(geo_converted)
    return result if result != _ffi.NULL else None


def temporal_simplify(temp: 'const Temporal *', synchronized: bool, eps_dist: float) -> 'Temporal *':
    temp_converted = _ffi.cast('const Temporal *', temp)
    result = _lib.temporal_simplify(temp_converted, synchronized, eps_dist)
    return result if result != _ffi.NULL else None


def tpoint_AsMVTGeom(temp: 'const Temporal *', bounds: 'const STBOX *', extent: 'int32_t', buffer: 'int32_t', clip_geom: bool, geom: 'GSERIALIZED **', timesarr: 'int64 **') -> "Tuple['bool', 'int']":
    temp_converted = _ffi.cast('const Temporal *', temp)
    bounds_converted = _ffi.cast('const STBOX *', bounds)
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


