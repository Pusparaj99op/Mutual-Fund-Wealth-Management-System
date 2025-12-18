import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Suppress noisy third-party warnings that are not actionable in CI/dev
import warnings
warnings.filterwarnings("ignore", message="CUDA initialization:.*")
warnings.filterwarnings("ignore", message="invalid escape sequence '\\s'")
