"""
Edge-to-cloud data-lake quickstart for PyMEOS.

Python port of the MobilityDuck ``examples/quickstart/quickstart.sql`` recipe.
Files written here are interoperable with MobilityDuck: same MEOS-WKB payload,
same native-scalar sidecar columns, same ``temporal`` footer.

Run with the ``parquet`` extra installed::

    pip install "pymeos[parquet]"
    python examples/datalake_quickstart.py
"""

from datetime import datetime, timedelta, timezone

from pymeos import pymeos_initialize, pymeos_finalize, TGeogPointSeq
from pymeos.io.parquet import write_temporal, read_temporal

pymeos_initialize("UTC")
try:
    # 1. Raw pings -> one trajectory per moving entity.
    base = datetime(2026, 1, 15, tzinfo=timezone.utc)
    fleet = [
        (1, 10.00, 55.50, 0.23, 0.05),
        (2, 14.00, 56.00, -0.18, -0.08),
        (3, 8.50, 57.50, 0.06, -0.06),
        (4, 12.10, 55.20, 0.04, 0.02),
        (5, 9.50, 54.50, 0.22, 0.06),
    ]

    def trajectory(lon, lat, dlon, dlat):
        pings = ", ".join(
            f"Point({lon + dlon * s:.6f} {lat + dlat * s:.6f})@"
            f"{(base + timedelta(minutes=10 * s)).isoformat()}"
            for s in range(12)
        )
        return TGeogPointSeq(f"[{pings}]")

    rows = {
        "entity_id": [e[0] for e in fleet],
        "traj": [trajectory(*e[1:]) for e in fleet],
    }
    print(f"{len(rows['entity_id'])} trajectories")

    # 2. Write to Parquet: MEOS-WKB payload + native-scalar sidecars
    #    (traj_ts_min/max, traj_x/y_min/max) + the `temporal` footer.
    path = "edge_to_cloud_demo.parquet"
    write_temporal(rows, path, row_group_size=2)

    # 3. Cloud side: prune on a native sidecar column *without* decoding any
    #    trajectory, then reconstruct only the survivors from WKB.
    window_start = base + timedelta(minutes=20)
    selected = read_temporal(path, filters=[("traj_ts_max", ">=", window_start)])
    print(f"{len(selected['entity_id'])} trajectories overlap the window")

    for eid, traj in zip(selected["entity_id"], selected["traj"]):
        print(
            f"  entity {eid}: length={traj.length():.1f} m, "
            f"type={type(traj).__name__}"
        )
finally:
    pymeos_finalize()
