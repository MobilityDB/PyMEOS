import re
from typing import Callable, Optional


def array_length_remover_modifier(
    list_name: str, length_param_name: str = "count"
) -> Callable[[str], str]:
    return lambda function: function.replace(f", {length_param_name}: int", "").replace(
        f", {length_param_name}", f", len({list_name})"
    )


def array_parameter_modifier(
    list_name: str, length_param_name: Optional[str] = None
) -> Callable[[str], str]:
    def custom_array_modifier(function: str) -> str:
        type_regex = list_name + r": '([\w \*]+)'"
        match = next(re.finditer(type_regex, function))
        whole_type = match.group(1)
        base_type = " ".join(whole_type.split(" ")[:-1])
        function = function.replace(
            match.group(0), f"{list_name}: 'List[{base_type}]'"
        ).replace(
            f"_ffi.cast('{whole_type}', {list_name})",
            f"_ffi.new('{base_type} []', {list_name})",
        )
        if length_param_name:
            function = function.replace(f", {length_param_name}: int", "").replace(
                f", {length_param_name}", f", len({list_name})"
            )
        return function

    return custom_array_modifier


def textset_make_modifier(function: str) -> str:
    function = array_parameter_modifier("values", "count")(function)
    return function.replace("_ffi.cast('const text *', x)", "cstring2text(x)").replace(
        "'List[const text]'", "List[str]"
    )


def meos_initialize_modifier(_: str) -> str:
    return """def meos_initialize(tz_str: "Optional[str]") -> None:
    
    if "PROJ_DATA" not in os.environ and "PROJ_LIB" not in os.environ:
        proj_dir = os.path.join(os.path.dirname(__file__), "proj_data")
        if os.path.exists(proj_dir):
            # Assume we are in a wheel and the PROJ data is in the package
            os.environ["PROJ_DATA"] = proj_dir
            os.environ["PROJ_LIB"] = proj_dir
    
    tz_str_converted = tz_str.encode('utf-8') if tz_str is not None else _ffi.NULL
    _lib.meos_initialize(tz_str_converted, _lib.py_error_handler)"""


def remove_error_check_modifier(function: str) -> str:
    return function.replace("    _check_error()\n", "")


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
    return (
        lambda _: f"""def {function}(wkb: bytes) -> '{return_type} *':
    wkb_converted = _ffi.new('uint8_t []', wkb)
    result = _lib.{function}(wkb_converted, len(wkb))
    return result if result != _ffi.NULL else None"""
    )


def as_wkb_modifier(function: str) -> str:
    return function.replace(
        "-> \"Tuple['uint8_t *', 'size_t *']\":", "-> bytes:"
    ).replace(
        "return result if result != _ffi.NULL else None, size_out[0]",
        "result_converted = bytes(result[i] for i in range(size_out[0])) if result != _ffi.NULL else None\n"
        "    return result_converted",
    )


def tstzset_make_modifier(function: str) -> str:
    return (
        function.replace("values: int", "values: List[int]")
        .replace(", count: int", "")
        .replace(
            "values_converted = _ffi.cast('const TimestampTz *', values)",
            "values_converted = [_ffi.cast('const TimestampTz', x) for x in values]",
        )
        .replace("count", "len(values)")
    )


def spanset_make_modifier(function: str) -> str:
    return (
        function.replace("spans: 'Span *', count: int", "spans: 'List[Span *]'")
        .replace("_ffi.cast('Span *', spans)", "_ffi.new('Span []', spans)")
        .replace(", count", ", len(spans)")
    )
