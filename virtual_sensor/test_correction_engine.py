from __future__ import annotations

import math
import unittest

import numpy as np

from virtual_sensor.correction_engine import (
    CorrectionConfig,
    CorrectionEngine,
)


FEATURE_NAMES = (
    "theta1_cmd",
    "theta2_cmd",
    "theta3_cmd",
    "theta1_meas",
    "theta2_meas",
    "theta3_meas",
    "sim_x",
    "sim_y",
    "sim_z",
)


class FixedPredictionModel:
    feature_names = FEATURE_NAMES
    target_names = ("error_x", "error_y", "error_z")

    def __init__(self, prediction: tuple[float, float, float]) -> None:
        self.prediction = prediction

    def predict(self, features: object) -> np.ndarray:
        feature_array = np.asarray(features)
        return np.tile(self.prediction, (feature_array.shape[0], 1))


class RaisingPredictionModel:
    feature_names = FEATURE_NAMES
    target_names = ("error_x", "error_y", "error_z")

    def predict(self, features: object) -> np.ndarray:
        raise RuntimeError("inference failed")


class CorrectionEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.features = (0.0,) * len(FEATURE_NAMES)
        self.target = (0.0, 0.0, -263.27731514697575)
        self.theta = (0.0, 0.0, 0.0)

    def test_correction_sign_and_z_disabled(self) -> None:
        engine = CorrectionEngine(
            FixedPredictionModel((4.0, -2.0, 20.0)),
            CorrectionConfig(gain=0.5, max_xy_correction_mm=10.0),
        )
        result = engine.apply(
            target_xyz_mm=self.target,
            nominal_theta_deg=self.theta,
            feature_names=FEATURE_NAMES,
            feature_values=self.features,
        )

        self.assertEqual(result.requested_correction_xyz_mm, (-2.0, 1.0, 0.0))
        self.assertEqual(result.applied_correction_xyz_mm, (-2.0, 1.0, 0.0))
        self.assertEqual(result.corrected_target_xyz_mm[2], self.target[2])
        self.assertFalse(result.fallback_used)

    def test_xy_vector_norm_clamp(self) -> None:
        engine = CorrectionEngine(
            FixedPredictionModel((-6.0, -8.0, 0.0)),
            CorrectionConfig(gain=1.0, max_xy_correction_mm=5.0),
        )
        result = engine.apply(
            target_xyz_mm=self.target,
            nominal_theta_deg=self.theta,
            feature_names=FEATURE_NAMES,
            feature_values=self.features,
        )

        self.assertTrue(result.correction_clamped)
        self.assertAlmostEqual(
            math.hypot(*result.applied_correction_xyz_mm[:2]),
            5.0,
        )
        self.assertEqual(result.applied_correction_xyz_mm, (3.0, 4.0, 0.0))

    def test_feature_order_mismatch_is_rejected(self) -> None:
        engine = CorrectionEngine(
            FixedPredictionModel((0.0, 0.0, 0.0)),
            CorrectionConfig(gain=0.25, max_xy_correction_mm=2.0),
        )
        with self.assertRaises(ValueError):
            engine.apply(
                target_xyz_mm=self.target,
                nominal_theta_deg=self.theta,
                feature_names=tuple(reversed(FEATURE_NAMES)),
                feature_values=self.features,
            )

    def test_nonfinite_prediction_falls_back(self) -> None:
        engine = CorrectionEngine(
            FixedPredictionModel((float("nan"), 0.0, 0.0)),
            CorrectionConfig(gain=0.25, max_xy_correction_mm=2.0),
        )
        result = engine.apply(
            target_xyz_mm=self.target,
            nominal_theta_deg=self.theta,
            feature_names=FEATURE_NAMES,
            feature_values=self.features,
        )

        self.assertTrue(result.fallback_used)
        self.assertEqual(result.status, "fallback_nonfinite_prediction")
        self.assertEqual(result.corrected_target_xyz_mm, self.target)
        self.assertEqual(result.corrected_theta_deg, self.theta)

    def test_inference_exception_falls_back(self) -> None:
        engine = CorrectionEngine(
            RaisingPredictionModel(),
            CorrectionConfig(gain=0.25, max_xy_correction_mm=2.0),
        )
        result = engine.apply(
            target_xyz_mm=self.target,
            nominal_theta_deg=self.theta,
            feature_names=FEATURE_NAMES,
            feature_values=self.features,
        )

        self.assertTrue(result.fallback_used)
        self.assertEqual(result.status, "fallback_inference_failure")
        self.assertEqual(result.corrected_target_xyz_mm, self.target)
        self.assertEqual(result.corrected_theta_deg, self.theta)

    def test_corrected_ik_rejection_falls_back(self) -> None:
        engine = CorrectionEngine(
            FixedPredictionModel((-1000.0, 0.0, 0.0)),
            CorrectionConfig(gain=1.0, max_xy_correction_mm=1000.0),
        )
        result = engine.apply(
            target_xyz_mm=self.target,
            nominal_theta_deg=self.theta,
            feature_names=FEATURE_NAMES,
            feature_values=self.features,
        )

        self.assertTrue(result.fallback_used)
        self.assertEqual(result.status, "fallback_corrected_ik_rejected")
        self.assertEqual(result.applied_correction_xyz_mm, (0.0, 0.0, 0.0))
        self.assertEqual(result.corrected_target_xyz_mm, self.target)
        self.assertEqual(result.corrected_theta_deg, self.theta)


if __name__ == "__main__":
    unittest.main()
