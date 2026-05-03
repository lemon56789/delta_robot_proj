from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinematics.forward_kinematics import delta_fk
from kinematics.inverse_kinematics import delta_ik


OUTPUT_CSV = Path("data/fake_pipeline/fake_pipeline_sample_2026-05-04.csv")
OUTPUT_JSON = Path("data/fake_pipeline/fake_pipeline_sample_2026-05-04.json")
DT_MS = 20
NUM_SAMPLES = 180
THETA_MIN_DEG = 0.0
THETA_MAX_DEG = 90.0

THETA_BIAS_DEG = (0.8, -0.6, 0.4)
THETA_LAG_ALPHA = 0.82
THETA_WOBBLE_DEG = (0.35, 0.25, -0.3)


@dataclass(frozen=True)
class FakePipelineRow:
    time: int
    target_x: float
    target_y: float
    target_z: float
    theta1_cmd: float
    theta2_cmd: float
    theta3_cmd: float
    theta1_meas: float
    theta2_meas: float
    theta3_meas: float
    sim_x: float
    sim_y: float
    sim_z: float
    error_x: float
    error_y: float
    error_z: float


def main() -> int:
    rows = build_fake_pipeline_rows()
    write_rows_csv(rows, OUTPUT_CSV)
    metadata = build_metadata(rows)
    write_metadata_json(metadata, OUTPUT_JSON)
    print(f"csv_written={OUTPUT_CSV}")
    print(f"json_written={OUTPUT_JSON}")
    print(f"row_count={len(rows)}")
    print(
        "trajectory_bounds="
        f"x[{min(row.target_x for row in rows):.3f},{max(row.target_x for row in rows):.3f}], "
        f"y[{min(row.target_y for row in rows):.3f},{max(row.target_y for row in rows):.3f}], "
        f"z[{min(row.target_z for row in rows):.3f},{max(row.target_z for row in rows):.3f}]"
    )
    return 0


def build_fake_pipeline_rows() -> list[FakePipelineRow]:
    rows: list[FakePipelineRow] = []
    previous_meas = (0.0, 0.0, 0.0)
    for index in range(NUM_SAMPLES):
        phase = 2.0 * math.pi * index / NUM_SAMPLES
        target = generate_target_position(phase)
        theta_cmd = delta_ik(
            *target,
            theta_min_deg=THETA_MIN_DEG,
            theta_max_deg=THETA_MAX_DEG,
        ).as_tuple()
        theta_meas = generate_fake_measured_angles(index, theta_cmd, previous_meas)
        previous_meas = theta_meas

        sim_position = delta_fk(*theta_cmd).as_tuple()
        measured_position = delta_fk(
            *theta_meas,
            initial_guess_mm=sim_position,
        ).as_tuple()

        rows.append(
            FakePipelineRow(
                time=index * DT_MS,
                target_x=target[0],
                target_y=target[1],
                target_z=target[2],
                theta1_cmd=theta_cmd[0],
                theta2_cmd=theta_cmd[1],
                theta3_cmd=theta_cmd[2],
                theta1_meas=theta_meas[0],
                theta2_meas=theta_meas[1],
                theta3_meas=theta_meas[2],
                sim_x=sim_position[0],
                sim_y=sim_position[1],
                sim_z=sim_position[2],
                error_x=measured_position[0] - sim_position[0],
                error_y=measured_position[1] - sim_position[1],
                error_z=measured_position[2] - sim_position[2],
            )
        )
    return rows


def generate_target_position(phase: float) -> tuple[float, float, float]:
    # Keep the first fake pipeline inside the conservative safe zone so the
    # dataset focuses on end-to-end wiring rather than boundary behavior.
    x_mm = 15.0 * math.sin(phase)
    y_mm = 12.0 * math.sin(2.0 * phase + 0.4)
    z_mm = -220.0 + 8.0 * math.cos(phase)
    return (x_mm, y_mm, z_mm)


def generate_fake_measured_angles(
    index: int,
    theta_cmd: tuple[float, float, float],
    previous_meas: tuple[float, float, float],
) -> tuple[float, float, float]:
    phase = 2.0 * math.pi * index / NUM_SAMPLES
    measured: list[float] = []
    for arm_index, theta_value in enumerate(theta_cmd):
        blended = THETA_LAG_ALPHA * previous_meas[arm_index] + (1.0 - THETA_LAG_ALPHA) * theta_value
        wobble = THETA_WOBBLE_DEG[arm_index] * math.sin(phase + 0.6 * arm_index)
        measured.append(blended + THETA_BIAS_DEG[arm_index] + wobble)
    return tuple(measured)  # type: ignore[return-value]


def write_rows_csv(rows: list[FakePipelineRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def build_metadata(rows: list[FakePipelineRow]) -> dict[str, object]:
    return {
        "row_count": len(rows),
        "time": {
            "dt_ms": DT_MS,
            "start_ms": rows[0].time if rows else 0,
            "end_ms": rows[-1].time if rows else 0,
        },
        "trajectory": {
            "type": "deterministic_lissajous_like",
            "x_min_mm": min(row.target_x for row in rows),
            "x_max_mm": max(row.target_x for row in rows),
            "y_min_mm": min(row.target_y for row in rows),
            "y_max_mm": max(row.target_y for row in rows),
            "z_min_mm": min(row.target_z for row in rows),
            "z_max_mm": max(row.target_z for row in rows),
        },
        "angle_limits": {
            "theta_min_deg": THETA_MIN_DEG,
            "theta_max_deg": THETA_MAX_DEG,
            "range_type": "hardware-safe provisional",
        },
        "fake_measurement_model": {
            "theta_bias_deg": list(THETA_BIAS_DEG),
            "theta_lag_alpha": THETA_LAG_ALPHA,
            "theta_wobble_deg": list(THETA_WOBBLE_DEG),
        },
        "csv_columns": [
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
        ],
        "error_summary": {
            "max_abs_error_x_mm": max(abs(row.error_x) for row in rows),
            "max_abs_error_y_mm": max(abs(row.error_y) for row in rows),
            "max_abs_error_z_mm": max(abs(row.error_z) for row in rows),
        },
    }


def write_metadata_json(metadata: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(metadata, json_file, ensure_ascii=True, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
