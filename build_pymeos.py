from cffi import FFI

from build_helpers import ADDITIONAL_DEFINITIONS

ffibuilder = FFI()

with open('/usr/local/include/meos.h', 'r') as f:
    content = f.read()
    content = content.replace('#', '//#')
    content = content.replace(*ADDITIONAL_DEFINITIONS)
ffibuilder.cdef(content)

ffibuilder.set_source('_meos_cffi',
                      '#include "meos_mod.h"   // the C header of the library',
                      libraries=['meos'], )  # library name, for the linker

ffibuilder.compile(verbose=True, debug=True)
