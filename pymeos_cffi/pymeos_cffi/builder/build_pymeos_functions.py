import re
from re import RegexFlag
from typing import List, Optional

from build_helpers import ADDITIONAL_DEFINITIONS
from build_pymeos_functions_modifiers import period_shift_tscale_modifier, cstring2text_modifier, text2cstring_modifier, \
    timestampset_make_modifier, gserialized_from_lwgeom_modifier
from pymeos_cffi.builder.objects import conversion_map, Conversion


class Parameter:

    def __init__(self, name: str, converted_name: str, ctype: str, ptype: str, cp_conversion: Optional[str]) -> None:
        super().__init__()
        self.name = name
        self.converted_name = converted_name
        self.ctype = ctype
        self.ptype = ptype
        self.cp_conversion = cp_conversion

    def is_interoperable(self):
        return any(self.ctype.startswith(x) for x in ['int', 'bool', 'double'])

    def get_ptype_without_pointers(self):
        if self.is_interoperable():
            return self.ptype.replace(" *'", "'").replace("**", '*')
        else:
            return self.ptype

    def get_ptype(self, nullable: bool) -> str:
        if nullable:
            return f'"Optional[{self.ptype}]"'
        return self.ptype

    def get_conversion(self, nullable: bool) -> Optional[str]:
        if self.cp_conversion is None:
            return None
        conversion = self.cp_conversion
        if nullable:
            conversion += f' if {self.name} else _ffi.NULL'
        return conversion

    def __str__(self) -> str:
        return f'{self.name=}, {self.converted_name=}, {self.ctype=}, {self.ptype=}, {self.cp_conversion=}'


class ReturnType:

    def __init__(self, ctype: str, ptype: str, conversion: Optional[str]) -> None:
        super().__init__()
        self.ctype = ctype
        self.return_type = ptype
        self.conversion = conversion


BASE = """from datetime import datetime, timedelta
from typing import Any, Tuple, Optional, List

import _meos_cffi
import shapely.geometry as spg
from dateutil.parser import parse
from postgis import Point

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


def lwpoint_to_point(lwpoint: Any) -> Point:
    return Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint),
                 lwpoint_get_z(lwpoint) if lwgeom_has_z(lwpoint) else None,
                 lwpoint_get_m(lwpoint) if lwgeom_has_m(lwpoint) else None,
                 lwgeom_get_srid(lwpoint))


def lwpoint_to_shapely_point(lwpoint: Any) -> spg.Point:
    return spg.Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint),lwpoint_get_z(lwpoint)) if lwgeom_has_z(lwpoint) \
        else spg.Point(lwpoint_get_x(lwpoint), lwpoint_get_y(lwpoint))


"""

manual_functions = {
}

function_modifiers = {
    'period_shift_tscale': period_shift_tscale_modifier,
    'cstring2text': cstring2text_modifier,
    'text2cstring': text2cstring_modifier,
    'timestampset_make': timestampset_make_modifier,
    'gserialized_from_lwgeom': gserialized_from_lwgeom_modifier,
}

# List of result function parameters in tuples of (function, parameter)
result_parameters = {
    ('tbool_value_at_timestamp', 'value'),
    ('ttext_value_at_timestamp', 'value'),
    ('tint_value_at_timestamp', 'value'),
    ('tfloat_value_at_timestamp', 'value'),
    ('tpoint_value_at_timestamp', 'value'),
}

# List of output function parameters in tuples of (function, parameter)
output_parameters = {}

# List of nullable function parameters in tuples of (function, parameter)
nullable_parameters = {
    ('temporal_as_mfjson', 'srs'),
    ('period_shift_tscale', 'duration'),
    ('period_shift_tscale', 'start'),
    ('timestampset_shift_tscale', 'start'),
    ('timestampset_shift_tscale', 'duration'),
    ('periodset_shift_tscale', 'start'),
    ('periodset_shift_tscale', 'duration'),
    ('temporal_shift_tscale', 'start'),
    ('temporal_shift_tscale', 'duration'),
    ('tbox_make', 'p'),
    ('tbox_make', 's'),
    ('stbox_make', 'p'),
}


# Checks if parameter in function is nullable
def is_nullable_parameter(function: str, parameter: Parameter) -> bool:
    return (function, parameter.name) in nullable_parameters


# Checks if parameter in function is actually a result parameter
def is_result_parameter(function: str, parameter: Parameter) -> bool:
    if parameter.name == 'result':
        return True
    return (function, parameter.name) in result_parameters


# Checks if parameter in function is actually an output parameter
def is_output_parameter(function: str, parameter: Parameter) -> bool:
    if parameter.name.endswith('_out'):
        return True
    if parameter.name == 'count' and parameter.ptype.endswith("*'"):
        return True
    return (function, parameter.name) in output_parameters


def main():
    with open('/usr/local/include/meos.h') as f:
        content = f.read()
        content = content.replace('#', '//#')
        content = content.replace(*ADDITIONAL_DEFINITIONS)
    f_regex = r'extern (?:static )?(?:inline )?(?P<returnType>(?:const )?\w+(?: \*+)?) ?(?P<function>\w+)\((?P<params>[\w ,\*]*)\);'
    matches = re.finditer(f_regex, ''.join(content.splitlines()), flags=RegexFlag.MULTILINE)

    with open('../functions.py', 'w+') as file:
        file.write(BASE)
        for match in matches:
            named = match.groupdict()
            function = named['function']
            inner_return_type = named['returnType']
            return_type = get_return_type(inner_return_type)
            inner_params = named['params']
            params = get_params(inner_params)
            function_string = build_function_string(function, return_type, params)
            file.write(function_string)
            file.write('\n\n\n')


def get_params(inner_params: str) -> List[Parameter]:
    return [p for p in (get_param(param.strip()) for param in inner_params.split(',')) if p is not None]


# Creates Parameter object from a function parameter
def get_param(inner_param: str) -> Optional[Parameter]:
    # Split param name and type
    split = inner_param.split(' ')

    # Type is everything except last word
    param_type = ' '.join(split[:-1])

    # Check if parameter is pointer and fix type and name accordingly
    if split[-1].startswith('**'):
        param_type += ' **'
    elif split[-1].startswith('*'):
        param_type += ' *'
    param_name = split[-1].lstrip('*')

    # Check if the parameter name is a reserved word and change it if necessary
    reserved_words = {
        'str': 'string',
        'is': 'iset',
    }
    if param_name in reserved_words:
        param_name = reserved_words[param_name]

    # Return None to remove the parameter if it's void
    if param_name == 'void':
        return None

    # Get the type conversion
    conversion = get_param_conversion(param_type)

    # If no parameter conversion is available, assume none is necessary and give python type Any
    if conversion is None:
        return Parameter(param_name, param_name, 'Any', param_type, '')

    # If no conversion is needed between c and python types, use parameter name also as converted name
    if conversion.p_to_c is None:
        return Parameter(param_name, param_name, param_type, conversion.p_type, None)

    # If a conversion is needed, create new name and add the conversion
    return Parameter(param_name, f'{param_name}_converted', param_type, conversion.p_type,
                     f'{param_name}_converted = {conversion.p_to_c(param_name)}')


# Returns a conversion for a type
def get_param_conversion(param_type: str) -> Conversion:
    # Check if type is known
    if param_type in conversion_map:
        return conversion_map[param_type]
    # Otherwise, create a new conversion

    # If it's a double pointer, cast as array
    if param_type.endswith('**'):
        return Conversion(param_type, f"'{param_type}'",
                          lambda name: f"[_ffi.cast('{param_type[:-1]}', x) for x in {name}]", lambda name: name)

    # Otherwise, cast normally
    else:
        return Conversion(param_type, f"'{param_type}'", lambda name: f"_ffi.cast('{param_type}', {name})",
                          lambda name: name)


# Creates a ReturnType object from the function return type
def get_return_type(inner_return_type) -> ReturnType:
    # Check if a conversion is known
    if inner_return_type in conversion_map:
        conversion = conversion_map[inner_return_type]
        return ReturnType(conversion.c_type, conversion.p_type,
                          conversion.c_to_p('result') if conversion.c_to_p else None)
    # Otherwise, don't transform anything
    return ReturnType(inner_return_type, f"'{inner_return_type}'", None)


def build_function_string(function_name: str, return_type: ReturnType, parameters: List[Parameter]) -> str:
    # Check if there is a result param, i.e. output parameters that are the actual product of the function, instead of
    # whatever the function returns (typically void or bool/int indicating the success or failure of the function)
    result_param = None
    if len(parameters) > 1 and is_result_parameter(function_name, parameters[-1]):
        # Remove it from the list of parameters
        result_param = parameters.pop(-1)

    # Check if there are output parameters. Unlike result parameters, these are just normal parameters that provide
    # extra information or actual results that are meant to go along with whatever the function returns
    out_params = []
    if len(parameters) > 1:
        out_params = [p for p in parameters if is_output_parameter(function_name, p)]

    # Create wrapper function parameter list
    params = ', '.join(f'{p.name}: {p.get_ptype(is_nullable_parameter(function_name, p))}' for p in parameters
                       if p not in out_params)

    # Create necessary conversions for the parameters
    param_conversions = '\n    '.join(p.get_conversion(is_nullable_parameter(function_name, p)) for p in parameters
                                      if p.cp_conversion is not None and p not in out_params)

    # Create CFFI function parameter list
    inner_params = ', '.join(pc.name if pc in out_params else pc.converted_name for pc in parameters)

    # Add result conversion if necessary
    result_manipulation = None
    if return_type.conversion is not None:
        result_manipulation = f'    result = {return_type.conversion}\n'

    # Initialize the function return type to the python type unless it needs no conversion (where the C type gives
    # extra information while being interoperable), or the function is void
    function_return_type = return_type.return_type \
        if return_type.conversion is not None or return_type.return_type == 'None' \
        else f"'{return_type.ctype}'"
    # If there is a result param
    if result_param is not None:
        # Create the CFFI object to hold it
        param_conversions += f"\n    out_result = _ffi.new('{result_param.ctype}')"
        # Add it to the CFFI call param list
        inner_params += ', out_result'

        # If result is interoperable, remove pointer, otherwise, keep pointer
        returning_object = 'out_result'
        if result_param.is_interoperable():
            returning_object += '[0]'

        # If original C function returned bool, use it to return it when result is True, or raise exception when False
        if return_type.return_type == 'bool':
            result_manipulation = (result_manipulation or '') + "    if result:\n" \
                                                                f"        return {returning_object} if " \
                                                                f"{returning_object} != _ffi.NULL else None\n" \
                                                                "    raise Exception(f'C call went wrong: {result}')"
        # Otherwise, just return it normally
        else:
            result_manipulation = (result_manipulation or '') + f'    return {returning_object} if {returning_object}' \
                                                                f'!= _ffi.NULL else None\n'
        # Set the return type as the Python type, removing the pointer modifier if necessary
        function_return_type = result_param.get_ptype_without_pointers()
    # Otherwise, return the result normally (if needed)
    elif return_type.return_type != 'None':
        result_manipulation = (result_manipulation or '') + '    return result if result != _ffi.NULL else None'

    # For each output param
    for out_param in out_params:
        # Create the CFFI object to hold it
        param_conversions += f"\n    {out_param.name} = _ffi.new('{out_param.ctype}')"
        # Add its type to the return type of the function, removing the pointer modifier if necessary
        function_return_type += ', ' + out_param.get_ptype_without_pointers()
        # Add it to the return statement
        result_manipulation += f', {out_param.name + ("[0]" if out_param.name == "count" else "")}'

    # If there are output params, wrap function return type in a Tuple
    if len(out_params) > 0:
        function_return_type = f'"Tuple[{function_return_type}]"'

    # Add padding to param conversions
    if len(param_conversions) > 0:
        param_conversions = f'    {param_conversions}\n'

    # Add TO DO note if the function is listed in the manual_functions dictionary
    note = ''
    if function_name in manual_functions:
        note = f'#TODO {manual_functions[function_name]}\n'

    # Create common part of function string (note, name, parameters, return type and parameter conversions).
    base = f'{note}def {function_name}({params}) -> {function_return_type}:\n' \
           f'{param_conversions}'
    # If the function didn't return anything, just add the function call to the base
    if return_type.return_type == 'None':
        function_string = f'{base}' \
                          f'    _lib.{function_name}({inner_params})'
    # Otherwise, store the result in a variable
    else:
        function_string = f'{base}' \
                          f'    result = _lib.{function_name}({inner_params})'

    # Add whatever manipulation the result needs (maybe empty)
    if result_manipulation is not None:
        function_string += f'\n{result_manipulation}'

    # Check if there is function modifiers to modify specific elements of the function
    if function_name in function_modifiers:
        function_string = function_modifiers[function_name](function_string)

    return function_string


if __name__ == '__main__':
    main()
