from pymeos_cffi.builder.build_helpers import ADDITIONAL_DEFINITIONS


def main():
    with open('/usr/local/include/meos.h', 'r') as f:
        content = f.read()
        content = content.replace('#', '//#')
        content = content.replace(*ADDITIONAL_DEFINITIONS)
    with open('pymeos_cffi/builder/meos.h', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    main()
