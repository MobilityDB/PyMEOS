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
import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
IDL = HERE / "meos-idl.json"
PREVIEW = HERE / "_preview"
# RFC #94 §7 / MEOS-API #10 objectModel.dispatch keystone: the verbatim
# extended dispatch metadata (geo + the 4 temporal concretes, the two
# families not mechanically derivable from the signature catalog) and the
# byte-for-byte hand-written oracle it must reproduce. Used by the
# --verify-oo-dispatch-extended A/B gate (analogue of --verify-oo-
# roundtrip for the non-derivable families).
DISPATCH_EXT_FIXTURE = HERE / "_d1-dispatch-extended-fixture.json"
ORACLE_EXT = HERE / "_oracle_extended_methods.py"

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
    # backing C function name -> its IDL canonical param type list (used by
    # the faithful-mixin emitter to detect the trailing `distance` arg and
    # the restriction `*_stbox` border flag).
    params: dict[str, list[str]] = field(default_factory=dict)


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
        meth.params[cname] = [
            p.get("canonical", p.get("cType", "")) for p in entry["params"]
        ]
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


# --- faithful wired-in mixin emission -----------------------------------
#
# The Draft `_preview/` above is a shape sketch.  The faithful emitter below
# produces a mixin that is BEHAVIOURALLY identical to the hand-written
# pymeos/main/<t>.py regular families -- same isinstance ladder, same
# argument transforms, same result post-processing, same super()/raise
# fallback -- so the existing pytest suite passes unchanged against it.  It
# is modelled per type family; only families with a FAMILY_MODEL entry are
# wired in (the staged migration is one family per PR).

# Per-family binding: base scalar class, the family's own temporal class,
# the import path of each, and the arg-token -> (isinstance type, call-arg
# expression) map.  ``$o`` is the Python argument.  Tokens absent from a
# family's map are reported (never silently dropped).
FAMILY_MODEL = {
    "cbuffer": {
        "mixin_class": "TCbufferRegularMixin",
        "base_class": "Cbuffer",
        "base_import": "from ...collections.cbuffer import Cbuffer",
        "temporal_class": "TCbuffer",
        "temporal_import": "from ..tcbuffer import TCbuffer",
        # The temporal operand's C-name token.  A faithful temporal-type
        # mixin uses ONLY `<member>_<temporal_token>_<arg>` overloads (the
        # temporal value is the left operand); the reversed `<member>_
        # <base>_<temporal_token>` and base-class forms belong to the base
        # scalar class, not here -- exactly as the hand-written code does.
        "temporal_token": "tcbuffer",
        "tokens": {
            "cbuffer": ("Cbuffer", "$o._inner"),
            "tcbuffer": ("TCbuffer", "$o._inner"),
            "geo": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "geom": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "stbox": ("STBox", "$o._inner"),
        },
        "stbox_lazy": "from ...boxes import STBox",
    },
    "pose": {
        "mixin_class": "TPoseRegularMixin",
        "base_class": "Pose",
        "base_import": "from ...collections.pose import Pose",
        "temporal_class": "TPose",
        "temporal_import": "from ..tpose import TPose",
        "temporal_token": "tpose",
        "tokens": {
            "pose": ("Pose", "$o._inner"),
            "tpose": ("TPose", "$o._inner"),
            "geo": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "geom": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            # tpose distance spells its geometry overload `_tpose_point`
            "point": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "stbox": ("STBox", "$o._inner"),
        },
        "stbox_lazy": "from ...boxes import STBox",
    },
    "npoint": {
        "mixin_class": "TNpointRegularMixin",
        "base_class": "Npoint",
        "base_import": "from ...collections.npoint import Npoint, NpointSet",
        "temporal_class": "TNpoint",
        "temporal_import": "from ..tnpoint import TNpoint",
        "temporal_token": "tnpoint",
        "tokens": {
            "npoint": ("Npoint", "$o._inner"),
            "tnpoint": ("TNpoint", "$o._inner"),
            "npointset": ("NpointSet", "$o._inner"),
            "geo": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "geom": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            # tnpoint distance spells its geometry overload `_tnpoint_point`
            "point": ("shpb.BaseGeometry", "geo_to_gserialized($o, False)"),
            "stbox": ("STBox", "$o._inner"),
        },
        "stbox_lazy": "from ...boxes import STBox",
        # tnpoint.shortest_line takes `precision: int = 15` (tcbuffer/tpose
        # hardcode 10 with no param -> they omit this key, unaffected).
        "shortest_line_precision": 15,
    },
    "rgeo": {
        "mixin_class": "TRgeometryRegularMixin",
        "base_class": "TRgeometry",
        # `tpoint` arg token needs TPoint at runtime (isinstance); no
        # rgeometry base-value wrapper exists (base value is a shapely
        # geometry), so the base import is TPoint.
        "base_import": "from ..tpoint import TPoint",
        "temporal_class": "TRgeometry",
        "temporal_import": "from ..trgeometry import TRgeometry",
        "temporal_token": "trgeo",
        "tokens": {
            # rgeo uses geometry_to_gserialized(g) (single arg), not the
            # geo_to_gserialized(g, False) the other spatial families use.
            "geo": ("shpb.BaseGeometry", "geometry_to_gserialized($o)"),
            "trgeo": ("TRgeometry", "$o._inner"),
            "tpoint": ("TPoint", "$o._inner"),
            "stbox": ("STBox", "$o._inner"),
        },
        "stbox_lazy": "from ...boxes import STBox",
        # at/minus are NOT generated: rgeo restriction is the irregular
        # `trgeo_restrict_<timetype>` + direction-bool pattern (no
        # `trgeometry_at_*`/`_minus_*` in the catalog), so the generator
        # never collects them and they correctly stay hand-written.
    },
}

# Result post-processing, derived verbatim from the hand-written oracle.
_BOOL_GT0 = {"always_equal", "always_not_equal", "ever_equal", "ever_not_equal"}
_BOOL_EQ1 = {
    "is_ever_contains",
    "is_ever_covers",
    "is_ever_disjoint",
    "is_ever_within_distance",
    "ever_intersects",
    "ever_touches",
    "is_always_contains",
    "is_always_covers",
    "is_always_disjoint",
    "is_always_within_distance",
    "always_intersects",
    "always_touches",
}
_SHAPELY = {"shortest_line"}
_RAW = {"nearest_approach_distance"}
# Members whose unmatched-type branch delegates to the generic base impl
# (the rest raise TypeError, mirroring the hand-written code exactly).
_SUPER_FALLBACK = {
    "at",
    "minus",
    "temporal_equal",
    "temporal_not_equal",
    "temporal_less",
    "temporal_less_or_equal",
    "temporal_greater",
    "temporal_greater_or_equal",
}
# Members that take a trailing ``distance`` argument.
_WITHIN_DISTANCE = {
    "is_ever_within_distance",
    "is_always_within_distance",
    "within_distance",
}

_ORDER = [
    "geo",
    "geom",
    "point",
    "tpoint",
    "trgeo",
    "cbuffer",
    "tcbuffer",
    "npoint",
    "tnpoint",
    "npointset",
    "pose",
    "tpose",
    "rgeometry",
    "trgeometry",
    "stbox",
]

# oo_method_name -> the C-name member prefix (reverse of MEMBER_SPEC).
_OO_TO_CPREFIX = {oo: pfx for pfx, (oo, _k) in MEMBER_SPEC.items()}


def _faithful_overloads(oo_name: str, m: Method, ttok: str) -> dict[str, str]:
    """Rebuild the dispatch table for a temporal-type mixin: keep only the
    overloads whose C name is ``<member>_<ttok>_<arg>`` (or, for
    restriction, ``<ttok>_(at|minus)_<arg>``) and key on ``<arg>``.  This
    discards reversed-operand / base-class forms so the generated method
    calls exactly the backing the hand-written method called."""
    out: dict[str, str] = {}
    if oo_name in ("at", "minus"):
        pat = re.compile(rf"^{re.escape(ttok)}_{oo_name}_(.+)$")
    else:
        cpre = _OO_TO_CPREFIX[oo_name]
        pat = re.compile(rf"^{re.escape(cpre)}_{re.escape(ttok)}_(.+)$")
    for cn in m.c_names:
        mm = pat.match(cn)
        if mm:
            out.setdefault(mm.group(1), cn)
    return out


_MIXIN_HEADER = '''\
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# ============================================================================
#  GENERATED by tools/oo_codegen/codegen.py -- DO NOT EDIT.
#  Regenerate:
#    python3 tools/oo_codegen/codegen.py --mixin {family} \\
#        --mixin-out pymeos/main/_generated/{family}_methods.py
# ============================================================================
#
# Wired into pymeos.main.{temporal_class} via {mixin_class}.  Every method
# dispatches by argument type to the EXACT pymeos_cffi backing the
# hand-written method used -- same native call, same transforms, same
# result, never reimplemented: identical by construction.
"""Generated regular OO methods for the {temporal_class} family."""
from __future__ import annotations

from typing import TYPE_CHECKING

import shapely.geometry.base as shpb
from pymeos_cffi import *

from ...temporal import Temporal
{base_import}

if TYPE_CHECKING:
    {temporal_import}


class {mixin_class}:
    """Generated regular families (comparison, spatial relationship,
    distance, restriction) for :class:`{temporal_class}`."""
'''


def _result_return(oo_name: str, model: dict) -> str:
    if oo_name in _BOOL_GT0:
        return "        return result > 0\n"
    if oo_name in _BOOL_EQ1:
        return "        return result == 1\n"
    if oo_name in _RAW:
        return "        return result\n"
    if oo_name in _SHAPELY:
        # Some families' shortest_line takes a `precision` arg (e.g. tnpoint
        # `precision: int = 15`); others hardcode 10 with no param. Driven
        # by the family model so #90/#91 (no key) stay byte-identical.
        if model.get("shortest_line_precision") is not None:
            return (
                "        return gserialized_to_shapely_geometry(" "result, precision)\n"
            )
        return "        return gserialized_to_shapely_geometry(result, 10)\n"
    return "        return Temporal._factory(result)\n"


def emit_faithful_mixin(family: str, methods: dict[str, Method]) -> str:
    """Emit the behaviourally-faithful wired-in mixin for one modelled
    family.  Raises if a regular overload's arg token has no model mapping
    (so a coverage gap is loud, never silent)."""
    model = FAMILY_MODEL[family]
    tokens = model["tokens"]
    ttok = model["temporal_token"]
    out = [
        _MIXIN_HEADER.format(
            family=family,
            mixin_class=model["mixin_class"],
            temporal_class=model["temporal_class"],
            base_import=model["base_import"],
            temporal_import=model["temporal_import"],
        )
    ]

    # Faithful dispatch tables (temporal operand first); reversed/base forms
    # discarded.  Any arg token without a model mapping is loud, not silent.
    faithful = {oo: _faithful_overloads(oo, m, ttok) for oo, m in methods.items()}
    unmodelled = sorted(
        {tok for tbl in faithful.values() for tok in tbl if tok not in tokens}
    )
    if unmodelled:
        raise SystemExit(
            f"[{family}] arg tokens with no FAMILY_MODEL mapping: "
            f"{unmodelled} -- extend FAMILY_MODEL before wiring"
        )

    for oo_name in sorted(methods):
        m = methods[oo_name]
        ov = faithful[oo_name]
        if not ov:
            # No temporal-operand overload (member is base-class only);
            # the hand-written class does not expose it either.
            continue
        has_dist = oo_name in _WITHIN_DISTANCE
        sig = "self, other, distance" if has_dist else "self, other"
        if oo_name in _SHAPELY and model.get("shortest_line_precision") is not None:
            sig = (
                f"self, other, precision: int = " f"{model['shortest_line_precision']}"
            )
        body: list[str] = []
        # Lazy imports mirroring the hand-written idiom (self temporal type
        # and STBox are imported inside the method to avoid import cycles).
        needs_self = any(tokens[t][0] == model["temporal_class"] for t in ov)
        needs_stbox = "stbox" in ov
        if needs_self:
            body.append(f"        {model['temporal_import']}\n")
        if needs_stbox:
            body.append(f"        {model['stbox_lazy']}\n")

        branches = [t for t in _ORDER if t in ov]
        for i, tok in enumerate(branches):
            cfn = ov[tok]
            pytype, argexpr = tokens[tok]
            argexpr = argexpr.replace("$o", "other")
            nparams = len(m.params.get(cfn, []))
            call_args = ["self._inner", argexpr]
            if has_dist:
                call_args.append("distance")
            elif oo_name in ("at", "minus") and tok == "stbox" and nparams == 3:
                call_args.append("True")
            kw = "if" if i == 0 else "elif"
            body.append(
                f"        {kw} isinstance(other, {pytype}):\n"
                f"            result = {cfn}({', '.join(call_args)})\n"
            )
        if oo_name in _SUPER_FALLBACK:
            body.append(
                f"        else:\n" f"            return super().{oo_name}(other)\n"
            )
        else:
            body.append(
                "        else:\n"
                "            raise TypeError(\n"
                '                f"Operation not supported with type "\n'
                '                f"{other.__class__}"\n'
                "            )\n"
            )
        body.append(_result_return(oo_name, model))

        meos_fns = ", ".join(sorted(set(m.c_names)))
        out.append(
            f"\n    def {oo_name}({sig}):\n"
            f'        """Generated regular ``{oo_name}``.\n\n'
            f"        MEOS Functions:\n"
            f"            {meos_fns}\n"
            f'        """\n' + "".join(body)
        )
    return "".join(out)


# --- RFC #94 oo.dispatch consumer (Path B, PyMEOS side) -----------------
#
# Once MEOS-API enriches meta/meos-meta.json with the per-OO-member
# `oo.<family>.<member>.dispatch` blocks (RFC tools/oo_codegen/
# RFC-dispatch-metadata.md §3), this consumer emits the geo/temporal mixins
# from that CANONICAL catalog -- equivalence by construction at the catalog
# level, identical mechanism to the 4 FAMILY_MODEL-derived families.
#
# It is proven correct WITHOUT waiting for that metadata: serialising the 4
# already-A/B-proven families (cbuffer/pose/npoint/rgeo) into the RFC
# schema and feeding them back through this consumer reproduces their
# committed mixins BYTE-IDENTICALLY (the --verify-oo-roundtrip gate). The
# parallel MEOS-API session's geo/temporal blocks then plug into the same
# proven consumer.

# argTransform vocabulary -> PyMEOS idiom on `$o` (RFC §3 closed set).
_PYMEOS_ARGT = {
    "innerPtr": "$o._inner",
    "geoToGserialized": "geo_to_gserialized($o, {geodetic})",
    "geometryToGserialized": "geometry_to_gserialized($o)",
    "stboxToGeo": "stbox_to_geo($o._inner)",
    "scalarCast": "{cast}($o)",  # {cast} resolved per concrete base
    "scalarValue": "$o",
    "textsetMake": "textset_make($o)",
}
# RFC §7 `scalarType` -> the exact isinstance test for a py:"scalar" entry.
_SCALAR_ISINSTANCE = {
    "float": "float",
    "int": "int",
    "bool": "bool",
    "str": "str",
    "int|float": "(int, float)",
}
# Inverse, for serialising FAMILY_MODEL idioms back to the vocabulary so the
# round-trip exercises the real vocab->idiom path.
_ARGT_OF_IDIOM = {
    "$o._inner": ("innerPtr", False),
    "geo_to_gserialized($o, False)": ("geoToGserialized", False),
    "geo_to_gserialized($o, isinstance(self, TGeogPoint))": (
        "geoToGserialized",
        True,
    ),
    "geometry_to_gserialized($o)": ("geometryToGserialized", False),
    "stbox_to_geo($o._inner)": ("stboxToGeo", False),
    "float($o)": ("scalarCast", False),
    "$o": ("scalarValue", False),
}


def _serialize_family_dispatch(family: str, methods: dict) -> dict:
    """Express a FAMILY_MODEL family's resolved dispatch as the RFC #94 §3
    `oo.<family>` schema (abstract argTransform vocabulary).  This is the
    canonical form the MEOS-API catalog will carry; here it is derived from
    the proven path so the consumer can be round-trip-validated."""
    model = FAMILY_MODEL[family]
    tokens, ttok = model["tokens"], model["temporal_token"]
    faithful = {oo: _faithful_overloads(oo, m, ttok) for oo, m in methods.items()}
    oo_blocks: dict = {}
    for oo_name in sorted(methods):
        m, ov = methods[oo_name], faithful[oo_name]
        if not ov:
            continue
        disp = []
        for tok in (t for t in _ORDER if t in ov):
            cfn = ov[tok]
            pytype, argexpr = tokens[tok]
            argt, geo_self = _ARGT_OF_IDIOM[argexpr]
            entry = {"py": pytype, "fn": cfn, "argTransform": argt}
            if geo_self:
                entry["geodeticFromSelf"] = True
            if (
                oo_name in ("at", "minus")
                and tok == "stbox"
                and len(m.params.get(cfn, [])) == 3
            ):
                entry["extraArgs"] = ["True"]
            disp.append(entry)
        block = {
            "dispatch": disp,
            "fallback": "super" if oo_name in _SUPER_FALLBACK else "raise",
            "result": (
                "bool_gt0"
                if oo_name in _BOOL_GT0
                else (
                    "bool_eq1"
                    if oo_name in _BOOL_EQ1
                    else (
                        "scalar"
                        if oo_name in _RAW
                        else "shapely" if oo_name in _SHAPELY else "temporal"
                    )
                )
            ),
            "meosFns": sorted(set(m.c_names)),
        }
        if oo_name in _WITHIN_DISTANCE:
            block["extraParam"] = "distance"
        if oo_name in _SHAPELY and model.get("shortest_line_precision") is not None:
            block["extraParam"] = f"precision: int = {model['shortest_line_precision']}"
        oo_blocks[oo_name] = block
    return oo_blocks


# Real D1 (MEOS-API #10) blocks use ABSTRACT py names; map them to the
# PyMEOS isinstance idiom.  Identity for any name not listed -> the 4-family
# round-trip (concrete py names from FAMILY_MODEL) stays byte-identical.
_DISPATCH_PY = {
    "Point": "shp.Point",
    "BaseGeometry": "shpb.BaseGeometry",
    "GeoSet": "GeoSet",
    "STBox": "STBox",
    "TPoint": "TPoint",
    "IntSet": "IntSet",
    "IntSpan": "IntSpan",
    "IntSpanSet": "IntSpanSet",
    "FloatSet": "FloatSet",
    "FloatSpan": "FloatSpan",
    "FloatSpanSet": "FloatSpanSet",
}
_JSON_BOOL = {"true": "True", "false": "False"}
# Header/import binding for families that exist only via objectModel.dispatch
# (no FAMILY_MODEL).  Geo's mixin folds into TPoint (TGeomPoint/TGeogPoint
# disambiguated at runtime by geodeticFromSelf).
_DISPATCH_BINDING = {
    "geo": {
        "mixin_class": "TPointDispatchMixin",
        "temporal_class": "TPoint",
        "base_import": (
            "import shapely.geometry as shp\n"
            "import shapely.geometry.base as shpb\n"
            "from ...collections import GeoSet"
        ),
        "temporal_import": "from ..tpoint import TPoint, TGeogPoint",
        "stbox_lazy": "from ...boxes import STBox",
    },
}
# Temporal scalar concrete types (per-concrete contract). `cast` resolves
# scalarCast (`float()`/`int()` per the verbatim oracle; None where the
# oracle passes the scalar uncast).
for _tt, _cls, _base, _cast, _coll in (
    ("tfloat", "TFloat", "float", "float", "IntSet, IntSpan, IntSpanSet"),
    ("tint", "TInt", "int", "int", "FloatSet, FloatSpan, FloatSpanSet"),
    ("tbool", "TBool", "bool", None, ""),
    ("ttext", "TText", "str", None, ""),
):
    # Self temporal type is imported ONLY under TYPE_CHECKING (header) and
    # lazily inside each method (emit_from_oo_dispatch), mirroring the proven
    # FAMILY_MODEL template; a top-level self-import here would create an
    # import cycle once the mixin is wired into the class module.
    _imp = f"from ...collections import {_coll}" if _coll else ""
    _DISPATCH_BINDING[_tt] = {
        "mixin_class": f"{_cls}DispatchMixin",
        "temporal_class": _cls,
        "base_import": _imp,
        "temporal_import": f"from ..{_tt} import {_cls}",
        "stbox_lazy": "",  # temporal has no STBox branch
        "cast": _cast,
    }


def emit_from_oo_dispatch(family: str, oo_blocks: dict) -> str:
    """THE consumer: emit a faithful mixin from RFC #94 §3 / D1
    `objectModel.dispatch.<family>` blocks (the canonical MEOS-API catalog
    form).  Byte-identical to emit_faithful_mixin for the 4 proven families
    (round-trip gate); also consumes the real abstract-`py` D1 blocks."""
    model = FAMILY_MODEL.get(family) or _DISPATCH_BINDING[family]
    out = [
        _MIXIN_HEADER.format(
            family=family,
            mixin_class=model["mixin_class"],
            temporal_class=model["temporal_class"],
            base_import=model["base_import"],
            temporal_import=model["temporal_import"],
        )
    ]
    selfcls = model["temporal_class"]
    for oo_name in sorted(oo_blocks):
        blk = oo_blocks[oo_name]
        disp = blk["dispatch"]
        ep = blk.get("extraParam")
        if ep == "distance":
            sig = "self, other, distance"
        elif ep:
            sig = f"self, other, {ep}"
        else:
            sig = "self, other"
        body: list[str] = []
        if any(e["py"] in ("self", selfcls) for e in disp) or any(
            e.get("geodeticFromSelf") for e in disp
        ):
            body.append(f"        {model['temporal_import']}\n")
        if any(e["py"] == "STBox" for e in disp):
            body.append(f"        {model['stbox_lazy']}\n")
        cast = model.get("cast") or "float"
        for i, e in enumerate(disp):
            kw = "if" if i == 0 else "elif"
            py = e["py"]
            if py == "scalar":
                cond = f"isinstance(other, {_SCALAR_ISINSTANCE[e['scalarType']]})"
            elif py == "self":
                cond = f"isinstance(other, {selfcls})"
            elif py == "list[str]":
                cond = "isinstance(other, list) and isinstance(other[0], str)"
            else:
                cond = f"isinstance(other, {_DISPATCH_PY.get(py, py)})"
            if e.get("via") == "super":  # type-coercion entry, no fn
                body.append(
                    f"        {kw} {cond}:\n"
                    f"            return super().{oo_name}"
                    f"(other.{e['coerce']}())\n"
                )
                continue
            idiom = _PYMEOS_ARGT[e.get("argTransform", "innerPtr")]
            geod = (
                "isinstance(self, TGeogPoint)" if e.get("geodeticFromSelf") else "False"
            )
            argexpr = (
                idiom.replace("{geodetic}", geod)
                .replace("{cast}", cast)
                .replace("$o", "other")
            )
            call_args = ["self._inner", argexpr]
            if ep == "distance":
                call_args.append("distance")
            for x in e.get("extraArgs", []):
                call_args.append(_JSON_BOOL.get(x, x))
            body.append(
                f"        {kw} {cond}:\n"
                f"            result = {e['fn']}({', '.join(call_args)})\n"
            )
        if blk["fallback"] == "super":
            body.append(
                f"        else:\n" f"            return super().{oo_name}(other)\n"
            )
        else:
            body.append(
                "        else:\n"
                "            raise TypeError(\n"
                '                f"Operation not supported with type "\n'
                '                f"{other.__class__}"\n'
                "            )\n"
            )
        rk = blk["result"]
        body.append(
            "        return result > 0\n"
            if rk == "bool_gt0"
            else (
                "        return result == 1\n"
                if rk == "bool_eq1"
                else (
                    "        return result\n"
                    if rk == "scalar"
                    else (
                        "        return gserialized_to_shapely_geometry("
                        "result, precision)\n"
                        if rk == "shapely" and ep
                        else (
                            "        return gserialized_to_shapely_geometry("
                            "result, 10)\n"
                            if rk == "shapely"
                            else "        return Temporal._factory(result)\n"
                        )
                    )
                )
            )
        )
        # Real D1 blocks carry only {dispatch,fallback,result}; derive the
        # docstring fn list from the dispatch when meosFns is absent (the
        # round-trip serialisation supplies meosFns -> byte-identical).
        meos_fns = blk.get("meosFns") or sorted({e["fn"] for e in disp if "fn" in e})
        out.append(
            f"\n    def {oo_name}({sig}):\n"
            f'        """Generated regular ``{oo_name}``.\n\n'
            f"        MEOS Functions:\n"
            f"            {', '.join(meos_fns)}\n"
            f'        """\n' + "".join(body)
        )
    return "".join(out)


# --- RFC #94 §7 keystone: A/B proof for the non-derivable families ------
#
# geo and temporal cannot be reproduced from the signature catalog via a
# FAMILY_MODEL (RFC #94 §1), so --verify-oo-roundtrip cannot guard them.
# Instead they are driven by the verbatim objectModel.dispatch metadata
# (MEOS-API #10) and proven equivalent to the hand-written oracle by
# *dispatch-skeleton* equality: each editorial method reduces to an
# ordered list of (isinstance type-set, normalized action) branches plus
# a terminal result wrap; the generated method and the oracle method must
# reduce to the identical skeleton. Variable spellings (``value`` vs
# ``other``), temp bindings (``gs = f(...); g(gs)`` vs inlined ``g(f(...))``)
# and ``isinstance(x,A) or isinstance(x,B)`` vs ``isinstance(x,(A,B))`` are
# normalized away -- only behaviour is compared.


def _ab_norm_expr(node: ast.AST, param: str) -> str:
    class _R(ast.NodeTransformer):
        def visit_Name(self, n):  # noqa: N802
            new = "$o" if n.id == param else n.id
            return ast.copy_location(ast.Name(id=new, ctx=n.ctx), n)

    return ast.unparse(_R().visit(ast.fix_missing_locations(node)))


def _ab_isinstance(test: ast.AST, param: str):
    """(frozenset of type-leaf names, sorted extra-guard tuple)."""
    types, extra = set(), []

    def walk(n):
        if isinstance(n, ast.BoolOp):  # flatten `or` / `and` chains
            for v in n.values:
                walk(v)
            return
        if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "isinstance":
            tgt = n.args[0]
            if isinstance(tgt, ast.Subscript):  # e.g. isinstance(other[0], str)
                extra.append("idx0:" + _ab_norm_expr(n.args[1], param))
                return
            a = n.args[1]
            if isinstance(a, ast.Tuple):
                for el in a.elts:
                    types.add(ast.unparse(el))
            else:
                types.add(ast.unparse(a))

    walk(test)
    return frozenset(types), tuple(sorted(extra))


def _ab_inline_temps(stmts):
    out, subst = [], {}
    for s in stmts:
        if (
            isinstance(s, ast.Assign)
            and len(s.targets) == 1
            and isinstance(s.targets[0], ast.Name)
            and s.targets[0].id != "result"
        ):
            subst[s.targets[0].id] = s.value
            continue

        class _R(ast.NodeTransformer):
            def visit_Name(self, n):  # noqa: N802
                return subst.get(n.id, n) if n.id in subst else n

        out.append(_R().visit(s))
    return out


def _ab_action(stmts, param):
    stmts = _ab_inline_temps(stmts)
    for st in stmts:
        if (
            isinstance(st, ast.Assign)
            and isinstance(st.targets[0], ast.Name)
            and st.targets[0].id == "result"
            and isinstance(st.value, ast.Call)
        ):
            c = st.value
            return ("call", c.func.id, tuple(_ab_norm_expr(a, param) for a in c.args))
    s = stmts[-1] if stmts else None
    if isinstance(s, ast.Return):
        v = s.value
        if v is None:
            return ("return_none",)
        if (
            isinstance(v, ast.Call)
            and isinstance(v.func, ast.Attribute)
            and isinstance(v.func.value, ast.Call)
            and getattr(v.func.value.func, "id", None) == "super"
        ):
            return (
                "super",
                v.func.attr,
                _ab_norm_expr(v.args[0], param) if v.args else None,
            )
        if isinstance(v, ast.Compare):  # return f(...) > 0
            return (
                "call_cmp",
                v.left.func.id,
                tuple(_ab_norm_expr(a, param) for a in v.left.args),
                ast.unparse(v.ops[0]),
                ast.unparse(v.comparators[0]),
            )
        if isinstance(v, ast.Call):  # return f(...)  (bare scalar)
            return (
                "call_ret",
                v.func.id,
                tuple(_ab_norm_expr(a, param) for a in v.args),
            )
    if isinstance(s, ast.Raise):
        return (
            "raise",
            s.exc.func.id if isinstance(s.exc, ast.Call) else ast.unparse(s.exc),
        )
    return ("?", ast.dump(s) if s else None)


def _ab_skeleton(fn: ast.FunctionDef):
    param = fn.args.args[1].arg if len(fn.args.args) > 1 else "other"
    body = [
        s
        for s in fn.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
        and not isinstance(s, (ast.Import, ast.ImportFrom))
    ]
    branches, terminal = [], None
    node = body[0] if body else None
    while isinstance(node, ast.If):
        branches.append(
            (*_ab_isinstance(node.test, param), _ab_action(node.body, param))
        )
        if node.orelse and len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node = node.orelse[0]
        else:
            if node.orelse:
                branches.append(((), (), _ab_action(node.orelse, param)))
            break
    tail = [s for s in body if not isinstance(s, ast.If)]
    if tail and isinstance(tail[-1], ast.Return):
        v = tail[-1].value
        if isinstance(v, ast.Call):
            terminal = ("wrap", ast.unparse(v.func))
        elif isinstance(v, ast.Compare):
            terminal = ("cmp", ast.unparse(v.ops[0]), ast.unparse(v.comparators[0]))
        elif isinstance(v, ast.Name):
            terminal = ("bare",)
    norm = []
    for ts, ex, act in branches:
        if act[0] == "call_cmp":
            norm.append((ts, ex, ("call", act[1], act[2])))
            terminal = terminal or ("cmp", act[3], act[4])
        elif act[0] == "call_ret":
            norm.append((ts, ex, ("call", act[1], act[2])))
            terminal = terminal or ("bare",)
        else:
            norm.append((ts, ex, act))
    return tuple(norm), terminal


# editorial members per family (the methods carrying non-derivable
# dispatch); geo's family-key for --mixin-from-dispatch is "geo", its
# oracle class is _Oracle_tpoint.
_AB_FAMILIES = {
    "tfloat": "tfloat",
    "tint": "tint",
    "tbool": "tbool",
    "ttext": "ttext",
    "geo": "tpoint",
}


def verify_oo_dispatch_extended():
    """Prove the metadata-driven consumer reproduces the verbatim oracle's
    dispatch behaviour for geo + the 4 temporal concretes. Returns
    ``(ok, report_lines, checked, mismatches)``."""
    idl = json.loads(DISPATCH_EXT_FIXTURE.read_text())
    disp = idl["objectModel"]["dispatch"]
    oracle_mod = ast.parse(ORACLE_EXT.read_text())
    oracle = {}
    for cls in [n for n in oracle_mod.body if isinstance(n, ast.ClassDef)]:
        oracle[cls.name] = {
            f.name: f for f in cls.body if isinstance(f, ast.FunctionDef)
        }
    lines, checked, miss = [], 0, 0
    for fam, ocls in _AB_FAMILIES.items():
        oo = disp[fam] if fam == "geo" else disp["temporal"][fam]
        gen = ast.parse(emit_from_oo_dispatch(fam, oo))
        gmeth = {f.name: f for f in ast.walk(gen) if isinstance(f, ast.FunctionDef)}
        ometh = oracle[f"_Oracle_{ocls}"]
        for m in sorted(x for x in gmeth if x in ometh):
            checked += 1
            same = _ab_skeleton(ometh[m]) == _ab_skeleton(gmeth[m])
            miss += not same
            lines.append(
                f"  {fam:<6}.{m:<24} " f"{'EQUIVALENT ✓' if same else 'DIVERGES ✗'}"
            )
            if not same:
                lines.append(f"      oracle: {_ab_skeleton(ometh[m])}")
                lines.append(f"      gen   : {_ab_skeleton(gmeth[m])}")
    return miss == 0, lines, checked, miss


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
    ap.add_argument(
        "--mixin",
        metavar="FAMILY",
        help="emit the behaviourally-faithful wired-in mixin for one "
        "modelled family instead of the Draft preview",
    )
    ap.add_argument(
        "--mixin-out",
        metavar="PATH",
        help="destination for --mixin (default: stdout)",
    )
    ap.add_argument(
        "--verify-oo-roundtrip",
        action="store_true",
        help="prove the RFC #94 oo.dispatch consumer correct: serialise "
        "each proven FAMILY_MODEL family to the RFC schema and assert the "
        "consumer reproduces emit_faithful_mixin BYTE-IDENTICALLY",
    )
    ap.add_argument(
        "--mixin-from-dispatch",
        metavar="FAMILY",
        help="emit a mixin from an idl carrying oo.<FAMILY> dispatch "
        "(the canonical MEOS-API path, RFC #94 §5)",
    )
    ap.add_argument(
        "--verify-oo-dispatch-extended",
        action="store_true",
        help="prove the RFC #94 §7 keystone: the consumer fed the verbatim "
        "objectModel.dispatch metadata (MEOS-API #10) reproduces the "
        "hand-written oracle's dispatch behaviour for geo + the 4 temporal "
        "concretes (the families not derivable via --verify-oo-roundtrip)",
    )
    args = ap.parse_args()

    if args.verify_oo_dispatch_extended:
        ok, report, checked, miss = verify_oo_dispatch_extended()
        print("\n".join(report))
        print(
            f"VERIFY-EXTENDED: {'PASS' if ok else 'FAIL'} - {checked} "
            f"editorial methods across geo + tfloat/tint/tbool/ttext, "
            f"{miss} divergence(s); consumer == verbatim oracle by "
            "dispatch-skeleton equality (RFC #94 §7 keystone, codegen 6/6)"
        )
        return 0 if ok else 1

    idl = json.loads(Path(args.idl).read_text())

    if args.mixin_from_dispatch:
        fam = args.mixin_from_dispatch
        # Real schema home is idl.objectModel.dispatch.<family> (MEOS-API
        # #10 feat/object-model, parser/object_model.py); RFC #94 §3's
        # top-level `oo` was illustrative. Fall back to `oo` for older
        # fixtures. (Handled before collect(): a dispatch-only catalog
        # need not carry `functions`.)
        _disp = idl.get("objectModel", {}).get("dispatch", {})
        # Temporal is per-concrete: dispatch.temporal.{tfloat,tint,tbool,ttext}
        if fam in ("tfloat", "tint", "tbool", "ttext"):
            oo = _disp.get("temporal", {}).get(fam)
        else:
            oo = _disp.get(fam) or idl.get("oo", {}).get(fam)
        if not oo:
            raise SystemExit(
                f"--mixin-from-dispatch {fam!r}: idl carries no "
                f"objectModel.dispatch.{fam} (pending the MEOS-API "
                f"enrichment, RFC #94 / MEOS-API #10)"
            )
        src = emit_from_oo_dispatch(fam, oo)
        if args.mixin_out:
            Path(args.mixin_out).write_text(src)
            print(f"[oo-codegen] wrote {fam} mixin from catalog oo.dispatch")
        else:
            print(src)
        return 0

    fams, st = collect(idl)

    if args.verify_oo_roundtrip:
        ok = True
        for fam in sorted(FAMILY_MODEL):
            direct = emit_faithful_mixin(fam, fams[fam])
            viacat = emit_from_oo_dispatch(
                fam, _serialize_family_dispatch(fam, fams[fam])
            )
            same = direct == viacat
            ok &= same
            print(
                f"  {fam:<8} oo.dispatch round-trip "
                f"{'BYTE-IDENTICAL ✓' if same else 'DIFERS ✗'} "
                f"({len(direct)}b)"
            )
        print(
            "VERIFY: "
            + (
                "PASS - consumer == proven path for all "
                f"{len(FAMILY_MODEL)} families; geo/temporal plug into the "
                "same consumer via MEOS-API oo.dispatch"
                if ok
                else "FAIL - consumer diverges from the proven path"
            )
        )
        return 0 if ok else 1

    if args.mixin:
        if args.mixin not in FAMILY_MODEL:
            raise SystemExit(
                f"--mixin {args.mixin!r}: no FAMILY_MODEL (modelled: "
                f"{sorted(FAMILY_MODEL)})"
            )
        src = emit_faithful_mixin(args.mixin, fams[args.mixin])
        if args.mixin_out:
            Path(args.mixin_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.mixin_out).write_text(src)
            print(
                f"[oo-codegen] wrote faithful mixin "
                f"{FAMILY_MODEL[args.mixin]['mixin_class']} -> "
                f"{args.mixin_out} ({len(fams[args.mixin])} methods)"
            )
        else:
            print(src)
        return 0

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
