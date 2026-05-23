"""
Parquet / Arrow data-lake interchange for PyMEOS temporal types.

Recipe (identical to the MobilityDuck data-lake consumer, so files written by
either tool interoperate):

* the temporal column is stored as an opaque **MEOS-WKB** payload
  (``Temporal.as_wkb()``),
* O(1) **native-scalar sidecar** columns are derived from each value's inline
  bounding box (``ts_min``/``ts_max`` and, per type, ``x*/y*/z*`` spatial or
  ``v*`` numeric bounds) so a Parquet/Arrow engine prunes row groups from
  column statistics *without decoding the payload*,
* a ``temporal`` footer (Parquet ``KV_METADATA`` / Arrow schema metadata)
  declares each temporal column's encoding and base type.

``pyarrow`` is required only to call these helpers (``pip install
pymeos[parquet]``).
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Optional, Sequence, Union

FOOTER_KEY = "temporal"
FOOTER_VERSION = "1.0.0"
WKB_ENCODING = "MEOS-WKB"
WKB_ENCODING_VERSION = "1.0"

__all__ = [
    "temporal_footer",
    "to_arrow",
    "from_arrow",
    "write_temporal",
    "read_temporal",
    "FOOTER_VERSION",
    "WKB_ENCODING",
    "WKB_ENCODING_VERSION",
]


def _pa():
    try:
        import pyarrow as pa  # noqa: F401

        return pa
    except ModuleNotFoundError as e:  # pragma: no cover - exercised via extra
        raise ModuleNotFoundError(
            "pyarrow is required for pymeos.io; install it with "
            "`pip install pymeos[parquet]`"
        ) from e


def _pq():
    _pa()
    import pyarrow.parquet as pq

    return pq


# --------------------------------------------------------------------------- #
# Footer (interop contract, byte-identical to MobilityDuck temporalFooter())
# --------------------------------------------------------------------------- #
def temporal_footer(columns: Mapping[str, str]) -> str:
    """
    Build the ``temporal`` footer JSON declaring the WKB-encoded columns.

    Byte-identical to MobilityDuck's ``temporalFooter()`` so a Parquet file is
    portable across both tools::

        {"version":"1.0.0","columns":{"<col>":{"encoding":"MEOS-WKB",
         "encoding_version":"1.0","base_type":"<type>"}}}

    Args:
        columns: mapping of column name to MEOS base type (e.g.
            ``{"trip": "tgeompoint"}``).

    Returns:
        The footer as a compact JSON string.
    """
    payload = {
        "version": FOOTER_VERSION,
        "columns": {
            name: {
                "encoding": WKB_ENCODING,
                "encoding_version": WKB_ENCODING_VERSION,
                "base_type": base_type,
            }
            for name, base_type in columns.items()
        },
    }
    return json.dumps(payload, separators=(",", ":"))


def _parse_footer(blob: Optional[bytes]) -> dict:
    if not blob:
        return {}
    footer = json.loads(blob.decode("utf-8") if isinstance(blob, bytes) else blob)
    return footer.get("columns", {})


# --------------------------------------------------------------------------- #
# Type/bbox introspection
# --------------------------------------------------------------------------- #
def _base_type_name(obj: Any) -> str:
    from ..main import TGeomPoint, TGeogPoint, TInt, TFloat, TBool, TText

    if isinstance(obj, TGeomPoint):
        return "tgeompoint"
    if isinstance(obj, TGeogPoint):
        return "tgeogpoint"
    if isinstance(obj, TInt):
        return "tint"
    if isinstance(obj, TFloat):
        return "tfloat"
    if isinstance(obj, TBool):
        return "tbool"
    if isinstance(obj, TText):
        return "ttext"
    raise TypeError(f"unsupported temporal type: {type(obj).__name__}")


def _sidecar_values(obj: Any) -> "dict[str, Any]":
    """Native-scalar bounds extracted O(1) from the value's inline bbox."""
    from ..main import TPoint, TNumber

    if isinstance(obj, TPoint):
        box = obj.bounding_box()
        out = {
            "ts_min": box.tmin(),
            "ts_max": box.tmax(),
            "x_min": box.xmin(),
            "x_max": box.xmax(),
            "y_min": box.ymin(),
            "y_max": box.ymax(),
        }
        if box.zmin() is not None:
            out["z_min"] = box.zmin()
            out["z_max"] = box.zmax()
        return out
    if isinstance(obj, TNumber):
        box = obj.bounding_box()
        return {
            "ts_min": box.tmin(),
            "ts_max": box.tmax(),
            "v_min": box.xmin(),
            "v_max": box.xmax(),
        }
    span = obj.bounding_box()  # TsTzSpan for tbool / ttext
    return {"ts_min": span.lower(), "ts_max": span.upper()}


_TS_KEYS = {"ts_min", "ts_max"}


def _sidecar_arrow_type(suffix: str):
    pa = _pa()
    return pa.timestamp("us", tz="UTC") if suffix in _TS_KEYS else pa.float64()


# --------------------------------------------------------------------------- #
# Columnar normalisation
# --------------------------------------------------------------------------- #
def _as_columns(data: Any) -> "dict[str, list]":
    # pandas DataFrame
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        return {c: list(data[c]) for c in data.columns}
    # Mapping of column -> sequence
    if isinstance(data, Mapping):
        return {k: list(v) for k, v in data.items()}
    # Sequence of row mappings
    rows = list(data)
    if rows and isinstance(rows[0], Mapping):
        keys = list(rows[0].keys())
        return {k: [r.get(k) for r in rows] for k in keys}
    raise TypeError(
        "data must be a pandas DataFrame, a {column: sequence} mapping, "
        "or a sequence of row dicts"
    )


def _is_temporal(value: Any) -> bool:
    from ..temporal import Temporal

    return isinstance(value, Temporal)


def _detect_temporal_columns(
    cols: "dict[str, list]", explicit: Optional[Sequence[str]]
) -> "list[str]":
    if explicit is not None:
        return list(explicit)
    detected = []
    for name, values in cols.items():
        if any(v is not None and _is_temporal(v) for v in values):
            detected.append(name)
    return detected


# --------------------------------------------------------------------------- #
# Arrow-native API
# --------------------------------------------------------------------------- #
def to_arrow(
    data: Any,
    *,
    temporal_columns: Optional[Sequence[str]] = None,
    sidecars: bool = True,
):
    """
    Build a ``pyarrow.Table`` with WKB payload columns, native-scalar sidecars
    and the ``temporal`` footer in the schema metadata.

    Args:
        data: a pandas ``DataFrame``, a ``{column: sequence}`` mapping, or a
            sequence of row dicts.
        temporal_columns: columns to encode; auto-detected (any column holding
            ``Temporal`` values) when omitted.
        sidecars: also emit ``<col>_ts_min``/``ts_max`` and the per-type
            spatial (``x/y/z``) or numeric (``v``) bound columns.

    Returns:
        ``pyarrow.Table``.
    """
    pa = _pa()
    cols = _as_columns(data)
    temporal_cols = _detect_temporal_columns(cols, temporal_columns)

    arrays: "dict[str, Any]" = {}
    footer_cols: "dict[str, str]" = {}

    for name, values in cols.items():
        if name not in temporal_cols:
            arrays[name] = pa.array(values)
            continue

        base_type = None
        wkb_col: "list[Optional[bytes]]" = []
        per_row: "list[Optional[dict]]" = []  # row-aligned sidecar dicts
        for v in values:
            if v is None:
                wkb_col.append(None)
                per_row.append(None)
                continue
            if base_type is None:
                base_type = _base_type_name(v)
            wkb_col.append(v.as_wkb())
            per_row.append(_sidecar_values(v) if sidecars else None)
        if base_type is None:
            raise ValueError(f"temporal column {name!r} is entirely null")
        footer_cols[name] = base_type
        arrays[name] = pa.array(wkb_col, type=pa.binary())
        if sidecars:
            suffixes: "list[str]" = []
            for d in per_row:
                for k in d or ():
                    if k not in suffixes:
                        suffixes.append(k)
            for suffix in suffixes:
                col = [None if d is None else d.get(suffix) for d in per_row]
                arrays[f"{name}_{suffix}"] = pa.array(
                    col, type=_sidecar_arrow_type(suffix)
                )

    table = pa.table(arrays)
    md = dict(table.schema.metadata or {})
    md[FOOTER_KEY.encode()] = temporal_footer(footer_cols).encode("utf-8")
    return table.replace_schema_metadata(md)


def from_arrow(table, *, reconstruct: bool = True):
    """
    Reverse of :func:`to_arrow`. Reads the ``temporal`` footer and, when
    ``reconstruct`` is set, rebuilds PyMEOS objects from the WKB columns
    (the type is recovered from the WKB itself, the footer is advisory).

    Returns a ``dict`` of ``{column: list}`` (sidecar columns preserved).
    """
    _pa()
    from ..temporal import Temporal

    footer = _parse_footer((table.schema.metadata or {}).get(FOOTER_KEY.encode()))
    out: "dict[str, list]" = {}
    for name in table.column_names:
        values = table.column(name).to_pylist()
        if reconstruct and name in footer:
            out[name] = [None if v is None else Temporal.from_wkb(v) for v in values]
        else:
            out[name] = values
    return out


# --------------------------------------------------------------------------- #
# Parquet file API
# --------------------------------------------------------------------------- #
def write_temporal(
    data: Any,
    path: str,
    *,
    temporal_columns: Optional[Sequence[str]] = None,
    sidecars: bool = True,
    row_group_size: Optional[int] = None,
    **write_kwargs: Any,
) -> None:
    """
    Write ``data`` to a Parquet file using the data-lake recipe. The
    ``temporal`` footer lands in the Parquet ``KV_METADATA`` and the native
    sidecar columns carry the row-group statistics used for pushdown.
    """
    pq = _pq()
    table = to_arrow(data, temporal_columns=temporal_columns, sidecars=sidecars)
    pq.write_table(table, path, row_group_size=row_group_size, **write_kwargs)


def read_temporal(
    path: str,
    *,
    columns: Optional[Sequence[str]] = None,
    filters: Optional[Any] = None,
    reconstruct: bool = True,
):
    """
    Read a Parquet file written by :func:`write_temporal` (or MobilityDuck).

    ``filters`` is passed straight to ``pyarrow.parquet``; predicates on the
    native sidecar columns (e.g. ``[("trip_ts_min", "<=", end)]``) prune row
    groups before any WKB is decoded.
    """
    pq = _pq()
    table = pq.read_table(
        path, columns=list(columns) if columns else None, filters=filters
    )
    return from_arrow(table, reconstruct=reconstruct)
