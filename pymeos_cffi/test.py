from pymeos_cffi.functions import meos_initialize, meos_finish, tbool_in


meos_initialize()
meos_initialize()
meos_initialize()

tbool = tbool_in('t@2000-01-23')

meos_finish()