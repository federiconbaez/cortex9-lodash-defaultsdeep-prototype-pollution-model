"""CLI: python -m lodash_ddeep_model <scenario.json> [--version 4.17.11|4.17.12]"""
from __future__ import annotations

import argparse
import json

from .lodash import VERSIONS
from .scenario import load, run_all


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="lodash_ddeep_model")
    ap.add_argument("scenario")
    ap.add_argument("--version", choices=VERSIONS)
    a = ap.parse_args(argv)
    r = run_all(load(a.scenario))
    print(json.dumps(r[a.version] if a.version else r, indent=2))
    return 0
