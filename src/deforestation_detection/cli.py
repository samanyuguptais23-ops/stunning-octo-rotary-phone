"""Unified CLI entry point for training and prediction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .model import load_model, predict_image, save_metrics, save_model, train_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deforestation-detection",
        description="Illegal Deforestation Detection — train or predict",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data/raw",
        help="Root directory of the labelled dataset (default: data/raw)",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="models/deforestation_model.pkl",
        help="Where to save / load the model bundle (default: models/deforestation_model.pkl)",
    )
    parser.add_argument(
        "--predict",
        type=str,
        default=None,
        metavar="IMAGE_PATH",
        help="Path to an image to classify (skips training)",
    )
    parser.add_argument(
        "--reports_dir",
        type=str,
        default="reports",
        help="Directory where metrics.json is written after training (default: reports)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    model_path = Path(args.model_path)

    if args.predict:
        bundle = load_model(model_path)
        label, confidence = predict_image(bundle, Path(args.predict))
        print(f"prediction:  {label}")
        print(f"confidence:  {confidence:.4f}")
        return

    # Training mode
    data_dir = Path(args.data_dir)
    bundle, metrics = train_model(data_dir)
    save_model(bundle, model_path)
    save_metrics(metrics, Path(args.reports_dir))


if __name__ == "__main__":
    main(sys.argv[1:])
