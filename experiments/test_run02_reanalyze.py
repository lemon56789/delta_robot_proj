from __future__ import annotations

import math
import unittest

import numpy as np

from experiments.run02_reanalyze import (
    best_circle_shift,
    c_round,
    classify_step_segment,
    fit_circle,
    initial_home_offset,
    project_servo_commands,
    tracking_metrics,
)


class Run02ReanalysisTest(unittest.TestCase):
    def test_home_offset_and_normalized_metric(self) -> None:
        rows = [
            {
                "phase": "home_1",
                "vision_x": 2.0,
                "vision_y": -1.0,
                "target_x": 0.0,
                "target_y": 0.0,
            },
            {
                "phase": "home_1",
                "vision_x": 2.0,
                "vision_y": -1.0,
                "target_x": 0.0,
                "target_y": 0.0,
            },
            {
                "phase": "x_plus",
                "vision_x": 12.0,
                "vision_y": -1.0,
                "target_x": 10.0,
                "target_y": 0.0,
            },
        ]
        offset = initial_home_offset(rows)
        self.assertEqual(offset, (2.0, -1.0))
        normalized = tracking_metrics(rows, offset_xy=offset)
        self.assertAlmostEqual(normalized["tracking_xy_rmse"], 0.0)

    def test_firmware_rounding_and_servo_projection(self) -> None:
        self.assertEqual(c_round(84.5), 85)
        self.assertEqual(c_round(-1.5), -2)
        self.assertEqual(project_servo_commands((0.0, 0.0, 0.0)), (84, 86, 88))
        self.assertEqual(project_servo_commands((1.0, -1.0, 2.0)), (83, 87, 86))

    def test_step_segment_classification(self) -> None:
        self.assertEqual(
            classify_step_segment(
                {"phase": "home_1", "phase_elapsed_ms": 2000.0}
            ),
            "initial_home",
        )
        self.assertEqual(
            classify_step_segment(
                {"phase": "x_plus", "phase_elapsed_ms": 999.0}
            ),
            "transition",
        )
        self.assertEqual(
            classify_step_segment(
                {"phase": "x_plus", "phase_elapsed_ms": 1000.0}
            ),
            "stable",
        )

    def test_circle_fit_and_shift_sweep(self) -> None:
        times = np.arange(0.0, 30_001.0, 100.0)
        omega = 2.0 * math.pi / 30_000.0
        target_angles = omega * times
        target = np.column_stack(
            (40.0 * np.cos(target_angles), 40.0 * np.sin(target_angles))
        )
        lag_ms = 300.0
        vision_angles = omega * (times - lag_ms)
        vision = np.column_stack(
            (
                3.0 + 40.0 * np.cos(vision_angles),
                -2.0 + 40.0 * np.sin(vision_angles),
            )
        )
        center_x, center_y, radius = fit_circle(vision)
        self.assertAlmostEqual(center_x, 3.0, places=6)
        self.assertAlmostEqual(center_y, -2.0, places=6)
        self.assertAlmostEqual(radius, 40.0, places=6)

        shifted = best_circle_shift(
            times=times,
            vision_xy=vision - np.asarray([3.0, -2.0]),
            target_times=times,
            target_xy=target,
        )
        self.assertEqual(shifted["best_target_time_shift_ms"], -300)
        self.assertLess(shifted["best_tracking_xy_rmse_mm"], 1e-9)


if __name__ == "__main__":
    unittest.main()
