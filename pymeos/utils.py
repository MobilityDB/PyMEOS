from .main import TGeomPointSeq, TGeogPointSeq
from movingpandas import Trajectory
from geopandas import GeoDataFrame
from pymeos_cffi.functions import *
from shapely.geometry import Point

# TODO TGeomPointSeq vs TGeogPointSeq
# Add Trajectory ID & Object ID to TPointSeq?

def get_wkt(traj):
    res = "["
    for row in traj.df.iloc():
        item = row.geometry.wkt + '@' + row.name.__str__()
        res += item + ','
    res = res[:-1] + ']'
    return res

def convert_traj_2_tpointseq(traj : Trajectory):
    if not isinstance(traj, Trajectory):
        raise ValueError("The input should be a Trajectory")
    wkt = get_wkt(traj)
    seq = TGeogPointSeq(string=wkt)
    return seq

def convert_tpointseq_2_traj(seq : TGeogPointSeq):
    if not isinstance(seq, TGeogPointSeq):
        raise ValueError("The input should be a TGeogPointSeq")
    for inst in seq.instants:
        text = tpoint_as_text(inst._inner,10)
        # extract all info from text, or other APIs of MEOS?
        # construct Point and Timestamp, then GeoDataFrame
    gdf = GeoDataFrame()
    traj = Trajectory(df=gdf)
    return traj