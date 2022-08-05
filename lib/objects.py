from typing import Callable, Dict, Optional

import _meos_cffi

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


class Conversion:

    def __init__(self, c_type: str, p_type: str, p_to_c: Optional[Callable[[str], str]],
                 c_to_p: Optional[Callable[[str], str]]) -> None:
        super().__init__()
        self.c_type = c_type
        self.p_type = p_type
        self.p_to_c = p_to_c
        self.c_to_p = c_to_p


conversion_map: Dict[str, Conversion] = {
    'void': Conversion('void', 'None', None, None),
    'bool': Conversion('bool', 'bool', None, None),
    'double': Conversion('double', 'float', None, None),
    'char *': Conversion('char *', 'str', lambda p_obj: f"{p_obj}.encode('utf-8')",
                         lambda c_obj: f"_ffi.string({c_obj}).decode('utf-8')"),
    'int': Conversion('int', 'int', None, None),
    'int8': Conversion('int8', 'int', lambda p_obj: f"_ffi.cast('int8', {p_obj})", None),
    'int16': Conversion('int16', 'int', lambda p_obj: f"_ffi.cast('int16', {p_obj})", None),
    'int32': Conversion('int32', 'int', lambda p_obj: f"_ffi.cast('int32', {p_obj})", None),
    'int64': Conversion('int64', 'int', lambda p_obj: f"_ffi.cast('int64', {p_obj})", None),
    'uint8': Conversion('uint8', 'int', lambda p_obj: f"_ffi.cast('uint8', {p_obj})", None),
    'uint16': Conversion('uint16', 'int', lambda p_obj: f"_ffi.cast('uint16', {p_obj})", None),
    'uint32': Conversion('uint32', 'int', lambda p_obj: f"_ffi.cast('uint32', {p_obj})", None),
    'uint64': Conversion('uint64', 'int', lambda p_obj: f"_ffi.cast('uint64', {p_obj})", None),
    'Timestamp': Conversion('Timestamp', 'int', lambda p_obj: f"_ffi.cast('Timestamp', {p_obj})", None),
    'TimestampTz': Conversion('TimestampTz', 'int', lambda p_obj: f"_ffi.cast('TimestampTz', {p_obj})", None),
    'TimeOffset': Conversion('TimeOffset', 'int', lambda p_obj: f"_ffi.cast('TimeOffset', {p_obj})", None),
}
