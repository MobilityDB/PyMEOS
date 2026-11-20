#!/usr/bin/env python3
# Copyright (c) 2016-2026, Université libre de Bruxelles and PyMEOS
# contributors. Licensed under the PostgreSQL License (see LICENSE).
#
# Catalog-driven generator of the classes of a MEOS family the PyMEOS core
# has no module for.
#
# BINDING-HEADER-PARSE-OK: this generator reads only the meos-idl.json catalog
# and the signatures pymeos_cffi exports, never a MEOS header.
#
# The classes are the catalog's own: the nodes of the Value companion of the
# object model whose `conditional` names the family (RASTER gives Raster,
# RaQuet and BandStats). Each class gets every method and operator
# objectModel.classes.<C> assigns it and every aggregate of the catalog over
# its values, as MEOS.NET's tools/objectgen.py projects them. A method is named
# snake(ooName), PyMEOS's case of the object model's language-neutral name. How
# each argument and answer crosses is read off the signature pymeos_cffi
# exports for the function: a struct pointer whose type is a class's cType
# crosses as that object's _inner, a list of them as a list of _inner, and an
# answer of a generated class is wrapped in it. A member no rule reads is
# reported and left out, never hand-written.
#
# Usage:
#   python3 tools/oo_codegen/classgen.py --idl <meos-idl.json> --family RASTER

from __future__ import annotations

import argparse
import json
import keyword
import os
import re
import sys
import typing
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from codegen import ROOT, format_mixin  # noqa: E402


def snake(oo_name: str) -> str:
    """The snake case of an ooName, as #_arg_token reads a C member name into a
    token: the inverse of how MEOS-API camel-cases it, a word starting at each
    capital and a run of capitals one word (``asHexWKB`` is ``as_hex_wkb``)."""
    words = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z0-9]+|[A-Z]+[0-9]*", oo_name)
    name = "_".join(w.lower() for w in words) if words else oo_name.lower()
    return name + "_" if keyword.iskeyword(name) else name


def clean(ctype: str) -> str:
    """A C type without its qualifiers and spaces, the key #collect matches on."""
    return re.sub(r"\b(const|struct)\b", "", ctype).replace(" ", "")


class Slot:
    """How one argument or answer of a pymeos_cffi function crosses, as #Method
    records an overload: the C type its annotation states, whether it is a list
    of them and whether it is optional."""

    def __init__(self, hint):
        """Read a pymeos_cffi annotation as #_arg_token reads a C member name."""
        self.optional = False
        self.is_list = False
        self.ctype = None
        # The annotation a scalar keeps, the Python type pymeos_cffi states.
        self.python = getattr(hint, "__name__", None) if hint in (int, float, bool, str, bytes) else "typing.Any"
        args = typing.get_args(hint)
        if typing.get_origin(hint) is typing.Union or type(hint).__name__ == "UnionType":
            rest = [a for a in args if a is not type(None)]
            self.optional = len(rest) < len(args)
            hint = rest[0] if len(rest) == 1 else hint
            args = typing.get_args(hint)
        if typing.get_origin(hint) is list and args:
            self.is_list = True
            hint = args[0]
            args = typing.get_args(hint)
        if typing.get_origin(hint) is typing.Annotated and len(args) > 1 and isinstance(args[1], str):
            self.ctype = clean(args[1])
            # Only a CFFI pointer needs a class: a string or a list the flat
            # layer already reads (`Annotated[str, 'char *']`) crosses as it is.
            self.raw = args[0].__name__ in ("_CDataBase", "CData")
            if args[0] is list and self.ctype.endswith("**"):
                self.is_list, self.raw, self.ctype = True, True, self.ctype[:-1]
        else:
            self.raw = False


class Model:
    """The catalog and pymeos_cffi together, as #collect reads the catalog."""

    def __init__(self, idl: dict, cffi, pymeos):
        """The catalog, pymeos_cffi and the PyMEOS core, whose classes and
        #create_temporal and #create_collection factories an answer reuses."""
        self.idl = idl
        self.cffi = cffi
        self.pymeos = pymeos
        self.om = idl["objectModel"]
        self.functions = {f["name"]: f for f in idl["functions"]}
        # A C type several classes share (Temporal for TInt, TFloat, ...) names
        # the class of its own name, the one the others descend from.
        self.class_of_ctype = {}
        for cls, spec in self.om["classes"].items():
            ctype = clean(spec.get("cType") or "")
            if ctype and (ctype + "*" not in self.class_of_ctype or cls == ctype):
                self.class_of_ctype[ctype + "*"] = cls

    def is_temporal(self, cls: str) -> bool:
        """Whether a class is of the temporal lattice, as #_family_of reads a
        temporal function's family."""
        return cls in self.om["lattice"]

    def is_collection(self, cls: str) -> bool:
        """Whether a class is of the Collection companion, a set, span or span set."""
        node = self.om["companions"]["Collection"]
        return cls in (node.get("nodes") or node)

    def family_classes(self, family: str) -> list[str]:
        """The classes of a family, read off the catalog as #_family_of reads a
        function's family: the Value companion nodes the family conditions."""
        nodes = self.om["companions"]["Value"]["nodes"]
        return sorted(cls for cls, node in nodes.items() if node.get("conditional") == family)

    def signature(self, fname: str):
        """The type hints and argument names pymeos_cffi exports for a function,
        the flat signature #emit_faithful_mixin calls through."""
        fn = getattr(self.cffi, fname, None)
        if fn is None:
            return None
        return typing.get_type_hints(fn, include_extras=True), fn.__code__.co_varnames[: fn.__code__.co_argcount]

    def aggregate_class(self, agg: dict, value_ctype: str) -> str | None:
        """The class of an aggregate, as #_family_of reads a function's family
        off its prefix: the leaf whose prefix is the SQL type of its values, else
        the class of the C type its transition takes them as."""
        sql = (agg.get("args") or [None])[0]
        for name, node in self.om["lattice"].items():
            if node.get("kind") == "leaf" and sql in (node.get("prefixes") or []):
                return name
        return self.class_of_ctype.get(clean(value_ctype))


class Generator:
    """The classes of one family, as #emit_faithful_mixin writes one mixin."""

    def __init__(self, model: Model, family: str):
        self.m = model
        self.family = family
        self.classes = model.family_classes(family)
        self.deferred: list[tuple[str, str, str]] = []

    def defer(self, cls: str, member: str, why: str) -> None:
        """Count a member left out, as #Stats counts a function not emitted."""
        self.deferred.append((cls, member, why))

    def held(self, slot: Slot) -> str | None:
        """The class a raw pointer slot holds, when this module emits it or the
        PyMEOS core defines it, as #_faithful_overloads unwraps an argument."""
        cls = self.m.class_of_ctype.get(slot.ctype or "") if slot.raw else None
        if cls and (cls in self.classes or hasattr(self.m.pymeos, cls)):
            return cls
        return None

    def argument(self, name: str, slot: Slot) -> tuple[str, str] | None:
        """(annotation, expression) of one argument, as #_faithful_overloads
        unwraps an argument to its _inner."""
        cls = self.held(slot)
        if cls and slot.is_list:
            expr = f"[x._inner for x in {name}]"
            return f"list[{cls}]", (f"{expr} if {name} is not None else None" if slot.optional else expr)
        if cls:
            return cls, (f"{name}._inner if {name} is not None else None" if slot.optional else f"{name}._inner")
        if slot.raw and slot.ctype and slot.ctype.endswith("*"):
            return None
        return slot.python, name

    def answer(self, hint, expr: str) -> str | None:
        """The expression of one answer, as #_result_return post-processes one:
        a class this module emits is wrapped in it, a temporal value and a
        collection as the PyMEOS core's factories wrap them, and another class
        of the core by its own constructor."""
        slot = Slot(hint)
        cls = self.held(slot)
        if cls in self.classes:
            return f"_wrap({cls}, {expr})"
        if cls and self.m.is_temporal(cls):
            return f"_TemporalFactory.create_temporal({expr})"
        if cls and self.m.is_collection(cls):
            return f"_CollectionFactory.create_collection({expr})"
        if cls:
            return f"_wrap(pymeos.{cls}, {expr})"
        if slot.raw and slot.ctype and slot.ctype.endswith("*"):
            return None
        return expr

    def returned(self, hints) -> tuple[str, str] | None:
        """(expression over ``_r``, annotation) of a function's answer."""
        ret = hints.get("return")
        if ret is None or ret is type(None):
            return "None", "None"
        if typing.get_origin(ret) is tuple:
            parts = [self.answer(h, f"_r[{i}]") for i, h in enumerate(typing.get_args(ret))]
            if any(p is None for p in parts):
                return None
            return "(" + ", ".join(parts) + ")", "tuple"
        one = self.answer(ret, "_r")
        if one is None:
            return None
        cls = self.m.class_of_ctype.get(Slot(ret).ctype or "")
        return one, (f"{cls} | None" if cls in self.classes else "typing.Any")

    def member(self, cls: str, entry: dict) -> dict | None:
        """One method or operator of the object model, as #emit_faithful_mixin
        writes one member: the receiver is the argument of the class's own type,
        the second for an operator the model reflects onto its right operand."""
        fname = entry["function"]
        sig = self.m.signature(fname)
        if sig is None:
            self.defer(cls, entry["ooName"], f"{fname} is not in pymeos_cffi")
            return None
        hints, names = sig
        receiver_ctype = clean(self.m.om["classes"][cls]["cType"]) + "*"
        at = 1 if entry.get("receiver") == "right" else 0
        receiver = names[at] if len(names) > at and Slot(hints.get(names[at])).ctype == receiver_ctype else None
        params, args = [], []
        for name in names:
            if name == receiver:
                args.append("self._inner")
                continue
            arg = self.argument(name, Slot(hints.get(name)))
            if arg is None:
                self.defer(cls, entry["ooName"], f"argument {name} of {fname}")
                return None
            params.append((name, arg[0]))
            args.append(arg[1])
        ret = self.returned(hints)
        if ret is None:
            self.defer(cls, entry["ooName"], f"answer of {fname}")
            return None
        return {
            "name": snake(entry["ooName"]),
            "static": receiver is None,
            "params": params,
            "call": f"{fname}({', '.join(args)})",
            "fname": fname,
            "args": args,
            "answer": ret[0],
            "returns": ret[1],
            "doc": f"MEOS function: {fname}",
        }

    def aggregates(self, cls: str) -> list[dict]:
        """Every aggregate of the catalog over the values of a class, a static
        method threading the transition from a NULL state into the final
        function, which frees the state, as #emit_faithful_mixin writes a member."""
        out, seen = [], set()
        for agg in self.m.idl.get("aggregates") or []:
            transition = (agg.get("transition") or {}).get("meos")
            final = (agg.get("final") or {}).get("meos")
            f = self.m.functions.get(transition or "")
            if not f or not final or len(f.get("params", [])) < 2:
                continue
            if self.m.aggregate_class(agg, f["params"][1]["canonical"]) != cls:
                continue
            name = snake(agg.get("altSqlName") or agg["sqlName"])
            if name in seen:
                continue
            seen.add(name)
            tsig, fsig = self.m.signature(transition), self.m.signature(final)
            if tsig is None or fsig is None:
                self.defer(cls, name, f"{transition} or {final} is not in pymeos_cffi")
                continue
            hints, names = tsig
            params, args = [], ["_state", "_v._inner"]
            for pname in names[2:]:
                arg = self.argument(pname, Slot(hints.get(pname)))
                if arg is None:
                    params = None
                    break
                params.append((pname, arg[0]))
                args.append(arg[1])
            ret = self.returned(fsig[0])
            if params is None or ret is None:
                self.defer(cls, name, f"{transition} / {final}")
                continue
            out.append(
                {
                    "name": name,
                    "static": True,
                    "params": [("values", f"list[{cls}]"), *params],
                    "aggregate": (transition, ", ".join(args), final),
                    "answer": ret[0],
                    "returns": ret[1],
                    "doc": f"Aggregate {agg['sqlName']}: MEOS {transition} over the values, then {final}",
                }
            )
        return out

    def dispatcher(self, cls: str, name: str, overloads: list[dict]) -> list[str] | None:
        """One method for the overloads of one name, as #emit_faithful_mixin
        writes an isinstance ladder: each overload is tried in turn on the type
        of the arguments where the overloads differ. Overloads no argument type
        tells apart are left out."""
        first = overloads[0]
        if any(o["static"] != first["static"] or len(o["params"]) != len(first["params"]) for o in overloads):
            self.defer(cls, name, "overloads of different shapes")
            return None
        names = [n for n, _ in first["params"]]
        differ = [i for i in range(len(names)) if len({o["params"][i][1] for o in overloads}) > 1]
        tests, seen = [], set()
        for o in overloads:
            parts = []
            for i in differ:
                ann = o["params"][i][1]
                if ann in ("int", "float"):
                    parts.append(f"isinstance({names[i]}, (int, float))")
                elif ann in ("bool", "str", "bytes") or ann in self.classes:
                    parts.append(f"isinstance({names[i]}, {ann})")
                elif ann != "typing.Any" and hasattr(self.m.pymeos, ann):
                    parts.append(f"isinstance({names[i]}, pymeos.{ann})")
                else:
                    parts = None
                    break
            key = " and ".join(parts) if parts else None
            if not key or key in seen:
                self.defer(cls, name, "overloads no argument type tells apart")
                return None
            seen.add(key)
            tests.append(key)
        params = ", ".join(names)
        head = f"def {name}({params})" if first["static"] else f"def {name}(self{', ' if params else ''}{params})"
        lines = ["    @staticmethod"] if first["static"] else []
        doc = "MEOS functions: " + ", ".join(o["fname"] for o in overloads)
        lines += [f"    {head} -> typing.Any:", f'        """{doc}"""']
        for test, o in zip(tests, overloads, strict=True):
            mapping = {old: new for (old, _), new in zip(o["params"], names, strict=True)}
            args = [re.sub(r"\b\w+\b", lambda w, mp=mapping: mp.get(w.group(0), w.group(0)), a) for a in o["args"]]
            lines += [
                f"        if {test}:",
                f"            _r = {o['fname']}({', '.join(args)})",
                f"            return {o['answer']}",
            ]
        lines.append(f"        raise TypeError(f'{name} of {cls} takes no {{type({names[differ[0]]}).__name__}}')")
        return lines

    def emit_member(self, m: dict) -> list[str]:
        """The lines of one member, as #emit_faithful_mixin lays out one."""
        params = ", ".join(f"{n}: {t}" for n, t in m["params"])
        head = f"def {m['name']}({params})" if m["static"] else f"def {m['name']}(self{', ' if params else ''}{params})"
        lines = ["    @staticmethod"] if m["static"] else []
        lines += [f"    {head} -> {m['returns']}:", f'        """{m["doc"]}"""']
        if "aggregate" in m:
            transition, args, final = m["aggregate"]
            lines += [
                "        _state = None",
                "        for _v in values:",
                f"            _state = {transition}({args})",
                f"        _r = {final}(_state)",
            ]
        else:
            lines.append(f"        _r = {m['call']}")
        lines.append(f"        return {m['answer']}")
        return lines

    def emit(self) -> str:
        """The module of the family's classes, as #emit_faithful_mixin writes a
        mixin; members of one name that no argument tells apart are left out."""
        out = [
            "# Code generated by tools/oo_codegen/classgen.py from meos-idl.json. DO NOT EDIT.",
            "from __future__ import annotations",
            "",
            "import typing",
            "",
            "from pymeos_cffi import *",
            "from pymeos_cffi.functions import _ffi",
            "",
            "import pymeos",
            "",
            "from ..factory import _CollectionFactory, _TemporalFactory",
            "",
            f"__all__ = {self.classes!r}",
            "",
            "",
            "def _wrap(cls, inner):",
            '    """The object of a class around a MEOS pointer, None for NULL."""',
            "    return None if inner is None or inner == _ffi.NULL else cls(_inner=inner)",
            "",
        ]
        for cls in self.classes:
            spec = self.m.om["classes"].get(cls, {})
            members: dict[str, list[dict]] = {}
            for entry in (spec.get("methods") or []) + (spec.get("operators") or []):
                if entry.get("ooExclude"):
                    continue
                m = self.member(cls, entry)
                if m:
                    members.setdefault(m["name"], []).append(m)
            for m in self.aggregates(cls):
                members.setdefault(m["name"], []).append(m)
            doc = (self.m.om["companions"]["Value"]["nodes"].get(cls) or {}).get("doc") or f"A MEOS {cls}."
            out += ["", f"class {cls}:", f'    """{doc}"""', "", '    __slots__ = ["_inner"]', ""]
            out += ["    def __init__(self, *, _inner):", "        self._inner = _inner", ""]
            for name in sorted(members):
                overloads = members[name]
                if len(overloads) > 1:
                    lines = self.dispatcher(cls, name, overloads)
                    if lines:
                        out += lines + [""]
                    continue
                out += self.emit_member(overloads[0]) + [""]
        return "\n".join(out) + "\n"


def main() -> int:
    """Write the module of a family, as #main of codegen.py writes a mixin."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--idl", default=os.environ.get("MEOS_IDL"), required="MEOS_IDL" not in os.environ)
    ap.add_argument("--family", default="RASTER")
    args = ap.parse_args()
    import pymeos_cffi

    import pymeos

    gen = Generator(Model(json.loads(Path(args.idl).read_text()), pymeos_cffi, pymeos), args.family)
    path = ROOT / "pymeos" / args.family.lower() / f"{args.family.lower()}.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_mixin(gen.emit(), path))
    print(f"{path.relative_to(ROOT)}: {len(gen.classes)} classes, {len(gen.deferred)} members left out")
    for cls, member, why in gen.deferred:
        print(f"  {cls}.{member}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
