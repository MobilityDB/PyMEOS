from cffi import FFI

ffibuilder = FFI()

with open('sources/types.c', 'r') as t, open('sources/functions.c', 'r') as f:
    content = t.read() + f.read()
ffibuilder.cdef(content)

ffibuilder.set_source('_meos_cffi',
                      '#include "meos_mod.h"   // the C header of the library',
                      libraries=['meos'], )  # library name, for the linker

ffibuilder.compile(verbose=True)
