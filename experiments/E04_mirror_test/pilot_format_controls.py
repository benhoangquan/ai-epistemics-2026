"""Format controls on PILOT data (no API calls): (1) multi-option drafts; writes results/E04/pilot_format_controls.md."""
import re, numpy as np
from common import RES, read_jsonl, boot_ci, fmt_ci
import json
MULTI = re.compile(r"\boption\s*(?:\d|[a-c]\b|one|two|three)|\bversion\s*(?:\d|[a-c]\b)|\b(?:two|three|a few|several)\s+(?:versions|options|drafts|alternatives)|\balternative(?:s)?\b[^\n]{0,20}(?:message|version|draft)|\bhere are (?:two|three|a few|some)\b", re.I)
scs = {s["id"]: s for s in read_jsonl(RES / "scenarios.jsonl")}
dr = read_jsonl(RES / "drafts.jsonl")
out = ["# Pilot format controls (no API calls)\n", "Source: drafts.jsonl (pilot, deepseek-v4-flash judge). Multi-option = regex `MULTI` in pilot_format_controls.py.\n",
       "## 1. Multi-option drafts\n", "| drafter | multi-option drafts | mirror bias ambiguous, all (n) | excluding scenarios with a multi-option draft (n) | paired: mean stance of multi vs single drafts |\n|---|---|---|---|---|"]
res = {}
for m in ("gemma-4-31b-it", "glm-5.3-flash"):
    rows = [r for r in dr if r["model"] == m]
    nm = sum(bool(MULTI.search(r["draft"])) for r in rows)
    by = {}
    for r in rows:
        if r["rating"] and scs[r["id"]]["design"] == "ambiguous":
            by.setdefault(r["id"], {})[r["telling"]] = r
    allb = [d["A"]["rating"]["stance"] + d["B"]["rating"]["stance"] - 100 for d in by.values() if len(d) == 2]
    nomb = [d["A"]["rating"]["stance"] + d["B"]["rating"]["stance"] - 100 for d in by.values() if len(d) == 2 and not MULTI.search(d["A"]["draft"]) and not MULTI.search(d["B"]["draft"])]
    ms = [r["rating"]["stance"] for r in rows if r["rating"] and MULTI.search(r["draft"])]
    ss = [r["rating"]["stance"] for r in rows if r["rating"] and not MULTI.search(r["draft"])]
    res[m] = {"multi": nm, "n": len(rows), "all": boot_ci(allb), "n_all": len(allb), "nomulti": boot_ci(nomb), "n_nomulti": len(nomb)}
    out.append(f"| {m} | {nm} of {len(rows)} | {fmt_ci(boot_ci(allb))} ({len(allb)}) | {fmt_ci(boot_ci(nomb))} ({len(nomb)}) | multi {np.mean(ms) if ms else float('nan'):.1f} (n={len(ms)}) vs single {np.mean(ss):.1f} (n={len(ss)}) |")
(RES / "pilot_format_controls.md").write_text("\n".join(out) + "\n")
(RES / "pilot_format_controls.json").write_text(json.dumps(res, indent=1, default=float))
print("\n".join(out))
