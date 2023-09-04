from enum import IntEnum


class MEOSCode(IntEnum):
    MEOS_SUCCESS = 0,  # Successful operation

    MEOS_ERR_INTERNAL_ERROR = 1,  # Unspecified internal error
    MEOS_ERR_INTERNAL_TYPE_ERROR = 2,  # Internal type error
    MEOS_ERR_VALUE_OUT_OF_RANGE = 3,  # Internal out of range error
    MEOS_ERR_DIVISION_BY_ZERO = 4,  # Internal division by zero error
    MEOS_ERR_MEMORY_ALLOC_ERROR = 5,  # Internal malloc error
    MEOS_ERR_AGGREGATION_ERROR = 6,  # Internal aggregation error
    MEOS_ERR_DIRECTORY_ERROR = 7,  # Internal directory error
    MEOS_ERR_FILE_ERROR = 8,  # Internal file error

    MEOS_ERR_INVALID_ARG = 10,  # Invalid argument
    MEOS_ERR_INVALID_ARG_TYPE = 11,  # Invalid argument type
    MEOS_ERR_INVALID_ARG_VALUE = 12,  # Invalid argument value

    MEOS_ERR_MFJSON_INPUT = 20,  # MFJSON input error
    MEOS_ERR_MFJSON_OUTPUT = 21,  # MFJSON output error
    MEOS_ERR_TEXT_INPUT = 22,  # Text input error
    MEOS_ERR_TEXT_OUTPUT = 23,  # Text output error
    MEOS_ERR_WKB_INPUT = 24,  # WKB input error
    MEOS_ERR_WKB_OUTPUT = 25,  # WKB output error
    MEOS_ERR_GEOJSON_INPUT = 26,  # GEOJSON input error
    MEOS_ERR_GEOJSON_OUTPUT = 27,  # GEOJSON output error


class MeosException(Exception):
    """Base class for all MEOS errors."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


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


def raise_meos_exception(level: int, code: int, message: str):
    if code == MEOSCode.MEOS_ERR_INTERNAL_ERROR:
        raise MeosInternalError(code, message)
    elif code == MEOSCode.MEOS_ERR_INTERNAL_TYPE_ERROR:
        raise MeosInternalTypeError(code, message)
    elif code == MEOSCode.MEOS_ERR_VALUE_OUT_OF_RANGE:
        raise MeosValueOutOfRangeError(code, message)
    elif code == MEOSCode.MEOS_ERR_DIVISION_BY_ZERO:
        raise MeosDivisionByZeroError(code, message)
    elif code == MEOSCode.MEOS_ERR_MEMORY_ALLOC_ERROR:
        raise MeosMemoryAllocError(code, message)
    elif code == MEOSCode.MEOS_ERR_AGGREGATION_ERROR:
        raise MeosAggregationError(code, message)
    elif code == MEOSCode.MEOS_ERR_DIRECTORY_ERROR:
        raise MeosDirectoryError(code, message)
    elif code == MEOSCode.MEOS_ERR_FILE_ERROR:
        raise MeosFileError(code, message)
    elif code == MEOSCode.MEOS_ERR_INVALID_ARG:
        raise MeosInvalidArgError(code, message)
    elif code == MEOSCode.MEOS_ERR_INVALID_ARG_TYPE:
        raise MeosInvalidArgTypeError(code, message)
    elif code == MEOSCode.MEOS_ERR_INVALID_ARG_VALUE:
        raise MeosInvalidArgValueError(code, message)
    elif code == MEOSCode.MEOS_ERR_MFJSON_INPUT:
        raise MeosMfJsonInputError(code, message)
    elif code == MEOSCode.MEOS_ERR_MFJSON_OUTPUT:
        raise MeosMfJsonOutputError(code, message)
    elif code == MEOSCode.MEOS_ERR_TEXT_INPUT:
        raise MeosTextInputError(code, message)
    elif code == MEOSCode.MEOS_ERR_TEXT_OUTPUT:
        raise MeosTextOutputError(code, message)
    elif code == MEOSCode.MEOS_ERR_WKB_INPUT:
        raise MeosWkbInputError(code, message)
    elif code == MEOSCode.MEOS_ERR_WKB_OUTPUT:
        raise MeosWkbOutputError(code, message)
    elif code == MEOSCode.MEOS_ERR_GEOJSON_INPUT:
        raise MeosGeoJsonInputError(code, message)
    elif code == MEOSCode.MEOS_ERR_GEOJSON_OUTPUT:
        raise MeosGeoJsonOutputError(code, message)
    else:
        raise MeosException(code, f'{message}\nThe MEOS error code ({code}) has not been recognized. '
                                  f'Please, report this to the MEOS developers.')
