from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt


FloatArray = npt.NDArray[np.float64]


@dataclass(frozen=True)
class RidgeModel:
    coefficients: FloatArray
    intercept: FloatArray
    feature_mean: FloatArray
    feature_scale: FloatArray
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]
    alpha: float
    training_run_ids: tuple[str, ...]

    def predict(self, features: npt.ArrayLike) -> FloatArray:
        feature_array = np.asarray(features, dtype=np.float64)
        if feature_array.ndim != 2:
            raise ValueError("features must be a two-dimensional array")
        if feature_array.shape[1] != len(self.feature_names):
            raise ValueError(
                "feature count does not match model: "
                f"{feature_array.shape[1]} != {len(self.feature_names)}"
            )
        standardized = (feature_array - self.feature_mean) / self.feature_scale
        return standardized @ self.coefficients + self.intercept

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            output_path,
            coefficients=self.coefficients,
            intercept=self.intercept,
            feature_mean=self.feature_mean,
            feature_scale=self.feature_scale,
            feature_names=np.asarray(self.feature_names),
            target_names=np.asarray(self.target_names),
            alpha=np.asarray(self.alpha, dtype=np.float64),
            training_run_ids=np.asarray(self.training_run_ids),
        )

    @classmethod
    def load(cls, path: str | Path) -> RidgeModel:
        with np.load(Path(path), allow_pickle=False) as artifact:
            return cls(
                coefficients=np.asarray(
                    artifact["coefficients"], dtype=np.float64
                ),
                intercept=np.asarray(artifact["intercept"], dtype=np.float64),
                feature_mean=np.asarray(
                    artifact["feature_mean"], dtype=np.float64
                ),
                feature_scale=np.asarray(
                    artifact["feature_scale"], dtype=np.float64
                ),
                feature_names=tuple(str(value) for value in artifact["feature_names"]),
                target_names=tuple(str(value) for value in artifact["target_names"]),
                alpha=float(artifact["alpha"]),
                training_run_ids=tuple(
                    str(value) for value in artifact["training_run_ids"]
                ),
            )


def fit_ridge(
    features: npt.ArrayLike,
    targets: npt.ArrayLike,
    *,
    alpha: float,
    feature_names: tuple[str, ...],
    target_names: tuple[str, ...],
    training_run_ids: tuple[str, ...],
) -> RidgeModel:
    if alpha < 0.0:
        raise ValueError("alpha must be non-negative")

    feature_array = np.asarray(features, dtype=np.float64)
    target_array = np.asarray(targets, dtype=np.float64)
    if feature_array.ndim != 2 or target_array.ndim != 2:
        raise ValueError("features and targets must be two-dimensional arrays")
    if feature_array.shape[0] != target_array.shape[0]:
        raise ValueError("features and targets must have the same row count")
    if feature_array.shape[0] == 0:
        raise ValueError("training data must not be empty")
    if feature_array.shape[1] != len(feature_names):
        raise ValueError("feature_names does not match the feature matrix")
    if target_array.shape[1] != len(target_names):
        raise ValueError("target_names does not match the target matrix")
    if not np.isfinite(feature_array).all() or not np.isfinite(target_array).all():
        raise ValueError("training data contains non-finite values")

    feature_mean = feature_array.mean(axis=0)
    feature_scale = feature_array.std(axis=0)
    feature_scale = np.where(feature_scale > 0.0, feature_scale, 1.0)
    standardized = (feature_array - feature_mean) / feature_scale

    target_mean = target_array.mean(axis=0)
    centered_targets = target_array - target_mean
    if alpha == 0.0:
        coefficients = np.linalg.lstsq(
            standardized,
            centered_targets,
            rcond=None,
        )[0]
    else:
        regularized_gram = standardized.T @ standardized
        regularized_gram += alpha * np.eye(
            standardized.shape[1], dtype=np.float64
        )
        right_hand_side = standardized.T @ centered_targets
        coefficients = np.linalg.solve(regularized_gram, right_hand_side)

    return RidgeModel(
        coefficients=coefficients,
        intercept=target_mean,
        feature_mean=feature_mean,
        feature_scale=feature_scale,
        feature_names=feature_names,
        target_names=target_names,
        alpha=alpha,
        training_run_ids=training_run_ids,
    )
