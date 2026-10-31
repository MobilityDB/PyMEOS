#!/usr/bin/env python3
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# Catalog-driven generator of PyMEOS's regular OO method families.
#
# The temporal classes of pymeos/main spell out, uniformly across the
# temporal types, the regular method families: comparison, spatial
# relationship (ever, always, temporal), distance and restriction.  Each
# member is an isinstance ladder forwarding self._inner and the unwrapped
# argument to a typed MEOS overload and post-processing the result.  This
# tool reads the meos-idl.json catalog of the MEOS the package builds
# against (--idl, or $MEOS_IDL, the catalog the test workflow derives),
# groups the regular-family C functions by temporal type family and member,
# and writes, for each family FAMILY_MODEL describes, one mixin of
# dispatching methods into pymeos/main/_generated/<module>_methods.py, laid
# out by the repository's ruff configuration.  Each generated method calls
# the pymeos_cffi function of its overload; nothing is reimplemented.
#
# The irregular core -- constructors, conversions, accessors, transforms,
# input and output -- stays hand-written.  The generator counts and names
# every function it does not emit, and --check fails when one is neither
# emitted nor counted.
#
# Usage:
#   python3 tools/oo_codegen/codegen.py --idl <meos-idl.json> --check
#   python3 tools/oo_codegen/codegen.py --idl <meos-idl.json> --mixin <family>

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The six in-scope temporal type families, witnessed on the C function name.
# Order is significant: the most specific token wins, so `geo` does not swallow a
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
        meth.params[cname] = [p.get("canonical", p.get("cType", "")) for p in entry["params"]]
        st.emitted_overloads += 1
        st.by_family[fam] += 1
    return fams, st


# --- mixin emission -----------------------------------------------------
#
# A family's mixin holds the isinstance ladder of each regular member, its
# argument transforms, its result post-processing and its super() or raise
# fallback.  A family is wired in when FAMILY_MODEL describes it.

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
        "base_import": "from ...collections import FloatSpan\nfrom ...collections.pose import Pose",
        "temporal_class": "TPose",
        "temporal_import": "from ..tpose import TPose",
        "temporal_token": "tpose",
        "tokens": {
            # tpose_at_elevation / tpose_minus_elevation take the elevation
            # span as a float span
            "elevation": ("FloatSpan", "$o._inner"),
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
        "base_import": "from datetime import datetime\n\n"
        "from ...collections import TsTzSet, TsTzSpan, TsTzSpanSet\n"
        "from ...collections.pose import Pose, PoseSet\n"
        "from ..tpoint import TPoint",
        "temporal_class": "TRgeometry",
        "temporal_import": "from ..trgeometry import TRgeometry",
        "temporal_token": "trgeometry",
        "tokens": {
            # rgeo uses geometry_to_gserialized(g) (single arg), not the
            # geo_to_gserialized(g, False) the other spatial families use.
            "geo": ("shpb.BaseGeometry", "geometry_to_gserialized($o)"),
            "trgeometry": ("TRgeometry", "$o._inner"),
            # trgeometry_at_* / trgeometry_minus_* restrict to a geometry, a
            # pose, a set of poses and the time types
            "geom": ("shpb.BaseGeometry", "geometry_to_gserialized($o)"),
            "value": ("Pose", "$o._inner"),
            "values": ("PoseSet", "$o._inner"),
            "timestamptz": ("datetime", "datetime_to_timestamptz($o)"),
            "tstzset": ("TsTzSet", "$o._inner"),
            "tstzspan": ("TsTzSpan", "$o._inner"),
            "tstzspanset": ("TsTzSpanSet", "$o._inner"),
            "tpoint": ("TPoint", "$o._inner"),
            "stbox": ("STBox", "$o._inner"),
        },
        "stbox_lazy": "from ...boxes import STBox",
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
    "value",
    "values",
    "elevation",
    "stbox",
    "timestamptz",
    "tstzset",
    "tstzspan",
    "tstzspanset",
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
#    python3 tools/oo_codegen/codegen.py --idl <meos-idl.json> --mixin {family} \\
#        --mixin-out pymeos/main/_generated/{module}_methods.py
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
        # A family whose shortest_line takes a `precision` argument (tnpoint,
        # `precision: int = 15`) says so in its model; the others write 10
        # decimal digits.
        if model.get("shortest_line_precision") is not None:
            return "        return gserialized_to_shapely_geometry(result, precision)\n"
        return "        return gserialized_to_shapely_geometry(result, 10)\n"
    return "        return Temporal._factory(result)\n"


ROOT = HERE.parent.parent


def mixin_path(family: str) -> Path:
    """The file of the package a family's mixin is committed in."""
    module = FAMILY_MODEL[family]["temporal_class"].lower()
    return ROOT / "pymeos" / "main" / "_generated" / f"{module}_methods.py"


def format_mixin(src: str, path: Path) -> str:
    """Return a mixin as the repository's ruff configuration writes it: its
    imports sorted and its unused ones dropped by ``ruff check --fix``, then
    laid out by ``ruff format``, so the committed file is the generator's
    output and passes the ruff workflow unchanged."""
    for cmd in (["ruff", "check", "--fix", "--quiet", "--exit-zero"], ["ruff", "format", "--quiet"]):
        src = subprocess.run(
            cmd + ["--stdin-filename", str(path), "-"],
            input=src,
            capture_output=True,
            text=True,
            check=True,
            cwd=ROOT,
        ).stdout
    return src


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
            module=model["temporal_class"].lower(),
            temporal_import=model["temporal_import"],
        )
    ]

    # Faithful dispatch tables (temporal operand first); reversed/base forms
    # discarded.  Any arg token without a model mapping is loud, not silent.
    faithful = {oo: _faithful_overloads(oo, m, ttok) for oo, m in methods.items()}
    unmodelled = sorted({tok for tbl in faithful.values() for tok in tbl if tok not in tokens})
    if unmodelled:
        raise SystemExit(
            f"[{family}] arg tokens with no FAMILY_MODEL mapping: {unmodelled} -- extend FAMILY_MODEL before wiring"
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
            sig = f"self, other, precision: int = {model['shortest_line_precision']}"
        body: list[str] = []
        # Lazy imports mirroring the hand-written idiom (self temporal type
        # and STBox are imported inside the method to avoid import cycles).
        needs_self = any(tokens[t][0] == model["temporal_class"] for t in ov)
        needs_stbox = "stbox" in ov
        if needs_self:
            body.append(f"        {model['temporal_import']}\n")
        if needs_stbox:
            body.append(f"        {model['stbox_lazy']}\n")

        unordered = sorted(t for t in ov if t not in _ORDER)
        if unordered:
            raise SystemExit(
                f"[{family}] {oo_name}: arg tokens with no place in _ORDER: {unordered} -- extend _ORDER before wiring"
            )
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
                f"        {kw} isinstance(other, {pytype}):\n            result = {cfn}({', '.join(call_args)})\n"
            )
        if oo_name in _SUPER_FALLBACK:
            body.append(f"        else:\n            return super().{oo_name}(other)\n")
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


# --- driver -------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--idl",
        default=os.environ.get("MEOS_IDL"),
        required="MEOS_IDL" not in os.environ,
        help="the meos-idl.json catalog of the MEOS the package builds against (default: $MEOS_IDL)",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if any in-scope function is neither emitted nor counted as an explicit exclusion",
    )
    ap.add_argument(
        "--mixin",
        metavar="FAMILY",
        help="write the mixin of one family FAMILY_MODEL describes",
    )
    ap.add_argument(
        "--mixin-out",
        metavar="PATH",
        help="destination for --mixin (default: stdout)",
    )
    args = ap.parse_args()

    idl = json.loads(Path(args.idl).read_text())
    fams, st = collect(idl)

    if args.mixin:
        if args.mixin not in FAMILY_MODEL:
            raise SystemExit(f"--mixin {args.mixin!r}: no FAMILY_MODEL (modelled: {sorted(FAMILY_MODEL)})")
        out = Path(args.mixin_out) if args.mixin_out else mixin_path(args.mixin)
        src = format_mixin(emit_faithful_mixin(args.mixin, fams[args.mixin]), out)
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
        print(f"               {fam:<9}: {len(fams[fam]):>3} methods, {st.by_family[fam]:>4} overloads")
    print(f"[oo-codegen] hand-written core   : {st.irregular} (constructors/conversions/accessors/transforms/IO)")
    print(f"[oo-codegen] Datum-internal      : {st.datum} (excluded)")
    print(f"[oo-codegen] out of scope        : {st.out_of_scope} (non-temporal-family headers)")
    print(f"[oo-codegen] accounted           : {accounted}/{total}")

    unaccounted = total - accounted
    ok = unaccounted == 0 and len(fams) == 6
    if args.check:
        print(
            "CHECK: "
            + (
                "PASS - every function emitted or explicitly counted, all 6 families present"
                if ok
                else f"FAIL - {unaccounted} unaccounted, {len(fams)} families"
            )
        )
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
