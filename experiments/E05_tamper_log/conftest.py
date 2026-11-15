# Make the E05 modules importable as top-level modules in tests (the experiment dir is not a package).
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
