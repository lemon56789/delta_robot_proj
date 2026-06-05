from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
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
            f"vision_valid_rows={result['vision_valid_rows']}"
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
) -> dict[str, int]:
    main_rows = _read_csv(real_raw_dir / f"main_{run_id}.csv")
    vision_rows = _read_csv(vision_raw_dir / f"vision_{run_id}.csv")
    sim_rows = _read_csv(simulation_raw_dir / f"simscape_{run_id}.csv")

    if not main_rows:
        raise ValueError(f"main CSV has no rows for run_id={run_id}")
    if not sim_rows:
        raise ValueError(f"Simscape CSV has no rows for run_id={run_id}")

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

    vision_series = _build_vision_series(main_rows=main_rows, vision_rows=vision_rows)
    merged_rows = _build_merged_rows(
        main_rows=main_rows,
        sim_by_time=sim_by_time,
        measured_by_time=measured_by_time,
        vision_series=vision_series,
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

    return {
        "main_rows": len(main_rows),
        "vision_valid_rows": len(vision_series),
        "measured_rows": len(measured_rows),
        "merged_rows": len(merged_rows),
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


def _build_vision_series(
    *,
    main_rows: list[dict[str, str]],
    vision_rows: list[dict[str, str]],
) -> list[TimeSeriesPoint]:
    if not vision_rows:
        return []

    first_main_time_ms = _float(main_rows[0], "time")
    first_vision_time_s = _float(vision_rows[0], "vision_time")
    points: list[TimeSeriesPoint] = []
    for row in vision_rows:
        if not (_bool(row.get("valid", "")) and _bool(row.get("marker_detected", ""))):
            continue
        aligned_time_ms = first_main_time_ms + (
            (_float(row, "vision_time") - first_vision_time_s) * 1000.0
        )
        points.append(
            TimeSeriesPoint(
                time_ms=aligned_time_ms,
                values=(_float(row, "vision_x"), _float(row, "vision_y")),
            )
        )
    return points


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
