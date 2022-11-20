import re
import sys

from build_helpers import ADDITIONAL_DEFINITIONS


def main(header_path):
    with open(header_path, 'r') as f:
        content = f.read()
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.RegexFlag.MULTILINE)
        # Comment macros
        content = content.replace('#', '//#')
        content = re.sub(r'^//(#define \w+ \d+)\s*$', '\g<1>', content, flags=re.RegexFlag.MULTILINE)
        # Add additional definitions
        content = content.replace(*ADDITIONAL_DEFINITIONS)
    with open('pymeos_cffi/builder/meos.h', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('/usr/local/include/meos.h')
