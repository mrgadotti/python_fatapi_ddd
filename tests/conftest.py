import sys
from pathlib import Path

# Ensure project root (one level up from tests/) is on sys.path so "from app..." works
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)