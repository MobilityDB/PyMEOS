"""Portable bare-name dialect — the single codegen source of truth.

`meta/portable-aliases.json` is the curated, authoritative operator →
bare-name mapping (RFC #920; native in MobilityDB via PR #1075). Folding it
into the catalog means every binding/engine generates the *identical* bare
names, so a user learns one reference and assumes the rest.

This is curated canonical data, not a heuristic — it is preserved verbatim
and only *derived* lookups are added (no guessing of C symbols: upstream
aliases reuse each operator's own backing function, equivalence by
construction). Pure dict → dict; no libclang.
"""

import json
from pathlib import Path


def attach_portable_aliases(idl: dict, path: Path) -> dict:
    """Attach ``idl["portableAliases"]`` from the canonical mapping file."""
    if not Path(path).exists():
        return idl
    data = json.loads(Path(path).read_text())

    pairs = [p for fam in data["families"].values() for p in fam]
    by_operator = {p["operator"]: p["bareName"] for p in pairs}
    by_bare_name = {p["bareName"]: p["operator"] for p in pairs}

    # Integrity: the mapping must be bijective (no operator or bare name may
    # map two ways) — a collision would make codegen ambiguous.
    if len(by_operator) != len(pairs) or len(by_bare_name) != len(pairs):
        raise ValueError("portable-aliases: duplicate operator or bareName")

    idl["portableAliases"] = {
        "provenance": data["provenance"],
        "families": data["families"],
        "alreadyCanonical": data["alreadyCanonical"],
        "explicitBacking": data.get("explicitBacking", {}),
        "scope": data["scope"],          # cbuffer/npoint/pose/rgeo in scope
        "notes": data["notes"],
        "byOperator": by_operator,       # "&&" -> "overlaps"
        "byBareName": by_bare_name,      # "overlaps" -> "&&"
        "bareNames": sorted(by_bare_name),
        "count": len(pairs),
    }
    return idl
