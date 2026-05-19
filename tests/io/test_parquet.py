from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("pyarrow")  # the optional `parquet` extra

import pyarrow as pa  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

from pymeos import TGeogPointSeq, TFloatSeq  # noqa: E402
from pymeos.io.parquet import (  # noqa: E402
    temporal_footer,
    to_arrow,
    from_arrow,
    write_temporal,
    read_temporal,
)

# Byte-for-byte output of MobilityDuck's temporalFooter() (interop contract).
_MOBILITYDUCK_FOOTER = (
    '{"version":"1.0.0","columns":{"traj":{"encoding":"MEOS-WKB",'
    '"encoding_version":"1.0","base_type":"tgeogpoint"}}}'
)


def _base():
    return datetime(2026, 1, 15, tzinfo=timezone.utc)


def _traj(lon, lat, dlon, dlat):
    pts = ", ".join(
        f"Point({lon + dlon * s:.6f} {lat + dlat * s:.6f})@"
        f"{(_base() + timedelta(minutes=10 * s)).isoformat()}"
        for s in range(12)
    )
    return TGeogPointSeq(f"[{pts}]")


def test_footer_is_byte_identical_to_mobilityduck():
    assert temporal_footer({"traj": "tgeogpoint"}) == _MOBILITYDUCK_FOOTER


def test_to_arrow_emits_wkb_payload_sidecars_and_footer():
    rows = {
        "entity_id": [1, 2],
        "traj": [_traj(10, 55, 0.2, 0.05), _traj(14, 56, -0.1, -0.08)],
    }
    tbl = to_arrow(rows)

    assert b"temporal" in (tbl.schema.metadata or {})
    assert pa.types.is_binary(tbl.schema.field("traj").type)
    for c in (
        "traj_ts_min",
        "traj_ts_max",
        "traj_x_min",
        "traj_x_max",
        "traj_y_min",
        "traj_y_max",
    ):
        assert c in tbl.column_names
    assert pa.types.is_timestamp(tbl.schema.field("traj_ts_min").type)
    assert pa.types.is_floating(tbl.schema.field("traj_x_min").type)


def test_parquet_roundtrip_footer_and_sidecar_pushdown(tmp_path):
    rows = {
        "entity_id": [1, 2, 3],
        "traj": [
            _traj(10, 55, 0.2, 0.05),
            _traj(8.5, 57.5, 0.06, -0.06),
            _traj(9.5, 54.5, 0.22, 0.06),
        ],
    }
    path = str(tmp_path / "demo.parquet")
    write_temporal(rows, path, row_group_size=1)

    assert pq.read_metadata(path).metadata[b"temporal"] == _MOBILITYDUCK_FOOTER.encode()

    # every trajectory starts at _base(); a >= cutoff filter prunes everything
    cutoff = _base() + timedelta(minutes=30)
    pruned = read_temporal(path, filters=[("traj_ts_min", ">=", cutoff)])
    assert len(pruned["entity_id"]) == 0

    full = read_temporal(path)
    assert len(full["entity_id"]) == 3
    assert type(full["traj"][0]).__name__.startswith("TGeogPoint")
    assert full["traj"][0] == rows["traj"][0]  # WKB round-trip is lossless


def test_tfloat_numeric_sidecars_roundtrip():
    data = {"id": [1], "v": [TFloatSeq("[1@2026-01-01, 9@2026-01-02]")]}
    tbl = to_arrow(data)
    assert {"v_v_min", "v_v_max", "v_ts_min", "v_ts_max"}.issubset(
        set(tbl.column_names)
    )
    back = from_arrow(tbl)
    assert back["v"][0] == data["v"][0]
