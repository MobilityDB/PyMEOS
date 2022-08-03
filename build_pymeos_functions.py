import re
from typing import List, Optional, Tuple

from src.objects import conversion_map, Conversion


def main():
    with open('./sources/functions.c') as f:
        content = f.read()
    function_regex = r'extern (?P<returnType>(?:const )?\w+(?: \*+)?) ?(?P<function>\w+)\((?P<params>[\w ,\*]*)\);'
    matches = re.finditer(function_regex, ''.join(content.splitlines()))

    with open('./src/functions.py', 'w+') as file:
        file.write('from typing import Any\n'
                   'from datetime import datetime\n'
                   'import _meos_cffi\n'
                   '\n'
                   '_ffi = _meos_cffi.ffi\n'
                   '_lib = _meos_cffi.lib\n'
                   '\n\n'
                   'def datetime_to_timestamptz(dt: datetime) -> int:\n'
                   "    return _lib.pg_timestamptz_in(dt.strftime('%Y-%m-%d %H:%M:%S%z').encode('utf-8'), -1)\n"
                   '\n\n')
        for match in matches:
            named = match.groupdict()
            function = named['function']
            inner_return_type = named['returnType']
            return_type, result_conversion = get_return_type(inner_return_type)
            inner_params = named['params']
            params = get_params(inner_params)
            function_string = build_functions_string(function, return_type, params, result_conversion)
            file.write(function_string)
            file.write('\n\n\n')


def get_params(inner_params: str) -> List[Tuple[str, str, str, str]]:
    return [p for p in (get_param(param.strip()) for param in inner_params.split(',')) if p is not None]


def get_param(inner_param: str) -> Optional[Tuple[str, str, str, str]]:
    split = inner_param.split(' ')
    param_type = ' '.join(split[:-1])
    if split[-1].startswith('*'):
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
        return param_name, 'Any', '', param_name
    return param_name, conversion.p_type, f'{param_name}_converted = {conversion.p_to_c(param_name)}', f'{param_name}_converted'


def get_param_conversion(param_type: str) -> Optional[Conversion]:
    if param_type not in conversion_map:
        return None
    conversion = conversion_map[param_type]
    return conversion


def get_return_type(inner_return_type) -> Tuple[str, Optional[str]]:
    if inner_return_type not in conversion_map:
        return 'Any', None
    conversion = conversion_map[inner_return_type]
    return conversion.p_type, conversion.c_to_p('result')


def build_functions_string(function_name: str, return_type: str, parameters: List[Tuple[str, str, str, str]],
                           result_conversion: Optional[str]) -> str:
    params = ', '.join(f'{p[0]}: {p[1]}' for p in parameters)
    param_conversions = '\n    '.join(p[2] for p in parameters if p[2] != '')
    if len(param_conversions) > 0:
        param_conversions = f'    {param_conversions}\n'
    inner_params = ', '.join(pc[3] for pc in parameters)
    if return_type == 'None':
        return f'def {function_name}({params}) -> {return_type}:\n' \
               f'{param_conversions}' \
               f'    _lib.{function_name}({inner_params})'
    if return_type == 'Any':
        return f'def {function_name}({params}) -> {return_type}:\n' \
               f'{param_conversions}' \
               f'    return _lib.{function_name}({inner_params})\n'
    return f'def {function_name}({params}) -> {return_type}:\n' \
           f'{param_conversions}' \
           f'    result = _lib.{function_name}({inner_params})\n' \
           f'    result = {result_conversion or "result"}\n' \
           f'    return result'


if __name__ == '__main__':
    main()
