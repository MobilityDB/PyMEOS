import pandas as pd
from geopandas import GeoDataFrame
from movingpandas import Trajectory
from postgis import Point as pPoint
from shapely.geometry import Point as sPoint

from .main import TGeogPointSeq, TGeogPointInst


# TODO TGeomPointSeq vs TGeogPointSeq
# Add Trajectory ID & Object ID to TPointSeq?
# CRS info?

def get_wkt(traj):
    res = "["
    for row in traj.df.iloc():
        item = row.geometry.wkt + '@' + row.name.__str__()
        res += item + ','
    res = res[:-1] + ']'
    return res


def shapely_2_postgis_point(point: sPoint):
    return pPoint(point.x, point.y)


def postgis_2_sharpely_point(point: pPoint):
    return sPoint(point.x, point.y)


def extract_coordinate(tpointinst_text: str):
    start = tpointinst_text.find('(')
    end = tpointinst_text.find(')')
    coordinate_text = tpointinst_text[start + 1:end]
    coordinate = [float(n) for n in coordinate_text.split()]
    return coordinate


def convert_traj_2_tpointseq(traj: Trajectory, normalize=False):
    # extract wkt string from trajectory for conversion
    if not isinstance(traj, Trajectory):
        raise ValueError("The input should be a Trajectory")
    wkt = get_wkt(traj)
    seq = TGeogPointSeq(string=wkt, normalize=normalize)
    return seq


def convert_traj_2_tpointseq_v1(traj: Trajectory, normalize=False):
    # extract the coordinates and timestampe from trajectory for conversion
    if not isinstance(traj, Trajectory):
        raise ValueError("The input should be a Trajectory")
    geom_column_name = traj.get_geom_column_name()
    # By checking the initialization function of TGeogPointInst, it still uses wkt string as input.
    # That's might be why this function is slow
    instant_list = [
        TGeogPointInst(point=shapely_2_postgis_point(traj.df.iloc[i][geom_column_name]), timestamp=traj.df.iloc[i].name)
        for i in range(len(traj.df))]
    seq = TGeogPointSeq(instant_list=instant_list, normalize=normalize)
    return seq


def convert_traj_2_tpointseq_v2(traj: Trajectory, normalize=False):
    # extract the coordinates and timestampe from trajectory for conversion
    if not isinstance(traj, Trajectory):
        raise ValueError("The input should be a Trajectory")
    geom_column_name = traj.get_geom_column_name()
    instant_list = [TGeogPointInst(
        string=f"POINT({traj.df.iloc[i][geom_column_name].x} {traj.df.iloc[i][geom_column_name].y})@{traj.df.iloc[i].name}")
                    for i in range(len(traj.df))]
    seq = TGeogPointSeq(instant_list=instant_list, normalize=normalize)
    return seq


def convert_tpointseq_2_traj(seq: TGeogPointSeq):
    if not isinstance(seq, TGeogPointSeq):
        raise ValueError("The input should be a TGeogPointSeq")
    data = list()
    for inst in seq.instants:
        # TODO: extract coordinate directly from inst.value 'GSERIALIZED'
        coordinate = extract_coordinate(tpoint_as_text(inst._inner, 10))
        t = inst.timestamp
        data.append([sPoint(coordinate[0], coordinate[1]), t])
    df = pd.DataFrame(data, columns=["geometry", "t"]).set_index('t')
    gdf = GeoDataFrame(df)
    traj = Trajectory(df=gdf, traj_id=0)
    return traj
