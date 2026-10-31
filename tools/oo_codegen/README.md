# PyMEOS OO method-family generator

`codegen.py` reads the `meos-idl.json` catalog of the MEOS the package builds
against, the catalog the [MEOS-API](https://github.com/MobilityDB/MEOS-API)
parser derives from the installed MEOS headers, and writes the *regular*
method families of the temporal classes as mixins of the package:
comparison, spatial relationship (ever, always, temporal), distance and
restriction.

Each family `FAMILY_MODEL` describes gets one mixin,
`pymeos/main/_generated/<module>_methods.py`, which its temporal class takes
as its first base. Every generated method dispatches by the argument's type
to the `pymeos_cffi` function of that overload; nothing is reimplemented.
The irregular core (constructors, conversions, accessors, transforms, input
and output) stays hand-written in `pymeos/main/<module>.py`.

## Running

```
export MEOS_IDL=<path to meos-idl.json>
python3 tools/oo_codegen/codegen.py --check            # accounting gate
python3 tools/oo_codegen/codegen.py --mixin cbuffer    # rewrite one mixin
```

`--check` fails when a catalogued function is neither emitted nor counted
under a named exclusion (Datum-bearing internals, the hand-written core,
functions outside the temporal families). `--mixin` writes the mixin of one
family through `ruff check --fix` and `ruff format`, so the committed file
is the generator's output and passes the repository's ruff workflow. A
catalog argument token the family model does not map stops the generator
with its name, so a new MEOS overload is never dropped silently.

The test workflow derives the catalog from the MobilityDB branch the package
version names and sets `MEOS_IDL` for pytest;
`tests/test_oo_codegen_coverage.py` checks the accounting, that every
committed mixin is the generator's output on that catalog, and that every
function a mixin calls is a function of the catalog.
