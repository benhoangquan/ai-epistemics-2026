"""E01 cheat-policy stress test. Usage: run.py {smoke|main|bandit|analyze}"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import benches as B  # noqa: E402

N_MAIN = {"b1": 150, "b2": 40, "b3": 24, "b4": 30}
N_SMOKE = {"b1": 5, "b2": 3, "b3": 2, "b4": 6}


def benches(n: dict) -> None:
    t0 = time.time()
    for key, fn in (("b1", B.run_b1), ("b2", B.run_b2), ("b3", B.run_b3), ("b4", B.run_b4)):
        print(f"== {key} n={n[key]} ({time.time() - t0:.0f}s)", flush=True)
        fn(n[key])
    print(f"== done in {time.time() - t0:.0f}s", flush=True)


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    if cmd == "smoke":
        B.CONST_JUDGED = 2
        B.RAW = B.RES / "smoke"
        benches(N_SMOKE)
        import bandit
        bandit.RAW = B.RAW
        print(bandit.propose())
    elif cmd == "main":
        benches(N_MAIN)
    elif cmd == "bandit":
        import bandit
        eval_ids = {it["id"] for it in B.load_darkbench(N_MAIN["b4"])}
        pulls = int(sys.argv[2]) if len(sys.argv) > 2 else 80
        print(json.dumps(bandit.run(pulls=pulls, eval_ids=eval_ids, n_val=N_MAIN["b4"]), indent=2), flush=True)
    elif cmd == "analyze":
        import analyze
        analyze.main()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
