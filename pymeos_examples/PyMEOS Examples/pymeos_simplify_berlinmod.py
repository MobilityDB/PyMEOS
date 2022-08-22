from pymeos import Temporal
from pymeos_cffi import meos_initialize, meos_finish
import pandas as pd
from postgis import Geometry

DELTA_DISTANCE = 1

if __name__ == '__main__':
    meos_initialize()

    # define converters for parsing csv files
    geom_converter = Geometry.from_ewkb
    hexwkb_converter = Temporal.temporal_from_hexwkb

    trips = pd.read_csv('../data/trips.csv', converters={'trip': hexwkb_converter, 'trajectory': geom_converter})
    print("%d trip records read.\n\n" % len(trips))

    trips['simplfied_dp'] = trips['trip'].apply(lambda x: x.simplify(DELTA_DISTANCE, False))
    trips['simplfied_sed'] = trips['trip'].apply(lambda x: x.simplify(DELTA_DISTANCE, True))

    for _, trip in trips.iterrows():
        print(f"Vehicle: {trip['vehicle']}, Date: {trip['day']}, Seq: {trip['seq']}",
            f"No. of instants: {trip['trip'].num_instants},",
            f"No. of instants DP: {trip['simplfied_dp'].num_instants},",
            f"No. of instants SED: {trip['simplfied_sed'].num_instants}")

    meos_finish()