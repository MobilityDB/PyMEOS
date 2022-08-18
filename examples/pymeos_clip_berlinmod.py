from pymeos import TGeomPointInst, TGeomPointInstSet, TGeomPointSeqSet, TGeomPointSeq
from pymeos_cffi.functions import meos_initialize, meos_finish, gserialized_in, \
    temporal_from_hexwkb, tpoint_length, tpoint_at_geometry, tpoint_minus_geometry
import pandas as pd
import numpy as np
from tabulate import tabulate

import _meos_cffi
_ffi = _meos_cffi.ffi

import warnings
warnings.filterwarnings("ignore")


if __name__ == '__main__':
    meos_initialize()

    # define converters for parsing csv files
    geom_converter = lambda x: gserialized_in(x, -1)
    hexwkb_converter = temporal_from_hexwkb

    # read csv files
    communes = pd.read_csv('communes.csv', converters={'geom': geom_converter})
    print("%d commune records read." % len(communes));

    brussels_region = pd.read_csv('brussels_region.csv', converters={'geom': geom_converter})
    print("Brussels region record read.");

    trips = pd.read_csv('trips.csv', converters={'trip': hexwkb_converter, 'trajectory': geom_converter})
    print("%d trip records read.\n\n" % len(trips));

    # Construct distance matrix
    num_communes = len(communes['id'].unique())
    num_vehicles = len(trips['vehicle'].unique())
    distance = np.zeros((num_vehicles+1, num_communes+3), dtype=float)

    for _, trip in trips.iterrows():
        vehicle_id = trip['vehicle']
        # Compute the trip distance
        trip_length = tpoint_length(trip['trip']) / 1000.0
        # Add to the vehicle total
        distance[vehicle_id-1][0] += trip_length
        # Add to the column total
        distance[num_vehicles][0] += trip_length

        for _, commune in communes.iterrows():
            commune_id = commune['id']
            atgeom = tpoint_at_geometry(trip['trip'], commune['geom'])
            if atgeom != _ffi.NULL:
                # Compute the length of the trip projected to the commune
                inside_length = tpoint_length(atgeom) / 1000.0
                # Add to the cell
                distance[vehicle_id-1][commune_id] += inside_length
                # Add to the row total
                distance[vehicle_id-1][num_communes+2] += inside_length
                # Add to the commune total
                distance[num_vehicles][commune_id] += inside_length
                # Add to the inside total
                distance[num_vehicles][num_communes+2] += inside_length
        
        minusgeom = tpoint_minus_geometry(trip['trip'], brussels_region['geom'][0])
        if minusgeom != _ffi.NULL:
            outside_length = tpoint_length(minusgeom) / 1000.0
            # Add to the row 
            distance[vehicle_id-1][num_communes+1] += outside_length
            # Add to the column total
            distance[num_vehicles][num_communes+1] += outside_length

    # construct data frame for printing
    columns = ['Distance'] + [str(id) for id in communes['id']] + ['Outside', 'Inside']
    df_distance = pd.DataFrame(distance, columns=columns)
    df_distance.insert(0, 'Vhe', [str(i+1) for i in range(num_vehicles)] + ['total'])
    df_distance.set_index('Vhe', inplace=True)

    # Whether to filter columns with only zero values
    filter_zero = True
    if filter_zero:
        left_cols = [col for col in df_distance.columns if df_distance[col].any()]
        print(tabulate(df_distance[left_cols], headers='keys', tablefmt='psql'))
    else:
        print(tabulate(df_distance, headers='keys', tablefmt='psql'))

    meos_finish()