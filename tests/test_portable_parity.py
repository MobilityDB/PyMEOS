"""Portable bare-name parity gate for PyMEOS.

The canonical portable dialect (RFC #920; contract:
MobilityDB/MEOS-API ``meta/portable-aliases.json``, vendored verbatim under
``tools/portable_aliases/``) is the single cross-binding source of truth.
This test is the PyMEOS analogue of MobilityDB's
``tools/portable_aliases/generate.py --check`` and MEOS-API's
``portable_parity.py``: it asserts that the generated ``pymeos.portable``
API exposes EVERY canonical bare name, each backed by a real pymeos_cffi
function, across all six in-scope type families -- 0 unbacked, zero
per-binding exceptions.  It runs without the compiled binding (operating on
the contract + the committed generated module + the MEOS function universe),
and additionally verifies against the live pymeos_cffi when present.

    python3 -m pytest tests/test_portable_parity.py
    python3 tests/test_portable_parity.py
"""

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "portable_aliases"
sys.path.insert(0, str(TOOLS))

from portable import attach_portable_aliases          # vendored from SoT
from portable_parity import build_parity              # vendored from SoT
import generate as gen

CONTRACT = TOOLS / "portable-aliases.json"
GENERATED = ROOT / "pymeos" / "portable.py"


def _contract():
    return attach_portable_aliases({"functions": []}, CONTRACT)["portableAliases"]


def _resolve_universe():
    """(universe, source).  Live pymeos_cffi if built (CI), else the in-tree
    MEOS headers, else (None, None) -> universe-dependent checks skip."""
    try:
        return gen.universe_from_cffi(), "pymeos_cffi"
    except Exception:
        pass
    dirs = gen._default_header_dirs()
    if dirs:
        return gen.universe_from_headers(dirs), f"headers:{dirs}"
    return None, None


def _committed_all_and_tables():
    """AST-read the committed module without importing it (no binding needed)."""
    tree = ast.parse(GENERATED.read_text())
    all_names, tables = None, {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        name = getattr(node.targets[0], "id", "")
        if name == "__all__":
            all_names = ast.literal_eval(node.value)
        elif name.startswith("_T_"):
            tables[name[3:]] = ast.literal_eval(node.value)
    return all_names, tables


class ContractIntegrity(unittest.TestCase):
    def test_29_bijective_pairs(self):
        pa = _contract()
        self.assertEqual(pa["count"], 29)
        self.assertEqual(len(pa["bareNames"]), 29)
        self.assertEqual(len(pa["byOperator"]), 29)
        self.assertEqual(len(pa["byBareName"]), 29)
        self.assertEqual(
            pa["scope"]["inScopeTypeFamilies"],
            ["temporal", "geo", "cbuffer", "npoint", "pose", "rgeo"])


class CommittedModule(unittest.TestCase):
    """The shipped pymeos/portable.py must expose every canonical bare name
    with a real, non-empty backing table -- zero per-binding exceptions."""

    def test_exposes_every_bare_name(self):
        pa = _contract()
        all_names, tables = _committed_all_and_tables()
        self.assertEqual(sorted(all_names), sorted(pa["bareNames"]))
        self.assertEqual(set(tables), set(pa["bareNames"]))
        empty = sorted(b for b, t in tables.items() if not t)
        self.assertEqual(empty, [], f"bare names with no backing: {empty}")

    def test_every_entry_routes_to_a_real_symbol(self):
        _, tables = _committed_all_and_tables()
        for bare, tbl in tables.items():
            for key, sym in tbl.items():
                self.assertIsInstance(sym, str)
                self.assertRegex(sym, r"^[a-z][a-z0-9_]+$",
                                 f"{bare}: bad backing symbol {sym!r}")


@unittest.skipIf(_resolve_universe()[0] is None,
                 "no pymeos_cffi and no MEOS headers available")
class ParityGate(unittest.TestCase):
    """Byte-identical to the MEOS-API SoT parity logic: 29/29, 0 unbacked."""

    def setUp(self):
        self.universe, self.source = _resolve_universe()

    def test_29_of_29_backed_zero_unbacked(self):
        rep = build_parity(attach_portable_aliases(
            {"functions": [{"name": n} for n in self.universe]}, CONTRACT))
        self.assertEqual(rep["total"], 29)
        self.assertEqual(rep["needsExplicitBacking"], 0,
                         f"unbacked: {rep['unbacked']}")
        self.assertEqual(rep["backed"], 29)
        self.assertEqual(rep["parityPct"], 100.0)

    def test_all_six_families_present(self):
        pa = _contract()
        in_scope = pa["scope"]["inScopeTypeFamilies"]
        fam_re = gen.family_regexes(in_scope)
        witnessed = set()
        for bare in pa["bareNames"]:
            syms, _ = gen.backing_symbols(
                bare, pa.get("explicitBacking", {}).get(bare, []),
                self.universe)
            for s in syms:
                for fam, rx in fam_re.items():
                    if rx.search(s):
                        witnessed.add(fam)
        missing = [f for f in in_scope if f not in witnessed]
        self.assertEqual(missing, [], f"families with no backing: {missing}")


@unittest.skipIf(_resolve_universe()[0] is None,
                 "no pymeos_cffi and no MEOS headers available")
class CommittedModuleValidity(unittest.TestCase):
    """Every backing symbol the shipped module dispatches to must exist in
    the resolved universe -- i.e. the committed ``pymeos/portable.py`` is
    valid for the binding actually under test (catches hand edits and stale
    drift that would break runtime, while tolerating benign MEOS overload
    additions across versions, unlike a brittle byte-for-byte snapshot).
    """

    def test_every_committed_symbol_is_real(self):
        universe, _ = _resolve_universe()
        _, tables = _committed_all_and_tables()
        unknown = sorted({
            sym for tbl in tables.values() for sym in tbl.values()
            if sym not in universe
        })
        self.assertEqual(
            unknown, [],
            f"pymeos/portable.py dispatches to {len(unknown)} symbol(s) "
            f"absent from the binding -- regenerate with "
            f"tools/portable_aliases/generate.py: {unknown[:10]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
