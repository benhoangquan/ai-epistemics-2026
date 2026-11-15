"""Item 5 (stretch, post hoc, 15 Nov): backtest a recalibrated-crowd baseline on the Manifold ledger.
Claims are bucketed by claim time into 4 equal-count time blocks; claims in block q>=1 (q=1..3) are scored against
p_before recalibrated by a map fitted only on claims whose MARKET's last observed claim is before the block start
(a proxy for 'resolved before'; resolution time is not in the derived ledger). Eligible claims = blocks 1-3.
    uv run python -I experiments/E03_track_record/real_recal.py
Outputs: results/E03/real_recal_summary.json, real_recal_stability.csv"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, str(Path(__file__).resolve().parent))
import real
from rules import RULES
OUT = real.OUT
df = pd.read_csv(OUT / "real_claims_main.csv.gz")
df["pb"] = df.p_before.clip(0.01, 0.99)
tm = df.groupby("market").time.max()
df["t_end"] = df.market.map(tm)
cuts = np.quantile(df.time, [0, .25, .5, .75, 1])
blk = np.clip(np.searchsorted(cuts, df.time, side="right") - 1, 0, 3)
df["blk"] = blk
info = {"n_claims_all": int(len(df)), "fit": {}}
for mode in ("logit", "iso"):
    cb = np.full(len(df), np.nan)
    for q in (1, 2, 3):
        past = (df.t_end < cuts[q]).values
        cur = (blk == q)
        if mode == "logit":
            z = np.log(df.pb / (1 - df.pb)).values
            m = LogisticRegression(C=1e6).fit(z[past, None], df.y.values[past])
            cb[cur] = m.predict_proba(z[cur, None])[:, 1]
            info["fit"][f"logit_block{q}"] = {"n_fit": int(past.sum()), "slope": float(m.coef_[0, 0]),
                                              "intercept": float(m.intercept_[0])}
        else:
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0.01, y_max=0.99).fit(df.pb.values[past], df.y.values[past].astype(float))
            cb[cur] = iso.predict(df.pb.values[cur])
            info["fit"][f"iso_block{q}"] = {"n_fit": int(past.sum())}
    df["cb_" + mode] = cb
el = df[df.blk >= 1].reset_index(drop=True)
info["n_claims_eligible"] = int(len(el))
def ll(c, y):
    c = np.clip(c, 1e-3, 1 - 1e-3)
    return float(np.mean(np.log2(np.where(y, c, 1 - c))))
info["baseline_mean_log2score_eligible_claims"] = {"raw_p_before": ll(el.p_before.values, el.y.values),
    "logit_recal": ll(el.cb_logit.values, el.y.values), "iso_recal": ll(el.cb_iso.values, el.y.values),
    "by_block_raw": {int(q): ll(el.p_before.values[el.blk == q], el.y.values[el.blk == q]) for q in (1, 2, 3)},
    "by_block_logit": {int(q): ll(el.cb_logit.values[el.blk == q], el.y.values[el.blk == q]) for q in (1, 2, 3)},
    "by_block_iso": {int(q): ll(el.cb_iso.values[el.blk == q], el.y.values[el.blk == q]) for q in (1, 2, 3)}}
print(json.dumps(info["baseline_mean_log2score_eligible_claims"], indent=1))
codes = pd.Index(sorted(df.topic.unique()))
rng = np.random.default_rng(0)


def run(variant, MIN):
    d = el.copy()
    if variant != "raw":
        d["p_before"] = d["cb_" + variant]
    cnt = d.groupby("user").size()
    d = d[d.user.isin(cnt[cnt >= MIN].index)].reset_index(drop=True)
    users, sc, stats = real.score(d, topic_codes=codes)
    S = pd.DataFrame(sc, index=users)
    uidx = {u: i for i, u in enumerate(users)}
    d["u"] = d.user.map(uidx)
    out = {"variant": variant, "min_claims": MIN, "n_users": len(users), "n_claims": len(d),
           "pop_mean_IG_bits": float(stats["eb_ig"]["mu"])}
    # split-half stability: mean of 10 random splits and temporal split, CI by bootstrap over users (200)
    B = rng.integers(0, len(users), (200, len(users)))
    st = {}
    for R in ("ACC", "BRIER", "IG", "IG-SUM", "BSS", "EB0-IG"):
        st[R] = {"rand": [], "temp": None}
    H = {R: [] for R in st}
    for s in range(11):
        dd = d.assign(o=rng.random(len(d))).sort_values(["u", "o"]) if s < 10 else d.sort_values(["u", "time"])
        pos = dd.groupby("u").cumcount().values
        n_u = dd.groupby("u").u.transform("size").values
        half = (pos % 2) if s < 10 else (pos >= n_u / 2).astype(int)
        pair = []
        for h in (0, 1):
            part = dd[half == h]
            uu, sch, _ = real.score(part, stats=stats, topic_codes=codes)
            pair.append({R: pd.Series(sch[R], index=uu).reindex(users).values for R in st})
        for R in st:
            H[R].append((pair[0][R], pair[1][R]))

    def rho(x, y):
        ok = np.isfinite(x) & np.isfinite(y)
        return spearmanr(x[ok], y[ok]).correlation
    for R in st:
        rr = np.mean([rho(*H[R][s]) for s in range(10)])
        bt = [rho(H[R][10][0][b], H[R][10][1][b]) for b in B]
        out[f"{R}_rand"] = float(rr)
        out[f"{R}_temp"] = float(rho(*H[R][10]))
        out[f"{R}_temp_ci"] = [float(np.percentile(bt, 2.5)), float(np.percentile(bt, 97.5))]
    pr = {R: rankdata(np.nan_to_num(S[R].values, nan=-np.inf)) / len(S) * 100 for R in ("ACC", "IG", "IG-SUM")}
    fav = np.where(d.bet_yes, d.p_before, 1 - d.p_before)
    nc = pd.Series(fav >= 0.9, index=d.index).groupby(d.user).mean().loc[users].values
    gap = pr["ACC"] - pr["IG"]
    bs = [spearmanr(nc[b], gap[b]).correlation for b in B]
    out["signature_rho"] = float(spearmanr(nc, gap).correlation)
    out["signature_ci"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out, S


res, scores = [], {}
for MIN in (20, 50):
    for v in ("raw", "logit", "iso"):
        o, S = run(v, MIN)
        res.append(o)
        scores[(v, MIN)] = S
    for v in ("logit", "iso"):  # agreement of user rankings with the raw-crowd ranking on the same claims
        a, b = scores[("raw", MIN)], scores[(v, MIN)]
        com = a.index.intersection(b.index)
        for o in res:
            if o["variant"] == v and o["min_claims"] == MIN:
                o["spearman_IG_vs_raw_IG"] = float(spearmanr(a.loc[com, "IG"], b.loc[com, "IG"]).correlation)
                o["spearman_IGSUM_vs_raw_IGSUM"] = float(spearmanr(a.loc[com, "IG-SUM"], b.loc[com, "IG-SUM"]).correlation)
info["results"] = res
(OUT / "real_recal_summary.json").write_text(json.dumps(info, indent=1))
pd.DataFrame(res).round(3).to_csv(OUT / "real_recal_stability.csv", index=False)
print(json.dumps(info["fit"], indent=1)); print(pd.DataFrame(res).round(3).T.to_string())
