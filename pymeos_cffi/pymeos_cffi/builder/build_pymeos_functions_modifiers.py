def period_shift_tscale_modifier(function: str) -> str:
    return function \
        .replace(') ->', ', result: "Optional[\'Period *\']") ->') \
        .replace("out_result = _ffi.new('Period *')", "out_result = _ffi.cast('Period *', result)")


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


def timestampset_make_modifier(function: str) -> str:
    return function \
        .replace('times: int', 'times: List[int]') \
        .replace("times_converted = _ffi.cast('const TimestampTz *', times)",
                 "times_converted = [_ffi.cast('const TimestampTz', x) for x in times]")


def gserialized_from_lwgeom_modifier(function: str) -> str:
    return function \
        .replace(", size: 'size_t *'", '') \
        .replace("_ffi.cast('size_t *', size)", '_ffi.NULL')
