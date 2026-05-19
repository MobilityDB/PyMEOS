#!/bin/bash
# Regenerate tools/oo_codegen/meos-idl.json directly from the MEOS-API parser
# (github.com/MobilityDB/MEOS-API run.py), proving the vendored catalog IS
# the canonical MEOS-API artifact and not a hand-massaged copy.
#
# The vendored copy is normally taken from PyMEOS-CFFI's builder/meos-idl.json
# (itself a MEOS-API run.py snapshot, byte-schema-identical: functions{file,
# name,params,returnType}, structs[].fields[].offset_bits, enums). This script
# reproduces that snapshot from MEOS-API directly against a chosen MEOS ref.
#
# Usage:
#   tools/oo_codegen/regen-from-meos-api.sh <MEOS_INCLUDE_DIR> \
#       [MEOS_API_REF]   # default: feat/portable-aliases (PR #8)
#
# Then review the diff and re-run the generator + Black:
#   python3 tools/oo_codegen/codegen.py --check
#   python3 tools/oo_codegen/codegen.py --mixin cbuffer \
#       --mixin-out pymeos/main/_generated/tcbuffer_methods.py
#   black tools/oo_codegen pymeos/main/_generated
set -euo pipefail

INCLUDE_DIR=${1:?usage: regen-from-meos-api.sh <MEOS_INCLUDE_DIR> [REF]}
REF=${2:-feat/portable-aliases}
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "[regen] cloning MEOS-API@$REF ..."
git clone --depth 1 -b "$REF" \
  https://github.com/MobilityDB/MEOS-API "$WORK/MEOS-API" >/dev/null 2>&1
python3 -m pip install --quiet --user 'libclang==18.1.1' >/dev/null 2>&1 || true

echo "[regen] running MEOS-API run.py against $INCLUDE_DIR ..."
( cd "$WORK/MEOS-API" && python3 run.py "$INCLUDE_DIR" )

cp "$WORK/MEOS-API/output/meos-idl.json" "$HERE/meos-idl.json"
python3 - "$HERE/meos-idl.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(f"[regen] wrote meos-idl.json: {len(d['functions'])} functions, "
      f"{len(d.get('structs', []))} structs, {len(d.get('enums', []))} enums")
PY
echo "[regen] done -- review 'git diff', then regenerate the mixin + Black."
