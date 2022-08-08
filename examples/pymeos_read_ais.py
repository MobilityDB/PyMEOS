import _meos_cffi
from postgis import Point

from lib.functions import pg_timestamp_out
from src.models import TGeogPointInst

_ffi = _meos_cffi.ffi
_lib = _meos_cffi.lib


class AISRecord:

    def __init__(self, timestamp: str, mmsi: int, latitude: float, longitude: float, sog: float) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.point = TGeogPointInst(string=, point=, timestamp=)
        self.sog = sog


def main():
    # Initialize MEOS
    _lib.meos_initialize()

    with open('aisinput.csv', 'r') as file:
        lines = file.read().splitlines()

    records = 0
    nulls = 0

    for line in lines[1:]:
        split = line.split(',')
        if len(split) == 5:
            rec = AISRecord(
                split[0],
                int(split[1]),
                float(split[2]),
                float(split[3]),
                float(split[4])
            )
            records += 1
        else:
            print("Record with missing values ignored\n")
            nulls += 1
            continue
        # Print only 1 out of 1000 records
        if records % 1000 == 0:
            t_out = pg_timestamp_out(rec.timestamp)
            buffer = f"SRID=4326;Point({rec.longitude} {rec.latitude})@{t_out}+00".encode('utf-8')
            inst1 = _lib.tgeogpoint_in(buffer)
            inst1_out = _lib.tpoint_as_text(inst1, 2)
            inst1_out = _ffi.string(inst1_out).decode('utf8')

            inst2 = _lib.tfloatinst_make(rec.sog, rec.timestamp)
            inst2 = _ffi.cast('Temporal *', inst2)
            inst2_out = _lib.tfloat_out(inst2, 2)
            inst2_out = _ffi.string(inst2_out).decode('utf8')
            print(f"MMSI: {rec.mmsi}, Location:{inst1_out} SOG : {inst2_out}")

    print(f"{records} records read.\n {nulls} incomplete records ignored")

    # Finalize MEOS
    _lib.meos_finish()


if __name__ == '__main__':
    main()
