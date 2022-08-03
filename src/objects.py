from typing import Callable, Dict

import _meos_cffi

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


class Conversion:

    def __init__(self, c_type: str, p_type: str, p_to_c: Callable[[str], str], c_to_p: Callable[[str], str]) -> None:
        super().__init__()
        self.c_type = c_type
        self.p_type = p_type
        self.p_to_c = p_to_c
        self.c_to_p = c_to_p


conversion_map: Dict[str, Conversion] = {
    'void': Conversion('void', 'None', lambda p_obj: p_obj, lambda c_obj: c_obj),
    'char *': Conversion('char *', 'str', lambda p_obj: f"{p_obj}.encode('utf-8')",
                         lambda c_obj: f"_ffi.string({c_obj}).decode('utf-8')"),
    'int8': Conversion('int8', 'int', lambda p_obj: f"_ffi.cast('int8', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'int16': Conversion('int16', 'int', lambda p_obj: f"_ffi.cast('int16', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'int32': Conversion('int32', 'int', lambda p_obj: f"_ffi.cast('int32', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'int64': Conversion('int64', 'int', lambda p_obj: f"_ffi.cast('int64', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'uint8': Conversion('uint8', 'int', lambda p_obj: f"_ffi.cast('uint8', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'uint16': Conversion('uint16', 'int', lambda p_obj: f"_ffi.cast('uint16', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'uint32': Conversion('uint32', 'int', lambda p_obj: f"_ffi.cast('uint32', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'uint64': Conversion('uint64', 'int', lambda p_obj: f"_ffi.cast('uint64', {p_obj})", lambda c_obj: f"int({c_obj})"),
    'Timestamp': Conversion('Timestamp', 'int', lambda p_obj: f"_ffi.cast('Timestamp', {p_obj})",
                            lambda c_obj: f"int({c_obj})"),
    'TimestampTz': Conversion('TimestampTz', 'int', lambda p_obj: f"_ffi.cast('TimestampTz', {p_obj})",
                              lambda c_obj: f"int({c_obj})"),
    'TimeOffset': Conversion('TimeOffset', 'int', lambda p_obj: f"_ffi.cast('TimeOffset', {p_obj})",
                             lambda c_obj: f"int({c_obj})"),
}

int8 = int
int16 = int
int32 = int
int64 = int

uint8 = int
uint16 = int
uint32 = int
uint64 = int

Timestamp = int
TimestampTz = int
TimeOffset = int
