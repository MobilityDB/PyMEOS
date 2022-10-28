import warnings

import numpy as np
import pandas as pd
from postgis import Geometry
from pymeos import Temporal, pymeos_initialize, pymeos_finalize
from tabulate import tabulate

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    pymeos_initialize()

    # read csv files
    communes = pd.read_csv('../data/communes.csv', converters={'geom': Geometry.from_ewkb})
    print("%d commune records read." % len(communes))

    brussels_region = pd.read_csv('../data/brussels_region.csv', converters={'geom': Geometry.from_ewkb})
    print("Brussels region record read.")

    trips = pd.read_csv('../data/trips.csv',
                        converters={'trip': Temporal.from_hexwkb, 'trajectory': Geometry.from_ewkb})
    print("%d trip records read.\n\n" % len(trips))

    # Construct distance matrix
    num_communes = len(communes['id'].unique())
    num_vehicles = len(trips['vehicle'].unique())
    distance = np.zeros((num_vehicles + 1, num_communes + 3), dtype=float)

    for _, trip in trips.iterrows():
        vehicle_id = trip['vehicle']
        trip_seq = trip['trip']
        # Compute the trip distance
        trip_length = trip_seq.distance / 1000.0
        # Add to the vehicle total
        distance[vehicle_id - 1][0] += trip_length
        # Add to the column total
        distance[num_vehicles][0] += trip_length

        for _, commune in communes.iterrows():
            commune_id = commune['id']
            atgeom = trip_seq.at(commune['geom'])
            if atgeom:
                # Compute the length of the trip projected to the commune
                inside_length = atgeom.distance / 1000.0
                # Add to the cell
                distance[vehicle_id - 1][commune_id] += inside_length
                # Add to the row total
                distance[vehicle_id - 1][num_communes + 2] += inside_length
                # Add to the commune total
                distance[num_vehicles][commune_id] += inside_length
                # Add to the inside total
                distance[num_vehicles][num_communes + 2] += inside_length

        minusgeom = trip_seq.minus(brussels_region['geom'][0])
        if minusgeom:
            outside_length = minusgeom.distance / 1000.0
            # Add to the row 
            distance[vehicle_id - 1][num_communes + 1] += outside_length
            # Add to the column total
            distance[num_vehicles][num_communes + 1] += outside_length

    # construct data frame for printing
    columns = ['Distance'] + [str(id) for id in communes['id']] + ['Outside', 'Inside']
    df_distance = pd.DataFrame(distance, columns=columns)
    df_distance.insert(0, 'Vhe', [str(i + 1) for i in range(num_vehicles)] + ['total'])
    df_distance.set_index('Vhe', inplace=True)

    # Whether to filter columns with only zero values
    filter_zero = True
    if filter_zero:
        left_cols = [col for col in df_distance.columns if df_distance[col].any()]
        print(tabulate(df_distance[left_cols], headers='keys', tablefmt='psql', floatfmt='.3f'))
    else:
        print(tabulate(df_distance, headers='keys', tablefmt='psql', floatfmt='.3f'))

    pymeos_finalize()