"""Item 2 (post hoc, 15 Nov): rerun main and R2 at 30 seeds. Seeds 0-9 come from the existing cache (identical to the
original run); seeds 10-29 are new. Writes NEW files results/E03/sim_{cond}_30seeds.json (originals untouched)."""
import json, sys
from multiprocessing import Pool
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim

if __name__ == "__main__":
    for cond in ["main", "R2"]:
        jobs = [(cond, s, False, False) for s in range(30)]
        with Pool(18) as p:
            out = p.map(sim.run_seed, jobs)
        (sim.OUT / f"sim_{cond}_30seeds.json").write_text(json.dumps(out))
        print("wrote", cond, flush=True)
