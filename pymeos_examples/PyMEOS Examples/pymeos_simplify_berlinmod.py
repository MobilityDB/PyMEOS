import pandas as pd
from postgis import Geometry
from pymeos import Temporal, pymeos_initialize, pymeos_finalize

DELTA_DISTANCE = 1


def main():
    pymeos_initialize()
    trips = pd.read_csv('../data/trips.csv',
                        converters={
                            'trip': Temporal.from_hexwkb,
                            'trajectory': Geometry.from_ewkb
                        })
    print(f'{len(trips)} trip records read.\n\n')

    trips['simplfied_dp'] = trips['trip'].apply(lambda x: x.simplify(DELTA_DISTANCE, False))
    trips['simplfied_sed'] = trips['trip'].apply(lambda x: x.simplify(DELTA_DISTANCE, True))
    for _, trip in trips.iterrows():
        print(f"Vehicle: {trip['vehicle']}, Date: {trip['day']}, Seq: {trip['seq']}",
              f"No. of instants: {trip['trip'].num_instants},",
              f"No. of instants DP: {trip['simplfied_dp'].num_instants},",
              f"No. of instants SED: {trip['simplfied_sed'].num_instants}")

    pymeos_finalize()


if __name__ == '__main__':
    main()
