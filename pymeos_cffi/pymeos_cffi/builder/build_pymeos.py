from cffi import FFI

ffibuilder = FFI()

with open("./pymeos_cffi/builder/meos.h", "r") as f:
    content = f.read()

ffibuilder.cdef(content)

ffibuilder.set_source(
    "_meos_cffi",
    '#include "meos.h"\n' '#include "meos_catalog.h"\n' '#include "meos_internal.h"',
    libraries=["meos"],
    library_dirs=["/usr/local/lib"],
)  # library name, for the linker

if __name__ == "__main__":  # not when running with setuptools
    ffibuilder.compile(verbose=True)
