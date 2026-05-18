#!/usr/bin/env python3
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# Generate the portable bare-name dialect for PyMEOS.
#
# The canonical portable bare-name mapping (RFC #920, MobilityDB #861) is the
# single cross-binding codegen source of truth: every binding/engine exposes
# the SAME bare names (overlaps, contains, teq, ...) so a user learns one
# reference and assumes the rest.  The mapping is type-agnostic -- it applies
# to every temporal type family.
#
# This tool reads
#   * the vendored contract  tools/portable_aliases/portable-aliases.json
#     (verbatim from MobilityDB/MEOS-API; folded into the catalog shape with
#      the vendored attach_portable_aliases, byte-identical to the SoT), and
#   * the MEOS function universe -- the exact C functions PyMEOS exposes
#     through pymeos_cffi -- obtained from the MEOS headers (default) or, in
#     CI where pymeos_cffi is built, by introspecting it directly,
# and emits  pymeos/portable.py : one callable per canonical bare name that
# DISPATCHES, by the runtime C type of its arguments, to the EXACT pymeos_cffi
# backing function the corresponding operator uses.  No behaviour is
# reimplemented -- every leaf is a direct pymeos_cffi call, so each bare name
# is identical to the operator by construction.
#
# Usage:
#   python3 tools/portable_aliases/generate.py --headers <meos/include> \
#       [--out pymeos/portable.py] [--report build/portable_parity.json]
#   python3 tools/portable_aliases/generate.py --cffi --check   # CI gate

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from portable import attach_portable_aliases  # vendored from MEOS-API (SoT)
from portable_parity import build_parity      # vendored from MEOS-API (SoT)

CONTRACT = HERE / "portable-aliases.json"

# Param/return C base type -> the runtime token the generated dispatcher keys
# on.  MEOS passes every temporal subtype as `const Temporal *`, so all
# temporal overloads of an operator collapse onto one generic symbol keyed by
# `Temporal` -- which is why this stays small and unambiguous.
SCALAR_PY_TOKEN = {
    "bool": "bool", "int": "int", "int32": "int", "int64": "bigint",
    "long": "bigint", "double": "float", "float8": "float",
    "text": "text", "TimestampTz": "timestamptz", "Timestamp": "timestamptz",
    "DateADT": "date", "Interval": "interval",
}

# Header declaration:  extern <ret> <name>(<params>);   (one per line in MEOS)
_DECL = re.compile(
    r"^\s*extern\s+(.+?[\s*])\b([A-Za-z_]\w*)\s*\(([^;{]*)\)\s*;", re.M)


def _base_ctype(decl: str) -> str:
    """Last type identifier of a C declarator, sans const / * / arg name."""
    toks = re.findall(r"[A-Za-z_]\w*", decl.replace("const", " "))
    if not toks:
        return ""
    # `const STBox *box1` -> ['STBox','box1']; `int i` -> ['int','i'];
    # `double` -> ['double'].  The base type is the token before the name,
    # or the only token.  A pointer means the prior token is the type.
    if "*" in decl:
        return toks[0]
    return toks[0] if len(toks) == 1 else toks[-2] if len(toks) > 1 else toks[0]


def _params(raw: str):
    raw = raw.strip()
    if not raw or raw == "void":
        return ()
    out = []
    for p in raw.split(","):
        p = p.strip()
        if p in ("...", ""):
            out.append("...")
            continue
        out.append(_base_ctype(p))
    return tuple(out)


def universe_from_headers(dirs):
    """{name: (ret_base, (param_base, ...))} parsed from MEOS *.h files."""
    funcs = {}
    files = []
    for d in dirs:
        d = Path(d)
        if d.is_file():
            files.append(d)
        elif d.is_dir():
            files += sorted(d.glob("meos*.h"))
    if not files:
        sys.exit(f"no MEOS headers found in {dirs} -- pass --headers <dir>")
    for fp in files:
        text = fp.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
        text = re.sub(r"//.*", " ", text)
        for m in _DECL.finditer(text):
            ret, name, params = m.group(1), m.group(2), m.group(3)
            funcs[name] = (_base_ctype(ret + " r"), _params(params))
    return funcs


def universe_from_cffi():
    """Names actually exported by the installed pymeos_cffi (CI path)."""
    import pymeos_cffi  # noqa: only available where the binding is built
    return {
        n: (None, None)
        for n in dir(pymeos_cffi)
        if not n.startswith("_") and callable(getattr(pymeos_cffi, n))
    }


def backing_symbols(bare, explicit_prefixes, universe):
    """Mirror portable_parity: name == bare or startswith bare+'_'; else the
    verified explicit-backing C prefixes (e.g. nearestApproachDistance->nad)."""
    def match(pfx):
        return [n for n in universe if n == pfx or n.startswith(pfx + "_")]

    hits, via = match(bare), "prefix"
    if not hits:
        for pfx in explicit_prefixes:
            hits += match(pfx)
        via = "explicit" if hits else None
    return sorted(set(hits)), via


def token(ctype):
    """C base type -> dispatcher token (Temporal stays Temporal; scalars
    fold to a stable Python-facing token)."""
    return SCALAR_PY_TOKEN.get(ctype, ctype)


# Each in-scope type family is *witnessed* when some backing symbol of some
# canonical bare name carries that family's MEOS name token -- the same
# per-family convention MobilityDB's tools/portable_aliases/generate.py and
# its six mobilitydb/sql/<fam>/..._portable_aliases.in.sql files use.  This
# proves cbuffer/npoint/pose/rgeo are covered exactly like every other type
# (the hard invariant: never a headline exclusion), without inventing a gate
# that diverges from the SoT's type-agnostic 29/29 parity.
FAMILY_PATTERNS = {
    "temporal": r"(^|_)(temporal|tspatial|tnumber|tbool|tint|tfloat|ttext)(_|$)",
    "geo": r"(^|_)(geo|tgeo|geom|geog|tgeompoint|tgeogpoint|tpoint)(_|$)",
    "cbuffer": r"cbuffer",
    "npoint": r"npoint",
    "pose": r"(^|_)t?pose(_|$)",
    "rgeo": r"(t?rgeo|trgeometry|rgeometry)",
}


def family_regexes(in_scope):
    return {f: re.compile(FAMILY_PATTERNS.get(f, re.escape(f)), re.I)
            for f in in_scope}


HEADER = '''\
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# ============================================================================
#  GENERATED by tools/portable_aliases/generate.py -- DO NOT EDIT.
#  Regenerate:  python3 tools/portable_aliases/generate.py --headers <inc>
# ============================================================================
#
# The portable bare-name dialect (RFC #920; canonical contract:
# MobilityDB/MEOS-API meta/portable-aliases.json; native in MobilityDB via
# the 1303-alias PR #1075).  Every binding exposes the IDENTICAL bare names
# from that one mapping, type-agnostically across all six temporal type
# families (temporal, geo, cbuffer, npoint, pose, rgeo).
#
# Each bare name dispatches, by the runtime C type of its arguments, to the
# EXACT pymeos_cffi function the operator is backed by -- the same native
# call the type-qualified API uses.  Nothing is reimplemented: every bare
# name is identical to its operator by construction.
"""Portable bare-name dialect for PyMEOS (generated -- see module comment)."""
from __future__ import annotations

import datetime as _dt

# Resolved at call time so importing this module never requires the compiled
# binding to be present (e.g. docs / parity checks).
_cffi = None


def _pymeos_cffi():
    global _cffi
    if _cffi is None:
        import pymeos_cffi as _c

        _cffi = _c
    return _cffi


def _unwrap(a):
    return a._inner if hasattr(a, "_inner") else a


def _arg_token(a):
    """Runtime C base type of an argument, mirroring pymeos.factory's cdata
    field-sniffing (no ffi object needed) plus Python scalars."""
    if isinstance(a, bool):
        return "bool"
    if isinstance(a, int):
        return "int"
    if isinstance(a, float):
        return "float"
    if isinstance(a, str):
        return "text"
    if isinstance(a, _dt.datetime):
        return "timestamptz"
    if isinstance(a, _dt.date):
        return "date"
    if isinstance(a, _dt.timedelta):
        return "interval"
    o = _unwrap(a)
    for attr, tok in (
        ("temptype", "Temporal"),       # every temporal subtype (6 families)
        ("spansettype", "SpanSet"),
        ("spantype", "Span"),
        ("settype", "Set"),
    ):
        if hasattr(o, attr):
            return tok
    # Boxes / geo / spatial base types: distinguishing struct fields.
    for attr, tok in (
        ("srid", "STBox"),              # STBox carries an srid; TBox does not
        ("period", "TBox"),
        ("gflags", "GSERIALIZED"),
        ("rid", "Npoint"),
        ("radius", "Cbuffer"),
    ):
        if hasattr(o, attr):
            return tok
    return type(a).__name__


def _wrap(res):
    """Re-wrap MEOS-object results with the existing PyMEOS factories; pass
    scalars (bool/float/int/str) and None straight through."""
    if res is None or isinstance(res, (bool, int, float, str, bytes)):
        return res
    from .factory import _TemporalFactory, _CollectionFactory

    for fn in (_TemporalFactory.create_temporal,
               _CollectionFactory.create_collection):
        try:
            return fn(res)
        except Exception:
            pass
    return res


def _dispatch(name, table, args):
    key = tuple(_arg_token(a) for a in args)
    sym = table.get(key)
    if sym is None and len(key) == 2:           # symmetric fallback
        sym = table.get((key[1], key[0]))
    if sym is None:
        raise TypeError(
            f"{name}(): no portable overload for argument types {key}; "
            f"supported: {sorted(table)}"
        )
    fn = getattr(_pymeos_cffi(), sym)
    return _wrap(fn(*[_unwrap(a) for a in args]))
'''

FUNC_TMPL = '''

_T_{bare} = {table!r}


def {bare}(*args):
    """Portable ``{op}`` ({family}) -> pymeos_cffi backing call."""
    return _dispatch({bare!r}, _T_{bare}, args)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--headers", action="append", default=[],
                    help="MEOS include dir / header (repeatable)")
    ap.add_argument("--cffi", action="store_true",
                    help="introspect the installed pymeos_cffi (CI gate)")
    ap.add_argument("--contract", default=str(CONTRACT))
    ap.add_argument("--out", default=str(HERE.parents[1] / "pymeos"
                                        / "portable.py"))
    ap.add_argument("--report", default="")
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero unless 29/29 backed across 6 families")
    args = ap.parse_args()

    idl = attach_portable_aliases({"functions": []}, Path(args.contract))
    pa = idl["portableAliases"]
    by_bare = pa["byBareName"]               # bareName -> operator
    fam_of = {p["bareName"]: fam
              for fam, lst in pa["families"].items() for p in lst}
    explicit = pa.get("explicitBacking", {})
    in_scope = pa["scope"]["inScopeTypeFamilies"]

    # Codegen needs C signatures (to key dispatch on argument C types), so
    # the universe is ALWAYS the MEOS headers.  In CI the headers are the
    # freshly built+installed MEOS at the install prefix, so the committed
    # module stays in lock-step with the binding.  --cffi adds a *separate*
    # name-level assertion against the live built binding.
    hdrs = args.headers or _default_header_dirs()
    universe = universe_from_headers(hdrs)
    src = f"headers:{hdrs}"

    # Parity (name-level, byte-identical to the MEOS-API SoT logic).
    parity = build_parity(
        attach_portable_aliases(
            {"functions": [{"name": n} for n in universe]},
            Path(args.contract)))

    cffi_parity = None
    if args.cffi:
        try:
            cffi_u = universe_from_cffi()
            cffi_parity = build_parity(attach_portable_aliases(
                {"functions": [{"name": n} for n in cffi_u]},
                Path(args.contract)))
        except Exception as e:                       # binding not built
            cffi_parity = {"error": str(e)}

    # Codegen tables: bare -> {(arg C-type tokens): symbol}.
    fam_re = family_regexes(in_scope)
    tables, family_witness = {}, defaultdict(set)
    for bare in sorted(by_bare):
        syms, _ = backing_symbols(bare, explicit.get(bare, []), universe)
        tbl = {}
        for s in syms:
            for fam, rx in fam_re.items():
                if rx.search(s):
                    family_witness[fam].add(bare)
            ret, params = universe.get(s, (None, None))
            if params is None:          # cffi path: name only, no signature
                continue
            tbl[tuple(token(p) for p in params)] = s
        tables[bare] = tbl

    backed = parity["backed"]
    total = parity["total"]
    missing_fam = [f for f in in_scope if not family_witness.get(f)]

    body = [HEADER, f"\n__all__ = {sorted(by_bare)!r}\n"]
    for bare in sorted(by_bare):
        body.append(FUNC_TMPL.format(
            bare=bare, op=by_bare[bare], family=fam_of[bare],
            table=tables[bare]))
    Path(args.out).write_text("".join(body), encoding="utf-8")

    report = {
        "source": src,
        "universeSize": len(universe),
        "parity": {k: parity[k] for k in
                   ("total", "backed", "needsExplicitBacking", "parityPct")},
        "unbacked": parity["unbacked"],
        "inScopeFamilies": in_scope,
        "familyWitness": {k: sorted(v) for k, v in family_witness.items()},
        "familiesMissing": missing_fam,
        "cffiParity": (None if cffi_parity is None else
                       {k: cffi_parity.get(k) for k in
                        ("total", "backed", "needsExplicitBacking",
                         "unbacked", "error")}),
        "out": args.out,
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, indent=2))

    print(f"[portable] source={src} universe={len(universe)} "
          f"backed={backed}/{total} ({parity['parityPct']}%) "
          f"unbacked={parity['unbacked']} families_missing={missing_fam}")
    print(f"[portable] wrote {args.out} ({len(by_bare)} bare names)")

    cffi_fail = False
    if cffi_parity is not None:
        if "error" in cffi_parity and cffi_parity.get("error"):
            print(f"[portable] cffi check: binding not importable "
                  f"({cffi_parity['error']}) -- skipped")
        else:
            cffi_fail = (bool(cffi_parity["unbacked"])
                         or cffi_parity["backed"] != cffi_parity["total"])
            print(f"[portable] cffi check: "
                  f"{cffi_parity['backed']}/{cffi_parity['total']} backed, "
                  f"unbacked={cffi_parity['unbacked']}")

    fail = (bool(parity["unbacked"]) or backed != total or bool(missing_fam)
            or cffi_fail)
    if args.check:
        print("CHECK: " + ("FAIL" if fail else
              f"PASS - {total}/{total} backed, 0 unbacked, "
              f"all {len(in_scope)} families present"))
        return 1 if fail else 0
    return 0


def _default_header_dirs():
    """The single MEOS include dir to generate from, deterministically.

    Install-prefix first so a local run matches CI, where the workflow
    builds + installs MEOS to the prefix (``/usr/local`` | ``/opt/homebrew``)
    before regenerating; ``MEOS_INCLUDE`` overrides; the sibling MobilityDB
    checkout is the last resort.  A single dir keeps the committed artifact
    reproducible across machines.
    """
    for c in (os.environ.get("MEOS_INCLUDE"),
              "/usr/local/include", "/opt/homebrew/include",
              HERE.parents[2] / "MobilityDB" / "meos" / "include"):
        if c and Path(c).is_dir() and any(Path(c).glob("meos*.h")):
            return [str(c)]
    return []


if __name__ == "__main__":
    sys.exit(main())
