"""Scenario = target spec + list of JSON sources, run under both versions."""
from __future__ import annotations

import json
from pathlib import Path

from .lodash import VERSIONS, Lodash
from .realm import Realm, to_py


def load(path) -> dict:
    return json.loads(Path(path).read_text())


def build_target(r: Realm, spec: dict):
    t = r.from_json(spec.get("json", {}), "target")
    t.label = "target"
    fn = spec.get("own_constructor_function")
    if fn:
        t.define("constructor", r.new_function(fn))
    return t


def run_one(sc: dict, version: str) -> dict:
    r = Realm()
    lo = Lodash(r, version)
    t = build_target(r, sc.get("target", {}))
    srcs = [r.from_json(s, f"src{i}") for i, s in enumerate(sc["sources"])]
    lo.defaults_deep(t, *srcs)
    return {"pollution": r.pollution(), "result": to_py(t),
            "constructor_guard_hits": sum("function guard" in x for x in lo.trace), "trace": lo.trace}


def run_all(sc: dict) -> dict:
    return {v: run_one(sc, v) for v in VERSIONS}
