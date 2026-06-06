from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import date
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, TextIO

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinematics.inverse_kinematics import delta_ik
from virtual_sensor.correction_engine import (
    CorrectionConfig,
    CorrectionEngine,
    CorrectionResult,
)
from virtual_sensor.ridge_model import RidgeModel


HOME_Z_MM = -263.27731514697575
THETA_MIN_DEG = -45.0
THETA_MAX_DEG = 90.0
DEFAULT_HOLD_S = 5.0
DEFAULT_CIRCLE_ENDPOINT_HOLD_S = 2.0
DEFAULT_CIRCLE_POINTS = 72
DEFAULT_CIRCLE_DURATION_S = 30.0
DEFAULT_SAMPLE_PERIOD_S = 0.1
DEFAULT_COMMAND_UPDATE_PERIOD_S = 0.5
DEFAULT_GAIN = 0.25
DEFAULT_CLAMP_MM = 2.0
TIME_SOURCE = "pc_scheduled_elapsed_ms"
THETA_MEAS_SOURCE = "command_echo_no_encoder"

TRAJECTORIES = (
    "cross_pm30",
    "reverse_grid_3x3_pm40",
    "diamond_pm35",
    "circle_r40",
)
CORRECTION_STATES = ("off", "on")

MAIN_FIELDNAMES = [
    "run_id",
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
    "valid",
    "phase",
    "command",
    "time_source",
    "theta_meas_source",
]

CORRECTION_FIELDNAMES = [
    "run_id",
    "time",
    "actual_elapsed_ms",
    "schedule_lag_ms",
    "target_x",
    "target_y",
    "target_z",
    "sim_x",
    "sim_y",
    "sim_z",
    "nominal_theta1",
    "nominal_theta2",
    "nominal_theta3",
    "predicted_error_x",
    "predicted_error_y",
    "predicted_error_z",
    "requested_correction_x",
    "requested_correction_y",
    "requested_correction_z",
    "applied_correction_x",
    "applied_correction_y",
    "applied_correction_z",
    "corrected_target_x",
    "corrected_target_y",
    "corrected_target_z",
    "corrected_theta1",
    "corrected_theta2",
    "corrected_theta3",
    "correction_gain",
    "max_xy_correction_mm",
    "correction_clamped",
    "fallback_used",
    "command_sent",
    "correction_status",
]


@dataclass(frozen=True)
class TrajectoryPoint:
    phase: str
    target_x: float
    target_y: float
    target_z: float
    nominal_theta: tuple[float, float, float]
    hold_s: float


@dataclass(frozen=True)
class ScheduledPoint:
    time_ms: int
    phase: str
    target_xyz_mm: tuple[float, float, float]
    nominal_theta_deg: tuple[float, float, float]


@dataclass(frozen=True)
class SimscapePoint:
    time_ms: int
    sim_xyz_mm: tuple[float, float, float]


def main() -> int:
    args = parse_args()
    if args.command == "manifest":
        entries = build_run_manifest(run_date=args.date)
        write_json(args.output, {"run_count": len(entries), "runs": entries})
        print(f"run_count={len(entries)}")
        print(f"manifest={args.output}")
        return 0

    return run_command(args)


def run_command(args: argparse.Namespace) -> int:
    validate_run_id(
        run_id=args.run_id,
        trajectory=args.trajectory,
        correction_state=args.correction,
    )
    points = build_trajectory_points(
        trajectory=args.trajectory,
        target_z_mm=args.target_z_mm,
        hold_s=args.hold_s,
        circle_endpoint_hold_s=args.circle_endpoint_hold_s,
        circle_points=args.circle_points,
        circle_duration_s=args.circle_duration_s,
        theta_min_deg=args.theta_min_deg,
        theta_max_deg=args.theta_max_deg,
    )
    schedule = build_schedule(points, sample_period_s=args.sample_period_s)

    output_csv = Path(args.output_csv or f"data/real/raw/main_{args.run_id}.csv")
    metadata_json = Path(args.metadata_json or output_csv.with_suffix(".json"))
    serial_log = Path(
        args.serial_log or output_csv.with_name(f"serial_{args.run_id}.txt")
    )
    correction_csv = Path(
        args.correction_csv
        or output_csv.with_name(f"correction_{args.run_id}.csv")
    )

    simscape_points: list[SimscapePoint] | None = None
    engine: CorrectionEngine | None = None
    model_path: Path | None = None
    if args.correction == "on":
        if args.simscape_csv is None:
            raise SystemExit("--simscape-csv is required for correction ON")
        model_path = Path(args.model)
        simscape_points = load_simscape_schedule(
            Path(args.simscape_csv),
            expected_times_ms=[row.time_ms for row in schedule],
        )
        model = RidgeModel.load(model_path)
        engine = CorrectionEngine(
            model,
            CorrectionConfig(
                gain=args.gain,
                max_xy_correction_mm=args.max_xy_correction_mm,
                theta_min_deg=args.theta_min_deg,
                theta_max_deg=args.theta_max_deg,
            ),
        )

    summary = execute_schedule(
        schedule=schedule,
        run_id=args.run_id,
        correction_state=args.correction,
        output_csv=output_csv,
        correction_csv=correction_csv,
        serial_log=serial_log,
        simscape_points=simscape_points,
        engine=engine,
        port=args.port,
        baudrate=args.baudrate,
        ready_wait_s=args.ready_wait_s,
        gain=args.gain,
        max_xy_correction_mm=args.max_xy_correction_mm,
        command_update_period_s=args.command_update_period_s,
        dry_run=args.dry_run,
    )
    write_metadata(
        output_path=metadata_json,
        args=args,
        output_csv=output_csv,
        correction_csv=correction_csv,
        serial_log=serial_log,
        model_path=model_path,
        points=points,
        schedule=schedule,
        summary=summary,
    )

    print(f"main_csv={output_csv}")
    print(f"correction_csv={correction_csv}")
    print(f"metadata_json={metadata_json}")
    print(f"serial_log={serial_log}")
    print(f"row_count={summary['row_count']}")
    print(f"fallback_count={summary['fallback_count']}")
    print(f"clamp_count={summary['clamp_count']}")
    print(f"max_schedule_lag_ms={summary['max_schedule_lag_ms']}")
    return 0


def build_run_manifest(*, run_date: str) -> list[dict[str, Any]]:
    date.fromisoformat(run_date)
    entries: list[dict[str, Any]] = []
    sequence = 1
    for repetition in range(1, 4):
        for trajectory in TRAJECTORIES:
            for correction_state in CORRECTION_STATES:
                run_id = (
                    f"{run_date}_run02_{trajectory}_{correction_state}"
                    f"_r{repetition:02d}"
                )
                entries.append(
                    {
                        "sequence": sequence,
                        "run_id": run_id,
                        "trajectory": trajectory,
                        "correction": correction_state,
                        "repetition": repetition,
                        "main_csv": f"data/real/raw/main_{run_id}.csv",
                        "vision_csv": f"data/vision/raw/vision_{run_id}.csv",
                        "simscape_csv": (
                            "data/simulation/raw/"
                            f"simscape_run02_nominal_{trajectory}.csv"
                        ),
                        "correction_csv": (
                            f"data/real/raw/correction_{run_id}.csv"
                        ),
                    }
                )
                sequence += 1
    return entries


def validate_run_id(
    *,
    run_id: str,
    trajectory: str,
    correction_state: str,
) -> None:
    expected_fragment = f"_run02_{trajectory}_{correction_state}_r"
    if expected_fragment not in run_id:
        raise ValueError(
            "run_id must contain the finalized trajectory/state naming: "
            f"{expected_fragment}"
        )
    repetition_text = run_id.rsplit("_r", 1)[-1]
    if repetition_text not in {"01", "02", "03"}:
        raise ValueError("Run 02 repetition must be r01, r02, or r03")


def build_trajectory_points(
    *,
    trajectory: str,
    target_z_mm: float,
    hold_s: float,
    circle_endpoint_hold_s: float,
    circle_points: int,
    circle_duration_s: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> list[TrajectoryPoint]:
    if hold_s <= 0.0:
        raise ValueError("hold_s must be positive")
    if circle_endpoint_hold_s <= 0.0:
        raise ValueError("circle_endpoint_hold_s must be positive")
    if circle_points < 8:
        raise ValueError("circle_points must be at least 8")
    if circle_duration_s <= 0.0:
        raise ValueError("circle_duration_s must be positive")

    if trajectory == "cross_pm30":
        specs = [
            ("home_1", 0.0, 0.0, hold_s),
            ("x_plus", 30.0, 0.0, hold_s),
            ("home_2", 0.0, 0.0, hold_s),
            ("x_minus", -30.0, 0.0, hold_s),
            ("home_3", 0.0, 0.0, hold_s),
            ("y_plus", 0.0, 30.0, hold_s),
            ("home_4", 0.0, 0.0, hold_s),
            ("y_minus", 0.0, -30.0, hold_s),
            ("home_5", 0.0, 0.0, hold_s),
        ]
    elif trajectory == "reverse_grid_3x3_pm40":
        specs = [
            ("home_1", 0.0, 0.0, hold_s),
            ("x_plus_y_plus", 40.0, 40.0, hold_s),
            ("x_center_y_plus", 0.0, 40.0, hold_s),
            ("x_minus_y_plus", -40.0, 40.0, hold_s),
            ("x_plus_y_center", 40.0, 0.0, hold_s),
            ("center", 0.0, 0.0, hold_s),
            ("x_minus_y_center", -40.0, 0.0, hold_s),
            ("x_plus_y_minus", 40.0, -40.0, hold_s),
            ("x_center_y_minus", 0.0, -40.0, hold_s),
            ("x_minus_y_minus", -40.0, -40.0, hold_s),
            ("home_2", 0.0, 0.0, hold_s),
        ]
    elif trajectory == "diamond_pm35":
        specs = [
            ("home_1", 0.0, 0.0, hold_s),
            ("x_plus", 35.0, 0.0, hold_s),
            ("y_plus", 0.0, 35.0, hold_s),
            ("x_minus", -35.0, 0.0, hold_s),
            ("y_minus", 0.0, -35.0, hold_s),
            ("x_plus_end", 35.0, 0.0, hold_s),
            ("home_2", 0.0, 0.0, hold_s),
        ]
    elif trajectory == "circle_r40":
        specs = [
            ("home_1", 0.0, 0.0, hold_s),
            (
                "circle_start_hold",
                40.0,
                0.0,
                circle_endpoint_hold_s,
            ),
        ]
        step_hold_s = circle_duration_s / circle_points
        for index in range(1, circle_points + 1):
            angle_rad = 2.0 * math.pi * index / circle_points
            specs.append(
                (
                    f"circle_ccw_{index:03d}",
                    _clean_zero(40.0 * math.cos(angle_rad)),
                    _clean_zero(40.0 * math.sin(angle_rad)),
                    step_hold_s,
                )
            )
        specs.extend(
            [
                (
                    "circle_end_hold",
                    40.0,
                    0.0,
                    circle_endpoint_hold_s,
                ),
                ("home_2", 0.0, 0.0, hold_s),
            ]
        )
    else:
        raise ValueError(f"unsupported Run 02 trajectory: {trajectory}")

    return [
        make_trajectory_point(
            phase=phase,
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=target_z_mm,
            hold_s=point_hold_s,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
        )
        for phase, x_mm, y_mm, point_hold_s in specs
    ]


def make_trajectory_point(
    *,
    phase: str,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    hold_s: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> TrajectoryPoint:
    theta_solution = delta_ik(
        x_mm,
        y_mm,
        z_mm,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
    ).as_tuple()
    theta = tuple(float(round(value)) for value in theta_solution)
    return TrajectoryPoint(
        phase=phase,
        target_x=x_mm,
        target_y=y_mm,
        target_z=z_mm,
        nominal_theta=(theta[0], theta[1], theta[2]),
        hold_s=hold_s,
    )


def build_schedule(
    points: list[TrajectoryPoint],
    *,
    sample_period_s: float,
) -> list[ScheduledPoint]:
    if sample_period_s <= 0.0:
        raise ValueError("sample_period_s must be positive")
    sample_period_ms = sample_period_s * 1000.0
    schedule: list[ScheduledPoint] = []
    phase_start_ms = 0.0
    for point in points:
        phase_end_ms = phase_start_ms + point.hold_s * 1000.0
        sample_index = 0
        while True:
            time_ms_float = phase_start_ms + sample_index * sample_period_ms
            if time_ms_float >= phase_end_ms - 1e-9:
                break
            time_ms = round(time_ms_float)
            if schedule and time_ms <= schedule[-1].time_ms:
                time_ms = schedule[-1].time_ms + 1
            schedule.append(
                ScheduledPoint(
                    time_ms=time_ms,
                    phase=point.phase,
                    target_xyz_mm=(
                        point.target_x,
                        point.target_y,
                        point.target_z,
                    ),
                    nominal_theta_deg=point.nominal_theta,
                )
            )
            sample_index += 1
        phase_start_ms = phase_end_ms
    if not schedule:
        raise ValueError("trajectory schedule is empty")
    return schedule


def load_simscape_schedule(
    path: Path,
    *,
    expected_times_ms: list[int],
) -> list[SimscapePoint]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"time", "sim_x", "sim_y", "sim_z"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"Simscape CSV is missing required columns: {path}")
        points = [
            SimscapePoint(
                time_ms=_parse_exact_int(row["time"], path=path),
                sim_xyz_mm=(
                    _parse_finite(row["sim_x"], path=path),
                    _parse_finite(row["sim_y"], path=path),
                    _parse_finite(row["sim_z"], path=path),
                ),
            )
            for row in reader
        ]
    actual_times = [point.time_ms for point in points]
    if actual_times != expected_times_ms:
        raise ValueError(
            "Simscape time axis must exactly match the deterministic Run 02 "
            f"schedule: expected {len(expected_times_ms)} rows, "
            f"found {len(actual_times)}"
        )
    return points


def execute_schedule(
    *,
    schedule: list[ScheduledPoint],
    run_id: str,
    correction_state: str,
    output_csv: Path,
    correction_csv: Path,
    serial_log: Path,
    simscape_points: list[SimscapePoint] | None,
    engine: CorrectionEngine | None,
    port: str | None,
    baudrate: int,
    ready_wait_s: float,
    gain: float,
    max_xy_correction_mm: float,
    command_update_period_s: float,
    dry_run: bool,
) -> dict[str, int]:
    for path in (output_csv, correction_csv, serial_log):
        path.parent.mkdir(parents=True, exist_ok=True)
    if correction_state == "on" and (engine is None or simscape_points is None):
        raise ValueError("correction ON requires an engine and Simscape points")
    if correction_state == "off" and (
        engine is not None or simscape_points is not None
    ):
        raise ValueError("correction OFF must not use an engine or Simscape")
    if command_update_period_s <= 0.0:
        raise ValueError("command_update_period_s must be positive")
    command_update_period_ms = round(command_update_period_s * 1000.0)

    serial_conn = None
    if not dry_run:
        if port is None:
            raise SystemExit("--port is required unless --dry-run is used")
        serial_conn = open_serial(port=port, baudrate=baudrate)
        time.sleep(ready_wait_s)

    fallback_count = 0
    clamp_count = 0
    max_schedule_lag_ms = 0
    consecutive_fallbacks = 0
    previous_result: CorrectionResult | None = None
    previous_sim_xyz: tuple[float, float, float] | None = None
    previous_phase: str | None = None
    last_command_time_ms: int | None = None
    logger_start = time.monotonic()
    with (
        output_csv.open("w", encoding="utf-8", newline="") as main_file,
        correction_csv.open(
            "w", encoding="utf-8", newline=""
        ) as correction_file,
        serial_log.open("w", encoding="utf-8", newline="\n") as serial_file,
    ):
        main_writer = csv.DictWriter(
            main_file,
            fieldnames=MAIN_FIELDNAMES,
            lineterminator="\n",
        )
        correction_writer = csv.DictWriter(
            correction_file,
            fieldnames=CORRECTION_FIELDNAMES,
            lineterminator="\n",
        )
        main_writer.writeheader()
        correction_writer.writeheader()

        for index, scheduled in enumerate(schedule):
            if not dry_run:
                wait_until(
                    logger_start=logger_start,
                    scheduled_time_ms=scheduled.time_ms,
                    serial_conn=serial_conn,
                    serial_file=serial_file,
                )
            actual_elapsed_ms = round(
                (time.monotonic() - logger_start) * 1000.0
            )
            schedule_lag_ms = (
                0 if dry_run else actual_elapsed_ms - scheduled.time_ms
            )
            max_schedule_lag_ms = max(max_schedule_lag_ms, schedule_lag_ms)
            if schedule_lag_ms > 500:
                close_serial(serial_conn)
                raise RuntimeError(
                    f"schedule lag exceeded 500 ms at {scheduled.time_ms} ms"
                )

            sim_xyz = (
                None
                if simscape_points is None
                else simscape_points[index].sim_xyz_mm
            )
            command_sent = (
                previous_result is None
                or scheduled.phase != previous_phase
                or last_command_time_ms is None
                or (
                    scheduled.time_ms - last_command_time_ms
                    >= command_update_period_ms
                )
            )
            if command_sent:
                result = correction_result(
                    scheduled=scheduled,
                    correction_state=correction_state,
                    sim_xyz_mm=sim_xyz,
                    engine=engine,
                )
                previous_result = result
                previous_sim_xyz = sim_xyz
                previous_phase = scheduled.phase
                last_command_time_ms = scheduled.time_ms
                fallback_count += int(result.fallback_used)
                clamp_count += int(result.correction_clamped)
                consecutive_fallbacks = (
                    consecutive_fallbacks + 1
                    if result.fallback_used
                    else 0
                )
                if consecutive_fallbacks >= 3 or fallback_count >= 5:
                    close_serial(serial_conn)
                    raise RuntimeError(
                        "correction fallback stop condition reached"
                    )
            else:
                if previous_result is None:
                    raise RuntimeError("previous correction result is missing")
                result = previous_result
            effective_sim_xyz = sim_xyz if command_sent else previous_sim_xyz

            command = format_all_command(result.corrected_theta_deg)
            if command_sent:
                send_command(serial_conn, command, dry_run=dry_run)
                write_serial_event(
                    serial_file,
                    logger_start=logger_start,
                    direction="TX",
                    line=command,
                    scheduled_time_ms=scheduled.time_ms,
                )
            read_serial_available(
                serial_conn,
                serial_file,
                logger_start=logger_start,
            )

            main_writer.writerow(
                main_row(
                    run_id=run_id,
                    scheduled=scheduled,
                    command=command,
                    commanded_theta=result.corrected_theta_deg,
                )
            )
            correction_writer.writerow(
                correction_row(
                    run_id=run_id,
                    scheduled=scheduled,
                    actual_elapsed_ms=actual_elapsed_ms,
                    schedule_lag_ms=schedule_lag_ms,
                    sim_xyz_mm=effective_sim_xyz,
                    result=result,
                    gain=gain,
                    max_xy_correction_mm=max_xy_correction_mm,
                    command_sent=command_sent,
                )
            )
            main_file.flush()
            correction_file.flush()

    close_serial(serial_conn)
    return {
        "row_count": len(schedule),
        "fallback_count": fallback_count,
        "clamp_count": clamp_count,
        "max_schedule_lag_ms": max_schedule_lag_ms,
    }


def correction_result(
    *,
    scheduled: ScheduledPoint,
    correction_state: str,
    sim_xyz_mm: tuple[float, float, float] | None,
    engine: CorrectionEngine | None,
) -> CorrectionResult:
    if correction_state == "off":
        return CorrectionResult(
            predicted_error_xyz_mm=(0.0, 0.0, 0.0),
            requested_correction_xyz_mm=(0.0, 0.0, 0.0),
            applied_correction_xyz_mm=(0.0, 0.0, 0.0),
            corrected_target_xyz_mm=scheduled.target_xyz_mm,
            corrected_theta_deg=scheduled.nominal_theta_deg,
            correction_clamped=False,
            fallback_used=False,
            status="disabled",
        )
    if engine is None:
        raise ValueError("correction ON requires an engine")
    if sim_xyz_mm is None:
        raise ValueError("correction ON requires a Simscape point")
    theta = scheduled.nominal_theta_deg
    features_by_name = {
        "theta1_cmd": theta[0],
        "theta2_cmd": theta[1],
        "theta3_cmd": theta[2],
        "theta1_meas": theta[0],
        "theta2_meas": theta[1],
        "theta3_meas": theta[2],
        "sim_x": sim_xyz_mm[0],
        "sim_y": sim_xyz_mm[1],
        "sim_z": sim_xyz_mm[2],
    }
    try:
        feature_values = tuple(
            features_by_name[name] for name in engine.feature_names
        )
    except KeyError as exc:
        raise ValueError(f"unsupported model feature for Run 02: {exc}") from exc
    return engine.apply(
        target_xyz_mm=scheduled.target_xyz_mm,
        nominal_theta_deg=scheduled.nominal_theta_deg,
        feature_names=engine.feature_names,
        feature_values=feature_values,
    )


def main_row(
    *,
    run_id: str,
    scheduled: ScheduledPoint,
    command: str,
    commanded_theta: tuple[float, float, float],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "time": scheduled.time_ms,
        "target_x": scheduled.target_xyz_mm[0],
        "target_y": scheduled.target_xyz_mm[1],
        "target_z": scheduled.target_xyz_mm[2],
        "theta1_cmd": commanded_theta[0],
        "theta2_cmd": commanded_theta[1],
        "theta3_cmd": commanded_theta[2],
        "theta1_meas": commanded_theta[0],
        "theta2_meas": commanded_theta[1],
        "theta3_meas": commanded_theta[2],
        "valid": True,
        "phase": scheduled.phase,
        "command": command,
        "time_source": TIME_SOURCE,
        "theta_meas_source": THETA_MEAS_SOURCE,
    }


def correction_row(
    *,
    run_id: str,
    scheduled: ScheduledPoint,
    actual_elapsed_ms: int,
    schedule_lag_ms: int,
    sim_xyz_mm: tuple[float, float, float] | None,
    result: CorrectionResult,
    gain: float,
    max_xy_correction_mm: float,
    command_sent: bool,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "time": scheduled.time_ms,
        "actual_elapsed_ms": actual_elapsed_ms,
        "schedule_lag_ms": schedule_lag_ms,
        "target_x": scheduled.target_xyz_mm[0],
        "target_y": scheduled.target_xyz_mm[1],
        "target_z": scheduled.target_xyz_mm[2],
        "sim_x": "" if sim_xyz_mm is None else sim_xyz_mm[0],
        "sim_y": "" if sim_xyz_mm is None else sim_xyz_mm[1],
        "sim_z": "" if sim_xyz_mm is None else sim_xyz_mm[2],
        "nominal_theta1": scheduled.nominal_theta_deg[0],
        "nominal_theta2": scheduled.nominal_theta_deg[1],
        "nominal_theta3": scheduled.nominal_theta_deg[2],
        "predicted_error_x": result.predicted_error_xyz_mm[0],
        "predicted_error_y": result.predicted_error_xyz_mm[1],
        "predicted_error_z": result.predicted_error_xyz_mm[2],
        "requested_correction_x": result.requested_correction_xyz_mm[0],
        "requested_correction_y": result.requested_correction_xyz_mm[1],
        "requested_correction_z": result.requested_correction_xyz_mm[2],
        "applied_correction_x": result.applied_correction_xyz_mm[0],
        "applied_correction_y": result.applied_correction_xyz_mm[1],
        "applied_correction_z": result.applied_correction_xyz_mm[2],
        "corrected_target_x": result.corrected_target_xyz_mm[0],
        "corrected_target_y": result.corrected_target_xyz_mm[1],
        "corrected_target_z": result.corrected_target_xyz_mm[2],
        "corrected_theta1": result.corrected_theta_deg[0],
        "corrected_theta2": result.corrected_theta_deg[1],
        "corrected_theta3": result.corrected_theta_deg[2],
        "correction_gain": gain,
        "max_xy_correction_mm": max_xy_correction_mm,
        "correction_clamped": result.correction_clamped,
        "fallback_used": result.fallback_used,
        "command_sent": command_sent,
        "correction_status": result.status,
    }


def wait_until(
    *,
    logger_start: float,
    scheduled_time_ms: int,
    serial_conn: object | None,
    serial_file: TextIO,
) -> None:
    deadline = logger_start + scheduled_time_ms / 1000.0
    while True:
        read_serial_available(
            serial_conn,
            serial_file,
            logger_start=logger_start,
        )
        remaining = deadline - time.monotonic()
        if remaining <= 0.0:
            return
        time.sleep(min(0.005, remaining))


def open_serial(*, port: str, baudrate: int) -> object:
    try:
        import serial
    except ImportError as exc:
        raise SystemExit(
            "pyserial is required for real Run 02 logging. "
            "Install it with: python -m pip install pyserial"
        ) from exc
    return serial.Serial(port=port, baudrate=baudrate, timeout=0.01)


def close_serial(serial_conn: object | None) -> None:
    if serial_conn is not None:
        serial_conn.close()


def send_command(
    serial_conn: object | None,
    command: str,
    *,
    dry_run: bool,
) -> None:
    if dry_run:
        return
    if serial_conn is None:
        raise RuntimeError("serial connection is not open")
    serial_conn.write((command + "\n").encode("ascii"))
    serial_conn.flush()


def read_serial_available(
    serial_conn: object | None,
    serial_file: TextIO,
    *,
    logger_start: float,
) -> None:
    if serial_conn is None:
        return
    while getattr(serial_conn, "in_waiting", 0):
        line = serial_conn.readline().decode("utf-8", errors="replace").strip()
        if line:
            write_serial_event(
                serial_file,
                logger_start=logger_start,
                direction="RX",
                line=line,
                scheduled_time_ms=None,
            )


def write_serial_event(
    serial_file: TextIO,
    *,
    logger_start: float,
    direction: str,
    line: str,
    scheduled_time_ms: int | None,
) -> None:
    actual_elapsed_ms = round((time.monotonic() - logger_start) * 1000.0)
    scheduled = "" if scheduled_time_ms is None else str(scheduled_time_ms)
    serial_file.write(
        f"{actual_elapsed_ms},{scheduled},{direction},{line}\n"
    )
    serial_file.flush()


def format_all_command(theta_deg: tuple[float, float, float]) -> str:
    values = " ".join(_format_float(value) for value in theta_deg)
    return f"ALL {values}"


def _format_float(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


def _clean_zero(value: float) -> float:
    return 0.0 if math.isclose(value, 0.0, abs_tol=1e-12) else value


def _parse_exact_int(raw: str, *, path: Path) -> int:
    value = float(raw)
    rounded = round(value)
    if not math.isfinite(value) or not math.isclose(
        value, rounded, abs_tol=1e-9
    ):
        raise ValueError(f"Simscape time must be an integer millisecond: {path}")
    return rounded


def _parse_finite(raw: str, *, path: Path) -> float:
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"non-finite Simscape value: {path}")
    return value


def write_metadata(
    *,
    output_path: Path,
    args: argparse.Namespace,
    output_csv: Path,
    correction_csv: Path,
    serial_log: Path,
    model_path: Path | None,
    points: list[TrajectoryPoint],
    schedule: list[ScheduledPoint],
    summary: dict[str, int],
) -> None:
    content = {
        "run_id": args.run_id,
        "trajectory": args.trajectory,
        "correction": args.correction,
        "output_csv": str(output_csv),
        "correction_csv": str(correction_csv),
        "serial_log": str(serial_log),
        "simscape_csv": args.simscape_csv,
        "model": None if model_path is None else str(model_path),
        "dry_run": args.dry_run,
        "time_source": TIME_SOURCE,
        "theta_meas_source": THETA_MEAS_SOURCE,
        "row_count": len(schedule),
        "schedule_end_ms": schedule[-1].time_ms,
        "sampling": {
            "sample_period_s": args.sample_period_s,
            "command_update_period_s": args.command_update_period_s,
            "hold_s": args.hold_s,
            "circle_endpoint_hold_s": args.circle_endpoint_hold_s,
            "circle_points": args.circle_points,
            "circle_duration_s": args.circle_duration_s,
        },
        "correction_config": {
            "gain": args.gain,
            "max_xy_correction_mm": args.max_xy_correction_mm,
            "z_correction_enabled": False,
        },
        "ik": {
            "target_z_mm": args.target_z_mm,
            "theta_min_deg": args.theta_min_deg,
            "theta_max_deg": args.theta_max_deg,
        },
        "serial": {
            "port": args.port,
            "baudrate": args.baudrate,
            "ready_wait_s": args.ready_wait_s,
        },
        "summary": summary,
        "points": [asdict(point) for point in points],
    }
    write_json(output_path, content)


def write_json(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(content, json_file, ensure_ascii=True, indent=2)
        json_file.write("\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run 02 OFF/ON deterministic serial logger"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    manifest = subparsers.add_parser(
        "manifest",
        help="Write the finalized 24-run execution manifest",
    )
    manifest.add_argument("--date", required=True, help="YYYY-MM-DD")
    manifest.add_argument(
        "--output",
        type=Path,
        default=Path("experiments/run02_24_run_manifest.json"),
    )

    run = subparsers.add_parser("run", help="Execute or dry-run one Run 02 run")
    run.add_argument("trajectory", choices=TRAJECTORIES)
    run.add_argument("--correction", choices=CORRECTION_STATES, required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--port", default=None)
    run.add_argument("--baudrate", type=int, default=9600)
    run.add_argument("--output-csv", default=None)
    run.add_argument("--metadata-json", default=None)
    run.add_argument("--serial-log", default=None)
    run.add_argument("--correction-csv", default=None)
    run.add_argument("--simscape-csv", default=None)
    run.add_argument(
        "--model",
        default="virtual_sensor/models/ridge_run01_main_2026-06-06.npz",
    )
    run.add_argument("--target-z-mm", type=float, default=HOME_Z_MM)
    run.add_argument("--hold-s", type=float, default=DEFAULT_HOLD_S)
    run.add_argument(
        "--circle-endpoint-hold-s",
        type=float,
        default=DEFAULT_CIRCLE_ENDPOINT_HOLD_S,
    )
    run.add_argument(
        "--circle-points",
        type=int,
        default=DEFAULT_CIRCLE_POINTS,
    )
    run.add_argument(
        "--circle-duration-s",
        type=float,
        default=DEFAULT_CIRCLE_DURATION_S,
    )
    run.add_argument(
        "--sample-period-s",
        type=float,
        default=DEFAULT_SAMPLE_PERIOD_S,
    )
    run.add_argument(
        "--command-update-period-s",
        type=float,
        default=DEFAULT_COMMAND_UPDATE_PERIOD_S,
    )
    run.add_argument("--ready-wait-s", type=float, default=2.0)
    run.add_argument("--gain", type=float, default=DEFAULT_GAIN)
    run.add_argument(
        "--max-xy-correction-mm",
        type=float,
        default=DEFAULT_CLAMP_MM,
    )
    run.add_argument("--theta-min-deg", type=float, default=THETA_MIN_DEG)
    run.add_argument("--theta-max-deg", type=float, default=THETA_MAX_DEG)
    run.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
