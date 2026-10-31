"""Coverage and backing gate of the catalog-driven OO method-family generator.

``tools/oo_codegen/codegen.py`` reads the meos-idl.json catalog of the MEOS the
package builds against (``$MEOS_IDL``, the catalog the test workflow derives)
and accounts for every catalogued function: emitted as a regular method or
counted under a named exclusion, none unaccounted, all six temporal type
families present.  The mixins committed in ``pymeos/main/_generated/`` are the
generator's output on that catalog as #format_mixin lays it out, and every MEOS function they call is a
function of the catalog.  The tests call the generator's own #collect and
#emit_faithful_mixin rather than restating them.

    MEOS_IDL=<meos-idl.json> python3 -m pytest tests/test_oo_codegen_coverage.py
"""

import ast
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "oo_codegen"
sys.path.insert(0, str(TOOLS))

import codegen as cg  # noqa: E402  (the generator, found through the path set above)

IN_SCOPE = ["cbuffer", "geo", "npoint", "pose", "rgeo", "temporal"]
# The conversions the binding owns, which the mixins call beside MEOS.
BINDING_CONVERSIONS = {
    "datetime_to_timestamptz",
    "geo_to_gserialized",
    "geometry_to_gserialized",
    "gserialized_to_shapely_geometry",
}


def _idl():
    """The catalog $MEOS_IDL names, as #collect reads it."""
    path = os.environ.get("MEOS_IDL")
    if not path:
        raise RuntimeError(
            "MEOS_IDL names no catalog: set it to the meos-idl.json of the MEOS the package builds against"
        )
    return json.loads(Path(path).read_text())


def _called_names(tree):
    """The names of the plain functions a module calls, as #emit_faithful_mixin writes them."""
    return {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}


class CoverageAccounting(unittest.TestCase):
    """The accounting #collect states."""

    def test_zero_unaccounted(self):
        idl = _idl()
        _, st = cg.collect(idl)
        accounted = st.emitted_overloads + st.datum + st.irregular + st.out_of_scope
        self.assertEqual(len(idl["functions"]) - accounted, 0)

    def test_all_six_families_present(self):
        fams, _ = cg.collect(_idl())
        self.assertEqual(sorted(fams), IN_SCOPE)


class BackingValidity(unittest.TestCase):
    """The committed mixins are #emit_faithful_mixin's output and call catalog functions."""

    def test_committed_matches_generator(self):
        fams, _ = cg.collect(_idl())
        for family in cg.FAMILY_MODEL:
            path = cg.mixin_path(family)
            with self.subTest(family=family):
                generated = cg.format_mixin(
                    cg.emit_faithful_mixin(family, fams[cg.FAMILY_MODEL[family].get("catalog_family", family)]), path
                )
                self.assertEqual(
                    path.read_text(),
                    generated,
                    f"{path.name} is not the generator's output: run codegen.py --mixin {family}",
                )

    def test_every_called_function_is_in_the_catalog(self):
        names = {f["name"] for f in _idl()["functions"]}
        for family in cg.FAMILY_MODEL:
            path = cg.mixin_path(family)
            called = _called_names(ast.parse(path.read_text()))
            meos = {n for n in called if "_" in n and n.islower()} - BINDING_CONVERSIONS
            with self.subTest(module=path.name):
                self.assertEqual(sorted(meos - names), [])


if __name__ == "__main__":
    unittest.main()
