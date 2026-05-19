"""Coverage + backing gate for the meos-idl.json-driven OO codegen.

This is the high-level analogue of ``tests/test_portable_parity.py``: it
asserts that ``tools/oo_codegen/codegen.py`` accounts for EVERY catalogued
function (emitted as a regular method or counted under a named exclusion --
zero unaccounted), covers all six in-scope temporal type families, and that
every overload the committed Draft preview dispatches to is the EXACT
``pymeos_cffi`` backing symbol present in the vendored catalog (reuse the
operator's own backing -- equivalence by construction, never reimplemented).

It runs fully offline (no compiled binding): the catalog is the vendored
``tools/oo_codegen/meos-idl.json`` and the preview is read by AST without
importing it.

    python3 -m pytest tests/test_oo_codegen_coverage.py
    python3 tests/test_oo_codegen_coverage.py
"""

import ast
import json
import py_compile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "oo_codegen"
PREVIEW = TOOLS / "_preview"
sys.path.insert(0, str(TOOLS))

import codegen as cg  # the generator under test

IN_SCOPE = ["cbuffer", "geo", "npoint", "pose", "rgeo", "temporal"]


def _idl():
    return json.loads((TOOLS / "meos-idl.json").read_text())


def _collected():
    return cg.collect(_idl())


def _preview_tables():
    """AST-read every committed preview module without importing it.

    Returns ``{family: {method_name: {arg_key: backing_symbol}}}`` plus the
    set of module paths seen, so the committed Draft can be checked against
    the generator without a compiled binding.
    """
    out = {}
    for path in sorted(PREVIEW.glob("*_methods.py")):
        family = path.stem.replace("_methods", "")
        tree = ast.parse(path.read_text())
        methods = {}
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            if not cls.name.startswith("T"):
                continue
            for fn in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
                table = None
                for stmt in fn.body:
                    if (
                        isinstance(stmt, ast.Assign)
                        and getattr(stmt.targets[0], "id", "") == "_disp"
                    ):
                        table = ast.literal_eval(stmt.value)
                if table is not None:
                    methods[fn.name] = table
        out[family] = methods
    return out


class CoverageAccounting(unittest.TestCase):
    """Every catalogued function is emitted or explicitly counted."""

    def test_zero_unaccounted(self):
        idl = _idl()
        _, st = cg.collect(idl)
        total = len(idl["functions"])
        accounted = st.emitted_overloads + st.datum + st.irregular + st.out_of_scope
        self.assertEqual(
            accounted,
            total,
            f"{total - accounted} functions neither emitted nor counted",
        )

    def test_all_six_families_present(self):
        fams, _ = _collected()
        self.assertEqual(sorted(fams), IN_SCOPE)
        empty = sorted(f for f, m in fams.items() if not m)
        self.assertEqual(empty, [], f"families with no methods: {empty}")


class CommittedPreview(unittest.TestCase):
    """The committed Draft preview must compile, parse, and stay in
    lock-step with the generator (catches hand edits / stale drift)."""

    def test_every_module_compiles(self):
        mods = sorted(PREVIEW.glob("*_methods.py"))
        self.assertEqual(len(mods), 6, f"expected 6 preview modules, found {len(mods)}")
        for path in mods:
            py_compile.compile(str(path), doraise=True)

    def test_every_entry_is_a_valid_symbol(self):
        for family, methods in _preview_tables().items():
            for meth, table in methods.items():
                self.assertTrue(table, f"{family}.{meth}: empty dispatch")
                for key, sym in table.items():
                    self.assertRegex(
                        sym,
                        r"^[a-z][a-z0-9_]+$",
                        f"{family}.{meth}[{key}]: bad symbol {sym!r}",
                    )

    def test_committed_matches_generator(self):
        fams, _ = _collected()
        expected = {
            fam: {name: m.overloads for name, m in meths.items()}
            for fam, meths in fams.items()
        }
        self.assertEqual(
            _preview_tables(),
            expected,
            "committed _preview/ is out of sync -- regenerate with "
            "`python3 tools/oo_codegen/codegen.py && black tools/oo_codegen`",
        )


class BackingValidity(unittest.TestCase):
    """Every symbol the preview dispatches to is a real catalogued
    function -- the generated method reuses the operator's own backing,
    so it is identical by construction (never reimplemented)."""

    def test_every_symbol_is_a_real_idl_function(self):
        names = {f["name"] for f in _idl()["functions"]}
        unknown = sorted(
            {
                sym
                for methods in _preview_tables().values()
                for table in methods.values()
                for sym in table.values()
                if sym not in names
            }
        )
        self.assertEqual(
            unknown,
            [],
            f"preview dispatches to {len(unknown)} symbol(s) absent from "
            f"meos-idl.json: {unknown[:10]}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
