"""Scoring rules for a track-record ledger. Shared by the simulation (sim.py) and the Manifold analysis (real.py).

Every rule maps a source's claims (stated probability r, outcome y, crowd prior c, topic) to one number;
higher is better. Population statistics (topic means, empirical-Bayes constants) come from `pop_stats`.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-3
RULES = ["ACC", "BRIER", "LOG", "DW-ACC", "DW-BRIER", "TOPIC-BRIER", "EB-BRIER",
         "BSS", "IG", "EB-IG", "EB0-IG", "IG-SUM",
         "BRIER-GAIN"]  # BRIER-GAIN was added after the first main run (post hoc, exploratory): see README
# rule families, used for plots and the summary
FAMILY = {"ACC": "absolute", "BRIER": "absolute", "LOG": "absolute", "DW-ACC": "difficulty-weighted",
          "DW-BRIER": "difficulty-weighted", "TOPIC-BRIER": "per-topic", "EB-BRIER": "shrinkage",
          "BSS": "crowd-relative", "IG": "crowd-relative", "EB-IG": "shrinkage", "EB0-IG": "crowd-relative",
          "IG-SUM": "crowd-relative"}


def claim_terms(r, y, c):
    r = np.clip(r, EPS, 1 - EPS)
    c = np.clip(c, EPS, 1 - EPS)
    y = y.astype(bool)
    acc = np.where(np.abs(r - 0.5) < 1e-12, 0.5, ((r > 0.5) == y).astype(float))
    yf = y.astype(float)
    brier = (r - yf) ** 2
    brier_c = (c - yf) ** 2
    log = np.log2(np.where(y, r, 1 - r))
    log_c = np.log2(np.where(y, c, 1 - c))
    return {"acc": acc, "brier": brier, "brier_c": brier_c, "log": log, "ig": log - log_c, "w": 4 * c * (1 - c)}


def _mom(src, x, n_src):
    """Method-of-moments empirical-Bayes constants for per-source means of per-claim score x."""
    cnt = np.bincount(src, minlength=n_src).astype(float)
    ok = cnt >= 2
    m = np.bincount(src, weights=x, minlength=n_src) / np.maximum(cnt, 1)
    ssw = np.bincount(src, weights=(x - m[src]) ** 2, minlength=n_src)
    s2w = ssw[ok].sum() / (cnt[ok] - 1).sum()
    mu = m[ok].mean()
    tau2 = max(m[ok].var() - (s2w / cnt[ok]).mean(), 1e-12)
    return {"mu": float(mu), "kappa": float(s2w / tau2), "s2w": float(s2w), "tau2": float(tau2)}


def pop_stats(src, n_src, terms, topic, n_topics):
    tb = np.bincount(topic, weights=terms["brier"], minlength=n_topics) / np.maximum(
        np.bincount(topic, minlength=n_topics), 1)
    return {"topic_brier": tb, "eb_brier": _mom(src, -terms["brier"], n_src), "eb_ig": _mom(src, terms["ig"], n_src)}


def aggregate(src, n_src, terms, topic, stats):
    cnt = np.bincount(src, minlength=n_src).astype(float)

    def S(x):
        return np.bincount(src, weights=x, minlength=n_src)

    with np.errstate(invalid="ignore", divide="ignore"):
        w = terms["w"]
        mb = -S(terms["brier"]) / cnt
        mig = S(terms["ig"]) / cnt
        eb_b, eb_i = stats["eb_brier"], stats["eb_ig"]
        out = {
            "ACC": S(terms["acc"]) / cnt,
            "BRIER": mb,
            "LOG": S(terms["log"]) / cnt,
            "DW-ACC": S(w * terms["acc"]) / S(w),
            "DW-BRIER": -S(w * terms["brier"]) / S(w),
            "TOPIC-BRIER": S(stats["topic_brier"][topic] - terms["brier"]) / cnt,
            "EB-BRIER": (cnt * mb + eb_b["kappa"] * eb_b["mu"]) / (cnt + eb_b["kappa"]),
            "BSS": 1 - S(terms["brier"]) / S(terms["brier_c"]),
            "IG": mig,
            "EB-IG": (cnt * mig + eb_i["kappa"] * eb_i["mu"]) / (cnt + eb_i["kappa"]),
            "EB0-IG": (cnt * mig) / (cnt + eb_i["kappa"]),
            "IG-SUM": S(terms["ig"]),
            "BRIER-GAIN": S(terms["brier_c"] - terms["brier"]) / cnt,  # difference form of BSS (post hoc)
        }
    return out
