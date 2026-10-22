#!/usr/bin/env python3
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# meos-idl.json-driven generator for PyMEOS's *regular* OO method families.
#
# This is the high-level analogue of two existing artifacts in the ecosystem:
#
#   * GoMEOS PR #2 (refactor/codegen-meos-idl, tools/codegen.py -> tools/
#     _preview/): the non-destructive Draft-artifact discipline -- a vendored
#     meos-idl.json, output written to an underscore-prefixed `_preview/`
#     directory that the package never imports, GoMEOS-style coverage stats,
#     and explicit counted exclusions (Datum-bearing internals, irregular
#     shapes) instead of silent gaps.
#
#   * PyMEOS PR #87 (tools/portable_aliases/generate.py): the in-repo
#     content model -- every generated callable DISPATCHES to the EXACT
#     pymeos_cffi backing function the hand-written surface uses, by the
#     argument's runtime type; nothing is reimplemented, so each generated
#     method is identical to the hand-written one by construction
#     (aliases-reuse-backing).
#
# The hand-written PyMEOS types (pymeos/main/t*.py) spell out, by hand and
# uniformly across every temporal type, a set of *regular* method families:
# comparison, spatial relationship (ever/always/temporal), distance, and
# restriction.  Each member is a thin isinstance ladder that forwards
# self._inner + the unwrapped argument to a typed MEOS overload and post-
# processes the result deterministically.  That regularity is exactly what a
# signature catalog can synthesise: this tool reads the vendored
# meos-idl.json, groups the regular-family C functions by temporal type
# family and member, and emits one dispatching method per (family, member)
# into tools/oo_codegen/_preview/<family>_methods.py.
#
# The irregular core -- constructors, conversions, accessors, transforms,
# I/O -- is NOT generatable from signatures alone (it needs per-function
# editorial decisions) and stays hand-written.  The generator counts and
# names every function it does not emit; nothing is silently dropped.
#
# Output is a Draft artifact: tools/oo_codegen/_preview/ is never imported
# by the pymeos package.  It lets a reviewer diff the generated uniform
# surface against the hand-written one before any staged migration.
#
# Usage:
#   python3 tools/oo_codegen/codegen.py [--idl <path>] [--out <dir>] [--check]

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDL = HERE / "meos-idl.json"
PREVIEW = HERE / "_preview"

# The six in-scope temporal type families, witnessed on the C function name
# exactly as PyMEOS PR #87's tools/portable_aliases/generate.py does (kept
# byte-compatible so the two generators agree on what "a family" is).  Order
# is significant: the most specific token wins, so `geo` does not swallow a
# `tcbuffer`/`tnpoint`/`tpose`/`trgeometry` name.
FAMILY_PATTERNS = [
    ("cbuffer", r"cbuffer"),
    ("npoint", r"npoint"),
    ("pose", r"(^|_)t?pose(_|$)"),
    ("rgeo", r"(t?rgeo|trgeometry|rgeometry)"),
    ("geo", r"(^|_)(tgeo|tgeompoint|tgeogpoint|tpoint|tspatial|geo|geom|geog)(_|$)"),
    ("temporal", r"(^|_)(temporal|tnumber|tbool|tint|tfloat|ttext)(_|$)"),
]
_FAMILY_RE = [(f, re.compile(p, re.I)) for f, p in FAMILY_PATTERNS]

# Result post-processing kind for each regular member class:
#   bool_gt0  -> `> 0`               (ever/always equality predicates)
#   bool_eq1  -> `== 1`              (ever/always spatial relationships)
#   temporal  -> Temporal._factory   (temporal predicates / restriction /
#                                     temporal comparison / temporal distance)
#   scalar    -> pass through        (nearest-approach distance: float)
#   wrap      -> generic factory     (nearest-approach instant, shortest line)
#
# Member spec: C-name prefix -> (oo_method_name, result_kind).  These are the
# exact prefixes observed in meos-idl.json across the six family headers; the
# oo_method_name matches the hand-written method so a reviewer can diff them
# line for line.
MEMBER_SPEC: dict[str, tuple[str, str]] = {
    # --- comparison (boolean) ---
    "always_eq": ("always_equal", "bool_gt0"),
    "always_ne": ("always_not_equal", "bool_gt0"),
    "ever_eq": ("ever_equal", "bool_gt0"),
    "ever_ne": ("ever_not_equal", "bool_gt0"),
    # --- comparison (temporal) ---
    "teq": ("temporal_equal", "temporal"),
    "tne": ("temporal_not_equal", "temporal"),
    "tlt": ("temporal_less", "temporal"),
    "tle": ("temporal_less_or_equal", "temporal"),
    "tgt": ("temporal_greater", "temporal"),
    "tge": ("temporal_greater_or_equal", "temporal"),
    # --- spatial relationship: ever ---
    "econtains": ("is_ever_contains", "bool_eq1"),
    "ecovers": ("is_ever_covers", "bool_eq1"),
    "edisjoint": ("is_ever_disjoint", "bool_eq1"),
    "edwithin": ("is_ever_within_distance", "bool_eq1"),
    "eintersects": ("ever_intersects", "bool_eq1"),
    "etouches": ("ever_touches", "bool_eq1"),
    # --- spatial relationship: always ---
    "acontains": ("is_always_contains", "bool_eq1"),
    "acovers": ("is_always_covers", "bool_eq1"),
    "adisjoint": ("is_always_disjoint", "bool_eq1"),
    "adwithin": ("is_always_within_distance", "bool_eq1"),
    "aintersects": ("always_intersects", "bool_eq1"),
    "atouches": ("always_touches", "bool_eq1"),
    # --- spatial relationship: temporal ---
    "tcontains": ("contains", "temporal"),
    "tcovers": ("covers", "temporal"),
    "tdisjoint": ("disjoint", "temporal"),
    "tdwithin": ("within_distance", "temporal"),
    "tintersects": ("intersects", "temporal"),
    "ttouches": ("touches", "temporal"),
    # --- distance ---
    "tdistance": ("distance", "temporal"),
    "nad": ("nearest_approach_distance", "scalar"),
    "nai": ("nearest_approach_instant", "wrap"),
    "shortestline": ("shortest_line", "wrap"),
}

# Regular restriction members are spelled `<typefamtoken>_at_*` /
# `<typefamtoken>_minus_*` (and the generic `temporal_at_*`/`temporal_minus_*`
# fallbacks), so they are matched structurally rather than by a fixed prefix.
_RESTRICT_RE = re.compile(r"^[a-z0-9]+_(at|minus)_[a-z0-9]+$")

# Longest-first so `always_eq`/`ever_eq` are tried before any shorter token
# and `tdistance` before a hypothetical `t`-prefixed member.
_MEMBER_PREFIXES = sorted(MEMBER_SPEC, key=len, reverse=True)


def _family_of(cname: str) -> str | None:
    for fam, rx in _FAMILY_RE:
        if rx.search(cname):
            return fam
    return None


def _is_datum_internal(entry: dict) -> bool:
    """Datum-bearing functions are MEOS-internal helpers the hand-written
    surface re-exposes through typed overloads; the codegen cannot synthesise
    those overloads from signatures, so they are an explicit counted
    exclusion, never a silent gap (mirrors GoMEOS codegen)."""
    if "Datum" in entry["returnType"]["c"].split():
        return True
    return any("Datum" in p["cType"].split() for p in entry["params"])


def _arg_token(cname: str, member: str, kind: str) -> str:
    """The dispatch key for an overload: the trailing C-name token(s) after
    the member prefix and the type-family token.  Mirrors the isinstance
    ladder of the hand-written method but is derived deterministically from
    the catalog (e.g. ``econtains_tcbuffer_cbuffer`` -> ``cbuffer``,
    ``temporal_at_tstzspan`` -> ``tstzspan``)."""
    if kind == "restrict":
        # `<typefam>_at_<arg>` -> arg is everything after `_at_`/`_minus_`.
        return re.sub(r"^[a-z0-9]+_(at|minus)_", "", cname)
    rest = cname[len(member) :].lstrip("_")
    parts = rest.split("_")
    # Drop the first token (the type-family token: tcbuffer/tnpoint/...); the
    # remainder is the argument kind.  A single token means a self-only
    # overload (rare); key it on the type family itself.
    return "_".join(parts[1:]) if len(parts) > 1 else (parts[0] if parts else "")


@dataclass
class Method:
    oo_name: str
    kind: str
    # arg-kind token -> backing pymeos_cffi C function name
    overloads: dict[str, str] = field(default_factory=dict)
    c_names: list[str] = field(default_factory=list)


@dataclass
class Stats:
    emitted_methods: int = 0
    emitted_overloads: int = 0
    datum: int = 0
    irregular: int = 0
    out_of_scope: int = 0
    by_family: dict = field(default_factory=lambda: defaultdict(int))


def collect(idl: dict) -> tuple[dict[str, dict[str, Method]], Stats]:
    """Group regular-family functions into family -> {oo_name: Method}."""
    fams: dict[str, dict[str, Method]] = defaultdict(dict)
    st = Stats()
    for entry in idl["functions"]:
        cname = entry["name"]
        fam = _family_of(cname)
        if fam is None:
            st.out_of_scope += 1
            continue
        if _is_datum_internal(entry):
            st.datum += 1
            continue

        member = next(
            (p for p in _MEMBER_PREFIXES if cname == p or cname.startswith(p + "_")),
            None,
        )
        if member is not None:
            oo_name, kind = MEMBER_SPEC[member]
            token = _arg_token(cname, member, "member")
        elif _RESTRICT_RE.match(cname):
            verb = _RESTRICT_RE.match(cname).group(1)
            oo_name, kind = ("at" if verb == "at" else "minus"), "restrict"
            token = _arg_token(cname, "", "restrict")
        else:
            # In-scope but not a regular family member: a constructor,
            # conversion, accessor, transform or I/O function that stays
            # hand-written.  Counted, not dropped.
            st.irregular += 1
            continue

        meth = fams[fam].setdefault(oo_name, Method(oo_name, kind))
        # First overload wins a key; collisions across headers are recorded
        # so a reviewer sees every backing symbol.
        meth.overloads.setdefault(token or fam, cname)
        meth.c_names.append(cname)
        st.emitted_overloads += 1
        st.by_family[fam] += 1
    return fams, st


# --- emission -----------------------------------------------------------

_RESULT_EXPR = {
    "bool_gt0": "_r > 0",
    "bool_eq1": "_r == 1",
    "temporal": "Temporal._factory(_r)",
    "scalar": "_r",
    "wrap": "_wrap(_r)",
    "restrict": "Temporal._factory(_r)",
}

_MODULE_HEADER = '''\
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# ============================================================================
#  GENERATED by tools/oo_codegen/codegen.py -- DO NOT EDIT.  DRAFT ARTIFACT.
#  Regenerate:  python3 tools/oo_codegen/codegen.py
# ============================================================================
#
# This is a NON-DESTRUCTIVE preview of the regular "{family}" OO method
# families synthesised from the vendored meos-idl.json.  It is NOT imported
# by the pymeos package (the directory is underscore-prefixed); it exists so
# a reviewer can diff this uniform, deterministic surface against the hand-
# written pymeos/main/*.py before any staged migration.
#
# Every generated method DISPATCHES, by the C-name token of its argument, to
# the EXACT pymeos_cffi backing function the hand-written method uses -- the
# same native call, never reimplemented (aliases-reuse-backing): each method
# is identical to its hand-written counterpart by construction.
"""Preview of generated regular OO methods for the {family} family."""
from __future__ import annotations

# Resolved lazily so importing this Draft module never requires the compiled
# binding (parity checks / docs).
_cffi = None


def _c():
    global _cffi
    if _cffi is None:
        import pymeos_cffi as _m

        _cffi = _m
    return _cffi


def _unwrap(a):
    return a._inner if hasattr(a, "_inner") else a


def _wrap(_r):
    """Re-wrap a MEOS-object result with the existing PyMEOS factories;
    scalars and None pass straight through (mirrors PR #87's _wrap)."""
    if _r is None or isinstance(_r, (bool, int, float, str, bytes)):
        return _r
    from pymeos.factory import _TemporalFactory, _CollectionFactory

    for fn in (_TemporalFactory.create_temporal,
               _CollectionFactory.create_collection):
        try:
            return fn(_r)
        except Exception:
            pass
    return _r


class Temporal:  # noqa: D101  (diff-readability stand-in for the real base)
    @staticmethod
    def _factory(_r):
        return _wrap(_r)

'''

_METHOD_TMPL = '''
    # MEOS Functions: {meos_fns}
    def {oo_name}(self, other):
        """Generated regular `{oo_name}` -> exact pymeos_cffi backing call."""
        _disp = {table!r}
        _key = getattr(other, "__meos_token__", type(other).__name__.lower())
        _sym = _disp.get(_key) or (next(iter(_disp.values()))
                                   if len(_disp) == 1 else None)
        if _sym is None:
            raise TypeError(
                f"{oo_name}(): no overload for {{type(other).__name__}}; "
                f"argument kinds: {{sorted(_disp)}}")
        _r = getattr(_c(), _sym)(self._inner, _unwrap(other))
        return {result_expr}
'''


def emit(fams: dict[str, dict[str, Method]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for family, methods in sorted(fams.items()):
        cls = "T" + family.capitalize() + "Methods"
        body = [_MODULE_HEADER.format(family=family)]
        body.append(f"\nclass {cls}:\n")
        body.append(
            f'    """Generated regular methods for the {family} '
            f'family (preview)."""\n'
        )
        if not methods:
            body.append("    pass\n")
        for oo_name in sorted(methods):
            m = methods[oo_name]
            body.append(
                _METHOD_TMPL.format(
                    oo_name=oo_name,
                    meos_fns=", ".join(sorted(set(m.c_names))),
                    table=m.overloads,
                    result_expr=_RESULT_EXPR[m.kind],
                )
            )
        (out_dir / f"{family}_methods.py").write_text("".join(body))


# --- driver -------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--idl", default=str(IDL))
    ap.add_argument("--out", default=str(PREVIEW))
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if any in-scope function is neither "
        "emitted nor counted as an explicit exclusion",
    )
    args = ap.parse_args()

    idl = json.loads(Path(args.idl).read_text())
    fams, st = collect(idl)
    emit(fams, Path(args.out))

    st.emitted_methods = sum(len(m) for m in fams.values())
    total = len(idl["functions"])
    accounted = st.emitted_overloads + st.datum + st.irregular + st.out_of_scope

    print(f"[oo-codegen] idl functions       : {total}")
    print(
        f"[oo-codegen] emitted methods     : {st.emitted_methods} "
        f"({st.emitted_overloads} overloads) across "
        f"{len(fams)} families"
    )
    for fam in sorted(st.by_family):
        print(
            f"               {fam:<9}: {len(fams[fam]):>3} methods, "
            f"{st.by_family[fam]:>4} overloads"
        )
    print(
        f"[oo-codegen] hand-written core   : {st.irregular} "
        f"(constructors/conversions/accessors/transforms/IO)"
    )
    print(f"[oo-codegen] Datum-internal      : {st.datum} (excluded)")
    print(
        f"[oo-codegen] out of scope        : {st.out_of_scope} "
        f"(non-temporal-family headers)"
    )
    print(f"[oo-codegen] accounted           : {accounted}/{total}")

    unaccounted = total - accounted
    ok = unaccounted == 0 and len(fams) == 6
    if args.check:
        print(
            "CHECK: "
            + (
                "PASS - every function emitted or explicitly "
                "counted, all 6 families present"
                if ok
                else f"FAIL - {unaccounted} unaccounted, " f"{len(fams)} families"
            )
        )
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
