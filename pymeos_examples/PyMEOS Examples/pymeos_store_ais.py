import os

from postgis import Point
from pymeos import TGeogPointInst, TFloatInst, pymeos_initialize, pymeos_finalize
from pymeos.db import MobilityDB
from tqdm import tqdm


class AISRecord:

    @staticmethod
    def make(timestamp: str, mmsi: int, latitude: float, longitude: float, sog: float) -> 'AISRecord':
        point = TGeogPointInst(point=Point(latitude, longitude), timestamp=timestamp)
        sog = TFloatInst(value=sog, timestamp=timestamp)
        return AISRecord(mmsi, point, sog)

    def __init__(self, mmsi: int, point: TGeogPointInst, sog: TFloatInst) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.point = point
        self.sog = sog


def main():
    # ----------------------------------------------------------------------
    # ------------------ Section 1: Connect to MobilityDB ------------------
    # ----------------------------------------------------------------------

    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PHPort', 5433)
    db = os.getenv('PGDATABASE', 'test')
    user = os.getenv('PGUSER', 'docker')
    password = os.getenv('PGPASSWORD', 'docker')

    connection = MobilityDB.connect(host=host, port=port, database=db, user=user, password=password)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS public.MEOS_demo;")
    cursor.execute("CREATE TABLE public.MEOS_demo"
                   "(MMSI integer, location public.tgeogpoint, SOG public.tfloat);")

    # ----------------------------------------------------------------------
    # - Section 2: Initialize MEOS and read the input PyMEOS Examples file -
    # ----------------------------------------------------------------------
    pymeos_initialize()

    with open('../data/aisinput.csv', 'r') as file:
        lines = file.read().splitlines()

    # ----------------------------------------------------------------------
    # - Section 3: Save each observation as a temporal point in MobilityDB -
    # ----------------------------------------------------------------------

    records = 0
    nulls = 0
    for line in tqdm(lines[1:]):
        split = line.split(',')
        if len(split) == 5:
            rec = AISRecord.make(split[0], int(split[1]), float(split[2]), float(split[3]), float(split[4]))
            records += 1
        else:
            print("Record with missing values ignored\n")
            nulls += 1
            continue
        cursor.execute(f"INSERT INTO public.MEOS_demo(MMSI, location, SOG) "
                       f"VALUES ({rec.mmsi}, '{rec.point}', '{rec.sog}');")

    print(f"{records} records read.\n {nulls} incomplete records ignored")

    # ----------------------------------------------------------------------
    # ------------------ Section 4: Read from MobilityDB -------------------
    # ----------------------------------------------------------------------

    cursor.execute("SELECT * FROM public.MEOS_demo WHERE MMSI = 265513270;")

    first_record = AISRecord(*cursor.fetchone())

    print(f"MMSI: {first_record.mmsi} | Point: {first_record.point} | SOG: {first_record.sog}")

    # ----------------------------------------------------------------------
    # -------------- Section 5: Close and wrap everything up ---------------
    # ----------------------------------------------------------------------

    connection.commit()
    cursor.close()
    pymeos_finalize()


if __name__ == '__main__':
    main()
