from postgis import Point

from pymeos import TGeogPointInst, TFloatInst
from pymeos_cffi.functions import meos_initialize, meos_finish


class AISRecord:

    def __init__(self, timestamp: str, mmsi: int, latitude: float, longitude: float, sog: float) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.point = TGeogPointInst(point=Point(latitude, longitude), timestamp=timestamp)
        self.sog = TFloatInst(sog, timestamp)


def main():
    meos_initialize()

    with open('aisinput.csv', 'r') as file:
        lines = file.read().splitlines()

    records = 0
    nulls = 0

    for line in lines[1:]:
        split = line.split(',')
        if len(split) == 5:
            rec = AISRecord(split[0], int(split[1]), float(split[2]), float(split[3]), float(split[4]))
            records += 1
        else:
            print("Record with missing values ignored\n")
            nulls += 1
            continue
        # Print only 1 out of 1000 records
        if records % 1000 == 0:
            print(f"MMSI: {rec.mmsi}, Location:{rec.point} SOG : {rec.sog}")

    print(f"{records} records read.\n {nulls} incomplete records ignored")

    # Finalize MEOS
    meos_finish()


if __name__ == '__main__':
    main()
