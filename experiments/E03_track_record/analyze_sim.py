"""Summarize the simulation: learned-cheater inflation per rule with bootstrap CIs over seeds, hand-coded
cheats, transfer matrix, learned policies, the pre-registered kill test, and Figure 1.

    uv run python -I experiments/E03_track_record/analyze_sim.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim  # noqa: E402
from rules import FAMILY  # noqa: E402

OUT = sim.OUT
CONDS = ["main", "R1", "R2", "R3", "main_strong"]
COND_LABEL = {"main": "main", "R1": "R1 miscalibrated honest", "R2": "R2 biased crowd", "R3": "R3 min volume 30",
              "main_strong": "main, ~5x CEM budget"}


def boot_ci(x, n=10000, seed=0):
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def describe_policy(theta, cond, n_worlds=5, seed=123):
    """Realized behaviour of a learned policy on fresh worlds."""
    rng = np.random.default_rng(seed)
    th = np.asarray(theta)
    rows = []
    for _ in range(n_worlds):
        w = sim.make_world(rng, sim.CONDS[cond])
        logw = th[:sim.N_BINS][w["bin"]] + th[sim.N_BINS:sim.N_BINS + sim.N_TOPICS][w["topic"]]
        n = int(round(10 ** np.clip(th[-1], sim.LO[-1], sim.HI[-1])))
        idx = np.argpartition(-(logw + rng.gumbel(size=len(logw))), n - 1)[:n]
        c = w["c"][idx]
        r = sim.sigmoid(th[-3] * sim.logit(c) + th[-2])
        rows.append({"n_claims": n, "share_crowd_ge_0.95": float((np.abs(c - 0.5) >= 0.45).mean()),
                     "share_crowd_ge_0.8": float((np.abs(c - 0.5) >= 0.3).mean()),
                     "mean_abs_stated_minus_crowd": float(np.abs(r - c).mean()),
                     "share_more_extreme_than_crowd": float((np.abs(r - 0.5) > np.abs(c - 0.5) + 1e-9).mean()),
                     "alpha": float(th[-3]), "beta": float(th[-2])})
    return pd.DataFrame(rows).mean().to_dict()


def skill_recovery(cond="main", n_worlds=50, seed=7):
    """Validity check: Spearman correlation between honest sources' true skill k and their rule score."""
    from scipy.stats import spearmanr
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_worlds):
        w = sim.make_world(rng, sim.CONDS[cond])
        out.append([spearmanr(w["k"], h).correlation for h in w["H"]])
    out = np.array(out)
    return {R: boot_ci(out[:, i]) for i, R in enumerate(sim.RULES)}


def main():
    rows, hc_rows, pol_rows, transfer = [], [], [], {}
    rec = skill_recovery()
    for cond in CONDS:
        fn = OUT / f"sim_{cond}.json"
        if not fn.exists():
            continue
        res = json.loads(fn.read_text())
        rules = res[0]["rules"]
        hc_names = list(res[0]["handcoded"])
        for ri, R in enumerate(rules):
            pct = [r["learned"][R]["pct"] for r in res]
            bm = [r["learned"][R]["beat_median"] for r in res]
            hc = {h: np.mean([r["handcoded"][h]["pct_mean"][ri] for r in res]) for h in hc_names}
            best_h = max(hc, key=hc.get)
            m, lo, hi = boot_ci(pct)
            bmm, bml, bmh = boot_ci(bm)
            rows.append({"cond": cond, "rule": R, "family": FAMILY.get(R, "post-hoc"), "n_seeds": len(res),
                         "learned_pct": m, "ci_lo": lo, "ci_hi": hi, "seed_min": min(pct), "seed_max": max(pct),
                         "beat_median_share": bmm, "bm_ci_lo": bml, "bm_ci_hi": bmh,
                         "best_handcoded": best_h, "best_handcoded_pct": hc[best_h],
                         "copy_crowd_pct": hc["copy-crowd"],
                         "skill_rho_main": rec[R][0], "skill_rho_lo": rec[R][1], "skill_rho_hi": rec[R][2]})
            for h in hc_names:
                v = [r["handcoded"][h]["pct_mean"][ri] for r in res]
                hm, hl, hh = boot_ci(v)
                hc_rows.append({"cond": cond, "strategy": h, "rule": R, "pct": hm, "ci_lo": hl, "ci_hi": hh})
            if cond == "main" or R in ("BSS", "IG", "EB-IG", "EB0-IG", "IG-SUM", "BRIER-GAIN"):
                d = [describe_policy(r["learned"][R]["theta"], cond.split("_")[0], n_worlds=2, seed=r["seed"])
                     for r in res]
                med = pd.DataFrame(d).median().to_dict()
                pol_rows.append({"cond": cond, "trained_on": R, **{k: round(v, 3) for k, v in med.items()}})
        transfer[cond] = pd.DataFrame(
            [np.mean([r["learned"][R]["pct_all_rules"] for r in res], 0) for R in rules],
            index=pd.Index(rules, name="trained_on"), columns=rules)

    summ = pd.DataFrame(rows)
    summ.round(2).to_csv(OUT / "sim_summary.csv", index=False)
    hc_df = pd.DataFrame(hc_rows)
    hc_df.round(2).to_csv(OUT / "sim_handcoded.csv", index=False)
    piv = hc_df[hc_df.cond == "main"].pivot(index="strategy", columns="rule", values="pct")
    piv[[R for R in summ.rule.unique() if R in piv.columns]].round(0).astype(int).to_csv(OUT / "sim_handcoded_main_pivot.csv")
    res_main = json.loads((OUT / "sim_main.json").read_text())
    ebc = {k: {"median": float(np.median(v)), "p25": float(np.percentile(v, 25)), "p75": float(np.percentile(v, 75)),
               "share_tau2_floored(kappa>1e6)": float((v > 1e6).mean()), "n_worlds": len(v)}
           for k in res_main[0]["eb"] for v in [np.concatenate([r["eb"][k] for r in res_main])]}
    (OUT / "sim_eb_constants.json").write_text(json.dumps(ebc, indent=1))
    pd.DataFrame(pol_rows).to_csv(OUT / "sim_learned_policies.csv", index=False)
    for cond, T in transfer.items():
        T.round(1).to_csv(OUT / f"sim_transfer_{cond}.csv")

    # pre-registered kill test on the main condition
    mn = summ[summ.cond == "main"].set_index("rule")
    pre = [R for R in mn.index if R in FAMILY]
    inflated = [R for R in ("ACC", "BRIER") if mn.loc[R, "ci_lo"] > 50]
    holds = [R for R in pre if mn.loc[R, "ci_hi"] < 50]
    kt = {"inflated_widely_used": inflated, "rules_holding_below_median": holds,
          "signal_present": bool(inflated) and bool(holds),
          "note": "learned-cheater percentile among 200 honest skilled sources; 95% bootstrap CI over 10 seeds"}
    (OUT / "killtest_sim.json").write_text(json.dumps(kt, indent=1))
    print(json.dumps(kt, indent=1))
    print(summ[["cond", "rule", "learned_pct", "ci_lo", "ci_hi", "beat_median_share", "best_handcoded",
                "best_handcoded_pct", "copy_crowd_pct", "skill_rho_main"]].round(2).to_string(index=False))
    figure(summ)


def figure(summ):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    col = {"absolute": "#2a78d6", "difficulty-weighted": "#2a78d6", "per-topic": "#2a78d6",
           "shrinkage": "#eb6834", "crowd-relative": "#1baf7a", "post-hoc": "#1baf7a"}
    grp = {"absolute": "absolute / difficulty-weighted / per-topic", "difficulty-weighted":
           "absolute / difficulty-weighted / per-topic", "per-topic": "absolute / difficulty-weighted / per-topic",
           "shrinkage": "EB shrinkage toward population mean", "crowd-relative": "crowd-relative",
           "post-hoc": "crowd-relative"}
    mn = summ[summ.cond == "main"].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.2, 5.2), dpi=160)
    y = np.arange(len(mn))[::-1]
    ax.axvline(50, color="#52514e", lw=1, ls="--", zorder=0)
    ax.text(51.5, y.max() - 2.5, "median honest\nskilled source", fontsize=7.5, color="#52514e", va="center")
    seen = set()
    for yi, (_, r) in zip(y, mn.iterrows()):
        c = col[r.family]
        lab = grp[r.family] if grp[r.family] not in seen else None
        seen.add(grp[r.family])
        ax.plot([r.ci_lo, r.ci_hi], [yi, yi], color=c, lw=2, solid_capstyle="round")
        ax.plot(r.learned_pct, yi, "o", ms=8, color=c, mec="white", mew=1.5, label=lab, zorder=3)
        ax.plot(r.best_handcoded_pct, yi, "|", ms=10, mew=2, color="#0b0b0b", zorder=2,
                label="best of 10 hand-coded cheats" if "hc" not in seen else None)
        seen.add("hc")
        ax.text(101.5, yi, f"{r.learned_pct:.0f}", va="center", fontsize=8, color="#0b0b0b")
    names = [f"{R}{' *' if f == 'post-hoc' else ''}" for R, f in zip(mn.rule, mn.family)]
    ax.set_yticks(y, names, fontsize=8.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Zero-skill learning cheater: percentile among 200 honest skilled sources (held-out)", fontsize=8.5)
    ax.set_title("Which reliability score survives a learning cheater?", fontsize=10.5, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color="#e4e3df", lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=7.5, loc="lower right", frameon=True, framealpha=0.95)
    fig.text(0.01, 0.005, "Dots: mean over 10 seeds; bars: 95% bootstrap CI over seeds. * = rule added post hoc.",
             fontsize=7, color="#52514e")
    fig.tight_layout(rect=(0, 0.02, 0.97, 1))
    fig.savefig(OUT / "fig1_cheater_inflation.png")
    print("wrote fig1")


if __name__ == "__main__":
    main()
