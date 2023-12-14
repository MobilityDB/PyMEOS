import logging
from _meos_cffi import lib as _lib
from .enums import ErrorLevel

logger = logging.getLogger("pymeos_cffi")


class MeosException(Exception):
    """Base class for all MEOS errors."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.__class__.__name__} ({self.code}): {self.message}"


class MeosInternalError(MeosException):
    """Superclass for internal errors."""

    pass


class MeosArgumentError(MeosException):
    """Superclass for invalid argument errors."""

    pass


class MeosIoError(MeosException):
    """Unspecified internal error."""

    pass


class MeosInternalTypeError(MeosInternalError):
    """Internal type error."""

    pass


class MeosValueOutOfRangeError(MeosInternalError):
    """Internal out of range error."""

    pass


class MeosDivisionByZeroError(MeosInternalError):
    """Internal division by zero error."""

    pass


class MeosMemoryAllocError(MeosInternalError):
    """Internal malloc error."""

    pass


class MeosAggregationError(MeosInternalError):
    """Internal aggregation error."""

    pass


class MeosDirectoryError(MeosInternalError):
    """Internal directory error."""

    pass


class MeosFileError(MeosInternalError):
    """Internal file error."""

    pass


class MeosInvalidArgError(MeosArgumentError):
    """Invalid argument."""

    pass


class MeosInvalidArgTypeError(MeosArgumentError):
    """Invalid argument type."""

    pass


class MeosInvalidArgValueError(MeosArgumentError):
    """Invalid argument value."""

    pass


class MeosMfJsonInputError(MeosIoError):
    """MFJSON input error."""

    pass


class MeosMfJsonOutputError(MeosIoError):
    """MFJSON output error."""

    pass


class MeosTextInputError(MeosIoError):
    """Text input error."""

    pass


class MeosTextOutputError(MeosIoError):
    """Text output error."""

    pass


class MeosWkbInputError(MeosIoError):
    """WKB input error."""

    pass


class MeosWkbOutputError(MeosIoError):
    """WKB output error."""

    pass


class MeosGeoJsonInputError(MeosIoError):
    """GEOJSON input error."""

    pass


class MeosGeoJsonOutputError(MeosIoError):
    """GEOJSON output error."""

    pass


_exception_map = {
    _lib.MEOS_ERR_INTERNAL_ERROR: MeosInternalError,
    _lib.MEOS_ERR_INTERNAL_TYPE_ERROR: MeosInternalTypeError,
    _lib.MEOS_ERR_VALUE_OUT_OF_RANGE: MeosValueOutOfRangeError,
    _lib.MEOS_ERR_DIVISION_BY_ZERO: MeosDivisionByZeroError,
    _lib.MEOS_ERR_MEMORY_ALLOC_ERROR: MeosMemoryAllocError,
    _lib.MEOS_ERR_AGGREGATION_ERROR: MeosAggregationError,
    _lib.MEOS_ERR_DIRECTORY_ERROR: MeosDirectoryError,
    _lib.MEOS_ERR_FILE_ERROR: MeosFileError,
    _lib.MEOS_ERR_INVALID_ARG: MeosInvalidArgError,
    _lib.MEOS_ERR_INVALID_ARG_TYPE: MeosInvalidArgTypeError,
    _lib.MEOS_ERR_INVALID_ARG_VALUE: MeosInvalidArgValueError,
    _lib.MEOS_ERR_MFJSON_INPUT: MeosMfJsonInputError,
    _lib.MEOS_ERR_MFJSON_OUTPUT: MeosMfJsonOutputError,
    _lib.MEOS_ERR_TEXT_INPUT: MeosTextInputError,
    _lib.MEOS_ERR_TEXT_OUTPUT: MeosTextOutputError,
    _lib.MEOS_ERR_WKB_INPUT: MeosWkbInputError,
    _lib.MEOS_ERR_WKB_OUTPUT: MeosWkbOutputError,
    _lib.MEOS_ERR_GEOJSON_INPUT: MeosGeoJsonInputError,
    _lib.MEOS_ERR_GEOJSON_OUTPUT: MeosGeoJsonOutputError,
}


def report_meos_exception(level: int, code: int, message: str):
    exception_class = _exception_map.get(code, MeosException)
    exception = exception_class(code, message)
    if level == ErrorLevel.NOTICE:
        logger.info("MEOS NOTICE: ", exc_info=exception)
    elif level == ErrorLevel.WARNING:
        logger.warning("MEOS WARNING: ", exc_info=exception)
    elif level == ErrorLevel.ERROR:
        logger.error("MEOS ERROR: ", exc_info=exception)
        raise exception
    else:
        logger.error(f"Error raised with unknown level {level}: {exception}")
        raise exception
