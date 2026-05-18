# Portable bare-name dialect (PyMEOS)

PyMEOS exposes every MobilityDB operator under a single **portable bare
name** (`overlaps`, `contains`, `teq`, `nearestApproachDistance`, …) so one
query reads the same across every binding/engine.

## Source of truth

`portable-aliases.json` is the canonical contract, vendored **verbatim**
from `MobilityDB/MEOS-API` (`meta/portable-aliases.json`, RFC #920;
discussion MobilityDB #861; native in MobilityDB via the 1303-alias
PR #1075). `portable.py` and `portable_parity.py` are likewise vendored
verbatim from MEOS-API so PyMEOS's parity logic is byte-identical to the
ecosystem source of truth. Update them only by re-vendoring from MEOS-API.

The mapping is **29 operator → bare-name pairs**, type-agnostic across all
six in-scope temporal type families: `temporal, geo, cbuffer, npoint, pose,
rgeo`.

## What is generated

`pymeos/portable.py` (GENERATED — do not edit) defines one callable per
bare name. Each dispatches, by the runtime C type of its arguments, to the
**exact `pymeos_cffi` function** the operator is backed by — the same native
call the type-qualified API uses. Nothing is reimplemented: every bare name
is identical to its operator by construction.

## Regenerate

```
python3 tools/portable_aliases/generate.py            # uses MEOS at the
                                                      # install prefix
python3 tools/portable_aliases/generate.py --check    # parity gate
python3 tools/portable_aliases/generate.py --cffi --check  # also assert the
                                                      # live built binding
```

`MEOS_INCLUDE=<dir>` (or `--headers <dir>`) selects the MEOS headers; the
default is the install prefix, then a sibling MobilityDB checkout.

## Gate

`tests/test_portable_parity.py` (run by `pytest`, and the explicit CI step)
asserts: the contract is 29 bijective pairs; the generated API exposes every
bare name with a non-empty backing table; parity is **29/29 backed, 0
unbacked** (byte-identical to the MEOS-API logic); all six in-scope families
are witnessed; and every committed backing symbol exists in the binding
under test. Zero per-binding exceptions.
