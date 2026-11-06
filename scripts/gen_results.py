"""Regenerate results/ from fixtures/scenarios. Usage: gen_results.py <out_dir>"""
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from lodash_ddeep_model.lodash import VERSIONS  # noqa: E402
from lodash_ddeep_model.scenario import load, run_all  # noqa: E402


def main(out: str) -> int:
    o = Path(out)
    o.mkdir(parents=True, exist_ok=True)
    allr, buf = {}, io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["scenario", "version", "pollution", "constructor_guard_hits", "result"])
    for p in sorted((ROOT / "fixtures/scenarios").glob("*.json")):
        sc = load(p)
        r = run_all(sc)
        allr[sc["name"]] = r
        for v in VERSIONS:
            w.writerow([sc["name"], v, ";".join(r[v]["pollution"]), r[v]["constructor_guard_hits"],
                        json.dumps(r[v]["result"], sort_keys=True)])
    (o / "scenarios.csv").write_text(buf.getvalue())
    (o / "scenarios.json").write_text(json.dumps(allr, indent=1) + "\n")
    (o / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256((o / n).read_bytes()).hexdigest()}  {n}\n" for n in ("scenarios.csv", "scenarios.json")))
    print(f"wrote {len(allr)} scenarios to {o}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
