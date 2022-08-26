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
    'const char *': Conversion('const char *', 'str', lambda p_obj: f"{p_obj}.encode('utf-8')",
                               lambda c_obj: f"_ffi.string({c_obj}).decode('utf-8')"),
    'text': Conversion('text', 'str', lambda p_obj: f"cstring2text({p_obj})", lambda c_obj: f"text2cstring({c_obj})"),
    'text *': Conversion('text *', 'str', lambda p_obj: f"cstring2text({p_obj})",
                         lambda c_obj: f"text2cstring({c_obj})"),
    'const text': Conversion('const text', 'str', lambda p_obj: f"cstring2text({p_obj})",
                             lambda c_obj: f"text2cstring({c_obj})"),
    'const text *': Conversion('const text *', 'str', lambda p_obj: f"cstring2text({p_obj})",
                               lambda c_obj: f"text2cstring({c_obj})"),
    'int': Conversion('int', 'int', None, None),
    'int8': Conversion('int8', 'int', None, None),
    'int16': Conversion('int16', 'int', None, None),
    'int32': Conversion('int32', 'int', None, None),
    'int64': Conversion('int64', 'int', None, None),
    'uint8': Conversion('uint8', 'int', None, None),
    'uint16': Conversion('uint16', 'int', None, None),
    'uint32': Conversion('uint32', 'int', None, None),
    'uint64': Conversion('uint64', 'int', None, None),
    'uint8_t': Conversion('uint8_t', 'int', None, None),
    'Timestamp': Conversion('Timestamp', 'int', None, None),
    'TimestampTz': Conversion('TimestampTz', 'int', None, None),
    'TimestampTz *': Conversion('TimestampTz *', 'int', None, None),
    'const TimestampTz': Conversion('const TimestampTz', 'int', None, None),
    'const TimestampTz *': Conversion('const TimestampTz *', 'int', None, None),
    'TimeOffset': Conversion('TimeOffset', 'int', None, None),
}
