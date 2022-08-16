import movingpandas as mpd
import pandas as pd
from pymeos_cffi.functions import meos_initialize, meos_finish
from geopandas import GeoDataFrame
from shapely.geometry import Point
from datetime import datetime

from pymeos.utils import convert_traj_2_tpointseq, convert_tpointseq_2_traj

import warnings
warnings.filterwarnings('ignore')

df = pd.DataFrame([
    {'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
    {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
    {'geometry':Point(6,6), 't':datetime(2018,1,1,12,10,0)},
    {'geometry':Point(9,9), 't':datetime(2018,1,1,12,15,0)}
    ]).set_index('t')

gdf = GeoDataFrame(df, crs=31256)
traj = mpd.Trajectory(gdf, 1)

print("traj:", traj)
print("traj duration:", traj.get_duration())

meos_initialize()

seq = convert_traj_2_tpointseq(traj)
print("seq:", seq)
print("seq duration:", seq.duration)

new_traj = convert_tpointseq_2_traj(seq)
print("new_traj:", new_traj)
print("new_traj duration:", new_traj.get_duration())

meos_finish()


