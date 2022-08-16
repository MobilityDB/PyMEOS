import re
from re import RegexFlag
from typing import List, Optional, Tuple

from build_helpers import ADDITIONAL_DEFINITIONS
from pymeos_cffi.objects import conversion_map, Conversion

BASE = """from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List

import _meos_cffi
from dateutil.parser import parse

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


def create_pointer(object: 'Any', type: str) -> 'Any *':
    return _ffi.new(f'{type} *', object)


def datetime_to_timestamptz(dt: datetime) -> int:
    return _lib.pg_timestamptz_in(dt.strftime('%Y-%m-%d %H:%M:%S%z').encode('utf-8'), -1)


def timestamptz_to_datetime(ts: int) -> datetime:
    return parse(pg_timestamptz_out(ts))


def timedelta_to_interval(td: timedelta) -> Any:
    return _ffi.new('Interval *', {'time': td.microseconds + td.seconds * 1000000, 'day': td.days, 'month': 0})


def interval_to_timedelta(interval: Any) -> timedelta:
    # TODO fix for months/years
    return timedelta(days=interval.day, microseconds=interval.time)


"""

manual_functions = {
    'period_shift_tscale': 'result parameter is also input. start and duration parameters can be null.',
    'timestampset_shift_tscale': 'start and duration parameters can be null.',
    'periodset_shift_tscale': 'start and duration parameters can be null.',
    'temporal_shift_tscale': 'start and duration parameters can be null.',
    'tbox_make': 'p and s parameters can be null',
    'stbox_make': 'p parameter can be null',
    'periodset_timestamps': 'return type should be int * and int.',
    'cstring2text': "return type should be 'text *'. result shouldn't be converted using text2cstring",
    'text2cstring': "parameter type should be 'text *'. parameter shouldn't be converted using cstring2text",
    'tbool_value_at_timestamp': 'value parameter is output',
    'ttext_value_at_timestamp': 'value parameter is output',
    'tint_value_at_timestamp': 'value parameter is output',
    'tfloat_value_at_timestamp': 'value parameter is output',
    'tpoint_value_at_timestamp': 'value parameter is output',
    'timestampset_make': "times parameter cast must be to an array of integers: [_ffi.cast('const TimestampTz', x) for x in times]",
    'temporal_as_mfjson': 'srs can be null.'
}


def main():
    with open('/usr/local/include/meos.h') as f:
        content = f.read()
        content = content.replace('#', '//#')
        content = content.replace(*ADDITIONAL_DEFINITIONS)
    f_regex = r'extern (?P<returnType>(?:const )?\w+(?: \*+)?) ?(?P<function>\w+)\((?P<params>[\w ,\*]*)\);'
    matches = re.finditer(f_regex, ''.join(content.splitlines()), flags=RegexFlag.MULTILINE)

    with open('pymeos_cffi/functions.py', 'w+') as file:
        file.write(BASE)
        for match in matches:
            named = match.groupdict()
            function = named['function']
            inner_return_type = named['returnType']
            return_type, result_conversion = get_return_type(inner_return_type)
            inner_params = named['params']
            params = get_params(inner_params)
            function_string = build_function_string(function, return_type, params, result_conversion)
            file.write(function_string)
            file.write('\n\n\n')


def get_params(inner_params: str) -> List[Tuple[str, str, str, str, str]]:
    return [p for p in (get_param(param.strip()) for param in inner_params.split(',')) if p is not None]


def get_param(inner_param: str) -> Optional[Tuple[str, str, Optional[str], str, str]]:
    split = inner_param.split(' ')
    param_type = ' '.join(split[:-1])
    if split[-1].startswith('**'):
        param_type += ' **'
    elif split[-1].startswith('*'):
        param_type += ' *'
    param_name = split[-1].lstrip('*')
    if param_name == 'str':
        param_name = 'string'
    elif param_name == 'is':
        param_name = 'iset'
    elif param_name == 'void':
        return None
    conversion = get_param_conversion(param_type)
    if conversion is None:
        return param_name, 'Any', '', param_name, param_type
    if conversion.p_to_c is None:
        return param_name, conversion.p_type, None, param_name, param_type
    return param_name, conversion.p_type, f'{param_name}_converted = {conversion.p_to_c(param_name)}', f'{param_name}_converted', param_type


def get_param_conversion(param_type: str) -> Optional[Conversion]:
    if param_type not in conversion_map:
        if param_type.endswith('**'):
            return Conversion(param_type, f"'{param_type}'",
                              lambda name: f"[_ffi.cast('{param_type[:-1]}', x) for x in {name}]", lambda name: name)
        else:
            return Conversion(param_type, f"'{param_type}'", lambda name: f"_ffi.cast('{param_type}', {name})",
                              lambda name: name)
    conversion = conversion_map[param_type]
    return conversion


def get_return_type(inner_return_type) -> Tuple[str, Optional[str]]:
    if inner_return_type not in conversion_map:
        return f"'{inner_return_type}'", None
    conversion = conversion_map[inner_return_type]
    return conversion.p_type, conversion.c_to_p('result') if conversion.c_to_p else None


def build_function_string(function_name: str, return_type: str, parameters: List[Tuple[str, str, str, str, str]],
                          result_conversion: Optional[str]) -> str:
    result_param = None
    if len(parameters) > 1 and parameters[-1][0] == 'result':
        result_param = parameters.pop(-1)

    out_params = []
    if len(parameters) > 1:
        out_params = [p for p in parameters if p[0].endswith('_out') or (p[0] == 'count' and p[1].endswith("*'"))]

    params = ', '.join(f'{p[0]}: {p[1]}' for p in parameters if p not in out_params)
    param_conversions = '\n    '.join(p[2] for p in parameters if p[2] is not None and p not in out_params)
    inner_params = ', '.join(pc[0] if pc in out_params else pc[3] for pc in parameters)
    result_manipulation = None
    if result_conversion is not None:
        result_manipulation = f'    result = {result_conversion}\n'

    if result_param is not None:
        param_conversions += f"\n    out_result = _ffi.new('{result_param[4]}')"
        inner_params += ', out_result'
        if return_type == 'bool':
            result_manipulation = (result_manipulation or '') + "    if result:\n" \
                                                                "        return out_result[0]\n" \
                                                                "    raise Exception(f'C call went wrong: {result}')"
        else:
            result_manipulation = (result_manipulation or '') + '    return out_result[0]\n'
        return_type = result_param[1]
    else:
        result_manipulation = (result_manipulation or '') + '    return result'

    for out_param in out_params:
        param_conversions += f"\n    {out_param[0]} = _ffi.new('{out_param[4]}')"
        return_type += f', {out_param[1]}'
        result_manipulation += f', {out_param[0] + ("[0]" if out_param[0] == "count" else "")}'

    if len(out_params) > 0:
        return_type = f'"Tuple[{return_type}]"'

    if len(param_conversions) > 0:
        param_conversions = f'    {param_conversions}\n'

    note = ''
    if function_name in manual_functions:
        note = f'#TODO {manual_functions[function_name]}\n'
    if return_type == 'None':
        return f'{note}def {function_name}({params}) -> {return_type}:\n' \
               f'{param_conversions}' \
               f'    _lib.{function_name}({inner_params})'
    if result_manipulation is None:
        return f'{note}def {function_name}({params}) -> {return_type}:\n' \
               f'{param_conversions}' \
               f'    result = _lib.{function_name}({inner_params})\n' \
               f'    return result'
    return f'{note}def {function_name}({params}) -> {return_type}:\n' \
           f'{param_conversions}' \
           f'    result = _lib.{function_name}({inner_params})\n' \
           f'{result_manipulation}'


if __name__ == '__main__':
    main()
