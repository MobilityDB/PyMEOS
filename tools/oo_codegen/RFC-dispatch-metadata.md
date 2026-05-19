# RFC — canonical *dispatch* metadata for 100 % faithful OO codegen

**Status:** proposed (PyMEOS-authored cross-repo handoff to MobilityDB/MEOS-API)
**Scope:** the path to 100 % of the OO codegen-switch — covering the two
families (`geo`, `temporal`) that cannot be faithfully generated today.

## 1. Problem

The `meos-idl.json`-driven faithful generator (`tools/oo_codegen/codegen.py`)
switched **4 of 6** temporal-type families to generated mixins, each proven
equivalent to the hand-written code (TCbuffer #90, TPose #91, TNpoint #92,
TRgeometry #93). It works because those families' regular-method dispatch is
**mechanically derivable from the catalog**: the C-name structure
`<member>_<typetoken>_<argtoken>` (e.g. `econtains_tcbuffer_cbuffer`) plus a
small per-family token model is sufficient to reproduce the hand-written
`isinstance` ladder exactly (equivalence by construction).

`geo` (TGeomPoint/TGeogPoint) and `temporal` (TFloat/TInt/TBool/TText) **cannot**
be generated this way. Their hand-written regular methods encode *editorial
dispatch decisions that are absent from `meos-idl.json`* and therefore not
derivable from it:

| Family | Editorial dispatch not in the catalog |
|---|---|
| geo | `STBox` → `tdistance_tgeo_geo(self._inner, stbox_to_geo(other._inner))` (no `*_tgeo_stbox` in the catalog — the STBox routing is a Python-side convenience); `shp.Point` vs `shpb.BaseGeometry` split → *different* backings (`tpoint_at_value` vs `tpoint_at_geom`); the geometry transform is **runtime-self-dependent**: `geo_to_gserialized(other, isinstance(self, TGeogPoint))`; `GeoSet` → generic `temporal_at_values`; regular families split across the `TPoint` ABC and its subclasses |
| temporal | `IntSet`/`IntSpan`/`IntSpanSet` → `super().at(other.to_floatset())` (Python-side type coercion, no `tfloat_at_intset` in the catalog); scalars passed **by value** with a per-member cast (`tfloat_at_value(self._inner, float(other))`); self-type uses the **generic** `*_temporal_temporal` (no typed `*_tfloat_tfloat`) |

A PyMEOS-local generator extension that hard-codes this dispatch into
`FAMILY_MODEL` was considered and **rejected**: it would merely relocate the
editorial Python logic into per-binding config — *no* equivalence by
construction (the catalog is no longer the source of truth), equal bug risk,
more config than the code it replaces, and it would diverge from every other
binding's generator. That is the transcription anti-pattern.

## 2. Root cause

`meos-idl.json` is a *signature* catalog. The geo/temporal dispatch is
*editorial* (type coercions, conversions, runtime flags, generic fallbacks).
The MEOS-API RFC (MobilityDB issue #836 / discussion #920) already designed
the catalog to carry **editorial/shape decisions** in the
`meta/meos-meta.json` enrichment layer, merged into `meos-idl.json` so that
**every binding's codegen consumes the same canonical facts**
(GoMEOS already consumes `shape.*` annotations this way). The gap is simply
that the *dispatch* facts geo/temporal need have no schema yet.

## 3. Proposal — a `dispatch` annotation in `meta/meos-meta.json`

Add a per-OO-member `dispatch` block (merged into `meos-idl.json` like the
existing `shape`) describing the **ordered argument→backing table** the
hand-written method encodes. It is declarative, catalog-owned, and
binding-agnostic; each binding's existing faithful generator consumes it the
same way it already consumes the `<member>_<type>_<arg>` token model —
restoring equivalence by construction at the *catalog* level.

```jsonc
// meta/meos-meta.json  (excerpt — keyed by OO family + member)
"oo": {
  "geo": {
    "at": {
      "dispatch": [
        { "py": "Point",       "fn": "tpoint_at_value",
          "argTransform": "geoToGserialized", "geodeticFromSelf": true },
        { "py": "BaseGeometry","fn": "tpoint_at_geom",
          "argTransform": "geoToGserialized", "geodeticFromSelf": true },
        { "py": "GeoSet",      "fn": "temporal_at_values" },
        { "py": "STBox",       "fn": "tgeo_at_stbox", "extraArgs": ["true"] }
      ],
      "fallback": "super", "result": "temporal"
    },
    "distance": {
      "dispatch": [
        { "py": "BaseGeometry","fn": "tdistance_tgeo_geo",
          "argTransform": "geoToGserialized", "geodeticFromSelf": true },
        { "py": "STBox",       "fn": "tdistance_tgeo_geo",
          "argTransform": "stboxToGeo" },
        { "py": "TPoint",      "fn": "tdistance_tgeo_tgeo" }
      ],
      "fallback": "raise", "result": "temporal"
    }
  },
  "temporal": {
    "at": {
      "dispatch": [
        { "py": "scalar",  "fn": "<t>_at_value", "argTransform": "scalarCast" },
        { "py": "IntSet",  "coerce": "to_floatset",  "via": "super" },
        { "py": "IntSpan", "coerce": "to_floatspan", "via": "super" }
      ],
      "fallback": "super", "result": "temporal"
    },
    "always_equal": {
      "dispatch": [
        { "py": "scalar", "fn": "always_eq_<t>_<base>", "argTransform": "scalarValue" },
        { "py": "self",   "fn": "always_eq_temporal_temporal" }
      ],
      "fallback": "raise", "result": "bool_gt0"
    }
  }
}
```

`argTransform` values are a **closed, named vocabulary** (`geoToGserialized`,
`stboxToGeo`, `scalarCast`, `scalarValue`, `innerPtr`, …) — every binding maps
each name to its own idiom (PyMEOS: `geo_to_gserialized($o, <geodetic>)`,
`stbox_to_geo($o._inner)`, `float($o)`, `$o`, `$o._inner`). `geodeticFromSelf`
is the only runtime-self primitive (PyMEOS → `isinstance(self, TGeogPoint)`).
The vocabulary is finite because the editorial decisions are finite and
already enumerated above.

## 4. Why this is sound (and Path A is not)

- **Single source of truth.** The dispatch becomes a *catalog fact*, authored
  once in MEOS-API, consumed identically by Go/NET/PyMEOS/… — the RFC's whole
  premise. Equivalence by construction is restored: the generator emits from
  canonical metadata, not per-binding guesses.
- **Acceptance unchanged.** Each binding still proves it via its existing A/B
  suite test (behavioural equivalence) — the same gate used for the 4 shipped
  families.
- **Ecosystem-wide 100 %**, not PyMEOS-local: every binding's geo/temporal
  surface becomes generated from the same metadata.

## 5. Ownership & sequencing

- **MEOS-API (parallel-owned):** add the `oo.<family>.<member>.dispatch`
  schema to `meta/meos-meta.json` + the `argTransform` vocabulary doc; emit it
  into `meos-idl.json`. (This RFC is the handoff brief; the dispatch tables in
  §3 are extracted verbatim from PyMEOS's hand-written oracle and are complete
  for geo/temporal — see `tools/oo_codegen/codegen.py` `FAMILY_MODEL` for the
  4 already-derived families as the precedent.)
- **PyMEOS (this repo, follow-up):** teach `codegen.py` to consume
  `oo.*.dispatch` (map the `argTransform` vocabulary to PyMEOS idioms; add
  `geodeticFromSelf`, `coerce/via:super`, `scalar` primitives), then generate
  + A/B-prove geo & temporal mixins → **codegen 100 % (6/6)**. The local
  `FAMILY_MODEL` for the 4 derived families converges onto the same consumed
  metadata over time.

Until the metadata lands, geo/temporal **correctly stay hand-written** — they
are fully functional (no API-parity gap); only the *codegen-uniformity* goal
is outstanding, and this RFC is its sound resolution.

## 6. Unification — one systemic root cause

Driving the MEOS-1.4 bump (PyMEOS #81, Wave 2 of the integration train)
surfaced the same root cause and consolidates the whole problem space:

- `bump/meos-1.4` collects cleanly but is **299 failed / 4193 passed**
  against a composed Wave-0 MEOS + freshly-regenerated PyMEOS-CFFI.
- **~96 of those are a single class**: the regenerated `pymeos_cffi`
  wrappers do bare `_ffi.cast('T *', None)` / `None.encode('utf-8')` for
  optional params (e.g. `temporal_as_mfjson.srs`, `stbox_make.s`).
- **PyMEOS-CFFI's codegen is already correct** — it emits
  `… if x is not None else _ffi.NULL` *iff* the param is in
  `shape.nullable` of `meos-idl.json` (`build_pymeos_functions.py`). The
  failures exist purely because the Wave-1 `meos-idl.json` **lacks the
  `shape.nullable` enrichment** for those params.

So the geo/temporal `oo.dispatch` gap (this RFC), the original
`NotImplementedError` stub→real gap, **and** the ~96-failure MEOS-1.4
nullable regression are *the same defect*: **`meta/meos-meta.json`
enrichment is incomplete**. They are one problem, not three.

**This RFC is therefore generalised:** the canonical-metadata completion it
proposes must also cover **`shape.nullable`** (and the `shape.*` editorial
annotations GoMEOS already consumes). Consumers are already written for it —
every binding's codegen reads `shape.nullable` today; it is simply empty. A
blanket "treat every pointer/string param as nullable" shim is rejected for
the same reason as the Path-A transcription hack: it would silently `NULL`
params that should raise, masking genuine argument errors — not
equivalence-preserving. The sound fix is enriching the canonical catalog so
the already-deployed, already-correct codegen does the right thing
everywhere at once.

**Net:** completing `meta/meos-meta.json` (`oo.dispatch` + `shape.nullable`
+ `shape.*`) is *the* single highest lever for ecosystem-wide 100 % parity —
it closes geo/temporal codegen, the stub→real surface, and ≈⅓ of the
MEOS-1.4 bump together. This is the one cross-repo handoff to MEOS-API that
matters most.

## 7. Verbatim extended dispatch SoT (D1-extension — transcribe, do not derive)

§3 above carried only the **4 illustrative** members. This section is the
**complete, fully-resolved, verbatim** editorial-member dispatch, transcribed
1:1 from the hand-written oracle (`pymeos/main/{tpoint,tfloat,tint,tbool,
ttext}.py` on `feat/extended-temporal-types`). No placeholders, no `<t>/<base>`
— every `fn`/type/cast is resolved. The MEOS-API session transcribes this
**verbatim** into `meta/object-model.json#/dispatch` (geo single-block;
`temporal.{tfloat,tint,tbool,ttext}.<member>` per-concrete, the adopted
contract); §6's "do not re-derive" applies — a prose recipe is *not* a
substitute for these tables (it already produced 5 verified errors, below).

**Schema additions to the closed vocabulary:** `scalarType` (the exact
`isinstance` test for a `py:"scalar"` entry, e.g. `"float"`, `"int|float"`,
`"int"`, `"bool"`, `"str"`); `argTransform` gains `scalarValue` (pass `$o`
as-is), `scalarCast` (cast `$o` to the block's concrete base — `float()` for
`tfloat`, `int()` for `tint`), `textsetMake` (`textset_make($o)`); `py:"list[str]"`
(= `isinstance(other,list) and isinstance(other[0],str)`). `coerce`+`via:"super"`
unchanged.

**Recipe-vs-oracle errors this SoT corrects (why verbatim is mandatory):**
(1) temporal has **no** editorial `distance` member (TFloat/TInt expose none);
(2) `geo.nearest_approach_distance` STBox uses the *typed* `nad_tgeo_stbox`
(`innerPtr`), **not** `stboxToGeo`; (3) TFloat always/ever-compare `scalarType`
is `"float"`, but its `temporal_equal`/`at` is `"int|float"` — differs per
member; (4) TInt coerces **Float→Int** (`to_intset`…), the opposite direction
to TFloat, and its `temporal_equal` is `teq_tint_int($o)` with **no cast**
(`scalarValue`), unlike TFloat's `float()`-cast; (5) TBool exposes only
`temporal_equal/not_equal/at/minus` (no `always_/ever_`); TText `at/minus`
has a `list[str]→temporal_at_values(textset_make(...))` branch.

```jsonc
// dispatch.geo  (ADD to the 2 already in D1: at, distance)
"minus": { "fallback":"super", "result":"temporal", "dispatch":[
  {"py":"Point",       "fn":"tpoint_minus_value","argTransform":"geoToGserialized","geodeticFromSelf":true},
  {"py":"BaseGeometry","fn":"tpoint_minus_geom", "argTransform":"geoToGserialized","geodeticFromSelf":true},
  {"py":"GeoSet",      "fn":"temporal_minus_values"},
  {"py":"STBox",       "fn":"tgeo_minus_stbox",  "extraArgs":["true"]} ]},
"nearest_approach_distance": { "fallback":"raise", "result":"scalar", "dispatch":[
  {"py":"BaseGeometry","fn":"nad_tgeo_geo","argTransform":"geoToGserialized","geodeticFromSelf":true},
  {"py":"STBox",       "fn":"nad_tgeo_stbox"},
  {"py":"TPoint",      "fn":"nad_tgeo_tgeo"} ]}

// dispatch.temporal.tfloat  (self entry => generic *_temporal_temporal)
"always_equal":    {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"float","fn":"always_eq_tfloat_float","argTransform":"scalarValue"},
  {"py":"self","fn":"always_eq_temporal_temporal"}]},
"always_not_equal":{"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"float","fn":"always_ne_tfloat_float","argTransform":"scalarValue"},
  {"py":"self","fn":"always_ne_temporal_temporal"}]},
"ever_equal":      {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"float","fn":"ever_eq_tfloat_float","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_eq_temporal_temporal"}]},
"ever_not_equal":  {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"float","fn":"ever_ne_tfloat_float","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_ne_temporal_temporal"}]},
"temporal_equal":    {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"teq_tfloat_float","argTransform":"scalarCast"}]},
"temporal_not_equal":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"tne_tfloat_float","argTransform":"scalarCast"}]},
"at":   {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"tfloat_at_value","argTransform":"scalarCast"},
  {"py":"IntSet",    "coerce":"to_floatset",    "via":"super"},
  {"py":"IntSpan",   "coerce":"to_floatspan",   "via":"super"},
  {"py":"IntSpanSet","coerce":"to_floatspanset","via":"super"}]},
"minus":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"tfloat_minus_value","argTransform":"scalarCast"},
  {"py":"IntSet",    "coerce":"to_floatset",    "via":"super"},
  {"py":"IntSpan",   "coerce":"to_floatspan",   "via":"super"},
  {"py":"IntSpanSet","coerce":"to_floatspanset","via":"super"}]}

// dispatch.temporal.tint
"always_equal":    {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"always_eq_tint_int","argTransform":"scalarValue"},
  {"py":"self","fn":"always_eq_temporal_temporal"}]},
"always_not_equal":{"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"always_ne_tint_int","argTransform":"scalarValue"},
  {"py":"self","fn":"always_ne_temporal_temporal"}]},
"ever_equal":      {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"ever_eq_tint_int","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_eq_temporal_temporal"}]},
"ever_not_equal":  {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"ever_ne_tint_int","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_ne_temporal_temporal"}]},
"temporal_equal":    {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"teq_tint_int","argTransform":"scalarValue"}]},
"temporal_not_equal":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int","fn":"tne_tint_int","argTransform":"scalarValue"}]},
"at":   {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"tint_at_value","argTransform":"scalarCast"},
  {"py":"FloatSet",    "coerce":"to_intset",    "via":"super"},
  {"py":"FloatSpan",   "coerce":"to_intspan",   "via":"super"},
  {"py":"FloatSpanSet","coerce":"to_intspanset","via":"super"}]},
"minus":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"int|float","fn":"tint_minus_value","argTransform":"scalarCast"},
  {"py":"FloatSet",    "coerce":"to_intset",    "via":"super"},
  {"py":"FloatSpan",   "coerce":"to_intspan",   "via":"super"},
  {"py":"FloatSpanSet","coerce":"to_intspanset","via":"super"}]}

// dispatch.temporal.tbool  (ONLY these; no always_/ever_ editorial)
"temporal_equal":    {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"bool","fn":"teq_tbool_bool","argTransform":"scalarValue"}]},
"temporal_not_equal":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"bool","fn":"tne_tbool_bool","argTransform":"scalarValue"}]},
"at":   {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"bool","fn":"tbool_at_value","argTransform":"scalarValue"}]},
"minus":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"bool","fn":"tbool_minus_value","argTransform":"scalarValue"}]}

// dispatch.temporal.ttext
"always_equal":    {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"always_eq_ttext_text","argTransform":"scalarValue"},
  {"py":"self","fn":"always_eq_temporal_temporal"}]},
"always_not_equal":{"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"always_ne_ttext_text","argTransform":"scalarValue"},
  {"py":"self","fn":"always_ne_temporal_temporal"}]},
"ever_equal":      {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"ever_eq_ttext_text","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_eq_temporal_temporal"}]},
"ever_not_equal":  {"fallback":"raise","result":"bool_gt0","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"ever_ne_ttext_text","argTransform":"scalarValue"},
  {"py":"self","fn":"ever_ne_temporal_temporal"}]},
"temporal_equal":    {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"teq_ttext_text","argTransform":"scalarValue"}]},
"temporal_not_equal":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"tne_ttext_text","argTransform":"scalarValue"}]},
"at":   {"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"ttext_at_value","argTransform":"scalarValue"},
  {"py":"list[str]","fn":"temporal_at_values","argTransform":"textsetMake"}]},
"minus":{"fallback":"super","result":"temporal","dispatch":[
  {"py":"scalar","scalarType":"str","fn":"ttext_minus_value","argTransform":"scalarValue"},
  {"py":"list[str]","fn":"temporal_minus_values","argTransform":"textsetMake"}]}
```

Every `fn`, `scalarType`, `coerce`, `argTransform`, `fallback`, `result`
above is copied from the verbatim hand-written method bodies (extracted by
AST, not summarised). This is the SoT for the D1 extension; the consumer
side (PyMEOS #95) is being extended to the same vocabulary in lock-step.
