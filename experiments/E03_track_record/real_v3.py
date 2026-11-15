"""X5 (review round): Manifold checks (a)-(d). Uses the derived first-buy ledger results/E03/real_claims_main.csv.gz
(168,701 claims, 28,704 users); users with >= MIN claims as in real.py.
    uv run python -I experiments/E03_track_record/real_v3.py
Outputs: results/E03/real_v3_summary.json, real_v3_stability.csv, real_v3_horizon.csv
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata, spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import real
from rules import claim_terms

OUT = real.OUT
df = pd.read_csv(OUT / "real_claims_main.csv.gz")
rng = np.random.default_rng(0)
STEP = 0.5
sig = lambda z: 1 / (1 + np.exp(-z))
pb = np.clip(df.p_before.values, 1e-3, 1 - 1e-3)
dirn = np.where(df.bet_yes.values, 1.0, -1.0)
y = df.y.values.astype(bool)
r_dir = sig(np.log(pb / (1 - pb)) + STEP * dirn)  # c shifted by a fixed log-odds step in the direction of the trade
t_orig = claim_terms(df.p_after.values, y, df.p_before.values)
t_dir = claim_terms(r_dir, y, df.p_before.values)
df["acc_dir"] = (df.bet_yes.values == y).astype(float)  # original ACC: side bet on won
pa = df.p_after.values
df["acc_price"] = np.where(np.abs(pa - 0.5) < 1e-12, 0.5, ((pa > 0.5) == y).astype(float))  # post-bet price thresholded at 0.5
df["brier"], df["brier_c"], df["ig"], df["ig_dir"] = t_orig["brier"], t_orig["brier_c"], t_orig["ig"], t_dir["ig"]
df["fav_dir"] = np.where(df.bet_yes, df.p_before, 1 - df.p_before)  # crowd prob of the side the user bet on
df["fav_price"] = np.maximum(df.p_before, 1 - df.p_before)  # crowd prob of the side the market favours
df["nc_dir"] = (df.fav_dir >= 0.9).astype(float); df["nc_price"] = (df.fav_price >= 0.9).astype(float)
RUL = ["ACC_dir", "ACC_price", "BRIER", "IG", "IG-SUM", "BSS", "DIR-IG", "DIR-IG-SUM"]


def user_scores(u, n_u, w, d):
    """weighted per-user scores; w = claim weights (0/1 for halves, multiplicities for the market bootstrap)."""
    S = lambda x: np.bincount(u, weights=w * x, minlength=n_u)
    cnt = S(np.ones(len(u)))
    with np.errstate(invalid="ignore", divide="ignore"):
        return {"ACC_dir": S(d.acc_dir.values) / cnt, "ACC_price": S(d.acc_price.values) / cnt, "BRIER": -S(d.brier.values) / cnt,
                "IG": S(d.ig.values) / cnt, "IG-SUM": S(d.ig.values), "BSS": 1 - S(d.brier.values) / S(d.brier_c.values),
                "DIR-IG": S(d.ig_dir.values) / cnt, "DIR-IG-SUM": S(d.ig_dir.values)}, cnt


def rho(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    return spearmanr(a[ok], b[ok]).correlation


def stability(MIN, nsplits=20, nboot=300):
    cnt = df.groupby("user").size()
    d = df[df.user.isin(cnt[cnt >= MIN].index)].reset_index(drop=True)
    users, u = np.unique(d.user.values, return_inverse=True)
    n_u = len(users)
    H = {R: np.zeros((nsplits + 1, 2, n_u)) for R in RUL}
    for s in range(nsplits + 1):
        if s < nsplits:
            order = np.lexsort((rng.random(len(d)), u))
        else:
            order = np.lexsort((d.time.values, u))
        pos = np.empty(len(d), int)
        uo = u[order]
        starts = np.r_[0, np.flatnonzero(np.diff(uo)) + 1]
        cum = np.arange(len(d)) - np.repeat(starts, np.diff(np.r_[starts, len(d)]))
        nn = np.repeat(np.diff(np.r_[starts, len(d)]), np.diff(np.r_[starts, len(d)]))
        half_o = (cum % 2) if s < nsplits else (cum >= nn / 2).astype(int)
        pos[order] = half_o
        for h in (0, 1):
            sc, _ = user_scores(u, n_u, (pos == h).astype(float), d)
            for R in RUL:
                H[R][s, h] = sc[R]
    B = rng.integers(0, n_u, (nboot, n_u))
    rows = []
    for R in RUL:
        rr = np.mean([rho(H[R][s, 0], H[R][s, 1]) for s in range(nsplits)])
        bt = [np.mean([rho(H[R][s, 0, b], H[R][s, 1, b]) for s in range(nsplits)]) for b in B]  # CI over ALL 20 splits
        tt = rho(H[R][-1, 0], H[R][-1, 1]); tb = [rho(H[R][-1, 0, b], H[R][-1, 1, b]) for b in B]
        rows.append(dict(min_claims=MIN, n_users=n_u, n_claims=len(d), rule=R, random_split=rr, random_lo=np.percentile(bt, 2.5),
                         random_hi=np.percentile(bt, 97.5), temporal=tt, temporal_lo=np.percentile(tb, 2.5),
                         temporal_hi=np.percentile(tb, 97.5)))
    return rows, d, users, u


rows, summ = [], {}
for MIN in (20, 50, 100):
    r, d, users, u = stability(MIN)
    rows += r
    if MIN == 20:
        d20, users20, u20 = d, users, u
pd.DataFrame(rows).round(3).to_csv(OUT / "real_v3_stability.csv", index=False)

# signature (users >= 20 claims). ACC rank minus IG rank vs near-certain share; variants by orientation.
n_u = len(users20)
def signature(w, which):
    sc, cnt = user_scores(u20, n_u, w, d20)
    nc = np.bincount(u20, weights=w * d20[which[2]].values, minlength=n_u) / cnt
    ok = cnt > 0
    a, g = sc[which[0]][ok], sc[which[1]][ok]
    gap = rankdata(a) - rankdata(g)
    return spearmanr(nc[ok], gap).correlation

VAR = {"original (direction ACC, direction favourite share, mean IG)": ("ACC_dir", "IG", "nc_dir"),
       "price-thresholded ACC, direction favourite share": ("ACC_price", "IG", "nc_dir"),
       "price-thresholded ACC, price favourite share": ("ACC_price", "IG", "nc_price"),
       "direction ACC, price favourite share": ("ACC_dir", "IG", "nc_price"),
       "direction ACC vs DIR-IG, direction share": ("ACC_dir", "DIR-IG", "nc_dir")}
ones = np.ones(len(d20))
mk, mi = np.unique(d20.market.values, return_inverse=True)
sigout = {}
for name, wh in VAR.items():
    point = signature(ones, wh)
    ub = []
    for _ in range(300):
        us = rng.integers(0, n_u, n_u)  # user bootstrap: reweight claims by user multiplicity
        mult = np.bincount(us, minlength=n_u).astype(float)
        sc, cnt = user_scores(u20, n_u, np.ones(len(d20)), d20)
        nc = np.bincount(u20, weights=d20[wh[2]].values, minlength=n_u) / cnt
        a, g = rankdata(np.repeat(sc[wh[0]], 1)[us]), rankdata(sc[wh[1]][us])
        ub.append(spearmanr(nc[us], a - g).correlation)
    mb = []
    for _ in range(300):  # market-cluster bootstrap: resample markets with replacement
        mm = np.bincount(rng.integers(0, len(mk), len(mk)), minlength=len(mk)).astype(float)
        mb.append(signature(mm[mi], wh))
    sigout[name] = {"rho": float(point), "user_boot_ci": [float(np.percentile(ub, 2.5)), float(np.percentile(ub, 97.5))],
                    "market_cluster_boot_ci": [float(np.percentile(mb, 2.5)), float(np.percentile(mb, 97.5))],
                    "n_users": n_u, "n_markets": len(mk)}
summ["signature"] = sigout

# (d) horizon: time from claim to resolution, by claim-time block (quartiles of claim time, as in real_recal.py)
res_t = {}
for m in df.market.unique():
    try:
        res_t[m] = json.loads((real.DATA / "markets" / f"{m}.json").read_text()).get("resolutionTime")
    except Exception:
        res_t[m] = None
df["res_t"] = df.market.map(res_t).astype(float)
df["horizon_days"] = (df.res_t - df.time) / 86.4e6
cuts = np.quantile(df.time, [0, .25, .5, .75, 1])
df["blk"] = np.clip(np.searchsorted(cuts, df.time, side="right") - 1, 0, 3)
hz = []
for q in range(4):
    x = df[df.blk == q]
    mq = x.groupby("market").horizon_days.median()
    meds = []
    mk_q = x.market.unique()
    for _ in range(300):
        pick = rng.choice(mk_q, len(mk_q))
        meds.append(np.median(x.set_index("market").loc[pick].horizon_days.values))
    hz.append(dict(block=q, n_claims=len(x), n_markets=len(mk_q), horizon_median_days=x.horizon_days.median(),
                   median_ci_lo=np.percentile(meds, 2.5), median_ci_hi=np.percentile(meds, 97.5), horizon_mean_days=x.horizon_days.mean(),
                   p25=x.horizon_days.quantile(.25), p75=x.horizon_days.quantile(.75),
                   share_claims_horizon_gt_30d=float((x.horizon_days > 30).mean()),
                   claim_time_start=str(pd.to_datetime(cuts[q], unit="ms").date()), claim_time_end=str(pd.to_datetime(cuts[q + 1], unit="ms").date())))
pd.DataFrame(hz).round(2).to_csv(OUT / "real_v3_horizon.csv", index=False)
# block facts used by real_recal.py: resolved markets (t_end < block start) available for each fit
tend = df.groupby("market").time.max()
summ["fit_sets"] = {f"block{q}": {"markets_with_last_claim_before_block_start": int((tend < cuts[q]).sum()),
                                  "claims_in_those_markets": int(df.market.map(tend).lt(cuts[q]).sum())} for q in (1, 2, 3)}
summ["markets_total"] = int(df.market.nunique()); summ["claims_total"] = int(len(df))
summ["markets_missing_resolution_time"] = int(sum(v is None for v in res_t.values()))
summ["share_claims_is_limit"] = float(df.is_limit.mean())
summ["step_logodds"] = STEP
(OUT / "real_v3_summary.json").write_text(json.dumps(summ, indent=1))
print(json.dumps(summ, indent=1)); print(pd.DataFrame(rows).round(2).to_string(index=False)); print(pd.DataFrame(hz).round(2).to_string(index=False))
