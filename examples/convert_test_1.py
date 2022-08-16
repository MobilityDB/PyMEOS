import movingpandas as mpd
import pandas as pd
from pymeos_cffi.functions import meos_initialize, meos_finish
from geopandas import GeoDataFrame, read_file
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

import time
import os

from pymeos.utils import convert_traj_2_tpointseq, convert_tpointseq_2_traj, \
    convert_traj_2_tpointseq_v1

import warnings
warnings.filterwarnings('ignore')

start = time.time()

# Test with geo_small.gpkg
# path = os.path.dirname(os.path.abspath(__file__)) + '/data/geo_small.gpkg'
# gdf = read_file(path)
# traj_collection = mpd.TrajectoryCollection(gdf, 'trajectory_id', t='t')
# traj = traj_collection.trajectories[1]

# Test with aisinput.csv
path = os.path.dirname(os.path.abspath(__file__)) + '/aisinput.csv'
pdf = pd.read_csv(path)
gdf = GeoDataFrame(pdf.drop(['latitude', 'longitude'], axis=1),
                       geometry=gpd.points_from_xy(pdf.longitude, pdf.latitude))
ships = mpd.TrajectoryCollection(gdf, 'mmsi', t='t')
traj = ships.trajectories[0]
load_time = time.time() - start

print("traj:", traj)
print("traj duration:", traj.get_duration())

meos_initialize()

start = time.time()
seq = convert_traj_2_tpointseq(traj)
time_traj2tpointseq = time.time()-start

# print("seq:", seq)
print("seq num_instants:", seq.num_instants)
print("seq duration:", seq.duration)

start = time.time()
new_traj = convert_tpointseq_2_traj(seq)
time_tpointseq2traj = time.time()-start

print("new_traj:", new_traj)
print("new_traj duration:", new_traj.get_duration())

meos_finish()

print("\nTIME USAGE")
print("load data & construct traj:", load_time)
print("traj -> tpointseq:", time_traj2tpointseq)
print("tpointseq -> traj:", time_tpointseq2traj)

