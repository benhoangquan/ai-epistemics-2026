"""Fetch resolved binary Manifold markets and their bets (public API, no token), caching raw JSON.

Resumable: every response is cached under results/E03/data/manifold/ and never re-requested.
Polite: at most ~3 requests/second (documented limit is 500/min), retries with backoff.

    uv run python -I experiments/E03_track_record/fetch_manifold.py --n-markets 700
"""
from __future__ import annotations

import argparse
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results" / "E03" / "data" / "manifold"
API = "https://api.manifold.markets/v0"
MIN_INTERVAL = 0.34
_last = [0.0]


def get(path: str, params: dict | None = None):
    url = f"{API}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    for attempt in range(6):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "apart-epistemics-sprint-research/0.1 (E03 pilot)"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(5 * 2**attempt)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * 2**attempt)
    raise RuntimeError(f"failed after retries: {url}")


def cached(fn: Path, thunk):
    if fn.exists():
        return json.loads(fn.read_text())
    out = thunk()
    fn.parent.mkdir(parents=True, exist_ok=True)
    tmp = fn.with_suffix(".tmp")
    tmp.write_text(json.dumps(out))
    tmp.rename(fn)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-markets", type=int, default=700)
    ap.add_argument("--max-pages", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    pool = []
    for off in range(0, 1001, 500):  # API caps offset at 1000
        page = cached(DATA / f"search_popular_{off}.json", lambda off=off: get("search-markets", {
            "term": "", "filter": "resolved", "contractType": "BINARY", "sort": "most-popular",
            "limit": 500, "offset": off}))
        pool.extend(page)
    seen, elig = set(), []
    for m in pool:
        if m["id"] in seen:
            continue
        seen.add(m["id"])
        if (m.get("resolution") in ("YES", "NO") and m.get("mechanism") == "cpmm-1" and m.get("token", "MANA") == "MANA"
                and 20 <= m.get("uniqueBettorCount", 0) <= 500):
            elig.append(m)
    print(f"pool {len(pool)} unique {len(seen)} eligible {len(elig)}", flush=True)
    rng = random.Random(a.seed)
    sample = rng.sample(elig, min(a.n_markets, len(elig)))
    (DATA / "sample_ids.json").write_text(json.dumps([m["id"] for m in sample]))

    for j, m in enumerate(sample):
        mid = m["id"]
        cached(DATA / "markets" / f"{mid}.json", lambda: get(f"market/{mid}"))
        fn = DATA / "bets" / f"{mid}.json"
        if not fn.exists():
            bets, before, truncated = [], None, False
            for p in range(a.max_pages):
                params = {"contractId": mid, "limit": 1000}
                if before:
                    params["before"] = before
                page = get("bets", params)
                bets.extend(page)
                if len(page) < 1000:
                    break
                before = page[-1]["id"]
            else:
                truncated = True
            fn.parent.mkdir(parents=True, exist_ok=True)
            fn.write_text(json.dumps({"truncated": truncated, "bets": bets}))
        if j % 25 == 0:
            print(f"{j + 1}/{len(sample)} markets fetched", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
