import os
import logging

from datetime import datetime, timedelta, date
from typing import Any, Tuple, Optional, List, Union

import _meos_cffi
from .errors import report_meos_exception
import shapely.geometry as spg
from dateutil.parser import parse
from shapely import wkt, get_srid, set_srid
from shapely.geometry.base import BaseGeometry

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib

_error: Optional[int] = None
_error_level: Optional[int] = None
_error_message: Optional[str] = None

logger = logging.getLogger("pymeos_cffi")


def _check_error() -> None:
    global _error, _error_level, _error_message
    if _error is not None:
        error = _error
        error_level = _error_level
        error_message = _error_message
        _error = None
        _error_level = None
        _error_message = None
        report_meos_exception(error_level, error, error_message)


@_ffi.def_extern()
def py_error_handler(error_level, error_code, error_msg):
    global _error, _error_level, _error_message
    _error = error_code
    _error_level = error_level
    _error_message = _ffi.string(error_msg).decode("utf-8")
    logger.debug(
        f"ERROR Handler called: Level: {_error} | Code: {_error_level} | Message: {_error_message}"
    )


def create_pointer(object: "Any", type: str) -> "Any *":
    return _ffi.new(f"{type} *", object)


def get_address(value: "Any") -> "Any *":
    return _ffi.addressof(value)


def datetime_to_timestamptz(dt: datetime) -> "TimestampTz":
    return _lib.pg_timestamptz_in(
        dt.strftime("%Y-%m-%d %H:%M:%S%z").encode("utf-8"), -1
    )


def timestamptz_to_datetime(ts: "TimestampTz") -> datetime:
    return parse(pg_timestamptz_out(ts))


def date_to_date_adt(dt: date) -> "DateADT":
    return _lib.pg_date_in(dt.strftime("%Y-%m-%d").encode("utf-8"))


def date_adt_to_date(ts: "DateADT") -> date:
    return parse(pg_date_out(ts)).date()


def timedelta_to_interval(td: timedelta) -> Any:
    return _ffi.new(
        "Interval *",
        {"time": td.microseconds + td.seconds * 1000000, "day": td.days, "month": 0},
    )


def interval_to_timedelta(interval: Any) -> timedelta:
    # TODO fix for months/years
    return timedelta(days=interval.day, microseconds=interval.time)


def geo_to_gserialized(geom: BaseGeometry, geodetic: bool) -> "GSERIALIZED *":
    if geodetic:
        return geography_to_gserialized(geom)
    else:
        return geometry_to_gserialized(geom)


def geometry_to_gserialized(geom: BaseGeometry) -> "GSERIALIZED *":
    text = wkt.dumps(geom)
    if get_srid(geom) > 0:
        text = f"SRID={get_srid(geom)};{text}"
    gs = pgis_geometry_in(text, -1)
    return gs


def geography_to_gserialized(geom: BaseGeometry) -> "GSERIALIZED *":
    text = wkt.dumps(geom)
    if get_srid(geom) > 0:
        text = f"SRID={get_srid(geom)};{text}"
    gs = pgis_geography_in(text, -1)
    return gs


def gserialized_to_shapely_point(
    geom: "const GSERIALIZED *", precision: int = 15
) -> spg.Point:
    text = geo_as_text(geom, precision)
    geometry = wkt.loads(text)
    srid = lwgeom_get_srid(geom)
    if srid > 0:
        geometry = set_srid(geometry, srid)
    return geometry


def gserialized_to_shapely_geometry(
    geom: "const GSERIALIZED *", precision: int = 15
) -> BaseGeometry:
    text = geo_as_text(geom, precision)
    geometry = wkt.loads(text)
    srid = lwgeom_get_srid(geom)
    if srid > 0:
        geometry = set_srid(geometry, srid)
    return geometry


def as_tinstant(temporal: "Temporal *") -> "TInstant *":
    return _ffi.cast("TInstant *", temporal)


def as_tsequence(temporal: "Temporal *") -> "TSequence *":
    return _ffi.cast("TSequence *", temporal)


def as_tsequenceset(temporal: "Temporal *") -> "TSequenceSet *":
    return _ffi.cast("TSequenceSet *", temporal)


# -----------------------------------------------------------------------------
# ----------------------End of manually-defined functions----------------------
# -----------------------------------------------------------------------------
def lwpoint_make(
    srid: "int32_t", hasz: int, hasm: int, p: "const POINT4D *"
) -> "LWPOINT *":
    srid_converted = _ffi.cast("int32_t", srid)
    p_converted = _ffi.cast("const POINT4D *", p)
    result = _lib.lwpoint_make(srid_converted, hasz, hasm, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_from_gserialized(g: "const GSERIALIZED *") -> "LWGEOM *":
    g_converted = _ffi.cast("const GSERIALIZED *", g)
    result = _lib.lwgeom_from_gserialized(g_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_from_lwgeom(geom: "LWGEOM *") -> "GSERIALIZED *":
    geom_converted = _ffi.cast("LWGEOM *", geom)
    size_converted = _ffi.NULL
    result = _lib.geo_from_lwgeom(geom_converted, size_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_get_srid(geom: "const LWGEOM *") -> "int32_t":
    geom_converted = _ffi.cast("const LWGEOM *", geom)
    result = _lib.lwgeom_get_srid(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_x(point: "const LWPOINT *") -> "double":
    point_converted = _ffi.cast("const LWPOINT *", point)
    result = _lib.lwpoint_get_x(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_y(point: "const LWPOINT *") -> "double":
    point_converted = _ffi.cast("const LWPOINT *", point)
    result = _lib.lwpoint_get_y(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_z(point: "const LWPOINT *") -> "double":
    point_converted = _ffi.cast("const LWPOINT *", point)
    result = _lib.lwpoint_get_z(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwpoint_get_m(point: "const LWPOINT *") -> "double":
    point_converted = _ffi.cast("const LWPOINT *", point)
    result = _lib.lwpoint_get_m(point_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_has_z(geom: "const LWGEOM *") -> "int":
    geom_converted = _ffi.cast("const LWGEOM *", geom)
    result = _lib.lwgeom_has_z(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lwgeom_has_m(geom: "const LWGEOM *") -> "int":
    geom_converted = _ffi.cast("const LWGEOM *", geom)
    result = _lib.lwgeom_has_m(geom_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno() -> "int":
    result = _lib.meos_errno()
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_set(err: int) -> "int":
    result = _lib.meos_errno_set(err)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_restore(err: int) -> "int":
    result = _lib.meos_errno_restore(err)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_errno_reset() -> "int":
    result = _lib.meos_errno_reset()
    _check_error()
    return result if result != _ffi.NULL else None


def meos_set_datestyle(newval: str, extra: "void *") -> "bool":
    newval_converted = newval.encode("utf-8")
    extra_converted = _ffi.cast("void *", extra)
    result = _lib.meos_set_datestyle(newval_converted, extra_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_set_intervalstyle(newval: str, extra: "Optional[int]") -> "bool":
    newval_converted = newval.encode("utf-8")
    extra_converted = extra if extra is not None else _ffi.NULL
    result = _lib.meos_set_intervalstyle(newval_converted, extra_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_get_datestyle() -> str:
    result = _lib.meos_get_datestyle()
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def meos_get_intervalstyle() -> str:
    result = _lib.meos_get_intervalstyle()
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def meos_initialize(tz_str: "Optional[str]") -> None:
    tz_str_converted = tz_str.encode("utf-8") if tz_str is not None else _ffi.NULL
    _lib.meos_initialize(tz_str_converted, _lib.py_error_handler)


def meos_finalize() -> None:
    _lib.meos_finalize()
    _check_error()


def add_date_int(d: "DateADT", days: int) -> "DateADT":
    d_converted = _ffi.cast("DateADT", d)
    days_converted = _ffi.cast("int32", days)
    result = _lib.add_date_int(d_converted, days_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_interval_interval(
    interv1: "const Interval *", interv2: "const Interval *"
) -> "Interval *":
    interv1_converted = _ffi.cast("const Interval *", interv1)
    interv2_converted = _ffi.cast("const Interval *", interv2)
    result = _lib.add_interval_interval(interv1_converted, interv2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_timestamptz_interval(t: int, interv: "const Interval *") -> "TimestampTz":
    t_converted = _ffi.cast("TimestampTz", t)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.add_timestamptz_interval(t_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bool_in(string: str) -> "bool":
    string_converted = string.encode("utf-8")
    result = _lib.bool_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bool_out(b: bool) -> str:
    result = _lib.bool_out(b)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def cstring2text(cstring: str) -> "text *":
    cstring_converted = cstring.encode("utf-8")
    result = _lib.cstring2text(cstring_converted)
    return result


def date_to_timestamptz(d: "DateADT") -> "TimestampTz":
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_to_timestamptz(d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_date_date(d1: "DateADT", d2: "DateADT") -> "Interval *":
    d1_converted = _ffi.cast("DateADT", d1)
    d2_converted = _ffi.cast("DateADT", d2)
    result = _lib.minus_date_date(d1_converted, d2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_date_int(d: "DateADT", days: int) -> "DateADT":
    d_converted = _ffi.cast("DateADT", d)
    days_converted = _ffi.cast("int32", days)
    result = _lib.minus_date_int(d_converted, days_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamptz_interval(t: int, interv: "const Interval *") -> "TimestampTz":
    t_converted = _ffi.cast("TimestampTz", t)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.minus_timestamptz_interval(t_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamptz_timestamptz(t1: int, t2: int) -> "Interval *":
    t1_converted = _ffi.cast("TimestampTz", t1)
    t2_converted = _ffi.cast("TimestampTz", t2)
    result = _lib.minus_timestamptz_timestamptz(t1_converted, t2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_interval_double(interv: "const Interval *", factor: float) -> "Interval *":
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.mult_interval_double(interv_converted, factor)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_date_in(string: str) -> "DateADT":
    string_converted = string.encode("utf-8")
    result = _lib.pg_date_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_date_out(d: "DateADT") -> str:
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.pg_date_out(d_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def pg_interval_cmp(interv1: "const Interval *", interv2: "const Interval *") -> "int":
    interv1_converted = _ffi.cast("const Interval *", interv1)
    interv2_converted = _ffi.cast("const Interval *", interv2)
    result = _lib.pg_interval_cmp(interv1_converted, interv2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_in(string: str, typmod: int) -> "Interval *":
    string_converted = string.encode("utf-8")
    typmod_converted = _ffi.cast("int32", typmod)
    result = _lib.pg_interval_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_make(
    years: int, months: int, weeks: int, days: int, hours: int, mins: int, secs: float
) -> "Interval *":
    years_converted = _ffi.cast("int32", years)
    months_converted = _ffi.cast("int32", months)
    weeks_converted = _ffi.cast("int32", weeks)
    days_converted = _ffi.cast("int32", days)
    hours_converted = _ffi.cast("int32", hours)
    mins_converted = _ffi.cast("int32", mins)
    result = _lib.pg_interval_make(
        years_converted,
        months_converted,
        weeks_converted,
        days_converted,
        hours_converted,
        mins_converted,
        secs,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def pg_interval_out(interv: "const Interval *") -> str:
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.pg_interval_out(interv_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def pg_time_in(string: str, typmod: int) -> "TimeADT":
    string_converted = string.encode("utf-8")
    typmod_converted = _ffi.cast("int32", typmod)
    result = _lib.pg_time_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_time_out(t: "TimeADT") -> str:
    t_converted = _ffi.cast("TimeADT", t)
    result = _lib.pg_time_out(t_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def pg_timestamp_in(string: str, typmod: int) -> "Timestamp":
    string_converted = string.encode("utf-8")
    typmod_converted = _ffi.cast("int32", typmod)
    result = _lib.pg_timestamp_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamp_out(t: int) -> str:
    t_converted = _ffi.cast("Timestamp", t)
    result = _lib.pg_timestamp_out(t_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def pg_timestamptz_in(string: str, typmod: int) -> "TimestampTz":
    string_converted = string.encode("utf-8")
    typmod_converted = _ffi.cast("int32", typmod)
    result = _lib.pg_timestamptz_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pg_timestamptz_out(t: int) -> str:
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.pg_timestamptz_out(t_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def text2cstring(textptr: "text *") -> str:
    result = _lib.text2cstring(textptr)
    result = _ffi.string(result).decode("utf-8")
    return result


def text_cmp(txt1: str, txt2: str) -> "int":
    txt1_converted = cstring2text(txt1)
    txt2_converted = cstring2text(txt2)
    result = _lib.text_cmp(txt1_converted, txt2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text_copy(txt: str) -> str:
    txt_converted = cstring2text(txt)
    result = _lib.text_copy(txt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def text_initcap(txt: str) -> str:
    txt_converted = cstring2text(txt)
    result = _lib.text_initcap(txt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def text_lower(txt: str) -> str:
    txt_converted = cstring2text(txt)
    result = _lib.text_lower(txt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def text_out(txt: str) -> str:
    txt_converted = cstring2text(txt)
    result = _lib.text_out(txt_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def text_upper(txt: str) -> str:
    txt_converted = cstring2text(txt)
    result = _lib.text_upper(txt_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def textcat_text_text(txt1: str, txt2: str) -> str:
    txt1_converted = cstring2text(txt1)
    txt2_converted = cstring2text(txt2)
    result = _lib.textcat_text_text(txt1_converted, txt2_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def timestamptz_to_date(t: int) -> "DateADT":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_date(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_as_ewkb(gs: "const GSERIALIZED *", endian: str) -> "bytea *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    endian_converted = endian.encode("utf-8")
    result = _lib.geo_as_ewkb(gs_converted, endian_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_as_ewkt(gs: "const GSERIALIZED *", precision: int) -> str:
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geo_as_ewkt(gs_converted, precision)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geo_as_geojson(
    gs: "const GSERIALIZED *", option: int, precision: int, srs: "Optional[str]"
) -> str:
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    srs_converted = srs.encode("utf-8") if srs is not None else _ffi.NULL
    result = _lib.geo_as_geojson(gs_converted, option, precision, srs_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geo_as_hexewkb(gs: "const GSERIALIZED *", endian: str) -> str:
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    endian_converted = endian.encode("utf-8")
    result = _lib.geo_as_hexewkb(gs_converted, endian_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geo_as_text(gs: "const GSERIALIZED *", precision: int) -> str:
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geo_as_text(gs_converted, precision)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geo_from_ewkb(bytea_wkb: "const bytea *", srid: int) -> "GSERIALIZED *":
    bytea_wkb_converted = _ffi.cast("const bytea *", bytea_wkb)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.geo_from_ewkb(bytea_wkb_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_from_geojson(geojson: str) -> "GSERIALIZED *":
    geojson_converted = geojson.encode("utf-8")
    result = _lib.geo_from_geojson(geojson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_out(gs: "const GSERIALIZED *") -> str:
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geo_out(gs_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geo_same(gs1: "const GSERIALIZED *", gs2: "const GSERIALIZED *") -> "bool":
    gs1_converted = _ffi.cast("const GSERIALIZED *", gs1)
    gs2_converted = _ffi.cast("const GSERIALIZED *", gs2)
    result = _lib.geo_same(gs1_converted, gs2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geography_from_hexewkb(wkt: str) -> "GSERIALIZED *":
    wkt_converted = wkt.encode("utf-8")
    result = _lib.geography_from_hexewkb(wkt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geography_from_text(wkt: str, srid: int) -> "GSERIALIZED *":
    wkt_converted = wkt.encode("utf-8")
    result = _lib.geography_from_text(wkt_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def geometry_from_hexewkb(wkt: str) -> "GSERIALIZED *":
    wkt_converted = wkt.encode("utf-8")
    result = _lib.geometry_from_hexewkb(wkt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geometry_from_text(wkt: str, srid: int) -> "GSERIALIZED *":
    wkt_converted = wkt.encode("utf-8")
    result = _lib.geometry_from_text(wkt_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def pgis_geography_in(string: str, geog_typmod: int) -> "GSERIALIZED *":
    string_converted = string.encode("utf-8")
    geog_typmod_converted = _ffi.cast("int32", geog_typmod)
    result = _lib.pgis_geography_in(string_converted, geog_typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def pgis_geometry_in(string: str, typmod: int) -> "GSERIALIZED *":
    string_converted = string.encode("utf-8")
    typmod_converted = _ffi.cast("int32", typmod)
    result = _lib.pgis_geometry_in(string_converted, typmod_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.bigintset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_out(set: "const Set *") -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.bigintset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def bigintspan_in(string: str) -> "Span *":
    string_converted = string.encode("utf-8")
    result = _lib.bigintspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_out(s: "const Span *") -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.bigintspan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def bigintspanset_in(string: str) -> "SpanSet *":
    string_converted = string.encode("utf-8")
    result = _lib.bigintspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_out(ss: "const SpanSet *") -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.bigintspanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def dateset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.dateset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_out(s: "const Set *") -> str:
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def datespan_in(string: str) -> "Span *":
    string_converted = string.encode("utf-8")
    result = _lib.datespan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_out(s: "const Span *") -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def datespanset_in(string: str) -> "SpanSet *":
    string_converted = string.encode("utf-8")
    result = _lib.datespanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_out(ss: "const SpanSet *") -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def floatset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.floatset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_out(set: "const Set *", maxdd: int) -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.floatset_out(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def floatspan_in(string: str) -> "Span *":
    string_converted = string.encode("utf-8")
    result = _lib.floatspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_out(s: "const Span *", maxdd: int) -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def floatspanset_in(string: str) -> "SpanSet *":
    string_converted = string.encode("utf-8")
    result = _lib.floatspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_out(ss: "const SpanSet *", maxdd: int) -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geogset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.geogset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geomset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.geomset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_as_ewkt(set: "const Set *", maxdd: int) -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.geoset_as_ewkt(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geoset_as_text(set: "const Set *", maxdd: int) -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.geoset_as_text(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def geoset_out(set: "const Set *", maxdd: int) -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.geoset_out(set_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def intset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.intset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_out(set: "const Set *") -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.intset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def intspan_in(string: str) -> "Span *":
    string_converted = string.encode("utf-8")
    result = _lib.intspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_out(s: "const Span *") -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def intspanset_in(string: str) -> "SpanSet *":
    string_converted = string.encode("utf-8")
    result = _lib.intspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_out(ss: "const SpanSet *") -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def set_as_hexwkb(s: "const Set *", variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast("const Set *", s)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.set_as_hexwkb(s_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size_out[0]


def set_as_wkb(s: "const Set *", variant: int) -> bytes:
    s_converted = _ffi.cast("const Set *", s)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.set_as_wkb(s_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def set_from_hexwkb(hexwkb: str) -> "Set *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.set_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_from_wkb(wkb: bytes) -> "Set *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.set_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def span_as_hexwkb(s: "const Span *", variant: int) -> "Tuple[str, 'size_t *']":
    s_converted = _ffi.cast("const Span *", s)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.span_as_hexwkb(s_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size_out[0]


def span_as_wkb(s: "const Span *", variant: int) -> bytes:
    s_converted = _ffi.cast("const Span *", s)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.span_as_wkb(s_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def span_from_hexwkb(hexwkb: str) -> "Span *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.span_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_from_wkb(wkb: bytes) -> "Span *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.span_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def spanset_as_hexwkb(ss: "const SpanSet *", variant: int) -> "Tuple[str, 'size_t *']":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.spanset_as_hexwkb(ss_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size_out[0]


def spanset_as_wkb(ss: "const SpanSet *", variant: int) -> bytes:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.spanset_as_wkb(ss_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def spanset_from_hexwkb(hexwkb: str) -> "SpanSet *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.spanset_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_from_wkb(wkb: bytes) -> "SpanSet *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.spanset_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def textset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.textset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_out(set: "const Set *") -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.textset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tstzset_in(string: str) -> "Set *":
    string_converted = string.encode("utf-8")
    result = _lib.tstzset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_out(set: "const Set *") -> str:
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.tstzset_out(set_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tstzspan_in(string: str) -> "Span *":
    string_converted = string.encode("utf-8")
    result = _lib.tstzspan_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_out(s: "const Span *") -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_out(s_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tstzspanset_in(string: str) -> "SpanSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tstzspanset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_out(ss: "const SpanSet *") -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_out(ss_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def bigintset_make(values: "List[const int64]") -> "Set *":
    values_converted = _ffi.new("const int64 []", values)
    result = _lib.bigintset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_make(
    lower: int, upper: int, lower_inc: bool, upper_inc: bool
) -> "Span *":
    lower_converted = _ffi.cast("int64", lower)
    upper_converted = _ffi.cast("int64", upper)
    result = _lib.bigintspan_make(
        lower_converted, upper_converted, lower_inc, upper_inc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_make(values: "List[const DateADT]") -> "Set *":
    values_converted = _ffi.new("const DateADT []", values)
    result = _lib.dateset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_make(
    lower: "DateADT", upper: "DateADT", lower_inc: bool, upper_inc: bool
) -> "Span *":
    lower_converted = _ffi.cast("DateADT", lower)
    upper_converted = _ffi.cast("DateADT", upper)
    result = _lib.datespan_make(lower_converted, upper_converted, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_make(values: "List[const double]") -> "Set *":
    values_converted = _ffi.new("const double []", values)
    result = _lib.floatset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_make(
    lower: float, upper: float, lower_inc: bool, upper_inc: bool
) -> "Span *":
    result = _lib.floatspan_make(lower, upper, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_make(values: "const GSERIALIZED **") -> "Set *":
    values_converted = [_ffi.cast("const GSERIALIZED *", x) for x in values]
    result = _lib.geoset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def intset_make(values: "List[const int]") -> "Set *":
    values_converted = _ffi.new("const int []", values)
    result = _lib.intset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> "Span *":
    result = _lib.intspan_make(lower, upper, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def set_copy(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_copy(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_copy(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_copy(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_copy(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_copy(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make(spans: "List[Span *]", normalize: bool, ordered: bool) -> "SpanSet *":
    spans_converted = _ffi.new("Span []", spans)
    result = _lib.spanset_make(spans_converted, len(spans), normalize, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_make(values: List[str]) -> "Set *":
    values_converted = [cstring2text(x) for x in values]
    result = _lib.textset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_make(values: List[int]) -> "Set *":
    values_converted = [_ffi.cast("const TimestampTz", x) for x in values]
    result = _lib.tstzset_make(values_converted, len(values))
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_make(lower: int, upper: int, lower_inc: bool, upper_inc: bool) -> "Span *":
    lower_converted = _ffi.cast("TimestampTz", lower)
    upper_converted = _ffi.cast("TimestampTz", upper)
    result = _lib.tstzspan_make(lower_converted, upper_converted, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_set(i: int) -> "Set *":
    i_converted = _ffi.cast("int64", i)
    result = _lib.bigint_to_set(i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_span(i: int) -> "Span *":
    result = _lib.bigint_to_span(i)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_to_spanset(i: int) -> "SpanSet *":
    result = _lib.bigint_to_spanset(i)
    _check_error()
    return result if result != _ffi.NULL else None


def date_to_set(d: "DateADT") -> "Set *":
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_to_set(d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def date_to_span(d: "DateADT") -> "Span *":
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_to_span(d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def date_to_spanset(d: "DateADT") -> "SpanSet *":
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_to_spanset(d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_to_tstzset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_to_tstzset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_to_tstzspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_to_tstzspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_to_tstzspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_to_tstzspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_set(d: float) -> "Set *":
    result = _lib.float_to_set(d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_span(d: float) -> "Span *":
    result = _lib.float_to_span(d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_spanset(d: float) -> "SpanSet *":
    result = _lib.float_to_spanset(d)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_to_intset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_to_intset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_to_intspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_to_intspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_to_intspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_to_intspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_to_set(gs: "GSERIALIZED *") -> "Set *":
    gs_converted = _ffi.cast("GSERIALIZED *", gs)
    result = _lib.geo_to_set(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_set(i: int) -> "Set *":
    result = _lib.int_to_set(i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_span(i: int) -> "Span *":
    result = _lib.int_to_span(i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_spanset(i: int) -> "SpanSet *":
    result = _lib.int_to_spanset(i)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_to_floatset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_to_floatset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_to_floatspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_to_floatspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_to_floatspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_to_floatspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_to_spanset(s: "const Set *") -> "SpanSet *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_to_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_to_spanset(s: "const Span *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_to_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text_to_set(txt: str) -> "Set *":
    txt_converted = cstring2text(txt)
    result = _lib.text_to_set(txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_to_set(t: int) -> "Set *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_set(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_to_span(t: int) -> "Span *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_span(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_to_spanset(t: int) -> "SpanSet *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_spanset(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_to_dateset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_to_dateset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_to_datespan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_to_datespan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_to_datespanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_to_datespanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_end_value(s: "const Set *") -> "int64":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.bigintset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_start_value(s: "const Set *") -> "int64":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.bigintset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_value_n(s: "const Set *", n: int) -> "int64":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("int64 *")
    result = _lib.bigintset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def bigintset_values(s: "const Set *") -> "int64 *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.bigintset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_lower(s: "const Span *") -> "int64":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.bigintspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_upper(s: "const Span *") -> "int64":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.bigintspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_width(s: "const Span *") -> "int64":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.bigintspan_width(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_lower(ss: "const SpanSet *") -> "int64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.bigintspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_upper(ss: "const SpanSet *") -> "int64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.bigintspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_width(ss: "const SpanSet *", boundspan: bool) -> "int64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.bigintspanset_width(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_end_value(s: "const Set *") -> "DateADT":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_start_value(s: "const Set *") -> "DateADT":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_value_n(s: "const Set *", n: int) -> "DateADT *":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("DateADT *")
    result = _lib.dateset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def dateset_values(s: "const Set *") -> "DateADT *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_duration(s: "const Span *") -> "Interval *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_duration(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_lower(s: "const Span *") -> "DateADT":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_upper(s: "const Span *") -> "DateADT":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_date_n(ss: "const SpanSet *", n: int) -> "DateADT *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    out_result = _ffi.new("DateADT *")
    result = _lib.datespanset_date_n(ss_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def datespanset_dates(ss: "const SpanSet *") -> "Tuple['DateADT *', 'int']":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    count = _ffi.new("int *")
    result = _lib.datespanset_dates(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def datespanset_duration(ss: "const SpanSet *", boundspan: bool) -> "Interval *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_duration(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_end_date(ss: "const SpanSet *") -> "DateADT":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_end_date(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_num_dates(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_num_dates(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_start_date(ss: "const SpanSet *") -> "DateADT":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_start_date(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_end_value(s: "const Set *") -> "double":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_start_value(s: "const Set *") -> "double":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_value_n(s: "const Set *", n: int) -> "double":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("double *")
    result = _lib.floatset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def floatset_values(s: "const Set *") -> "double *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_lower(s: "const Span *") -> "double":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_upper(s: "const Span *") -> "double":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_width(s: "const Span *") -> "double":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_width(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_lower(ss: "const SpanSet *") -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_upper(ss: "const SpanSet *") -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_width(ss: "const SpanSet *", boundspan: bool) -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_width(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_end_value(s: "const Set *") -> "GSERIALIZED *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.geoset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_srid(s: "const Set *") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.geoset_srid(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_start_value(s: "const Set *") -> "GSERIALIZED *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.geoset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_value_n(s: "const Set *", n: int) -> "GSERIALIZED **":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("GSERIALIZED **")
    result = _lib.geoset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def geoset_values(s: "const Set *") -> "GSERIALIZED **":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.geoset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_end_value(s: "const Set *") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_start_value(s: "const Set *") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_value_n(s: "const Set *", n: int) -> "int":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("int *")
    result = _lib.intset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def intset_values(s: "const Set *") -> "int *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_lower(s: "const Span *") -> "int":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_upper(s: "const Span *") -> "int":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_width(s: "const Span *") -> "int":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_width(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_lower(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_upper(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_width(ss: "const SpanSet *", boundspan: bool) -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_width(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def set_hash(s: "const Set *") -> "uint32":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_hash(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_hash_extended(s: "const Set *", seed: int) -> "uint64":
    s_converted = _ffi.cast("const Set *", s)
    seed_converted = _ffi.cast("uint64", seed)
    result = _lib.set_hash_extended(s_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_num_values(s: "const Set *") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_num_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_to_span(s: "const Set *") -> "Span *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_to_span(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_hash(s: "const Span *") -> "uint32":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_hash(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_hash_extended(s: "const Span *", seed: int) -> "uint64":
    s_converted = _ffi.cast("const Span *", s)
    seed_converted = _ffi.cast("uint64", seed)
    result = _lib.span_hash_extended(s_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_lower_inc(s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_lower_inc(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_upper_inc(s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_upper_inc(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_end_span(ss: "const SpanSet *") -> "Span *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_end_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_hash(ss: "const SpanSet *") -> "uint32":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_hash(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_hash_extended(ss: "const SpanSet *", seed: int) -> "uint64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    seed_converted = _ffi.cast("uint64", seed)
    result = _lib.spanset_hash_extended(ss_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_lower_inc(ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_lower_inc(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_num_spans(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_num_spans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_span(ss: "const SpanSet *") -> "Span *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_span_n(ss: "const SpanSet *", i: int) -> "Span *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_span_n(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_spans(ss: "const SpanSet *") -> "Span **":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_spans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_start_span(ss: "const SpanSet *") -> "Span *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_start_span(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_upper_inc(ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_upper_inc(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_end_value(s: "const Set *") -> str:
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_end_value(s_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def textset_start_value(s: "const Set *") -> str:
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_start_value(s_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def textset_value_n(s: "const Set *", n: int) -> "text **":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("text **")
    result = _lib.textset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def textset_values(s: "const Set *") -> "text **":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_end_value(s: "const Set *") -> "TimestampTz":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_start_value(s: "const Set *") -> "TimestampTz":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_value_n(s: "const Set *", n: int) -> int:
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.tstzset_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tstzset_values(s: "const Set *") -> "TimestampTz *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_duration(s: "const Span *") -> "Interval *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_duration(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_lower(s: "const Span *") -> "TimestampTz":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_upper(s: "const Span *") -> "TimestampTz":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_duration(ss: "const SpanSet *", boundspan: bool) -> "Interval *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_duration(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_end_timestamptz(ss: "const SpanSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_end_timestamptz(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_lower(ss: "const SpanSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_num_timestamps(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_num_timestamps(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_start_timestamptz(ss: "const SpanSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_start_timestamptz(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_timestamptz_n(ss: "const SpanSet *", n: int) -> int:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.tstzspanset_timestamptz_n(ss_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tstzspanset_timestamps(ss: "const SpanSet *") -> "Tuple['TimestampTz *', 'int']":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tstzspanset_timestamps(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tstzspanset_upper(ss: "const SpanSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigintset_shift_scale(
    s: "const Set *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    shift_converted = _ffi.cast("int64", shift)
    width_converted = _ffi.cast("int64", width)
    result = _lib.bigintset_shift_scale(
        s_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspan_shift_scale(
    s: "const Span *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    shift_converted = _ffi.cast("int64", shift)
    width_converted = _ffi.cast("int64", width)
    result = _lib.bigintspan_shift_scale(
        s_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def bigintspanset_shift_scale(
    ss: "const SpanSet *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    shift_converted = _ffi.cast("int64", shift)
    width_converted = _ffi.cast("int64", width)
    result = _lib.bigintspanset_shift_scale(
        ss_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_shift_scale(
    s: "const Set *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_shift_scale(
    s: "const Span *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_shift_scale(
    ss: "const SpanSet *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_shift_scale(
        ss_converted, shift, width, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_degrees(s: "const Set *", normalize: bool) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_degrees(s_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_radians(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_radians(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_round(s: "const Set *", maxdd: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_shift_scale(
    s: "const Set *", shift: float, width: float, hasshift: bool, haswidth: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_round(s: "const Span *", maxdd: int) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_shift_scale(
    s: "const Span *", shift: float, width: float, hasshift: bool, haswidth: bool
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_round(ss: "const SpanSet *", maxdd: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_round(ss_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_shift_scale(
    ss: "const SpanSet *", shift: float, width: float, hasshift: bool, haswidth: bool
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_shift_scale(
        ss_converted, shift, width, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_round(s: "const Set *", maxdd: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.geoset_round(s_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_set_srid(s: "const Set *", srid: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.geoset_set_srid(s_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_transform(s: "const Set *", srid: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.geoset_transform(s_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_transform_pipeline(
    s: "const Set *", pipelinestr: str, srid: int, is_forward: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    pipelinestr_converted = pipelinestr.encode("utf-8")
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.geoset_transform_pipeline(
        s_converted, pipelinestr_converted, srid_converted, is_forward
    )
    _check_error()
    return result if result != _ffi.NULL else None


def point_transform(gs: "const GSERIALIZED *", srid: int) -> "GSERIALIZED *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.point_transform(gs_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def point_transform_pipeline(
    gs: "const GSERIALIZED *", pipelinestr: str, srid: int, is_forward: bool
) -> "GSERIALIZED *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    pipelinestr_converted = pipelinestr.encode("utf-8")
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.point_transform_pipeline(
        gs_converted, pipelinestr_converted, srid_converted, is_forward
    )
    _check_error()
    return result if result != _ffi.NULL else None


def intset_shift_scale(
    s: "const Set *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_shift_scale(
    s: "const Span *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_shift_scale(s_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_shift_scale(
    ss: "const SpanSet *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_shift_scale(ss_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_initcap(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_initcap(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_lower(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_lower(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textset_upper(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textset_upper(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_textset_text(s: "const Set *", txt: str) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.textcat_textset_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_text_textset(txt: str, s: "const Set *") -> "Set *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.textcat_text_textset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_tprecision(
    t: int, duration: "const Interval *", torigin: int
) -> "TimestampTz":
    t_converted = _ffi.cast("TimestampTz", t)
    duration_converted = _ffi.cast("const Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.timestamptz_tprecision(
        t_converted, duration_converted, torigin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_shift_scale(
    s: "const Set *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.tstzset_shift_scale(s_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_tprecision(
    s: "const Set *", duration: "const Interval *", torigin: int
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    duration_converted = _ffi.cast("const Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.tstzset_tprecision(s_converted, duration_converted, torigin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_shift_scale(
    s: "const Span *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.tstzspan_shift_scale(s_converted, shift_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_tprecision(
    s: "const Span *", duration: "const Interval *", torigin: int
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    duration_converted = _ffi.cast("const Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.tstzspan_tprecision(
        s_converted, duration_converted, torigin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_shift_scale(
    ss: "const SpanSet *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.tstzspanset_shift_scale(
        ss_converted, shift_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_tprecision(
    ss: "const SpanSet *", duration: "const Interval *", torigin: int
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    duration_converted = _ffi.cast("const Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.tstzspanset_tprecision(
        ss_converted, duration_converted, torigin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def set_cmp(s1: "const Set *", s2: "const Set *") -> "int":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_cmp(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_eq(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_eq(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_ge(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_ge(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_gt(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_gt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_le(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_le(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_lt(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_lt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_ne(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_ne(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_cmp(s1: "const Span *", s2: "const Span *") -> "int":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_cmp(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_eq(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_eq(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_ge(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_ge(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_gt(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_gt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_le(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_le(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_lt(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_lt(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_ne(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_ne(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_cmp(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "int":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_cmp(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_eq(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_eq(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_ge(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_ge(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_gt(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_gt(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_le(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_le(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_lt(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_lt(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_ne(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_ne(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.adjacent_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.adjacent_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.adjacent_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.adjacent_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.adjacent_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.adjacent_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.adjacent_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.adjacent_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.adjacent_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.adjacent_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.adjacent_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.adjacent_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.adjacent_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.adjacent_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_set(i: int, s: "const Set *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_span(i: int, s: "const Span *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_bigint_spanset(i: int, ss: "const SpanSet *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_date_set(d: "DateADT", s: "const Set *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_date_span(d: "DateADT", s: "const Span *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_set(d: float, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_span(d: float, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_float_spanset(d: float, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_geo_set(gs: "GSERIALIZED *", s: "const Set *") -> "bool":
    gs_converted = _ffi.cast("GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_geo_set(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_set(i: int, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_span(i: int, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_int_spanset(i: int, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.contained_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.contained_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.contained_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_text_set(txt: str, s: "const Set *") -> "bool":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamptz_set(t: int, s: "const Set *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamptz_span(t: int, s: "const Span *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_bigint(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.contains_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_date(s: "const Set *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.contains_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_float(s: "const Set *", d: float) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contains_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_geo(s: "const Set *", gs: "GSERIALIZED *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    gs_converted = _ffi.cast("GSERIALIZED *", gs)
    result = _lib.contains_set_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_int(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contains_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.contains_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_text(s: "const Set *", t: str) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = cstring2text(t)
    result = _lib.contains_set_text(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_timestamptz(s: "const Set *", t: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.contains_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.contains_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.contains_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contains_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contains_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.contains_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contains_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.contains_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.contains_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.contains_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contains_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contains_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contains_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.contains_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.contains_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.overlaps_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.overlaps_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overlaps_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overlaps_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.overlaps_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_date_set(d: "DateADT", s: "const Set *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.after_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_date_span(d: "DateADT", s: "const Span *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.after_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.after_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_set_date(s: "const Set *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.after_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_set_timestamptz(s: "const Set *", t: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.after_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.after_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.after_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.after_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.after_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamptz_set(t: int, s: "const Set *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.after_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamptz_span(t: int, s: "const Span *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.after_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.after_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_date_set(d: "DateADT", s: "const Set *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.before_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_date_span(d: "DateADT", s: "const Span *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.before_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.before_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_set_date(s: "const Set *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.before_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_set_timestamptz(s: "const Set *", t: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.before_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.before_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.before_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.before_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.before_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamptz_set(t: int, s: "const Set *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.before_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamptz_span(t: int, s: "const Span *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.before_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.before_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_set(i: int, s: "const Set *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_span(i: int, s: "const Span *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_bigint_spanset(i: int, ss: "const SpanSet *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_set(d: float, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_span(d: float, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_float_spanset(d: float, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_set(i: int, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_span(i: int, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_int_spanset(i: int, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_bigint(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.left_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_float(s: "const Set *", d: float) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_int(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.left_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_text(s: "const Set *", txt: str) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.left_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.left_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.left_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.left_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.left_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_text_set(txt: str, s: "const Set *") -> "bool":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_date_set(d: "DateADT", s: "const Set *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overafter_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_date_span(d: "DateADT", s: "const Span *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overafter_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overafter_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_set_date(s: "const Set *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overafter_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_set_timestamptz(s: "const Set *", t: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overafter_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overafter_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overafter_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overafter_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overafter_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamptz_set(t: int, s: "const Set *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overafter_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamptz_span(t: int, s: "const Span *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overafter_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overafter_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_date_set(d: "DateADT", s: "const Set *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overbefore_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_date_span(d: "DateADT", s: "const Span *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overbefore_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "bool":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overbefore_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_set_date(s: "const Set *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overbefore_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_set_timestamptz(s: "const Set *", t: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overbefore_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_span_date(s: "const Span *", d: "DateADT") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overbefore_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_span_timestamptz(s: "const Span *", t: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overbefore_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.overbefore_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.overbefore_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamptz_set(t: int, s: "const Set *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overbefore_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamptz_span(t: int, s: "const Span *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overbefore_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "bool":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overbefore_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_set(i: int, s: "const Set *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_span(i: int, s: "const Span *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_bigint_spanset(i: int, ss: "const SpanSet *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_set(d: float, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_span(d: float, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_float_spanset(d: float, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_set(i: int, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_span(i: int, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_int_spanset(i: int, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_bigint(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overleft_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_float(s: "const Set *", d: float) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_int(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.overleft_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_text(s: "const Set *", txt: str) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.overleft_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overleft_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.overleft_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overleft_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.overleft_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_text_set(txt: str, s: "const Set *") -> "bool":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_set(i: int, s: "const Set *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_span(i: int, s: "const Span *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_bigint_spanset(i: int, ss: "const SpanSet *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_set(d: float, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_span(d: float, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_float_spanset(d: float, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_set(i: int, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_span(i: int, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_int_spanset(i: int, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_bigint(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overright_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_float(s: "const Set *", d: float) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_int(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.overright_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_text(s: "const Set *", txt: str) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.overright_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overright_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.overright_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.overright_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.overright_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_text_set(txt: str, s: "const Set *") -> "bool":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_set(i: int, s: "const Set *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_span(i: int, s: "const Span *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_bigint_spanset(i: int, ss: "const SpanSet *") -> "bool":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_set(d: float, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_span(d: float, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_float_spanset(d: float, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_set(i: int, s: "const Set *") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_span(i: int, s: "const Span *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_int_spanset(i: int, ss: "const SpanSet *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_bigint(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.right_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_float(s: "const Set *", d: float) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_int(s: "const Set *", i: int) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_set(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.right_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_text(s: "const Set *", txt: str) -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.right_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_bigint(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.right_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_float(s: "const Span *", d: float) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_int(s: "const Span *", i: int) -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.right_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_bigint(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.right_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_float(ss: "const SpanSet *", d: float) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_int(ss: "const SpanSet *", i: int) -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.right_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_text_set(txt: str, s: "const Set *") -> "bool":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_bigint_set(i: int, s: "const Set *") -> "Set *":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_date_set(d: "const DateADT", s: "const Set *") -> "Set *":
    d_converted = _ffi.cast("const DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_float_set(d: float, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_geo_set(gs: "const GSERIALIZED *", s: "const Set *") -> "Set *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_geo_set(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_int_set(i: int, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_bigint(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.intersection_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_date(s: "const Set *", d: "DateADT") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.intersection_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_float(s: "const Set *", d: float) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_geo(s: "const Set *", gs: "const GSERIALIZED *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.intersection_set_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_int(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_set(s1: "const Set *", s2: "const Set *") -> "Set *":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.intersection_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_text(s: "const Set *", txt: str) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.intersection_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_set_timestamptz(s: "const Set *", t: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.intersection_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_bigint(s: "const Span *", i: int) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.intersection_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_date(s: "const Span *", d: "DateADT") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.intersection_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_float(s: "const Span *", d: float) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intersection_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_int(s: "const Span *", i: int) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intersection_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_span(s1: "const Span *", s2: "const Span *") -> "Span *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.intersection_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intersection_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_timestamptz(s: "const Span *", t: int) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.intersection_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_bigint(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.intersection_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.intersection_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_float(ss: "const SpanSet *", d: float) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intersection_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_int(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intersection_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intersection_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_spanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "SpanSet *":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.intersection_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.intersection_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_text_set(txt: str, s: "const Set *") -> "Set *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_timestamptz_set(t: int, s: "const Set *") -> "Set *":
    t_converted = _ffi.cast("const TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_bigint_set(i: int, s: "const Set *") -> "Set *":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_bigint_span(i: int, s: "const Span *") -> "SpanSet *":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_bigint_span(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_bigint_spanset(i: int, ss: "const SpanSet *") -> "SpanSet *":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_date_set(d: "DateADT", s: "const Set *") -> "Set *":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_date_span(d: "DateADT", s: "const Span *") -> "SpanSet *":
    d_converted = _ffi.cast("DateADT", d)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_date_span(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_date_spanset(d: "DateADT", ss: "const SpanSet *") -> "SpanSet *":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_float_set(d: float, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_float_span(d: float, s: "const Span *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_float_span(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_float_spanset(d: float, ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_geo_set(gs: "const GSERIALIZED *", s: "const Set *") -> "Set *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_geo_set(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_int_set(i: int, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_int_span(i: int, s: "const Span *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_int_spanset(i: int, ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_bigint(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.minus_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_date(s: "const Set *", d: "DateADT") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.minus_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_float(s: "const Set *", d: float) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_geo(s: "const Set *", gs: "const GSERIALIZED *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.minus_set_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_int(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_set(s1: "const Set *", s2: "const Set *") -> "Set *":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.minus_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_text(s: "const Set *", txt: str) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.minus_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_set_timestamptz(s: "const Set *", t: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.minus_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_bigint(s: "const Span *", i: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.minus_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_date(s: "const Span *", d: "DateADT") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.minus_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_float(s: "const Span *", d: float) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_int(s: "const Span *", i: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_span(s1: "const Span *", s2: "const Span *") -> "SpanSet *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.minus_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_timestamptz(s: "const Span *", t: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.minus_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_bigint(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.minus_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.minus_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_float(ss: "const SpanSet *", d: float) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_int(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_spanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "SpanSet *":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.minus_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.minus_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_text_set(txt: str, s: "const Set *") -> "Set *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamptz_set(t: int, s: "const Set *") -> "Set *":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamptz_span(t: int, s: "const Span *") -> "SpanSet *":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_timestamptz_spanset(t: int, ss: "const SpanSet *") -> "SpanSet *":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigint_set(i: int, s: "const Set *") -> "Set *":
    i_converted = _ffi.cast("int64", i)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_bigint_set(i_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigint_span(s: "const Span *", i: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.union_bigint_span(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_bigint_spanset(i: int, ss: "SpanSet *") -> "SpanSet *":
    i_converted = _ffi.cast("int64", i)
    ss_converted = _ffi.cast("SpanSet *", ss)
    result = _lib.union_bigint_spanset(i_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_date_set(d: "const DateADT", s: "const Set *") -> "Set *":
    d_converted = _ffi.cast("const DateADT", d)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_date_set(d_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_date_span(s: "const Span *", d: "DateADT") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.union_date_span(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_date_spanset(d: "DateADT", ss: "SpanSet *") -> "SpanSet *":
    d_converted = _ffi.cast("DateADT", d)
    ss_converted = _ffi.cast("SpanSet *", ss)
    result = _lib.union_date_spanset(d_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_float_set(d: float, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_float_set(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_float_span(s: "const Span *", d: float) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_float_span(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_float_spanset(d: float, ss: "SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("SpanSet *", ss)
    result = _lib.union_float_spanset(d, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_geo_set(gs: "const GSERIALIZED *", s: "const Set *") -> "Set *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_geo_set(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_int_set(i: int, s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_int_set(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_int_span(i: int, s: "const Span *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_int_span(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_int_spanset(i: int, ss: "SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("SpanSet *", ss)
    result = _lib.union_int_spanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_bigint(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.union_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_date(s: "const Set *", d: "DateADT") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.union_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_float(s: "const Set *", d: float) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_geo(s: "const Set *", gs: "const GSERIALIZED *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.union_set_geo(s_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_int(s: "const Set *", i: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_set(s1: "const Set *", s2: "const Set *") -> "Set *":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.union_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_text(s: "const Set *", txt: str) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.union_set_text(s_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_timestamptz(s: "const Set *", t: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("const TimestampTz", t)
    result = _lib.union_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_bigint(s: "const Span *", i: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.union_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_date(s: "const Span *", d: "DateADT") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.union_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_float(s: "const Span *", d: float) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_int(s: "const Span *", i: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_span(s1: "const Span *", s2: "const Span *") -> "SpanSet *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.union_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_spanset(s: "const Span *", ss: "const SpanSet *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.union_span_spanset(s_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_timestamptz(s: "const Span *", t: int) -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.union_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_bigint(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.union_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.union_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_float(ss: "const SpanSet *", d: float) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.union_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_int(ss: "const SpanSet *", i: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.union_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_spanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "SpanSet *":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.union_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.union_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_text_set(txt: str, s: "const Set *") -> "Set *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_text_set(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_timestamptz_set(t: int, s: "const Set *") -> "Set *":
    t_converted = _ffi.cast("const TimestampTz", t)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_timestamptz_set(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_timestamptz_span(t: int, s: "const Span *") -> "SpanSet *":
    t_converted = _ffi.cast("TimestampTz", t)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_timestamptz_span(t_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_timestamptz_spanset(t: int, ss: "SpanSet *") -> "SpanSet *":
    t_converted = _ffi.cast("TimestampTz", t)
    ss_converted = _ffi.cast("SpanSet *", ss)
    result = _lib.union_timestamptz_spanset(t_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintset_bigintset(s1: "const Set *", s2: "const Set *") -> "int64":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_bigintset_bigintset(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintspan_bigintspan(s1: "const Span *", s2: "const Span *") -> "int64":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_bigintspan_bigintspan(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintspanset_bigintspan(
    ss: "const SpanSet *", s: "const Span *"
) -> "int64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_bigintspanset_bigintspan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_bigintspanset_bigintspanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "int64":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_bigintspanset_bigintspanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_dateset_dateset(s1: "const Set *", s2: "const Set *") -> "int":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_dateset_dateset(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_datespan_datespan(s1: "const Span *", s2: "const Span *") -> "int":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_datespan_datespan(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_datespanset_datespan(ss: "const SpanSet *", s: "const Span *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_datespanset_datespan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_datespanset_datespanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "int":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_datespanset_datespanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatset_floatset(s1: "const Set *", s2: "const Set *") -> "double":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_floatset_floatset(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatspan_floatspan(s1: "const Span *", s2: "const Span *") -> "double":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_floatspan_floatspan(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatspanset_floatspan(
    ss: "const SpanSet *", s: "const Span *"
) -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_floatspanset_floatspan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_floatspanset_floatspanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "double":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_floatspanset_floatspanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intset_intset(s1: "const Set *", s2: "const Set *") -> "int":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_intset_intset(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intspan_intspan(s1: "const Span *", s2: "const Span *") -> "int":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_intspan_intspan(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intspanset_intspan(ss: "const SpanSet *", s: "const Span *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_intspanset_intspan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_intspanset_intspanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "int":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_intspanset_intspanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_bigint(s: "const Set *", i: int) -> "int64":
    s_converted = _ffi.cast("const Set *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.distance_set_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_date(s: "const Set *", d: "DateADT") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.distance_set_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_float(s: "const Set *", d: float) -> "double":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.distance_set_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_int(s: "const Set *", i: int) -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.distance_set_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_timestamptz(s: "const Set *", t: int) -> "double":
    s_converted = _ffi.cast("const Set *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.distance_set_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_bigint(s: "const Span *", i: int) -> "int64":
    s_converted = _ffi.cast("const Span *", s)
    i_converted = _ffi.cast("int64", i)
    result = _lib.distance_span_bigint(s_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_date(s: "const Span *", d: "DateADT") -> "int":
    s_converted = _ffi.cast("const Span *", s)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.distance_span_date(s_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_float(s: "const Span *", d: float) -> "double":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_span_float(s_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_int(s: "const Span *", i: int) -> "int":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_span_int(s_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_timestamptz(s: "const Span *", t: int) -> "double":
    s_converted = _ffi.cast("const Span *", s)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.distance_span_timestamptz(s_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_bigint(ss: "const SpanSet *", i: int) -> "int64":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    i_converted = _ffi.cast("int64", i)
    result = _lib.distance_spanset_bigint(ss_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_date(ss: "const SpanSet *", d: "DateADT") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.distance_spanset_date(ss_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_float(ss: "const SpanSet *", d: float) -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.distance_spanset_float(ss_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_int(ss: "const SpanSet *", i: int) -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.distance_spanset_int(ss_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_timestamptz(ss: "const SpanSet *", t: int) -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.distance_spanset_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tstzset_tstzset(s1: "const Set *", s2: "const Set *") -> "double":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_tstzset_tstzset(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tstzspan_tstzspan(s1: "const Span *", s2: "const Span *") -> "double":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_tstzspan_tstzspan(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tstzspanset_tstzspan(ss: "const SpanSet *", s: "const Span *") -> "double":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_tstzspanset_tstzspan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tstzspanset_tstzspanset(
    ss1: "const SpanSet *", ss2: "const SpanSet *"
) -> "double":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_tstzspanset_tstzspanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_extent_transfn(state: "Span *", i: int) -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    i_converted = _ffi.cast("int64", i)
    result = _lib.bigint_extent_transfn(state_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bigint_union_transfn(state: "Set *", i: int) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    i_converted = _ffi.cast("int64", i)
    result = _lib.bigint_union_transfn(state_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def date_extent_transfn(state: "Span *", d: "DateADT") -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_extent_transfn(state_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def date_union_transfn(state: "Set *", d: "DateADT") -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    d_converted = _ffi.cast("DateADT", d)
    result = _lib.date_union_transfn(state_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_extent_transfn(state: "Span *", d: float) -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    result = _lib.float_extent_transfn(state_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def float_union_transfn(state: "Set *", d: float) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    result = _lib.float_union_transfn(state_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def int_extent_transfn(state: "Span *", i: int) -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    result = _lib.int_extent_transfn(state_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def int_union_transfn(state: "Set *", i: int) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    i_converted = _ffi.cast("int32", i)
    result = _lib.int_union_transfn(state_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_extent_transfn(state: "Span *", s: "const Set *") -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_extent_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_union_finalfn(state: "Set *") -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    result = _lib.set_union_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_union_transfn(state: "Set *", s: "Set *") -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    s_converted = _ffi.cast("Set *", s)
    result = _lib.set_union_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_extent_transfn(state: "Span *", s: "const Span *") -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_extent_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_union_transfn(state: "SpanSet *", s: "const Span *") -> "SpanSet *":
    state_converted = _ffi.cast("SpanSet *", state)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_union_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_extent_transfn(state: "Span *", ss: "const SpanSet *") -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_extent_transfn(state_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_union_finalfn(state: "SpanSet *") -> "SpanSet *":
    state_converted = _ffi.cast("SpanSet *", state)
    result = _lib.spanset_union_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_union_transfn(state: "SpanSet *", ss: "const SpanSet *") -> "SpanSet *":
    state_converted = _ffi.cast("SpanSet *", state)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_union_transfn(state_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def text_union_transfn(state: "Set *", txt: str) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    txt_converted = cstring2text(txt)
    result = _lib.text_union_transfn(state_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_extent_transfn(state: "Span *", t: int) -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_extent_transfn(state_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_union_transfn(state: "Set *", t: int) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_union_transfn(state_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_in(string: str) -> "TBox *":
    string_converted = string.encode("utf-8")
    result = _lib.tbox_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_out(box: "const TBox *", maxdd: int) -> str:
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_out(box_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tbox_from_wkb(wkb: bytes) -> "TBOX *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.tbox_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def tbox_from_hexwkb(hexwkb: str) -> "TBox *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.tbox_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_from_wkb(wkb: bytes) -> "STBOX *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.stbox_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def stbox_from_hexwkb(hexwkb: str) -> "STBox *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.stbox_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_as_wkb(box: "const TBox *", variant: int) -> bytes:
    box_converted = _ffi.cast("const TBox *", box)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.tbox_as_wkb(box_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def tbox_as_hexwkb(box: "const TBox *", variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast("const TBox *", box)
    variant_converted = _ffi.cast("uint8_t", variant)
    size = _ffi.new("size_t *")
    result = _lib.tbox_as_hexwkb(box_converted, variant_converted, size)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size[0]


def stbox_as_wkb(box: "const STBox *", variant: int) -> bytes:
    box_converted = _ffi.cast("const STBox *", box)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.stbox_as_wkb(box_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def stbox_as_hexwkb(box: "const STBox *", variant: int) -> "Tuple[str, 'size_t *']":
    box_converted = _ffi.cast("const STBox *", box)
    variant_converted = _ffi.cast("uint8_t", variant)
    size = _ffi.new("size_t *")
    result = _lib.stbox_as_hexwkb(box_converted, variant_converted, size)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size[0]


def stbox_in(string: str) -> "STBox *":
    string_converted = string.encode("utf-8")
    result = _lib.stbox_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_out(box: "const STBox *", maxdd: int) -> str:
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_out(box_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def float_tstzspan_to_tbox(d: float, s: "const Span *") -> "TBox *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.float_tstzspan_to_tbox(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_timestamptz_to_tbox(d: float, t: int) -> "TBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.float_timestamptz_to_tbox(d, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_tstzspan_to_stbox(gs: "const GSERIALIZED *", s: "const Span *") -> "STBox *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.geo_tstzspan_to_stbox(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_timestamptz_to_stbox(gs: "const GSERIALIZED *", t: int) -> "STBox *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.geo_timestamptz_to_stbox(gs_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_tstzspan_to_tbox(i: int, s: "const Span *") -> "TBox *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.int_tstzspan_to_tbox(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_timestamptz_to_tbox(i: int, t: int) -> "TBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.int_timestamptz_to_tbox(i, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_tstzspan_to_tbox(span: "const Span *", s: "const Span *") -> "TBox *":
    span_converted = _ffi.cast("const Span *", span)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.numspan_tstzspan_to_tbox(span_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_timestamptz_to_tbox(span: "const Span *", t: int) -> "TBox *":
    span_converted = _ffi.cast("const Span *", span)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.numspan_timestamptz_to_tbox(span_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_copy(box: "const STBox *") -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_copy(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_make(
    hasx: bool,
    hasz: bool,
    geodetic: bool,
    srid: int,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    zmin: float,
    zmax: float,
    s: "const Span *",
) -> "STBox *":
    srid_converted = _ffi.cast("int32", srid)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.stbox_make(
        hasx,
        hasz,
        geodetic,
        srid_converted,
        xmin,
        xmax,
        ymin,
        ymax,
        zmin,
        zmax,
        s_converted,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_copy(box: "const TBox *") -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_copy(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_make(s: "Optional['const Span *']", p: "Optional['const Span *']") -> "TBox *":
    s_converted = _ffi.cast("const Span *", s) if s is not None else _ffi.NULL
    p_converted = _ffi.cast("const Span *", p) if p is not None else _ffi.NULL
    result = _lib.tbox_make(s_converted, p_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_to_tbox(d: float) -> "TBox *":
    result = _lib.float_to_tbox(d)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_to_stbox(gs: "const GSERIALIZED *") -> "STBox *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geo_to_stbox(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def int_to_tbox(i: int) -> "TBox *":
    result = _lib.int_to_tbox(i)
    _check_error()
    return result if result != _ffi.NULL else None


def set_to_tbox(s: "const Set *") -> "TBox *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_to_tbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_to_tbox(s: "const Span *") -> "TBox *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_to_tbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_to_tbox(ss: "const SpanSet *") -> "TBox *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_to_tbox(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatialset_to_stbox(s: "const Set *") -> "STBox *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.spatialset_to_stbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_gbox(box: "const STBox *") -> "GBOX *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_to_gbox(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_box3d(box: "const STBox *") -> "BOX3D *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_to_box3d(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_geo(box: "const STBox *") -> "GSERIALIZED *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_to_geo(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_to_tstzspan(box: "const STBox *") -> "Span *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_to_tstzspan(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_to_intspan(box: "const TBox *") -> "Span *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_to_intspan(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_to_floatspan(box: "const TBox *") -> "Span *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_to_floatspan(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_to_tstzspan(box: "const TBox *") -> "Span *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_to_tstzspan(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_to_stbox(t: int) -> "STBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_stbox(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_to_tbox(t: int) -> "TBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_to_tbox(t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_to_stbox(s: "const Set *") -> "STBox *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_to_stbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_to_stbox(s: "const Span *") -> "STBox *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_to_stbox(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_to_stbox(ss: "const SpanSet *") -> "STBox *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_to_stbox(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_to_tbox(temp: "const Temporal *") -> "TBox *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_to_tbox(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_to_stbox(temp: "const Temporal *") -> "STBox *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_to_stbox(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hast(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_hast(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hasx(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_hasx(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_hasz(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_hasz(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_isgeodetic(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_isgeodetic(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_srid(box: "const STBox *") -> "int32":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_srid(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_tmax(box: "const STBox *") -> int:
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.stbox_tmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmax_inc(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.stbox_tmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmin(box: "const STBox *") -> int:
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.stbox_tmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_tmin_inc(box: "const STBox *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.stbox_tmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_xmax(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_xmin(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_ymax(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_ymax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_ymin(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_ymin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_zmax(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_zmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_zmin(box: "const STBox *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.stbox_zmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_hast(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_hast(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_hasx(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_hasx(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_tmax(box: "const TBox *") -> int:
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.tbox_tmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmax_inc(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.tbox_tmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmin(box: "const TBox *") -> int:
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.tbox_tmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_tmin_inc(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.tbox_tmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmax(box: "const TBox *") -> "double":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.tbox_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmax_inc(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.tbox_xmax_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmin(box: "const TBox *") -> "double":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.tbox_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbox_xmin_inc(box: "const TBox *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("bool *")
    result = _lib.tbox_xmin_inc(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tboxfloat_xmax(box: "const TBox *") -> "double":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.tboxfloat_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tboxfloat_xmin(box: "const TBox *") -> "double":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("double *")
    result = _lib.tboxfloat_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tboxint_xmax(box: "const TBox *") -> "int":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("int *")
    result = _lib.tboxint_xmax(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tboxint_xmin(box: "const TBox *") -> "int":
    box_converted = _ffi.cast("const TBox *", box)
    out_result = _ffi.new("int *")
    result = _lib.tboxint_xmin(box_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def stbox_expand_space(box: "const STBox *", d: float) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_expand_space(box_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_expand_time(box: "const STBox *", interv: "const Interval *") -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.stbox_expand_time(box_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_get_space(box: "const STBox *") -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_get_space(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_quad_split(box: "const STBox *") -> "Tuple['STBox *', 'int']":
    box_converted = _ffi.cast("const STBox *", box)
    count = _ffi.new("int *")
    result = _lib.stbox_quad_split(box_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def stbox_round(box: "const STBox *", maxdd: int) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_round(box_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_set_srid(box: "const STBox *", srid: int) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.stbox_set_srid(box_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_shift_scale_time(
    box: "const STBox *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.stbox_shift_scale_time(
        box_converted, shift_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_transform(box: "const STBox *", srid: int) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.stbox_transform(box_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_transform_pipeline(
    box: "const STBox *", pipelinestr: str, srid: int, is_forward: bool
) -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    pipelinestr_converted = pipelinestr.encode("utf-8")
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.stbox_transform_pipeline(
        box_converted, pipelinestr_converted, srid_converted, is_forward
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_expand_time(box: "const TBox *", interv: "const Interval *") -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tbox_expand_time(box_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_expand_float(box: "const TBox *", d: "const double") -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    d_converted = _ffi.cast("const double", d)
    result = _lib.tbox_expand_float(box_converted, d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_expand_int(box: "const TBox *", i: "const int") -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    i_converted = _ffi.cast("const int", i)
    result = _lib.tbox_expand_int(box_converted, i_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_round(box: "const TBox *", maxdd: int) -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_round(box_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_float(
    box: "const TBox *", shift: float, width: float, hasshift: bool, haswidth: bool
) -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_shift_scale_float(
        box_converted, shift, width, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_int(
    box: "const TBox *", shift: int, width: int, hasshift: bool, haswidth: bool
) -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_shift_scale_int(box_converted, shift, width, hasshift, haswidth)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_shift_scale_time(
    box: "const TBox *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.tbox_shift_scale_time(
        box_converted, shift_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def union_tbox_tbox(
    box1: "const TBox *", box2: "const TBox *", strict: bool
) -> "TBox *":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.union_tbox_tbox(box1_converted, box2_converted, strict)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "TBox *":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.intersection_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_stbox_stbox(
    box1: "const STBox *", box2: "const STBox *", strict: bool
) -> "STBox *":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.union_stbox_stbox(box1_converted, box2_converted, strict)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "STBox *":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.intersection_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.adjacent_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.adjacent_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.contained_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.contained_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.contains_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.contains_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.overlaps_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overlaps_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.same_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.same_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.left_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.overleft_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.right_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.overright_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.before_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.overbefore_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.after_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.overafter_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.left_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overleft_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.right_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overright_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def below_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.below_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbelow_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overbelow_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def above_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.above_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overabove_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overabove_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def front_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.front_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overfront_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overfront_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def back_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.back_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overback_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overback_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.before_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overbefore_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.after_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.overafter_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_eq(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_eq(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_ne(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_ne(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_cmp(box1: "const TBox *", box2: "const TBox *") -> "int":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_cmp(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_lt(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_lt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_le(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_le(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_ge(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_ge(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_gt(box1: "const TBox *", box2: "const TBox *") -> "bool":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.tbox_gt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_eq(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_eq(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_ne(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_ne(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_cmp(box1: "const STBox *", box2: "const STBox *") -> "int":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_cmp(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_lt(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_lt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_le(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_le(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_ge(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_ge(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_gt(box1: "const STBox *", box2: "const STBox *") -> "bool":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.stbox_gt(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tbool_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tfloat_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.ttext_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeompoint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpoint_in(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeogpoint_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tbool_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tint_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tfloat_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.ttext_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeompoint_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpoint_from_mfjson(string: str) -> "Temporal *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeogpoint_from_mfjson(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_wkb(wkb: bytes) -> "Temporal *":
    wkb_converted = _ffi.new("uint8_t []", wkb)
    result = _lib.temporal_from_wkb(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None


def temporal_from_hexwkb(hexwkb: str) -> "Temporal *":
    hexwkb_converted = hexwkb.encode("utf-8")
    result = _lib.temporal_from_hexwkb(hexwkb_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_out(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tint_out(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tfloat_out(temp: "const Temporal *", maxdd: int) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def ttext_out(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_out(temp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tpoint_out(temp: "const Temporal *", maxdd: int) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tpoint_as_text(temp: "const Temporal *", maxdd: int) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_as_text(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tpoint_as_ewkt(temp: "const Temporal *", maxdd: int) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_as_ewkt(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temporal_as_mfjson(
    temp: "const Temporal *",
    with_bbox: bool,
    flags: int,
    precision: int,
    srs: "Optional[str]",
) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    srs_converted = srs.encode("utf-8") if srs is not None else _ffi.NULL
    result = _lib.temporal_as_mfjson(
        temp_converted, with_bbox, flags, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temporal_as_wkb(temp: "const Temporal *", variant: int) -> bytes:
    temp_converted = _ffi.cast("const Temporal *", temp)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.temporal_as_wkb(temp_converted, variant_converted, size_out)
    _check_error()
    result_converted = (
        bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None
    )
    return result_converted


def temporal_as_hexwkb(
    temp: "const Temporal *", variant: int
) -> "Tuple[str, 'size_t *']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    variant_converted = _ffi.cast("uint8_t", variant)
    size_out = _ffi.new("size_t *")
    result = _lib.temporal_as_hexwkb(temp_converted, variant_converted, size_out)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None, size_out[0]


def tbool_from_base_temp(b: bool, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_from_base_temp(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_make(b: bool, t: int) -> "TInstant *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tboolinst_make(b, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_from_base_tstzset(b: bool, s: "const Set *") -> "TSequence *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tboolseq_from_base_tstzset(b, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_from_base_tstzspan(b: bool, s: "const Span *") -> "TSequence *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tboolseq_from_base_tstzspan(b, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_from_base_tstzspanset(
    b: bool, ss: "const SpanSet *"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tboolseqset_from_base_tstzspanset(b, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_copy(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_copy(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_from_base_temp(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_from_base_temp(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_make(d: float, t: int) -> "TInstant *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tfloatinst_make(d, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_tstzspan(
    d: float, s: "const Span *", interp: "interpType"
) -> "TSequence *":
    s_converted = _ffi.cast("const Span *", s)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tfloatseq_from_base_tstzspan(d, s_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_from_base_tstzset(d: float, s: "const Set *") -> "TSequence *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tfloatseq_from_base_tstzset(d, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_from_base_tstzspanset(
    d: float, ss: "const SpanSet *", interp: "interpType"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tfloatseqset_from_base_tstzspanset(d, ss_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_from_base_temp(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_from_base_temp(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintinst_make(i: int, t: int) -> "TInstant *":
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tintinst_make(i, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_from_base_tstzspan(i: int, s: "const Span *") -> "TSequence *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tintseq_from_base_tstzspan(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_from_base_tstzset(i: int, s: "const Set *") -> "TSequence *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tintseq_from_base_tstzset(i, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_from_base_tstzspanset(i: int, ss: "const SpanSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tintseqset_from_base_tstzspanset(i, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_from_base_temp(
    gs: "const GSERIALIZED *", temp: "const Temporal *"
) -> "Temporal *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_from_base_temp(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_make(gs: "const GSERIALIZED *", t: int) -> "TInstant *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tpointinst_make(gs_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_from_base_tstzspan(
    gs: "const GSERIALIZED *", s: "const Span *", interp: "interpType"
) -> "TSequence *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Span *", s)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tpointseq_from_base_tstzspan(
        gs_converted, s_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_from_base_tstzset(
    gs: "const GSERIALIZED *", s: "const Set *"
) -> "TSequence *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tpointseq_from_base_tstzset(gs_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_from_base_tstzspanset(
    gs: "const GSERIALIZED *", ss: "const SpanSet *", interp: "interpType"
) -> "TSequenceSet *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tpointseqset_from_base_tstzspanset(
        gs_converted, ss_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make(
    instants: "const TInstant **",
    count: int,
    lower_inc: bool,
    upper_inc: bool,
    interp: "interpType",
    normalize: bool,
) -> "TSequence *":
    instants_converted = [_ffi.cast("const TInstant *", x) for x in instants]
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_make(
        instants_converted, count, lower_inc, upper_inc, interp_converted, normalize
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make(
    sequences: "const TSequence **", count: int, normalize: bool
) -> "TSequenceSet *":
    sequences_converted = [_ffi.cast("const TSequence *", x) for x in sequences]
    result = _lib.tsequenceset_make(sequences_converted, count, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_gaps(
    instants: "const TInstant **",
    count: int,
    interp: "interpType",
    maxt: "Interval *",
    maxdist: float,
) -> "TSequenceSet *":
    instants_converted = [_ffi.cast("const TInstant *", x) for x in instants]
    interp_converted = _ffi.cast("interpType", interp)
    maxt_converted = _ffi.cast("Interval *", maxt)
    result = _lib.tsequenceset_make_gaps(
        instants_converted, count, interp_converted, maxt_converted, maxdist
    )
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_from_base_temp(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_from_base_temp(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextinst_make(txt: str, t: int) -> "TInstant *":
    txt_converted = cstring2text(txt)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.ttextinst_make(txt_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_from_base_tstzspan(txt: str, s: "const Span *") -> "TSequence *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.ttextseq_from_base_tstzspan(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_from_base_tstzset(txt: str, s: "const Set *") -> "TSequence *":
    txt_converted = cstring2text(txt)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.ttextseq_from_base_tstzset(txt_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_from_base_tstzspanset(
    txt: str, ss: "const SpanSet *"
) -> "TSequenceSet *":
    txt_converted = cstring2text(txt)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.ttextseqset_from_base_tstzspanset(txt_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tstzspan(temp: "const Temporal *") -> "Span *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_to_tstzspan(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_to_tint(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_to_tint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_to_tfloat(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_to_tfloat(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_to_span(temp: "const Temporal *") -> "Span *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_to_span(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_end_value(temp: "const Temporal *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_start_value(temp: "const Temporal *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_value_at_timestamptz(
    temp: "const Temporal *", t: int, strict: bool
) -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("bool *")
    result = _lib.tbool_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tbool_values(temp: "const Temporal *") -> "Tuple['bool *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tbool_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_duration(temp: "const Temporal *", boundspan: bool) -> "Interval *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_duration(temp_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_instant(temp: "const Temporal *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_end_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_sequence(temp: "const Temporal *") -> "TSequence *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_end_sequence(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_end_timestamptz(temp: "const Temporal *") -> "TimestampTz":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_end_timestamptz(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_hash(temp: "const Temporal *") -> "uint32":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_hash(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_instant_n(temp: "const Temporal *", n: int) -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_instant_n(temp_converted, n)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_instants(temp: "const Temporal *") -> "Tuple['TInstant **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_instants(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_interp(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_interp(temp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temporal_max_instant(temp: "const Temporal *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_max_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_min_instant(temp: "const Temporal *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_min_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_instants(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_num_instants(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_sequences(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_num_sequences(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_num_timestamps(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_num_timestamps(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_segments(temp: "const Temporal *") -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_segments(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_sequence_n(temp: "const Temporal *", i: int) -> "TSequence *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_sequence_n(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_sequences(temp: "const Temporal *") -> "Tuple['TSequence **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_sequences(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_lower_inc(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_lower_inc(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_upper_inc(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_upper_inc(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_start_instant(temp: "const Temporal *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_start_instant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_start_sequence(temp: "const Temporal *") -> "TSequence *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_start_sequence(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_start_timestamptz(temp: "const Temporal *") -> "TimestampTz":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_start_timestamptz(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_stops(
    temp: "const Temporal *", maxdist: float, minduration: "const Interval *"
) -> "TSequenceSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    minduration_converted = _ffi.cast("const Interval *", minduration)
    result = _lib.temporal_stops(temp_converted, maxdist, minduration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_subtype(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_subtype(temp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temporal_time(temp: "const Temporal *") -> "SpanSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_time(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_timestamptz_n(temp: "const Temporal *", n: int) -> int:
    temp_converted = _ffi.cast("const Temporal *", temp)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.temporal_timestamptz_n(temp_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def temporal_timestamps(temp: "const Temporal *") -> "Tuple['TimestampTz *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_timestamps(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tfloat_end_value(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_max_value(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_min_value(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_start_value(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_value_at_timestamptz(
    temp: "const Temporal *", t: int, strict: bool
) -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("double *")
    result = _lib.tfloat_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tfloat_values(temp: "const Temporal *") -> "Tuple['double *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tfloat_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tint_end_value(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_max_value(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_min_value(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_start_value(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_value_at_timestamptz(temp: "const Temporal *", t: int, strict: bool) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("int *")
    result = _lib.tint_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tint_values(temp: "const Temporal *") -> "Tuple['int *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tint_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tnumber_integral(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_integral(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_twavg(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_twavg(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_valuespans(temp: "const Temporal *") -> "SpanSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_valuespans(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_end_value(temp: "const Temporal *") -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_start_value(temp: "const Temporal *") -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_start_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_value_at_timestamptz(
    temp: "const Temporal *", t: int, strict: bool
) -> "GSERIALIZED **":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("GSERIALIZED **")
    result = _lib.tpoint_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tpoint_values(temp: "const Temporal *") -> "Tuple['GSERIALIZED **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tpoint_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def ttext_end_value(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_end_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_max_value(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_max_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_min_value(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_min_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_start_value(temp: "const Temporal *") -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_start_value(temp_converted)
    _check_error()
    result = text2cstring(result)
    return result if result != _ffi.NULL else None


def ttext_value_at_timestamptz(
    temp: "const Temporal *", t: int, strict: bool
) -> "text **":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("text **")
    result = _lib.ttext_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def ttext_values(temp: "const Temporal *") -> "Tuple['text **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.ttext_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def float_degrees(value: float, normalize: bool) -> "double":
    result = _lib.float_degrees(value, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_scale_time(
    temp: "const Temporal *", duration: "const Interval *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    duration_converted = _ffi.cast("const Interval *", duration)
    result = _lib.temporal_scale_time(temp_converted, duration_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_set_interp(temp: "const Temporal *", interp: "interpType") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.temporal_set_interp(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_shift_scale_time(
    temp: "const Temporal *",
    shift: "Optional['const Interval *']",
    duration: "Optional['const Interval *']",
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    shift_converted = (
        _ffi.cast("const Interval *", shift) if shift is not None else _ffi.NULL
    )
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    result = _lib.temporal_shift_scale_time(
        temp_converted, shift_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_shift_time(
    temp: "const Temporal *", shift: "const Interval *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    shift_converted = _ffi.cast("const Interval *", shift)
    result = _lib.temporal_shift_time(temp_converted, shift_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tinstant(temp: "const Temporal *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_to_tinstant(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tsequence(temp: "const Temporal *", interp_str: str) -> "TSequence *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    interp_str_converted = interp_str.encode("utf-8")
    result = _lib.temporal_to_tsequence(temp_converted, interp_str_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_to_tsequenceset(
    temp: "const Temporal *", interp_str: str
) -> "TSequenceSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    interp_str_converted = interp_str.encode("utf-8")
    result = _lib.temporal_to_tsequenceset(temp_converted, interp_str_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_degrees(temp: "const Temporal *", normalize: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_degrees(temp_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_radians(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_radians(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_round(temp: "const Temporal *", maxdd: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_round(temp_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_scale_value(temp: "const Temporal *", width: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_scale_value(temp_converted, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_shift_scale_value(
    temp: "const Temporal *", shift: float, width: float
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_shift_scale_value(temp_converted, shift, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_shift_value(temp: "const Temporal *", shift: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_shift_value(temp_converted, shift)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatarr_round(temp: "const Temporal **", count: int, maxdd: int) -> "Temporal **":
    temp_converted = [_ffi.cast("const Temporal *", x) for x in temp]
    result = _lib.tfloatarr_round(temp_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_scale_value(temp: "const Temporal *", width: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_scale_value(temp_converted, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_shift_scale_value(
    temp: "const Temporal *", shift: int, width: int
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_shift_scale_value(temp_converted, shift, width)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_shift_value(temp: "const Temporal *", shift: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_shift_value(temp_converted, shift)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_round(temp: "const Temporal *", maxdd: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_round(temp_converted, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_transform(temp: "const Temporal *", srid: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpoint_transform(temp_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_transform_pipeline(
    temp: "const Temporal *", pipelinestr: str, srid: int, is_forward: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    pipelinestr_converted = pipelinestr.encode("utf-8")
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpoint_transform_pipeline(
        temp_converted, pipelinestr_converted, srid_converted, is_forward
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointarr_round(temp: "const Temporal **", count: int, maxdd: int) -> "Temporal **":
    temp_converted = [_ffi.cast("const Temporal *", x) for x in temp]
    result = _lib.tpointarr_round(temp_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_append_tinstant(
    temp: "Temporal *",
    inst: "const TInstant *",
    maxdist: float,
    maxt: "Optional['Interval *']",
    expand: bool,
) -> "Temporal *":
    temp_converted = _ffi.cast("Temporal *", temp)
    inst_converted = _ffi.cast("const TInstant *", inst)
    maxt_converted = _ffi.cast("Interval *", maxt) if maxt is not None else _ffi.NULL
    result = _lib.temporal_append_tinstant(
        temp_converted, inst_converted, maxdist, maxt_converted, expand
    )
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_append_tsequence(
    temp: "Temporal *", seq: "const TSequence *", expand: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("Temporal *", temp)
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.temporal_append_tsequence(temp_converted, seq_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_tstzspan(
    temp: "const Temporal *", s: "const Span *", connect: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.temporal_delete_tstzspan(temp_converted, s_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_tstzspanset(
    temp: "const Temporal *", ss: "const SpanSet *", connect: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.temporal_delete_tstzspanset(temp_converted, ss_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_timestamptz(
    temp: "const Temporal *", t: int, connect: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.temporal_delete_timestamptz(temp_converted, t_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_delete_tstzset(
    temp: "const Temporal *", s: "const Set *", connect: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.temporal_delete_tstzset(temp_converted, s_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_insert(
    temp1: "const Temporal *", temp2: "const Temporal *", connect: bool
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_insert(temp1_converted, temp2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_merge(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_merge(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_merge_array(temparr: "Temporal **", count: int) -> "Temporal *":
    temparr_converted = [_ffi.cast("Temporal *", x) for x in temparr]
    result = _lib.temporal_merge_array(temparr_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_update(
    temp1: "const Temporal *", temp2: "const Temporal *", connect: bool
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_update(temp1_converted, temp2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_at_value(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_at_value(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_minus_value(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_minus_value(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_max(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_at_max(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_min(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_at_min(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_tstzspan(temp: "const Temporal *", s: "const Span *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.temporal_at_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_tstzspanset(
    temp: "const Temporal *", ss: "const SpanSet *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.temporal_at_tstzspanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_timestamptz(temp: "const Temporal *", t: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.temporal_at_timestamptz(temp_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_tstzset(temp: "const Temporal *", s: "const Set *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.temporal_at_tstzset(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_at_values(temp: "const Temporal *", set: "const Set *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.temporal_at_values(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_max(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_minus_max(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_min(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_minus_min(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_tstzspan(
    temp: "const Temporal *", s: "const Span *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.temporal_minus_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_tstzspanset(
    temp: "const Temporal *", ss: "const SpanSet *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.temporal_minus_tstzspanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_timestamptz(temp: "const Temporal *", t: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.temporal_minus_timestamptz(temp_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_tstzset(temp: "const Temporal *", s: "const Set *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.temporal_minus_tstzset(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_minus_values(temp: "const Temporal *", set: "const Set *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.temporal_minus_values(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_at_value(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_at_value(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_minus_value(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_minus_value(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_at_value(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_at_value(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_minus_value(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_minus_value(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_at_span(temp: "const Temporal *", span: "const Span *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    span_converted = _ffi.cast("const Span *", span)
    result = _lib.tnumber_at_span(temp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_at_spanset(temp: "const Temporal *", ss: "const SpanSet *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tnumber_at_spanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_at_tbox(temp: "const Temporal *", box: "const TBox *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tnumber_at_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_span(temp: "const Temporal *", span: "const Span *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    span_converted = _ffi.cast("const Span *", span)
    result = _lib.tnumber_minus_span(temp_converted, span_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_spanset(
    temp: "const Temporal *", ss: "const SpanSet *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tnumber_minus_spanset(temp_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_minus_tbox(temp: "const Temporal *", box: "const TBox *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tnumber_minus_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_geom_time(
    temp: "const Temporal *",
    gs: "const GSERIALIZED *",
    zspan: "Optional['const Span *']",
    period: "const Span *",
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = (
        _ffi.cast("const Span *", zspan) if zspan is not None else _ffi.NULL
    )
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpoint_at_geom_time(
        temp_converted, gs_converted, zspan_converted, period_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_stbox(
    temp: "const Temporal *", box: "const STBox *", border_inc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpoint_at_stbox(temp_converted, box_converted, border_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_at_value(temp: "const Temporal *", gs: "GSERIALIZED *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("GSERIALIZED *", gs)
    result = _lib.tpoint_at_value(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_geom_time(
    temp: "const Temporal *",
    gs: "const GSERIALIZED *",
    zspan: "Optional['const Span *']",
    period: "const Span *",
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = (
        _ffi.cast("const Span *", zspan) if zspan is not None else _ffi.NULL
    )
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpoint_minus_geom_time(
        temp_converted, gs_converted, zspan_converted, period_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_stbox(
    temp: "const Temporal *", box: "const STBox *", border_inc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpoint_minus_stbox(temp_converted, box_converted, border_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_minus_value(temp: "const Temporal *", gs: "GSERIALIZED *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("GSERIALIZED *", gs)
    result = _lib.tpoint_minus_value(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_at_value(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_at_value(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_minus_value(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ttext_minus_value(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_cmp(temp1: "const Temporal *", temp2: "const Temporal *") -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_cmp(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_eq(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_eq(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ge(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_ge(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_gt(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_gt(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_le(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_le(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_lt(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_lt(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_ne(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_ne(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_bool_tbool(b: bool, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_point_tpoint(
    gs: "const GSERIALIZED *", temp: "const Temporal *"
) -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tbool_bool(temp: "const Temporal *", b: bool) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_eq_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.always_eq_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_eq_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_eq_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_bool_tbool(b: bool, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_point_tpoint(
    gs: "const GSERIALIZED *", temp: "const Temporal *"
) -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tbool_bool(temp: "const Temporal *", b: bool) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_ne_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.always_ne_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_ne_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_ne_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_ge_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_ge_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_gt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_gt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_le_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_le_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.always_lt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.always_lt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_bool_tbool(b: bool, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_point_tpoint(gs: "const GSERIALIZED *", temp: "const Temporal *") -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tbool_bool(temp: "const Temporal *", b: bool) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_eq_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tpoint_point(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.ever_eq_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_eq_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_eq_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_ge_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_ge_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_gt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_gt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_le_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_le_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_lt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_lt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_bool_tbool(b: bool, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_float_tfloat(d: float, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_int_tint(i: int, temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_point_tpoint(gs: "const GSERIALIZED *", temp: "const Temporal *") -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tbool_bool(temp: "const Temporal *", b: bool) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_ne_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_text_ttext(txt: str, temp: "const Temporal *") -> "int":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tfloat_float(temp: "const Temporal *", d: float) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tpoint_point(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.ever_ne_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.ever_ne_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_ttext_text(temp: "const Temporal *", txt: str) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.ever_ne_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_bool_tbool(b: bool, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_point_tpoint(
    gs: "const GSERIALIZED *", temp: "const Temporal *"
) -> "Temporal *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tbool_bool(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tbool_tbool(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tfloat_tfloat(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_tfloat_tfloat(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.teq_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.teq_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_tint_tint(temp1: "const Temporal *", temp2: "const Temporal *") -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_tint_tint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.teq_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def teq_ttext_ttext(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.teq_ttext_ttext(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tge_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tge_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tge_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tge_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tge_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tge_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tge_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.tge_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tgt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tgt_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.tgt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tle_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tle_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tle_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tle_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tle_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tle_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tle_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.tle_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tlt_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tlt_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tlt_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tlt_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tlt_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tlt_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tlt_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.tlt_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_bool_tbool(b: bool, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_float_tfloat(d: float, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_float_tfloat(d, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_int_tint(i: int, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_int_tint(i, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_point_tpoint(
    gs: "const GSERIALIZED *", temp: "const Temporal *"
) -> "Temporal *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_point_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tbool_bool(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tbool_tbool(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tfloat_tfloat(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_tfloat_tfloat(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.tne_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tne_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_tint_tint(temp1: "const Temporal *", temp2: "const Temporal *") -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_tint_tint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.tne_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tne_ttext_ttext(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tne_ttext_ttext(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.adjacent_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.adjacent_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.adjacent_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.adjacent_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.adjacent_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.adjacent_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.adjacent_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.adjacent_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.adjacent_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.adjacent_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.adjacent_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contained_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contained_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contained_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contained_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.contained_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contained_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.contained_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contained_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contained_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contains_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contains_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contains_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contains_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contains_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contains_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.contains_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contains_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.contains_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.contains_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.contains_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overlaps_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overlaps_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overlaps_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overlaps_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overlaps_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overlaps_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.overlaps_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overlaps_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overlaps_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overlaps_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overlaps_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overlaps_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.same_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.same_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.same_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.same_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.same_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.same_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.same_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.same_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.same_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.same_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def same_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.same_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def above_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.above_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def above_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.above_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def above_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.above_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.after_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.after_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.after_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.after_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.after_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.after_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.after_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.after_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def after_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.after_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def back_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.back_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def back_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.back_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def back_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.back_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.before_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.before_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.before_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.before_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.before_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.before_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.before_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.before_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def before_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.before_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def below_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.below_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def below_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.below_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def below_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.below_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def front_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.front_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def front_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.front_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def front_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.front_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.left_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.left_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.left_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.left_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.left_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.left_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.left_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overabove_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overabove_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overabove_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overabove_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overabove_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overabove_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overafter_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overafter_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overafter_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overafter_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.overafter_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overafter_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overafter_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overafter_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overafter_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overafter_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overback_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overback_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overback_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overback_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overback_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overback_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overbefore_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overbefore_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_temporal_tstzspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overbefore_temporal_tstzspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_temporal_temporal(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overbefore_temporal_temporal(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.overbefore_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overbefore_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overbefore_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overbefore_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbefore_tstzspan_temporal(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overbefore_tstzspan_temporal(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbelow_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overbelow_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbelow_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overbelow_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overbelow_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overbelow_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overfront_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overfront_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overfront_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overfront_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overfront_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overfront_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overleft_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overleft_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overleft_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.overleft_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overleft_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overleft_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overleft_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overright_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overright_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.overright_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.overright_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overright_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.overright_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.overright_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_numspan_tnumber(s: "const Span *", temp: "const Temporal *") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.right_numspan_tnumber(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_stbox_tpoint(box: "const STBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const STBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.right_stbox_tpoint(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tbox_tnumber(box: "const TBox *", temp: "const Temporal *") -> "bool":
    box_converted = _ffi.cast("const TBox *", box)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.right_tbox_tnumber(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tnumber_numspan(temp: "const Temporal *", s: "const Span *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_tnumber_numspan(temp_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.right_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.right_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.right_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "bool":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.right_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_bool_tbool(b: bool, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tand_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_tbool_bool(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tand_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tand_tbool_tbool(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tand_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_when_true(temp: "const Temporal *") -> "SpanSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_when_true(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnot_tbool(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnot_tbool(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_bool_tbool(b: bool, temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tor_bool_tbool(b, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_tbool_bool(temp: "const Temporal *", b: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tor_tbool_bool(temp_converted, b)
    _check_error()
    return result if result != _ffi.NULL else None


def tor_tbool_tbool(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tor_tbool_tbool(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_float_tfloat(d: float, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.add_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_int_tint(i: int, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.add_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tfloat_float(tnumber: "const Temporal *", d: float) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.add_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tint_int(tnumber: "const Temporal *", i: int) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.add_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def add_tnumber_tnumber(
    tnumber1: "const Temporal *", tnumber2: "const Temporal *"
) -> "Temporal *":
    tnumber1_converted = _ffi.cast("const Temporal *", tnumber1)
    tnumber2_converted = _ffi.cast("const Temporal *", tnumber2)
    result = _lib.add_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_float_tfloat(d: float, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.div_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_int_tint(i: int, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.div_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tfloat_float(tnumber: "const Temporal *", d: float) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.div_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tint_int(tnumber: "const Temporal *", i: int) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.div_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def div_tnumber_tnumber(
    tnumber1: "const Temporal *", tnumber2: "const Temporal *"
) -> "Temporal *":
    tnumber1_converted = _ffi.cast("const Temporal *", tnumber1)
    tnumber2_converted = _ffi.cast("const Temporal *", tnumber2)
    result = _lib.div_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_float_tfloat(d: float, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.mult_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_int_tint(i: int, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.mult_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tfloat_float(tnumber: "const Temporal *", d: float) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.mult_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tint_int(tnumber: "const Temporal *", i: int) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.mult_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def mult_tnumber_tnumber(
    tnumber1: "const Temporal *", tnumber2: "const Temporal *"
) -> "Temporal *":
    tnumber1_converted = _ffi.cast("const Temporal *", tnumber1)
    tnumber2_converted = _ffi.cast("const Temporal *", tnumber2)
    result = _lib.mult_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_float_tfloat(d: float, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.sub_float_tfloat(d, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_int_tint(i: int, tnumber: "const Temporal *") -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.sub_int_tint(i, tnumber_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tfloat_float(tnumber: "const Temporal *", d: float) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.sub_tfloat_float(tnumber_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tint_int(tnumber: "const Temporal *", i: int) -> "Temporal *":
    tnumber_converted = _ffi.cast("const Temporal *", tnumber)
    result = _lib.sub_tint_int(tnumber_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def sub_tnumber_tnumber(
    tnumber1: "const Temporal *", tnumber2: "const Temporal *"
) -> "Temporal *":
    tnumber1_converted = _ffi.cast("const Temporal *", tnumber1)
    tnumber2_converted = _ffi.cast("const Temporal *", tnumber2)
    result = _lib.sub_tnumber_tnumber(tnumber1_converted, tnumber2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_derivative(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_derivative(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_abs(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_abs(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_angular_difference(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_angular_difference(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_delta_value(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_delta_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_text_ttext(txt: str, temp: "const Temporal *") -> "Temporal *":
    txt_converted = cstring2text(txt)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.textcat_text_ttext(txt_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_ttext_text(temp: "const Temporal *", txt: str) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    txt_converted = cstring2text(txt)
    result = _lib.textcat_ttext_text(temp_converted, txt_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_ttext_ttext(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.textcat_ttext_ttext(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_upper(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_upper(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_lower(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_lower(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_initcap(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_initcap(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tfloat_float(temp: "const Temporal *", d: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.distance_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tint_int(temp: "const Temporal *", i: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.distance_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.distance_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.distance_tpoint_point(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.distance_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_stbox_geo(box: "const STBox *", gs: "const GSERIALIZED *") -> "double":
    box_converted = _ffi.cast("const STBox *", box)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.nad_stbox_geo(box_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "double":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    result = _lib.nad_stbox_stbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tint_int(temp: "const Temporal *", i: int) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.nad_tint_int(temp_converted, i)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tint_tbox(temp: "const Temporal *", box: "const TBox *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.nad_tint_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tint_tint(temp1: "const Temporal *", temp2: "const Temporal *") -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.nad_tint_tint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tboxint_tboxint(box1: "const TBox *", box2: "const TBox *") -> "int":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.nad_tboxint_tboxint(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tfloat_float(temp: "const Temporal *", d: float) -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.nad_tfloat_float(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tfloat_tfloat(temp1: "const Temporal *", temp2: "const Temporal *") -> "double":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.nad_tfloat_tfloat(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tfloat_tbox(temp: "const Temporal *", box: "const TBox *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.nad_tfloat_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tboxfloat_tboxfloat(box1: "const TBox *", box2: "const TBox *") -> "double":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.nad_tboxfloat_tboxfloat(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.nad_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_stbox(temp: "const Temporal *", box: "const STBox *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.nad_tpoint_stbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tpoint_tpoint(temp1: "const Temporal *", temp2: "const Temporal *") -> "double":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.nad_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nai_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "TInstant *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.nai_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nai_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "TInstant *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.nai_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def shortestline_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.shortestline_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def shortestline_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "GSERIALIZED *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.shortestline_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bearing_point_point(
    gs1: "const GSERIALIZED *", gs2: "const GSERIALIZED *"
) -> "double":
    gs1_converted = _ffi.cast("const GSERIALIZED *", gs1)
    gs2_converted = _ffi.cast("const GSERIALIZED *", gs2)
    out_result = _ffi.new("double *")
    result = _lib.bearing_point_point(gs1_converted, gs2_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def bearing_tpoint_point(
    temp: "const Temporal *", gs: "const GSERIALIZED *", invert: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.bearing_tpoint_point(temp_converted, gs_converted, invert)
    _check_error()
    return result if result != _ffi.NULL else None


def bearing_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.bearing_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_angular_difference(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_angular_difference(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_azimuth(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_azimuth(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_convex_hull(temp: "const Temporal *") -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_convex_hull(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_cumulative_length(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_cumulative_length(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_direction(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    out_result = _ffi.new("double *")
    result = _lib.tpoint_direction(temp_converted, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tpoint_get_x(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_get_x(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_y(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_get_y(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_z(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_get_z(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_is_simple(temp: "const Temporal *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_is_simple(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_length(temp: "const Temporal *") -> "double":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_length(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_speed(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_speed(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_srid(temp: "const Temporal *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_srid(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_stboxes(temp: "const Temporal *") -> "Tuple['STBox *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tpoint_stboxes(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_trajectory(temp: "const Temporal *") -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_trajectory(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_twcentroid(temp: "const Temporal *") -> "GSERIALIZED *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_twcentroid(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_expand_space(gs: "const GSERIALIZED *", d: float) -> "STBox *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geo_expand_space(gs_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def geomeas_to_tpoint(gs: "const GSERIALIZED *") -> "Temporal *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.geomeas_to_tpoint(gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpoint_to_tgeompoint(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgeogpoint_to_tgeompoint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_to_tgeogpoint(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgeompoint_to_tgeogpoint(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_AsMVTGeom(
    temp: "const Temporal *",
    bounds: "const STBox *",
    extent: "int32_t",
    buffer: "int32_t",
    clip_geom: bool,
    gsarr: "GSERIALIZED **",
    timesarr: "int64 **",
) -> "Tuple['bool', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    bounds_converted = _ffi.cast("const STBox *", bounds)
    extent_converted = _ffi.cast("int32_t", extent)
    buffer_converted = _ffi.cast("int32_t", buffer)
    gsarr_converted = [_ffi.cast("GSERIALIZED *", x) for x in gsarr]
    timesarr_converted = [_ffi.cast("int64 *", x) for x in timesarr]
    count = _ffi.new("int *")
    result = _lib.tpoint_AsMVTGeom(
        temp_converted,
        bounds_converted,
        extent_converted,
        buffer_converted,
        clip_geom,
        gsarr_converted,
        timesarr_converted,
        count,
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_expand_space(temp: "const Temporal *", d: float) -> "STBox *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_expand_space(temp_converted, d)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_make_simple(temp: "const Temporal *") -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.tpoint_make_simple(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_set_srid(temp: "const Temporal *", srid: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpoint_set_srid(temp_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_tfloat_to_geomeas(
    tpoint: "const Temporal *", measure: "const Temporal *", segmentize: bool
) -> "GSERIALIZED **":
    tpoint_converted = _ffi.cast("const Temporal *", tpoint)
    measure_converted = _ffi.cast("const Temporal *", measure)
    out_result = _ffi.new("GSERIALIZED **")
    result = _lib.tpoint_tfloat_to_geomeas(
        tpoint_converted, measure_converted, segmentize, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def acontains_geo_tpoint(gs: "const GSERIALIZED *", temp: "const Temporal *") -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.acontains_geo_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adisjoint_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.adisjoint_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adisjoint_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.adisjoint_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adwithin_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *", dist: float
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.adwithin_tpoint_geo(temp_converted, gs_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def adwithin_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *", dist: float
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.adwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def aintersects_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.aintersects_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def aintersects_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.aintersects_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def atouches_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.atouches_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def econtains_geo_tpoint(gs: "const GSERIALIZED *", temp: "const Temporal *") -> "int":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.econtains_geo_tpoint(gs_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.edisjoint_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edisjoint_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.edisjoint_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def edwithin_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *", dist: float
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.edwithin_tpoint_geo(temp_converted, gs_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def edwithin_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *", dist: float
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.edwithin_tpoint_tpoint(temp1_converted, temp2_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def eintersects_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *"
) -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.eintersects_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def eintersects_tpoint_tpoint(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "int":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.eintersects_tpoint_tpoint(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def etouches_tpoint_geo(temp: "const Temporal *", gs: "const GSERIALIZED *") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.etouches_tpoint_geo(temp_converted, gs_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tcontains_geo_tpoint(
    gs: "const GSERIALIZED *", temp: "const Temporal *", restr: bool, atvalue: bool
) -> "Temporal *":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tcontains_geo_tpoint(gs_converted, temp_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tdisjoint_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *", restr: bool, atvalue: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.tdisjoint_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_geo(
    temp: "const Temporal *",
    gs: "const GSERIALIZED *",
    dist: float,
    restr: bool,
    atvalue: bool,
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.tdwithin_tpoint_geo(
        temp_converted, gs_converted, dist, restr, atvalue
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tdwithin_tpoint_tpoint(
    temp1: "const Temporal *",
    temp2: "const Temporal *",
    dist: float,
    restr: bool,
    atvalue: bool,
) -> "Temporal *":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.tdwithin_tpoint_tpoint(
        temp1_converted, temp2_converted, dist, restr, atvalue
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tintersects_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *", restr: bool, atvalue: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.tintersects_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def ttouches_tpoint_geo(
    temp: "const Temporal *", gs: "const GSERIALIZED *", restr: bool, atvalue: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    result = _lib.ttouches_tpoint_geo(temp_converted, gs_converted, restr, atvalue)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_tand_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_tand_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbool_tor_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tbool_tor_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_extent_transfn(s: "Span *", temp: "const Temporal *") -> "Span *":
    s_converted = _ffi.cast("Span *", s)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_extent_transfn(s_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tagg_finalfn(state: "SkipList *") -> "Temporal *":
    state_converted = _ffi.cast("SkipList *", state)
    result = _lib.temporal_tagg_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tcount_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_tcount_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tmax_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tmin_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_tsum_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tfloat_tsum_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_wmax_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tfloat_wmax_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_wmin_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tfloat_wmin_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloat_wsum_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tfloat_wsum_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timestamptz_tcount_transfn(state: "Optional['SkipList *']", t: int) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.timestamptz_tcount_transfn(state_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tmax_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tmin_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_tsum_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tint_tsum_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_wmax_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tint_wmax_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_wmin_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tint_wmin_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tint_wsum_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tint_wsum_transfn(state_converted, temp_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_extent_transfn(
    box: "Optional['TBox *']", temp: "const Temporal *"
) -> "TBox *":
    box_converted = _ffi.cast("TBox *", box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_extent_transfn(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_tavg_finalfn(state: "SkipList *") -> "Temporal *":
    state_converted = _ffi.cast("SkipList *", state)
    result = _lib.tnumber_tavg_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_tavg_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_tavg_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_wavg_transfn(
    state: "SkipList *", temp: "const Temporal *", interv: "const Interval *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("const Temporal *", temp)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tnumber_wavg_transfn(
        state_converted, temp_converted, interv_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_extent_transfn(
    box: "Optional['STBox *']", temp: "const Temporal *"
) -> "STBox *":
    box_converted = _ffi.cast("STBox *", box) if box is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_extent_transfn(box_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_tcentroid_finalfn(state: "SkipList *") -> "Temporal *":
    state_converted = _ffi.cast("SkipList *", state)
    result = _lib.tpoint_tcentroid_finalfn(state_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_tcentroid_transfn(state: "SkipList *", temp: "Temporal *") -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state)
    temp_converted = _ffi.cast("Temporal *", temp)
    result = _lib.tpoint_tcentroid_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_tcount_transfn(
    state: "Optional['SkipList *']", s: "const Set *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_tcount_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_tcount_transfn(
    state: "Optional['SkipList *']", s: "const Span *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_tcount_transfn(state_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_tcount_transfn(
    state: "Optional['SkipList *']", ss: "const SpanSet *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_tcount_transfn(state_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_tmax_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_tmax_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttext_tmin_transfn(
    state: "Optional['SkipList *']", temp: "const Temporal *"
) -> "SkipList *":
    state_converted = _ffi.cast("SkipList *", state) if state is not None else _ffi.NULL
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ttext_tmin_transfn(state_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_dp(
    temp: "const Temporal *", eps_dist: float, synchronized: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_simplify_dp(temp_converted, eps_dist, synchronized)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_max_dist(
    temp: "const Temporal *", eps_dist: float, synchronized: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_simplify_max_dist(temp_converted, eps_dist, synchronized)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_min_dist(temp: "const Temporal *", dist: float) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_simplify_min_dist(temp_converted, dist)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_simplify_min_tdelta(
    temp: "const Temporal *", mint: "const Interval *"
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    mint_converted = _ffi.cast("const Interval *", mint)
    result = _lib.temporal_simplify_min_tdelta(temp_converted, mint_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tprecision(
    temp: "const Temporal *", duration: "const Interval *", origin: int
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    duration_converted = _ffi.cast("const Interval *", duration)
    origin_converted = _ffi.cast("TimestampTz", origin)
    result = _lib.temporal_tprecision(
        temp_converted, duration_converted, origin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tsample(
    temp: "const Temporal *", duration: "const Interval *", origin: int
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    duration_converted = _ffi.cast("const Interval *", duration)
    origin_converted = _ffi.cast("TimestampTz", origin)
    result = _lib.temporal_tsample(temp_converted, duration_converted, origin_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_dyntimewarp_distance(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "double":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_dyntimewarp_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_dyntimewarp_path(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    count = _ffi.new("int *")
    result = _lib.temporal_dyntimewarp_path(temp1_converted, temp2_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_frechet_distance(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "double":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_frechet_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_frechet_path(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Tuple['Match *', 'int']":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    count = _ffi.new("int *")
    result = _lib.temporal_frechet_path(temp1_converted, temp2_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_hausdorff_distance(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "double":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.temporal_hausdorff_distance(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_bucket(value: float, size: float, origin: float) -> "double":
    result = _lib.float_bucket(value, size, origin)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_bucket_list(
    bounds: "const Span *", size: float, origin: float
) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast("const Span *", bounds)
    count = _ffi.new("int *")
    result = _lib.floatspan_bucket_list(bounds_converted, size, origin, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def int_bucket(value: int, size: int, origin: int) -> "int":
    result = _lib.int_bucket(value, size, origin)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_bucket_list(
    bounds: "const Span *", size: int, origin: int
) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast("const Span *", bounds)
    count = _ffi.new("int *")
    result = _lib.intspan_bucket_list(bounds_converted, size, origin, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def stbox_tile(
    point: "GSERIALIZED *",
    t: int,
    xsize: float,
    ysize: float,
    zsize: float,
    duration: "Interval *",
    sorigin: "GSERIALIZED *",
    torigin: int,
    hast: bool,
) -> "STBox *":
    point_converted = _ffi.cast("GSERIALIZED *", point)
    t_converted = _ffi.cast("TimestampTz", t)
    duration_converted = _ffi.cast("Interval *", duration)
    sorigin_converted = _ffi.cast("GSERIALIZED *", sorigin)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.stbox_tile(
        point_converted,
        t_converted,
        xsize,
        ysize,
        zsize,
        duration_converted,
        sorigin_converted,
        torigin_converted,
        hast,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_tile_list(
    bounds: "const STBox *",
    xsize: float,
    ysize: float,
    zsize: float,
    duration: "Optional['const Interval *']",
    sorigin: "GSERIALIZED *",
    torigin: int,
) -> "Tuple['STBox *', 'int']":
    bounds_converted = _ffi.cast("const STBox *", bounds)
    duration_converted = (
        _ffi.cast("const Interval *", duration) if duration is not None else _ffi.NULL
    )
    sorigin_converted = _ffi.cast("GSERIALIZED *", sorigin)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    count = _ffi.new("int *")
    result = _lib.stbox_tile_list(
        bounds_converted,
        xsize,
        ysize,
        zsize,
        duration_converted,
        sorigin_converted,
        torigin_converted,
        count,
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_time_split(
    temp: "Temporal *", duration: "Interval *", torigin: int
) -> "Tuple['Temporal **', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    duration_converted = _ffi.cast("Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    time_buckets = _ffi.new("TimestampTz **")
    count = _ffi.new("int *")
    result = _lib.temporal_time_split(
        temp_converted, duration_converted, torigin_converted, time_buckets, count
    )
    _check_error()
    return result if result != _ffi.NULL else None, time_buckets[0], count[0]


def tfloat_value_split(
    temp: "Temporal *", size: float, origin: float
) -> "Tuple['Temporal **', 'double *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    value_buckets = _ffi.new("double **")
    count = _ffi.new("int *")
    result = _lib.tfloat_value_split(temp_converted, size, origin, value_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], count[0]


def tfloat_value_time_split(
    temp: "Temporal *",
    size: float,
    duration: "Interval *",
    vorigin: float,
    torigin: int,
) -> "Tuple['Temporal **', 'double *', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    duration_converted = _ffi.cast("Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    value_buckets = _ffi.new("double **")
    time_buckets = _ffi.new("TimestampTz **")
    count = _ffi.new("int *")
    result = _lib.tfloat_value_time_split(
        temp_converted,
        size,
        duration_converted,
        vorigin,
        torigin_converted,
        value_buckets,
        time_buckets,
        count,
    )
    _check_error()
    return (
        result if result != _ffi.NULL else None,
        value_buckets[0],
        time_buckets[0],
        count[0],
    )


def tpoint_space_split(
    temp: "Temporal *",
    xsize: "float",
    ysize: "float",
    zsize: "float",
    sorigin: "GSERIALIZED *",
    bitmatrix: bool,
) -> "Tuple['Temporal **', 'GSERIALIZED ***', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    xsize_converted = _ffi.cast("float", xsize)
    ysize_converted = _ffi.cast("float", ysize)
    zsize_converted = _ffi.cast("float", zsize)
    sorigin_converted = _ffi.cast("GSERIALIZED *", sorigin)
    space_buckets = _ffi.new("GSERIALIZED ***")
    count = _ffi.new("int *")
    result = _lib.tpoint_space_split(
        temp_converted,
        xsize_converted,
        ysize_converted,
        zsize_converted,
        sorigin_converted,
        bitmatrix,
        space_buckets,
        count,
    )
    _check_error()
    return result if result != _ffi.NULL else None, space_buckets[0], count[0]


def tfloatbox_tile(
    value: float,
    t: int,
    vsize: float,
    duration: "Interval *",
    vorigin: float,
    torigin: int,
) -> "TBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    duration_converted = _ffi.cast("Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.tfloatbox_tile(
        value, t_converted, vsize, duration_converted, vorigin, torigin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatbox_tile_list(
    box: "const TBox *",
    xsize: float,
    duration: "const Interval *",
    xorigin: "Optional[float]",
    torigin: "Optional[int]",
) -> "Tuple['TBox *', 'int']":
    box_converted = _ffi.cast("const TBox *", box)
    duration_converted = _ffi.cast("const Interval *", duration)
    xorigin_converted = xorigin if xorigin is not None else _ffi.NULL
    torigin_converted = (
        _ffi.cast("TimestampTz", torigin) if torigin is not None else _ffi.NULL
    )
    count = _ffi.new("int *")
    result = _lib.tfloatbox_tile_list(
        box_converted,
        xsize,
        duration_converted,
        xorigin_converted,
        torigin_converted,
        count,
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def timestamptz_bucket(
    timestamp: int, duration: "const Interval *", origin: int
) -> "TimestampTz":
    timestamp_converted = _ffi.cast("TimestampTz", timestamp)
    duration_converted = _ffi.cast("const Interval *", duration)
    origin_converted = _ffi.cast("TimestampTz", origin)
    result = _lib.timestamptz_bucket(
        timestamp_converted, duration_converted, origin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tint_value_split(
    temp: "Temporal *", size: int, origin: int
) -> "Tuple['Temporal **', 'int *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    value_buckets = _ffi.new("int **")
    count = _ffi.new("int *")
    result = _lib.tint_value_split(temp_converted, size, origin, value_buckets, count)
    _check_error()
    return result if result != _ffi.NULL else None, value_buckets[0], count[0]


def tint_value_time_split(
    temp: "Temporal *", size: int, duration: "Interval *", vorigin: int, torigin: int
) -> "Tuple['Temporal **', 'int *', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    duration_converted = _ffi.cast("Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    value_buckets = _ffi.new("int **")
    time_buckets = _ffi.new("TimestampTz **")
    count = _ffi.new("int *")
    result = _lib.tint_value_time_split(
        temp_converted,
        size,
        duration_converted,
        vorigin,
        torigin_converted,
        value_buckets,
        time_buckets,
        count,
    )
    _check_error()
    return (
        result if result != _ffi.NULL else None,
        value_buckets[0],
        time_buckets[0],
        count[0],
    )


def tintbox_tile(
    value: int, t: int, vsize: int, duration: "Interval *", vorigin: int, torigin: int
) -> "TBox *":
    t_converted = _ffi.cast("TimestampTz", t)
    duration_converted = _ffi.cast("Interval *", duration)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    result = _lib.tintbox_tile(
        value, t_converted, vsize, duration_converted, vorigin, torigin_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tintbox_tile_list(
    box: "const TBox *",
    xsize: int,
    duration: "const Interval *",
    xorigin: "Optional[int]",
    torigin: "Optional[int]",
) -> "Tuple['TBox *', 'int']":
    box_converted = _ffi.cast("const TBox *", box)
    duration_converted = _ffi.cast("const Interval *", duration)
    xorigin_converted = xorigin if xorigin is not None else _ffi.NULL
    torigin_converted = (
        _ffi.cast("TimestampTz", torigin) if torigin is not None else _ffi.NULL
    )
    count = _ffi.new("int *")
    result = _lib.tintbox_tile_list(
        box_converted,
        xsize,
        duration_converted,
        xorigin_converted,
        torigin_converted,
        count,
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpoint_space_time_split(
    temp: "Temporal *",
    xsize: "float",
    ysize: "float",
    zsize: "float",
    duration: "Interval *",
    sorigin: "GSERIALIZED *",
    torigin: int,
    bitmatrix: bool,
) -> "Tuple['Temporal **', 'GSERIALIZED ***', 'TimestampTz *', 'int']":
    temp_converted = _ffi.cast("Temporal *", temp)
    xsize_converted = _ffi.cast("float", xsize)
    ysize_converted = _ffi.cast("float", ysize)
    zsize_converted = _ffi.cast("float", zsize)
    duration_converted = _ffi.cast("Interval *", duration)
    sorigin_converted = _ffi.cast("GSERIALIZED *", sorigin)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    space_buckets = _ffi.new("GSERIALIZED ***")
    time_buckets = _ffi.new("TimestampTz **")
    count = _ffi.new("int *")
    result = _lib.tpoint_space_time_split(
        temp_converted,
        xsize_converted,
        ysize_converted,
        zsize_converted,
        duration_converted,
        sorigin_converted,
        torigin_converted,
        bitmatrix,
        space_buckets,
        time_buckets,
        count,
    )
    _check_error()
    return (
        result if result != _ffi.NULL else None,
        space_buckets[0],
        time_buckets[0],
        count[0],
    )


def tstzspan_bucket_list(
    bounds: "const Span *", duration: "const Interval *", origin: int
) -> "Tuple['Span *', 'int']":
    bounds_converted = _ffi.cast("const Span *", bounds)
    duration_converted = _ffi.cast("const Interval *", duration)
    origin_converted = _ffi.cast("TimestampTz", origin)
    count = _ffi.new("int *")
    result = _lib.tstzspan_bucket_list(
        bounds_converted, duration_converted, origin_converted, count
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temptype_subtype(subtype: "tempSubtype") -> "bool":
    subtype_converted = _ffi.cast("tempSubtype", subtype)
    result = _lib.temptype_subtype(subtype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temptype_subtype_all(subtype: "tempSubtype") -> "bool":
    subtype_converted = _ffi.cast("tempSubtype", subtype)
    result = _lib.temptype_subtype_all(subtype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tempsubtype_name(subtype: "tempSubtype") -> str:
    subtype_converted = _ffi.cast("tempSubtype", subtype)
    result = _lib.tempsubtype_name(subtype_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tempsubtype_from_string(string: str, subtype: "int16 *") -> "bool":
    string_converted = string.encode("utf-8")
    subtype_converted = _ffi.cast("int16 *", subtype)
    result = _lib.tempsubtype_from_string(string_converted, subtype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meosoper_name(oper: "meosOper") -> str:
    oper_converted = _ffi.cast("meosOper", oper)
    result = _lib.meosoper_name(oper_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def meosoper_from_string(name: str) -> "meosOper":
    name_converted = name.encode("utf-8")
    result = _lib.meosoper_from_string(name_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def interptype_name(interp: "interpType") -> str:
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.interptype_name(interp_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def interptype_from_string(interp_str: str) -> "interpType":
    interp_str_converted = interp_str.encode("utf-8")
    result = _lib.interptype_from_string(interp_str_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meostype_name(type: "meosType") -> str:
    type_converted = _ffi.cast("meosType", type)
    result = _lib.meostype_name(type_converted)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temptype_basetype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.temptype_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def settype_basetype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.settype_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spantype_basetype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spantype_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spantype_spansettype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spantype_spansettype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spansettype_spantype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spansettype_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_spantype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.basetype_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_settype(type: "meosType") -> "meosType":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.basetype_settype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def meos_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.meos_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alpha_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.alpha_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alphanum_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.alphanum_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.geo_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatial_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spatial_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def time_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.time_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.set_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.set_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.numset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_numset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_numset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timeset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.timeset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_timeset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_timeset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_spantype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.set_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_set_spantype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_set_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def alphanumset_type(settype: "meosType") -> "bool":
    settype_converted = _ffi.cast("meosType", settype)
    result = _lib.alphanumset_type(settype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.geoset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_geoset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_geoset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spatialset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spatialset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_spatialset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_spatialset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.span_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_canon_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.span_canon_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.span_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_bbox_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.span_bbox_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.numspan_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.numspan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_numspan_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_numspan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespan_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.timespan_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespan_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.timespan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_timespan_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_timespan_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.spanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.numspanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def timespanset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.timespanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_timespanset_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_timespanset_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.temporal_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.temporal_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temptype_continuous(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.temptype_continuous(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_byvalue(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.basetype_byvalue(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_varlength(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.basetype_varlength(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def basetype_length(type: "meosType") -> "int16":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.basetype_length(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def talphanum_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.talphanum_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def talpha_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.talpha_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tnumber_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_tnumber_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tnumber_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_tnumber_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_settype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_settype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_spantype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_spantype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_spansettype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tnumber_spansettype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tspatial_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tspatial_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tspatial_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_tspatial_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tspatial_basetype(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tspatial_basetype(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeo_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tgeo_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ensure_tnumber_tgeo_type(type: "meosType") -> "bool":
    type_converted = _ffi.cast("meosType", type)
    result = _lib.ensure_tnumber_tgeo_type(type_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_degrees(d: "Datum", normalize: "Datum") -> "Datum":
    d_converted = _ffi.cast("Datum", d)
    normalize_converted = _ffi.cast("Datum", normalize)
    result = _lib.datum_degrees(d_converted, normalize_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_radians(d: "Datum") -> "Datum":
    d_converted = _ffi.cast("Datum", d)
    result = _lib.datum_radians(d_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash(d: "Datum", basetype: "meosType") -> "uint32":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.datum_hash(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datum_hash_extended(d: "Datum", basetype: "meosType", seed: int) -> "uint64":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    seed_converted = _ffi.cast("uint64", seed)
    result = _lib.datum_hash_extended(d_converted, basetype_converted, seed_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_in(string: str, basetype: "meosType") -> "Set *":
    string_converted = string.encode("utf-8")
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.set_in(string_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_out(s: "const Set *", maxdd: int) -> str:
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def span_in(string: str, spantype: "meosType") -> "Span *":
    string_converted = string.encode("utf-8")
    spantype_converted = _ffi.cast("meosType", spantype)
    result = _lib.span_in(string_converted, spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_out(s: "const Span *", maxdd: int) -> str:
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_out(s_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def spanset_in(string: str, spantype: "meosType") -> "SpanSet *":
    string_converted = string.encode("utf-8")
    spantype_converted = _ffi.cast("meosType", spantype)
    result = _lib.spanset_in(string_converted, spantype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_out(ss: "const SpanSet *", maxdd: int) -> str:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def set_cp(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_cp(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_make(
    values: "const Datum *", count: int, basetype: "meosType", ordered: bool
) -> "Set *":
    values_converted = _ffi.cast("const Datum *", values)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.set_make(values_converted, count, basetype_converted, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def set_make_exp(
    values: "const Datum *",
    count: int,
    maxcount: int,
    basetype: "meosType",
    ordered: bool,
) -> "Set *":
    values_converted = _ffi.cast("const Datum *", values)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.set_make_exp(
        values_converted, count, maxcount, basetype_converted, ordered
    )
    _check_error()
    return result if result != _ffi.NULL else None


def set_make_free(
    values: "Datum *", count: int, basetype: "meosType", ordered: bool
) -> "Set *":
    values_converted = _ffi.cast("Datum *", values)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.set_make_free(values_converted, count, basetype_converted, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def span_cp(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_cp(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_make(
    lower: "Datum",
    upper: "Datum",
    lower_inc: bool,
    upper_inc: bool,
    basetype: "meosType",
) -> "Span *":
    lower_converted = _ffi.cast("Datum", lower)
    upper_converted = _ffi.cast("Datum", upper)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.span_make(
        lower_converted, upper_converted, lower_inc, upper_inc, basetype_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def span_set(
    lower: "Datum",
    upper: "Datum",
    lower_inc: bool,
    upper_inc: bool,
    basetype: "meosType",
    spantype: "meosType",
    s: "Span *",
) -> None:
    lower_converted = _ffi.cast("Datum", lower)
    upper_converted = _ffi.cast("Datum", upper)
    basetype_converted = _ffi.cast("meosType", basetype)
    spantype_converted = _ffi.cast("meosType", spantype)
    s_converted = _ffi.cast("Span *", s)
    _lib.span_set(
        lower_converted,
        upper_converted,
        lower_inc,
        upper_inc,
        basetype_converted,
        spantype_converted,
        s_converted,
    )
    _check_error()


def spanset_cp(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_cp(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make_exp(
    spans: "Span *", count: int, maxcount: int, normalize: bool, ordered: bool
) -> "SpanSet *":
    spans_converted = _ffi.cast("Span *", spans)
    result = _lib.spanset_make_exp(spans_converted, count, maxcount, normalize, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_make_free(
    spans: "Span *", count: int, normalize: bool, ordered: bool
) -> "SpanSet *":
    spans_converted = _ffi.cast("Span *", spans)
    result = _lib.spanset_make_free(spans_converted, count, normalize, ordered)
    _check_error()
    return result if result != _ffi.NULL else None


def dateset_tstzset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.dateset_tstzset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_tstzspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.datespan_tstzspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespanset_tstzspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.datespanset_tstzspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_intset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_intset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_intspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_intspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_intspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_intspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intset_floatset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intset_floatset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspan_floatspan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intspan_floatspan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intspanset_floatspanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intspanset_floatspanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_span(s: "const Set *") -> "Span *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_span(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_spanset(s: "const Set *") -> "SpanSet *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_spanset(s: "const Span *") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.span_spanset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzset_dateset(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tstzset_dateset(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_datespan(s: "const Span *") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tstzspan_datespan(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspanset_datespanset(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tstzspanset_datespanset(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_set_span(value: "Datum", basetype: "meosType", s: "Span *") -> None:
    value_converted = _ffi.cast("Datum", value)
    basetype_converted = _ffi.cast("meosType", basetype)
    s_converted = _ffi.cast("Span *", s)
    _lib.value_set_span(value_converted, basetype_converted, s_converted)
    _check_error()


def value_to_set(d: "Datum", basetype: "meosType") -> "Set *":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.value_to_set(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_to_span(d: "Datum", basetype: "meosType") -> "Span *":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.value_to_span(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def value_to_spanset(d: "Datum", basetype: "meosType") -> "SpanSet *":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.value_to_spanset(d_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_width(s: "const Span *") -> "Datum":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.numspan_width(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_width(ss: "const SpanSet *", boundspan: bool) -> "Datum":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.numspanset_width(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def set_end_value(s: "const Set *") -> "Datum":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_end_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_mem_size(s: "const Set *") -> "int":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_mem_size(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_set_span(s: "const Set *", sp: "Span *") -> None:
    s_converted = _ffi.cast("const Set *", s)
    sp_converted = _ffi.cast("Span *", sp)
    _lib.set_set_span(s_converted, sp_converted)
    _check_error()


def set_span(s: "const Set *") -> "Span *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_span(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_start_value(s: "const Set *") -> "Datum":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_start_value(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_value_n(s: "const Set *", n: int) -> "Datum *":
    s_converted = _ffi.cast("const Set *", s)
    out_result = _ffi.new("Datum *")
    result = _lib.set_value_n(s_converted, n, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def set_vals(s: "const Set *") -> "Datum *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_vals(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_values(s: "const Set *") -> "Datum *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_values(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_lower(ss: "const SpanSet *") -> "Datum":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_lower(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_mem_size(ss: "const SpanSet *") -> "int":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_mem_size(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_sps(ss: "const SpanSet *") -> "const Span **":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_sps(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_upper(ss: "const SpanSet *") -> "Datum":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_upper(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def datespan_set_tstzspan(s1: "const Span *", s2: "Span *") -> None:
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("Span *", s2)
    _lib.datespan_set_tstzspan(s1_converted, s2_converted)
    _check_error()


def floatset_deg(s: "const Set *", normalize: bool) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_deg(s_converted, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_rad(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_rad(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def floatset_rnd(s: "const Set *", size: int) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.floatset_rnd(s_converted, size)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_rnd(s: "const Span *", size: int) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.floatspan_rnd(s_converted, size)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspanset_rnd(ss: "const SpanSet *", size: int) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.floatspanset_rnd(ss_converted, size)
    _check_error()
    return result if result != _ffi.NULL else None


def floatspan_set_intspan(s1: "const Span *", s2: "Span *") -> None:
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("Span *", s2)
    _lib.floatspan_set_intspan(s1_converted, s2_converted)
    _check_error()


def intspan_set_floatspan(s1: "const Span *", s2: "Span *") -> None:
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("Span *", s2)
    _lib.intspan_set_floatspan(s1_converted, s2_converted)
    _check_error()


def numset_shift_scale(
    s: "const Set *", shift: "Datum", width: "Datum", hasshift: bool, haswidth: bool
) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.numset_shift_scale(
        s_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def numspan_shift_scale(
    s: "const Span *", shift: "Datum", width: "Datum", hasshift: bool, haswidth: bool
) -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.numspan_shift_scale(
        s_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def numspanset_shift_scale(
    ss: "const SpanSet *",
    shift: "Datum",
    width: "Datum",
    hasshift: bool,
    haswidth: bool,
) -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.numspanset_shift_scale(
        ss_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def set_compact(s: "const Set *") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.set_compact(s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_expand(s1: "const Span *", s2: "Span *") -> None:
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("Span *", s2)
    _lib.span_expand(s1_converted, s2_converted)
    _check_error()


def spanset_compact(ss: "const SpanSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.spanset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def textcat_textset_text_int(s: "const Set *", txt: str, invert: bool) -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    txt_converted = cstring2text(txt)
    result = _lib.textcat_textset_text_int(s_converted, txt_converted, invert)
    _check_error()
    return result if result != _ffi.NULL else None


def tstzspan_set_datespan(s1: "const Span *", s2: "Span *") -> None:
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("Span *", s2)
    _lib.tstzspan_set_datespan(s1_converted, s2_converted)
    _check_error()


def set_cmp_int(s1: "const Set *", s2: "const Set *") -> "int":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_cmp_int(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def set_eq_int(s1: "const Set *", s2: "const Set *") -> "bool":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.set_eq_int(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_cmp_int(s1: "const Span *", s2: "const Span *") -> "int":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_cmp_int(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def span_eq_int(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.span_eq_int(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_cmp_int(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "int":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_cmp_int(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanset_eq_int(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "bool":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.spanset_eq_int(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adj_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.adj_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.adjacent_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.adjacent_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def adjacent_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.adjacent_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def cont_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.cont_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_set(value: "Datum", s: "const Set *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.contained_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_span(value: "Datum", s: "const Span *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.contained_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contained_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.contained_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_set_value(s: "const Set *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.contains_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.contains_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def contains_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.contains_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ovadj_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.ovadj_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def over_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.over_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_set_value(s: "const Set *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.left_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.left_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.left_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_set(value: "Datum", s: "const Set *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.left_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_span(value: "Datum", s: "const Span *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.left_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def left_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.left_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lf_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.lf_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def lfnadj_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.lfnadj_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_set_value(s: "const Set *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overleft_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overleft_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overleft_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_set(value: "Datum", s: "const Set *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overleft_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_span(value: "Datum", s: "const Span *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overleft_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overleft_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overleft_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_set_value(s: "const Set *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overright_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overright_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.overright_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_set(value: "Datum", s: "const Set *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.overright_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_span(value: "Datum", s: "const Span *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.overright_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def overright_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.overright_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ovlf_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.ovlf_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ovri_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.ovri_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ri_span_span(s1: "const Span *", s2: "const Span *") -> "bool":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.ri_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_set(value: "Datum", s: "const Set *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.right_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_set_value(s: "const Set *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.right_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_span(value: "Datum", s: "const Span *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.right_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_value_spanset(value: "Datum", ss: "const SpanSet *") -> "bool":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.right_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_span_value(s: "const Span *", value: "Datum") -> "bool":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.right_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def right_spanset_value(ss: "const SpanSet *", value: "Datum") -> "bool":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.right_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def bbox_union_span_span(s1: "const Span *", s2: "const Span *") -> "Span *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    out_result = _ffi.new("Span *")
    _lib.bbox_union_span_span(s1_converted, s2_converted, out_result)
    _check_error()
    return out_result if out_result != _ffi.NULL else None


def inter_span_span(s1: "const Span *", s2: "const Span *") -> "Span *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    out_result = _ffi.new("Span *")
    result = _lib.inter_span_span(s1_converted, s2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def intersection_set_value(s: "const Set *", value: "Datum") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.intersection_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_span_value(s: "const Span *", value: "Datum") -> "Span *":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.intersection_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_spanset_value(ss: "const SpanSet *", value: "Datum") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.intersection_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_value_set(value: "Datum", s: "const Set *") -> "Set *":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.intersection_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_value_span(value: "Datum", s: "const Span *") -> "Span *":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.intersection_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def intersection_value_spanset(value: "Datum", ss: "const SpanSet *") -> "SpanSet *":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.intersection_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def mi_span_span(s1: "const Span *", s2: "const Span *") -> "Span *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    out_result = _ffi.new("Span *")
    result = _lib.mi_span_span(s1_converted, s2_converted, out_result)
    _check_error()
    return out_result if out_result != _ffi.NULL else None


def minus_set_value(s: "const Set *", value: "Datum") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.minus_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_span_value(s: "const Span *", value: "Datum") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.minus_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_spanset_value(ss: "const SpanSet *", value: "Datum") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.minus_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_value_set(value: "Datum", s: "const Set *") -> "Set *":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.minus_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_value_span(value: "Datum", s: "const Span *") -> "SpanSet *":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.minus_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def minus_value_spanset(value: "Datum", ss: "const SpanSet *") -> "SpanSet *":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.minus_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def super_union_span_span(s1: "const Span *", s2: "const Span *") -> "Span *":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.super_union_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_set_value(s: "const Set *", value: "const Datum") -> "Set *":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("const Datum", value)
    result = _lib.union_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_span_value(s: "const Span *", value: "Datum") -> "SpanSet *":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.union_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_spanset_value(ss: "const SpanSet *", value: "Datum") -> "SpanSet *":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.union_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_value_set(value: "const Datum", s: "const Set *") -> "Set *":
    value_converted = _ffi.cast("const Datum", value)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.union_value_set(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_value_span(value: "Datum", s: "const Span *") -> "SpanSet *":
    value_converted = _ffi.cast("Datum", value)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.union_value_span(value_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def union_value_spanset(value: "Datum", ss: "const SpanSet *") -> "SpanSet *":
    value_converted = _ffi.cast("Datum", value)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.union_value_spanset(value_converted, ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dist_set_set(s1: "const Set *", s2: "const Set *") -> "Datum":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.dist_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def dist_span_span(s1: "const Span *", s2: "const Span *") -> "Datum":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.dist_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_set(s1: "const Set *", s2: "const Set *") -> "Datum":
    s1_converted = _ffi.cast("const Set *", s1)
    s2_converted = _ffi.cast("const Set *", s2)
    result = _lib.distance_set_set(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_set_value(s: "const Set *", value: "Datum") -> "Datum":
    s_converted = _ffi.cast("const Set *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.distance_set_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_span(s1: "const Span *", s2: "const Span *") -> "Datum":
    s1_converted = _ffi.cast("const Span *", s1)
    s2_converted = _ffi.cast("const Span *", s2)
    result = _lib.distance_span_span(s1_converted, s2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_span_value(s: "const Span *", value: "Datum") -> "Datum":
    s_converted = _ffi.cast("const Span *", s)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.distance_span_value(s_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_span(ss: "const SpanSet *", s: "const Span *") -> "Datum":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.distance_spanset_span(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_spanset(ss1: "const SpanSet *", ss2: "const SpanSet *") -> "Datum":
    ss1_converted = _ffi.cast("const SpanSet *", ss1)
    ss2_converted = _ffi.cast("const SpanSet *", ss2)
    result = _lib.distance_spanset_spanset(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_spanset_value(ss: "const SpanSet *", value: "Datum") -> "Datum":
    ss_converted = _ffi.cast("const SpanSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.distance_spanset_value(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_value_value(l: "Datum", r: "Datum", basetype: "meosType") -> "Datum":
    l_converted = _ffi.cast("Datum", l)
    r_converted = _ffi.cast("Datum", r)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.distance_value_value(l_converted, r_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def spanbase_extent_transfn(
    state: "Span *", value: "Datum", basetype: "meosType"
) -> "Span *":
    state_converted = _ffi.cast("Span *", state)
    value_converted = _ffi.cast("Datum", value)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.spanbase_extent_transfn(
        state_converted, value_converted, basetype_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def value_union_transfn(
    state: "Set *", value: "Datum", basetype: "meosType"
) -> "Set *":
    state_converted = _ffi.cast("Set *", state)
    value_converted = _ffi.cast("Datum", value)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.value_union_transfn(
        state_converted, value_converted, basetype_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def number_tstzspan_to_tbox(
    d: "Datum", basetype: "meosType", s: "const Span *"
) -> "TBox *":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.number_tstzspan_to_tbox(d_converted, basetype_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def number_timestamptz_to_tbox(d: "Datum", basetype: "meosType", t: int) -> "TBox *":
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.number_timestamptz_to_tbox(
        d_converted, basetype_converted, t_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_cp(box: "const STBox *") -> "STBox *":
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.stbox_cp(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_set(
    hasx: bool,
    hasz: bool,
    geodetic: bool,
    srid: int,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    zmin: float,
    zmax: float,
    s: "const Span *",
    box: "STBox *",
) -> None:
    srid_converted = _ffi.cast("int32", srid)
    s_converted = _ffi.cast("const Span *", s)
    box_converted = _ffi.cast("STBox *", box)
    _lib.stbox_set(
        hasx,
        hasz,
        geodetic,
        srid_converted,
        xmin,
        xmax,
        ymin,
        ymax,
        zmin,
        zmax,
        s_converted,
        box_converted,
    )
    _check_error()


def tbox_cp(box: "const TBox *") -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.tbox_cp(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tbox_set(s: "const Span *", p: "const Span *", box: "TBox *") -> None:
    s_converted = _ffi.cast("const Span *", s)
    p_converted = _ffi.cast("const Span *", p)
    box_converted = _ffi.cast("TBox *", box)
    _lib.tbox_set(s_converted, p_converted, box_converted)
    _check_error()


def box3d_to_stbox(box: "const BOX3D *") -> "STBox *":
    box_converted = _ffi.cast("const BOX3D *", box)
    result = _lib.box3d_to_stbox(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def gbox_to_stbox(box: "const GBOX *") -> "STBox *":
    box_converted = _ffi.cast("const GBOX *", box)
    result = _lib.gbox_to_stbox(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def float_set_tbox(d: float, box: "TBox *") -> None:
    box_converted = _ffi.cast("TBox *", box)
    _lib.float_set_tbox(d, box_converted)
    _check_error()


def gbox_to_stbox(box: "const GBOX *") -> "STBox *":
    box_converted = _ffi.cast("const GBOX *", box)
    result = _lib.gbox_to_stbox(box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geo_set_stbox(gs: "const GSERIALIZED *", box: "STBox *") -> "bool":
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    box_converted = _ffi.cast("STBox *", box)
    result = _lib.geo_set_stbox(gs_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def geoarr_set_stbox(values: "const Datum *", count: int, box: "STBox *") -> None:
    values_converted = _ffi.cast("const Datum *", values)
    box_converted = _ffi.cast("STBox *", box)
    _lib.geoarr_set_stbox(values_converted, count, box_converted)
    _check_error()


def int_set_tbox(i: int, box: "TBox *") -> None:
    box_converted = _ffi.cast("TBox *", box)
    _lib.int_set_tbox(i, box_converted)
    _check_error()


def number_set_tbox(d: "Datum", basetype: "meosType", box: "TBox *") -> None:
    d_converted = _ffi.cast("Datum", d)
    basetype_converted = _ffi.cast("meosType", basetype)
    box_converted = _ffi.cast("TBox *", box)
    _lib.number_set_tbox(d_converted, basetype_converted, box_converted)
    _check_error()


def number_to_tbox(value: "Datum", basetype: "meosType") -> "TBox *":
    value_converted = _ffi.cast("Datum", value)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.number_to_tbox(value_converted, basetype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def numset_set_tbox(s: "const Set *", box: "TBox *") -> None:
    s_converted = _ffi.cast("const Set *", s)
    box_converted = _ffi.cast("TBox *", box)
    _lib.numset_set_tbox(s_converted, box_converted)
    _check_error()


def numspan_set_tbox(span: "const Span *", box: "TBox *") -> None:
    span_converted = _ffi.cast("const Span *", span)
    box_converted = _ffi.cast("TBox *", box)
    _lib.numspan_set_tbox(span_converted, box_converted)
    _check_error()


def numspanset_set_tbox(ss: "const SpanSet *", box: "TBox *") -> None:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    box_converted = _ffi.cast("TBox *", box)
    _lib.numspanset_set_tbox(ss_converted, box_converted)
    _check_error()


def spatialset_set_stbox(set: "const Set *", box: "STBox *") -> None:
    set_converted = _ffi.cast("const Set *", set)
    box_converted = _ffi.cast("STBox *", box)
    _lib.spatialset_set_stbox(set_converted, box_converted)
    _check_error()


def stbox_set_box3d(box: "const STBox *", box3d: "BOX3D *") -> None:
    box_converted = _ffi.cast("const STBox *", box)
    box3d_converted = _ffi.cast("BOX3D *", box3d)
    _lib.stbox_set_box3d(box_converted, box3d_converted)
    _check_error()


def stbox_set_gbox(box: "const STBox *", gbox: "GBOX *") -> None:
    box_converted = _ffi.cast("const STBox *", box)
    gbox_converted = _ffi.cast("GBOX *", gbox)
    _lib.stbox_set_gbox(box_converted, gbox_converted)
    _check_error()


def timestamptz_set_stbox(t: int, box: "STBox *") -> None:
    t_converted = _ffi.cast("TimestampTz", t)
    box_converted = _ffi.cast("STBox *", box)
    _lib.timestamptz_set_stbox(t_converted, box_converted)
    _check_error()


def timestamptz_set_tbox(t: int, box: "TBox *") -> None:
    t_converted = _ffi.cast("TimestampTz", t)
    box_converted = _ffi.cast("TBox *", box)
    _lib.timestamptz_set_tbox(t_converted, box_converted)
    _check_error()


def tstzset_set_stbox(s: "const Set *", box: "STBox *") -> None:
    s_converted = _ffi.cast("const Set *", s)
    box_converted = _ffi.cast("STBox *", box)
    _lib.tstzset_set_stbox(s_converted, box_converted)
    _check_error()


def tstzset_set_tbox(s: "const Set *", box: "TBox *") -> None:
    s_converted = _ffi.cast("const Set *", s)
    box_converted = _ffi.cast("TBox *", box)
    _lib.tstzset_set_tbox(s_converted, box_converted)
    _check_error()


def tstzspan_set_stbox(s: "const Span *", box: "STBox *") -> None:
    s_converted = _ffi.cast("const Span *", s)
    box_converted = _ffi.cast("STBox *", box)
    _lib.tstzspan_set_stbox(s_converted, box_converted)
    _check_error()


def tstzspan_set_tbox(s: "const Span *", box: "TBox *") -> None:
    s_converted = _ffi.cast("const Span *", s)
    box_converted = _ffi.cast("TBox *", box)
    _lib.tstzspan_set_tbox(s_converted, box_converted)
    _check_error()


def tstzspanset_set_stbox(ss: "const SpanSet *", box: "STBox *") -> None:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    box_converted = _ffi.cast("STBox *", box)
    _lib.tstzspanset_set_stbox(ss_converted, box_converted)
    _check_error()


def tstzspanset_set_tbox(ss: "const SpanSet *", box: "TBox *") -> None:
    ss_converted = _ffi.cast("const SpanSet *", ss)
    box_converted = _ffi.cast("TBox *", box)
    _lib.tstzspanset_set_tbox(ss_converted, box_converted)
    _check_error()


def tbox_shift_scale_value(
    box: "const TBox *",
    shift: "Datum",
    width: "Datum",
    basetype: "meosType",
    hasshift: bool,
    haswidth: bool,
) -> "TBox *":
    box_converted = _ffi.cast("const TBox *", box)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.tbox_shift_scale_value(
        box_converted,
        shift_converted,
        width_converted,
        basetype_converted,
        hasshift,
        haswidth,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def stbox_expand(box1: "const STBox *", box2: "STBox *") -> None:
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("STBox *", box2)
    _lib.stbox_expand(box1_converted, box2_converted)
    _check_error()


def tbox_expand(box1: "const TBox *", box2: "TBox *") -> None:
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("TBox *", box2)
    _lib.tbox_expand(box1_converted, box2_converted)
    _check_error()


def inter_stbox_stbox(box1: "const STBox *", box2: "const STBox *") -> "STBox *":
    box1_converted = _ffi.cast("const STBox *", box1)
    box2_converted = _ffi.cast("const STBox *", box2)
    out_result = _ffi.new("STBox *")
    result = _lib.inter_stbox_stbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def inter_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "TBox *":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    out_result = _ffi.new("TBox *")
    result = _lib.inter_tbox_tbox(box1_converted, box2_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def geoarr_as_text(
    geoarr: "const Datum *", count: int, maxdd: int, extended: bool
) -> "char **":
    geoarr_converted = _ffi.cast("const Datum *", geoarr)
    result = _lib.geoarr_as_text(geoarr_converted, count, maxdd, extended)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_as_mfjson(inst: "const TInstant *", with_bbox: bool) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tboolinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tboolinst_from_mfjson(mfjson: "json_object *") -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tboolinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.tboolinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_as_mfjson(seq: "const TSequence *", with_bbox: bool) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tboolseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tboolseq_from_mfjson(mfjson: "json_object *") -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tboolseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tboolseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_as_mfjson(ss: "const TSequenceSet *", with_bbox: bool) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tboolseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tboolseqset_from_mfjson(mfjson: "json_object *") -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tboolseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tboolseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tboolseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_in(string: str, temptype: "meosType") -> "Temporal *":
    string_converted = string.encode("utf-8")
    temptype_converted = _ffi.cast("meosType", temptype)
    result = _lib.temporal_in(string_converted, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_out(temp: "const Temporal *", maxdd: int) -> str:
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_out(temp_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def temparr_out(temparr: "const Temporal **", count: int, maxdd: int) -> "char **":
    temparr_converted = [_ffi.cast("const Temporal *", x) for x in temparr]
    result = _lib.temparr_out(temparr_converted, count, maxdd)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_as_mfjson(
    inst: "const TInstant *", with_bbox: bool, precision: int
) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tfloatinst_as_mfjson(inst_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tfloatinst_from_mfjson(mfjson: "json_object *") -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tfloatinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.tfloatinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_as_mfjson(
    seq: "const TSequence *", with_bbox: bool, precision: int
) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tfloatseq_as_mfjson(seq_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tfloatseq_from_mfjson(
    mfjson: "json_object *", interp: "interpType"
) -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tfloatseq_from_mfjson(mfjson_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tfloatseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_as_mfjson(
    ss: "const TSequenceSet *", with_bbox: bool, precision: int
) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tfloatseqset_as_mfjson(ss_converted, with_bbox, precision)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tfloatseqset_from_mfjson(
    mfjson: "json_object *", interp: "interpType"
) -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tfloatseqset_from_mfjson(mfjson_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tfloatseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointinst_from_mfjson(mfjson: "json_object *", srid: int) -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tgeogpointinst_from_mfjson(mfjson_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeogpointinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseq_from_mfjson(
    mfjson: "json_object *", srid: int, interp: "interpType"
) -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeogpointseq_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeogpointseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseqset_from_mfjson(
    mfjson: "json_object *", srid: int, interp: "interpType"
) -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeogpointseqset_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeogpointseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeogpointseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_from_mfjson(mfjson: "json_object *", srid: int) -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tgeompointinst_from_mfjson(mfjson_converted, srid)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeompointinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_from_mfjson(
    mfjson: "json_object *", srid: int, interp: "interpType"
) -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeompointseq_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeompointseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_from_mfjson(
    mfjson: "json_object *", srid: int, interp: "interpType"
) -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tgeompointseqset_from_mfjson(mfjson_converted, srid, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tgeompointseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_as_mfjson(
    inst: "const TInstant *", with_bbox: bool, precision: int, srs: str
) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    srs_converted = srs.encode("utf-8")
    result = _lib.tinstant_as_mfjson(
        inst_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tinstant_from_mfjson(
    mfjson: "json_object *", isgeo: bool, srid: int, temptype: "meosType"
) -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    temptype_converted = _ffi.cast("meosType", temptype)
    result = _lib.tinstant_from_mfjson(
        mfjson_converted, isgeo, srid, temptype_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_in(string: str, temptype: "meosType") -> "TInstant *":
    string_converted = string.encode("utf-8")
    temptype_converted = _ffi.cast("meosType", temptype)
    result = _lib.tinstant_in(string_converted, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_out(inst: "const TInstant *", maxdd: int) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_out(inst_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tintinst_as_mfjson(inst: "const TInstant *", with_bbox: bool) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tintinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tintinst_from_mfjson(mfjson: "json_object *") -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tintinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.tintinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_as_mfjson(seq: "const TSequence *", with_bbox: bool) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tintseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tintseq_from_mfjson(mfjson: "json_object *") -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tintseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tintseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_as_mfjson(ss: "const TSequenceSet *", with_bbox: bool) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tintseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tintseqset_from_mfjson(mfjson: "json_object *") -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.tintseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tintseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.tintseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointarr_as_text(
    temparr: "const Temporal **", count: int, maxdd: int, extended: bool
) -> "char **":
    temparr_converted = [_ffi.cast("const Temporal *", x) for x in temparr]
    result = _lib.tpointarr_as_text(temparr_converted, count, maxdd, extended)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_as_mfjson(
    inst: "const TInstant *", with_bbox: bool, precision: int, srs: str
) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    srs_converted = srs.encode("utf-8")
    result = _lib.tpointinst_as_mfjson(
        inst_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tpointseq_as_mfjson(
    seq: "const TSequence *", with_bbox: bool, precision: int, srs: str
) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    srs_converted = srs.encode("utf-8")
    result = _lib.tpointseq_as_mfjson(
        seq_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tpointseqset_as_mfjson(
    ss: "const TSequenceSet *", with_bbox: bool, precision: int, srs: str
) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    srs_converted = srs.encode("utf-8")
    result = _lib.tpointseqset_as_mfjson(
        ss_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tsequence_as_mfjson(
    seq: "const TSequence *", with_bbox: bool, precision: int, srs: str
) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    srs_converted = srs.encode("utf-8")
    result = _lib.tsequence_as_mfjson(
        seq_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tsequence_from_mfjson(
    mfjson: "json_object *",
    isgeo: bool,
    srid: int,
    temptype: "meosType",
    interp: "interpType",
) -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    temptype_converted = _ffi.cast("meosType", temptype)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_from_mfjson(
        mfjson_converted, isgeo, srid, temptype_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_in(
    string: str, temptype: "meosType", interp: "interpType"
) -> "TSequence *":
    string_converted = string.encode("utf-8")
    temptype_converted = _ffi.cast("meosType", temptype)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_in(string_converted, temptype_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_out(seq: "const TSequence *", maxdd: int) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_out(seq_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tsequenceset_as_mfjson(
    ss: "const TSequenceSet *", with_bbox: bool, precision: int, srs: str
) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    srs_converted = srs.encode("utf-8")
    result = _lib.tsequenceset_as_mfjson(
        ss_converted, with_bbox, precision, srs_converted
    )
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def tsequenceset_from_mfjson(
    mfjson: "json_object *",
    isgeo: bool,
    srid: int,
    temptype: "meosType",
    interp: "interpType",
) -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    temptype_converted = _ffi.cast("meosType", temptype)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequenceset_from_mfjson(
        mfjson_converted, isgeo, srid, temptype_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_in(
    string: str, temptype: "meosType", interp: "interpType"
) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    temptype_converted = _ffi.cast("meosType", temptype)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequenceset_in(
        string_converted, temptype_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_out(ss: "const TSequenceSet *", maxdd: int) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_out(ss_converted, maxdd)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def ttextinst_as_mfjson(inst: "const TInstant *", with_bbox: bool) -> str:
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.ttextinst_as_mfjson(inst_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def ttextinst_from_mfjson(mfjson: "json_object *") -> "TInstant *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.ttextinst_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextinst_in(string: str) -> "TInstant *":
    string_converted = string.encode("utf-8")
    result = _lib.ttextinst_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_as_mfjson(seq: "const TSequence *", with_bbox: bool) -> str:
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.ttextseq_as_mfjson(seq_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def ttextseq_from_mfjson(mfjson: "json_object *") -> "TSequence *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.ttextseq_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseq_in(string: str, interp: "interpType") -> "TSequence *":
    string_converted = string.encode("utf-8")
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.ttextseq_in(string_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_as_mfjson(ss: "const TSequenceSet *", with_bbox: bool) -> str:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.ttextseqset_as_mfjson(ss_converted, with_bbox)
    _check_error()
    result = _ffi.string(result).decode("utf-8")
    return result if result != _ffi.NULL else None


def ttextseqset_from_mfjson(mfjson: "json_object *") -> "TSequenceSet *":
    mfjson_converted = _ffi.cast("json_object *", mfjson)
    result = _lib.ttextseqset_from_mfjson(mfjson_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ttextseqset_in(string: str) -> "TSequenceSet *":
    string_converted = string.encode("utf-8")
    result = _lib.ttextseqset_in(string_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_mfjson(mfjson: str, temptype: "meosType") -> "Temporal *":
    mfjson_converted = mfjson.encode("utf-8")
    temptype_converted = _ffi.cast("meosType", temptype)
    result = _lib.temporal_from_mfjson(mfjson_converted, temptype_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_cp(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_cp(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_from_base_temp(
    value: "Datum", temptype: "meosType", temp: "const Temporal *"
) -> "Temporal *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_from_base_temp(
        value_converted, temptype_converted, temp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_copy(inst: "const TInstant *") -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_copy(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_make(value: "Datum", temptype: "meosType", t: int) -> "TInstant *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tinstant_make(value_converted, temptype_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_make_free(value: "Datum", temptype: "meosType", t: int) -> "TInstant *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tinstant_make_free(value_converted, temptype_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_make_coords(
    xcoords: "const double *",
    ycoords: "const double *",
    zcoords: "const double *",
    times: int,
    count: int,
    srid: int,
    geodetic: bool,
    lower_inc: bool,
    upper_inc: bool,
    interp: "interpType",
    normalize: bool,
) -> "TSequence *":
    xcoords_converted = _ffi.cast("const double *", xcoords)
    ycoords_converted = _ffi.cast("const double *", ycoords)
    zcoords_converted = _ffi.cast("const double *", zcoords)
    times_converted = _ffi.cast("const TimestampTz *", times)
    srid_converted = _ffi.cast("int32", srid)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tpointseq_make_coords(
        xcoords_converted,
        ycoords_converted,
        zcoords_converted,
        times_converted,
        count,
        srid_converted,
        geodetic,
        lower_inc,
        upper_inc,
        interp_converted,
        normalize,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_copy(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_copy(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_from_base_tstzset(
    value: "Datum", temptype: "meosType", ss: "const Set *"
) -> "TSequence *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    ss_converted = _ffi.cast("const Set *", ss)
    result = _lib.tsequence_from_base_tstzset(
        value_converted, temptype_converted, ss_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_from_base_tstzspan(
    value: "Datum", temptype: "meosType", s: "const Span *", interp: "interpType"
) -> "TSequence *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    s_converted = _ffi.cast("const Span *", s)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_from_base_tstzspan(
        value_converted, temptype_converted, s_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make_exp(
    instants: "const TInstant **",
    count: int,
    maxcount: int,
    lower_inc: bool,
    upper_inc: bool,
    interp: "interpType",
    normalize: bool,
) -> "TSequence *":
    instants_converted = [_ffi.cast("const TInstant *", x) for x in instants]
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_make_exp(
        instants_converted,
        count,
        maxcount,
        lower_inc,
        upper_inc,
        interp_converted,
        normalize,
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_make_free(
    instants: "TInstant **",
    count: int,
    lower_inc: bool,
    upper_inc: bool,
    interp: "interpType",
    normalize: bool,
) -> "TSequence *":
    instants_converted = [_ffi.cast("TInstant *", x) for x in instants]
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_make_free(
        instants_converted, count, lower_inc, upper_inc, interp_converted, normalize
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_copy(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_copy(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tseqsetarr_to_tseqset(
    seqsets: "TSequenceSet **", count: int, totalseqs: int
) -> "TSequenceSet *":
    seqsets_converted = [_ffi.cast("TSequenceSet *", x) for x in seqsets]
    result = _lib.tseqsetarr_to_tseqset(seqsets_converted, count, totalseqs)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_from_base_tstzspanset(
    value: "Datum", temptype: "meosType", ss: "const SpanSet *", interp: "interpType"
) -> "TSequenceSet *":
    value_converted = _ffi.cast("Datum", value)
    temptype_converted = _ffi.cast("meosType", temptype)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequenceset_from_base_tstzspanset(
        value_converted, temptype_converted, ss_converted, interp_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_exp(
    sequences: "const TSequence **", count: int, maxcount: int, normalize: bool
) -> "TSequenceSet *":
    sequences_converted = [_ffi.cast("const TSequence *", x) for x in sequences]
    result = _lib.tsequenceset_make_exp(sequences_converted, count, maxcount, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_make_free(
    sequences: "TSequence **", count: int, normalize: bool
) -> "TSequenceSet *":
    sequences_converted = [_ffi.cast("TSequence *", x) for x in sequences]
    result = _lib.tsequenceset_make_free(sequences_converted, count, normalize)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_set_tstzspan(temp: "const Temporal *", s: "Span *") -> None:
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("Span *", s)
    _lib.temporal_set_tstzspan(temp_converted, s_converted)
    _check_error()


def tinstant_set_tstzspan(inst: "const TInstant *", s: "Span *") -> None:
    inst_converted = _ffi.cast("const TInstant *", inst)
    s_converted = _ffi.cast("Span *", s)
    _lib.tinstant_set_tstzspan(inst_converted, s_converted)
    _check_error()


def tnumber_span(temp: "const Temporal *") -> "Span *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tnumber_span(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_set_tstzspan(seq: "const TSequence *", s: "Span *") -> None:
    seq_converted = _ffi.cast("const TSequence *", seq)
    s_converted = _ffi.cast("Span *", s)
    _lib.tsequence_set_tstzspan(seq_converted, s_converted)
    _check_error()


def tsequenceset_set_tstzspan(ss: "const TSequenceSet *", s: "Span *") -> None:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("Span *", s)
    _lib.tsequenceset_set_tstzspan(ss_converted, s_converted)
    _check_error()


def temporal_end_value(temp: "const Temporal *") -> "Datum":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_end_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_insts(temp: "const Temporal *") -> "Tuple['const TInstant **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_insts(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_max_value(temp: "const Temporal *") -> "Datum":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_max_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_mem_size(temp: "const Temporal *") -> "size_t":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_mem_size(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_min_value(temp: "const Temporal *") -> "Datum":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_min_value(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_seqs(temp: "const Temporal *") -> "Tuple['const TSequence **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_seqs(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_set_bbox(temp: "const Temporal *", box: "void *") -> None:
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("void *", box)
    _lib.temporal_set_bbox(temp_converted, box_converted)
    _check_error()


def temporal_set_tstzspan(temp: "const Temporal *", s: "Span *") -> None:
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("Span *", s)
    _lib.temporal_set_tstzspan(temp_converted, s_converted)
    _check_error()


def temporal_seqs(temp: "const Temporal *") -> "Tuple['const TSequence **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_seqs(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_vals(temp: "const Temporal *") -> "Tuple['Datum *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_vals(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_values(temp: "const Temporal *") -> "Tuple['Datum *', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    count = _ffi.new("int *")
    result = _lib.temporal_values(temp_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_hash(inst: "const TInstant *") -> "uint32":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_hash(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_insts(inst: "const TInstant *") -> "Tuple['const TInstant **', 'int']":
    inst_converted = _ffi.cast("const TInstant *", inst)
    count = _ffi.new("int *")
    result = _lib.tinstant_insts(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_set_bbox(inst: "const TInstant *", box: "void *") -> None:
    inst_converted = _ffi.cast("const TInstant *", inst)
    box_converted = _ffi.cast("void *", box)
    _lib.tinstant_set_bbox(inst_converted, box_converted)
    _check_error()


def tinstant_time(inst: "const TInstant *") -> "SpanSet *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_time(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_timestamps(inst: "const TInstant *") -> "Tuple['TimestampTz *', 'int']":
    inst_converted = _ffi.cast("const TInstant *", inst)
    count = _ffi.new("int *")
    result = _lib.tinstant_timestamps(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tinstant_val(inst: "const TInstant *") -> "Datum":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_val(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_value(inst: "const TInstant *") -> "Datum":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tinstant_value(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_value_at_timestamptz(inst: "const TInstant *", t: int) -> "Datum *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("Datum *")
    result = _lib.tinstant_value_at_timestamptz(inst_converted, t_converted, out_result)
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tinstant_vals(inst: "const TInstant *") -> "Tuple['Datum *', 'int']":
    inst_converted = _ffi.cast("const TInstant *", inst)
    count = _ffi.new("int *")
    result = _lib.tinstant_vals(inst_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tnumber_set_span(temp: "const Temporal *", span: "Span *") -> None:
    temp_converted = _ffi.cast("const Temporal *", temp)
    span_converted = _ffi.cast("Span *", span)
    _lib.tnumber_set_span(temp_converted, span_converted)
    _check_error()


def tnumberinst_valuespans(inst: "const TInstant *") -> "SpanSet *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tnumberinst_valuespans(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_valuespans(seq: "const TSequence *") -> "SpanSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_valuespans(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_valuespans(ss: "const TSequenceSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_valuespans(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_duration(seq: "const TSequence *") -> "Interval *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_duration(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_end_timestamptz(seq: "const TSequence *") -> "TimestampTz":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_end_timestamptz(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_hash(seq: "const TSequence *") -> "uint32":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_hash(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_insts(seq: "const TSequence *") -> "const TInstant **":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_insts(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_max_inst(seq: "const TSequence *") -> "const TInstant *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_max_inst(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_max_val(seq: "const TSequence *") -> "Datum":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_max_val(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_min_inst(seq: "const TSequence *") -> "const TInstant *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_min_inst(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_min_val(seq: "const TSequence *") -> "Datum":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_min_val(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_segments(seq: "const TSequence *") -> "Tuple['TSequence **', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tsequence_segments(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_seqs(seq: "const TSequence *") -> "Tuple['const TSequence **', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tsequence_seqs(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_set_bbox(seq: "const TSequence *", box: "void *") -> None:
    seq_converted = _ffi.cast("const TSequence *", seq)
    box_converted = _ffi.cast("void *", box)
    _lib.tsequence_set_bbox(seq_converted, box_converted)
    _check_error()


def tsequence_expand_bbox(seq: "TSequence *", inst: "const TInstant *") -> None:
    seq_converted = _ffi.cast("TSequence *", seq)
    inst_converted = _ffi.cast("const TInstant *", inst)
    _lib.tsequence_expand_bbox(seq_converted, inst_converted)
    _check_error()


def tsequence_start_timestamptz(seq: "const TSequence *") -> "TimestampTz":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_start_timestamptz(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_time(seq: "const TSequence *") -> "SpanSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_time(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_timestamps(seq: "const TSequence *") -> "Tuple['TimestampTz *', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tsequence_timestamps(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequence_value_at_timestamptz(
    seq: "const TSequence *", t: int, strict: bool
) -> "Datum *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("Datum *")
    result = _lib.tsequence_value_at_timestamptz(
        seq_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tsequence_vals(seq: "const TSequence *") -> "Tuple['Datum *', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tsequence_vals(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_duration(ss: "const TSequenceSet *", boundspan: bool) -> "Interval *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_duration(ss_converted, boundspan)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_end_timestamptz(ss: "const TSequenceSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_end_timestamptz(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_hash(ss: "const TSequenceSet *") -> "uint32":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_hash(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_inst_n(ss: "const TSequenceSet *", n: int) -> "const TInstant *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_inst_n(ss_converted, n)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_insts(ss: "const TSequenceSet *") -> "const TInstant **":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_insts(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_max_inst(ss: "const TSequenceSet *") -> "const TInstant *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_max_inst(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_max_val(ss: "const TSequenceSet *") -> "Datum":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_max_val(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_min_inst(ss: "const TSequenceSet *") -> "const TInstant *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_min_inst(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_min_val(ss: "const TSequenceSet *") -> "Datum":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_min_val(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_num_instants(ss: "const TSequenceSet *") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_num_instants(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_num_timestamps(ss: "const TSequenceSet *") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_num_timestamps(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_segments(ss: "const TSequenceSet *") -> "Tuple['TSequence **', 'int']":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tsequenceset_segments(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_seqs(ss: "const TSequenceSet *") -> "const TSequence **":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_seqs(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_set_bbox(ss: "const TSequenceSet *", box: "void *") -> None:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    box_converted = _ffi.cast("void *", box)
    _lib.tsequenceset_set_bbox(ss_converted, box_converted)
    _check_error()


def tsequenceset_start_timestamptz(ss: "const TSequenceSet *") -> "TimestampTz":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_start_timestamptz(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_time(ss: "const TSequenceSet *") -> "SpanSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_time(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_timespan(ss: "const TSequenceSet *") -> "Interval *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_timespan(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_timestamptz_n(ss: "const TSequenceSet *", n: int) -> int:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    out_result = _ffi.new("TimestampTz *")
    result = _lib.tsequenceset_timestamptz_n(ss_converted, n, out_result)
    _check_error()
    if result:
        return out_result[0] if out_result[0] != _ffi.NULL else None
    return None


def tsequenceset_timestamps(
    ss: "const TSequenceSet *",
) -> "Tuple['TimestampTz *', 'int']":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tsequenceset_timestamps(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tsequenceset_value_at_timestamptz(
    ss: "const TSequenceSet *", t: int, strict: bool
) -> "Datum *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("Datum *")
    result = _lib.tsequenceset_value_at_timestamptz(
        ss_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tsequenceset_vals(ss: "const TSequenceSet *") -> "Tuple['Datum *', 'int']":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tsequenceset_vals(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def temporal_compact(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_compact(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restart(temp: "Temporal *", count: int) -> None:
    temp_converted = _ffi.cast("Temporal *", temp)
    _lib.temporal_restart(temp_converted, count)
    _check_error()


def temporal_tsequence(temp: "const Temporal *", interp: "interpType") -> "TSequence *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.temporal_tsequence(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_tsequenceset(
    temp: "const Temporal *", interp: "interpType"
) -> "TSequenceSet *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.temporal_tsequenceset(temp_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_shift_time(
    inst: "const TInstant *", interv: "const Interval *"
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    interv_converted = _ffi.cast("const Interval *", interv)
    result = _lib.tinstant_shift_time(inst_converted, interv_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_to_tsequence(
    inst: "const TInstant *", interp: "interpType"
) -> "TSequence *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tinstant_to_tsequence(inst_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_to_tsequence_free(
    inst: "TInstant *", interp: "interpType"
) -> "TSequence *":
    inst_converted = _ffi.cast("TInstant *", inst)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tinstant_to_tsequence_free(inst_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_to_tsequenceset(
    inst: "const TInstant *", interp: "interpType"
) -> "TSequenceSet *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tinstant_to_tsequenceset(inst_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_shift_scale_value(
    temp: "const Temporal *",
    shift: "Datum",
    width: "Datum",
    hasshift: bool,
    haswidth: bool,
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.tnumber_shift_scale_value(
        temp_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_shift_value(inst: "const TInstant *", shift: "Datum") -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    shift_converted = _ffi.cast("Datum", shift)
    result = _lib.tnumberinst_shift_value(inst_converted, shift_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_shift_scale_value(
    seq: "const TSequence *",
    shift: "Datum",
    width: "Datum",
    hasshift: bool,
    haswidth: bool,
) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    shift_converted = _ffi.cast("Datum", shift)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.tnumberseq_shift_scale_value(
        seq_converted, shift_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_shift_scale_value(
    ss: "const TSequenceSet *",
    start: "Datum",
    width: "Datum",
    hasshift: bool,
    haswidth: bool,
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    start_converted = _ffi.cast("Datum", start)
    width_converted = _ffi.cast("Datum", width)
    result = _lib.tnumberseqset_shift_scale_value(
        ss_converted, start_converted, width_converted, hasshift, haswidth
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_compact(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_compact(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restart(seq: "TSequence *", count: int) -> None:
    seq_converted = _ffi.cast("TSequence *", seq)
    _lib.tsequence_restart(seq_converted, count)
    _check_error()


def tsequence_set_interp(
    seq: "const TSequence *", interp: "interpType"
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_set_interp(seq_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_shift_scale_time(
    seq: "const TSequence *", shift: "const Interval *", duration: "const Interval *"
) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    shift_converted = _ffi.cast("const Interval *", shift)
    duration_converted = _ffi.cast("const Interval *", duration)
    result = _lib.tsequence_shift_scale_time(
        seq_converted, shift_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_subseq(
    seq: "const TSequence *", from_: int, to: int, lower_inc: bool, upper_inc: bool
) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_subseq(seq_converted, from_, to, lower_inc, upper_inc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tinstant(seq: "const TSequence *") -> "TInstant *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_to_tinstant(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tsequenceset(seq: "const TSequence *") -> "TSequenceSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_to_tsequenceset(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tsequenceset_free(seq: "TSequence *") -> "TSequenceSet *":
    seq_converted = _ffi.cast("TSequence *", seq)
    result = _lib.tsequence_to_tsequenceset_free(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_to_tsequenceset_interp(
    seq: "const TSequence *", interp: "interpType"
) -> "TSequenceSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequence_to_tsequenceset_interp(seq_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_compact(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restart(ss: "TSequenceSet *", count: int) -> None:
    ss_converted = _ffi.cast("TSequenceSet *", ss)
    _lib.tsequenceset_restart(ss_converted, count)
    _check_error()


def tsequenceset_set_interp(
    ss: "const TSequenceSet *", interp: "interpType"
) -> "Temporal *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    interp_converted = _ffi.cast("interpType", interp)
    result = _lib.tsequenceset_set_interp(ss_converted, interp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_shift_scale_time(
    ss: "const TSequenceSet *", start: "const Interval *", duration: "const Interval *"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    start_converted = _ffi.cast("const Interval *", start)
    duration_converted = _ffi.cast("const Interval *", duration)
    result = _lib.tsequenceset_shift_scale_time(
        ss_converted, start_converted, duration_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_discrete(ss: "const TSequenceSet *") -> "TSequence *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_to_discrete(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_linear(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_to_linear(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_step(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_to_step(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_tinstant(ss: "const TSequenceSet *") -> "TInstant *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_to_tinstant(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_to_tsequence(ss: "const TSequenceSet *") -> "TSequence *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_to_tsequence(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_merge(
    inst1: "const TInstant *", inst2: "const TInstant *"
) -> "Temporal *":
    inst1_converted = _ffi.cast("const TInstant *", inst1)
    inst2_converted = _ffi.cast("const TInstant *", inst2)
    result = _lib.tinstant_merge(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_merge_array(instants: "const TInstant **", count: int) -> "Temporal *":
    instants_converted = [_ffi.cast("const TInstant *", x) for x in instants]
    result = _lib.tinstant_merge_array(instants_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_append_tinstant(
    seq: "TSequence *",
    inst: "const TInstant *",
    maxdist: float,
    maxt: "const Interval *",
    expand: bool,
) -> "Temporal *":
    seq_converted = _ffi.cast("TSequence *", seq)
    inst_converted = _ffi.cast("const TInstant *", inst)
    maxt_converted = _ffi.cast("const Interval *", maxt)
    result = _lib.tsequence_append_tinstant(
        seq_converted, inst_converted, maxdist, maxt_converted, expand
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_append_tsequence(
    seq1: "TSequence *", seq2: "const TSequence *", expand: bool
) -> "Temporal *":
    seq1_converted = _ffi.cast("TSequence *", seq1)
    seq2_converted = _ffi.cast("const TSequence *", seq2)
    result = _lib.tsequence_append_tsequence(seq1_converted, seq2_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_timestamptz(
    seq: "const TSequence *", t: int, connect: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tsequence_delete_timestamptz(seq_converted, t_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_tstzset(
    seq: "const TSequence *", s: "const Set *", connect: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tsequence_delete_tstzset(seq_converted, s_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_tstzspan(
    seq: "const TSequence *", s: "const Span *", connect: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tsequence_delete_tstzspan(seq_converted, s_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_delete_tstzspanset(
    seq: "const TSequence *", ss: "const SpanSet *", connect: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tsequence_delete_tstzspanset(seq_converted, ss_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_insert(
    seq1: "const TSequence *", seq2: "const TSequence *", connect: bool
) -> "Temporal *":
    seq1_converted = _ffi.cast("const TSequence *", seq1)
    seq2_converted = _ffi.cast("const TSequence *", seq2)
    result = _lib.tsequence_insert(seq1_converted, seq2_converted, connect)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_merge(
    seq1: "const TSequence *", seq2: "const TSequence *"
) -> "Temporal *":
    seq1_converted = _ffi.cast("const TSequence *", seq1)
    seq2_converted = _ffi.cast("const TSequence *", seq2)
    result = _lib.tsequence_merge(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_merge_array(sequences: "const TSequence **", count: int) -> "Temporal *":
    sequences_converted = [_ffi.cast("const TSequence *", x) for x in sequences]
    result = _lib.tsequence_merge_array(sequences_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_append_tinstant(
    ss: "TSequenceSet *",
    inst: "const TInstant *",
    maxdist: float,
    maxt: "const Interval *",
    expand: bool,
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("TSequenceSet *", ss)
    inst_converted = _ffi.cast("const TInstant *", inst)
    maxt_converted = _ffi.cast("const Interval *", maxt)
    result = _lib.tsequenceset_append_tinstant(
        ss_converted, inst_converted, maxdist, maxt_converted, expand
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_append_tsequence(
    ss: "TSequenceSet *", seq: "const TSequence *", expand: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("TSequenceSet *", ss)
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequenceset_append_tsequence(ss_converted, seq_converted, expand)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_timestamptz(
    ss: "const TSequenceSet *", t: int
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tsequenceset_delete_timestamptz(ss_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_tstzset(
    ss: "const TSequenceSet *", s: "const Set *"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tsequenceset_delete_tstzset(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_tstzspan(
    ss: "const TSequenceSet *", s: "const Span *"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tsequenceset_delete_tstzspan(ss_converted, s_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_delete_tstzspanset(
    ss: "const TSequenceSet *", ps: "const SpanSet *"
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    ps_converted = _ffi.cast("const SpanSet *", ps)
    result = _lib.tsequenceset_delete_tstzspanset(ss_converted, ps_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_insert(
    ss1: "const TSequenceSet *", ss2: "const TSequenceSet *"
) -> "TSequenceSet *":
    ss1_converted = _ffi.cast("const TSequenceSet *", ss1)
    ss2_converted = _ffi.cast("const TSequenceSet *", ss2)
    result = _lib.tsequenceset_insert(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_merge(
    ss1: "const TSequenceSet *", ss2: "const TSequenceSet *"
) -> "TSequenceSet *":
    ss1_converted = _ffi.cast("const TSequenceSet *", ss1)
    ss2_converted = _ffi.cast("const TSequenceSet *", ss2)
    result = _lib.tsequenceset_merge(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_merge_array(
    seqsets: "const TSequenceSet **", count: int
) -> "TSequenceSet *":
    seqsets_converted = [_ffi.cast("const TSequenceSet *", x) for x in seqsets]
    result = _lib.tsequenceset_merge_array(seqsets_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_expand_bbox(seq: "TSequence *", inst: "const TInstant *") -> None:
    seq_converted = _ffi.cast("TSequence *", seq)
    inst_converted = _ffi.cast("const TInstant *", inst)
    _lib.tsequence_expand_bbox(seq_converted, inst_converted)
    _check_error()


def tsequence_set_bbox(seq: "const TSequence *", box: "void *") -> None:
    seq_converted = _ffi.cast("const TSequence *", seq)
    box_converted = _ffi.cast("void *", box)
    _lib.tsequence_set_bbox(seq_converted, box_converted)
    _check_error()


def tsequenceset_expand_bbox(ss: "TSequenceSet *", seq: "const TSequence *") -> None:
    ss_converted = _ffi.cast("TSequenceSet *", ss)
    seq_converted = _ffi.cast("const TSequence *", seq)
    _lib.tsequenceset_expand_bbox(ss_converted, seq_converted)
    _check_error()


def tsequenceset_set_bbox(ss: "const TSequenceSet *", box: "void *") -> None:
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    box_converted = _ffi.cast("void *", box)
    _lib.tsequenceset_set_bbox(ss_converted, box_converted)
    _check_error()


def tdiscseq_restrict_minmax(
    seq: "const TSequence *", min: bool, atfunc: bool
) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tdiscseq_restrict_minmax(seq_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tcontseq_restrict_minmax(
    seq: "const TSequence *", min: bool, atfunc: bool
) -> "TSequenceSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tcontseq_restrict_minmax(seq_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_bbox_restrict_set(temp: "const Temporal *", set: "const Set *") -> "bool":
    temp_converted = _ffi.cast("const Temporal *", temp)
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.temporal_bbox_restrict_set(temp_converted, set_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_minmax(
    temp: "const Temporal *", min: bool, atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_restrict_minmax(temp_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_timestamptz(
    temp: "const Temporal *", t: int, atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.temporal_restrict_timestamptz(temp_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_tstzset(
    temp: "const Temporal *", s: "const Set *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.temporal_restrict_tstzset(temp_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_tstzspan(
    temp: "const Temporal *", s: "const Span *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.temporal_restrict_tstzspan(temp_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_tstzspanset(
    temp: "const Temporal *", ss: "const SpanSet *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.temporal_restrict_tstzspanset(temp_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_value(
    temp: "const Temporal *", value: "Datum", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.temporal_restrict_value(temp_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_restrict_values(
    temp: "const Temporal *", set: "const Set *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.temporal_restrict_values(temp_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_value_at_timestamptz(
    temp: "const Temporal *", t: int, strict: bool
) -> "Datum *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    t_converted = _ffi.cast("TimestampTz", t)
    out_result = _ffi.new("Datum *")
    result = _lib.temporal_value_at_timestamptz(
        temp_converted, t_converted, strict, out_result
    )
    _check_error()
    if result:
        return out_result if out_result != _ffi.NULL else None
    return None


def tinstant_restrict_tstzspan(
    inst: "const TInstant *", period: "const Span *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tinstant_restrict_tstzspan(inst_converted, period_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_tstzspanset(
    inst: "const TInstant *", ss: "const SpanSet *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tinstant_restrict_tstzspanset(inst_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_timestamptz(
    inst: "const TInstant *", t: int, atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tinstant_restrict_timestamptz(inst_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_tstzset(
    inst: "const TInstant *", s: "const Set *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tinstant_restrict_tstzset(inst_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_value(
    inst: "const TInstant *", value: "Datum", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.tinstant_restrict_value(inst_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_restrict_values(
    inst: "const TInstant *", set: "const Set *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    set_converted = _ffi.cast("const Set *", set)
    result = _lib.tinstant_restrict_values(inst_converted, set_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_restrict_span(
    temp: "const Temporal *", span: "const Span *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    span_converted = _ffi.cast("const Span *", span)
    result = _lib.tnumber_restrict_span(temp_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_restrict_spanset(
    temp: "const Temporal *", ss: "const SpanSet *", atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tnumber_restrict_spanset(temp_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_restrict_span(
    inst: "const TInstant *", span: "const Span *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    span_converted = _ffi.cast("const Span *", span)
    result = _lib.tnumberinst_restrict_span(inst_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_restrict_spanset(
    inst: "const TInstant *", ss: "const SpanSet *", atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tnumberinst_restrict_spanset(inst_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_restrict_span(
    ss: "const TSequenceSet *", span: "const Span *", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    span_converted = _ffi.cast("const Span *", span)
    result = _lib.tnumberseqset_restrict_span(ss_converted, span_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_restrict_spanset(
    ss: "const TSequenceSet *", spanset: "const SpanSet *", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    spanset_converted = _ffi.cast("const SpanSet *", spanset)
    result = _lib.tnumberseqset_restrict_spanset(
        ss_converted, spanset_converted, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_restrict_geom_time(
    temp: "const Temporal *",
    gs: "const GSERIALIZED *",
    zspan: "const Span *",
    period: "const Span *",
    atfunc: bool,
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = _ffi.cast("const Span *", zspan)
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpoint_restrict_geom_time(
        temp_converted, gs_converted, zspan_converted, period_converted, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_restrict_stbox(
    temp: "const Temporal *", box: "const STBox *", border_inc: bool, atfunc: bool
) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpoint_restrict_stbox(
        temp_converted, box_converted, border_inc, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_restrict_geom_time(
    inst: "const TInstant *",
    gs: "const GSERIALIZED *",
    zspan: "const Span *",
    period: "const Span *",
    atfunc: bool,
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = _ffi.cast("const Span *", zspan)
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpointinst_restrict_geom_time(
        inst_converted, gs_converted, zspan_converted, period_converted, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_restrict_stbox(
    inst: "const TInstant *", box: "const STBox *", border_inc: bool, atfunc: bool
) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpointinst_restrict_stbox(
        inst_converted, box_converted, border_inc, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_restrict_geom_time(
    seq: "const TSequence *",
    gs: "const GSERIALIZED *",
    zspan: "const Span *",
    period: "const Span *",
    atfunc: bool,
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = _ffi.cast("const Span *", zspan)
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpointseq_restrict_geom_time(
        seq_converted, gs_converted, zspan_converted, period_converted, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_restrict_stbox(
    seq: "const TSequence *", box: "const STBox *", border_inc: bool, atfunc: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpointseq_restrict_stbox(
        seq_converted, box_converted, border_inc, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_restrict_geom_time(
    ss: "const TSequenceSet *",
    gs: "const GSERIALIZED *",
    zspan: "const Span *",
    period: "const Span *",
    atfunc: bool,
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    gs_converted = _ffi.cast("const GSERIALIZED *", gs)
    zspan_converted = _ffi.cast("const Span *", zspan)
    period_converted = _ffi.cast("const Span *", period)
    result = _lib.tpointseqset_restrict_geom_time(
        ss_converted, gs_converted, zspan_converted, period_converted, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_restrict_stbox(
    ss: "const TSequenceSet *", box: "const STBox *", border_inc: bool, atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    box_converted = _ffi.cast("const STBox *", box)
    result = _lib.tpointseqset_restrict_stbox(
        ss_converted, box_converted, border_inc, atfunc
    )
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_at_timestamptz(seq: "const TSequence *", t: int) -> "TInstant *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tsequence_at_timestamptz(seq_converted, t_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_tstzspan(
    seq: "const TSequence *", s: "const Span *", atfunc: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tsequence_restrict_tstzspan(seq_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_restrict_tstzspanset(
    seq: "const TSequence *", ss: "const SpanSet *", atfunc: bool
) -> "Temporal *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    ss_converted = _ffi.cast("const SpanSet *", ss)
    result = _lib.tsequence_restrict_tstzspanset(seq_converted, ss_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_minmax(
    ss: "const TSequenceSet *", min: bool, atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_restrict_minmax(ss_converted, min, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_tstzspan(
    ss: "const TSequenceSet *", s: "const Span *", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("const Span *", s)
    result = _lib.tsequenceset_restrict_tstzspan(ss_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_tstzspanset(
    ss: "const TSequenceSet *", ps: "const SpanSet *", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    ps_converted = _ffi.cast("const SpanSet *", ps)
    result = _lib.tsequenceset_restrict_tstzspanset(ss_converted, ps_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_timestamptz(
    ss: "const TSequenceSet *", t: int, atfunc: bool
) -> "Temporal *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    t_converted = _ffi.cast("TimestampTz", t)
    result = _lib.tsequenceset_restrict_timestamptz(ss_converted, t_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_tstzset(
    ss: "const TSequenceSet *", s: "const Set *", atfunc: bool
) -> "Temporal *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tsequenceset_restrict_tstzset(ss_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_value(
    ss: "const TSequenceSet *", value: "Datum", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.tsequenceset_restrict_value(ss_converted, value_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_restrict_values(
    ss: "const TSequenceSet *", s: "const Set *", atfunc: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    s_converted = _ffi.cast("const Set *", s)
    result = _lib.tsequenceset_restrict_values(ss_converted, s_converted, atfunc)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_cmp(inst1: "const TInstant *", inst2: "const TInstant *") -> "int":
    inst1_converted = _ffi.cast("const TInstant *", inst1)
    inst2_converted = _ffi.cast("const TInstant *", inst2)
    result = _lib.tinstant_cmp(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tinstant_eq(inst1: "const TInstant *", inst2: "const TInstant *") -> "bool":
    inst1_converted = _ffi.cast("const TInstant *", inst1)
    inst2_converted = _ffi.cast("const TInstant *", inst2)
    result = _lib.tinstant_eq(inst1_converted, inst2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_cmp(seq1: "const TSequence *", seq2: "const TSequence *") -> "int":
    seq1_converted = _ffi.cast("const TSequence *", seq1)
    seq2_converted = _ffi.cast("const TSequence *", seq2)
    result = _lib.tsequence_cmp(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_eq(seq1: "const TSequence *", seq2: "const TSequence *") -> "bool":
    seq1_converted = _ffi.cast("const TSequence *", seq1)
    seq2_converted = _ffi.cast("const TSequence *", seq2)
    result = _lib.tsequence_eq(seq1_converted, seq2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_cmp(ss1: "const TSequenceSet *", ss2: "const TSequenceSet *") -> "int":
    ss1_converted = _ffi.cast("const TSequenceSet *", ss1)
    ss2_converted = _ffi.cast("const TSequenceSet *", ss2)
    result = _lib.tsequenceset_cmp(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_eq(ss1: "const TSequenceSet *", ss2: "const TSequenceSet *") -> "bool":
    ss1_converted = _ffi.cast("const TSequenceSet *", ss1)
    ss2_converted = _ffi.cast("const TSequenceSet *", ss2)
    result = _lib.tsequenceset_eq(ss1_converted, ss2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_eq_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tpointinst_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tpointinst_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tpointseq_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tpointseq_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tpointseqset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tpointseqset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_eq_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_eq_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ne_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tpointinst_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tpointinst_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tpointseq_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tpointseq_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tpointseqset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tpointseqset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ne_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ne_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_ge_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ge_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ge_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ge_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_ge_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_ge_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_gt_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_gt_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_gt_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_gt_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_gt_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_gt_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_le_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_le_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_le_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_le_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_le_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_le_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.always_lt_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_lt_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_lt_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_lt_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def always_lt_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.always_lt_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_eq_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tpointinst_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tpointinst_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tpointseq_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tpointseq_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tpointseqset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tpointseqset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_eq_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_eq_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ne_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tpointinst_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tpointinst_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tpointseq_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tpointseq_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tpointseqset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tpointseqset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ne_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ne_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_ge_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ge_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ge_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ge_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_ge_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_ge_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_gt_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_gt_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_gt_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_gt_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_gt_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_gt_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_le_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_le_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_tinstant_base(inst: "const TInstant *", value: "Datum") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_le_tinstant_base(inst_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_tsequence_base(seq: "const TSequence *", value: "Datum") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_le_tsequence_base(seq_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_le_tsequenceset_base(ss: "const TSequenceSet *", value: "Datum") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_le_tsequenceset_base(ss_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_base_temporal(value: "Datum", temp: "const Temporal *") -> "int":
    value_converted = _ffi.cast("Datum", value)
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.ever_lt_base_temporal(value_converted, temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def ever_lt_temporal_base(temp: "const Temporal *", value: "Datum") -> "int":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.ever_lt_temporal_base(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseq_derivative(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tfloatseq_derivative(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tfloatseqset_derivative(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tfloatseqset_derivative(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberinst_abs(inst: "const TInstant *") -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tnumberinst_abs(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_abs(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_abs(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_angular_difference(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_angular_difference(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_delta_value(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_delta_value(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_abs(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_abs(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_angular_difference(ss: "const TSequenceSet *") -> "TSequence *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_angular_difference(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_delta_value(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_delta_value(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def distance_tnumber_number(temp: "const Temporal *", value: "Datum") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.distance_tnumber_number(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tbox_tbox(box1: "const TBox *", box2: "const TBox *") -> "Datum":
    box1_converted = _ffi.cast("const TBox *", box1)
    box2_converted = _ffi.cast("const TBox *", box2)
    result = _lib.nad_tbox_tbox(box1_converted, box2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tnumber_number(temp: "const Temporal *", value: "Datum") -> "Datum":
    temp_converted = _ffi.cast("const Temporal *", temp)
    value_converted = _ffi.cast("Datum", value)
    result = _lib.nad_tnumber_number(temp_converted, value_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tnumber_tbox(temp: "const Temporal *", box: "const TBox *") -> "Datum":
    temp_converted = _ffi.cast("const Temporal *", temp)
    box_converted = _ffi.cast("const TBox *", box)
    result = _lib.nad_tnumber_tbox(temp_converted, box_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def nad_tnumber_tnumber(
    temp1: "const Temporal *", temp2: "const Temporal *"
) -> "Datum":
    temp1_converted = _ffi.cast("const Temporal *", temp1)
    temp2_converted = _ffi.cast("const Temporal *", temp2)
    result = _lib.nad_tnumber_tnumber(temp1_converted, temp2_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_srid(inst: "const TInstant *") -> "int":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tpointinst_srid(inst_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_trajectory(seq: "const TSequence *") -> "GSERIALIZED *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_trajectory(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_azimuth(seq: "const TSequence *") -> "TSequenceSet *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_azimuth(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_cumulative_length(
    seq: "const TSequence *", prevlength: float
) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_cumulative_length(seq_converted, prevlength)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_is_simple(seq: "const TSequence *") -> "bool":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_is_simple(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_length(seq: "const TSequence *") -> "double":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_length(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_speed(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_speed(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_srid(seq: "const TSequence *") -> "int":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_srid(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_stboxes(seq: "const TSequence *") -> "Tuple['STBox *', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tpointseq_stboxes(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_azimuth(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_azimuth(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_cumulative_length(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_cumulative_length(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_is_simple(ss: "const TSequenceSet *") -> "bool":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_is_simple(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_length(ss: "const TSequenceSet *") -> "double":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_length(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_speed(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_speed(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_srid(ss: "const TSequenceSet *") -> "int":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_srid(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_stboxes(ss: "const TSequenceSet *") -> "Tuple['STBox *', 'int']":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tpointseqset_stboxes(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_trajectory(ss: "const TSequenceSet *") -> "GSERIALIZED *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_trajectory(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpoint_get_coord(temp: "const Temporal *", coord: int) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tpoint_get_coord(temp_converted, coord)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointinst_tgeogpointinst(inst: "const TInstant *", oper: bool) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    result = _lib.tgeompointinst_tgeogpointinst(inst_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseq_tgeogpointseq(seq: "const TSequence *", oper: bool) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tgeompointseq_tgeogpointseq(seq_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompointseqset_tgeogpointseqset(
    ss: "const TSequenceSet *", oper: bool
) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tgeompointseqset_tgeogpointseqset(ss_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tgeompoint_tgeogpoint(temp: "const Temporal *", oper: bool) -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.tgeompoint_tgeogpoint(temp_converted, oper)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointinst_set_srid(inst: "const TInstant *", srid: int) -> "TInstant *":
    inst_converted = _ffi.cast("const TInstant *", inst)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpointinst_set_srid(inst_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_make_simple(seq: "const TSequence *") -> "Tuple['TSequence **', 'int']":
    seq_converted = _ffi.cast("const TSequence *", seq)
    count = _ffi.new("int *")
    result = _lib.tpointseq_make_simple(seq_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseq_set_srid(seq: "const TSequence *", srid: int) -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpointseq_set_srid(seq_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_make_simple(
    ss: "const TSequenceSet *",
) -> "Tuple['TSequence **', 'int']":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    count = _ffi.new("int *")
    result = _lib.tpointseqset_make_simple(ss_converted, count)
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tpointseqset_set_srid(ss: "const TSequenceSet *", srid: int) -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    srid_converted = _ffi.cast("int32", srid)
    result = _lib.tpointseqset_set_srid(ss_converted, srid_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_integral(seq: "const TSequence *") -> "double":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_integral(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_twavg(seq: "const TSequence *") -> "double":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_twavg(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_integral(ss: "const TSequenceSet *") -> "double":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_integral(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_twavg(ss: "const TSequenceSet *") -> "double":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_twavg(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_twcentroid(seq: "const TSequence *") -> "GSERIALIZED *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_twcentroid(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_twcentroid(ss: "const TSequenceSet *") -> "GSERIALIZED *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_twcentroid(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_compact(temp: "const Temporal *") -> "Temporal *":
    temp_converted = _ffi.cast("const Temporal *", temp)
    result = _lib.temporal_compact(temp_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequence_compact(seq: "const TSequence *") -> "TSequence *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tsequence_compact(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tsequenceset_compact(ss: "const TSequenceSet *") -> "TSequenceSet *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tsequenceset_compact(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def skiplist_free(list: "SkipList *") -> None:
    list_converted = _ffi.cast("SkipList *", list)
    _lib.skiplist_free(list_converted)
    _check_error()


def temporal_app_tinst_transfn(
    state: "Temporal *", inst: "const TInstant *", maxdist: float, maxt: "Interval *"
) -> "Temporal *":
    state_converted = _ffi.cast("Temporal *", state)
    inst_converted = _ffi.cast("const TInstant *", inst)
    maxt_converted = _ffi.cast("Interval *", maxt)
    result = _lib.temporal_app_tinst_transfn(
        state_converted, inst_converted, maxdist, maxt_converted
    )
    _check_error()
    return result if result != _ffi.NULL else None


def temporal_app_tseq_transfn(
    state: "Temporal *", seq: "const TSequence *"
) -> "Temporal *":
    state_converted = _ffi.cast("Temporal *", state)
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.temporal_app_tseq_transfn(state_converted, seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_integral(seq: "const TSequence *") -> "double":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_integral(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseq_twavg(seq: "const TSequence *") -> "double":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tnumberseq_twavg(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_integral(ss: "const TSequenceSet *") -> "double":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_integral(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumberseqset_twavg(ss: "const TSequenceSet *") -> "double":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tnumberseqset_twavg(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseq_twcentroid(seq: "const TSequence *") -> "GSERIALIZED *":
    seq_converted = _ffi.cast("const TSequence *", seq)
    result = _lib.tpointseq_twcentroid(seq_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tpointseqset_twcentroid(ss: "const TSequenceSet *") -> "GSERIALIZED *":
    ss_converted = _ffi.cast("const TSequenceSet *", ss)
    result = _lib.tpointseqset_twcentroid(ss_converted)
    _check_error()
    return result if result != _ffi.NULL else None


def tnumber_value_split(
    temp: "const Temporal *", size: "Datum", origin: "Datum", buckets: "Datum **"
) -> "Tuple['Temporal **', 'int']":
    temp_converted = _ffi.cast("const Temporal *", temp)
    size_converted = _ffi.cast("Datum", size)
    origin_converted = _ffi.cast("Datum", origin)
    buckets_converted = [_ffi.cast("Datum *", x) for x in buckets]
    count = _ffi.new("int *")
    result = _lib.tnumber_value_split(
        temp_converted, size_converted, origin_converted, buckets_converted, count
    )
    _check_error()
    return result if result != _ffi.NULL else None, count[0]


def tbox_tile(
    value: "Datum",
    t: int,
    vsize: "Datum",
    duration: "Interval *",
    vorigin: "Datum",
    torigin: int,
    basetype: "meosType",
) -> "TBox *":
    value_converted = _ffi.cast("Datum", value)
    t_converted = _ffi.cast("TimestampTz", t)
    vsize_converted = _ffi.cast("Datum", vsize)
    duration_converted = _ffi.cast("Interval *", duration)
    vorigin_converted = _ffi.cast("Datum", vorigin)
    torigin_converted = _ffi.cast("TimestampTz", torigin)
    basetype_converted = _ffi.cast("meosType", basetype)
    result = _lib.tbox_tile(
        value_converted,
        t_converted,
        vsize_converted,
        duration_converted,
        vorigin_converted,
        torigin_converted,
        basetype_converted,
    )
    _check_error()
    return result if result != _ffi.NULL else None
