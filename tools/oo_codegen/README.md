# PyMEOS OO method-family code generator

`codegen.py` reads the vendored `meos-idl.json` (the signature catalog
produced by the [MEOS-API](https://github.com/MobilityDB/MEOS-API) parser
and consumed verbatim by every binding) and emits one idiomatic PyMEOS
**OO method** per *regular* method-family member into
`tools/oo_codegen/_preview/<family>_methods.py`.

It is the high-level analogue of two existing ecosystem artifacts:

* **GoMEOS PR #2** (`refactor/codegen-meos-idl`, `tools/codegen.py` →
  `tools/_preview/`) — the non-destructive Draft-artifact discipline: a
  vendored IDL, output written to an underscore-prefixed directory the
  package never imports, explicit *counted* exclusions instead of silent
  gaps, and a coverage report.
* **PyMEOS PR #87** (`tools/portable_aliases/generate.py`) — the in-repo
  content model: every generated callable dispatches to the **exact
  `pymeos_cffi` backing function** the hand-written surface uses. Nothing
  is reimplemented, so each generated method is identical to its
  hand-written counterpart by construction.

## Running

```
python3 tools/oo_codegen/codegen.py            # regenerate the preview
python3 tools/oo_codegen/codegen.py --check    # accounting gate (CI)
```

The generator is offline and import-safe: it reads only the vendored JSON
and never needs a compiled MEOS.

## Coverage today

2833 catalogued functions, fully accounted for:

| Bucket | Count |
|---|---|
| Emitted regular methods | **107** (407 typed overloads) across **all 6** families |
| &nbsp;&nbsp;cbuffer | 30 methods / 103 overloads |
| &nbsp;&nbsp;geo | 29 / 83 |
| &nbsp;&nbsp;npoint | 12 / 35 |
| &nbsp;&nbsp;pose | 12 / 35 |
| &nbsp;&nbsp;rgeo | 10 / 30 |
| &nbsp;&nbsp;temporal | 14 / 121 |
| Hand-written core (see below) | 864 |
| Datum-bearing internal helpers (excluded) | 43 |
| Out of scope (non-temporal-family headers) | 1519 |

Zero unaccounted: every function is either emitted or counted under an
explicit, named exclusion. `--check` fails the build otherwise.

## What is generated vs hand-written (the hybrid, matching GoMEOS)

The hand-written PyMEOS types spell out, uniformly across every temporal
type, a set of **regular** families whose entire behaviour is a thin
isinstance ladder forwarding `self._inner` + the unwrapped argument to a
typed MEOS overload and post-processing the result deterministically. That
regularity is exactly what a signature catalog can synthesise:

* **comparison** — `always/ever_equal`, `*_not_equal`, `temporal_*`
* **spatial relationship** — ever (`is_ever_*`, `ever_intersects/touches`),
  always (`is_always_*`, `always_intersects/touches`), temporal
  (`contains/covers/disjoint/within_distance/intersects/touches`)
* **distance** — `distance`, `nearest_approach_distance/instant`,
  `shortest_line`
* **restriction** — `at`, `minus`

The **irregular core stays hand-written** because it needs per-function
editorial decisions a signature alone does not carry: constructors
(`from_*`), conversions (`to_*`, `as_wkt/ewkt`), accessors and transforms
(`srid`, `round`, `transform`, …) and I/O (`read_from_cursor`). These are
counted (864) and named, never silently dropped — the same discipline
GoMEOS applies to its Datum-bearing exclusions.

## Non-destructive Draft artifact

`tools/oo_codegen/_preview/` is **never imported by the `pymeos`
package** — the directory is underscore-prefixed and the modules carry a
self-contained, lazily-resolved `pymeos_cffi` shim so they import cleanly
without the compiled binding. The preview exists so a reviewer can diff
this uniform, deterministic surface against the hand-written
`pymeos/main/*.py` before any staged migration. It is intentionally
committed (like GoMEOS's `tools/_preview/*.go`).

## Black

The committed preview is formatted with Black (`~= 24`, the repo's
`black.yml` pin). After regenerating, re-apply it before committing:

```
python3 tools/oo_codegen/codegen.py
black tools/oo_codegen
```

The CI gate (`--check`) asserts accounting and family coverage, not
formatting, so a raw regenerate never breaks the build.

## Refreshing the IDL

`meos-idl.json` is vendored from `PyMEOS-CFFI` (`builder/meos-idl.json`,
the `bump/meos-1.4` line). When MEOS bumps, copy the regenerated catalog
back and re-run:

```
cp ../PyMEOS-CFFI/builder/meos-idl.json tools/oo_codegen/meos-idl.json
python3 tools/oo_codegen/codegen.py && black tools/oo_codegen
```
