# PyMEOS generation — the canonical per-binding generator policy

PyMEOS is a **generated** binding. This document is the contract for how it is generated,
under the ecosystem-wide per-binding generator policy.

## The policy (ecosystem-wide)

Every MobilityDB language binding is a **pure projection of the MEOS-API catalog**, and
**each binding owns its own generator, in its own repo**, in a canonical layout. The single
source of truth is the **catalog** (`MEOS-API/output/meos-idl.json`, generated from the MEOS
C headers). A binding is an independent, plug-and-play module that owns its generation.

Each binding repo satisfies the same invariants: in-repo generator; own
`tools/pin/compose-order.txt`; vendored/pinned catalog; thin language projection
(language-neutral decisions live in the catalog); full automation toward a zero-hand-written
surface (generate-then-retire; the last green-CI version is the equivalence probe).

## PyMEOS is two layers (like Rust's meos-sys / meos)

1. **PyMEOS-CFFI** (separate repo) — the low-level CFFI binding. Generator = `builder/`,
   driving `pymeos_cffi/functions.py` from `meos-idl.json`. It keeps its **own**
   `tools/pin/compose-order.txt` + `GENERATION.md`.
2. **PyMEOS** (this repo) — the idiomatic **OO** layer on top of PyMEOS-CFFI. Generator =
   **`tools/oo_codegen/codegen.py`**, which reads the vendored `tools/oo_codegen/meos-idl.json`
   and emits the OO **method-family mixins** (one mixin per `@ingroup`/type family), so the
   per-type classes are generated rather than hand-written.

## Faithful OO codegen via dispatch metadata (RFC)

The OO layer's path to **100% faithful** generation is the canonical dispatch metadata
described in `tools/oo_codegen/RFC-dispatch-metadata.md`: the catalog carries the per-method
dispatch so each generated family resolves to the correct MEOS function without per-binding
special-casing. This is the regularity end state — zero hand special-cases.

## Generate-then-retire — the green-CI version is the probe

The switch from hand-written OO classes to the generated mixins happens **family by family**
(tcbuffer, tpose, tnpoint, trgeometry, …), each proven against the **last green-CI version**
(parity + the full test suite) before the hand methods for that family are retired. Never
wipe-first.

## Pinning

PyMEOS's vendored `tools/oo_codegen/meos-idl.json` is generated from a MobilityDB
`ecosystem-pin-*` via the MEOS-API `run.py` (`tools/oo_codegen/regen-from-meos-api.sh`). That
pin is the *catalog/surface* input; PyMEOS's own `tools/pin/compose-order.txt` governs *this
repo's* PR accumulate. See it for the composing set and the disposition of every open PR.
