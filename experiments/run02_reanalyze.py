from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
from typing import Iterable

import numpy as np


RUN_ID_DATE = "2026-06-06"
ACTUAL_EXPERIMENT_DATE = "2026-06-07"
TRAJECTORIES = (
    "cross_pm30",
    "reverse_grid_3x3_pm40",
    "diamond_pm35",
    "circle_r40",
)
REPETITIONS = ("r01", "r02", "r03")
SERVO_CENTER_COMMANDS = (84, 86, 88)
SERVO_SIGNS = (-1, -1, -1)
SERVO_THETA_GAINS = (1.25, 1.25, 1.25)
TRANSITION_WINDOW_MS = 1000.0
CIRCLE_SHIFT_MIN_MS = -1000
CIRCLE_SHIFT_MAX_MS = 1000
CIRCLE_SHIFT_STEP_MS = 50
CIRCLE_NOMINAL_RADIUS_MM = 40.0


def main() -> int:
    args = _parse_args()
    report = build_reanalysis_report(
        real_raw_dir=args.real_raw_dir,
        processed_dir=args.processed_dir,
        comparison_path=args.comparison_report,
    )
    _write_json(args.output, report)
    print(f"pair_count={report['pair_count']}")
    print(f"output={args.output}")
    return 0


def build_reanalysis_report(
    *,
    real_raw_dir: Path,
    processed_dir: Path,
    comparison_path: Path,
) -> dict[str, object]:
    comparison = _read_json(comparison_path)
    official_pairs = {
        (str(pair["trajectory"]), str(pair["repetition"])): pair
        for pair in comparison["pairs"]
    }
    pairs: list[dict[str, object]] = []
    for trajectory in TRAJECTORIES:
        for repetition in REPETITIONS:
            off_id = _run_id(trajectory, "off", repetition)
            on_id = _run_id(trajectory, "on", repetition)
            off = load_run(
                run_id=off_id,
                real_raw_dir=real_raw_dir,
                processed_dir=processed_dir,
            )
            on = load_run(
                run_id=on_id,
                real_raw_dir=real_raw_dir,
                processed_dir=processed_dir,
            )
            pair = analyze_pair(
                trajectory=trajectory,
                repetition=repetition,
                off=off,
                on=on,
            )
            official = official_pairs[(trajectory, repetition)]
            pair["official_absolute_rmse_check"] = {
                "off_difference_mm": (
                    float(pair["absolute"]["off"]["tracking_xy_rmse"])
                    - float(official["off_metrics"]["tracking_xy_rmse"])
                ),
                "on_difference_mm": (
                    float(pair["absolute"]["on"]["tracking_xy_rmse"])
                    - float(official["on_metrics"]["tracking_xy_rmse"])
                ),
            }
            pairs.append(pair)

    trajectory_summaries = {
        trajectory: summarize_trajectory(
            [pair for pair in pairs if pair["trajectory"] == trajectory]
        )
        for trajectory in TRAJECTORIES
    }
    return {
        "report_type": "run02_existing_data_reanalysis",
        "actual_experiment_date": ACTUAL_EXPERIMENT_DATE,
        "run_id_date": RUN_ID_DATE,
        "pair_count": len(pairs),
        "policies": {
            "home_offset": (
                "median vision-minus-target vector over each run initial "
                "home_1 phase"
            ),
            "home_normalized": (
                "subtract each run initial home offset from all vision XY"
            ),
            "step_segments": {
                "transition": (
                    f"first {int(TRANSITION_WINDOW_MS)} ms after each "
                    "non-initial phase start"
                ),
                "stable": (
                    f"remaining samples after {int(TRANSITION_WINDOW_MS)} ms"
                ),
                "initial_home_excluded": True,
            },
            "servo_projection": {
                "mapping": (
                    "round(center + sign * theta * gain), matching firmware"
                ),
                "centers": SERVO_CENTER_COMMANDS,
                "signs": SERVO_SIGNS,
                "theta_gains": SERVO_THETA_GAINS,
                "actual_source": "main theta*_cmd recorded for transmitted command",
            },
            "circle": {
                "official_metric_preserved": True,
                "shift_sweep_ms": [
                    CIRCLE_SHIFT_MIN_MS,
                    CIRCLE_SHIFT_MAX_MS,
                    CIRCLE_SHIFT_STEP_MS,
                ],
                "shift_metric_is_diagnostic_only": True,
            },
        },
        "pairs": pairs,
        "trajectory_summaries": trajectory_summaries,
        "overall_equal_trajectory_weight": summarize_overall(
            trajectory_summaries
        ),
    }


def load_run(
    *,
    run_id: str,
    real_raw_dir: Path,
    processed_dir: Path,
) -> dict[str, object]:
    merged = _read_csv(processed_dir / f"merged_{run_id}.csv")
    main_rows = _read_csv(real_raw_dir / f"main_{run_id}.csv")
    correction_rows = _read_csv(real_raw_dir / f"correction_{run_id}.csv")
    main_by_time = {_time_key(_float(row, "time")): row for row in main_rows}
    enriched: list[dict[str, object]] = []
    phase_starts: dict[str, float] = {}
    previous_phase: str | None = None
    for main_row in main_rows:
        phase = main_row["phase"]
        if phase != previous_phase:
            phase_starts[phase] = _float(main_row, "time")
            previous_phase = phase
    for row in merged:
        key = _time_key(_float(row, "time"))
        main_row = main_by_time.get(key)
        if main_row is None:
            raise ValueError(f"merged time is absent from main CSV: {run_id} {key}")
        phase = main_row["phase"]
        enriched.append(
            {
                **row,
                "phase": phase,
                "phase_elapsed_ms": _float(row, "time") - phase_starts[phase],
                "vision_x": _float(row, "sim_x") + _float(row, "error_x"),
                "vision_y": _float(row, "sim_y") + _float(row, "error_y"),
            }
        )
    return {
        "run_id": run_id,
        "rows": enriched,
        "main_rows": main_rows,
        "correction_rows": correction_rows,
        "home_offset": initial_home_offset(enriched),
    }


def analyze_pair(
    *,
    trajectory: str,
    repetition: str,
    off: dict[str, object],
    on: dict[str, object],
) -> dict[str, object]:
    off_rows, on_rows = common_rows(
        list(off["rows"]),
        list(on["rows"]),
    )
    off_home = tuple(off["home_offset"])
    on_home = tuple(on["home_offset"])
    absolute_off = tracking_metrics(off_rows)
    absolute_on = tracking_metrics(on_rows)
    normalized_off = tracking_metrics(off_rows, offset_xy=off_home)
    normalized_on = tracking_metrics(on_rows, offset_xy=on_home)
    result: dict[str, object] = {
        "trajectory": trajectory,
        "repetition": repetition,
        "off_run_id": off["run_id"],
        "on_run_id": on["run_id"],
        "common_row_count": len(off_rows),
        "home": {
            "off_offset_xy_mm": off_home,
            "on_offset_xy_mm": on_home,
            "on_minus_off_xy_mm": (
                on_home[0] - off_home[0],
                on_home[1] - off_home[1],
            ),
            "shift_norm_mm": math.hypot(
                on_home[0] - off_home[0],
                on_home[1] - off_home[1],
            ),
        },
        "absolute": metric_comparison(absolute_off, absolute_on),
        "home_normalized": metric_comparison(normalized_off, normalized_on),
        "actuator_command": actuator_command_summary(
            main_rows=list(on["main_rows"]),
            correction_rows=list(on["correction_rows"]),
        ),
    }
    if trajectory == "circle_r40":
        result["circle"] = {
            "off": circle_diagnostics(off_rows),
            "on": circle_diagnostics(on_rows),
        }
    else:
        result["step_segments"] = step_segment_comparison(
            off_rows,
            on_rows,
            off_offset_xy=off_home,
            on_offset_xy=on_home,
        )
    return result


def common_rows(
    off_rows: list[dict[str, object]],
    on_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    off_by_time = {_time_key(_float(row, "time")): row for row in off_rows}
    on_by_time = {_time_key(_float(row, "time")): row for row in on_rows}
    keys = sorted(set(off_by_time) & set(on_by_time), key=float)
    if not keys:
        raise ValueError("OFF/ON pair has no common timestamps")
    return [off_by_time[key] for key in keys], [on_by_time[key] for key in keys]


def initial_home_offset(
    rows: list[dict[str, object]],
) -> tuple[float, float]:
    home_rows = [row for row in rows if row["phase"] == "home_1"]
    if not home_rows:
        raise ValueError("run has no aligned initial home rows")
    return (
        statistics.median(
            _float(row, "vision_x") - _float(row, "target_x")
            for row in home_rows
        ),
        statistics.median(
            _float(row, "vision_y") - _float(row, "target_y")
            for row in home_rows
        ),
    )


def tracking_metrics(
    rows: list[dict[str, object]],
    *,
    offset_xy: tuple[float, float] = (0.0, 0.0),
) -> dict[str, float | int]:
    errors = [
        (
            _float(row, "vision_x") - offset_xy[0] - _float(row, "target_x"),
            _float(row, "vision_y") - offset_xy[1] - _float(row, "target_y"),
        )
        for row in rows
    ]
    if not errors:
        raise ValueError("tracking metric requires rows")
    norms = [math.hypot(x, y) for x, y in errors]
    return {
        "row_count": len(errors),
        "tracking_x_rmse": math.sqrt(
            sum(x * x for x, _ in errors) / len(errors)
        ),
        "tracking_y_rmse": math.sqrt(
            sum(y * y for _, y in errors) / len(errors)
        ),
        "tracking_xy_rmse": math.sqrt(
            sum(x * x + y * y for x, y in errors) / len(errors)
        ),
        "tracking_xy_mae": statistics.mean(norms),
        "tracking_xy_max_error": max(norms),
    }


def metric_comparison(
    off: dict[str, float | int],
    on: dict[str, float | int],
) -> dict[str, object]:
    return {
        "off": off,
        "on": on,
        "improvement": {
            metric: improvement(float(off[metric]), float(on[metric]))
            for metric in (
                "tracking_xy_rmse",
                "tracking_xy_mae",
                "tracking_xy_max_error",
            )
        },
    }


def improvement(off_value: float, on_value: float) -> dict[str, float | bool | None]:
    absolute = off_value - on_value
    return {
        "absolute_mm": absolute,
        "percent": None if off_value == 0.0 else 100.0 * absolute / off_value,
        "improved": absolute > 0.0,
    }


def step_segment_comparison(
    off_rows: list[dict[str, object]],
    on_rows: list[dict[str, object]],
    *,
    off_offset_xy: tuple[float, float],
    on_offset_xy: tuple[float, float],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for segment in ("transition", "stable"):
        off_segment = [
            row for row in off_rows if classify_step_segment(row) == segment
        ]
        on_segment = [
            row for row in on_rows if classify_step_segment(row) == segment
        ]
        result[segment] = {
            "absolute": metric_comparison(
                tracking_metrics(off_segment),
                tracking_metrics(on_segment),
            ),
            "home_normalized": metric_comparison(
                tracking_metrics(off_segment, offset_xy=off_offset_xy),
                tracking_metrics(on_segment, offset_xy=on_offset_xy),
            ),
        }
    return result


def classify_step_segment(row: dict[str, object]) -> str:
    if row["phase"] == "home_1":
        return "initial_home"
    if _float(row, "phase_elapsed_ms") < TRANSITION_WINDOW_MS:
        return "transition"
    return "stable"


def actuator_command_summary(
    *,
    main_rows: list[dict[str, str]],
    correction_rows: list[dict[str, str]],
) -> dict[str, object]:
    main_by_time = {_time_key(_float(row, "time")): row for row in main_rows}
    command_rows = [
        row for row in correction_rows if _bool(row["command_sent"])
    ]
    actual_changed = 0
    theoretical_changed = 0
    changed_axes = [0, 0, 0]
    theoretical_changed_axes = [0, 0, 0]
    for row in command_rows:
        main_row = main_by_time[_time_key(_float(row, "time"))]
        nominal_theta = tuple(
            _float(row, f"nominal_theta{index}") for index in (1, 2, 3)
        )
        theoretical_theta = tuple(
            _float(row, f"corrected_theta{index}") for index in (1, 2, 3)
        )
        transmitted_theta = tuple(
            _float(main_row, f"theta{index}_cmd") for index in (1, 2, 3)
        )
        nominal_servo = project_servo_commands(nominal_theta)
        theoretical_servo = project_servo_commands(theoretical_theta)
        actual_servo = project_servo_commands(transmitted_theta)
        actual_axis_diff = [
            actual != nominal
            for actual, nominal in zip(actual_servo, nominal_servo, strict=True)
        ]
        theoretical_axis_diff = [
            actual != nominal
            for actual, nominal in zip(
                theoretical_servo,
                nominal_servo,
                strict=True,
            )
        ]
        actual_changed += any(actual_axis_diff)
        theoretical_changed += any(theoretical_axis_diff)
        changed_axes = [
            count + int(changed)
            for count, changed in zip(
                changed_axes,
                actual_axis_diff,
                strict=True,
            )
        ]
        theoretical_changed_axes = [
            count + int(changed)
            for count, changed in zip(
                theoretical_changed_axes,
                theoretical_axis_diff,
                strict=True,
            )
        ]
    count = len(command_rows)
    if count == 0:
        raise ValueError("correction log has no command rows")
    return {
        "command_event_count": count,
        "actual_integer_servo_changed_count": actual_changed,
        "actual_integer_servo_changed_ratio": actual_changed / count,
        "actual_axis_changed_ratio": [
            value / count for value in changed_axes
        ],
        "theoretical_fractional_servo_changed_count": theoretical_changed,
        "theoretical_fractional_servo_changed_ratio": (
            theoretical_changed / count
        ),
        "theoretical_axis_changed_ratio": [
            value / count for value in theoretical_changed_axes
        ],
    }


def project_servo_commands(
    theta_deg: Iterable[float],
) -> tuple[int, int, int]:
    values = tuple(float(value) for value in theta_deg)
    if len(values) != 3:
        raise ValueError("theta must have three values")
    return tuple(
        c_round(center + sign * theta * gain)
        for center, sign, theta, gain in zip(
            SERVO_CENTER_COMMANDS,
            SERVO_SIGNS,
            values,
            SERVO_THETA_GAINS,
            strict=True,
        )
    )


def c_round(value: float) -> int:
    if value >= 0.0:
        return math.floor(value + 0.5)
    return math.ceil(value - 0.5)


def circle_diagnostics(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    motion = [
        row for row in rows if str(row["phase"]).startswith("circle_ccw_")
    ]
    if len(motion) < 10:
        raise ValueError("circle diagnostics require motion rows")
    vision_xy = np.asarray(
        [
            [_float(row, "vision_x"), _float(row, "vision_y")]
            for row in motion
        ],
        dtype=np.float64,
    )
    target_xy = np.asarray(
        [
            [_float(row, "target_x"), _float(row, "target_y")]
            for row in motion
        ],
        dtype=np.float64,
    )
    times = np.asarray(
        [_float(row, "time") for row in motion],
        dtype=np.float64,
    )
    center_x, center_y, fitted_radius = fit_circle(vision_xy)
    target_radius = np.linalg.norm(target_xy, axis=1)
    radial_unit = target_xy / target_radius[:, None]
    tangential_unit = np.column_stack((-radial_unit[:, 1], radial_unit[:, 0]))
    tracking_error = vision_xy - target_xy
    radial_error = np.sum(tracking_error * radial_unit, axis=1)
    tangential_error = np.sum(tracking_error * tangential_unit, axis=1)

    measured_angle = np.unwrap(
        np.arctan2(
            vision_xy[:, 1] - center_y,
            vision_xy[:, 0] - center_x,
        )
    )
    target_angle = np.unwrap(np.arctan2(target_xy[:, 1], target_xy[:, 0]))
    phase_error = measured_angle - target_angle
    phase_error -= 2.0 * math.pi * round(
        float(np.median(phase_error)) / (2.0 * math.pi)
    )
    duration_ms = float(times[-1] - times[0])
    median_phase_error_rad = float(np.median(phase_error))
    angular_lag_ms = (
        median_phase_error_rad / (2.0 * math.pi) * duration_ms
    )
    shift = best_circle_shift(
        times=times,
        vision_xy=vision_xy,
        target_times=times,
        target_xy=target_xy,
    )
    radius_deviation = (
        np.linalg.norm(
            vision_xy - np.asarray([center_x, center_y]),
            axis=1,
        )
        - CIRCLE_NOMINAL_RADIUS_MM
    )
    return {
        "row_count": len(motion),
        "fitted_center_xy_mm": [center_x, center_y],
        "fitted_radius_mm": fitted_radius,
        "path_radius_deviation_rmse_mm": _rms(radius_deviation),
        "target_frame_radial_error": vector_metrics(radial_error),
        "target_frame_tangential_error": vector_metrics(tangential_error),
        "phase_error": {
            "median_deg": math.degrees(median_phase_error_rad),
            "rmse_deg": math.degrees(_rms(phase_error)),
            "equivalent_median_lag_ms": angular_lag_ms,
        },
        "shift_sweep": shift,
    }


def fit_circle(points: np.ndarray) -> tuple[float, float, float]:
    if points.ndim != 2 or points.shape[1] != 2 or points.shape[0] < 3:
        raise ValueError("circle fit requires Nx2 points")
    matrix = np.column_stack(
        (2.0 * points[:, 0], 2.0 * points[:, 1], np.ones(len(points)))
    )
    rhs = np.sum(points * points, axis=1)
    solution, _, _, _ = np.linalg.lstsq(matrix, rhs, rcond=None)
    center_x, center_y, constant = (float(value) for value in solution)
    radius_sq = constant + center_x * center_x + center_y * center_y
    if radius_sq <= 0.0:
        raise ValueError("circle fit produced non-positive radius")
    return center_x, center_y, math.sqrt(radius_sq)


def best_circle_shift(
    *,
    times: np.ndarray,
    vision_xy: np.ndarray,
    target_times: np.ndarray,
    target_xy: np.ndarray,
) -> dict[str, float | int]:
    best_shift = 0
    best_rmse = math.inf
    best_count = 0
    for shift_ms in range(
        CIRCLE_SHIFT_MIN_MS,
        CIRCLE_SHIFT_MAX_MS + CIRCLE_SHIFT_STEP_MS,
        CIRCLE_SHIFT_STEP_MS,
    ):
        query_times = times + shift_ms
        valid = (
            (query_times >= target_times[0])
            & (query_times <= target_times[-1])
        )
        if int(valid.sum()) < 10:
            continue
        target_x = np.interp(query_times[valid], target_times, target_xy[:, 0])
        target_y = np.interp(query_times[valid], target_times, target_xy[:, 1])
        errors = vision_xy[valid] - np.column_stack((target_x, target_y))
        rmse = math.sqrt(float(np.mean(np.sum(errors * errors, axis=1))))
        if rmse < best_rmse:
            best_shift = shift_ms
            best_rmse = rmse
            best_count = int(valid.sum())
    return {
        "best_target_time_shift_ms": best_shift,
        "best_tracking_xy_rmse_mm": best_rmse,
        "row_count": best_count,
    }


def vector_metrics(values: np.ndarray) -> dict[str, float]:
    return {
        "mean_mm": float(np.mean(values)),
        "rmse_mm": _rms(values),
        "mae_mm": float(np.mean(np.abs(values))),
    }


def summarize_trajectory(
    pairs: list[dict[str, object]],
) -> dict[str, object]:
    summary: dict[str, object] = {"pair_count": len(pairs)}
    for metric_group in ("absolute", "home_normalized"):
        off_values = [
            float(pair[metric_group]["off"]["tracking_xy_rmse"])
            for pair in pairs
        ]
        on_values = [
            float(pair[metric_group]["on"]["tracking_xy_rmse"])
            for pair in pairs
        ]
        summary[metric_group] = {
            "tracking_xy_rmse": {
                "off_mean_mm": statistics.mean(off_values),
                "on_mean_mm": statistics.mean(on_values),
                "improvement": improvement(
                    statistics.mean(off_values),
                    statistics.mean(on_values),
                ),
                "improved_pair_count": sum(
                    on_value < off_value
                    for off_value, on_value in zip(
                        off_values,
                        on_values,
                        strict=True,
                    )
                ),
            }
        }
    actuator_ratios = [
        float(pair["actuator_command"]["actual_integer_servo_changed_ratio"])
        for pair in pairs
    ]
    theoretical_ratios = [
        float(
            pair["actuator_command"][
                "theoretical_fractional_servo_changed_ratio"
            ]
        )
        for pair in pairs
    ]
    summary["actuator_command"] = {
        "actual_integer_servo_changed_ratio_mean": statistics.mean(
            actuator_ratios
        ),
        "theoretical_fractional_servo_changed_ratio_mean": statistics.mean(
            theoretical_ratios
        ),
    }
    if pairs[0]["trajectory"] == "circle_r40":
        summary["circle"] = {
            state: summarize_circle(pairs, state=state)
            for state in ("off", "on")
        }
    else:
        summary["step_segments"] = {
            segment: summarize_segment(pairs, segment=segment)
            for segment in ("transition", "stable")
        }
    return summary


def summarize_segment(
    pairs: list[dict[str, object]],
    *,
    segment: str,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for metric_group in ("absolute", "home_normalized"):
        off_values = [
            float(
                pair["step_segments"][segment][metric_group]["off"][
                    "tracking_xy_rmse"
                ]
            )
            for pair in pairs
        ]
        on_values = [
            float(
                pair["step_segments"][segment][metric_group]["on"][
                    "tracking_xy_rmse"
                ]
            )
            for pair in pairs
        ]
        result[metric_group] = {
            "off_mean_mm": statistics.mean(off_values),
            "on_mean_mm": statistics.mean(on_values),
            "improvement": improvement(
                statistics.mean(off_values),
                statistics.mean(on_values),
            ),
        }
    return result


def summarize_circle(
    pairs: list[dict[str, object]],
    *,
    state: str,
) -> dict[str, float]:
    diagnostics = [pair["circle"][state] for pair in pairs]
    return {
        "fitted_radius_mean_mm": statistics.mean(
            float(item["fitted_radius_mm"]) for item in diagnostics
        ),
        "radial_rmse_mean_mm": statistics.mean(
            float(item["target_frame_radial_error"]["rmse_mm"])
            for item in diagnostics
        ),
        "tangential_rmse_mean_mm": statistics.mean(
            float(item["target_frame_tangential_error"]["rmse_mm"])
            for item in diagnostics
        ),
        "tangential_mean_mm": statistics.mean(
            float(item["target_frame_tangential_error"]["mean_mm"])
            for item in diagnostics
        ),
        "phase_lag_mean_ms": statistics.mean(
            float(item["phase_error"]["equivalent_median_lag_ms"])
            for item in diagnostics
        ),
        "best_shift_mean_ms": statistics.mean(
            float(item["shift_sweep"]["best_target_time_shift_ms"])
            for item in diagnostics
        ),
        "best_shift_rmse_mean_mm": statistics.mean(
            float(item["shift_sweep"]["best_tracking_xy_rmse_mm"])
            for item in diagnostics
        ),
    }


def summarize_overall(
    trajectory_summaries: dict[str, dict[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for metric_group in ("absolute", "home_normalized"):
        off_values = [
            float(
                trajectory_summaries[trajectory][metric_group][
                    "tracking_xy_rmse"
                ]["off_mean_mm"]
            )
            for trajectory in TRAJECTORIES
        ]
        on_values = [
            float(
                trajectory_summaries[trajectory][metric_group][
                    "tracking_xy_rmse"
                ]["on_mean_mm"]
            )
            for trajectory in TRAJECTORIES
        ]
        result[metric_group] = {
            "off_mean_mm": statistics.mean(off_values),
            "on_mean_mm": statistics.mean(on_values),
            "improvement": improvement(
                statistics.mean(off_values),
                statistics.mean(on_values),
            ),
        }
    return result


def _run_id(trajectory: str, state: str, repetition: str) -> str:
    return f"{RUN_ID_DATE}_run02_{trajectory}_{state}_{repetition}"


def _rms(values: np.ndarray) -> float:
    return math.sqrt(float(np.mean(values * values)))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def _read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as json_file:
        return json.load(json_file)


def _write_json(path: Path, content: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as json_file:
        json.dump(content, json_file, indent=2, ensure_ascii=True)
        json_file.write("\n")


def _float(row: dict[str, object] | dict[str, str], column: str) -> float:
    value = float(row[column])
    if not math.isfinite(value):
        raise ValueError(f"non-finite value in column {column}")
    return value


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _time_key(value: float) -> str:
    return f"{value:.9f}".rstrip("0").rstrip(".")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reanalyze Run 02 without modifying existing datasets."
    )
    parser.add_argument(
        "--real-raw-dir",
        type=Path,
        default=Path("data/real/raw"),
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
    )
    parser.add_argument(
        "--comparison-report",
        type=Path,
        default=Path(
            "experiments/results/run02_comparison_2026-06-07.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "experiments/results/run02_reanalysis_2026-06-07.json"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
