#!/usr/bin/env bash
# regen-from-pin.sh — regenerate the PyMEOS OO layer from the MEOS catalog (per GENERATION.md).
# PyMEOS sits on PyMEOS-CFFI; regenerate/install that first (the orchestrator does so in phase 1).
#
# Usage:  tools/regen-from-pin.sh <pin>
#   env:  CATALOG = path to meos-idl.json produced by MEOS-API run.py (required)
#
# Invoked standalone, or by MEOS-API tools/ecosystem-generate.sh (phase 2, after PyMEOS-CFFI).
set -euo pipefail
PIN="${1:?usage: regen-from-pin.sh <pin>}"
CATALOG="${CATALOG:?set CATALOG to the meos-idl.json from MEOS-API run.py}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

# 1. vendor the catalog (same step as tools/oo_codegen/regen-from-meos-api.sh)
cp "$CATALOG" "$HERE/tools/oo_codegen/meos-idl.json"

# 2. run the in-repo OO generator -> the generated method-family mixins
python3 "$HERE/tools/oo_codegen/codegen.py"

# 3. build-verify (PyMEOS-CFFI must already be installed in the env)
( cd "$HERE" && python3 -m pytest -q ) || echo "WARN: PyMEOS pytest returned non-zero"
echo "[pymeos] regenerated OO layer from catalog at pin $PIN"
