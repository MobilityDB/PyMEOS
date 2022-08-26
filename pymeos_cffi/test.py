from pymeos_cffi import tpointseq_make_coords, pg_timestamptz_in
from pymeos_cffi.functions import meos_initialize, meos_finish

meos_initialize()

tps = tpointseq_make_coords([1, 2, 3], [5, 6, 7], None,
                            [pg_timestamptz_in('2000-01-01', -1), pg_timestamptz_in('2000-01-02', -1),
                             pg_timestamptz_in('2000-01-03', -1)], 3, 0, False, True, True, True, False)
print(tps)

meos_finish()
