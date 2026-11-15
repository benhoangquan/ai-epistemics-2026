"""Summarize results/E05/episodes.jsonl: success per (model, level) and pooled, Wilson 95% CIs, per-arm stats,
bandit convergence (arm pulls in last 30 episodes), failure reasons. Writes results/E05/summary.json / summary.md."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
import math
ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / "results" / "E05"
LV = ["G0", "G1", "G2", "G3", "G4"]
def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
eps = [json.loads(l) for l in (RES / "episodes.jsonl").read_text().splitlines() if l.strip()]
out = {}; md = []
def row(name, rs):
    k = sum(r["success"] for r in rs); n = len(rs); lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": k / n if n else None, "lo": lo, "hi": hi}
md.append("| group | level | k/n | rate | 95% Wilson |\n|---|---|---|---|---|")
for m in sorted({e["model"] for e in eps}) + ["pooled"]:
    for lv in LV:
        rs = [e for e in eps if e["level"] == lv and (m == "pooled" or e["model"] == m)]
        r = row(m, rs); out[f"{m}|{lv}"] = r
        md.append(f"| {m} | {lv} | {r['k']}/{r['n']} | {r['rate']:.2f} | [{r['lo']:.2f}, {r['hi']:.2f}] |" if r['n'] else f"| {m} | {lv} | 0/0 | | |")
md.append("\nPer arm (pooled models): level, arm: k/n\n")
for lv in LV:
    c = defaultdict(lambda: [0, 0])
    for e in eps:
        if e["level"] == lv: c[e["arm"]][0] += e["success"]; c[e["arm"]][1] += 1
    md.append(f"- {lv}: " + ", ".join(f"{a} {k}/{n}" for a, (k, n) in sorted(c.items(), key=lambda x: -x[1][1])))
    out[f"arms|{lv}"] = dict(c)
md.append("\nBandit convergence: most-pulled arms in the last 30 episodes per (model, level), with success\n")
for m in sorted({e["model"] for e in eps}):
    for lv in LV:
        rs = [e for e in eps if e["model"] == m and e["level"] == lv][-30:]
        c = Counter(e["arm"] for e in rs); s = Counter(e["arm"] for e in rs if e["success"])
        md.append(f"- {m} {lv}: " + ", ".join(f"{a} {s[a]}/{n}" for a, n in c.most_common(3)))
md.append("\nFailure modes (all episodes): ")
fm = Counter()
for e in eps:
    fm["parse_fail" if not e.get("parse_ok") else "not_hidden" if not e["hidden"] else "detected" if not e["success"] else "success"] += 1
    fm["refusal"] += bool(e.get("refusal")); fm["api_error"] += "error" in e
md.append(json.dumps(dict(fm))); out["failure_modes"] = dict(fm)
md.append("\nSuccesses at G2-G3 by timing: " + json.dumps(dict(Counter(e.get("timing") for e in eps if e["level"] in ("G2", "G3") and e["success"]))))
md.append("Total cost in episodes.jsonl (non-cached): $%.4f; episodes %d" % (sum(e.get("cost", 0) or 0 for e in eps), len(eps)))
(RES / "summary.json").write_text(json.dumps(out, indent=1)); (RES / "summary.md").write_text("\n".join(md) + "\n"); print("\n".join(md))
