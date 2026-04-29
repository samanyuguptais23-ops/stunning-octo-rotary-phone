"""Dataset utilities: file discovery and image loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

import numpy as np

from .features import extract_features_from_array, load_image

IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
)

CLASS_NAMES: List[str] = ["forest_intact", "illegal_deforestation"]


def list_image_files(root_dir: Path) -> List[Path]:
    """Return sorted list of image files found recursively under *root_dir*."""
    files: List[Path] = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in IMAGE_EXTENSIONS:
                files.append(path)
    return sorted(files)


def build_dataset(
    data_dir: Path,
    class_names: List[str],
    image_size: Tuple[int, int],
) -> Tuple[np.ndarray, np.ndarray]:
    """Load images from *data_dir* and return (feature_matrix, label_vector).

    Each class should have its own sub-folder named after the class.
    Corrupt or unreadable images are skipped; counts are reported.

    Raises
    ------
    FileNotFoundError
        If *data_dir* does not exist.
    ValueError
        If no class folders or images are found.
    """
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # Validate that at least one expected class folder exists.
    found_classes = [c for c in class_names if (data_dir / c).is_dir()]
    if not found_classes:
        raise ValueError(
            f"No class folders found in '{data_dir}'. "
            f"Expected at least one of: {', '.join(class_names)}"
        )

    features: List[np.ndarray] = []
    labels: List[int] = []
    skipped_total = 0

    for label, class_name in enumerate(class_names):
        class_dir = data_dir / class_name
        if not class_dir.is_dir():
            continue

        image_paths = list_image_files(class_dir)
        skipped = 0

        for image_path in image_paths:
            try:
                arr = load_image(image_path, image_size)
                features.append(extract_features_from_array(arr))
                labels.append(label)
            except Exception:  # noqa: BLE001
                skipped += 1

        loaded = len(image_paths) - skipped
        print(f"  [{class_name}]  loaded={loaded}  skipped={skipped}")
        skipped_total += skipped

    if skipped_total:
        print(f"Total skipped (corrupt/unreadable): {skipped_total}")

    if not features:
        raise ValueError(
            f"No images could be loaded from '{data_dir}'. "
            "Check that the class folders contain valid image files."
        )

    return np.vstack(features), np.asarray(labels, dtype=np.int64)
