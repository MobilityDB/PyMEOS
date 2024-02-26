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
    srid = geo_get_srid(geom)
    if srid > 0:
        geometry = set_srid(geometry, srid)
    return geometry


def gserialized_to_shapely_geometry(
    geom: "const GSERIALIZED *", precision: int = 15
) -> BaseGeometry:
    text = geo_as_text(geom, precision)
    geometry = wkt.loads(text)
    srid = geo_get_srid(geom)
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
