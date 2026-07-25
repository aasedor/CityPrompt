import sys
from pathlib import Path

# Allow `from compiler import ...` when running pytest from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
