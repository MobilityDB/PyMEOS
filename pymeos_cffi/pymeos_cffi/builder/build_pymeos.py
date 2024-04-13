import os

from cffi import FFI

ffibuilder = FFI()

with open("./pymeos_cffi/builder/meos.h", "r") as f:
    content = f.read()

ffibuilder.cdef(content)


def get_library_dirs():
    paths = ["/usr/local/lib", "/opt/homebrew/lib"]
    return [path for path in paths if os.path.exists(path)]


def get_include_dirs():
    paths = ["/usr/local/include", "/opt/homebrew/include"]
    return [path for path in paths if os.path.exists(path)]


ffibuilder.set_source(
    "_meos_cffi",
    '#include "meos.h"\n' '#include "meos_catalog.h"\n' '#include "meos_internal.h"',
    libraries=["meos"],
    library_dirs=get_library_dirs(),
    include_dirs=get_include_dirs(),
)

if __name__ == "__main__":  # not when running with setuptools
    ffibuilder.compile(verbose=True)
