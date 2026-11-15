"""Item 3 (post hoc, 15 Nov): rerun real.py with a higher minimum number of claims per user.
    uv run python -I experiments/E03_track_record/real_minclaims.py 50
Outputs go to results/E03/real_min<N>/ (real.py's output names, untouched originals)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import real

n = int(sys.argv[1])
out = real.ROOT / "results" / "E03" / f"real_min{n}"
out.mkdir(exist_ok=True)
real.OUT = out
real.MIN_CLAIMS = n
sys.argv = ["real.py"]
real.main()
