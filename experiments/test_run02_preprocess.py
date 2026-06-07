from __future__ import annotations

import unittest

from experiments.run02_preprocess import (
    VisionPoint,
    _align_circle,
    _align_step_trajectory,
    _interpolate_vision,
)


def _main_rows(phases: list[tuple[str, int, int]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for phase, start, end in phases:
        for time_ms in range(start, end, 100):
            rows.append({"time": str(time_ms), "phase": phase})
    return rows


def _vision_row(time_s: float, x: float, y: float) -> dict[str, str]:
    return {
        "vision_time": str(time_s),
        "vision_x": str(x),
        "vision_y": str(y),
        "valid": "True",
        "marker_detected": "True",
    }


class Run02PreprocessTest(unittest.TestCase):
    def test_step_alignment_uses_first_jump_and_validates_all_events(self) -> None:
        main_rows = _main_rows(
            [("home_1", 0, 5000), ("x_plus", 5000, 10000), ("home_2", 10000, 15000)]
        )
        vision_rows = [
            _vision_row(100.0, 0.0, 0.0),
            _vision_row(104.9, 0.0, 0.0),
            _vision_row(105.0, 30.0, 0.0),
            _vision_row(109.9, 30.0, 0.0),
            _vision_row(110.0, 0.0, 0.0),
            _vision_row(114.0, 0.0, 0.0),
        ]
        result = _align_step_trajectory(main_rows, vision_rows, vision_rows)
        self.assertEqual(result.anchors, ((105000.0, 5000.0),))
        self.assertEqual(result.diagnostics["event_count"], 2)
        self.assertEqual(result.diagnostics["max_abs_anchor_residual_ms"], 0.0)

    def test_circle_alignment_anchors_persistent_departure(self) -> None:
        main_rows = _main_rows(
            [
                ("home_1", 0, 5000),
                ("circle_start_hold", 5000, 7000),
                ("circle_ccw_001", 7000, 8000),
                ("circle_end_hold", 8000, 10000),
                ("home_2", 10000, 12000),
            ]
        )
        vision_rows = [
            _vision_row(10.0, 0.0, 0.0),
            _vision_row(11.0, 0.0, 0.0),
            _vision_row(12.0, 40.0, 0.0),
        ]
        vision_rows.extend(
            _vision_row(12.1 + index * 0.1, 40.0, 0.0)
            for index in range(10)
        )
        vision_rows.extend(
            [
                _vision_row(13.2, 36.0, 2.0),
                _vision_row(13.3, 33.0, 4.0),
                _vision_row(13.4, 28.0, 8.0),
                _vision_row(13.5, 20.0, 12.0),
                _vision_row(13.6, 10.0, 15.0),
                _vision_row(13.7, 0.0, 16.0),
                _vision_row(13.8, -10.0, 15.0),
                _vision_row(13.9, -20.0, 12.0),
                _vision_row(14.0, -28.0, 8.0),
                _vision_row(14.1, -33.0, 4.0),
                _vision_row(14.2, -36.0, 0.0),
                _vision_row(14.3, -33.0, -4.0),
                _vision_row(14.4, -28.0, -8.0),
                _vision_row(14.5, -20.0, -12.0),
                _vision_row(14.6, -10.0, -15.0),
                _vision_row(14.7, 0.0, -16.0),
                _vision_row(14.8, 10.0, -15.0),
                _vision_row(14.9, 20.0, -12.0),
                _vision_row(15.0, 28.0, -8.0),
                _vision_row(15.1, 33.0, -4.0),
                _vision_row(15.2, 38.0, -1.0),
                _vision_row(15.7, 40.0, 0.0),
                _vision_row(16.2, 40.0, 0.0),
                _vision_row(16.7, 40.0, 0.0),
                _vision_row(17.2, 0.0, 0.0),
            ]
        )
        result = _align_circle(main_rows, vision_rows, vision_rows)
        self.assertEqual(result.anchors, ((13300.0, 7000.0),))
        self.assertGreaterEqual(result.diagnostics["end_hold_duration_s"], 1.0)

    def test_interpolation_rejects_large_marker_gap(self) -> None:
        points = [
            VisionPoint(0.0, 0.0, 0.0, 0.0),
            VisionPoint(100.0, 100.0, 1.0, 0.0),
            VisionPoint(800.0, 800.0, 8.0, 0.0),
        ]
        self.assertEqual(
            _interpolate_vision(points, 50.0, max_gap_ms=500.0),
            (0.5, 0.0),
        )
        self.assertIsNone(
            _interpolate_vision(points, 400.0, max_gap_ms=500.0)
        )


if __name__ == "__main__":
    unittest.main()
