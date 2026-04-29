# Sample Images

Place sample images here for quick prediction tests.

These images are **not** part of the training dataset; they are used to
verify that a saved model loads and predicts correctly.

## Suggested layout

```
data/sample_images/
    forest_intact_sample.jpg
    deforestation_sample.jpg
```

## Where to find images

* [Sentinel Hub EO Browser](https://apps.sentinel-hub.com/eo-browser/) —
  free Sentinel-2 imagery at 10 m/pixel.
* [Planet Labs Education & Research Programme](https://www.planet.com/markets/education-and-research/)
* Any publicly available aerial/satellite imagery dataset (e.g. EuroSAT,
  DeepForest, Global Forest Watch).

> **Note:** Do *not* commit large image files to this repository.
> Add a line like `data/sample_images/*.jpg` to `.gitignore` if needed.
