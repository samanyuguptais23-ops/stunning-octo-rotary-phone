#!/usr/bin/env python3
"""Run inference on a single image using a saved model.

Usage
-----
    python scripts/predict.py --image path/to/image.jpg --model_path models/deforestation_model.pkl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root without `pip install -e .`
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deforestation_detection.model import load_model, predict_image  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Predict deforestation class for a single image."
    )
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument(
        "--model_path",
        default="models/deforestation_model.pkl",
        help="Path to the saved ModelBundle (default: models/deforestation_model.pkl)",
    )
    args = parser.parse_args()

    bundle = load_model(Path(args.model_path))
    label, confidence = predict_image(bundle, Path(args.image))
    print(f"prediction:  {label}")
    print(f"confidence:  {confidence:.4f}")


if __name__ == "__main__":
    main()
