from time import time

from spans import intrange, floatrange

from pymeos_cffi import tgeompoint_in, meos_initialize, tpoint_out, tintinst_make, tint_in, temporal_merge, \
    temporal_merge_array, intrange_to_intspan, span_out, floatrange_to_floatspan

meos_initialize('UTC')

t1 = tint_in('1@2000-01-01')
t2 = tint_in('2@2000-01-02')
ta = [t1, t2]
times = 1000
s = time()
for _ in range(times):
    t3 = temporal_merge(t1, t2)
m = time()
for _ in range(times):
    t3 = temporal_merge_array(ta, 2)
e = time()

print(f'Merge time: {m - s}s')
print(f'Merge Array time: {e - m}s')

ir = intrange(1, 4, lower_inc=False, upper_inc=True)
print(ir, ir.lower_inc, ir.upper_inc)
print(span_out(intrange_to_intspan(ir), -1))

fr = floatrange(1.0, 4.0, lower_inc=False, upper_inc=True)
print(fr, fr.lower_inc, fr.upper_inc)
print(span_out(floatrange_to_floatspan(fr), -1))
