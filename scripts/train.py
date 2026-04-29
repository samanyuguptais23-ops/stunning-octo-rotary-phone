#!/usr/bin/env python3
"""Train the deforestation detection model.

Usage
-----
    python scripts/train.py --data_dir data/raw --model_path models/deforestation_model.pkl
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root without `pip install -e .`
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deforestation_detection.cli import main  # noqa: E402

if __name__ == "__main__":
    # Strip "--predict" so this script always runs in training mode.
    argv = [a for a in sys.argv[1:] if not a.startswith("--predict")]
    main(argv)
