"""Part B: apply the ledger's scoring rules to real Manifold Markets bets.

Each user's first filled buy on a resolved YES/NO market is one claim: stated probability = market probability after
the bet, crowd prior = probability before, direction = bet side, outcome = resolution, time = bet time.

    uv run python -I experiments/E03_track_record/real.py               # main (first buy per user-market)
    uv run python -I experiments/E03_track_record/real.py --all-buys    # sensitivity: every filled buy
    uv run python -I experiments/E03_track_record/real.py --no-creator  # sensitivity: drop market creators' bets
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import RULES, aggregate, claim_terms, pop_stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "E03"
DATA = OUT / "data" / "manifold"
MIN_CLAIMS = 20

TOPICS = [  # first match wins; matched as substrings of the market's group slugs
    ("politics", ["politic", "election", "trump", "biden", "harris", "congress", "senate", "geopolit", "ukraine",
                  "russia", "israel", "gaza", "china", "uk-", "government", "president", "democrat", "republican"]),
    ("sports", ["sport", "nfl", "nba", "mlb", "nhl", "soccer", "football", "basketball", "baseball", "tennis",
                "chess", "esports", "olympic", "f1", "formula", "cricket", "boxing", "ufc", "golf"]),
    ("ai-tech", ["ai", "openai", "gpt", "llm", "technology", "tech", "anthropic", "google", "apple", "elon",
                 "twitter", "spacex", "software", "computing"]),
    ("econ-finance", ["econom", "stock", "crypto", "bitcoin", "finance", "business", "market", "inflation",
                      "fed", "interest-rate", "company"]),
    ("science-health", ["science", "space", "physics", "biology", "health", "covid", "medicine", "climate",
                        "superconduct", "lk-99", "math"]),
    ("culture", ["entertainment", "movie", "film", "music", "celebrit", "culture", "tv", "television", "award",
                 "oscar", "game", "book", "youtube", "internet"]),
    ("manifold-personal", ["manifold", "personal", "fun", "whale", "meta", "mana", "destiny", "dating"]),
]


def topic_of(slugs):
    s = " ".join(slugs or []).lower()
    for name, keys in TOPICS:
        if any(k in s for k in keys):
            return name
    return "other"


def load_claims(all_buys=False, no_creator=False):
    ids = json.loads((DATA / "sample_ids.json").read_text())
    rows, skipped = [], {"truncated": 0, "missing": 0, "bad_resolution": 0}
    for mid in ids:
        mf, bf = DATA / "markets" / f"{mid}.json", DATA / "bets" / f"{mid}.json"
        if not (mf.exists() and bf.exists()):
            skipped["missing"] += 1
            continue
        m, b = json.loads(mf.read_text()), json.loads(bf.read_text())
        if b["truncated"]:
            skipped["truncated"] += 1
            continue
        if m.get("resolution") not in ("YES", "NO"):
            skipped["bad_resolution"] += 1
            continue
        topic = topic_of(m.get("groupSlugs"))
        rt = m.get("resolutionTime") or 1e18
        for x in b["bets"]:
            if (x.get("amount", 0) <= 0 or x.get("isRedemption") or x.get("isAnte") or x.get("outcome") not in
                    ("YES", "NO") or x.get("probBefore") is None or x.get("probAfter") is None
                    or x["createdTime"] >= rt):
                continue
            if no_creator and x["userId"] == m["creatorId"]:
                continue
            rows.append((x["userId"], mid, x["createdTime"], x["outcome"] == "YES", float(x["probBefore"]),
                         float(x["probAfter"]), float(x["amount"]), bool(x.get("isApi", False)),
                         m["resolution"] == "YES", topic, x.get("limitProb") is not None,
                         (x["createdTime"] - m["createdTime"]) / max(rt - m["createdTime"], 1)))
    df = pd.DataFrame(rows, columns=["user", "market", "time", "bet_yes", "p_before", "p_after", "amount", "is_api",
                                     "y", "topic", "is_limit", "life_frac"])
    n_bets = len(df)
    if not all_buys:
        df = df.sort_values("time").groupby(["user", "market"], as_index=False).first()
    return df, skipped, n_bets


def score(df, stats=None, topic_codes=None):
    users, src = np.unique(df.user.values, return_inverse=True)
    t = claim_terms(df.p_after.values, df.y.values, df.p_before.values)
    t["acc"] = (df.bet_yes.values == df.y.values).astype(float)  # direction accuracy: the side you bet on won
    tc = topic_codes.get_indexer(df.topic.values) if topic_codes is not None else None
    if stats is None:
        stats = pop_stats(src, len(users), t, tc, len(topic_codes))
    return users, aggregate(src, len(users), t, tc, stats), stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-buys", action="store_true")
    ap.add_argument("--no-creator", action="store_true")
    ap.add_argument("--splits", type=int, default=20)
    ap.add_argument("--boot", type=int, default=500)
    a = ap.parse_args()
    tag = "main" + ("_allbuys" if a.all_buys else "") + ("_nocreator" if a.no_creator else "")
    df, skipped, n_bets = load_claims(a.all_buys, a.no_creator)
    n_all_claims = len(df)
    if tag == "main":  # compact derived ledger with hashed user ids (the raw API cache is ~0.7 GB)
        import hashlib
        h = {u: hashlib.sha256(u.encode()).hexdigest()[:12] for u in df.user.unique()}
        df.assign(user=df.user.map(h)).to_csv(OUT / "real_claims_main.csv.gz", index=False)
    cnt = df.groupby("user").size()
    keep = cnt[cnt >= MIN_CLAIMS].index
    d = df[df.user.isin(keep)].reset_index(drop=True)
    topic_codes = pd.Index(sorted(df.topic.unique()))
    users, sc, stats = score(d, topic_codes=topic_codes)
    S = pd.DataFrame(sc, index=users)

    # per-user descriptors
    g = d.groupby("user")
    fav = np.where(d.bet_yes, d.p_before, 1 - d.p_before)  # crowd prob of the side the user bet on
    d["near_certain"] = fav >= 0.9
    d["late"] = d.life_frac >= 0.9  # placed in the last 10% of the market's open-to-resolution lifetime
    desc = pd.DataFrame({"n": g.size(), "near_certain_share": g.near_certain.mean(), "api_share": g.is_api.mean(),
                         "late_share": g.late.mean(),
                         "mean_fav_prob": pd.Series(fav, index=d.index).groupby(d.user).mean()}).loc[users]
    U = pd.concat([desc, S], axis=1)
    U.rename(index=lambda u: __import__("hashlib").sha256(u.encode()).hexdigest()[:12]).to_csv(
        OUT / f"real_user_scores_{tag}.csv")

    rng = np.random.default_rng(0)
    # (a) split-half rank stability
    uidx = {u: i for i, u in enumerate(users)}
    d["u"] = d.user.map(uidx)
    halves = {R: np.zeros((a.splits + 1, 2, len(users))) for R in RULES}  # split 0..splits-1 random, last temporal
    for s in range(a.splits + 1):
        if s < a.splits:
            dd = d.assign(o=rng.random(len(d))).sort_values(["u", "o"])
        else:
            dd = d.sort_values(["u", "time"])
        pos = dd.groupby("u").cumcount().values
        n_u = dd.groupby("u").u.transform("size").values
        half = np.where(s < a.splits, pos % 2, (pos >= n_u / 2).astype(int))
        for h in (0, 1):
            part = dd[half == h]
            uu, sch, _ = score(part, stats=stats, topic_codes=topic_codes)
            for R in RULES:
                halves[R][s, h, :] = pd.Series(sch[R], index=uu).reindex(users).values

    def rho(x, y):
        ok = np.isfinite(x) & np.isfinite(y)
        return spearmanr(x[ok], y[ok]).correlation

    stab = []
    B = rng.integers(0, len(users), (a.boot, len(users)))
    for R in RULES:
        H = halves[R]
        r_rand = np.mean([rho(H[s, 0], H[s, 1]) for s in range(a.splits)])
        r_temp = rho(H[-1, 0], H[-1, 1])
        br = [np.mean([rho(H[s, 0, b], H[s, 1, b]) for s in range(0, a.splits, 4)]) for b in B]
        bt = [rho(H[-1, 0, b], H[-1, 1, b]) for b in B]
        stab.append({"rule": R, "n_users": len(users), "split_half_random": r_rand,
                     "random_ci_lo": np.percentile(br, 2.5), "random_ci_hi": np.percentile(br, 97.5),
                     "split_half_temporal": r_temp, "temporal_ci_lo": np.percentile(bt, 2.5),
                     "temporal_ci_hi": np.percentile(bt, 97.5)})
    stab = pd.DataFrame(stab)
    # selection habit: crowd probability of the side a user bets on, early half vs late half (temporal split)
    dt = d.sort_values(["u", "time"]).copy()
    dt["half"] = (dt.groupby("u").cumcount() >= dt.groupby("u").u.transform("size") / 2).astype(int)
    dt["fav"] = np.where(dt.bet_yes, dt.p_before, 1 - dt.p_before)
    fh = dt.groupby(["u", "half"]).fav.mean().unstack().reindex(range(len(users)))
    f0, f1 = fh[0].values, fh[1].values
    habit = {"temporal_split_rho_mean_fav_prob": float(rho(f0, f1)),
             "ci": [float(np.percentile(v, q)) for v in [[rho(f0[b], f1[b]) for b in B]] for q in (2.5, 97.5)],
             "spearman_mean_fav_prob_vs_ACC": float(spearmanr(U.mean_fav_prob, U.ACC).correlation),
             "spearman_mean_fav_prob_vs_IG": float(spearmanr(U.mean_fav_prob, U.IG).correlation)}
    stab.round(3).to_csv(OUT / f"real_stability_{tag}.csv", index=False)

    # (b) gaming signature
    pr = {R: rankdata(np.nan_to_num(U[R].values, nan=-np.inf)) / len(U) * 100 for R in RULES}
    gap = pr["ACC"] - pr["IG"]
    sig_r = spearmanr(U.near_certain_share, gap).correlation
    bs = [spearmanr(U.near_certain_share.values[b], gap[b]).correlation for b in B]
    bl = [spearmanr(U.late_share.values[b], gap[b]).correlation for b in B]
    top = pr["ACC"] >= 90
    ig_top = pr["IG"][top]
    nc_cut = float(np.quantile(U.near_certain_share.values, 0.9))
    hi_nc = U.near_certain_share.values >= nc_cut  # top decile of near-certain share
    sig = {
        "tag": tag, "n_bets_filtered": int(n_bets), "n_claims_all_users": int(n_all_claims),
        "n_claims_analysed": int(len(d)), "n_users_analysed": int(len(users)),
        "n_users_total": int(df.user.nunique()), "n_markets": int(df.market.nunique()),
        "markets_skipped": skipped, "date_range": [str(pd.to_datetime(df.time.min(), unit="ms").date()),
                                                   str(pd.to_datetime(df.time.max(), unit="ms").date())],
        "share_claims_correct_direction": float(d.bet_yes.eq(d.y).mean()),
        "share_claims_near_certain": float(d.near_certain.mean()),
        "spearman_nearcertain_vs_accrank_minus_igrank": float(sig_r),
        "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
        "spearman_late_share_vs_accrank_minus_igrank": float(spearmanr(U.late_share, gap).correlation),
        "late_ci": [float(np.percentile(bl, 2.5)), float(np.percentile(bl, 97.5))],
        "share_claims_late": float(d.late.mean()),
        "top_acc_decile_n": int(top.sum()), "top_acc_decile_median_ig_pct": float(np.median(ig_top)),
        "top_acc_decile_share_below_median_ig": float((ig_top < 50).mean()),
        "high_near_certain_users_n": int(hi_nc.sum()), "high_near_certain_cut": nc_cut,
        "high_near_certain_median_acc_pct": float(np.median(pr["ACC"][hi_nc])) if hi_nc.any() else None,
        "high_near_certain_median_ig_pct": float(np.median(pr["IG"][hi_nc])) if hi_nc.any() else None,
        "spearman_acc_vs_ig": float(spearmanr(U.ACC, U.IG).correlation),
        "selection_habit": habit,
        "spearman_brier_vs_ig": float(spearmanr(U.BRIER, U.IG).correlation),
        "eb_constants": {"brier": stats["eb_brier"], "ig": stats["eb_ig"]},
        "topic_counts": d.topic.value_counts().to_dict(),
    }
    api = U.api_share.values >= 0.5
    sig["api_users_n"] = int(api.sum())
    if api.any():
        sig["api_users_median_pct"] = {R: float(np.median(pr[R][api])) for R in RULES}
    # rank correlation matrix between rules
    S.corr(method="spearman").round(3).to_csv(OUT / f"real_rule_corr_{tag}.csv")
    (OUT / f"real_summary_{tag}.json").write_text(json.dumps(sig, indent=1, default=float))
    print(json.dumps(sig, indent=1, default=float))
    print(stab.round(3).to_string(index=False))
    if tag == "main":
        figure(U, pr, stab)


def figure(U, pr, stab):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160)
    ax = axes[0]
    st = stab.iloc[::-1]
    y = np.arange(len(st))
    ax.plot(st.split_half_random, y + 0.12, "o", color="#2a78d6", ms=6, label="random split")
    ax.hlines(y + 0.12, st.random_ci_lo, st.random_ci_hi, color="#2a78d6", lw=2)
    ax.plot(st.split_half_temporal, y - 0.12, "s", color="#eb6834", ms=6, label="early vs late half")
    ax.hlines(y - 0.12, st.temporal_ci_lo, st.temporal_ci_hi, color="#eb6834", lw=2)
    ax.set_yticks(y, st.rule, fontsize=8)
    ax.axvline(0, color="#52514e", lw=0.8)
    ax.set_xlabel("Split-half Spearman ρ of user scores", fontsize=8.5)
    ax.set_title(f"A. Rank stability on Manifold (n={len(U)} users)", fontsize=9.5, loc="left")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.grid(axis="x", color="#e4e3df", lw=0.6)
    ax = axes[1]
    sc = ax.scatter(pr["ACC"], pr["IG"], c=U.near_certain_share, cmap="viridis", s=10, alpha=0.8, lw=0)
    ax.plot([0, 100], [0, 100], color="#52514e", lw=0.8, ls="--")
    ax.set_xlabel("Percentile under accuracy (ACC)", fontsize=8.5)
    ax.set_ylabel("Percentile under information gain over crowd (IG)", fontsize=8.5)
    ax.set_title("B. Accuracy rank vs information-gain rank", fontsize=9.5, loc="left")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("share of claims on the ≥90% favourite", fontsize=8)
    for a_ in axes:
        for s in ("top", "right"):
            a_.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_manifold.png")
    print("wrote fig2")


if __name__ == "__main__":
    main()
