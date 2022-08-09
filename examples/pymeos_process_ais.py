from functools import cached_property
from typing import List, Optional

from postgis import Point

from lib.functions import meos_initialize, meos_finish
from src.models import TGeogPointInst, TGeogPointSeq


class AISRecord:

    def __init__(self, timestamp: str, mmsi: int, latitude: float, longitude: float, sog: float) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.point = TGeogPointInst(point=Point(latitude, longitude), timestamp=timestamp)
        self.sog = sog


class MMSIInstants:

    def __init__(self, mmsi: Optional[int] = None, instants: Optional[List[TGeogPointInst]] = None) -> None:
        super().__init__()
        self.mmsi = mmsi
        self.instants: List[TGeogPointInst] = instants or []

    @property
    def num_instants(self):
        return len(self.instants)

    @cached_property
    def sequence(self):
        return TGeogPointSeq(instant_list=self.instants, lower_inc=True, upper_inc=True)


def main():
    # Initialize MEOS Library
    meos_initialize()

    # Create array of ships
    ships: List[MMSIInstants] = []

    # Read input file
    with open('aisinput.csv', 'r') as file:

        records = 0
        nulls = 0
        file.readline()

        while True:
            line = file.readline().strip()
            if line == '':
                break
            split = line.split(',')

            # Read record
            if len(split) == 5:
                rec = AISRecord(split[0], int(split[1]), float(split[2]), float(split[3]), float(split[4]))
                records += 1
            else:
                print("Record with missing values ignored\n")
                nulls += 1
                continue

            # Find the place to store the new instant
            ship = next((ti for ti in ships if ti.mmsi == rec.mmsi), None)

            # If there is none, create a new one
            if ship is None:
                ship = MMSIInstants(mmsi=rec.mmsi)
                ships.append(ship)

            # Create the instant and store it in the array of the corresponding ship.
            # In the input file it is assumed that
            # - The coordinates are given in the WGS84 geographic coordinate system
            # - The timestamps are given in GMT time zone
            ship.instants.append(rec.point)

    print(f"\n{records} records read.\n{nulls} incomplete records ignored.\n")
    print(f"{len(ships)} trips read.\n")

    for ship in ships:
        # Create Temporal Geographic Point Sequence with the ship instants
        print(f"MMSI: {ship.mmsi}, "
              f"Number of input instants: {ship.num_instants}, "
              f"Number of instants: {ship.sequence.num_instants}, "
              f"Distance travelled: {ship.sequence.distance}")

    # Finalize MEOS Library
    meos_finish()


if __name__ == '__main__':
    main()
