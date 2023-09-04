import re
import subprocess
import sys


def get_defined_functions(library_path):
    result = subprocess.check_output(['nm', '-gD', library_path])
    output = result.decode('utf-8')
    lines = output.splitlines()
    defined = {line.split(' ')[-1] for line in lines if ' T ' in line}
    return defined


def remove_undefined_functions(content, so_path):
    defined = get_defined_functions(so_path)

    def remove_if_not_defined(m):
        function = m.group(0).split('(')[0].strip().split(' ')[-1].strip('*')
        if function in defined:
            return m.group(0)
        else:
            print('Removing undefined function', function)
            return ''

    content = re.sub(r'^extern .*?;', remove_if_not_defined, content, flags=re.RegexFlag.MULTILINE)
    return content


def main(header_path, so_path=None):
    with open(header_path, 'r') as f:
        content = f.read()
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.RegexFlag.MULTILINE)
        # Comment macros that are not number constants
        content = content.replace('#', '//#')
        content = re.sub(r'^//(#define \w+ \d+)\s*$', r'\g<1>', content, flags=re.RegexFlag.MULTILINE)
        # Add additional definitions
        # content = content.replace(*ADDITIONAL_DEFINITIONS)

        # Remove functions that are not actually defined in the library
        if so_path:
            content = remove_undefined_functions(content, so_path)

        # Add error handler
        content += '\n\nextern "Python" void py_error_handler(int, int, char*);'

    with open('pymeos_cffi/builder/meos.h', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1], sys.argv[2])
    else:
        main('/usr/local/include/meos.h', '/usr/local/lib/libmeos.so')
