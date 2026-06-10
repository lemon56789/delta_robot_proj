from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinematics.forward_kinematics import ForwardKinematicsError, delta_fk


RUN_ID_DATE = "2026-06-06"
TRAJECTORIES: tuple[str, ...] = (
    "cross_pm30",
    "reverse_grid_3x3_pm40",
    "diamond_pm35",
    "circle_r40",
)
REPETITIONS: tuple[str, ...] = ("r01", "r02", "r03")
CORRECTION_STATES: tuple[str, ...] = ("off", "on")
STEP_JUMP_THRESHOLD_MM = 10.0
STEP_MAX_ANCHOR_RESIDUAL_MS = 500.0
CIRCLE_HOME_JUMP_THRESHOLD_MM = 15.0
CIRCLE_DEPARTURE_THRESHOLD_MM = 5.0
CIRCLE_END_HOLD_THRESHOLD_MM = 5.0
CIRCLE_MIN_END_HOLD_S = 1.0
MAX_INTERPOLATION_GAP_MS = 500.0

MERGED_FIELDNAMES: tuple[str, ...] = (
    "time",
    "target_x",
    "target_y",
    "target_z",
    "theta1_cmd",
    "theta2_cmd",
    "theta3_cmd",
    "theta1_meas",
    "theta2_meas",
    "theta3_meas",
    "sim_x",
    "sim_y",
    "sim_z",
    "error_x",
    "error_y",
    "error_z",
)

MEASURED_POSITION_FIELDNAMES: tuple[str, ...] = (
    "run_id",
    "time",
    "measured_x_est",
    "measured_y_est",
    "measured_z_est",
    "estimator_method",
    "valid",
)


@dataclass(frozen=True)
class VisionPoint:
    source_time_ms: float
    aligned_time_ms: float
    x_mm: float
    y_mm: float


@dataclass(frozen=True)
class AlignmentResult:
    points: list[VisionPoint]
    method: str
    anchors: tuple[tuple[float, float], ...]
    source_total_rows: int
    source_valid_rows: int
    diagnostics: dict[str, object]


def main() -> int:
    args = _parse_args()
    run_ids = tuple(args.run_id) if args.run_id else build_run_ids()
    run_results: dict[str, dict[str, object]] = {}
    for run_id in run_ids:
        result = process_run(
            run_id=run_id,
            real_raw_dir=args.real_raw_dir,
            vision_raw_dir=args.vision_raw_dir,
            simulation_raw_dir=args.simulation_raw_dir,
            real_derived_dir=args.real_derived_dir,
            processed_dir=args.processed_dir,
        )
        run_results[run_id] = result
        print(
            f"run_id={run_id} "
            f"merged_rows={result['merged_rows']} "
            f"alignment={result['method']} "
            f"coverage={result['merged_coverage_ratio']:.6f}"
        )

    if set(run_ids) == set(build_run_ids()):
        report = build_comparison_report(
            run_results=run_results,
            real_raw_dir=args.real_raw_dir,
            processed_dir=args.processed_dir,
        )
        _write_json(args.comparison_output, report)
        print(f"comparison_report={args.comparison_output}")
    return 0


def build_run_ids() -> tuple[str, ...]:
    return tuple(
        f"{RUN_ID_DATE}_run02_{trajectory}_{state}_{repetition}"
        for trajectory in TRAJECTORIES
        for state in CORRECTION_STATES
        for repetition in REPETITIONS
    )


def process_run(
    *,
    run_id: str,
    real_raw_dir: Path,
    vision_raw_dir: Path,
    simulation_raw_dir: Path,
    real_derived_dir: Path,
    processed_dir: Path,
) -> dict[str, object]:
    trajectory, correction_state, repetition = parse_run_id(run_id)
    main_path = real_raw_dir / f"main_{run_id}.csv"
    vision_path = vision_raw_dir / f"vision_{run_id}.csv"
    correction_path = real_raw_dir / f"correction_{run_id}.csv"
    sim_path = (
        simulation_raw_dir / f"simscape_run02_nominal_{trajectory}.csv"
    )
    main_rows = _read_csv(main_path)
    vision_rows = _read_csv(vision_path)
    correction_rows = _read_csv(correction_path)
    sim_rows = _read_csv(sim_path)

    if not main_rows or not vision_rows or not correction_rows or not sim_rows:
        raise ValueError(f"Run 02 input contains an empty CSV: {run_id}")
    _validate_run_ids(run_id, main_rows, vision_rows, correction_rows)
    _validate_matching_time_axes(run_id, main_rows, sim_rows, correction_rows)

    sim_by_time = {_time_key(_float(row, "time")): row for row in sim_rows}
    measured_rows = _build_measured_position_rows(
        run_id=run_id,
        main_rows=main_rows,
        sim_by_time=sim_by_time,
    )
    measured_by_time = {
        _time_key(_float(row, "time")): row
        for row in measured_rows
        if _bool(row["valid"])
    }
    alignment = align_vision(
        trajectory=trajectory,
        main_rows=main_rows,
        vision_rows=vision_rows,
    )
    merged_rows = _build_merged_rows(
        main_rows=main_rows,
        sim_by_time=sim_by_time,
        measured_by_time=measured_by_time,
        vision_points=alignment.points,
    )
    if not merged_rows:
        raise ValueError(f"alignment produced no merged rows: {run_id}")

    real_derived_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    measured_path = real_derived_dir / f"measured_position_{run_id}.csv"
    merged_path = processed_dir / f"merged_{run_id}.csv"
    alignment_path = processed_dir / f"alignment_{run_id}.json"
    _write_csv(measured_path, MEASURED_POSITION_FIELDNAMES, measured_rows)
    _write_csv(merged_path, MERGED_FIELDNAMES, merged_rows)
    metrics = calculate_tracking_metrics(merged_rows)
    metadata = {
        "run_id": run_id,
        "trajectory": trajectory,
        "correction": correction_state,
        "repetition": repetition,
        "method": alignment.method,
        "main_csv": str(main_path),
        "vision_csv": str(vision_path),
        "correction_csv": str(correction_path),
        "simscape_csv": str(sim_path),
        "measured_position_csv": str(measured_path),
        "merged_csv": str(merged_path),
        "source_total_vision_rows": alignment.source_total_rows,
        "source_valid_vision_rows": alignment.source_valid_rows,
        "aligned_vision_rows": len(alignment.points),
        "main_rows": len(main_rows),
        "merged_rows": len(merged_rows),
        "merged_coverage_ratio": len(merged_rows) / len(main_rows),
        "max_interpolation_gap_ms": MAX_INTERPOLATION_GAP_MS,
        "anchors": [
            {
                "vision_time_ms": vision_time_ms,
                "main_time_ms": main_time_ms,
            }
            for vision_time_ms, main_time_ms in alignment.anchors
        ],
        "diagnostics": alignment.diagnostics,
        "tracking_metrics": metrics,
    }
    _write_json(alignment_path, metadata)
    return metadata


def parse_run_id(run_id: str) -> tuple[str, str, str]:
    for trajectory in TRAJECTORIES:
        marker = f"_run02_{trajectory}_"
        if marker not in run_id:
            continue
        suffix = run_id.split(marker, 1)[1]
        state, repetition = suffix.rsplit("_", 1)
        if state not in CORRECTION_STATES or repetition not in REPETITIONS:
            break
        return trajectory, state, repetition
    raise ValueError(f"unsupported Run 02 run_id: {run_id}")


def align_vision(
    *,
    trajectory: str,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
) -> AlignmentResult:
    valid_rows = [
        row
        for row in vision_rows
        if _bool(row.get("valid", ""))
        and _bool(row.get("marker_detected", ""))
    ]
    if not valid_rows:
        raise ValueError("vision CSV has no valid marker rows")
    if trajectory == "circle_r40":
        return _align_circle(main_rows, vision_rows, valid_rows)
    return _align_step_trajectory(main_rows, vision_rows, valid_rows)


def _align_step_trajectory(
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
) -> AlignmentResult:
    main_transition_times = _main_transition_times(main_rows)
    events = _vision_jump_events(
        valid_rows,
        threshold_mm=STEP_JUMP_THRESHOLD_MM,
    )
    if len(events) != len(main_transition_times):
        raise ValueError(
            "vision jump count does not match main phase transitions: "
            f"vision={len(events)} main={len(main_transition_times)}"
        )

    first_vision_ms = events[0][0]
    first_main_ms = main_transition_times[0]
    offset_ms = first_main_ms - first_vision_ms
    residuals = [
        (vision_ms + offset_ms) - main_ms
        for (vision_ms, _, _), main_ms in zip(
            events, main_transition_times, strict=True
        )
    ]
    max_abs_residual_ms = max(abs(value) for value in residuals)
    if max_abs_residual_ms > STEP_MAX_ANCHOR_RESIDUAL_MS:
        raise ValueError(
            "step alignment residual exceeds limit: "
            f"{max_abs_residual_ms:.3f} ms"
        )

    points = _offset_points(valid_rows, offset_ms)
    return AlignmentResult(
        points=points,
        method="step_first_jump_offset_with_all_transition_validation",
        anchors=((first_vision_ms, first_main_ms),),
        source_total_rows=len(vision_rows),
        source_valid_rows=len(valid_rows),
        diagnostics={
            "jump_threshold_mm": STEP_JUMP_THRESHOLD_MM,
            "event_count": len(events),
            "main_transition_times_ms": main_transition_times,
            "vision_event_times_ms": [event[0] for event in events],
            "vision_jump_distances_mm": [event[1] for event in events],
            "anchor_residuals_ms": residuals,
            "max_abs_anchor_residual_ms": max_abs_residual_ms,
        },
    )


def _align_circle(
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
) -> AlignmentResult:
    large_events = _vision_jump_events(
        valid_rows,
        threshold_mm=CIRCLE_HOME_JUMP_THRESHOLD_MM,
    )
    if len(large_events) != 2:
        raise ValueError(
            "circle must have home-to-start and end-to-home jumps: "
            f"found={len(large_events)}"
        )

    first_jump_index = large_events[0][2]
    final_jump_index = large_events[-1][2]
    baseline_rows = valid_rows[
        first_jump_index : min(first_jump_index + 10, len(valid_rows))
    ]
    if len(baseline_rows) < 5:
        raise ValueError("circle start hold has too few valid rows")
    baseline_x = statistics.median(_float(row, "vision_x") for row in baseline_rows)
    baseline_y = statistics.median(_float(row, "vision_y") for row in baseline_rows)
    departure_index = _first_persistent_departure(
        valid_rows,
        start_index=first_jump_index + len(baseline_rows),
        baseline_xy=(baseline_x, baseline_y),
        threshold_mm=CIRCLE_DEPARTURE_THRESHOLD_MM,
    )
    vision_departure_ms = _float(
        valid_rows[departure_index], "vision_time"
    ) * 1000.0
    main_motion_start_ms = _first_phase_time(main_rows, "circle_ccw_")
    offset_ms = main_motion_start_ms - vision_departure_ms

    end_hold_start_index = _find_end_hold_start(
        valid_rows=valid_rows,
        departure_index=departure_index,
        final_jump_index=final_jump_index,
        baseline_xy=(baseline_x, baseline_y),
        threshold_mm=CIRCLE_END_HOLD_THRESHOLD_MM,
    )
    end_hold_duration_s = (
        _float(valid_rows[final_jump_index - 1], "vision_time")
        - _float(valid_rows[end_hold_start_index], "vision_time")
    )
    if end_hold_duration_s < CIRCLE_MIN_END_HOLD_S:
        raise ValueError(
            "circle end hold is too short: "
            f"{end_hold_duration_s:.3f} s"
        )

    points = _offset_points(valid_rows, offset_ms)
    return AlignmentResult(
        points=points,
        method="circle_start_hold_departure_offset",
        anchors=((vision_departure_ms, main_motion_start_ms),),
        source_total_rows=len(vision_rows),
        source_valid_rows=len(valid_rows),
        diagnostics={
            "home_jump_threshold_mm": CIRCLE_HOME_JUMP_THRESHOLD_MM,
            "departure_threshold_mm": CIRCLE_DEPARTURE_THRESHOLD_MM,
            "start_hold_baseline_x_mm": baseline_x,
            "start_hold_baseline_y_mm": baseline_y,
            "home_jump_event_times_ms": [event[0] for event in large_events],
            "home_jump_distances_mm": [event[1] for event in large_events],
            "departure_vision_time_ms": vision_departure_ms,
            "motion_main_time_ms": main_motion_start_ms,
            "end_hold_start_vision_time_ms": (
                _float(valid_rows[end_hold_start_index], "vision_time") * 1000.0
            ),
            "end_hold_duration_s": end_hold_duration_s,
        },
    )


def _main_transition_times(main_rows: list[dict[str, str]]) -> list[float]:
    return [
        _float(main_rows[index], "time")
        for index in range(1, len(main_rows))
        if main_rows[index].get("phase") != main_rows[index - 1].get("phase")
    ]


def _first_phase_time(
    main_rows: list[dict[str, str]],
    prefix: str,
) -> float:
    for row in main_rows:
        if row.get("phase", "").startswith(prefix):
            return _float(row, "time")
    raise ValueError(f"main phase prefix not found: {prefix}")


def _vision_jump_events(
    valid_rows: list[dict[str, str]],
    *,
    threshold_mm: float,
) -> list[tuple[float, float, int]]:
    events: list[tuple[float, float, int]] = []
    for index in range(1, len(valid_rows)):
        before = valid_rows[index - 1]
        after = valid_rows[index]
        distance = math.hypot(
            _float(after, "vision_x") - _float(before, "vision_x"),
            _float(after, "vision_y") - _float(before, "vision_y"),
        )
        if distance >= threshold_mm:
            events.append(
                (_float(after, "vision_time") * 1000.0, distance, index)
            )
    return events


def _first_persistent_departure(
    valid_rows: list[dict[str, str]],
    *,
    start_index: int,
    baseline_xy: tuple[float, float],
    threshold_mm: float,
) -> int:
    for index in range(start_index, len(valid_rows) - 1):
        current_distance = _distance_from_row(valid_rows[index], baseline_xy)
        next_distance = _distance_from_row(valid_rows[index + 1], baseline_xy)
        if current_distance >= threshold_mm and next_distance >= threshold_mm:
            return index
    raise ValueError("circle departure event was not detected")


def _find_end_hold_start(
    *,
    valid_rows: list[dict[str, str]],
    departure_index: int,
    final_jump_index: int,
    baseline_xy: tuple[float, float],
    threshold_mm: float,
) -> int:
    if final_jump_index <= departure_index + 1:
        raise ValueError("circle final jump occurs before motion interval")
    index = final_jump_index - 1
    if _distance_from_row(valid_rows[index], baseline_xy) > threshold_mm:
        raise ValueError("circle end hold is not near the start hold position")
    while (
        index > departure_index
        and _distance_from_row(valid_rows[index - 1], baseline_xy)
        <= threshold_mm
    ):
        index -= 1
    return index


def _distance_from_row(
    row: dict[str, str],
    reference_xy: tuple[float, float],
) -> float:
    return math.hypot(
        _float(row, "vision_x") - reference_xy[0],
        _float(row, "vision_y") - reference_xy[1],
    )


def _offset_points(
    valid_rows: list[dict[str, str]],
    offset_ms: float,
) -> list[VisionPoint]:
    return [
        VisionPoint(
            source_time_ms=_float(row, "vision_time") * 1000.0,
            aligned_time_ms=_float(row, "vision_time") * 1000.0 + offset_ms,
            x_mm=_float(row, "vision_x"),
            y_mm=_float(row, "vision_y"),
        )
        for row in valid_rows
    ]


def _build_measured_position_rows(
    *,
    run_id: str,
    main_rows: list[dict[str, str]],
    sim_by_time: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous_position: tuple[float, float, float] | None = None
    for main_row in main_rows:
        main_time = _float(main_row, "time")
        if not _bool(main_row.get("valid", "")):
            rows.append(_invalid_measured_position_row(run_id, main_time))
            continue
        try:
            theta_meas = tuple(
                _float(main_row, f"theta{index}_meas")
                for index in (1, 2, 3)
            )
            sim_row = sim_by_time.get(_time_key(main_time))
            initial_guess = (
                (
                    _float(sim_row, "sim_x"),
                    _float(sim_row, "sim_y"),
                    _float(sim_row, "sim_z"),
                )
                if sim_row is not None
                else previous_position
            )
            measured_position = delta_fk(
                *theta_meas,
                initial_guess_mm=initial_guess,
            ).as_tuple()
            previous_position = measured_position
            rows.append(
                {
                    "run_id": run_id,
                    "time": _format_number(main_time),
                    "measured_x_est": _format_number(measured_position[0]),
                    "measured_y_est": _format_number(measured_position[1]),
                    "measured_z_est": _format_number(measured_position[2]),
                    "estimator_method": "fk_theta_meas_command_echo_no_encoder",
                    "valid": "True",
                }
            )
        except (ValueError, ForwardKinematicsError):
            rows.append(_invalid_measured_position_row(run_id, main_time))
    return rows


def _build_merged_rows(
    *,
    main_rows: list[dict[str, str]],
    sim_by_time: dict[str, dict[str, str]],
    measured_by_time: dict[str, dict[str, object]],
    vision_points: list[VisionPoint],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for main_row in main_rows:
        if not _bool(main_row.get("valid", "")):
            continue
        main_time = _float(main_row, "time")
        key = _time_key(main_time)
        sim_row = sim_by_time.get(key)
        measured_row = measured_by_time.get(key)
        vision_xy = _interpolate_vision(
            vision_points,
            main_time,
            max_gap_ms=MAX_INTERPOLATION_GAP_MS,
        )
        if sim_row is None or measured_row is None or vision_xy is None:
            continue
        sim_x = _float(sim_row, "sim_x")
        sim_y = _float(sim_row, "sim_y")
        sim_z = _float(sim_row, "sim_z")
        measured_z = float(measured_row["measured_z_est"])
        rows.append(
            {
                "time": _format_number(main_time),
                "target_x": main_row["target_x"],
                "target_y": main_row["target_y"],
                "target_z": main_row["target_z"],
                "theta1_cmd": main_row["theta1_cmd"],
                "theta2_cmd": main_row["theta2_cmd"],
                "theta3_cmd": main_row["theta3_cmd"],
                "theta1_meas": main_row["theta1_meas"],
                "theta2_meas": main_row["theta2_meas"],
                "theta3_meas": main_row["theta3_meas"],
                "sim_x": _format_number(sim_x),
                "sim_y": _format_number(sim_y),
                "sim_z": _format_number(sim_z),
                "error_x": _format_number(vision_xy[0] - sim_x),
                "error_y": _format_number(vision_xy[1] - sim_y),
                "error_z": _format_number(measured_z - sim_z),
            }
        )
    return rows


def _interpolate_vision(
    points: list[VisionPoint],
    target_time_ms: float,
    *,
    max_gap_ms: float,
) -> tuple[float, float] | None:
    if not points:
        return None
    if (
        target_time_ms < points[0].aligned_time_ms
        or target_time_ms > points[-1].aligned_time_ms
    ):
        return None
    low = 0
    high = len(points) - 1
    while low <= high:
        middle = (low + high) // 2
        middle_time = points[middle].aligned_time_ms
        if abs(middle_time - target_time_ms) <= 1e-9:
            return points[middle].x_mm, points[middle].y_mm
        if middle_time < target_time_ms:
            low = middle + 1
        else:
            high = middle - 1
    before = points[high]
    after = points[low]
    gap_ms = after.aligned_time_ms - before.aligned_time_ms
    if gap_ms <= 0.0 or gap_ms > max_gap_ms:
        return None
    ratio = (target_time_ms - before.aligned_time_ms) / gap_ms
    return (
        before.x_mm + ratio * (after.x_mm - before.x_mm),
        before.y_mm + ratio * (after.y_mm - before.y_mm),
    )


def calculate_tracking_metrics(
    merged_rows: list[dict[str, object] | dict[str, str]],
) -> dict[str, float | int]:
    errors = [_tracking_error(row) for row in merged_rows]
    if not errors:
        raise ValueError("tracking metrics require at least one row")
    x_values = [value[0] for value in errors]
    y_values = [value[1] for value in errors]
    xy_values = [math.hypot(*value) for value in errors]
    return {
        "row_count": len(errors),
        "tracking_x_rmse": math.sqrt(
            sum(value * value for value in x_values) / len(errors)
        ),
        "tracking_y_rmse": math.sqrt(
            sum(value * value for value in y_values) / len(errors)
        ),
        "tracking_xy_rmse": math.sqrt(
            sum(x * x + y * y for x, y in errors) / len(errors)
        ),
        "tracking_x_mae": sum(abs(value) for value in x_values) / len(errors),
        "tracking_y_mae": sum(abs(value) for value in y_values) / len(errors),
        "tracking_xy_mae": sum(xy_values) / len(errors),
        "tracking_xy_max_error": max(xy_values),
    }


def _tracking_error(
    row: dict[str, object] | dict[str, str],
) -> tuple[float, float]:
    vision_x = float(row["sim_x"]) + float(row["error_x"])
    vision_y = float(row["sim_y"]) + float(row["error_y"])
    return (
        vision_x - float(row["target_x"]),
        vision_y - float(row["target_y"]),
    )


def build_comparison_report(
    *,
    run_results: dict[str, dict[str, object]],
    real_raw_dir: Path,
    processed_dir: Path,
) -> dict[str, object]:
    pairs: list[dict[str, object]] = []
    for trajectory in TRAJECTORIES:
        for repetition in REPETITIONS:
            off_id = (
                f"{RUN_ID_DATE}_run02_{trajectory}_off_{repetition}"
            )
            on_id = f"{RUN_ID_DATE}_run02_{trajectory}_on_{repetition}"
            off_rows = _read_csv(processed_dir / f"merged_{off_id}.csv")
            on_rows = _read_csv(processed_dir / f"merged_{on_id}.csv")
            off_by_time = {_time_key(_float(row, "time")): row for row in off_rows}
            on_by_time = {_time_key(_float(row, "time")): row for row in on_rows}
            common_times = sorted(
                set(off_by_time) & set(on_by_time),
                key=float,
            )
            if not common_times:
                raise ValueError(f"OFF/ON pair has no common rows: {trajectory}")
            off_common = [off_by_time[key] for key in common_times]
            on_common = [on_by_time[key] for key in common_times]
            off_metrics = calculate_tracking_metrics(off_common)
            on_metrics = calculate_tracking_metrics(on_common)
            improvement = {
                metric: _metric_improvement(
                    float(off_metrics[metric]),
                    float(on_metrics[metric]),
                )
                for metric in (
                    "tracking_xy_rmse",
                    "tracking_xy_mae",
                    "tracking_xy_max_error",
                )
            }
            pair = {
                "trajectory": trajectory,
                "repetition": repetition,
                "off_run_id": off_id,
                "on_run_id": on_id,
                "common_row_count": len(common_times),
                "common_start_time_ms": float(common_times[0]),
                "common_end_time_ms": float(common_times[-1]),
                "off_metrics": off_metrics,
                "on_metrics": on_metrics,
                "improvement": improvement,
                "off_alignment": _alignment_summary(run_results[off_id]),
                "on_alignment": _alignment_summary(run_results[on_id]),
                "correction_on": _correction_summary(
                    real_raw_dir / f"correction_{on_id}.csv"
                ),
            }
            pairs.append(pair)

    trajectory_summaries = {
        trajectory: _summarize_pairs(
            [pair for pair in pairs if pair["trajectory"] == trajectory]
        )
        for trajectory in TRAJECTORIES
    }
    overall = _summarize_trajectories(trajectory_summaries)
    return {
        "report_type": "run02_off_on_tracking_comparison",
        "actual_experiment_date": "2026-06-07",
        "run_id_date": RUN_ID_DATE,
        "pair_count": len(pairs),
        "primary_metric": "tracking_xy_rmse",
        "pairing_policy": "same_trajectory_and_repetition_common_timestamps",
        "alignment_policy": {
            "step": "first_vision_jump_offset_all_transitions_validated",
            "circle": "start_hold_departure_offset_no_time_warp",
            "max_interpolation_gap_ms": MAX_INTERPOLATION_GAP_MS,
        },
        "pairs": pairs,
        "trajectory_summaries": trajectory_summaries,
        "overall_equal_trajectory_weight": overall,
    }


def _alignment_summary(result: dict[str, object]) -> dict[str, object]:
    diagnostics = dict(result["diagnostics"])
    return {
        "method": result["method"],
        "merged_rows": result["merged_rows"],
        "merged_coverage_ratio": result["merged_coverage_ratio"],
        "max_abs_anchor_residual_ms": diagnostics.get(
            "max_abs_anchor_residual_ms"
        ),
        "end_hold_duration_s": diagnostics.get("end_hold_duration_s"),
    }


def _correction_summary(path: Path) -> dict[str, float | int]:
    rows = _read_csv(path)
    lags = [_float(row, "schedule_lag_ms") for row in rows]
    clamped_rows = [row for row in rows if _bool(row["correction_clamped"])]
    return {
        "row_count": len(rows),
        "fallback_row_count": sum(_bool(row["fallback_used"]) for row in rows),
        "clamped_row_count": len(clamped_rows),
        "clamped_command_count": sum(
            _bool(row["correction_clamped"]) and _bool(row["command_sent"])
            for row in rows
        ),
        "max_schedule_lag_ms": max(lags),
        "mean_schedule_lag_ms": sum(lags) / len(lags),
    }


def _metric_improvement(off_value: float, on_value: float) -> dict[str, float | None]:
    absolute = off_value - on_value
    percent = None if off_value == 0.0 else 100.0 * absolute / off_value
    return {
        "absolute": absolute,
        "percent": percent,
        "improved": absolute > 0.0,
    }


def _summarize_pairs(pairs: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {"pair_count": len(pairs)}
    for metric in (
        "tracking_xy_rmse",
        "tracking_xy_mae",
        "tracking_xy_max_error",
    ):
        off_values = [
            float(dict(pair["off_metrics"])[metric]) for pair in pairs
        ]
        on_values = [
            float(dict(pair["on_metrics"])[metric]) for pair in pairs
        ]
        absolute_values = [
            float(dict(dict(pair["improvement"])[metric])["absolute"])
            for pair in pairs
        ]
        percent_values = [
            float(dict(dict(pair["improvement"])[metric])["percent"])
            for pair in pairs
            if dict(dict(pair["improvement"])[metric])["percent"] is not None
        ]
        summary[metric] = {
            "off_mean": statistics.mean(off_values),
            "off_population_std": statistics.pstdev(off_values),
            "on_mean": statistics.mean(on_values),
            "on_population_std": statistics.pstdev(on_values),
            "absolute_improvement_mean": statistics.mean(absolute_values),
            "improvement_percent_mean": statistics.mean(percent_values),
            "improved_pair_count": sum(value > 0.0 for value in absolute_values),
        }
    return summary


def _summarize_trajectories(
    trajectory_summaries: dict[str, dict[str, object]],
) -> dict[str, object]:
    summary: dict[str, object] = {"trajectory_count": len(trajectory_summaries)}
    for metric in (
        "tracking_xy_rmse",
        "tracking_xy_mae",
        "tracking_xy_max_error",
    ):
        metric_summaries = [
            dict(trajectory_summaries[trajectory][metric])
            for trajectory in TRAJECTORIES
        ]
        summary[metric] = {
            "off_mean": statistics.mean(
                float(item["off_mean"]) for item in metric_summaries
            ),
            "on_mean": statistics.mean(
                float(item["on_mean"]) for item in metric_summaries
            ),
            "absolute_improvement_mean": statistics.mean(
                float(item["absolute_improvement_mean"])
                for item in metric_summaries
            ),
            "improvement_percent_mean": statistics.mean(
                float(item["improvement_percent_mean"])
                for item in metric_summaries
            ),
            "improved_trajectory_count": sum(
                float(item["absolute_improvement_mean"]) > 0.0
                for item in metric_summaries
            ),
        }
    return summary


def _validate_run_ids(
    run_id: str,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    correction_rows: list[dict[str, str]],
) -> None:
    for name, rows in (
        ("main", main_rows),
        ("vision", vision_rows),
        ("correction", correction_rows),
    ):
        if any(row.get("run_id") != run_id for row in rows):
            raise ValueError(f"{name} run_id mismatch: {run_id}")


def _validate_matching_time_axes(
    run_id: str,
    main_rows: list[dict[str, str]],
    sim_rows: list[dict[str, str]],
    correction_rows: list[dict[str, str]],
) -> None:
    main_times = [_time_key(_float(row, "time")) for row in main_rows]
    sim_times = [_time_key(_float(row, "time")) for row in sim_rows]
    correction_times = [
        _time_key(_float(row, "time")) for row in correction_rows
    ]
    if main_times != sim_times or main_times != correction_times:
        raise ValueError(f"Run 02 time axes do not match: {run_id}")


def _invalid_measured_position_row(
    run_id: str,
    time_ms: float,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "time": _format_number(time_ms),
        "measured_x_est": "",
        "measured_y_est": "",
        "measured_z_est": "",
        "estimator_method": "fk_theta_meas_command_echo_no_encoder",
        "valid": "False",
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        return [dict(row) for row in reader]


def _write_csv(
    path: Path,
    fieldnames: Iterable[str],
    rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=tuple(fieldnames),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, content: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(content, json_file, ensure_ascii=True, indent=2)
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


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.15g}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Align, merge, and compare the finalized Run 02 dataset."
    )
    parser.add_argument("--run-id", action="append")
    parser.add_argument(
        "--real-raw-dir",
        type=Path,
        default=Path("data/real/raw"),
    )
    parser.add_argument(
        "--vision-raw-dir",
        type=Path,
        default=Path("data/vision/raw"),
    )
    parser.add_argument(
        "--simulation-raw-dir",
        type=Path,
        default=Path("data/simulation/raw"),
    )
    parser.add_argument(
        "--real-derived-dir",
        type=Path,
        default=Path("data/real/derived"),
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
    )
    parser.add_argument(
        "--comparison-output",
        type=Path,
        default=Path(
            "experiments/results/run02_comparison_2026-06-07.json"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
