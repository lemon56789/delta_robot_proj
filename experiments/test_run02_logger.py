from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from experiments.run02_logger import (
    TRAJECTORIES,
    build_run_manifest,
    build_schedule,
    build_trajectory_points,
    load_simscape_schedule,
)


COMMON = {
    "target_z_mm": -263.27731514697575,
    "hold_s": 5.0,
    "circle_endpoint_hold_s": 2.0,
    "circle_points": 72,
    "circle_duration_s": 30.0,
    "theta_min_deg": -45.0,
    "theta_max_deg": 90.0,
}


class Run02LoggerTest(unittest.TestCase):
    def test_manifest_has_24_unique_runs_and_paired_order(self) -> None:
        runs = build_run_manifest(run_date="2026-06-07")
        self.assertEqual(len(runs), 24)
        self.assertEqual(len({run["run_id"] for run in runs}), 24)
        for index in range(0, len(runs), 2):
            off = runs[index]
            on = runs[index + 1]
            self.assertEqual(off["trajectory"], on["trajectory"])
            self.assertEqual(off["repetition"], on["repetition"])
            self.assertEqual(off["correction"], "off")
            self.assertEqual(on["correction"], "on")

    def test_all_trajectories_build_strict_schedules(self) -> None:
        for trajectory in TRAJECTORIES:
            points = build_trajectory_points(
                trajectory=trajectory,
                **COMMON,
            )
            schedule = build_schedule(points, sample_period_s=0.1)
            times = [row.time_ms for row in schedule]
            self.assertTrue(all(b > a for a, b in zip(times, times[1:])))
            self.assertTrue(
                all(
                    -45.0 <= theta <= 90.0
                    for row in schedule
                    for theta in row.nominal_theta_deg
                )
            )

    def test_reverse_grid_is_exact_reverse_definition(self) -> None:
        points = build_trajectory_points(
            trajectory="reverse_grid_3x3_pm40",
            **COMMON,
        )
        xy = [(point.target_x, point.target_y) for point in points]
        self.assertEqual(
            xy,
            [
                (0.0, 0.0),
                (40.0, 40.0),
                (0.0, 40.0),
                (-40.0, 40.0),
                (40.0, 0.0),
                (0.0, 0.0),
                (-40.0, 0.0),
                (40.0, -40.0),
                (0.0, -40.0),
                (-40.0, -40.0),
                (0.0, 0.0),
            ],
        )

    def test_circle_has_distinct_start_and_end_holds(self) -> None:
        points = build_trajectory_points(
            trajectory="circle_r40",
            **COMMON,
        )
        self.assertEqual(points[1].phase, "circle_start_hold")
        self.assertEqual(points[1].hold_s, 2.0)
        self.assertEqual(points[-2].phase, "circle_end_hold")
        self.assertEqual(points[-2].hold_s, 2.0)
        self.assertEqual(
            (points[1].target_x, points[1].target_y),
            (40.0, 0.0),
        )
        self.assertEqual(
            (points[-2].target_x, points[-2].target_y),
            (40.0, 0.0),
        )

    def test_simscape_time_axis_must_match_exactly(self) -> None:
        points = build_trajectory_points(
            trajectory="diamond_pm35",
            **COMMON,
        )
        schedule = build_schedule(points, sample_period_s=0.1)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sim.csv"
            with path.open("w", encoding="utf-8", newline="") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["time", "sim_x", "sim_y", "sim_z"],
                )
                writer.writeheader()
                for row in schedule[:-1]:
                    writer.writerow(
                        {
                            "time": row.time_ms,
                            "sim_x": 0.0,
                            "sim_y": 0.0,
                            "sim_z": COMMON["target_z_mm"],
                        }
                    )
            with self.assertRaises(ValueError):
                load_simscape_schedule(
                    path,
                    expected_times_ms=[row.time_ms for row in schedule],
                )


if __name__ == "__main__":
    unittest.main()
