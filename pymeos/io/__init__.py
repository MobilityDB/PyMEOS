"""
Data-lake interchange for PyMEOS temporal types.

Mirrors the MobilityDuck data-lake consumer recipe so files written by either
tool interoperate: an opaque MEOS-WKB payload column, O(1) native-scalar
bounding-box *sidecar* columns that let Parquet/Arrow engines prune row groups
without decoding the temporal payload, and a ``temporal`` footer declaring the
column encodings.

The public surface lives in :mod:`pymeos.io.parquet`. Importing this package
does not require ``pyarrow``; only calling the read/write helpers does
(``pip install pymeos[parquet]``).
"""

from .parquet import (
    temporal_footer,
    to_arrow,
    from_arrow,
    write_temporal,
    read_temporal,
    FOOTER_VERSION,
    WKB_ENCODING,
    WKB_ENCODING_VERSION,
)

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
