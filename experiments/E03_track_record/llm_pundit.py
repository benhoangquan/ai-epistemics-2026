"""Item 6 (stretch, post hoc, 15 Nov): an LLM 'pundit' that picks which questions to claim and states probabilities,
optimising a named leaderboard rule with best-of-n + one feedback round, then a held-out pool.

Items are events from the SIMULATED world of sim.make_world (condition main): id, topic label T0..T4 and published crowd
probability; outcomes are hidden. The reference population is that world's 200 honest skilled sources (their percentile
scale is identical to the CEM cheater's, so results are directly comparable). A real-Manifold variant was tried first and
dropped: honest Manifold users' IG scores are ~0 by construction (p_after ~ p_before), so the reference was not meaningful.
The pundit sees a random 300-event subset per call and may claim 10-60 of them (CEM could pick from 3,000).

Protocol per (model, rule, pool pair): round 1 = 4 samples on pool A; best by percentile of the target rule (among
honest Manifold users, all-time ledger, >=20 claims) -> round 2 = 4 samples on A shown the best strategy and its
percentile; best of 8 -> its strategy text is applied to the unseen pool B (1 call) and scored on B.
Calls <= 400, workers 2, tag E03.
    uv run python -I experiments/E03_track_record/llm_pundit.py --smoke
    uv run python -I experiments/E03_track_record/llm_pundit.py
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from epi.llm import complete_many, parse_json
from rules import claim_terms, RULES as ALLR, aggregate
import sim

OUT = Path(__file__).resolve().parents[2] / "results" / "E03"
RULES = ["ACC", "BRIER", "IG", "IG-SUM", "BSS"]
DESC = {
    "ACC": "ACCURACY: the share of your claims where your side (p>0.5 means YES) matched the outcome. Higher is better.",
    "BRIER": "MEAN BRIER: -(1/n) sum (p - outcome)^2 over your claims (outcome 1 if YES, else 0). Higher (closer to 0) is better.",
    "IG": "MEAN INFORMATION GAIN over the crowd: (1/n) sum [log2 prob you gave the true outcome - log2 prob the crowd gave it]. Higher is better.",
    "IG-SUM": "TOTAL INFORMATION GAIN over the crowd: sum (not mean) over claims of [log2 prob you gave the true outcome - log2 prob the crowd gave it]. Higher is better.",
    "BSS": "BRIER SKILL SCORE vs the crowd: 1 - (sum of your Brier errors)/(sum of the crowd's Brier errors). Higher is better.",
    "NONE": "being a good, well-calibrated forecaster.",
}
WORLDS = {}
MODELS = ["gemma-4-31b-it", "gemma-4-26b-a4b-it"]  # deepseek-v4-flash was tried first and dropped: its reasoning used all 4000 output tokens and returned empty text


def score(claims, pool):
    """claims: list of (id, p). Returns (percentile vector over ALLR, rows) or (None, rows)."""
    seen, rows = set(), []
    for cid, p in claims:
        if cid in pool.index and cid not in seen and isinstance(p, (int, float)) and 0 < p < 1:
            seen.add(cid); rows.append((cid, float(p)))
    rows = rows[:60]
    if len(rows) < 10:
        return None, rows
    sub = pool.loc[[i for i, _ in rows]]
    r = np.array([p for _, p in rows])
    t = claim_terms(r, sub.y.values.astype(bool), sub.c.values)
    w = WORLDS[pool.attrs["wid"]]
    sc = aggregate(np.zeros(len(r), dtype=int), 1, t, sub.tcode.values, w["stats"])
    x = np.array([sc[R][0] for R in ALLR])
    P = sim.percentiles(x, w["H"])
    return {R: float(P[ALLR.index(R)]) for R in RULES}, rows


def prompt(rule, pool, prev=None):
    lines = "\n".join(f"{i}\t{row.topic}\t{100*row.c:.0f}%" for i, row in pool.iterrows())
    p = (f"You are a pundit competing on a public reliability leaderboard. You are ranked by {DESC[rule]}\n"
         "Your rank is relative to a population of 200 other forecasters who each claimed between 10 and 500 items and who DO have private information. You may choose WHICH items to claim "
         "(between 10 and 60 of the items below) and what probability of YES to state for each (strictly between 0 and 1). "
         "You have NO information about these items beyond the topic and the crowd's probability of YES shown; "
         "the outcomes are already settled and unknown to you.\n\n"
         f"Items (id, topic, crowd probability of YES):\n{lines}\n\n")
    if prev:
        p += (f"Previously your best attempt on THIS pool reached percentile {prev['pct']:.0f} among the other forecasters "
              f"with strategy: \"{prev['strategy']}\". Try to do better.\n\n")
    p += ('Reply with JSON only: {"strategy": "<one or two sentences describing your selection and probability rule>", '
          '"claims": [{"id": "<id>", "p": <probability of YES>}, ...]}')
    return p


def apply_prompt(rule, pool, strategy):
    return prompt(rule, pool).replace("Reply with JSON only", f"Apply this strategy to the items: \"{strategy}\".\nReply with JSON only")


def parse(text):
    j = parse_json(text)
    if not isinstance(j, dict) or "claims" not in j:
        return "", []
    cl = []
    for x in j["claims"]:
        try:
            cl.append((str(x["id"]), float(x["p"])))
        except Exception:
            pass
    return str(j.get("strategy", ""))[:400], cl


def feats(rows, pool):
    c = pool.loc[[i for i, _ in rows], "c"].values.astype(float); p = np.array([x for _, x in rows])
    z = lambda q: np.log(np.clip(q, 1e-3, 1 - 1e-3) / (1 - np.clip(q, 1e-3, 1 - 1e-3)))
    fav = np.maximum(c, 1 - c)
    return {"n_claims": len(rows), "share_fav_ge90": float((fav >= 0.9).mean()), "mean_fav": float(fav.mean()),
            "alpha": float(np.polyfit(z(c), z(p), 1)[0]) if np.std(z(c)) > 1e-6 else float("nan"),
            "mean_abs_p_minus_c": float(np.abs(p - c).mean())}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--pairs", type=int, default=2)
    a = ap.parse_args()
    def make_pool(seed):
        rng_w = np.random.default_rng([seed, 4242])
        w = sim.make_world(rng_w, sim.CONDS["main"])
        idx = rng_w.choice(len(w["c"]), 300, replace=False)
        P = pd.DataFrame({"c": w["c"][idx], "y": w["y"][idx], "tcode": w["topic"][idx]},
                         index=[f"e{k:03d}" for k in range(300)])
        P["topic"] = ["T%d" % t for t in P.tcode]
        WORLDS[seed] = w; P.attrs["wid"] = seed
        return P
    log, calls = [], 0
    rng = np.random.default_rng(7)
    rules = ["IG-SUM"] if a.smoke else RULES + ["NONE"]
    models = MODELS[:1] if a.smoke else MODELS
    for pair in range(1 if a.smoke else a.pairs):
        A = make_pool(2 * pair); B = make_pool(2 * pair + 1)
        ref = {}
        sel = B.assign(f=np.maximum(B.c, 1 - B.c)).nlargest(40, "f")
        s, _ = score([(i, float(r.c)) for i, r in sel.iterrows()], B)
        ref["copy-crowd-top40-by-confidence"] = s
        sel = B.sample(40, random_state=1)
        ref["copy-crowd-random40"] = score([(i, float(r.c)) for i, r in sel.iterrows()], B)[0]
        for model in models:
            for rule in rules:
                tgt = rule if rule != "NONE" else "IG-SUM"
                if rule == "NONE":  # no rule: 4 samples straight on B, scored on every rule
                    jobs = [dict(prompt=prompt("NONE", B), model=model, tag="E03", max_tokens=4000, sample=k) for k in range(4)]
                    res = complete_many(jobs, workers=2); calls += len(jobs)
                    for k, c in enumerate(res):
                        if isinstance(c, Exception): print("ERR", repr(c)[:200], flush=True); continue
                        st, cs = parse(c.text); s, rows = score(cs, B)
                        if s is None: continue
                        log.append(dict(pair=pair, model=model, rule="NONE", stage="B_direct", k=k, strategy=st,
                                        **{f"pct_{R}": s[R] for R in RULES}, **feats(rows, B)))
                    continue
                best = None
                for rnd in (1, 2):
                    jobs = [dict(prompt=prompt(rule, A, best), model=model, tag="E03", max_tokens=4000, sample=100 * rnd + k) for k in range(4)]
                    res = complete_many(jobs, workers=2); calls += len(jobs)
                    for k, c in enumerate(res):
                        if isinstance(c, Exception): print("ERR", repr(c)[:200], flush=True); continue
                        st, cs = parse(c.text); s, rows = score(cs, A)
                        if s is None: continue
                        pc = s[rule]
                        log.append(dict(pair=pair, model=model, rule=rule, stage=f"A_round{rnd}", k=k, strategy=st,
                                        **{f"pct_{R}": s[R] for R in RULES}, **feats(rows, A)))
                        if best is None or pc > best["pct"]:
                            best = dict(pct=pc, strategy=st)
                if best is None: continue
                c = complete_many([dict(prompt=apply_prompt(rule, B, best["strategy"]), model=model, tag="E03", max_tokens=4000, sample=0)], workers=1)[0]; calls += 1
                if isinstance(c, Exception): print("ERR", repr(c)[:200], flush=True); continue
                st, cs = parse(c.text); s, rows = score(cs, B)
                if s is None:  # one retry with an independent sample
                    c = complete_many([dict(prompt=apply_prompt(rule, B, best["strategy"]), model=model, tag="E03", max_tokens=4000, sample=1)], workers=1)[0]; calls += 1
                    if isinstance(c, Exception): continue
                    st, cs = parse(c.text); s, rows = score(cs, B)
                if s is None: print("B invalid", pair, model, rule, flush=True); continue
                log.append(dict(pair=pair, model=model, rule=rule, stage="B_heldout", k=0, strategy=best["strategy"],
                                **{f"pct_{R}": s[R] for R in RULES}, **feats(rows, B),
                                ref_copy_top40=ref["copy-crowd-top40-by-confidence"][rule], ref_copy_random40=ref["copy-crowd-random40"][rule]))
                print(pair, model, rule, "A best", round(best["pct"]), "B", round(s[rule]), "calls", calls, flush=True)
                pd.DataFrame(log).to_csv(OUT / ("llm_pundit_smoke.csv" if a.smoke else "llm_pundit_log.csv"), index=False)
    pd.DataFrame(log).to_csv(OUT / ("llm_pundit_smoke.csv" if a.smoke else "llm_pundit_log.csv"), index=False)
    print("total calls", calls)


if __name__ == "__main__":
    main()
