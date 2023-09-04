from typing import Callable


def array_length_remover_modifier(list_name: str, length_param_name: str = 'count') -> Callable[[str], str]:
    return lambda function: function \
        .replace(f', {length_param_name}: int', '') \
        .replace(f', {length_param_name}', f', len({list_name})')


def meos_initialize_modifier(_: str) -> str:
    return """def meos_initialize(tz_str: "Optional[str]") -> None:
    tz_str_converted = tz_str.encode('utf-8') if tz_str is not None else _ffi.NULL
    _lib.meos_initialize(tz_str_converted, _lib.py_error_handler)"""


def remove_error_check_modifier(function: str) -> str:
    return function.replace('    _check_error()\n', '')


def cstring2text_modifier(_: str) -> str:
    return """def cstring2text(cstring: str) -> 'text *':
    cstring_converted = cstring.encode('utf-8')
    result = _lib.cstring2text(cstring_converted)
    return result"""


def text2cstring_modifier(_: str) -> str:
    return """def text2cstring(textptr: 'text *') -> str:
    result = _lib.text2cstring(textptr)
    result = _ffi.string(result).decode('utf-8')
    return result"""


def from_wkb_modifier(function: str, return_type: str) -> Callable[[str], str]:
    return lambda _: f"""def {function}(wkb: bytes) -> '{return_type} *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.{function}(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None"""


def as_wkb_modifier(function: str) -> str:
    return function \
        .replace('-> "Tuple[\'uint8_t *\', \'size_t *\']":', '-> bytes:') \
        .replace('return result if result != _ffi.NULL else None, size_out[0]',
                 'result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None\n'
                 '    return result_converted')


def timestampset_make_modifier(function: str) -> str:
    return function \
        .replace('values: int', 'values: List[int]') \
        .replace("values_converted = _ffi.cast('const TimestampTz *', values)",
                 "values_converted = [_ffi.cast('const TimestampTz', x) for x in values]")


def tbool_at_values_modifier(function: str) -> str:
    return function \
        .replace("values: 'bool *', count: int", 'values: List[bool]') \
        .replace("_ffi.cast('bool *', values)",
                 "_ffi.new('bool []', values)") \
        .replace(', count', ', len(values_converted)')


def tbool_minus_values_modifier(function: str) -> str:
    return tbool_at_values_modifier(function)


def tint_at_values_modifier(function: str) -> str:
    return function \
        .replace("values: 'int *', count: int", 'values: List[int]') \
        .replace("_ffi.cast('int *', values)",
                 "_ffi.new('int []', values)") \
        .replace(', count', ', len(values_converted)')


def tint_minus_values_modifier(function: str) -> str:
    return tint_at_values_modifier(function)


def tfloat_at_values_modifier(function: str) -> str:
    return function \
        .replace("values: 'double *', count: int", 'values: List[float]') \
        .replace("_ffi.cast('double *', values)",
                 "_ffi.new('double []', values)") \
        .replace(', count', ', len(values_converted)')


def tfloat_minus_values_modifier(function: str) -> str:
    return tfloat_at_values_modifier(function)


def spanset_make_modifier(function: str) -> str:
    return function \
        .replace("spans: 'Span *', count: int", "spans: 'List[Span *]'") \
        .replace("_ffi.cast('Span *', spans)",
                 "_ffi.new('Span []', spans)") \
        .replace(', count', ', len(spans)')


def gserialized_from_lwgeom_modifier(function: str) -> str:
    return function \
        .replace(", size: 'size_t *'", '') \
        .replace("_ffi.cast('size_t *', size)", '_ffi.NULL')


def tpointseq_make_coords_modifier(function: str) -> str:
    return function \
        .replace('times: int', "times: 'const TimestampTz *'") \
        .replace("    xcoords_converted = _ffi.cast('const double *', xcoords)\n", '') \
        .replace("    ycoords_converted = _ffi.cast('const double *', ycoords)\n", '') \
        .replace("    times_converted = _ffi.cast('const TimestampTz *', times)\n", '') \
        .replace("_ffi.cast('const double *', zcoords)", 'zcoords') \
        .replace('xcoords_converted', 'xcoords') \
        .replace('ycoords_converted', 'ycoords') \
        .replace('times_converted', 'times')
