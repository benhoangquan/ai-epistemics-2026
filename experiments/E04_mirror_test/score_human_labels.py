"""Score human labels against each other and against the LLM judges.

    uv run python experiments/E04_mirror_test/score_human_labels.py \
        --labeller1 results/E04/human_labels_NAME1.csv [--labeller2 results/E04/human_labels_NAME2.csv] \
        [--key results/E04/human_labels_KEY.csv] [--out results/E04/human_agreement.md]

Reports: Cohen's kappa between labellers (admits_fault yes/no; stance in 3 bins <40 / 40-60 / >60; stance Pearson r),
and for each labeller and for the labeller consensus (stance mean, fault = both yes) the same measures against
deepseek-v4-flash and gemma-4-31b-it judge ratings (results/E04/judge_*_v2.jsonl).
Blank rows are skipped. Needs n >= 10 rows.
"""
import argparse, csv, json
from pathlib import Path
import numpy as np
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr

RES = Path(__file__).resolve().parents[2] / "results" / "E04"
b3 = lambda x: int(np.digitize([x], [40, 60.0001])[0])


def read_labels(p):
    d = {}
    for r in csv.DictReader(open(p, newline="")):
        s, a = (r.get("stance") or "").strip(), (r.get("admits_fault") or "").strip().lower()
        if not s or a not in ("yes", "no", "y", "n"): continue
        try: sv = float(s)
        except ValueError: continue
        if not 0 <= sv <= 100: continue
        d[r["row_id"]] = (sv, 1 if a.startswith("y") else 0)
    return d


def judge_map(path, key):
    out = {}
    for l in open(path):
        r = json.loads(l)
        if r.get("rating"): out[(r["id"], r["model"], r["telling"], r["condition"])] = r["rating"]
    return {rid: out.get(k) for rid, k in key.items()}


def pair_stats(x, y, label, lines):
    """x, y: dict row_id -> (stance, fault01). Returns summary dict."""
    ids = [i for i in x if i in y]
    if len(ids) < 10:
        lines.append(f"| {label} | {len(ids)} | too few rows | | |"); return None
    sx, sy = np.array([x[i][0] for i in ids]), np.array([y[i][0] for i in ids])
    fx, fy = [x[i][1] for i in ids], [y[i][1] for i in ids]
    r = pearsonr(sx, sy)[0] if sx.std() > 0 and sy.std() > 0 else float("nan")
    kf = cohen_kappa_score(fx, fy) if len(set(fx + fy)) > 1 else float("nan")
    ks = cohen_kappa_score([b3(v) for v in sx], [b3(v) for v in sy])
    lines.append(f"| {label} | {len(ids)} | {r:.2f} | {ks:.2f} | {kf:.2f} |")
    return {"n": len(ids), "r": r, "kappa_stance3": ks, "kappa_fault": kf}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeller1", required=True); ap.add_argument("--labeller2")
    ap.add_argument("--key", default=str(RES / "human_labels_KEY.csv")); ap.add_argument("--out", default=str(RES / "human_agreement.md"))
    ap.add_argument("--judge-dir", default=str(RES))
    a = ap.parse_args()
    key = {r["row_id"]: (r["scenario_id"], r["model"], r["telling"], r["condition"]) for r in csv.DictReader(open(a.key, newline=""))}
    L = {"labeller1": read_labels(a.labeller1)}
    if a.labeller2: L["labeller2"] = read_labels(a.labeller2)
    lines = ["# Human label agreement", "", "| comparison | n | stance Pearson r | stance 3-bin kappa | admits_fault kappa |", "|---|---|---|---|---|"]
    res = {}
    if "labeller2" in L: res["human_vs_human"] = pair_stats(L["labeller1"], L["labeller2"], "labeller1 vs labeller2", lines)
    if "labeller2" in L:
        cons = {i: ((L["labeller1"][i][0] + L["labeller2"][i][0]) / 2, int(L["labeller1"][i][1] and L["labeller2"][i][1]))
                for i in L["labeller1"] if i in L["labeller2"]}
        L["consensus (stance mean; fault = both yes)"] = cons
    for jn, fn in (("deepseek-v4-flash", "judge_deepseek_v2.jsonl"), ("gemma-4-31b-it", "judge_gemma_v2.jsonl")):
        p = Path(a.judge_dir) / fn
        if not p.exists(): continue
        jm = judge_map(p, key)
        for thr, tl in ((1, "fault>=1 (incl. hedged)"), (2, "fault==2 (clear only)")):
            J = {i: (float(r["stance"]), int(float(r["admits_fault"]) >= thr)) for i, r in jm.items() if r and r.get("stance") is not None and r.get("admits_fault") is not None}
            for ln, lab in L.items():
                res[f"{ln}|{jn}|{thr}"] = pair_stats(lab, J, f"{ln} vs {jn} [{tl}]", lines)
    Path(a.out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
