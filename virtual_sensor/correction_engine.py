from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol, Sequence

import numpy as np
import numpy.typing as npt

from kinematics.inverse_kinematics import InverseKinematicsError, delta_ik


FloatArray = npt.NDArray[np.float64]
Vector3 = tuple[float, float, float]


class ErrorPredictionModel(Protocol):
    feature_names: tuple[str, ...]
    target_names: tuple[str, ...]

    def predict(self, features: npt.ArrayLike) -> FloatArray:
        ...


@dataclass(frozen=True)
class CorrectionConfig:
    gain: float
    max_xy_correction_mm: float
    theta_min_deg: float = -45.0
    theta_max_deg: float = 90.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.gain) or self.gain < 0.0:
            raise ValueError("gain must be finite and non-negative")
        if (
            not math.isfinite(self.max_xy_correction_mm)
            or self.max_xy_correction_mm <= 0.0
        ):
            raise ValueError(
                "max_xy_correction_mm must be finite and positive"
            )
        if self.theta_min_deg >= self.theta_max_deg:
            raise ValueError("theta_min_deg must be less than theta_max_deg")


@dataclass(frozen=True)
class CorrectionResult:
    predicted_error_xyz_mm: Vector3
    requested_correction_xyz_mm: Vector3
    applied_correction_xyz_mm: Vector3
    corrected_target_xyz_mm: Vector3
    corrected_theta_deg: Vector3
    correction_clamped: bool
    fallback_used: bool
    status: str


class CorrectionEngine:
    def __init__(
        self,
        model: ErrorPredictionModel,
        config: CorrectionConfig,
    ) -> None:
        self._model = model
        self.config = config
        if (
            "error_x" not in model.target_names
            or "error_y" not in model.target_names
        ):
            raise ValueError("model targets must include error_x and error_y")

    @property
    def feature_names(self) -> tuple[str, ...]:
        return self._model.feature_names

    def apply(
        self,
        *,
        target_xyz_mm: Sequence[float],
        nominal_theta_deg: Sequence[float],
        feature_names: Sequence[str],
        feature_values: Sequence[float],
    ) -> CorrectionResult:
        target = _as_finite_vector3(target_xyz_mm, name="target_xyz_mm")
        nominal_theta = _as_finite_vector3(
            nominal_theta_deg,
            name="nominal_theta_deg",
        )
        _validate_nominal_theta(nominal_theta, self.config)

        if tuple(feature_names) != self.feature_names:
            raise ValueError(
                "feature schema does not match model: "
                f"{tuple(feature_names)} != {self.feature_names}"
            )

        try:
            feature_array = np.asarray(feature_values, dtype=np.float64)
        except (TypeError, ValueError):
            return _fallback_result(
                target=target,
                nominal_theta=nominal_theta,
                status="fallback_invalid_features",
            )
        if (
            feature_array.shape != (len(self.feature_names),)
            or not np.isfinite(feature_array).all()
        ):
            return _fallback_result(
                target=target,
                nominal_theta=nominal_theta,
                status="fallback_invalid_features",
            )

        try:
            prediction = np.asarray(
                self._model.predict(feature_array.reshape(1, -1)),
                dtype=np.float64,
            )
        except Exception:
            return _fallback_result(
                target=target,
                nominal_theta=nominal_theta,
                status="fallback_inference_failure",
            )
        if prediction.shape != (1, len(self._model.target_names)):
            return _fallback_result(
                target=target,
                nominal_theta=nominal_theta,
                status="fallback_invalid_prediction_shape",
            )

        predicted_by_name = dict(zip(self._model.target_names, prediction[0]))
        predicted_error = (
            float(predicted_by_name["error_x"]),
            float(predicted_by_name["error_y"]),
            float(predicted_by_name.get("error_z", 0.0)),
        )
        if not all(math.isfinite(value) for value in predicted_error):
            return _fallback_result(
                target=target,
                nominal_theta=nominal_theta,
                status="fallback_nonfinite_prediction",
            )

        requested_correction = (
            -self.config.gain * predicted_error[0],
            -self.config.gain * predicted_error[1],
            0.0,
        )
        applied_correction, clamped = _clamp_xy(
            requested_correction,
            max_norm_mm=self.config.max_xy_correction_mm,
        )
        corrected_target = (
            target[0] + applied_correction[0],
            target[1] + applied_correction[1],
            target[2],
        )

        try:
            corrected_theta = delta_ik(
                *corrected_target,
                previous_theta_deg=nominal_theta,
                theta_min_deg=self.config.theta_min_deg,
                theta_max_deg=self.config.theta_max_deg,
            ).as_tuple()
        except InverseKinematicsError:
            return CorrectionResult(
                predicted_error_xyz_mm=predicted_error,
                requested_correction_xyz_mm=requested_correction,
                applied_correction_xyz_mm=(0.0, 0.0, 0.0),
                corrected_target_xyz_mm=target,
                corrected_theta_deg=nominal_theta,
                correction_clamped=clamped,
                fallback_used=True,
                status="fallback_corrected_ik_rejected",
            )

        return CorrectionResult(
            predicted_error_xyz_mm=predicted_error,
            requested_correction_xyz_mm=requested_correction,
            applied_correction_xyz_mm=applied_correction,
            corrected_target_xyz_mm=corrected_target,
            corrected_theta_deg=corrected_theta,
            correction_clamped=clamped,
            fallback_used=False,
            status="applied_clamped" if clamped else "applied",
        )


def _as_finite_vector3(values: Sequence[float], *, name: str) -> Vector3:
    if len(values) != 3:
        raise ValueError(f"{name} must contain exactly three values")
    vector = tuple(float(value) for value in values)
    if not all(math.isfinite(value) for value in vector):
        raise ValueError(f"{name} must contain only finite values")
    return (vector[0], vector[1], vector[2])


def _validate_nominal_theta(
    nominal_theta: Vector3,
    config: CorrectionConfig,
) -> None:
    if any(
        theta < config.theta_min_deg or theta > config.theta_max_deg
        for theta in nominal_theta
    ):
        raise ValueError("nominal_theta_deg violates configured theta limits")


def _clamp_xy(
    correction_xyz_mm: Vector3,
    *,
    max_norm_mm: float,
) -> tuple[Vector3, bool]:
    xy_norm = math.hypot(correction_xyz_mm[0], correction_xyz_mm[1])
    if xy_norm <= max_norm_mm:
        return correction_xyz_mm, False
    scale = max_norm_mm / xy_norm
    return (
        correction_xyz_mm[0] * scale,
        correction_xyz_mm[1] * scale,
        0.0,
    ), True


def _fallback_result(
    *,
    target: Vector3,
    nominal_theta: Vector3,
    status: str,
) -> CorrectionResult:
    return CorrectionResult(
        predicted_error_xyz_mm=(0.0, 0.0, 0.0),
        requested_correction_xyz_mm=(0.0, 0.0, 0.0),
        applied_correction_xyz_mm=(0.0, 0.0, 0.0),
        corrected_target_xyz_mm=target,
        corrected_theta_deg=nominal_theta,
        correction_clamped=False,
        fallback_used=True,
        status=status,
    )
