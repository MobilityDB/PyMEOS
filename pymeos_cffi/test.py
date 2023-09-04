from pymeos_cffi import *

meos_initialize('UTC')

t = tfloat_in('2.0@2000-01-01')

try:
    print(tfloat_out(t, -2))
except MeosInvalidArgValueError as e:
    print(e)

print(tfloat_out(t, 2))