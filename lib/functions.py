from datetime import datetime, timedelta
from typing import Any, Tuple

import _meos_cffi
from dateutil.parser import parse

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


def datetime_to_timestamptz(dt: datetime) -> int:
    return _lib.pg_timestamptz_in(dt.strftime('%Y-%m-%d %H:%M:%S%z').encode('utf-8'), -1)


def timestamptz_to_datetime(ts: int) -> datetime:
    return parse(pg_timestamptz_out(ts))


def timedelta_to_interval(td: timedelta) -> Any:
    return _ffi.new('Interval *', {'time': td.microseconds + td.seconds * 1000000, 'day': td.days, 'month': 0})


def interval_to_timedelta(interval: Any) -> timedelta:
    # TODO fix for months/years
    return timedelta(days=interval.day, microseconds=interval.time)


def meos_initialize() -> None:
    _lib.meos_initialize()


def meos_finish() -> None:
    _lib.meos_finish()


def pg_timestamptz_in(string: str, typmod: int) -> int:
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamptz_in(string_converted, typmod_converted)
    result = int(result)
    return result


def pg_timestamp_in(string: str, typmod: int) -> int:
    string_converted = string.encode('utf-8')
    typmod_converted = _ffi.cast('int32', typmod)
    result = _lib.pg_timestamp_in(string_converted, typmod_converted)
    result = int(result)
    return result


def pg_timestamptz_out(dt: int) -> str:
    dt_converted = _ffi.cast('TimestampTz', dt)
    result = _lib.pg_timestamptz_out(dt_converted)
    result = _ffi.string(result).decode('utf-8')
    return result


def pg_timestamp_out(dt: int) -> str:
    dt_converted = _ffi.cast('Timestamp', dt)
    result = _lib.pg_timestamp_out(dt_converted)
    result = _ffi.string(result).decode('utf-8')
    return result


def floatspan_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.floatspan_in(string_converted)


def intspan_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.intspan_in(string_converted)


def period_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.period_in(string_converted)


def periodset_as_hexwkb(ps: Any, variant: Any, size_out: Any) -> str:
    result = _lib.periodset_as_hexwkb(ps, variant, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result


def periodset_as_wkb(ps: Any, variant: Any, size_out: Any) -> Any:
    return _lib.periodset_as_wkb(ps, variant, size_out)


def periodset_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.periodset_from_hexwkb(hexwkb)


def periodset_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.periodset_from_wkb(wkb, size)


def periodset_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.periodset_in(string_converted)


def periodset_out(ps: Any) -> str:
    result = _lib.periodset_out(ps)
    result = _ffi.string(result).decode('utf-8')
    return result


def span_as_hexwkb(s: Any, variant: Any, size_out: Any) -> str:
    result = _lib.span_as_hexwkb(s, variant, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result


def span_as_wkb(s: Any, variant: Any, size_out: Any) -> Any:
    return _lib.span_as_wkb(s, variant, size_out)


def span_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.span_from_hexwkb(hexwkb)


def span_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.span_from_wkb(wkb, size)


def span_out(s: Any, arg: Any) -> str:
    result = _lib.span_out(s, arg)
    result = _ffi.string(result).decode('utf-8')
    return result


def timestampset_as_hexwkb(ts: Any, variant: Any, size_out: Any) -> str:
    result = _lib.timestampset_as_hexwkb(ts, variant, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result


def timestampset_as_wkb(ts: Any, variant: Any, size_out: Any) -> Any:
    return _lib.timestampset_as_wkb(ts, variant, size_out)


def timestampset_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.timestampset_from_hexwkb(hexwkb)


def timestampset_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.timestampset_from_wkb(wkb, size)


def timestampset_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.timestampset_in(string_converted)


def timestampset_out(ts: Any) -> str:
    result = _lib.timestampset_out(ts)
    result = _ffi.string(result).decode('utf-8')
    return result


def floatspan_make(lower: Any, upper: Any, lower_inc: Any, upper_inc: Any) -> Any:
    return _lib.floatspan_make(lower, upper, lower_inc, upper_inc)


def intspan_make(lower: Any, upper: Any, lower_inc: Any, upper_inc: Any) -> Any:
    return _lib.intspan_make(lower, upper, lower_inc, upper_inc)


def period_make(lower: int, upper: int, lower_inc: Any, upper_inc: Any) -> Any:
    lower_converted = _ffi.cast('TimestampTz', lower)
    upper_converted = _ffi.cast('TimestampTz', upper)
    return _lib.period_make(lower_converted, upper_converted, lower_inc, upper_inc)


def periodset_copy(ps: Any) -> Any:
    return _lib.periodset_copy(ps)


def periodset_make(periods: Any, count: Any, normalize: Any) -> Any:
    return _lib.periodset_make(periods, count, normalize)


def periodset_make_free(periods: Any, count: Any, normalize: Any) -> Any:
    return _lib.periodset_make_free(periods, count, normalize)


def span_copy(s: Any) -> Any:
    return _lib.span_copy(s)


def timestampset_copy(ts: Any) -> Any:
    return _lib.timestampset_copy(ts)


def timestampset_make(times: Any, count: Any) -> Any:
    return _lib.timestampset_make(times, count)


def timestampset_make_free(times: Any, count: Any) -> Any:
    return _lib.timestampset_make_free(times, count)


def float_to_floaspan(d: Any) -> Any:
    return _lib.float_to_floaspan(d)


def int_to_intspan(i: Any) -> Any:
    return _lib.int_to_intspan(i)


def period_to_periodset(period: Any) -> Any:
    return _lib.period_to_periodset(period)


def periodset_to_period(ps: Any) -> Any:
    return _lib.periodset_to_period(ps)


def timestamp_to_period(t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.timestamp_to_period(t_converted)


def timestamp_to_periodset(t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.timestamp_to_periodset(t_converted)


def timestamp_to_timestampset(t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.timestamp_to_timestampset(t_converted)


def timestampset_to_periodset(ts: Any) -> Any:
    return _lib.timestampset_to_periodset(ts)


def floatspan_lower(s: Any) -> Any:
    return _lib.floatspan_lower(s)


def floatspan_upper(s: Any) -> Any:
    return _lib.floatspan_upper(s)


def intspan_lower(s: Any) -> Any:
    return _lib.intspan_lower(s)


def intspan_upper(s: Any) -> Any:
    return _lib.intspan_upper(s)


def period_duration(s: Any) -> Any:
    return _lib.period_duration(s)


def period_lower(p: Any) -> int:
    result = _lib.period_lower(p)
    result = int(result)
    return result


def period_upper(p: Any) -> int:
    result = _lib.period_upper(p)
    result = int(result)
    return result


def periodset_duration(ps: Any) -> Any:
    return _lib.periodset_duration(ps)


def periodset_end_period(ps: Any) -> Any:
    return _lib.periodset_end_period(ps)


def periodset_end_timestamp(ps: Any) -> int:
    result = _lib.periodset_end_timestamp(ps)
    result = int(result)
    return result


def periodset_hash(ps: Any) -> int:
    result = _lib.periodset_hash(ps)
    result = int(result)
    return result


def periodset_hash_extended(ps: Any, seed: int) -> int:
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.periodset_hash_extended(ps, seed_converted)
    result = int(result)
    return result


def periodset_mem_size(ps: Any) -> Any:
    return _lib.periodset_mem_size(ps)


def periodset_num_periods(ps: Any) -> Any:
    return _lib.periodset_num_periods(ps)


def periodset_num_timestamps(ps: Any) -> Any:
    return _lib.periodset_num_timestamps(ps)


def periodset_period_n(ps: Any, i: Any) -> Any:
    return _lib.periodset_period_n(ps, i)


def periodset_periods(ps: Any) -> Tuple[Any, int]:
    count = _ffi.new('int *')
    result = _lib.periodset_periods(ps, count)
    return result, count[0]


def periodset_start_period(ps: Any) -> Any:
    return _lib.periodset_start_period(ps)


def periodset_start_timestamp(ps: Any) -> int:
    result = _lib.periodset_start_timestamp(ps)
    result = int(result)
    return result


def periodset_timespan(ps: Any) -> Any:
    return _lib.periodset_timespan(ps)


def periodset_timestamp_n(ps: Any, n: Any) -> Any:
    result = _ffi.new('TimestampTz *')
    r = _lib.periodset_timestamp_n(ps, n, result)
    if r:
        return result[0]
    else:
        raise Exception()


def periodset_timestamps(ps: Any) -> [Any, int]:
    count = _ffi.new('int *')
    result = _lib.periodset_timestamps(ps, count)
    return result, count[0]


def span_hash(s: Any) -> int:
    result = _lib.span_hash(s)
    result = int(result)
    return result


def span_hash_extended(s: Any, seed: int) -> int:
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.span_hash_extended(s, seed_converted)
    result = int(result)
    return result


def span_lower_inc(s: Any) -> Any:
    return _lib.span_lower_inc(s)


def span_upper_inc(s: Any) -> Any:
    return _lib.span_upper_inc(s)


def span_width(s: Any) -> Any:
    return _lib.span_width(s)


def timestampset_end_timestamp(ss: Any) -> int:
    result = _lib.timestampset_end_timestamp(ss)
    result = int(result)
    return result


def timestampset_hash(ss: Any) -> int:
    result = _lib.timestampset_hash(ss)
    result = int(result)
    return result


def timestampset_hash_extended(ss: Any, seed: int) -> int:
    seed_converted = _ffi.cast('uint64', seed)
    result = _lib.timestampset_hash_extended(ss, seed_converted)
    result = int(result)
    return result


def timestampset_mem_size(ss: Any) -> Any:
    return _lib.timestampset_mem_size(ss)


def timestampset_num_timestamps(ss: Any) -> Any:
    return _lib.timestampset_num_timestamps(ss)


def timestampset_start_timestamp(ss: Any) -> int:
    result = _lib.timestampset_start_timestamp(ss)
    result = int(result)
    return result


def timestampset_timespan(ss: Any) -> Any:
    return _lib.timestampset_timespan(ss)


def timestampset_timestamp_n(ss: Any, n: Any) -> Any:
    result = _ffi.new('TimestampTz *')
    r = _lib.timestampset_timestamp_n(ss, n, result)
    if r:
        return result[0]
    else:
        raise Exception()


def timestampset_timestamps(ss: Any) -> Any:
    return _lib.timestampset_timestamps(ss)


def periodset_shift_tscale(ps: Any, start: Any, duration: Any) -> Any:
    return _lib.periodset_shift_tscale(ps, start or _ffi.NULL, duration or _ffi.NULL)


def span_expand(s1: Any, s2: Any) -> None:
    _lib.span_expand(s1, s2)


def lower_upper_shift_tscale(shift: Any, duration: Any, lower: Any, upper: Any) -> None:
    _lib.lower_upper_shift_tscale(shift, duration, lower, upper)


def period_shift_tscale(period: Any, start: Any, duration: Any) -> Any:
    result = span_copy(period)
    _lib.period_shift_tscale(start or _ffi.NULL, duration or _ffi.NULL, result)
    return result


def timestampset_shift_tscale(ss: Any, start: Any, duration: Any) -> Any:
    return _lib.timestampset_shift_tscale(ss, start or _ffi.NULL, duration or _ffi.NULL)


def adjacent_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.adjacent_floatspan_float(s, d)


def adjacent_intspan_int(s: Any, i: Any) -> Any:
    return _lib.adjacent_intspan_int(s, i)


def adjacent_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.adjacent_period_periodset(p, ps)


def adjacent_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_period_timestamp(p, t_converted)


def adjacent_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.adjacent_period_timestampset(p, ts)


def adjacent_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.adjacent_periodset_period(ps, p)


def adjacent_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.adjacent_periodset_periodset(ps1, ps2)


def adjacent_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_periodset_timestamp(ps, t_converted)


def adjacent_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.adjacent_periodset_timestampset(ps, ts)


def adjacent_span_span(s1: Any, s2: Any) -> Any:
    return _lib.adjacent_span_span(s1, s2)


def adjacent_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_timestamp_period(t_converted, p)


def adjacent_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_timestamp_periodset(t_converted, ps)


def adjacent_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.adjacent_timestampset_period(ts, p)


def adjacent_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.adjacent_timestampset_periodset(ts, ps)


def contained_float_floatspan(d: Any, s: Any) -> Any:
    return _lib.contained_float_floatspan(d, s)


def contained_int_intspan(i: Any, s: Any) -> Any:
    return _lib.contained_int_intspan(i, s)


def contained_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.contained_period_periodset(p, ps)


def contained_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.contained_periodset_period(ps, p)


def contained_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.contained_periodset_periodset(ps1, ps2)


def contained_span_span(s1: Any, s2: Any) -> Any:
    return _lib.contained_span_span(s1, s2)


def contained_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contained_timestamp_period(t_converted, p)


def contained_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contained_timestamp_periodset(t_converted, ps)


def contained_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contained_timestamp_timestampset(t_converted, ts)


def contained_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.contained_timestampset_period(ts, p)


def contained_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.contained_timestampset_periodset(ts, ps)


def contained_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.contained_timestampset_timestampset(ts1, ts2)


def contains_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.contains_floatspan_float(s, d)


def contains_intspan_int(s: Any, i: Any) -> Any:
    return _lib.contains_intspan_int(s, i)


def contains_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.contains_period_periodset(p, ps)


def contains_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contains_period_timestamp(p, t_converted)


def contains_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.contains_period_timestampset(p, ts)


def contains_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.contains_periodset_period(ps, p)


def contains_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.contains_periodset_periodset(ps1, ps2)


def contains_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contains_periodset_timestamp(ps, t_converted)


def contains_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.contains_periodset_timestampset(ps, ts)


def contains_span_span(s1: Any, s2: Any) -> Any:
    return _lib.contains_span_span(s1, s2)


def contains_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contains_timestampset_timestamp(ts, t_converted)


def contains_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.contains_timestampset_timestampset(ts1, ts2)


def overlaps_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.overlaps_period_periodset(p, ps)


def overlaps_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.overlaps_period_timestampset(p, ts)


def overlaps_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.overlaps_periodset_period(ps, p)


def overlaps_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.overlaps_periodset_periodset(ps1, ps2)


def overlaps_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.overlaps_periodset_timestampset(ps, ts)


def overlaps_span_span(s1: Any, s2: Any) -> Any:
    return _lib.overlaps_span_span(s1, s2)


def overlaps_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.overlaps_timestampset_period(ts, p)


def overlaps_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.overlaps_timestampset_periodset(ts, ps)


def overlaps_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.overlaps_timestampset_timestampset(ts1, ts2)


def after_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.after_period_periodset(p, ps)


def after_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_period_timestamp(p, t_converted)


def after_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.after_period_timestampset(p, ts)


def after_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.after_periodset_period(ps, p)


def after_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.after_periodset_periodset(ps1, ps2)


def after_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_periodset_timestamp(ps, t_converted)


def after_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.after_periodset_timestampset(ps, ts)


def after_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_timestamp_period(t_converted, p)


def after_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_timestamp_periodset(t_converted, ps)


def after_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_timestamp_timestampset(t_converted, ts)


def after_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.after_timestampset_period(ts, p)


def after_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.after_timestampset_periodset(ts, ps)


def after_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_timestampset_timestamp(ts, t_converted)


def after_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.after_timestampset_timestampset(ts1, ts2)


def before_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.before_period_periodset(p, ps)


def before_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_period_timestamp(p, t_converted)


def before_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.before_period_timestampset(p, ts)


def before_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.before_periodset_period(ps, p)


def before_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.before_periodset_periodset(ps1, ps2)


def before_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_periodset_timestamp(ps, t_converted)


def before_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.before_periodset_timestampset(ps, ts)


def before_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_timestamp_period(t_converted, p)


def before_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_timestamp_periodset(t_converted, ps)


def before_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_timestamp_timestampset(t_converted, ts)


def before_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.before_timestampset_period(ts, p)


def before_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.before_timestampset_periodset(ts, ps)


def before_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_timestampset_timestamp(ts, t_converted)


def before_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.before_timestampset_timestampset(ts1, ts2)


def left_float_floatspan(d: Any, s: Any) -> Any:
    return _lib.left_float_floatspan(d, s)


def left_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.left_floatspan_float(s, d)


def left_int_intspan(i: Any, s: Any) -> Any:
    return _lib.left_int_intspan(i, s)


def left_intspan_int(s: Any, i: Any) -> Any:
    return _lib.left_intspan_int(s, i)


def left_span_span(s1: Any, s2: Any) -> Any:
    return _lib.left_span_span(s1, s2)


def overafter_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.overafter_period_periodset(p, ps)


def overafter_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_period_timestamp(p, t_converted)


def overafter_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.overafter_period_timestampset(p, ts)


def overafter_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.overafter_periodset_period(ps, p)


def overafter_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.overafter_periodset_periodset(ps1, ps2)


def overafter_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_periodset_timestamp(ps, t_converted)


def overafter_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.overafter_periodset_timestampset(ps, ts)


def overafter_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_timestamp_period(t_converted, p)


def overafter_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_timestamp_periodset(t_converted, ps)


def overafter_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_timestamp_timestampset(t_converted, ts)


def overafter_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.overafter_timestampset_period(ts, p)


def overafter_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.overafter_timestampset_periodset(ts, ps)


def overafter_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_timestampset_timestamp(ts, t_converted)


def overafter_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.overafter_timestampset_timestampset(ts1, ts2)


def overbefore_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.overbefore_period_periodset(p, ps)


def overbefore_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_period_timestamp(p, t_converted)


def overbefore_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.overbefore_period_timestampset(p, ts)


def overbefore_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.overbefore_periodset_period(ps, p)


def overbefore_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.overbefore_periodset_periodset(ps1, ps2)


def overbefore_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_periodset_timestamp(ps, t_converted)


def overbefore_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.overbefore_periodset_timestampset(ps, ts)


def overbefore_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_timestamp_period(t_converted, p)


def overbefore_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_timestamp_periodset(t_converted, ps)


def overbefore_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_timestamp_timestampset(t_converted, ts)


def overbefore_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.overbefore_timestampset_period(ts, p)


def overbefore_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.overbefore_timestampset_periodset(ts, ps)


def overbefore_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_timestampset_timestamp(ts, t_converted)


def overbefore_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.overbefore_timestampset_timestampset(ts1, ts2)


def overleft_float_floatspan(d: Any, s: Any) -> Any:
    return _lib.overleft_float_floatspan(d, s)


def overleft_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.overleft_floatspan_float(s, d)


def overleft_int_intspan(i: Any, s: Any) -> Any:
    return _lib.overleft_int_intspan(i, s)


def overleft_intspan_int(s: Any, i: Any) -> Any:
    return _lib.overleft_intspan_int(s, i)


def overleft_span_span(s1: Any, s2: Any) -> Any:
    return _lib.overleft_span_span(s1, s2)


def overright_float_floatspan(d: Any, s: Any) -> Any:
    return _lib.overright_float_floatspan(d, s)


def overright_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.overright_floatspan_float(s, d)


def overright_int_intspan(i: Any, s: Any) -> Any:
    return _lib.overright_int_intspan(i, s)


def overright_intspan_int(s: Any, i: Any) -> Any:
    return _lib.overright_intspan_int(s, i)


def overright_span_span(s1: Any, s2: Any) -> Any:
    return _lib.overright_span_span(s1, s2)


def right_float_floatspan(d: Any, s: Any) -> Any:
    return _lib.right_float_floatspan(d, s)


def right_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.right_floatspan_float(s, d)


def right_int_intspan(i: Any, s: Any) -> Any:
    return _lib.right_int_intspan(i, s)


def right_intspan_int(s: Any, i: Any) -> Any:
    return _lib.right_intspan_int(s, i)


def right_span_span(s1: Any, s2: Any) -> Any:
    return _lib.right_span_span(s1, s2)


def intersection_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.intersection_period_periodset(p, ps)


def intersection_period_timestamp(p: Any, t: int, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.intersection_period_timestamp(p, t_converted, result)


def intersection_period_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.intersection_period_timestampset(ps, ts)


def intersection_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.intersection_periodset_period(ps, p)


def intersection_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.intersection_periodset_periodset(ps1, ps2)


def intersection_periodset_timestamp(ps: Any, t: int, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.intersection_periodset_timestamp(ps, t_converted, result)


def intersection_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.intersection_periodset_timestampset(ps, ts)


def intersection_span_span(s1: Any, s2: Any) -> Any:
    return _lib.intersection_span_span(s1, s2)


def intersection_timestamp_period(t: int, p: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.intersection_timestamp_period(t_converted, p, result)


def intersection_timestamp_periodset(t: int, ps: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.intersection_timestamp_periodset(t_converted, ps, result)


def intersection_timestamp_timestamp(t1: int, t2: int, result: Any) -> Any:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    return _lib.intersection_timestamp_timestamp(t1_converted, t2_converted, result)


def intersection_timestamp_timestampset(t: int, ts: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.intersection_timestamp_timestampset(t_converted, ts, result)


def intersection_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.intersection_timestampset_period(ts, p)


def intersection_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.intersection_timestampset_periodset(ts, ps)


def intersection_timestampset_timestamp(ts: Any, t: Any, result: Any) -> Any:
    return _lib.intersection_timestampset_timestamp(ts, t, result)


def intersection_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.intersection_timestampset_timestampset(ts1, ts2)


def minus_period_period(p1: Any, p2: Any) -> Any:
    return _lib.minus_period_period(p1, p2)


def minus_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.minus_period_periodset(p, ps)


def minus_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_period_timestamp(p, t_converted)


def minus_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.minus_period_timestampset(p, ts)


def minus_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.minus_periodset_period(ps, p)


def minus_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.minus_periodset_periodset(ps1, ps2)


def minus_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_periodset_timestamp(ps, t_converted)


def minus_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.minus_periodset_timestampset(ps, ts)


def minus_span_span(s1: Any, s2: Any) -> Any:
    return _lib.minus_span_span(s1, s2)


def minus_timestamp_period(t: int, p: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_timestamp_period(t_converted, p, result)


def minus_timestamp_periodset(t: int, ps: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_timestamp_periodset(t_converted, ps, result)


def minus_timestamp_timestamp(t1: int, t2: int, result: Any) -> Any:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    return _lib.minus_timestamp_timestamp(t1_converted, t2_converted, result)


def minus_timestamp_timestampset(t: int, ts: Any, result: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_timestamp_timestampset(t_converted, ts, result)


def minus_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.minus_timestampset_period(ts, p)


def minus_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.minus_timestampset_periodset(ts, ps)


def minus_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.minus_timestampset_timestamp(ts, t_converted)


def minus_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.minus_timestampset_timestampset(ts1, ts2)


def union_period_period(p1: Any, p2: Any) -> Any:
    return _lib.union_period_period(p1, p2)


def union_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.union_period_periodset(p, ps)


def union_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.union_period_timestamp(p, t_converted)


def union_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.union_period_timestampset(p, ts)


def union_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.union_periodset_period(ps, p)


def union_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.union_periodset_periodset(ps1, ps2)


def union_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.union_periodset_timestamp(ps, t_converted)


def union_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.union_periodset_timestampset(ps, ts)


def union_span_span(s1: Any, s2: Any, strict: Any) -> Any:
    return _lib.union_span_span(s1, s2, strict)


def union_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.union_timestamp_period(t_converted, p)


def union_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.union_timestamp_periodset(t_converted, ps)


def union_timestamp_timestamp(t1: int, t2: int) -> Any:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    return _lib.union_timestamp_timestamp(t1_converted, t2_converted)


def union_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.union_timestamp_timestampset(t_converted, ts)


def union_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.union_timestampset_period(ts, p)


def union_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.union_timestampset_periodset(ts, ps)


def union_timestampset_timestamp(ts: Any, t: Any) -> Any:
    return _lib.union_timestampset_timestamp(ts, t)


def union_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.union_timestampset_timestampset(ts1, ts2)


def distance_floatspan_float(s: Any, d: Any) -> Any:
    return _lib.distance_floatspan_float(s, d)


def distance_intspan_int(s: Any, i: Any) -> Any:
    return _lib.distance_intspan_int(s, i)


def distance_period_periodset(p: Any, ps: Any) -> Any:
    return _lib.distance_period_periodset(p, ps)


def distance_period_timestamp(p: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_period_timestamp(p, t_converted)


def distance_period_timestampset(p: Any, ts: Any) -> Any:
    return _lib.distance_period_timestampset(p, ts)


def distance_periodset_period(ps: Any, p: Any) -> Any:
    return _lib.distance_periodset_period(ps, p)


def distance_periodset_periodset(ps1: Any, ps2: Any) -> Any:
    return _lib.distance_periodset_periodset(ps1, ps2)


def distance_periodset_timestamp(ps: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_periodset_timestamp(ps, t_converted)


def distance_periodset_timestampset(ps: Any, ts: Any) -> Any:
    return _lib.distance_periodset_timestampset(ps, ts)


def distance_span_span(s1: Any, s2: Any) -> Any:
    return _lib.distance_span_span(s1, s2)


def distance_timestamp_period(t: int, p: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_timestamp_period(t_converted, p)


def distance_timestamp_periodset(t: int, ps: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_timestamp_periodset(t_converted, ps)


def distance_timestamp_timestamp(t1: int, t2: int) -> Any:
    t1_converted = _ffi.cast('TimestampTz', t1)
    t2_converted = _ffi.cast('TimestampTz', t2)
    return _lib.distance_timestamp_timestamp(t1_converted, t2_converted)


def distance_timestamp_timestampset(t: int, ts: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_timestamp_timestampset(t_converted, ts)


def distance_timestampset_period(ts: Any, p: Any) -> Any:
    return _lib.distance_timestampset_period(ts, p)


def distance_timestampset_periodset(ts: Any, ps: Any) -> Any:
    return _lib.distance_timestampset_periodset(ts, ps)


def distance_timestampset_timestamp(ts: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.distance_timestampset_timestamp(ts, t_converted)


def distance_timestampset_timestampset(ts1: Any, ts2: Any) -> Any:
    return _lib.distance_timestampset_timestampset(ts1, ts2)


def periodset_eq(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_eq(ps1, ps2)


def periodset_ne(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_ne(ps1, ps2)


def periodset_cmp(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_cmp(ps1, ps2)


def periodset_lt(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_lt(ps1, ps2)


def periodset_le(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_le(ps1, ps2)


def periodset_ge(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_ge(ps1, ps2)


def periodset_gt(ps1: Any, ps2: Any) -> Any:
    return _lib.periodset_gt(ps1, ps2)


def span_eq(s1: Any, s2: Any) -> Any:
    return _lib.span_eq(s1, s2)


def span_ne(s1: Any, s2: Any) -> Any:
    return _lib.span_ne(s1, s2)


def span_cmp(s1: Any, s2: Any) -> Any:
    return _lib.span_cmp(s1, s2)


def span_lt(s1: Any, s2: Any) -> Any:
    return _lib.span_lt(s1, s2)


def span_le(s1: Any, s2: Any) -> Any:
    return _lib.span_le(s1, s2)


def span_ge(s1: Any, s2: Any) -> Any:
    return _lib.span_ge(s1, s2)


def span_gt(s1: Any, s2: Any) -> Any:
    return _lib.span_gt(s1, s2)


def timestampset_eq(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_eq(ss1, ss2)


def timestampset_ne(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_ne(ss1, ss2)


def timestampset_cmp(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_cmp(ss1, ss2)


def timestampset_lt(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_lt(ss1, ss2)


def timestampset_le(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_le(ss1, ss2)


def timestampset_ge(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_ge(ss1, ss2)


def timestampset_gt(ss1: Any, ss2: Any) -> Any:
    return _lib.timestampset_gt(ss1, ss2)


def tbox_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tbox_in(string_converted)


def tbox_out(box: Any, maxdd: Any) -> str:
    result = _lib.tbox_out(box, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def tbox_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.tbox_from_wkb(wkb, size)


def tbox_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.tbox_from_hexwkb(hexwkb)


def stbox_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.stbox_from_wkb(wkb, size)


def stbox_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.stbox_from_hexwkb(hexwkb)


def tbox_as_wkb(box: Any, variant: Any, size_out: Any) -> Any:
    return _lib.tbox_as_wkb(box, variant, size_out)


def tbox_as_hexwkb(box: Any, variant: Any, size: Any) -> str:
    result = _lib.tbox_as_hexwkb(box, variant, size)
    result = _ffi.string(result).decode('utf-8')
    return result


def stbox_as_wkb(box: Any, variant: Any, size_out: Any) -> Any:
    return _lib.stbox_as_wkb(box, variant, size_out)


def stbox_as_hexwkb(box: Any, variant: Any, size: Any) -> str:
    result = _lib.stbox_as_hexwkb(box, variant, size)
    result = _ffi.string(result).decode('utf-8')
    return result


def stbox_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.stbox_in(string_converted)


def stbox_out(box: Any, maxdd: Any) -> str:
    result = _lib.stbox_out(box, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def tbox_make(hasx: Any, hast: Any, xmin: Any, xmax: Any, tmin: int, tmax: int) -> Any:
    tmin_converted = _ffi.cast('TimestampTz', tmin)
    tmax_converted = _ffi.cast('TimestampTz', tmax)
    return _lib.tbox_make(hasx, hast, xmin, xmax, tmin_converted, tmax_converted)


def tbox_set(hasx: Any, hast: Any, xmin: Any, xmax: Any, tmin: int, tmax: int, box: Any) -> None:
    tmin_converted = _ffi.cast('TimestampTz', tmin)
    tmax_converted = _ffi.cast('TimestampTz', tmax)
    _lib.tbox_set(hasx, hast, xmin, xmax, tmin_converted, tmax_converted, box)


def tbox_copy(box: Any) -> Any:
    return _lib.tbox_copy(box)


def stbox_make(hasx: Any, hasz: Any, hast: Any, geodetic: Any, srid: int, xmin: Any, xmax: Any, ymin: Any, ymax: Any,
               zmin: Any, zmax: Any, tmin: int, tmax: int) -> Any:
    srid_converted = _ffi.cast('int32', srid)
    tmin_converted = _ffi.cast('TimestampTz', tmin)
    tmax_converted = _ffi.cast('TimestampTz', tmax)
    return _lib.stbox_make(hasx, hasz, hast, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax,
                           tmin_converted, tmax_converted)


def stbox_set(hasx: Any, hasz: Any, hast: Any, geodetic: Any, srid: int, xmin: Any, xmax: Any, ymin: Any, ymax: Any,
              zmin: Any, zmax: Any, tmin: int, tmax: int, box: Any) -> None:
    srid_converted = _ffi.cast('int32', srid)
    tmin_converted = _ffi.cast('TimestampTz', tmin)
    tmax_converted = _ffi.cast('TimestampTz', tmax)
    _lib.stbox_set(hasx, hasz, hast, geodetic, srid_converted, xmin, xmax, ymin, ymax, zmin, zmax, tmin_converted,
                   tmax_converted, box)


def stbox_copy(box: Any) -> Any:
    return _lib.stbox_copy(box)


def int_to_tbox(i: Any) -> Any:
    return _lib.int_to_tbox(i)


def float_to_tbox(d: Any) -> Any:
    return _lib.float_to_tbox(d)


def span_to_tbox(span: Any) -> Any:
    return _lib.span_to_tbox(span)


def timestamp_to_tbox(t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.timestamp_to_tbox(t_converted)


def timestampset_to_tbox(ss: Any) -> Any:
    return _lib.timestampset_to_tbox(ss)


def period_to_tbox(p: Any) -> Any:
    return _lib.period_to_tbox(p)


def periodset_to_tbox(ps: Any) -> Any:
    return _lib.periodset_to_tbox(ps)


def int_timestamp_to_tbox(i: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.int_timestamp_to_tbox(i, t_converted)


def float_timestamp_to_tbox(d: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.float_timestamp_to_tbox(d, t_converted)


def int_period_to_tbox(i: Any, p: Any) -> Any:
    return _lib.int_period_to_tbox(i, p)


def float_period_to_tbox(d: Any, p: Any) -> Any:
    return _lib.float_period_to_tbox(d, p)


def span_timestamp_to_tbox(span: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.span_timestamp_to_tbox(span, t_converted)


def span_period_to_tbox(span: Any, p: Any) -> Any:
    return _lib.span_period_to_tbox(span, p)


def tbox_to_intspan(box: Any) -> Any:
    return _lib.tbox_to_intspan(box)


def tbox_to_floatspan(box: Any) -> Any:
    return _lib.tbox_to_floatspan(box)


def tbox_to_period(box: Any) -> Any:
    return _lib.tbox_to_period(box)


def stbox_to_period(box: Any) -> Any:
    return _lib.stbox_to_period(box)


def tnumber_to_tbox(temp: Any) -> Any:
    return _lib.tnumber_to_tbox(temp)


def stbox_to_geometry(box: Any) -> Any:
    return _lib.stbox_to_geometry(box)


def tpoint_to_stbox(temp: Any) -> Any:
    return _lib.tpoint_to_stbox(temp)


def geo_to_stbox(gs: Any) -> Any:
    return _lib.geo_to_stbox(gs)


def timestamp_to_stbox(t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.timestamp_to_stbox(t_converted)


def timestampset_to_stbox(ts: Any) -> Any:
    return _lib.timestampset_to_stbox(ts)


def period_to_stbox(p: Any) -> Any:
    return _lib.period_to_stbox(p)


def periodset_to_stbox(ps: Any) -> Any:
    return _lib.periodset_to_stbox(ps)


def geo_timestamp_to_stbox(gs: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.geo_timestamp_to_stbox(gs, t_converted)


def geo_period_to_stbox(gs: Any, p: Any) -> Any:
    return _lib.geo_period_to_stbox(gs, p)


def tbox_hasx(box: Any) -> Any:
    return _lib.tbox_hasx(box)


def tbox_hast(box: Any) -> Any:
    return _lib.tbox_hast(box)


def tbox_xmin(box: Any, result: Any) -> Any:
    return _lib.tbox_xmin(box, result)


def tbox_xmax(box: Any, result: Any) -> Any:
    return _lib.tbox_xmax(box, result)


def tbox_tmin(box: Any, result: Any) -> Any:
    return _lib.tbox_tmin(box, result)


def tbox_tmax(box: Any, result: Any) -> Any:
    return _lib.tbox_tmax(box, result)


def stbox_hasx(box: Any) -> Any:
    return _lib.stbox_hasx(box)


def stbox_hasz(box: Any) -> Any:
    return _lib.stbox_hasz(box)


def stbox_hast(box: Any) -> Any:
    return _lib.stbox_hast(box)


def stbox_isgeodetic(box: Any) -> Any:
    return _lib.stbox_isgeodetic(box)


def stbox_xmin(box: Any, result: Any) -> Any:
    return _lib.stbox_xmin(box, result)


def stbox_xmax(box: Any, result: Any) -> Any:
    return _lib.stbox_xmax(box, result)


def stbox_ymin(box: Any, result: Any) -> Any:
    return _lib.stbox_ymin(box, result)


def stbox_ymax(box: Any, result: Any) -> Any:
    return _lib.stbox_ymax(box, result)


def stbox_zmin(box: Any, result: Any) -> Any:
    return _lib.stbox_zmin(box, result)


def stbox_zmax(box: Any, result: Any) -> Any:
    return _lib.stbox_zmax(box, result)


def stbox_tmin(box: Any, result: Any) -> Any:
    return _lib.stbox_tmin(box, result)


def stbox_tmax(box: Any, result: Any) -> Any:
    return _lib.stbox_tmax(box, result)


def stbox_get_srid(box: Any) -> int:
    result = _lib.stbox_get_srid(box)
    result = int(result)
    return result


def tbox_expand(box1: Any, box2: Any) -> None:
    _lib.tbox_expand(box1, box2)


def tbox_shift_tscale(start: Any, duration: Any, box: Any) -> None:
    _lib.tbox_shift_tscale(start, duration, box)


def tbox_expand_value(box: Any, d: Any) -> Any:
    return _lib.tbox_expand_value(box, d)


def tbox_expand_temporal(box: Any, interval: Any) -> Any:
    return _lib.tbox_expand_temporal(box, interval)


def stbox_expand(box1: Any, box2: Any) -> None:
    _lib.stbox_expand(box1, box2)


def stbox_shift_tscale(start: Any, duration: Any, box: Any) -> None:
    _lib.stbox_shift_tscale(start, duration, box)


def stbox_set_srid(box: Any, srid: int) -> Any:
    srid_converted = _ffi.cast('int32', srid)
    return _lib.stbox_set_srid(box, srid_converted)


def stbox_expand_spatial(box: Any, d: Any) -> Any:
    return _lib.stbox_expand_spatial(box, d)


def stbox_expand_temporal(box: Any, interval: Any) -> Any:
    return _lib.stbox_expand_temporal(box, interval)


def contains_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.contains_tbox_tbox(box1, box2)


def contained_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.contained_tbox_tbox(box1, box2)


def overlaps_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.overlaps_tbox_tbox(box1, box2)


def same_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.same_tbox_tbox(box1, box2)


def adjacent_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.adjacent_tbox_tbox(box1, box2)


def contains_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.contains_stbox_stbox(box1, box2)


def contained_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.contained_stbox_stbox(box1, box2)


def overlaps_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overlaps_stbox_stbox(box1, box2)


def same_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.same_stbox_stbox(box1, box2)


def adjacent_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.adjacent_stbox_stbox(box1, box2)


def left_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.left_tbox_tbox(box1, box2)


def overleft_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.overleft_tbox_tbox(box1, box2)


def right_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.right_tbox_tbox(box1, box2)


def overright_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.overright_tbox_tbox(box1, box2)


def before_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.before_tbox_tbox(box1, box2)


def overbefore_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.overbefore_tbox_tbox(box1, box2)


def after_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.after_tbox_tbox(box1, box2)


def overafter_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.overafter_tbox_tbox(box1, box2)


def left_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.left_stbox_stbox(box1, box2)


def overleft_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overleft_stbox_stbox(box1, box2)


def right_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.right_stbox_stbox(box1, box2)


def overright_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overright_stbox_stbox(box1, box2)


def below_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.below_stbox_stbox(box1, box2)


def overbelow_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overbelow_stbox_stbox(box1, box2)


def above_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.above_stbox_stbox(box1, box2)


def overabove_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overabove_stbox_stbox(box1, box2)


def front_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.front_stbox_stbox(box1, box2)


def overfront_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overfront_stbox_stbox(box1, box2)


def back_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.back_stbox_stbox(box1, box2)


def overback_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overback_stbox_stbox(box1, box2)


def before_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.before_stbox_stbox(box1, box2)


def overbefore_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overbefore_stbox_stbox(box1, box2)


def after_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.after_stbox_stbox(box1, box2)


def overafter_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.overafter_stbox_stbox(box1, box2)


def union_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.union_tbox_tbox(box1, box2)


def inter_tbox_tbox(box1: Any, box2: Any, result: Any) -> Any:
    return _lib.inter_tbox_tbox(box1, box2, result)


def intersection_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.intersection_tbox_tbox(box1, box2)


def union_stbox_stbox(box1: Any, box2: Any, strict: Any) -> Any:
    return _lib.union_stbox_stbox(box1, box2, strict)


def inter_stbox_stbox(box1: Any, box2: Any, result: Any) -> Any:
    return _lib.inter_stbox_stbox(box1, box2, result)


def intersection_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.intersection_stbox_stbox(box1, box2)


def tbox_eq(box1: Any, box2: Any) -> Any:
    return _lib.tbox_eq(box1, box2)


def tbox_ne(box1: Any, box2: Any) -> Any:
    return _lib.tbox_ne(box1, box2)


def tbox_cmp(box1: Any, box2: Any) -> Any:
    return _lib.tbox_cmp(box1, box2)


def tbox_lt(box1: Any, box2: Any) -> Any:
    return _lib.tbox_lt(box1, box2)


def tbox_le(box1: Any, box2: Any) -> Any:
    return _lib.tbox_le(box1, box2)


def tbox_ge(box1: Any, box2: Any) -> Any:
    return _lib.tbox_ge(box1, box2)


def tbox_gt(box1: Any, box2: Any) -> Any:
    return _lib.tbox_gt(box1, box2)


def stbox_eq(box1: Any, box2: Any) -> Any:
    return _lib.stbox_eq(box1, box2)


def stbox_ne(box1: Any, box2: Any) -> Any:
    return _lib.stbox_ne(box1, box2)


def stbox_cmp(box1: Any, box2: Any) -> Any:
    return _lib.stbox_cmp(box1, box2)


def stbox_lt(box1: Any, box2: Any) -> Any:
    return _lib.stbox_lt(box1, box2)


def stbox_le(box1: Any, box2: Any) -> Any:
    return _lib.stbox_le(box1, box2)


def stbox_ge(box1: Any, box2: Any) -> Any:
    return _lib.stbox_ge(box1, box2)


def stbox_gt(box1: Any, box2: Any) -> Any:
    return _lib.stbox_gt(box1, box2)


def tbool_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tbool_in(string_converted)


def tbool_out(temp: Any) -> str:
    result = _lib.tbool_out(temp)
    result = _ffi.string(result).decode('utf-8')
    return result


def temporal_as_hexwkb(temp: Any, variant: Any, size_out: Any) -> str:
    result = _lib.temporal_as_hexwkb(temp, variant, size_out)
    result = _ffi.string(result).decode('utf-8')
    return result


def temporal_as_mfjson(temp: Any, with_bbox: Any, flags: Any, precision: Any, srs: str) -> str:
    srs_converted = srs.encode('utf-8')
    result = _lib.temporal_as_mfjson(temp, with_bbox, flags, precision, srs_converted)
    result = _ffi.string(result).decode('utf-8')
    return result


def temporal_as_wkb(temp: Any, variant: Any, size_out: Any) -> Any:
    return _lib.temporal_as_wkb(temp, variant, size_out)


def temporal_from_hexwkb(hexwkb: Any) -> Any:
    return _lib.temporal_from_hexwkb(hexwkb)


def temporal_from_mfjson(mfjson: str) -> Any:
    mfjson_converted = mfjson.encode('utf-8')
    return _lib.temporal_from_mfjson(mfjson_converted)


def temporal_from_wkb(wkb: Any, size: Any) -> Any:
    return _lib.temporal_from_wkb(wkb, size)


def tfloat_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tfloat_in(string_converted)


def tfloat_out(temp: Any, maxdd: Any) -> str:
    result = _lib.tfloat_out(temp, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def tgeogpoint_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tgeogpoint_in(string_converted)


def tgeompoint_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tgeompoint_in(string_converted)


def tint_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.tint_in(string_converted)


def tint_out(temp: Any) -> str:
    result = _lib.tint_out(temp)
    result = _ffi.string(result).decode('utf-8')
    return result


def tpoint_as_ewkt(temp: Any, maxdd: Any) -> str:
    result = _lib.tpoint_as_ewkt(temp, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def tpoint_as_text(temp: Any, maxdd: Any) -> str:
    result = _lib.tpoint_as_text(temp, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def tpoint_out(temp: Any, maxdd: Any) -> str:
    result = _lib.tpoint_out(temp, maxdd)
    result = _ffi.string(result).decode('utf-8')
    return result


def ttext_in(string: str) -> Any:
    string_converted = string.encode('utf-8')
    return _lib.ttext_in(string_converted)


def ttext_out(temp: Any) -> str:
    result = _lib.ttext_out(temp)
    result = _ffi.string(result).decode('utf-8')
    return result


def tbool_from_base(b: Any, temp: Any) -> Any:
    return _lib.tbool_from_base(b, temp)


def tboolinst_make(b: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tboolinst_make(b, t_converted)


def tboolinstset_from_base(b: Any, iset: Any) -> Any:
    return _lib.tboolinstset_from_base(b, iset)


def tboolinstset_from_base_time(b: Any, ts: Any) -> Any:
    return _lib.tboolinstset_from_base_time(b, ts)


def tboolseq_from_base(b: Any, seq: Any) -> Any:
    return _lib.tboolseq_from_base(b, seq)


def tboolseq_from_base_time(b: Any, p: Any) -> Any:
    return _lib.tboolseq_from_base_time(b, p)


def tboolseqset_from_base(b: Any, ss: Any) -> Any:
    return _lib.tboolseqset_from_base(b, ss)


def tboolseqset_from_base_time(b: Any, ps: Any) -> Any:
    return _lib.tboolseqset_from_base_time(b, ps)


def temporal_copy(temp: Any) -> Any:
    return _lib.temporal_copy(temp)


def tfloat_from_base(b: Any, temp: Any, linear: Any) -> Any:
    return _lib.tfloat_from_base(b, temp, linear)


def tfloatinst_make(d: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tfloatinst_make(d, t_converted)


def tfloatinstset_from_base(b: Any, iset: Any) -> Any:
    return _lib.tfloatinstset_from_base(b, iset)


def tfloatinstset_from_base_time(b: Any, ts: Any) -> Any:
    return _lib.tfloatinstset_from_base_time(b, ts)


def tfloatseq_from_base(b: Any, seq: Any, linear: Any) -> Any:
    return _lib.tfloatseq_from_base(b, seq, linear)


def tfloatseq_from_base_time(b: Any, p: Any, linear: Any) -> Any:
    return _lib.tfloatseq_from_base_time(b, p, linear)


def tfloatseqset_from_base(b: Any, ss: Any, linear: Any) -> Any:
    return _lib.tfloatseqset_from_base(b, ss, linear)


def tfloatseqset_from_base_time(b: Any, ps: Any, linear: Any) -> Any:
    return _lib.tfloatseqset_from_base_time(b, ps, linear)


def tgeogpoint_from_base(gs: Any, temp: Any, linear: Any) -> Any:
    return _lib.tgeogpoint_from_base(gs, temp, linear)


def tgeogpointinst_make(gs: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tgeogpointinst_make(gs, t_converted)


def tgeogpointinstset_from_base(gs: Any, iset: Any) -> Any:
    return _lib.tgeogpointinstset_from_base(gs, iset)


def tgeogpointinstset_from_base_time(gs: Any, ts: Any) -> Any:
    return _lib.tgeogpointinstset_from_base_time(gs, ts)


def tgeogpointseq_from_base(gs: Any, seq: Any, linear: Any) -> Any:
    return _lib.tgeogpointseq_from_base(gs, seq, linear)


def tgeogpointseq_from_base_time(gs: Any, p: Any, linear: Any) -> Any:
    return _lib.tgeogpointseq_from_base_time(gs, p, linear)


def tgeogpointseqset_from_base(gs: Any, ss: Any, linear: Any) -> Any:
    return _lib.tgeogpointseqset_from_base(gs, ss, linear)


def tgeogpointseqset_from_base_time(gs: Any, ps: Any, linear: Any) -> Any:
    return _lib.tgeogpointseqset_from_base_time(gs, ps, linear)


def tgeompoint_from_base(gs: Any, temp: Any, linear: Any) -> Any:
    return _lib.tgeompoint_from_base(gs, temp, linear)


def tgeompointinst_make(gs: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tgeompointinst_make(gs, t_converted)


def tgeompointinstset_from_base(gs: Any, iset: Any) -> Any:
    return _lib.tgeompointinstset_from_base(gs, iset)


def tgeompointinstset_from_base_time(gs: Any, ts: Any) -> Any:
    return _lib.tgeompointinstset_from_base_time(gs, ts)


def tgeompointseq_from_base(gs: Any, seq: Any, linear: Any) -> Any:
    return _lib.tgeompointseq_from_base(gs, seq, linear)


def tgeompointseq_from_base_time(gs: Any, p: Any, linear: Any) -> Any:
    return _lib.tgeompointseq_from_base_time(gs, p, linear)


def tgeompointseqset_from_base(gs: Any, ss: Any, linear: Any) -> Any:
    return _lib.tgeompointseqset_from_base(gs, ss, linear)


def tgeompointseqset_from_base_time(gs: Any, ps: Any, linear: Any) -> Any:
    return _lib.tgeompointseqset_from_base_time(gs, ps, linear)


def tinstantset_make(instants: Any, count: Any, merge: Any) -> Any:
    return _lib.tinstantset_make(instants, count, merge)


def tinstantset_make_free(instants: Any, count: Any, merge: Any) -> Any:
    return _lib.tinstantset_make_free(instants, count, merge)


def tint_from_base(i: Any, temp: Any) -> Any:
    return _lib.tint_from_base(i, temp)


def tintinst_make(i: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tintinst_make(i, t_converted)


def tintinstset_from_base(i: Any, iset: Any) -> Any:
    return _lib.tintinstset_from_base(i, iset)


def tintinstset_from_base_time(i: Any, ts: Any) -> Any:
    return _lib.tintinstset_from_base_time(i, ts)


def tintseq_from_base(i: Any, seq: Any) -> Any:
    return _lib.tintseq_from_base(i, seq)


def tintseq_from_base_time(i: Any, p: Any) -> Any:
    return _lib.tintseq_from_base_time(i, p)


def tintseqset_from_base(i: Any, ss: Any) -> Any:
    return _lib.tintseqset_from_base(i, ss)


def tintseqset_from_base_time(i: Any, ps: Any) -> Any:
    return _lib.tintseqset_from_base_time(i, ps)


def tsequence_make(instants: Any, count: Any, lower_inc: Any, upper_inc: Any, linear: Any, normalize: Any) -> Any:
    return _lib.tsequence_make(instants, count, lower_inc, upper_inc, linear, normalize)


def tsequence_make_free(instants: Any, count: Any, lower_inc: Any, upper_inc: Any, linear: Any, normalize: Any) -> Any:
    return _lib.tsequence_make_free(instants, count, lower_inc, upper_inc, linear, normalize)


def tsequenceset_make(sequences: Any, count: Any, normalize: Any) -> Any:
    return _lib.tsequenceset_make(sequences, count, normalize)


def tsequenceset_make_free(sequences: Any, count: Any, normalize: Any) -> Any:
    return _lib.tsequenceset_make_free(sequences, count, normalize)


def tsequenceset_make_gaps(instants: Any, count: Any, linear: Any, maxdist: Any, maxt: Any) -> Any:
    return _lib.tsequenceset_make_gaps(instants, count, linear, maxdist, maxt)


def ttext_from_base(txt: Any, temp: Any) -> Any:
    return _lib.ttext_from_base(txt, temp)


def ttextinst_make(txt: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.ttextinst_make(txt, t_converted)


def ttextinstset_from_base(txt: Any, iset: Any) -> Any:
    return _lib.ttextinstset_from_base(txt, iset)


def ttextinstset_from_base_time(txt: Any, ts: Any) -> Any:
    return _lib.ttextinstset_from_base_time(txt, ts)


def ttextseq_from_base(txt: Any, seq: Any) -> Any:
    return _lib.ttextseq_from_base(txt, seq)


def ttextseq_from_base_time(txt: Any, p: Any) -> Any:
    return _lib.ttextseq_from_base_time(txt, p)


def ttextseqset_from_base(txt: Any, ss: Any) -> Any:
    return _lib.ttextseqset_from_base(txt, ss)


def ttextseqset_from_base_time(txt: Any, ps: Any) -> Any:
    return _lib.ttextseqset_from_base_time(txt, ps)


def tfloat_to_tint(temp: Any) -> Any:
    return _lib.tfloat_to_tint(temp)


def tint_to_tfloat(temp: Any) -> Any:
    return _lib.tint_to_tfloat(temp)


def tnumber_to_span(temp: Any) -> Any:
    return _lib.tnumber_to_span(temp)


def tbool_end_value(temp: Any) -> Any:
    return _lib.tbool_end_value(temp)


def tbool_start_value(temp: Any) -> Any:
    return _lib.tbool_start_value(temp)


def tbool_values(temp: Any) -> Any:
    return _lib.tbool_values(temp)


def temporal_duration(temp: Any) -> Any:
    return _lib.temporal_duration(temp)


def temporal_end_instant(temp: Any) -> Any:
    return _lib.temporal_end_instant(temp)


def temporal_end_sequence(temp: Any) -> Any:
    return _lib.temporal_end_sequence(temp)


def temporal_end_timestamp(temp: Any) -> int:
    result = _lib.temporal_end_timestamp(temp)
    result = int(result)
    return result


def temporal_hash(temp: Any) -> int:
    result = _lib.temporal_hash(temp)
    result = int(result)
    return result


def temporal_instant_n(temp: Any, n: Any) -> Any:
    return _lib.temporal_instant_n(temp, n)


def temporal_instants(temp: Any, count: Any) -> Any:
    return _lib.temporal_instants(temp, count)


def temporal_interpolation(temp: Any) -> str:
    result = _lib.temporal_interpolation(temp)
    result = _ffi.string(result).decode('utf-8')
    return result


def temporal_max_instant(temp: Any) -> Any:
    return _lib.temporal_max_instant(temp)


def temporal_min_instant(temp: Any) -> Any:
    return _lib.temporal_min_instant(temp)


def temporal_num_instants(temp: Any) -> Any:
    return _lib.temporal_num_instants(temp)


def temporal_num_sequences(temp: Any) -> Any:
    return _lib.temporal_num_sequences(temp)


def temporal_num_timestamps(temp: Any) -> Any:
    return _lib.temporal_num_timestamps(temp)


def temporal_segments(temp: Any, count: Any) -> Any:
    return _lib.temporal_segments(temp, count)


def temporal_sequence_n(temp: Any, i: Any) -> Any:
    return _lib.temporal_sequence_n(temp, i)


def temporal_sequences(temp: Any, count: Any) -> Any:
    return _lib.temporal_sequences(temp, count)


def temporal_start_instant(temp: Any) -> Any:
    return _lib.temporal_start_instant(temp)


def temporal_start_sequence(temp: Any) -> Any:
    return _lib.temporal_start_sequence(temp)


def temporal_start_timestamp(temp: Any) -> int:
    result = _lib.temporal_start_timestamp(temp)
    result = int(result)
    return result


def temporal_subtype(temp: Any) -> str:
    result = _lib.temporal_subtype(temp)
    result = _ffi.string(result).decode('utf-8')
    return result


def temporal_time(temp: Any) -> Any:
    return _lib.temporal_time(temp)


def temporal_timespan(temp: Any) -> Any:
    return _lib.temporal_timespan(temp)


def temporal_timestamp_n(temp: Any, n: Any, result: Any) -> Any:
    return _lib.temporal_timestamp_n(temp, n, result)


def temporal_timestamps(temp: Any, count: Any) -> Any:
    return _lib.temporal_timestamps(temp, count)


def tfloat_end_value(temp: Any) -> Any:
    return _lib.tfloat_end_value(temp)


def tfloat_max_value(temp: Any) -> Any:
    return _lib.tfloat_max_value(temp)


def tfloat_min_value(temp: Any) -> Any:
    return _lib.tfloat_min_value(temp)


def tfloat_spans(temp: Any, count: Any) -> Any:
    return _lib.tfloat_spans(temp, count)


def tfloat_start_value(temp: Any) -> Any:
    return _lib.tfloat_start_value(temp)


def tfloat_values(temp: Any) -> Any:
    return _lib.tfloat_values(temp)


def tint_end_value(temp: Any) -> Any:
    return _lib.tint_end_value(temp)


def tint_max_value(temp: Any) -> Any:
    return _lib.tint_max_value(temp)


def tint_min_value(temp: Any) -> Any:
    return _lib.tint_min_value(temp)


def tint_start_value(temp: Any) -> Any:
    return _lib.tint_start_value(temp)


def tint_values(temp: Any) -> Any:
    return _lib.tint_values(temp)


def tpoint_end_value(temp: Any) -> Any:
    return _lib.tpoint_end_value(temp)


def tpoint_start_value(temp: Any) -> Any:
    return _lib.tpoint_start_value(temp)


def tpoint_values(temp: Any) -> Any:
    return _lib.tpoint_values(temp)


def ttext_end_value(temp: Any) -> Any:
    return _lib.ttext_end_value(temp)


def ttext_max_value(temp: Any) -> Any:
    return _lib.ttext_max_value(temp)


def ttext_min_value(temp: Any) -> Any:
    return _lib.ttext_min_value(temp)


def ttext_start_value(temp: Any) -> Any:
    return _lib.ttext_start_value(temp)


def ttext_values(temp: Any) -> Any:
    return _lib.ttext_values(temp)


def temporal_append_tinstant(temp: Any, inst: Any) -> Any:
    return _lib.temporal_append_tinstant(temp, inst)


def temporal_merge(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_merge(temp1, temp2)


def temporal_merge_array(temparr: Any, count: Any) -> Any:
    return _lib.temporal_merge_array(temparr, count)


def temporal_shift_tscale(temp: Any, shift: Any, duration: Any) -> Any:
    return _lib.temporal_shift_tscale(temp, shift, duration)


def temporal_step_to_linear(temp: Any) -> Any:
    return _lib.temporal_step_to_linear(temp)


def temporal_to_tinstant(temp: Any) -> Any:
    return _lib.temporal_to_tinstant(temp)


def temporal_to_tinstantset(temp: Any) -> Any:
    return _lib.temporal_to_tinstantset(temp)


def temporal_to_tsequence(temp: Any) -> Any:
    return _lib.temporal_to_tsequence(temp)


def temporal_to_tsequenceset(temp: Any) -> Any:
    return _lib.temporal_to_tsequenceset(temp)


def tbool_at_value(temp: Any, b: Any) -> Any:
    return _lib.tbool_at_value(temp, b)


def tbool_at_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tbool_at_values(temp, values, count)


def tbool_minus_value(temp: Any, b: Any) -> Any:
    return _lib.tbool_minus_value(temp, b)


def tbool_minus_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tbool_minus_values(temp, values, count)


def tbool_value_at_timestamp(temp: Any, t: int, strict: Any, value: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tbool_value_at_timestamp(temp, t_converted, strict, value)


def temporal_at_max(temp: Any) -> Any:
    return _lib.temporal_at_max(temp)


def temporal_at_min(temp: Any) -> Any:
    return _lib.temporal_at_min(temp)


def temporal_at_period(temp: Any, p: Any) -> Any:
    return _lib.temporal_at_period(temp, p)


def temporal_at_periodset(temp: Any, ps: Any) -> Any:
    return _lib.temporal_at_periodset(temp, ps)


def temporal_at_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.temporal_at_timestamp(temp, t_converted)


def temporal_at_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.temporal_at_timestampset(temp, ts)


def temporal_minus_max(temp: Any) -> Any:
    return _lib.temporal_minus_max(temp)


def temporal_minus_min(temp: Any) -> Any:
    return _lib.temporal_minus_min(temp)


def temporal_minus_period(temp: Any, p: Any) -> Any:
    return _lib.temporal_minus_period(temp, p)


def temporal_minus_periodset(temp: Any, ps: Any) -> Any:
    return _lib.temporal_minus_periodset(temp, ps)


def temporal_minus_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.temporal_minus_timestamp(temp, t_converted)


def temporal_minus_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.temporal_minus_timestampset(temp, ts)


def tfloat_at_value(temp: Any, d: Any) -> Any:
    return _lib.tfloat_at_value(temp, d)


def tfloat_at_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tfloat_at_values(temp, values, count)


def tfloat_minus_value(temp: Any, d: Any) -> Any:
    return _lib.tfloat_minus_value(temp, d)


def tfloat_minus_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tfloat_minus_values(temp, values, count)


def tfloat_value_at_timestamp(temp: Any, t: int, strict: Any, value: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tfloat_value_at_timestamp(temp, t_converted, strict, value)


def tint_at_value(temp: Any, i: Any) -> Any:
    return _lib.tint_at_value(temp, i)


def tint_at_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tint_at_values(temp, values, count)


def tint_minus_value(temp: Any, i: Any) -> Any:
    return _lib.tint_minus_value(temp, i)


def tint_minus_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tint_minus_values(temp, values, count)


def tint_value_at_timestamp(temp: Any, t: int, strict: Any, value: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tint_value_at_timestamp(temp, t_converted, strict, value)


def tnumber_at_span(temp: Any, span: Any) -> Any:
    return _lib.tnumber_at_span(temp, span)


def tnumber_at_spans(temp: Any, spans: Any, count: Any) -> Any:
    return _lib.tnumber_at_spans(temp, spans, count)


def tnumber_at_tbox(temp: Any, box: Any) -> Any:
    return _lib.tnumber_at_tbox(temp, box)


def tnumber_minus_span(temp: Any, span: Any) -> Any:
    return _lib.tnumber_minus_span(temp, span)


def tnumber_minus_spans(temp: Any, spans: Any, count: Any) -> Any:
    return _lib.tnumber_minus_spans(temp, spans, count)


def tnumber_minus_tbox(temp: Any, box: Any) -> Any:
    return _lib.tnumber_minus_tbox(temp, box)


def tpoint_at_geometry(temp: Any, gs: Any) -> Any:
    return _lib.tpoint_at_geometry(temp, gs)


def tpoint_at_stbox(temp: Any, box: Any) -> Any:
    return _lib.tpoint_at_stbox(temp, box)


def tpoint_at_value(temp: Any, gs: Any) -> Any:
    return _lib.tpoint_at_value(temp, gs)


def tpoint_at_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tpoint_at_values(temp, values, count)


def tpoint_minus_geometry(temp: Any, gs: Any) -> Any:
    return _lib.tpoint_minus_geometry(temp, gs)


def tpoint_minus_stbox(temp: Any, box: Any) -> Any:
    return _lib.tpoint_minus_stbox(temp, box)


def tpoint_minus_value(temp: Any, gs: Any) -> Any:
    return _lib.tpoint_minus_value(temp, gs)


def tpoint_minus_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.tpoint_minus_values(temp, values, count)


def tpoint_value_at_timestamp(temp: Any, t: int, strict: Any, value: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.tpoint_value_at_timestamp(temp, t_converted, strict, value)


def ttext_at_value(temp: Any, txt: Any) -> Any:
    return _lib.ttext_at_value(temp, txt)


def ttext_at_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.ttext_at_values(temp, values, count)


def ttext_minus_value(temp: Any, txt: Any) -> Any:
    return _lib.ttext_minus_value(temp, txt)


def ttext_minus_values(temp: Any, values: Any, count: Any) -> Any:
    return _lib.ttext_minus_values(temp, values, count)


def ttext_value_at_timestamp(temp: Any, t: int, strict: Any, value: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.ttext_value_at_timestamp(temp, t_converted, strict, value)


def tand_bool_tbool(b: Any, temp: Any) -> Any:
    return _lib.tand_bool_tbool(b, temp)


def tand_tbool_bool(temp: Any, b: Any) -> Any:
    return _lib.tand_tbool_bool(temp, b)


def tand_tbool_tbool(temp1: Any, temp2: Any) -> Any:
    return _lib.tand_tbool_tbool(temp1, temp2)


def tnot_tbool(temp: Any) -> Any:
    return _lib.tnot_tbool(temp)


def tor_bool_tbool(b: Any, temp: Any) -> Any:
    return _lib.tor_bool_tbool(b, temp)


def tor_tbool_bool(temp: Any, b: Any) -> Any:
    return _lib.tor_tbool_bool(temp, b)


def tor_tbool_tbool(temp1: Any, temp2: Any) -> Any:
    return _lib.tor_tbool_tbool(temp1, temp2)


def add_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.add_float_tfloat(d, tnumber)


def add_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.add_int_tint(i, tnumber)


def add_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.add_tfloat_float(tnumber, d)


def add_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.add_tint_int(tnumber, i)


def add_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.add_tnumber_tnumber(tnumber1, tnumber2)


def div_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.div_float_tfloat(d, tnumber)


def div_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.div_int_tint(i, tnumber)


def div_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.div_tfloat_float(tnumber, d)


def div_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.div_tint_int(tnumber, i)


def div_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.div_tnumber_tnumber(tnumber1, tnumber2)


def mult_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.mult_float_tfloat(d, tnumber)


def mult_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.mult_int_tint(i, tnumber)


def mult_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.mult_tfloat_float(tnumber, d)


def mult_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.mult_tint_int(tnumber, i)


def mult_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.mult_tnumber_tnumber(tnumber1, tnumber2)


def sub_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.sub_float_tfloat(d, tnumber)


def sub_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.sub_int_tint(i, tnumber)


def sub_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.sub_tfloat_float(tnumber, d)


def sub_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.sub_tint_int(tnumber, i)


def sub_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.sub_tnumber_tnumber(tnumber1, tnumber2)


def tnumber_degrees(temp: Any) -> Any:
    return _lib.tnumber_degrees(temp)


def tnumber_derivative(temp: Any) -> Any:
    return _lib.tnumber_derivative(temp)


def textcat_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.textcat_text_ttext(txt, temp)


def textcat_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.textcat_ttext_text(temp, txt)


def textcat_ttext_ttext(temp1: Any, temp2: Any) -> Any:
    return _lib.textcat_ttext_ttext(temp1, temp2)


def ttext_upper(temp: Any) -> Any:
    return _lib.ttext_upper(temp)


def ttext_lower(temp: Any) -> Any:
    return _lib.ttext_lower(temp)


def adjacent_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.adjacent_float_tfloat(d, tnumber)


def adjacent_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.adjacent_geo_tpoint(geo, tpoint)


def adjacent_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.adjacent_int_tint(i, tnumber)


def adjacent_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.adjacent_period_temporal(p, temp)


def adjacent_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.adjacent_periodset_temporal(ps, temp)


def adjacent_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.adjacent_span_tnumber(span, tnumber)


def adjacent_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.adjacent_stbox_tpoint(stbox, tpoint)


def adjacent_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.adjacent_tbox_tnumber(tbox, tnumber)


def adjacent_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.adjacent_temporal_period(temp, p)


def adjacent_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.adjacent_temporal_periodset(temp, ps)


def adjacent_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.adjacent_temporal_temporal(temp1, temp2)


def adjacent_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_temporal_timestamp(temp, t_converted)


def adjacent_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.adjacent_temporal_timestampset(temp, ts)


def adjacent_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.adjacent_tfloat_float(tnumber, d)


def adjacent_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.adjacent_timestamp_temporal(t_converted, temp)


def adjacent_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.adjacent_timestampset_temporal(ts, temp)


def adjacent_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.adjacent_tint_int(tnumber, i)


def adjacent_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.adjacent_tnumber_span(tnumber, span)


def adjacent_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.adjacent_tnumber_tbox(tnumber, tbox)


def adjacent_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.adjacent_tnumber_tnumber(tnumber1, tnumber2)


def adjacent_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.adjacent_tpoint_geo(tpoint, geo)


def adjacent_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.adjacent_tpoint_stbox(tpoint, stbox)


def adjacent_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.adjacent_tpoint_tpoint(tpoint1, tpoint2)


def contained_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.contained_float_tfloat(d, tnumber)


def contained_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.contained_geo_tpoint(geo, tpoint)


def contained_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.contained_int_tint(i, tnumber)


def contained_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.contained_period_temporal(p, temp)


def contained_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.contained_periodset_temporal(ps, temp)


def contained_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.contained_span_tnumber(span, tnumber)


def contained_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.contained_stbox_tpoint(stbox, tpoint)


def contained_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.contained_tbox_tnumber(tbox, tnumber)


def contained_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.contained_temporal_period(temp, p)


def contained_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.contained_temporal_periodset(temp, ps)


def contained_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.contained_temporal_temporal(temp1, temp2)


def contained_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contained_temporal_timestamp(temp, t_converted)


def contained_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.contained_temporal_timestampset(temp, ts)


def contained_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.contained_tfloat_float(tnumber, d)


def contained_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contained_timestamp_temporal(t_converted, temp)


def contained_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.contained_timestampset_temporal(ts, temp)


def contained_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.contained_tint_int(tnumber, i)


def contained_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.contained_tnumber_span(tnumber, span)


def contained_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.contained_tnumber_tbox(tnumber, tbox)


def contained_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.contained_tnumber_tnumber(tnumber1, tnumber2)


def contained_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.contained_tpoint_geo(tpoint, geo)


def contained_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.contained_tpoint_stbox(tpoint, stbox)


def contained_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.contained_tpoint_tpoint(tpoint1, tpoint2)


def contains_bbox_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.contains_bbox_geo_tpoint(geo, tpoint)


def contains_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.contains_float_tfloat(d, tnumber)


def contains_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.contains_int_tint(i, tnumber)


def contains_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.contains_period_temporal(p, temp)


def contains_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.contains_periodset_temporal(ps, temp)


def contains_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.contains_span_tnumber(span, tnumber)


def contains_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.contains_stbox_tpoint(stbox, tpoint)


def contains_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.contains_tbox_tnumber(tbox, tnumber)


def contains_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.contains_temporal_period(temp, p)


def contains_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.contains_temporal_periodset(temp, ps)


def contains_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.contains_temporal_temporal(temp1, temp2)


def contains_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contains_temporal_timestamp(temp, t_converted)


def contains_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.contains_temporal_timestampset(temp, ts)


def contains_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.contains_tfloat_float(tnumber, d)


def contains_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.contains_timestamp_temporal(t_converted, temp)


def contains_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.contains_timestampset_temporal(ts, temp)


def contains_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.contains_tint_int(tnumber, i)


def contains_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.contains_tnumber_span(tnumber, span)


def contains_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.contains_tnumber_tbox(tnumber, tbox)


def contains_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.contains_tnumber_tnumber(tnumber1, tnumber2)


def contains_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.contains_tpoint_geo(tpoint, geo)


def contains_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.contains_tpoint_stbox(tpoint, stbox)


def contains_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.contains_tpoint_tpoint(tpoint1, tpoint2)


def left_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.left_float_tfloat(d, tnumber)


def left_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.left_int_tint(i, tnumber)


def left_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.left_tfloat_float(tnumber, d)


def left_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.left_tint_int(tnumber, i)


def overlaps_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.overlaps_float_tfloat(d, tnumber)


def overlaps_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overlaps_geo_tpoint(geo, tpoint)


def overlaps_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.overlaps_int_tint(i, tnumber)


def overlaps_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.overlaps_period_temporal(p, temp)


def overlaps_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.overlaps_periodset_temporal(ps, temp)


def overlaps_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.overlaps_span_tnumber(span, tnumber)


def overlaps_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overlaps_stbox_tpoint(stbox, tpoint)


def overlaps_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.overlaps_tbox_tnumber(tbox, tnumber)


def overlaps_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.overlaps_temporal_period(temp, p)


def overlaps_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.overlaps_temporal_periodset(temp, ps)


def overlaps_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.overlaps_temporal_temporal(temp1, temp2)


def overlaps_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overlaps_temporal_timestamp(temp, t_converted)


def overlaps_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.overlaps_temporal_timestampset(temp, ts)


def overlaps_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.overlaps_tfloat_float(tnumber, d)


def overlaps_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overlaps_timestamp_temporal(t_converted, temp)


def overlaps_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.overlaps_timestampset_temporal(ts, temp)


def overlaps_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.overlaps_tint_int(tnumber, i)


def overlaps_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.overlaps_tnumber_span(tnumber, span)


def overlaps_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.overlaps_tnumber_tbox(tnumber, tbox)


def overlaps_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.overlaps_tnumber_tnumber(tnumber1, tnumber2)


def overlaps_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overlaps_tpoint_geo(tpoint, geo)


def overlaps_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overlaps_tpoint_stbox(tpoint, stbox)


def overlaps_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overlaps_tpoint_tpoint(tpoint1, tpoint2)


def overleft_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.overleft_float_tfloat(d, tnumber)


def overleft_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.overleft_int_tint(i, tnumber)


def overleft_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.overleft_tfloat_float(tnumber, d)


def overleft_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.overleft_tint_int(tnumber, i)


def overright_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.overright_float_tfloat(d, tnumber)


def overright_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.overright_int_tint(i, tnumber)


def overright_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.overright_tfloat_float(tnumber, d)


def overright_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.overright_tint_int(tnumber, i)


def right_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.right_float_tfloat(d, tnumber)


def right_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.right_int_tint(i, tnumber)


def right_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.right_tfloat_float(tnumber, d)


def right_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.right_tint_int(tnumber, i)


def same_float_tfloat(d: Any, tnumber: Any) -> Any:
    return _lib.same_float_tfloat(d, tnumber)


def same_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.same_geo_tpoint(geo, tpoint)


def same_int_tint(i: Any, tnumber: Any) -> Any:
    return _lib.same_int_tint(i, tnumber)


def same_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.same_period_temporal(p, temp)


def same_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.same_periodset_temporal(ps, temp)


def same_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.same_span_tnumber(span, tnumber)


def same_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.same_stbox_tpoint(stbox, tpoint)


def same_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.same_tbox_tnumber(tbox, tnumber)


def same_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.same_temporal_period(temp, p)


def same_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.same_temporal_periodset(temp, ps)


def same_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.same_temporal_temporal(temp1, temp2)


def same_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.same_temporal_timestamp(temp, t_converted)


def same_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.same_temporal_timestampset(temp, ts)


def same_tfloat_float(tnumber: Any, d: Any) -> Any:
    return _lib.same_tfloat_float(tnumber, d)


def same_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.same_timestamp_temporal(t_converted, temp)


def same_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.same_timestampset_temporal(ts, temp)


def same_tint_int(tnumber: Any, i: Any) -> Any:
    return _lib.same_tint_int(tnumber, i)


def same_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.same_tnumber_span(tnumber, span)


def same_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.same_tnumber_tbox(tnumber, tbox)


def same_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.same_tnumber_tnumber(tnumber1, tnumber2)


def same_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.same_tpoint_geo(tpoint, geo)


def same_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.same_tpoint_stbox(tpoint, stbox)


def same_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.same_tpoint_tpoint(tpoint1, tpoint2)


def above_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.above_geo_tpoint(geo, tpoint)


def above_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.above_stbox_tpoint(stbox, tpoint)


def above_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.above_tpoint_geo(tpoint, geo)


def above_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.above_tpoint_stbox(tpoint, stbox)


def above_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.above_tpoint_tpoint(tpoint1, tpoint2)


def after_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.after_period_temporal(p, temp)


def after_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.after_periodset_temporal(ps, temp)


def after_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.after_stbox_tpoint(stbox, tpoint)


def after_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.after_tbox_tnumber(tbox, tnumber)


def after_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.after_temporal_period(temp, p)


def after_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.after_temporal_periodset(temp, ps)


def after_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.after_temporal_temporal(temp1, temp2)


def after_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_temporal_timestamp(temp, t_converted)


def after_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.after_temporal_timestampset(temp, ts)


def after_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.after_timestamp_temporal(t_converted, temp)


def after_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.after_timestampset_temporal(ts, temp)


def after_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.after_tnumber_tbox(tnumber, tbox)


def after_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.after_tnumber_tnumber(tnumber1, tnumber2)


def after_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.after_tpoint_stbox(tpoint, stbox)


def after_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.after_tpoint_tpoint(tpoint1, tpoint2)


def back_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.back_geo_tpoint(geo, tpoint)


def back_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.back_stbox_tpoint(stbox, tpoint)


def back_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.back_tpoint_geo(tpoint, geo)


def back_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.back_tpoint_stbox(tpoint, stbox)


def back_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.back_tpoint_tpoint(tpoint1, tpoint2)


def before_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.before_period_temporal(p, temp)


def before_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.before_periodset_temporal(ps, temp)


def before_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.before_stbox_tpoint(stbox, tpoint)


def before_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.before_tbox_tnumber(tbox, tnumber)


def before_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.before_temporal_period(temp, p)


def before_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.before_temporal_periodset(temp, ps)


def before_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.before_temporal_temporal(temp1, temp2)


def before_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_temporal_timestamp(temp, t_converted)


def before_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.before_temporal_timestampset(temp, ts)


def before_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.before_timestamp_temporal(t_converted, temp)


def before_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.before_timestampset_temporal(ts, temp)


def before_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.before_tnumber_tbox(tnumber, tbox)


def before_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.before_tnumber_tnumber(tnumber1, tnumber2)


def before_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.before_tpoint_stbox(tpoint, stbox)


def before_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.before_tpoint_tpoint(tpoint1, tpoint2)


def below_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.below_geo_tpoint(geo, tpoint)


def below_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.below_stbox_tpoint(stbox, tpoint)


def below_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.below_tpoint_geo(tpoint, geo)


def below_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.below_tpoint_stbox(tpoint, stbox)


def below_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.below_tpoint_tpoint(tpoint1, tpoint2)


def front_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.front_geo_tpoint(geo, tpoint)


def front_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.front_stbox_tpoint(stbox, tpoint)


def front_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.front_tpoint_geo(tpoint, geo)


def front_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.front_tpoint_stbox(tpoint, stbox)


def front_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.front_tpoint_tpoint(tpoint1, tpoint2)


def left_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.left_geo_tpoint(geo, tpoint)


def left_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.left_span_tnumber(span, tnumber)


def left_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.left_stbox_tpoint(stbox, tpoint)


def left_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.left_tbox_tnumber(tbox, tnumber)


def left_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.left_tnumber_span(tnumber, span)


def left_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.left_tnumber_tbox(tnumber, tbox)


def left_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.left_tnumber_tnumber(tnumber1, tnumber2)


def left_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.left_tpoint_geo(tpoint, geo)


def left_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.left_tpoint_stbox(tpoint, stbox)


def left_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.left_tpoint_tpoint(tpoint1, tpoint2)


def overabove_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overabove_geo_tpoint(geo, tpoint)


def overabove_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overabove_stbox_tpoint(stbox, tpoint)


def overabove_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overabove_tpoint_geo(tpoint, geo)


def overabove_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overabove_tpoint_stbox(tpoint, stbox)


def overabove_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overabove_tpoint_tpoint(tpoint1, tpoint2)


def overafter_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.overafter_period_temporal(p, temp)


def overafter_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.overafter_periodset_temporal(ps, temp)


def overafter_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overafter_stbox_tpoint(stbox, tpoint)


def overafter_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.overafter_tbox_tnumber(tbox, tnumber)


def overafter_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.overafter_temporal_period(temp, p)


def overafter_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.overafter_temporal_periodset(temp, ps)


def overafter_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.overafter_temporal_temporal(temp1, temp2)


def overafter_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_temporal_timestamp(temp, t_converted)


def overafter_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.overafter_temporal_timestampset(temp, ts)


def overafter_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overafter_timestamp_temporal(t_converted, temp)


def overafter_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.overafter_timestampset_temporal(ts, temp)


def overafter_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.overafter_tnumber_tbox(tnumber, tbox)


def overafter_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.overafter_tnumber_tnumber(tnumber1, tnumber2)


def overafter_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overafter_tpoint_stbox(tpoint, stbox)


def overafter_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overafter_tpoint_tpoint(tpoint1, tpoint2)


def overback_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overback_geo_tpoint(geo, tpoint)


def overback_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overback_stbox_tpoint(stbox, tpoint)


def overback_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overback_tpoint_geo(tpoint, geo)


def overback_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overback_tpoint_stbox(tpoint, stbox)


def overback_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overback_tpoint_tpoint(tpoint1, tpoint2)


def overbefore_period_temporal(p: Any, temp: Any) -> Any:
    return _lib.overbefore_period_temporal(p, temp)


def overbefore_periodset_temporal(ps: Any, temp: Any) -> Any:
    return _lib.overbefore_periodset_temporal(ps, temp)


def overbefore_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overbefore_stbox_tpoint(stbox, tpoint)


def overbefore_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.overbefore_tbox_tnumber(tbox, tnumber)


def overbefore_temporal_period(temp: Any, p: Any) -> Any:
    return _lib.overbefore_temporal_period(temp, p)


def overbefore_temporal_periodset(temp: Any, ps: Any) -> Any:
    return _lib.overbefore_temporal_periodset(temp, ps)


def overbefore_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.overbefore_temporal_temporal(temp1, temp2)


def overbefore_temporal_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_temporal_timestamp(temp, t_converted)


def overbefore_temporal_timestampset(temp: Any, ts: Any) -> Any:
    return _lib.overbefore_temporal_timestampset(temp, ts)


def overbefore_timestamp_temporal(t: int, temp: Any) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.overbefore_timestamp_temporal(t_converted, temp)


def overbefore_timestampset_temporal(ts: Any, temp: Any) -> Any:
    return _lib.overbefore_timestampset_temporal(ts, temp)


def overbefore_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.overbefore_tnumber_tbox(tnumber, tbox)


def overbefore_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.overbefore_tnumber_tnumber(tnumber1, tnumber2)


def overbefore_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overbefore_tpoint_stbox(tpoint, stbox)


def overbefore_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overbefore_tpoint_tpoint(tpoint1, tpoint2)


def overbelow_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overbelow_geo_tpoint(geo, tpoint)


def overbelow_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overbelow_stbox_tpoint(stbox, tpoint)


def overbelow_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overbelow_tpoint_geo(tpoint, geo)


def overbelow_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overbelow_tpoint_stbox(tpoint, stbox)


def overbelow_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overbelow_tpoint_tpoint(tpoint1, tpoint2)


def overfront_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overfront_geo_tpoint(geo, tpoint)


def overfront_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overfront_stbox_tpoint(stbox, tpoint)


def overfront_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overfront_tpoint_geo(tpoint, geo)


def overfront_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overfront_tpoint_stbox(tpoint, stbox)


def overfront_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overfront_tpoint_tpoint(tpoint1, tpoint2)


def overleft_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overleft_geo_tpoint(geo, tpoint)


def overleft_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.overleft_span_tnumber(span, tnumber)


def overleft_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overleft_stbox_tpoint(stbox, tpoint)


def overleft_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.overleft_tbox_tnumber(tbox, tnumber)


def overleft_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.overleft_tnumber_span(tnumber, span)


def overleft_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.overleft_tnumber_tbox(tnumber, tbox)


def overleft_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.overleft_tnumber_tnumber(tnumber1, tnumber2)


def overleft_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overleft_tpoint_geo(tpoint, geo)


def overleft_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overleft_tpoint_stbox(tpoint, stbox)


def overleft_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overleft_tpoint_tpoint(tpoint1, tpoint2)


def overright_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.overright_geo_tpoint(geo, tpoint)


def overright_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.overright_span_tnumber(span, tnumber)


def overright_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.overright_stbox_tpoint(stbox, tpoint)


def overright_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.overright_tbox_tnumber(tbox, tnumber)


def overright_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.overright_tnumber_span(tnumber, span)


def overright_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.overright_tnumber_tbox(tnumber, tbox)


def overright_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.overright_tnumber_tnumber(tnumber1, tnumber2)


def overright_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.overright_tpoint_geo(tpoint, geo)


def overright_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.overright_tpoint_stbox(tpoint, stbox)


def overright_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.overright_tpoint_tpoint(tpoint1, tpoint2)


def right_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.right_geo_tpoint(geo, tpoint)


def right_span_tnumber(span: Any, tnumber: Any) -> Any:
    return _lib.right_span_tnumber(span, tnumber)


def right_stbox_tpoint(stbox: Any, tpoint: Any) -> Any:
    return _lib.right_stbox_tpoint(stbox, tpoint)


def right_tbox_tnumber(tbox: Any, tnumber: Any) -> Any:
    return _lib.right_tbox_tnumber(tbox, tnumber)


def right_tnumber_span(tnumber: Any, span: Any) -> Any:
    return _lib.right_tnumber_span(tnumber, span)


def right_tnumber_tbox(tnumber: Any, tbox: Any) -> Any:
    return _lib.right_tnumber_tbox(tnumber, tbox)


def right_tnumber_tnumber(tnumber1: Any, tnumber2: Any) -> Any:
    return _lib.right_tnumber_tnumber(tnumber1, tnumber2)


def right_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.right_tpoint_geo(tpoint, geo)


def right_tpoint_stbox(tpoint: Any, stbox: Any) -> Any:
    return _lib.right_tpoint_stbox(tpoint, stbox)


def right_tpoint_tpoint(tpoint1: Any, tpoint2: Any) -> Any:
    return _lib.right_tpoint_tpoint(tpoint1, tpoint2)


def distance_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.distance_tfloat_float(temp, d)


def distance_tint_int(temp: Any, i: Any) -> Any:
    return _lib.distance_tint_int(temp, i)


def distance_tnumber_tnumber(temp1: Any, temp2: Any) -> Any:
    return _lib.distance_tnumber_tnumber(temp1, temp2)


def distance_tpoint_geo(temp: Any, geo: Any) -> Any:
    return _lib.distance_tpoint_geo(temp, geo)


def distance_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.distance_tpoint_tpoint(temp1, temp2)


def nad_stbox_geo(box: Any, gs: Any) -> Any:
    return _lib.nad_stbox_geo(box, gs)


def nad_stbox_stbox(box1: Any, box2: Any) -> Any:
    return _lib.nad_stbox_stbox(box1, box2)


def nad_tbox_tbox(box1: Any, box2: Any) -> Any:
    return _lib.nad_tbox_tbox(box1, box2)


def nad_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.nad_tfloat_float(temp, d)


def nad_tfloat_tfloat(temp1: Any, temp2: Any) -> Any:
    return _lib.nad_tfloat_tfloat(temp1, temp2)


def nad_tint_int(temp: Any, i: Any) -> Any:
    return _lib.nad_tint_int(temp, i)


def nad_tint_tint(temp1: Any, temp2: Any) -> Any:
    return _lib.nad_tint_tint(temp1, temp2)


def nad_tnumber_tbox(temp: Any, box: Any) -> Any:
    return _lib.nad_tnumber_tbox(temp, box)


def nad_tpoint_geo(temp: Any, gs: Any) -> Any:
    return _lib.nad_tpoint_geo(temp, gs)


def nad_tpoint_stbox(temp: Any, box: Any) -> Any:
    return _lib.nad_tpoint_stbox(temp, box)


def nad_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.nad_tpoint_tpoint(temp1, temp2)


def nai_tpoint_geo(temp: Any, gs: Any) -> Any:
    return _lib.nai_tpoint_geo(temp, gs)


def nai_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.nai_tpoint_tpoint(temp1, temp2)


def shortestline_tpoint_geo(temp: Any, gs: Any, result: Any) -> Any:
    return _lib.shortestline_tpoint_geo(temp, gs, result)


def shortestline_tpoint_tpoint(temp1: Any, temp2: Any, result: Any) -> Any:
    return _lib.shortestline_tpoint_tpoint(temp1, temp2, result)


def tbool_always_eq(temp: Any, b: Any) -> Any:
    return _lib.tbool_always_eq(temp, b)


def tbool_ever_eq(temp: Any, b: Any) -> Any:
    return _lib.tbool_ever_eq(temp, b)


def tfloat_always_eq(temp: Any, d: Any) -> Any:
    return _lib.tfloat_always_eq(temp, d)


def tfloat_always_le(temp: Any, d: Any) -> Any:
    return _lib.tfloat_always_le(temp, d)


def tfloat_always_lt(temp: Any, d: Any) -> Any:
    return _lib.tfloat_always_lt(temp, d)


def tfloat_ever_eq(temp: Any, d: Any) -> Any:
    return _lib.tfloat_ever_eq(temp, d)


def tfloat_ever_le(temp: Any, d: Any) -> Any:
    return _lib.tfloat_ever_le(temp, d)


def tfloat_ever_lt(temp: Any, d: Any) -> Any:
    return _lib.tfloat_ever_lt(temp, d)


def tgeogpoint_always_eq(temp: Any, gs: Any) -> Any:
    return _lib.tgeogpoint_always_eq(temp, gs)


def tgeogpoint_ever_eq(temp: Any, gs: Any) -> Any:
    return _lib.tgeogpoint_ever_eq(temp, gs)


def tgeompoint_always_eq(temp: Any, gs: Any) -> Any:
    return _lib.tgeompoint_always_eq(temp, gs)


def tgeompoint_ever_eq(temp: Any, gs: Any) -> Any:
    return _lib.tgeompoint_ever_eq(temp, gs)


def tint_always_eq(temp: Any, i: Any) -> Any:
    return _lib.tint_always_eq(temp, i)


def tint_always_le(temp: Any, i: Any) -> Any:
    return _lib.tint_always_le(temp, i)


def tint_always_lt(temp: Any, i: Any) -> Any:
    return _lib.tint_always_lt(temp, i)


def tint_ever_eq(temp: Any, i: Any) -> Any:
    return _lib.tint_ever_eq(temp, i)


def tint_ever_le(temp: Any, i: Any) -> Any:
    return _lib.tint_ever_le(temp, i)


def tint_ever_lt(temp: Any, i: Any) -> Any:
    return _lib.tint_ever_lt(temp, i)


def ttext_always_eq(temp: Any, txt: Any) -> Any:
    return _lib.ttext_always_eq(temp, txt)


def ttext_always_le(temp: Any, txt: Any) -> Any:
    return _lib.ttext_always_le(temp, txt)


def ttext_always_lt(temp: Any, txt: Any) -> Any:
    return _lib.ttext_always_lt(temp, txt)


def ttext_ever_eq(temp: Any, txt: Any) -> Any:
    return _lib.ttext_ever_eq(temp, txt)


def ttext_ever_le(temp: Any, txt: Any) -> Any:
    return _lib.ttext_ever_le(temp, txt)


def ttext_ever_lt(temp: Any, txt: Any) -> Any:
    return _lib.ttext_ever_lt(temp, txt)


def temporal_cmp(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_cmp(temp1, temp2)


def temporal_eq(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_eq(temp1, temp2)


def temporal_ge(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_ge(temp1, temp2)


def temporal_gt(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_gt(temp1, temp2)


def temporal_le(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_le(temp1, temp2)


def temporal_lt(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_lt(temp1, temp2)


def temporal_ne(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_ne(temp1, temp2)


def teq_bool_tbool(b: Any, temp: Any) -> Any:
    return _lib.teq_bool_tbool(b, temp)


def teq_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.teq_float_tfloat(d, temp)


def teq_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.teq_geo_tpoint(geo, tpoint)


def teq_int_tint(i: Any, temp: Any) -> Any:
    return _lib.teq_int_tint(i, temp)


def teq_point_tgeogpoint(gs: Any, temp: Any) -> Any:
    return _lib.teq_point_tgeogpoint(gs, temp)


def teq_point_tgeompoint(gs: Any, temp: Any) -> Any:
    return _lib.teq_point_tgeompoint(gs, temp)


def teq_tbool_bool(temp: Any, b: Any) -> Any:
    return _lib.teq_tbool_bool(temp, b)


def teq_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.teq_temporal_temporal(temp1, temp2)


def teq_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.teq_text_ttext(txt, temp)


def teq_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.teq_tfloat_float(temp, d)


def teq_tgeogpoint_point(temp: Any, gs: Any) -> Any:
    return _lib.teq_tgeogpoint_point(temp, gs)


def teq_tgeompoint_point(temp: Any, gs: Any) -> Any:
    return _lib.teq_tgeompoint_point(temp, gs)


def teq_tint_int(temp: Any, i: Any) -> Any:
    return _lib.teq_tint_int(temp, i)


def teq_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.teq_tpoint_geo(tpoint, geo)


def teq_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.teq_ttext_text(temp, txt)


def tge_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.tge_float_tfloat(d, temp)


def tge_int_tint(i: Any, temp: Any) -> Any:
    return _lib.tge_int_tint(i, temp)


def tge_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.tge_temporal_temporal(temp1, temp2)


def tge_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.tge_text_ttext(txt, temp)


def tge_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.tge_tfloat_float(temp, d)


def tge_tint_int(temp: Any, i: Any) -> Any:
    return _lib.tge_tint_int(temp, i)


def tge_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.tge_ttext_text(temp, txt)


def tgt_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.tgt_float_tfloat(d, temp)


def tgt_int_tint(i: Any, temp: Any) -> Any:
    return _lib.tgt_int_tint(i, temp)


def tgt_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.tgt_temporal_temporal(temp1, temp2)


def tgt_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.tgt_text_ttext(txt, temp)


def tgt_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.tgt_tfloat_float(temp, d)


def tgt_tint_int(temp: Any, i: Any) -> Any:
    return _lib.tgt_tint_int(temp, i)


def tgt_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.tgt_ttext_text(temp, txt)


def tle_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.tle_float_tfloat(d, temp)


def tle_int_tint(i: Any, temp: Any) -> Any:
    return _lib.tle_int_tint(i, temp)


def tle_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.tle_temporal_temporal(temp1, temp2)


def tle_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.tle_text_ttext(txt, temp)


def tle_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.tle_tfloat_float(temp, d)


def tle_tint_int(temp: Any, i: Any) -> Any:
    return _lib.tle_tint_int(temp, i)


def tle_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.tle_ttext_text(temp, txt)


def tlt_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.tlt_float_tfloat(d, temp)


def tlt_int_tint(i: Any, temp: Any) -> Any:
    return _lib.tlt_int_tint(i, temp)


def tlt_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.tlt_temporal_temporal(temp1, temp2)


def tlt_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.tlt_text_ttext(txt, temp)


def tlt_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.tlt_tfloat_float(temp, d)


def tlt_tint_int(temp: Any, i: Any) -> Any:
    return _lib.tlt_tint_int(temp, i)


def tlt_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.tlt_ttext_text(temp, txt)


def tne_bool_tbool(b: Any, temp: Any) -> Any:
    return _lib.tne_bool_tbool(b, temp)


def tne_float_tfloat(d: Any, temp: Any) -> Any:
    return _lib.tne_float_tfloat(d, temp)


def tne_geo_tpoint(geo: Any, tpoint: Any) -> Any:
    return _lib.tne_geo_tpoint(geo, tpoint)


def tne_int_tint(i: Any, temp: Any) -> Any:
    return _lib.tne_int_tint(i, temp)


def tne_point_tgeogpoint(gs: Any, temp: Any) -> Any:
    return _lib.tne_point_tgeogpoint(gs, temp)


def tne_point_tgeompoint(gs: Any, temp: Any) -> Any:
    return _lib.tne_point_tgeompoint(gs, temp)


def tne_tbool_bool(temp: Any, b: Any) -> Any:
    return _lib.tne_tbool_bool(temp, b)


def tne_temporal_temporal(temp1: Any, temp2: Any) -> Any:
    return _lib.tne_temporal_temporal(temp1, temp2)


def tne_text_ttext(txt: Any, temp: Any) -> Any:
    return _lib.tne_text_ttext(txt, temp)


def tne_tfloat_float(temp: Any, d: Any) -> Any:
    return _lib.tne_tfloat_float(temp, d)


def tne_tgeogpoint_point(temp: Any, gs: Any) -> Any:
    return _lib.tne_tgeogpoint_point(temp, gs)


def tne_tgeompoint_point(temp: Any, gs: Any) -> Any:
    return _lib.tne_tgeompoint_point(temp, gs)


def tne_tint_int(temp: Any, i: Any) -> Any:
    return _lib.tne_tint_int(temp, i)


def tne_tpoint_geo(tpoint: Any, geo: Any) -> Any:
    return _lib.tne_tpoint_geo(tpoint, geo)


def tne_ttext_text(temp: Any, txt: Any) -> Any:
    return _lib.tne_ttext_text(temp, txt)


def bearing_point_point(geo1: Any, geo2: Any, result: Any) -> Any:
    return _lib.bearing_point_point(geo1, geo2, result)


def bearing_tpoint_point(temp: Any, gs: Any, invert: Any) -> Any:
    return _lib.bearing_tpoint_point(temp, gs, invert)


def bearing_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.bearing_tpoint_tpoint(temp1, temp2)


def tpoint_azimuth(temp: Any) -> Any:
    return _lib.tpoint_azimuth(temp)


def tpoint_cumulative_length(temp: Any) -> Any:
    return _lib.tpoint_cumulative_length(temp)


def tpoint_get_coord(temp: Any, coord: Any) -> Any:
    return _lib.tpoint_get_coord(temp, coord)


def tpoint_is_simple(temp: Any) -> Any:
    return _lib.tpoint_is_simple(temp)


def tpoint_length(temp: Any) -> Any:
    return _lib.tpoint_length(temp)


def tpoint_speed(temp: Any) -> Any:
    return _lib.tpoint_speed(temp)


def tpoint_srid(temp: Any) -> Any:
    return _lib.tpoint_srid(temp)


def tpoint_stboxes(temp: Any, count: Any) -> Any:
    return _lib.tpoint_stboxes(temp, count)


def tpoint_trajectory(temp: Any) -> Any:
    return _lib.tpoint_trajectory(temp)


def geo_expand_spatial(gs: Any, d: Any) -> Any:
    return _lib.geo_expand_spatial(gs, d)


def tgeompoint_tgeogpoint(temp: Any, oper: Any) -> Any:
    return _lib.tgeompoint_tgeogpoint(temp, oper)


def tpoint_expand_spatial(temp: Any, d: Any) -> Any:
    return _lib.tpoint_expand_spatial(temp, d)


def tpoint_make_simple(temp: Any, count: Any) -> Any:
    return _lib.tpoint_make_simple(temp, count)


def tpoint_set_srid(temp: Any, srid: int) -> Any:
    srid_converted = _ffi.cast('int32', srid)
    return _lib.tpoint_set_srid(temp, srid_converted)


def contains_geo_tpoint(geo: Any, temp: Any) -> Any:
    return _lib.contains_geo_tpoint(geo, temp)


def disjoint_tpoint_geo(temp: Any, gs: Any) -> Any:
    return _lib.disjoint_tpoint_geo(temp, gs)


def disjoint_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.disjoint_tpoint_tpoint(temp1, temp2)


def dwithin_tpoint_geo(temp: Any, gs: Any, dist: Any) -> Any:
    return _lib.dwithin_tpoint_geo(temp, gs, dist)


def dwithin_tpoint_tpoint(temp1: Any, temp2: Any, dist: Any) -> Any:
    return _lib.dwithin_tpoint_tpoint(temp1, temp2, dist)


def intersects_tpoint_geo(temp: Any, gs: Any) -> Any:
    return _lib.intersects_tpoint_geo(temp, gs)


def intersects_tpoint_tpoint(temp1: Any, temp2: Any) -> Any:
    return _lib.intersects_tpoint_tpoint(temp1, temp2)


def tcontains_geo_tpoint(gs: Any, temp: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.tcontains_geo_tpoint(gs, temp, restr, atvalue)


def tdisjoint_tpoint_geo(temp: Any, geo: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.tdisjoint_tpoint_geo(temp, geo, restr, atvalue)


def tdwithin_tpoint_geo(temp: Any, gs: Any, dist: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.tdwithin_tpoint_geo(temp, gs, dist, restr, atvalue)


def tdwithin_tpoint_tpoint(temp1: Any, temp2: Any, dist: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.tdwithin_tpoint_tpoint(temp1, temp2, dist, restr, atvalue)


def tintersects_tpoint_geo(temp: Any, geo: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.tintersects_tpoint_geo(temp, geo, restr, atvalue)


def touches_tpoint_geo(temp: Any, gs: Any) -> Any:
    return _lib.touches_tpoint_geo(temp, gs)


def ttouches_tpoint_geo(temp: Any, gs: Any, restr: Any, atvalue: Any) -> Any:
    return _lib.ttouches_tpoint_geo(temp, gs, restr, atvalue)


def temporal_intersects_period(temp: Any, p: Any) -> Any:
    return _lib.temporal_intersects_period(temp, p)


def temporal_intersects_periodset(temp: Any, ps: Any) -> Any:
    return _lib.temporal_intersects_periodset(temp, ps)


def temporal_intersects_timestamp(temp: Any, t: int) -> Any:
    t_converted = _ffi.cast('TimestampTz', t)
    return _lib.temporal_intersects_timestamp(temp, t_converted)


def temporal_intersects_timestampset(temp: Any, ss: Any) -> Any:
    return _lib.temporal_intersects_timestampset(temp, ss)


def tnumber_integral(temp: Any) -> Any:
    return _lib.tnumber_integral(temp)


def tnumber_twavg(temp: Any) -> Any:
    return _lib.tnumber_twavg(temp)


def tpoint_twcentroid(temp: Any) -> Any:
    return _lib.tpoint_twcentroid(temp)


def temporal_time_split(temp: Any, start: int, end: int, tunits: int, torigin: int, count: Any, buckets: Any,
                        newcount: Any) -> Any:
    start_converted = _ffi.cast('TimestampTz', start)
    end_converted = _ffi.cast('TimestampTz', end)
    tunits_converted = _ffi.cast('int64', tunits)
    torigin_converted = _ffi.cast('TimestampTz', torigin)
    return _lib.temporal_time_split(temp, start_converted, end_converted, tunits_converted, torigin_converted, count,
                                    buckets, newcount)


def tint_value_split(temp: Any, start_bucket: Any, size: Any, count: Any, buckets: Any, newcount: Any) -> Any:
    return _lib.tint_value_split(temp, start_bucket, size, count, buckets, newcount)


def tfloat_value_split(temp: Any, start_bucket: Any, size: Any, count: Any, buckets: Any, newcount: Any) -> Any:
    return _lib.tfloat_value_split(temp, start_bucket, size, count, buckets, newcount)


def temporal_frechet_distance(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_frechet_distance(temp1, temp2)


def temporal_dyntimewarp_distance(temp1: Any, temp2: Any) -> Any:
    return _lib.temporal_dyntimewarp_distance(temp1, temp2)


def temporal_frechet_path(temp1: Any, temp2: Any, count: Any) -> Any:
    return _lib.temporal_frechet_path(temp1, temp2, count)


def temporal_dyntimewarp_path(temp1: Any, temp2: Any, count: Any) -> Any:
    return _lib.temporal_dyntimewarp_path(temp1, temp2, count)
