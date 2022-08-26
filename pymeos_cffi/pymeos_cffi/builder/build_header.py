import re
import sys

from pymeos_cffi.builder.build_helpers import ADDITIONAL_DEFINITIONS


def main(header_path):
    with open(header_path, 'r') as f:
        content = f.read()
        content = content.replace('#', '//#')
        content = content.replace(*ADDITIONAL_DEFINITIONS)
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.RegexFlag.MULTILINE)
    with open('pymeos_cffi/builder/meos.h', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('/usr/local/include/meos.h')
