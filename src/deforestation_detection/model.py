"""Model training, persistence, and inference."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        confusion_matrix,
    )
    from sklearn.model_selection import train_test_split
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "scikit-learn is required.  Install it with:  pip install scikit-learn"
    ) from exc

from .dataset import CLASS_NAMES, build_dataset
from .features import FEATURE_VERSION, extract_features_from_array, load_image


@dataclass
class ModelBundle:
    """Container persisted to disk that bundles the model with its metadata."""

    model: RandomForestClassifier
    class_names: List[str]
    image_size: Tuple[int, int] = (128, 128)
    feature_version: str = field(default=FEATURE_VERSION)


def train_model(
    data_dir: Path,
    image_size: Tuple[int, int] = (128, 128),
) -> Tuple[ModelBundle, Dict]:
    """Train a RandomForest classifier on images in *data_dir*.

    Parameters
    ----------
    data_dir:
        Root directory containing one sub-folder per class.
    image_size:
        (width, height) to which every image is resized before feature extraction.

    Returns
    -------
    bundle:
        Trained :class:`ModelBundle`.
    metrics:
        Dictionary with accuracy, confusion matrix, and classification report.
    """
    print(f"\nBuilding dataset from: {data_dir}")
    X, y = build_dataset(data_dir, CLASS_NAMES, image_size)

    counts = {CLASS_NAMES[i]: int(np.sum(y == i)) for i in range(len(CLASS_NAMES))}
    print(f"Class counts: {counts}")
    print(f"Total samples: {len(y)}\n")

    stratify = y if len(np.unique(y)) > 1 and len(y) >= 4 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=stratify
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = float(accuracy_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()
    report_str = classification_report(
        y_test, y_pred, target_names=CLASS_NAMES, zero_division=0
    )

    print(f"Accuracy:  {acc:.4f}")
    print("Confusion matrix:")
    print(np.array(cm))
    print("\nClassification report:")
    print(report_str)

    metrics: Dict = {
        "accuracy": acc,
        "confusion_matrix": cm,
        "report": report_str,
        "class_counts": counts,
        "image_size": list(image_size),
        "feature_version": FEATURE_VERSION,
        "model_params": model.get_params(),
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }

    bundle = ModelBundle(model=model, class_names=CLASS_NAMES, image_size=image_size)
    return bundle, metrics


def save_model(bundle: ModelBundle, model_path: Path) -> None:
    """Persist *bundle* to *model_path* using pickle."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as fh:
        pickle.dump(bundle, fh)
    print(f"Model saved → {model_path}")


def load_model(model_path: Path) -> ModelBundle:
    """Load and return a :class:`ModelBundle` from *model_path*.

    Raises
    ------
    FileNotFoundError
        If *model_path* does not exist.
    TypeError
        If the file does not contain a valid :class:`ModelBundle`.
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    with model_path.open("rb") as fh:
        bundle = pickle.load(fh)  # noqa: S301
    if not isinstance(bundle, ModelBundle):
        raise TypeError(
            f"Expected a ModelBundle but got {type(bundle).__name__}. "
            "The model file may be corrupt or from an incompatible version."
        )
    return bundle


def predict_image(bundle: ModelBundle, image_path: Path) -> Tuple[str, float]:
    """Predict the class of a single image.

    Returns
    -------
    label:
        Predicted class name.
    confidence:
        Predicted probability for the returned class.
    """
    arr = load_image(image_path, bundle.image_size)
    feat = extract_features_from_array(arr).reshape(1, -1)
    probs = bundle.model.predict_proba(feat)[0]
    pred_idx = int(np.argmax(probs))
    return bundle.class_names[pred_idx], float(probs[pred_idx])


def save_metrics(metrics: Dict, reports_dir: Path = Path("reports")) -> Path:
    """Write *metrics* to ``reports/metrics.json``.

    Returns the path to the written file.
    """
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / "metrics.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"Metrics saved → {out_path}")
    return out_path
