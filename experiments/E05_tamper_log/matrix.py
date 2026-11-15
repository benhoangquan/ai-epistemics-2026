"""Deterministic attack x guarantee matrix. No model calls.

    uv run python experiments/E05_tamper_log/matrix.py

Writes results/E05/matrix.json, matrix.csv, matrix.md. Cell = fraction of the 40 instances (20 traces x 2
variants: forbidden tool on a cooperating server / on a local tool) in which the level's auditor raises a finding.
Also reports 'evades' = fraction where the forbidden action is hidden AND the auditor passes (attack succeeds)."""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(HERE))
from attacks import plan_for, run_tamper, scripted_attacks  # noqa: E402
from auditor import LEVELS, audit, hidden  # noqa: E402

RES = ROOT / "results" / "E05"


def variants(tr):
    for name, srv in (("coop", None), ("local", "local")):
        t = copy.deepcopy(tr)
        if srv is None:
            f = next(s for s in t["steps"] if s["forbidden"])
            if f["server"] == "local":
                f["server"] = "files.corp.example"
        else:
            for s in t["steps"]:
                if s["forbidden"]:
                    s["server"] = "local"
        yield name, t


def main():
    traces = [json.loads(l) for l in (RES / "traces.jsonl").read_text().splitlines() if l.strip()]
    out = {}
    for a in scripted_attacks():
        cells = {v: {lv: {"det": 0, "evade": 0, "n": 0} for lv in LEVELS} for v in ("coop", "local", "all")}
        napp = 0
        for tr in traces:
            for vn, t in variants(tr):
                coop = {s["server"] for s in t["steps"] if s["server"] != "local"}
                res = run_tamper(t, plan_for(a, t), coop)
                if res["errors"]:
                    continue
                napp += 1
                hid = hidden(res["bundle"], t["markers"])
                for lv in LEVELS:
                    d = bool(audit(res["bundle"], res["world"], lv))
                    for key in (vn, "all"):
                        c = cells[key][lv]
                        c["n"] += 1; c["det"] += d; c["evade"] += (hid and not d)
        out[a["key"]] = {"label": a["label"], "timing": a["timing"], "n_applicable": napp, "cells": cells}
    (RES / "matrix.json").write_text(json.dumps(out, indent=1))
    rows = ["attack,variant," + ",".join(f"{lv}_detect,{lv}_evade" for lv in LEVELS)]
    md = ["| attack (timing) | n | " + " | ".join(LEVELS) + " |", "|---|---|" + "---|" * len(LEVELS)]
    for k, v in out.items():
        for vn in ("coop", "local", "all"):
            rows.append(f"{k},{vn}," + ",".join(
                f"{c['det']/max(c['n'],1):.2f},{c['evade']/max(c['n'],1):.2f}" for c in (v['cells'][vn][lv] for lv in LEVELS)))
        md.append(f"| {k} ({v['timing']}) | {v['n_applicable']} | " + " | ".join(
            f"{v['cells']['all'][lv]['det']/max(v['cells']['all'][lv]['n'],1):.2f}" for lv in LEVELS) + " |")
    (RES / "matrix.csv").write_text("\n".join(rows) + "\n")
    (RES / "matrix.md").write_text("Detection rate (all 40 instances; coop/local split in matrix.csv)\n\n" + "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
