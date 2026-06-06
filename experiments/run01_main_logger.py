from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import time
from typing import TextIO


SQRT_3_OVER_2 = math.sqrt(3.0) / 2.0
ARM_OUTWARD_UNIT_VECTORS: tuple[tuple[float, float], ...] = (
    (0.0, -1.0),
    (SQRT_3_OVER_2, 0.5),
    (-SQRT_3_OVER_2, 0.5),
)

UPPER_ARM_LENGTH_MM = 125.0
PARALLELOGRAM_LINK_LENGTH_MM = 300.0
BASE_CENTER_TO_SIDE_MM = 46.0
PLATFORM_CENTER_TO_VERTEX_MM = 27.177
HOME_Z_MM = -263.27731514697575

THETA_MIN_DEG = -45.0
THETA_MAX_DEG = 90.0
TIME_SOURCE = "pc_elapsed_ms"
THETA_MEAS_SOURCE = "command_echo_no_encoder"
DEFAULT_CIRCLE_POINTS = 72
DEFAULT_CIRCLE_DURATION_S = 30.0

FIELDNAMES = [
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


class InverseKinematicsError(ValueError):
    pass


@dataclass(frozen=True)
class TrajectoryPoint:
    phase: str
    target_x: float
    target_y: float
    target_z: float
    theta1_cmd: int
    theta2_cmd: int
    theta3_cmd: int
    hold_s: float

    @property
    def command(self) -> str:
        return f"ALL {self.theta1_cmd} {self.theta2_cmd} {self.theta3_cmd}"


@dataclass(frozen=True)
class MainLogRow:
    run_id: str
    time: int
    target_x: float
    target_y: float
    target_z: float
    theta1_cmd: int
    theta2_cmd: int
    theta3_cmd: int
    theta1_meas: int
    theta2_meas: int
    theta3_meas: int
    valid: bool
    phase: str
    command: str
    time_source: str
    theta_meas_source: str


def main() -> int:
    args = parse_args()
    output_csv = Path(args.output_csv or f"data/real/raw/main_{args.run_id}.csv")
    metadata_json = Path(args.metadata_json or output_csv.with_suffix(".json"))
    serial_log = Path(args.serial_log or output_csv.with_name(f"serial_{args.run_id}.txt"))

    points = build_trajectory_points(
        trajectory=args.trajectory,
        target_z_mm=args.target_z_mm,
        static_duration_s=args.duration_s,
        hold_s=args.hold_s,
        circle_points=args.circle_points,
        circle_duration_s=args.circle_duration_s,
        theta_min_deg=args.theta_min_deg,
        theta_max_deg=args.theta_max_deg,
    )

    rows = run_logger(
        points=points,
        run_id=args.run_id,
        output_csv=output_csv,
        serial_log=serial_log,
        port=args.port,
        baudrate=args.baudrate,
        sample_period_s=args.sample_period_s,
        ready_wait_s=args.ready_wait_s,
        dry_run=args.dry_run,
    )
    write_metadata(
        output_path=metadata_json,
        args=args,
        output_csv=output_csv,
        serial_log=serial_log,
        points=points,
        row_count=len(rows),
    )

    print(f"main_csv={output_csv}")
    print(f"metadata_json={metadata_json}")
    print(f"serial_log={serial_log}")
    print(f"row_count={len(rows)}")
    print(f"theta_meas_source={THETA_MEAS_SOURCE}")
    print(f"time_source={TIME_SOURCE}")
    return 0


def build_trajectory_points(
    *,
    trajectory: str,
    target_z_mm: float,
    static_duration_s: float,
    hold_s: float,
    circle_points: int,
    circle_duration_s: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> list[TrajectoryPoint]:
    if circle_points < 8:
        raise ValueError("circle_points must be at least 8.")
    if circle_duration_s <= 0.0:
        raise ValueError("circle_duration_s must be positive.")

    if trajectory in ("static_center_pre", "static_center_hold"):
        return [
            make_point(
                phase=trajectory,
                x_mm=0.0,
                y_mm=0.0,
                z_mm=target_z_mm,
                hold_s=static_duration_s,
                theta_min_deg=theta_min_deg,
                theta_max_deg=theta_max_deg,
            )
        ]

    if trajectory in ("cross_pm10_pre", "cross_pm40_pre", "cross_pm20", "cross_pm15_holdout"):
        cross_amplitudes_mm = {
            "cross_pm10_pre": 10.0,
            "cross_pm40_pre": 40.0,
            "cross_pm20": 20.0,
            "cross_pm15_holdout": 15.0,
        }
        amplitude_mm = cross_amplitudes_mm[trajectory]
        point_specs = [
            ("home_1", 0.0, 0.0),
            ("x_plus_stop", amplitude_mm, 0.0),
            ("home_2", 0.0, 0.0),
            ("x_minus_stop", -amplitude_mm, 0.0),
            ("home_3", 0.0, 0.0),
            ("y_plus_stop", 0.0, amplitude_mm),
            ("home_4", 0.0, 0.0),
            ("y_minus_stop", 0.0, -amplitude_mm),
            ("home_5", 0.0, 0.0),
        ]
    elif trajectory in ("square_pm10_pre", "square_pm40_pre", "square_pm20", "square_pm15_holdout"):
        square_amplitudes_mm = {
            "square_pm10_pre": 10.0,
            "square_pm40_pre": 40.0,
            "square_pm20": 20.0,
            "square_pm15_holdout": 15.0,
        }
        amplitude_mm = square_amplitudes_mm[trajectory]
        point_specs = [
            ("home_1", 0.0, 0.0),
            ("q1_x_plus_y_plus", amplitude_mm, amplitude_mm),
            ("q2_x_minus_y_plus", -amplitude_mm, amplitude_mm),
            ("q3_x_minus_y_minus", -amplitude_mm, -amplitude_mm),
            ("q4_x_plus_y_minus", amplitude_mm, -amplitude_mm),
            ("q1_x_plus_y_plus_2", amplitude_mm, amplitude_mm),
            ("home_2", 0.0, 0.0),
        ]
    elif trajectory in ("circle_r40", "circle_r40_holdout"):
        return build_circle_points(
            target_z_mm=target_z_mm,
            hold_s=hold_s,
            circle_points=circle_points,
            circle_duration_s=circle_duration_s,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
        )
    elif trajectory == "grid_3x3_pm40":
        point_specs = [
            ("home_1", 0.0, 0.0),
            ("x_minus_y_minus", -40.0, -40.0),
            ("x_center_y_minus", 0.0, -40.0),
            ("x_plus_y_minus", 40.0, -40.0),
            ("x_minus_y_center", -40.0, 0.0),
            ("center", 0.0, 0.0),
            ("x_plus_y_center", 40.0, 0.0),
            ("x_minus_y_plus", -40.0, 40.0),
            ("x_center_y_plus", 0.0, 40.0),
            ("x_plus_y_plus", 40.0, 40.0),
            ("home_2", 0.0, 0.0),
        ]
    else:
        raise ValueError(f"unsupported trajectory: {trajectory}")

    return [
        make_point(
            phase=phase,
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=target_z_mm,
            hold_s=hold_s,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
        )
        for phase, x_mm, y_mm in point_specs
    ]


def build_circle_points(
    *,
    target_z_mm: float,
    hold_s: float,
    circle_points: int,
    circle_duration_s: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> list[TrajectoryPoint]:
    point_specs: list[tuple[str, float, float, float]] = [
        ("home_1", 0.0, 0.0, hold_s),
        ("circle_start_x_plus", 40.0, 0.0, hold_s),
    ]
    step_hold_s = circle_duration_s / circle_points
    for index in range(1, circle_points + 1):
        angle_rad = (2.0 * math.pi * index) / circle_points
        x_mm = 40.0 * math.cos(angle_rad)
        y_mm = 40.0 * math.sin(angle_rad)
        point_specs.append(
            (
                f"circle_ccw_{index:03d}",
                _clean_zero(x_mm),
                _clean_zero(y_mm),
                step_hold_s,
            )
        )
    point_specs.append(("home_2", 0.0, 0.0, hold_s))

    return [
        make_point(
            phase=phase,
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=target_z_mm,
            hold_s=point_hold_s,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
        )
        for phase, x_mm, y_mm, point_hold_s in point_specs
    ]


def _clean_zero(value: float) -> float:
    return 0.0 if math.isclose(value, 0.0, abs_tol=1e-12) else value


def make_point(
    *,
    phase: str,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    hold_s: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> TrajectoryPoint:
    theta = delta_ik(
        x_mm=x_mm,
        y_mm=y_mm,
        z_mm=z_mm,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
    )
    return TrajectoryPoint(
        phase=phase,
        target_x=x_mm,
        target_y=y_mm,
        target_z=z_mm,
        theta1_cmd=round(theta[0]),
        theta2_cmd=round(theta[1]),
        theta3_cmd=round(theta[2]),
        hold_s=hold_s,
    )


def run_logger(
    *,
    points: list[TrajectoryPoint],
    run_id: str,
    output_csv: Path,
    serial_log: Path,
    port: str | None,
    baudrate: int,
    sample_period_s: float,
    ready_wait_s: float,
    dry_run: bool,
) -> list[MainLogRow]:
    if sample_period_s <= 0.0:
        raise ValueError("sample_period_s must be positive.")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    serial_log.parent.mkdir(parents=True, exist_ok=True)

    serial_conn = None
    if not dry_run:
        if port is None:
            raise SystemExit("--port is required unless --dry-run is used.")
        serial_conn = open_serial(port=port, baudrate=baudrate)
        time.sleep(ready_wait_s)

    rows: list[MainLogRow] = []
    last_time_ms = [-1]
    logger_start = time.monotonic()
    with output_csv.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        with serial_log.open("w", encoding="utf-8", newline="\n") as serial_file:
            for point in points:
                send_command(serial_conn, point.command, dry_run=dry_run)
                write_serial_event(
                    serial_file,
                    logger_start=logger_start,
                    direction="TX",
                    line=point.command,
                )
                rows.extend(
                    sample_hold(
                        point=point,
                        run_id=run_id,
                        logger_start=logger_start,
                        sample_period_s=sample_period_s,
                        writer=writer,
                        serial_conn=serial_conn,
                        serial_file=serial_file,
                        last_time_ms=last_time_ms,
                    )
                )

    if serial_conn is not None:
        serial_conn.close()
    return rows


def sample_hold(
    *,
    point: TrajectoryPoint,
    run_id: str,
    logger_start: float,
    sample_period_s: float,
    writer: csv.DictWriter,
    serial_conn: object | None,
    serial_file: TextIO,
    last_time_ms: list[int],
) -> list[MainLogRow]:
    rows: list[MainLogRow] = []
    hold_start = time.monotonic()
    next_sample = hold_start
    while True:
        now = time.monotonic()
        read_serial_available(serial_conn, serial_file, logger_start=logger_start)
        if now >= next_sample:
            elapsed_ms = round((now - logger_start) * 1000.0)
            if elapsed_ms <= last_time_ms[0]:
                elapsed_ms = last_time_ms[0] + 1
            last_time_ms[0] = elapsed_ms
            row = MainLogRow(
                run_id=run_id,
                time=elapsed_ms,
                target_x=point.target_x,
                target_y=point.target_y,
                target_z=point.target_z,
                theta1_cmd=point.theta1_cmd,
                theta2_cmd=point.theta2_cmd,
                theta3_cmd=point.theta3_cmd,
                theta1_meas=point.theta1_cmd,
                theta2_meas=point.theta2_cmd,
                theta3_meas=point.theta3_cmd,
                valid=True,
                phase=point.phase,
                command=point.command,
                time_source=TIME_SOURCE,
                theta_meas_source=THETA_MEAS_SOURCE,
            )
            writer.writerow(asdict(row))
            rows.append(row)
            next_sample += sample_period_s

        if now - hold_start >= point.hold_s:
            break
        time.sleep(min(0.01, sample_period_s / 2.0))
    return rows


def open_serial(*, port: str, baudrate: int) -> object:
    try:
        import serial
    except ImportError as exc:
        raise SystemExit(
            "pyserial is required for real serial logging. "
            "Install it on computer 2 with: python -m pip install pyserial"
        ) from exc

    return serial.Serial(port=port, baudrate=baudrate, timeout=0.01)


def send_command(serial_conn: object | None, command: str, *, dry_run: bool) -> None:
    if dry_run:
        return
    if serial_conn is None:
        raise RuntimeError("serial connection is not open.")
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
            )


def write_serial_event(
    serial_file: TextIO,
    *,
    logger_start: float,
    direction: str,
    line: str,
) -> None:
    elapsed_ms = round((time.monotonic() - logger_start) * 1000.0)
    serial_file.write(f"{elapsed_ms},{direction},{line}\n")
    serial_file.flush()


def delta_ik(
    *,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    theta_min_deg: float,
    theta_max_deg: float,
) -> tuple[float, float, float]:
    theta_values: list[float] = []
    for arm_vector in ARM_OUTWARD_UNIT_VECTORS:
        theta_values.append(
            solve_single_arm_ik(
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                arm_vector=arm_vector,
                theta_min_deg=theta_min_deg,
                theta_max_deg=theta_max_deg,
            )
        )
    return (theta_values[0], theta_values[1], theta_values[2])


def solve_single_arm_ik(
    *,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    arm_vector: tuple[float, float],
    theta_min_deg: float,
    theta_max_deg: float,
) -> float:
    p_i = x_mm * arm_vector[0] + y_mm * arm_vector[1]
    delta_offset = PLATFORM_CENTER_TO_VERTEX_MM - BASE_CENTER_TO_SIDE_MM
    e_term = -2.0 * UPPER_ARM_LENGTH_MM * (p_i + delta_offset)
    f_term = 2.0 * UPPER_ARM_LENGTH_MM * z_mm
    g_term = (
        x_mm * x_mm
        + y_mm * y_mm
        + delta_offset * delta_offset
        + 2.0 * delta_offset * p_i
        + z_mm * z_mm
        + UPPER_ARM_LENGTH_MM * UPPER_ARM_LENGTH_MM
        - PARALLELOGRAM_LINK_LENGTH_MM * PARALLELOGRAM_LINK_LENGTH_MM
    )
    discriminant = e_term * e_term + f_term * f_term - g_term * g_term
    if discriminant < 0.0:
        raise InverseKinematicsError(
            f"target is outside IK workspace: x={x_mm}, y={y_mm}, z={z_mm}"
        )

    sqrt_discriminant = math.sqrt(max(discriminant, 0.0))
    denominator = g_term - e_term
    if math.isclose(denominator, 0.0, abs_tol=1e-12):
        if math.isclose(f_term, 0.0, abs_tol=1e-12):
            raise InverseKinematicsError("IK denominator is singular.")
        t_candidates = (-g_term / (2.0 * f_term),)
    else:
        t_candidates = (
            (-f_term + sqrt_discriminant) / denominator,
            (-f_term - sqrt_discriminant) / denominator,
        )

    theta_candidates = [
        math.degrees(2.0 * math.atan(t_value))
        for t_value in t_candidates
    ]
    valid_thetas = [
        theta
        for theta in theta_candidates
        if theta_min_deg <= theta <= theta_max_deg
    ]
    if not valid_thetas:
        raise InverseKinematicsError(
            f"IK solution violates theta range: x={x_mm}, y={y_mm}, z={z_mm}"
        )
    return min(valid_thetas)


def write_metadata(
    *,
    output_path: Path,
    args: argparse.Namespace,
    output_csv: Path,
    serial_log: Path,
    points: list[TrajectoryPoint],
    row_count: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "run_id": args.run_id,
        "trajectory": args.trajectory,
        "output_csv": str(output_csv),
        "serial_log": str(serial_log),
        "row_count": row_count,
        "time_source": TIME_SOURCE,
        "theta_meas_source": THETA_MEAS_SOURCE,
        "command_protocol": "Arduino serial line: ALL theta1 theta2 theta3",
        "dry_run": args.dry_run,
        "serial": {
            "port": args.port,
            "baudrate": args.baudrate,
            "ready_wait_s": args.ready_wait_s,
        },
        "sampling": {
            "sample_period_s": args.sample_period_s,
            "static_duration_s": args.duration_s,
            "hold_s": args.hold_s,
            "circle_points": args.circle_points,
            "circle_duration_s": args.circle_duration_s,
        },
        "ik": {
            "target_z_mm": args.target_z_mm,
            "theta_min_deg": args.theta_min_deg,
            "theta_max_deg": args.theta_max_deg,
            "geometry": {
                "upper_arm_length_mm": UPPER_ARM_LENGTH_MM,
                "parallelogram_link_length_mm": PARALLELOGRAM_LINK_LENGTH_MM,
                "base_center_to_side_mm": BASE_CENTER_TO_SIDE_MM,
                "platform_center_to_vertex_mm": PLATFORM_CENTER_TO_VERTEX_MM,
            },
        },
        "points": [asdict(point) for point in points],
    }
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, ensure_ascii=True, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run 01 main logger for the PC connected to Arduino. "
            "The script sends ALL theta commands and records a main CSV."
        )
    )
    parser.add_argument(
        "trajectory",
        choices=(
            "static_center_pre",
            "cross_pm10_pre",
            "square_pm10_pre",
            "cross_pm40_pre",
            "square_pm40_pre",
            "static_center_hold",
            "cross_pm20",
            "square_pm20",
            "circle_r40",
            "grid_3x3_pm40",
            "cross_pm15_holdout",
            "square_pm15_holdout",
            "circle_r40_holdout",
        ),
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--port", default=None, help="Arduino COM port, e.g. COM3.")
    parser.add_argument("--baudrate", type=int, default=9600)
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--metadata-json", default=None)
    parser.add_argument("--serial-log", default=None)
    parser.add_argument("--target-z-mm", type=float, default=HOME_Z_MM)
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--hold-s", type=float, default=1.0)
    parser.add_argument("--circle-points", type=int, default=DEFAULT_CIRCLE_POINTS)
    parser.add_argument("--circle-duration-s", type=float, default=DEFAULT_CIRCLE_DURATION_S)
    parser.add_argument("--sample-period-s", type=float, default=0.1)
    parser.add_argument("--ready-wait-s", type=float, default=2.0)
    parser.add_argument("--theta-min-deg", type=float, default=THETA_MIN_DEG)
    parser.add_argument("--theta-max-deg", type=float, default=THETA_MAX_DEG)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
