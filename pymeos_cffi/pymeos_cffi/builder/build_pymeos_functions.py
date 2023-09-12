import re
from re import RegexFlag
from typing import List, Optional

from build_pymeos_functions_modifiers import *
from objects import conversion_map, Conversion


class Parameter:

    def __init__(self, name: str, converted_name: str, ctype: str, ptype: str, cp_conversion: Optional[str]) -> None:
        super().__init__()
        self.name = name
        self.converted_name = converted_name
        self.ctype = ctype
        self.ptype = ptype
        self.cp_conversion = cp_conversion

    def is_interoperable(self):
        return any(self.ctype.startswith(x) for x in ['int', 'bool', 'double', 'TimestampTz'])

    def get_ptype_without_pointers(self):
        if self.is_interoperable():
            return self.ptype.replace(" *'", "'").replace("**", '*')
        else:
            return self.ptype

    def __str__(self) -> str:
        return f'{self.name=}, {self.converted_name=}, {self.ctype=}, {self.ptype=}, {self.cp_conversion=}'


class ReturnType:

    def __init__(self, ctype: str, ptype: str, conversion: Optional[str]) -> None:
        super().__init__()
        self.ctype = ctype
        self.return_type = ptype
        self.conversion = conversion


# List of functions defined in functions.py that shouldn't be exported

hidden_functions = [
    '_check_error',
]

# List of MEOS functions that should not defined in functions.py
skipped_functions = [
    'py_error_handler',
    'meos_initialize_timezone',
    'meos_initialize_error_handler',
    'meos_finalize_timezone',
]

function_notes = {
}

function_modifiers = {
    'meos_initialize': meos_initialize_modifier,
    'meos_finalize': remove_error_check_modifier,
    'cstring2text': cstring2text_modifier,
    'text2cstring': text2cstring_modifier,
    'timestampset_make': timestampset_make_modifier,
    'gserialized_from_lwgeom': gserialized_from_lwgeom_modifier,
    'spanset_make': spanset_make_modifier,
    'temporal_from_wkb': from_wkb_modifier('temporal_from_wkb', 'Temporal'),
    'set_from_wkb': from_wkb_modifier('set_from_wkb', 'Set'),
    'span_from_wkb': from_wkb_modifier('span_from_wkb', 'Span'),
    'spanset_from_wkb': from_wkb_modifier('spanset_from_wkb', 'SpanSet'),
    'tbox_from_wkb': from_wkb_modifier('tbox_from_wkb', 'TBOX'),
    'stbox_from_wkb': from_wkb_modifier('stbox_from_wkb', 'STBOX'),
    'temporal_as_wkb': as_wkb_modifier,
    'set_as_wkb': as_wkb_modifier,
    'span_as_wkb': as_wkb_modifier,
    'spanset_as_wkb': as_wkb_modifier,
    'tbox_as_wkb': as_wkb_modifier,
    'stbox_as_wkb': as_wkb_modifier,
    'intset_make': array_parameter_modifier('values', 'count'),
    'bigintset_make': array_parameter_modifier('values', 'count'),
    'floatset_make': array_parameter_modifier('values', 'count'),
    'textset_make': textset_make_modifier,
    'geoset_make': array_length_remover_modifier('values', 'count'),
}

# List of result function parameters in tuples of (function, parameter)
result_parameters = {
    ('tbool_value_at_timestamp', 'value'),
    ('ttext_value_at_timestamp', 'value'),
    ('tint_value_at_timestamp', 'value'),
    ('tfloat_value_at_timestamp', 'value'),
    ('tpoint_value_at_timestamp', 'value'),
}

# List of output function parameters in tuples of (function, parameter). All parameters named result are assumed
# to be output parameters, and it's not necessary to list them here.
output_parameters = {
    ('temporal_time_split', 'buckets'),
    ('temporal_time_split', 'newcount'),
    ('tint_value_split', 'buckets'),
    ('tint_value_split', 'newcount'),
    ('tfloat_value_split', 'buckets'),
    ('tfloat_value_split', 'newcount'),
    ('tint_value_time_split', 'newcount'),
    ('tfloat_value_time_split', 'newcount'),
    ('tbox_as_hexwkb', 'size'),
    ('stbox_as_hexwkb', 'size'),
    ('tbox_tile_list', 'rows'),
    ('tbox_tile_list', 'columns'),
    ('stbox_tile_list', 'cellcount'),
}

# List of nullable function parameters in tuples of (function, parameter)
nullable_parameters = {
    ('meos_initialize', 'tz_str'),
    ('temporal_append_tinstant', 'maxt'),
    ('temporal_as_mfjson', 'srs'),
    ('gserialized_as_geojson', 'srs'),
    ('period_shift_scale', 'shift'),
    ('period_shift_scale', 'duration'),
    ('timestampset_shift_scale', 'shift'),
    ('timestampset_shift_scale', 'duration'),
    ('periodset_shift_scale', 'shift'),
    ('periodset_shift_scale', 'duration'),
    ('temporal_shift_scale_time', 'shift'),
    ('temporal_shift_scale_time', 'duration'),
    ('tbox_make', 'p'),
    ('tbox_make', 's'),
    ('stbox_make', 'p'),
    ('stbox_shift_scale_time', 'shift'),
    ('stbox_shift_scale_time', 'duration'),
    ('temporal_tcount_transfn', 'state'),
    ('temporal_extent_transfn', 'p'),
    ('tnumber_extent_transfn', 'box'),
    ('tpoint_extent_transfn', 'box'),
    ('tbool_tand_transfn', 'state'),
    ('tbool_tor_transfn', 'state'),
    ('tbox_shift_scale_time', 'shift'),
    ('tbox_shift_scale_time', 'duration'),
    ('tint_tmin_transfn', 'state'),
    ('tfloat_tmin_transfn', 'state'),
    ('tint_tmax_transfn', 'state'),
    ('tfloat_tmax_transfn', 'state'),
    ('tint_tsum_transfn', 'state'),
    ('tfloat_tsum_transfn', 'state'),
    ('tnumber_tavg_transfn', 'state'),
    ('ttext_tmin_transfn', 'state'),
    ('ttext_tmax_transfn', 'state'),
    ('temporal_tcount_transfn', 'interval'),
    ('timestamp_tcount_transfn', 'interval'),
    ('timestampset_tcount_transfn', 'interval'),
    ('period_tcount_transfn', 'interval'),
    ('periodset_tcount_transfn', 'interval'),
    ('timestamp_extent_transfn', 'p'),
    ('timestamp_tcount_transfn', 'state'),
    ('timestampset_tcount_transfn', 'state'),
    ('period_tcount_transfn', 'state'),
    ('periodset_tcount_transfn', 'state'),
    ('stbox_tile_list', 'duration'),
    ('tbox_tile_list', 'xorigin'),
    ('tbox_tile_list', 'torigin'),
}


# Checks if parameter in function is nullable
def is_nullable_parameter(function: str, parameter: str) -> bool:
    return (function, parameter) in nullable_parameters


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


def check_modifiers(functions: List[str]) -> None:
    for func in function_modifiers.keys():
        if func not in functions:
            print(f'Modifier defined for non-existent function {func}')
    for func, param in result_parameters:
        if func not in functions:
            print(f'Result parameter defined for non-existent function {func} ({param})')
    for func, param in output_parameters:
        if func not in functions:
            print(f'Output parameter defined for non-existent function {func} ({param})')
    for func, param in nullable_parameters:
        if func not in functions:
            print(f'Nullable Parameter defined for non-existent function {func} ({param})')


def main():
    with open('pymeos_cffi/builder/meos.h') as f:
        content = f.read()
    # Regex lines:
    # 1st line: Match beginning of function with optional "extern", "static" and "inline"
    # 2nd line: Match the return type as any alphanumeric string with optional "const" modifier (before the type) or
    #             pointer modifier (after the type)
    # 3rd line: Match the name of the function as any alphanumeric string
    # 4th line: Match the parameters as any sequence of alphanumeric characters, commas, spaces and asterisks between
    #             parenthesis and end with a semicolon. (Parameter decomposition will be performed later)
    f_regex = r'(?:extern )?(?:static )?(?:inline )?' \
              r'(?P<returnType>(?:const )?\w+(?: \*+)?)' \
              r'\s*(?P<function>\w+)' \
              r'\((?P<params>[\w\s,\*]*)\);'
    matches = re.finditer(f_regex, ''.join(content.splitlines()), flags=RegexFlag.MULTILINE)

    with open('pymeos_cffi/builder/templates/functions.py') as f:
        base = f.read()

    with open('pymeos_cffi/functions.py', 'w+') as file:
        file.write(base)
        for match in matches:
            named = match.groupdict()
            function = named['function']
            inner_return_type = named['returnType']
            if function in skipped_functions:
                continue
            return_type = get_return_type(inner_return_type)
            inner_params = named['params']
            params = get_params(function, inner_params)
            function_string = build_function_string(function, return_type, params)
            file.write(function_string)
            file.write('\n\n\n')

    functions = []
    with open('pymeos_cffi/functions.py', 'r') as funcs, open('pymeos_cffi/__init__.py', 'w+') as init:
        content = funcs.read()
        matches = list(re.finditer(r'def (\w+)\(', content))
        init.write('from .functions import *\n\n')
        init.write('from .errors import *\n\n')
        init.write('__all__ = [\n'
                   "    # Exceptions \n"
                   "    'MeosException',\n"
                   "    'MeosInternalError',\n"
                   "    'MeosArgumentError',\n"
                   "    'MeosIoError',\n"
                   "    'MeosInternalTypeError',\n"
                   "    'MeosValueOutOfRangeError',\n"
                   "    'MeosDivisionByZeroError',\n"
                   "    'MeosMemoryAllocError',\n"
                   "    'MeosAggregationError',\n"
                   "    'MeosDirectoryError',\n"
                   "    'MeosFileError',\n"
                   "    'MeosInvalidArgError',\n"
                   "    'MeosInvalidArgTypeError',\n"
                   "    'MeosInvalidArgValueError',\n"
                   "    'MeosMfJsonInputError',\n"
                   "    'MeosMfJsonOutputError',\n"
                   "    'MeosTextInputError',\n"
                   "    'MeosTextOutputError',\n"
                   "    'MeosWkbInputError',\n"
                   "    'MeosWkbOutputError',\n"
                   "    'MeosGeoJsonInputError',\n"
                   "    'MeosGeoJsonOutputError',\n"
                   "    # Functions\n"
                   )
        for fn in matches:
            function_name = fn.group(1)
            if function_name in hidden_functions:
                continue
            init.write(f"    '{function_name}',\n")
            functions.append(function_name)
        init.write(']\n')

    check_modifiers(functions)


def get_params(function: str, inner_params: str) -> List[Parameter]:
    return [p for p in (get_param(function, param.strip()) for param in inner_params.split(',')) if p is not None]


# Creates Parameter object from a function parameter
def get_param(function: str, inner_param: str) -> Optional[Parameter]:
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

    # Check if parameter is nullable
    nullable = is_nullable_parameter(function, param_name)

    # If no conversion is needed between c and python types, use parameter name also as converted name
    if conversion.p_to_c is None:
        # If nullable, add null check
        if nullable:
            return Parameter(param_name, f'{param_name}_converted', param_type, f"'Optional[{conversion.p_type}]'",
                             f'{param_name}_converted = {param_name} if {param_name} is not None else _ffi.NULL')
        return Parameter(param_name, param_name, param_type, conversion.p_type, None)

    # If a conversion is needed, create new name and add the conversion
    if nullable:
        return Parameter(param_name, f'{param_name}_converted', param_type, f'"Optional[{conversion.p_type}]"',
                         f'{param_name}_converted = {conversion.p_to_c(param_name)} '
                         f'if {param_name} is not None else _ffi.NULL')
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
    params = ', '.join(f'{p.name}: {p.ptype}' for p in parameters
                       if p not in out_params)

    # Create necessary conversions for the parameters
    param_conversions = '\n    '.join(p.cp_conversion for p in parameters
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

            result_manipulation = (result_manipulation or '') + \
                                  "    if result:\n" \
                                  f"        return {returning_object} if {returning_object} != _ffi.NULL else None\n" \
                                  "    return None"
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
        result_manipulation += f', {out_param.name}[0]'

    # If there are output params, wrap function return type in a Tuple
    if len(out_params) > 0:
        function_return_type = f'"Tuple[{function_return_type}]"'

    # Add padding to param conversions
    if len(param_conversions) > 0:
        param_conversions = f'    {param_conversions}\n'

    # Add TO DO note if the function is listed in the function_notes dictionary
    note = ''
    if function_name in function_notes:
        note = f'#TODO {function_notes[function_name]}\n'

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

    # Add error handling
    function_string += f'\n    _check_error()'

    # Add whatever manipulation the result needs (maybe empty)
    if result_manipulation is not None:
        function_string += f'\n{result_manipulation}'

    # Check if there is function modifiers to modify specific elements of the function
    if function_name in function_modifiers:
        function_string = function_modifiers[function_name](function_string)

    return function_string


if __name__ == '__main__':
    main()
