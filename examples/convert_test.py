import movingpandas as mpd
import pandas as pd
import geopandas as gpd
import shapely as shp
from pymeos import TGeomPointSeq
from pymeos_cffi.functions import meos_initialize, meos_finish
from geopandas import GeoDataFrame
from shapely.geometry import Point
from datetime import datetime

from pymeos.utils import convert_traj_2_tpointseq

df = pd.DataFrame([
    {'geometry':Point(0,0), 't':datetime(2018,1,1,12,0,0)},
    {'geometry':Point(6,0), 't':datetime(2018,1,1,12,6,0)},
    {'geometry':Point(6,6), 't':datetime(2018,1,1,12,10,0)},
    {'geometry':Point(9,9), 't':datetime(2018,1,1,12,15,0)}
    ]).set_index('t')

gdf = GeoDataFrame(df, crs=31256)
traj = mpd.Trajectory(gdf, 1)

meos_initialize()

seq = convert_traj_2_tpointseq(traj)
print(seq)
# print(f'Total speed: {seq.speed}')
# print(f'Total distance: {seq.distance}')

meos_finish()


