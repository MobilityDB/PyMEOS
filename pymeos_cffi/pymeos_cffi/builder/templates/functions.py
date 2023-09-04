from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List, Union

import _meos_cffi
from .errors import raise_meos_exception
import postgis as pg
import shapely.geometry as spg
from dateutil.parser import parse
from shapely import wkt, wkb, get_srid
from shapely.geometry.base import BaseGeometry
from spans.types import floatrange, intrange

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib

_error: Optional[int] = None
_error_level: Optional[int] = None
_error_message: Optional[str] = None


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


def geo_to_gserialized(geom: Union[pg.Geometry, BaseGeometry], geodetic: bool) -> 'GSERIALIZED *':
    if geodetic:
        return geography_to_gserialized(geom)
    else:
        return geometry_to_gserialized(geom)


def geometry_to_gserialized(geom: Union[pg.Geometry, BaseGeometry]) -> 'GSERIALIZED *':
    if isinstance(geom, pg.Geometry):
        text = geom.wkt
        # if geom.has_srid():
        #     text = f'SRID={geom.srid};{text}'
    elif isinstance(geom, BaseGeometry):
        text = wkt.dumps(geom)
        if get_srid(geom) > 0:
            text = f'SRID={get_srid(geom)};{text}'
    else:
        raise TypeError('Parameter geom must be either a PostGIS Geometry or a Shapely BaseGeometry')
    gs = pgis_geometry_in(text, -1)
    return gs


def geography_to_gserialized(geom: Union[pg.Geometry, BaseGeometry]) -> 'GSERIALIZED *':
    if isinstance(geom, pg.Geometry):
        text = geom.wkt
        # if geom.has_srid():
        #     text = f'SRID={geom.srid};{text}'
    elif isinstance(geom, BaseGeometry):
        text = wkt.dumps(geom)
        if get_srid(geom) > 0:
            text = f'SRID={get_srid(geom)};{text}'
    else:
        raise TypeError('Parameter geom must be either a PostGIS Geometry or a Shapely BaseGeometry')
    gs = pgis_geography_in(text, -1)
    return gs


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

