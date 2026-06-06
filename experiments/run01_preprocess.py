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


RUN_IDS: tuple[str, ...] = (
    "2026-06-05_run01_pre_static_center_r01",
    "2026-06-05_run01_pre_cross_pm40_r01",
    "2026-06-05_run01_pre_square_pm40_r01",
)

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
class TimeSeriesPoint:
    time_ms: float
    values: tuple[float, ...]


@dataclass(frozen=True)
class PhaseSegment:
    phase: str
    start_time_ms: float
    end_time_ms: float


@dataclass(frozen=True)
class AlignmentResult:
    points: list[TimeSeriesPoint]
    method: str
    anchors: tuple[tuple[float, float], ...]
    source_valid_rows: int
    source_total_rows: int


def main() -> int:
    args = _parse_args()
    run_ids = tuple(args.run_id) if args.run_id else RUN_IDS

    for run_id in run_ids:
        result = process_run_id(
            run_id=run_id,
            real_raw_dir=args.real_raw_dir,
            vision_raw_dir=args.vision_raw_dir,
            simulation_raw_dir=args.simulation_raw_dir,
            real_derived_dir=args.real_derived_dir,
            processed_dir=args.processed_dir,
        )
        print(
            f"run_id={run_id} "
            f"measured_rows={result['measured_rows']} "
            f"merged_rows={result['merged_rows']} "
            f"main_rows={result['main_rows']} "
            f"vision_valid_rows={result['vision_valid_rows']} "
            f"alignment_method={result['alignment_method']}"
        )
    return 0


def process_run_id(
    *,
    run_id: str,
    real_raw_dir: Path,
    vision_raw_dir: Path,
    simulation_raw_dir: Path,
    real_derived_dir: Path,
    processed_dir: Path,
) -> dict[str, int | str]:
    main_path = real_raw_dir / f"main_{run_id}.csv"
    vision_path = vision_raw_dir / f"vision_{run_id}.csv"
    sim_path = _resolve_simscape_path(
        run_id=run_id,
        simulation_raw_dir=simulation_raw_dir,
    )
    main_rows = _read_csv(main_path)
    vision_rows = _read_csv(vision_path)
    sim_rows = _read_csv(sim_path)

    if not main_rows:
        raise ValueError(f"main CSV has no rows for run_id={run_id}")
    if not sim_rows:
        raise ValueError(f"Simscape CSV has no rows for run_id={run_id}")

    _validate_matching_time_axes(
        run_id=run_id,
        main_rows=main_rows,
        sim_rows=sim_rows,
    )
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

    alignment = _build_vision_alignment(
        run_id=run_id,
        main_rows=main_rows,
        vision_rows=vision_rows,
        sim_rows=sim_rows,
    )
    merged_rows = _build_merged_rows(
        main_rows=main_rows,
        sim_by_time=sim_by_time,
        measured_by_time=measured_by_time,
        vision_series=alignment.points,
    )

    real_derived_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(
        real_derived_dir / f"measured_position_{run_id}.csv",
        MEASURED_POSITION_FIELDNAMES,
        measured_rows,
    )
    _write_csv(
        processed_dir / f"merged_{run_id}.csv",
        MERGED_FIELDNAMES,
        merged_rows,
    )
    _write_alignment_metadata(
        output_path=processed_dir / f"alignment_{run_id}.json",
        run_id=run_id,
        main_path=main_path,
        vision_path=vision_path,
        sim_path=sim_path,
        alignment=alignment,
        main_rows=len(main_rows),
        merged_rows=len(merged_rows),
    )

    return {
        "main_rows": len(main_rows),
        "vision_valid_rows": alignment.source_valid_rows,
        "measured_rows": len(measured_rows),
        "merged_rows": len(merged_rows),
        "alignment_method": alignment.method,
    }


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
            theta_meas = (
                _float(main_row, "theta1_meas"),
                _float(main_row, "theta2_meas"),
                _float(main_row, "theta3_meas"),
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
            fk_result = delta_fk(*theta_meas, initial_guess_mm=initial_guess)
            measured_position = fk_result.as_tuple()
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


def _build_vision_alignment(
    *,
    run_id: str,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    sim_rows: list[dict[str, str]],
) -> AlignmentResult:
    if not vision_rows:
        return AlignmentResult([], "no_vision_rows", (), 0, 0)

    valid_rows = [
        row
        for row in vision_rows
        if _bool(row.get("valid", "")) and _bool(row.get("marker_detected", ""))
    ]
    if not valid_rows:
        return AlignmentResult([], "no_valid_vision_rows", (), 0, len(vision_rows))

    if "circle" in run_id:
        if "_run01_holdout_" in run_id:
            return _align_partial_circle_vision(
                main_rows=main_rows,
                vision_rows=vision_rows,
                valid_rows=valid_rows,
            )
        return _align_circle_vision(
            main_rows=main_rows,
            vision_rows=vision_rows,
            valid_rows=valid_rows,
        )

    main_segments = _phase_segments(main_rows, time_column="time", time_scale=1.0)
    vision_segments = _phase_segments(
        vision_rows,
        time_column="vision_time",
        time_scale=1000.0,
    )
    if len(main_segments) >= 3 and len(main_segments) == len(vision_segments):
        return _align_internal_phases(
            main_segments=main_segments,
            vision_segments=vision_segments,
            main_rows=main_rows,
            vision_rows=vision_rows,
            sim_rows=sim_rows,
            valid_rows=valid_rows,
            source_total_rows=len(vision_rows),
        )

    return _align_full_duration(
        main_rows=main_rows,
        valid_rows=valid_rows,
        source_total_rows=len(vision_rows),
        method="full_duration_static_or_fallback",
    )


def _align_internal_phases(
    *,
    main_segments: list[PhaseSegment],
    vision_segments: list[PhaseSegment],
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    sim_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
    source_total_rows: int,
) -> AlignmentResult:
    valid_phase_rows = _valid_rows_by_phase_segment(vision_rows)
    if len(valid_phase_rows) != len(vision_segments):
        raise ValueError(
            "valid vision phase segment count does not match all phase segments"
        )

    sim_by_time = {
        _time_key(_float(row, "time")): row
        for row in sim_rows
    }
    anchors: list[tuple[float, float]] = []
    for index in range(1, len(main_segments) - 1):
        stable_end_ms, departure_ms = _phase_departure_edges_ms(
            valid_phase_rows[index - 1]
        )
        if stable_end_ms is not None:
            anchors.append(
                (stable_end_ms, main_segments[index - 1].end_time_ms)
            )
        arrival_ms = (
            _float(valid_phase_rows[index][0], "vision_time") * 1000.0
        )
        main_start_ms = main_segments[index].start_time_ms
        main_settle_ms = _simscape_settle_time_ms(
            segment=main_segments[index],
            main_rows=main_rows,
            sim_by_time=sim_by_time,
        )
        anchors.extend(
            [
                (departure_ms, main_start_ms),
                (arrival_ms, main_settle_ms),
            ]
        )

    final_stable_end_ms, final_departure_ms = _phase_departure_edges_ms(
        valid_phase_rows[-2]
    )
    if final_stable_end_ms is not None:
        anchors.append(
            (final_stable_end_ms, main_segments[-2].end_time_ms)
        )
    anchors.append(
        (
            final_departure_ms,
            main_segments[-1].start_time_ms,
        )
    )
    _validate_increasing_anchors(anchors)
    start_vision_ms = anchors[0][0]
    end_vision_ms = anchors[-1][0]
    points = _map_valid_vision_rows(
        valid_rows=valid_rows,
        anchors=anchors,
        start_vision_ms=start_vision_ms,
        end_vision_ms=end_vision_ms,
    )
    return AlignmentResult(
        points=points,
        method="phase_departure_to_command_arrival_to_sim_settle",
        anchors=tuple(anchors),
        source_valid_rows=len(valid_rows),
        source_total_rows=source_total_rows,
    )


def _valid_rows_by_phase_segment(
    vision_rows: list[dict[str, str]],
) -> list[list[dict[str, str]]]:
    segments: list[list[dict[str, str]]] = []
    start_index = 0
    for index in range(1, len(vision_rows) + 1):
        phase_changed = (
            index == len(vision_rows)
            or vision_rows[index].get("phase", "")
            != vision_rows[start_index].get("phase", "")
        )
        if not phase_changed:
            continue
        valid_segment_rows = [
            row
            for row in vision_rows[start_index:index]
            if _bool(row.get("valid", ""))
            and _bool(row.get("marker_detected", ""))
        ]
        if not valid_segment_rows:
            raise ValueError(
                "vision phase has no valid rows: "
                f"{vision_rows[start_index].get('phase', '')}"
            )
        segments.append(valid_segment_rows)
        start_index = index
    return segments


def _phase_departure_edges_ms(
    phase_rows: list[dict[str, str]],
    *,
    displacement_threshold_mm: float = 5.0,
) -> tuple[float | None, float]:
    baseline_rows = phase_rows[: min(10, len(phase_rows))]
    baseline_x = statistics.median(
        _float(row, "vision_x") for row in baseline_rows
    )
    baseline_y = statistics.median(
        _float(row, "vision_y") for row in baseline_rows
    )
    displaced = [
        math.hypot(
            _float(row, "vision_x") - baseline_x,
            _float(row, "vision_y") - baseline_y,
        )
        >= displacement_threshold_mm
        for row in phase_rows
    ]
    for index in range(len(phase_rows) - 1):
        if displaced[index] and displaced[index + 1]:
            stable_end_ms = (
                _float(phase_rows[index - 1], "vision_time") * 1000.0
                if index > 0
                else None
            )
            departure_ms = (
                _float(phase_rows[index], "vision_time") * 1000.0
            )
            return stable_end_ms, departure_ms
    if displaced[-1]:
        stable_end_ms = (
            _float(phase_rows[-2], "vision_time") * 1000.0
            if len(phase_rows) > 1
            else None
        )
        departure_ms = _float(phase_rows[-1], "vision_time") * 1000.0
        return stable_end_ms, departure_ms
    # Some manually labeled logs omit the transition between phase labels.
    # In that case the last valid sample is the only observable departure edge.
    return None, _float(phase_rows[-1], "vision_time") * 1000.0


def _simscape_settle_time_ms(
    *,
    segment: PhaseSegment,
    main_rows: list[dict[str, str]],
    sim_by_time: dict[str, dict[str, str]],
    distance_threshold_mm: float = 3.0,
) -> float:
    segment_rows = [
        row
        for row in main_rows
        if segment.start_time_ms
        <= _float(row, "time")
        <= segment.end_time_ms
    ]
    if not segment_rows:
        raise ValueError(f"main phase has no rows: {segment.phase}")
    target_x = _float(segment_rows[0], "target_x")
    target_y = _float(segment_rows[0], "target_y")
    for row in segment_rows:
        time_ms = _float(row, "time")
        sim_row = sim_by_time[_time_key(time_ms)]
        distance = math.hypot(
            _float(sim_row, "sim_x") - target_x,
            _float(sim_row, "sim_y") - target_y,
        )
        if distance <= distance_threshold_mm:
            return time_ms
    raise ValueError(
        "Simscape phase did not settle within "
        f"{distance_threshold_mm:g} mm for phase {segment.phase}"
    )


def _validate_increasing_anchors(
    anchors: list[tuple[float, float]],
) -> None:
    for before, after in zip(anchors, anchors[1:], strict=False):
        if after[0] <= before[0]:
            raise ValueError(
                "vision alignment anchors are not strictly increasing"
            )
        if after[1] <= before[1]:
            raise ValueError(
                "main alignment anchors are not strictly increasing"
            )


def _align_circle_vision(
    *,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
) -> AlignmentResult:
    baseline_rows = valid_rows[: min(10, len(valid_rows))]
    home_x = sum(_float(row, "vision_x") for row in baseline_rows) / len(
        baseline_rows
    )
    home_y = sum(_float(row, "vision_y") for row in baseline_rows) / len(
        baseline_rows
    )
    motion_rows = [
        row
        for row in valid_rows
        if math.hypot(
            _float(row, "vision_x") - home_x,
            _float(row, "vision_y") - home_y,
        )
        >= 10.0
    ]
    if len(motion_rows) < 2:
        raise ValueError("circle vision alignment could not detect the motion interval")

    vision_start_ms = _float(motion_rows[0], "vision_time") * 1000.0
    vision_end_ms = _float(motion_rows[-1], "vision_time") * 1000.0
    main_start_ms = _float(main_rows[0], "time")
    main_end_ms = _float(main_rows[-1], "time")
    anchors = [
        (vision_start_ms, main_start_ms),
        (vision_end_ms, main_end_ms),
    ]
    points = _map_valid_vision_rows(
        valid_rows=valid_rows,
        anchors=anchors,
        start_vision_ms=vision_start_ms,
        end_vision_ms=vision_end_ms,
    )
    return AlignmentResult(
        points=points,
        method="circle_motion_radius_10mm",
        anchors=tuple(anchors),
        source_valid_rows=len(valid_rows),
        source_total_rows=len(vision_rows),
    )


def _align_partial_circle_vision(
    *,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
) -> AlignmentResult:
    baseline_rows = valid_rows[: min(10, len(valid_rows))]
    home_x = sum(_float(row, "vision_x") for row in baseline_rows) / len(
        baseline_rows
    )
    home_y = sum(_float(row, "vision_y") for row in baseline_rows) / len(
        baseline_rows
    )
    motion_rows = [
        row
        for row in valid_rows
        if math.hypot(
            _float(row, "vision_x") - home_x,
            _float(row, "vision_y") - home_y,
        )
        >= 10.0
    ]
    if len(motion_rows) < 2:
        raise ValueError("partial circle alignment could not detect motion")

    unwrapped_angles: list[float] = []
    for row in motion_rows:
        angle = math.atan2(
            _float(row, "vision_y") - home_y,
            _float(row, "vision_x") - home_x,
        )
        if unwrapped_angles:
            while angle - unwrapped_angles[-1] > math.pi:
                angle -= 2.0 * math.pi
            while angle - unwrapped_angles[-1] < -math.pi:
                angle += 2.0 * math.pi
        unwrapped_angles.append(angle)

    observed_angle = unwrapped_angles[-1] - unwrapped_angles[0]
    observed_fraction = min(max(observed_angle / (2.0 * math.pi), 0.0), 1.0)
    if observed_fraction <= 0.0:
        raise ValueError("partial circle has no positive angular coverage")

    main_motion_rows = [
        row for row in main_rows if row.get("phase", "") != "home_2"
    ]
    main_start_ms = _float(main_motion_rows[0], "time")
    main_full_end_ms = _float(main_motion_rows[-1], "time")
    main_observed_end_ms = main_start_ms + observed_fraction * (
        main_full_end_ms - main_start_ms
    )
    vision_start_ms = _float(motion_rows[0], "vision_time") * 1000.0
    vision_end_ms = _float(motion_rows[-1], "vision_time") * 1000.0
    anchors = [
        (vision_start_ms, main_start_ms),
        (vision_end_ms, main_observed_end_ms),
    ]
    points = _map_valid_vision_rows(
        valid_rows=motion_rows,
        anchors=anchors,
        start_vision_ms=vision_start_ms,
        end_vision_ms=vision_end_ms,
    )
    return AlignmentResult(
        points=points,
        method="partial_circle_observed_angular_coverage",
        anchors=tuple(anchors),
        source_valid_rows=len(valid_rows),
        source_total_rows=len(vision_rows),
    )


def _align_full_duration(
    *,
    main_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
    source_total_rows: int,
    method: str,
) -> AlignmentResult:
    vision_start_ms = _float(valid_rows[0], "vision_time") * 1000.0
    vision_end_ms = _float(valid_rows[-1], "vision_time") * 1000.0
    anchors = [
        (vision_start_ms, _float(main_rows[0], "time")),
        (vision_end_ms, _float(main_rows[-1], "time")),
    ]
    points = _map_valid_vision_rows(
        valid_rows=valid_rows,
        anchors=anchors,
        start_vision_ms=vision_start_ms,
        end_vision_ms=vision_end_ms,
    )
    return AlignmentResult(
        points=points,
        method=method,
        anchors=tuple(anchors),
        source_valid_rows=len(valid_rows),
        source_total_rows=source_total_rows,
    )


def _phase_segments(
    rows: list[dict[str, str]],
    *,
    time_column: str,
    time_scale: float,
) -> list[PhaseSegment]:
    segments: list[PhaseSegment] = []
    start_index = 0
    for index in range(1, len(rows) + 1):
        phase_changed = (
            index == len(rows)
            or rows[index].get("phase", "") != rows[start_index].get("phase", "")
        )
        if not phase_changed:
            continue
        segments.append(
            PhaseSegment(
                phase=rows[start_index].get("phase", ""),
                start_time_ms=_float(rows[start_index], time_column) * time_scale,
                end_time_ms=_float(rows[index - 1], time_column) * time_scale,
            )
        )
        start_index = index
    return segments


def _map_valid_vision_rows(
    *,
    valid_rows: list[dict[str, str]],
    anchors: list[tuple[float, float]],
    start_vision_ms: float,
    end_vision_ms: float,
) -> list[TimeSeriesPoint]:
    points: list[TimeSeriesPoint] = []
    for row in valid_rows:
        vision_time_ms = _float(row, "vision_time") * 1000.0
        if vision_time_ms < start_vision_ms or vision_time_ms > end_vision_ms:
            continue
        points.append(
            TimeSeriesPoint(
                time_ms=_piecewise_map_time(vision_time_ms, anchors),
                values=(_float(row, "vision_x"), _float(row, "vision_y")),
            )
        )
    return points


def _piecewise_map_time(
    source_time_ms: float,
    anchors: list[tuple[float, float]],
) -> float:
    for index in range(1, len(anchors)):
        source_before, target_before = anchors[index - 1]
        source_after, target_after = anchors[index]
        if source_time_ms <= source_after:
            if abs(source_after - source_before) <= 1e-9:
                return target_before
            ratio = (source_time_ms - source_before) / (
                source_after - source_before
            )
            return target_before + ratio * (target_after - target_before)
    return anchors[-1][1]


def _resolve_simscape_path(
    *,
    run_id: str,
    simulation_raw_dir: Path,
) -> Path:
    contract_path = simulation_raw_dir / f"simscape_{run_id}.csv"
    if contract_path.exists():
        return contract_path

    marker = "_run01_main_"
    if marker in run_id:
        export_run_id = run_id.replace(marker, "_run01_simscape_", 1)
        export_path = simulation_raw_dir / f"simscape_{export_run_id}.csv"
        if export_path.exists():
            return export_path
    raise FileNotFoundError(f"Simscape CSV not found for run_id={run_id}")


def _validate_matching_time_axes(
    *,
    run_id: str,
    main_rows: list[dict[str, str]],
    sim_rows: list[dict[str, str]],
) -> None:
    main_times = [_time_key(_float(row, "time")) for row in main_rows]
    sim_times = [_time_key(_float(row, "time")) for row in sim_rows]
    if main_times != sim_times:
        raise ValueError(
            f"Simscape/main time axes do not match exactly for run_id={run_id}"
        )


def _write_alignment_metadata(
    *,
    output_path: Path,
    run_id: str,
    main_path: Path,
    vision_path: Path,
    sim_path: Path,
    alignment: AlignmentResult,
    main_rows: int,
    merged_rows: int,
) -> None:
    metadata = {
        "run_id": run_id,
        "method": alignment.method,
        "main_csv": str(main_path),
        "vision_csv": str(vision_path),
        "simscape_csv": str(sim_path),
        "source_total_vision_rows": alignment.source_total_rows,
        "source_valid_vision_rows": alignment.source_valid_rows,
        "aligned_vision_rows": len(alignment.points),
        "main_rows": main_rows,
        "merged_rows": merged_rows,
        "anchors": [
            {
                "vision_time_ms": vision_time_ms,
                "main_time_ms": main_time_ms,
            }
            for vision_time_ms, main_time_ms in alignment.anchors
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, ensure_ascii=True, indent=2)


def _build_merged_rows(
    *,
    main_rows: list[dict[str, str]],
    sim_by_time: dict[str, dict[str, str]],
    measured_by_time: dict[str, dict[str, object]],
    vision_series: list[TimeSeriesPoint],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for main_row in main_rows:
        if not _bool(main_row.get("valid", "")):
            continue

        main_time = _float(main_row, "time")
        time_key = _time_key(main_time)
        sim_row = sim_by_time.get(time_key)
        measured_row = measured_by_time.get(time_key)
        vision_xy = _interpolate_series(vision_series, main_time)
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


def _interpolate_series(
    points: list[TimeSeriesPoint],
    target_time_ms: float,
) -> tuple[float, ...] | None:
    if not points:
        return None
    if target_time_ms < points[0].time_ms or target_time_ms > points[-1].time_ms:
        return None

    lower_index = 0
    upper_index = len(points) - 1
    while lower_index <= upper_index:
        middle_index = (lower_index + upper_index) // 2
        middle_time = points[middle_index].time_ms
        if middle_time == target_time_ms:
            return points[middle_index].values
        if middle_time < target_time_ms:
            lower_index = middle_index + 1
        else:
            upper_index = middle_index - 1

    before = points[upper_index]
    after = points[lower_index]
    if after.time_ms == before.time_ms:
        return before.values
    ratio = (target_time_ms - before.time_ms) / (after.time_ms - before.time_ms)
    return tuple(
        before_value + ratio * (after_value - before_value)
        for before_value, after_value in zip(before.values, after.values, strict=True)
    )


def _invalid_measured_position_row(run_id: str, time_ms: float) -> dict[str, object]:
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
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"CSV header is missing: {path}")
        return [dict(row) for row in reader]


def _write_csv(
    path: Path,
    fieldnames: Iterable[str],
    rows: list[dict[str, object]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=tuple(fieldnames),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _float(row: dict[str, str] | None, column_name: str) -> float:
    if row is None:
        raise ValueError(f"row is missing for column '{column_name}'")
    return float(row[column_name])


def _bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def _time_key(time_ms: float) -> str:
    return f"{time_ms:.9f}".rstrip("0").rstrip(".")


def _format_number(value: float) -> str:
    return f"{value:.12g}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Run 01-pre measured-position and merged validation CSVs."
    )
    parser.add_argument(
        "--run-id",
        action="append",
        help="Run ID to process. May be passed more than once. Defaults to all Run 01-pre IDs.",
    )
    parser.add_argument("--real-raw-dir", type=Path, default=Path("data/real/raw"))
    parser.add_argument("--vision-raw-dir", type=Path, default=Path("data/vision/raw"))
    parser.add_argument("--simulation-raw-dir", type=Path, default=Path("data/simulation/raw"))
    parser.add_argument("--real-derived-dir", type=Path, default=Path("data/real/derived"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
