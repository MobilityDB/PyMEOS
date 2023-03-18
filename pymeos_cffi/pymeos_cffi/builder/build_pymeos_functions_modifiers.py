from typing import Callable


def array_length_remover_modifier(list_name: str, length_param_name: str = 'count') -> Callable[[str], str]:
    return lambda function: function \
        .replace(f', {length_param_name}: int', '') \
        .replace(f', {length_param_name}', f', len({list_name})')


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


def tstzset_make_modifier(function: str) -> str:
    return function \
        .replace('times: int', 'times: List[int]') \
        .replace("times_converted = _ffi.cast('const TimestampTz *', times)",
                 "times_converted = [_ffi.cast('const TimestampTz', x) for x in times]")


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


def tbool_at_values_modifier(function: str) -> str:
    return function \
        .replace("values: 'bool *', count: int", 'values: List[bool]') \
        .replace("_ffi.cast('bool *', values)",
                 "_ffi.new('bool []', values)") \
        .replace(', count', ', len(values_converted)')


def tbool_minus_values_modifier(function: str) -> str:
    return tbool_at_values_modifier(function)


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
