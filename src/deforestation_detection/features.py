"""Feature extraction for satellite/aerial imagery."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Pillow is required.  Install it with:  pip install pillow"
    ) from exc

FEATURE_VERSION: str = "v1"


def load_image(path: Path, image_size: Tuple[int, int]) -> np.ndarray:
    """Open *path*, convert to RGB, resize to *image_size*, normalise to [0,1].

    Returns
    -------
    np.ndarray
        Float32 array of shape (H, W, 3).
    """
    with Image.open(path) as img:
        img = img.convert("RGB").resize(image_size, Image.LANCZOS)
        return np.asarray(img, dtype=np.float32) / 255.0


def extract_features_from_array(arr: np.ndarray) -> np.ndarray:
    """Convert an RGB image array (H x W x 3, float32, [0,1]) to a feature vector.

    Features
    --------
    * Per-channel mean and standard deviation (6 values).
    * Vegetation-inspired indices (3 values):
        - green dominance  = mean(G − (R+B)/2)
        - NDVI-like        = mean((G−R) / (G+R+ε))
        - excess green     = mean(2G − R − B)
    * Edge/texture proxy: mean absolute first-order difference along both axes.
    * Pixel-proportion heuristics (2 values):
        - fraction of pixels where G > R and G > B  (green/vegetated pixels)
        - fraction of pixels where R > G and B < G  (bare/soil pixels)

    Total: 14 features.
    """
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    mean_rgb = np.array([r.mean(), g.mean(), b.mean()], dtype=np.float32)
    std_rgb = np.array([r.std(), g.std(), b.std()], dtype=np.float32)

    eps = 1e-6
    green_dominance = float((g - (r + b) / 2.0).mean())
    ndvi_like = float(((g - r) / (g + r + eps)).mean())
    excess_green = float((2.0 * g - r - b).mean())

    texture = float(
        np.abs(np.diff(arr, axis=0)).mean() + np.abs(np.diff(arr, axis=1)).mean()
    )

    green_pixels = float(np.mean((g > r) & (g > b)))
    bare_pixels = float(np.mean((r > g) & (b < g)))

    return np.array(
        [
            *mean_rgb,
            *std_rgb,
            green_dominance,
            ndvi_like,
            excess_green,
            texture,
            green_pixels,
            bare_pixels,
        ],
        dtype=np.float32,
    )
