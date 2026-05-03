from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Iterable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinematics.forward_kinematics import ForwardKinematicsError, delta_fk
from kinematics.inverse_kinematics import diagnose_delta_ik


@dataclass(frozen=True)
class SweepConfig:
    x_min_mm: float
    x_max_mm: float
    x_step_mm: float
    y_min_mm: float
    y_max_mm: float
    y_step_mm: float
    z_min_mm: float
    z_max_mm: float
    z_step_mm: float
    theta_min_deg: float
    theta_max_deg: float
    roundtrip_tolerance_mm: float


@dataclass(frozen=True)
class SweepPointResult:
    x_mm: float
    y_mm: float
    z_mm: float
    theta_min_deg_limit: float
    theta_max_deg_limit: float
    status: str
    reason: str
    ik_failure_summary: str | None
    ik_arm1_status: str | None
    ik_arm2_status: str | None
    ik_arm3_status: str | None
    theta1_deg: float | None
    theta2_deg: float | None
    theta3_deg: float | None
    fk_x_mm: float | None
    fk_y_mm: float | None
    fk_z_mm: float | None
    roundtrip_error_mm: float | None
    fk_iterations: int | None
    fk_max_residual_mm2: float | None


def main() -> int:
    args = _parse_args()
    config = SweepConfig(
        x_min_mm=args.x_min,
        x_max_mm=args.x_max,
        x_step_mm=args.x_step,
        y_min_mm=args.y_min,
        y_max_mm=args.y_max,
        y_step_mm=args.y_step,
        z_min_mm=args.z_min,
        z_max_mm=args.z_max,
        z_step_mm=args.z_step,
        theta_min_deg=args.theta_min,
        theta_max_deg=args.theta_max,
        roundtrip_tolerance_mm=args.roundtrip_tolerance,
    )
    results = run_workspace_sweep(config)
    summary = build_summary(config, results)
    _print_summary(summary)

    if args.output_csv is not None:
        output_csv_path = Path(args.output_csv)
        write_results_csv(results, output_csv_path)
        write_summary_json(summary, output_csv_path.with_suffix(".json"))
        print(f"csv_written={args.output_csv}")
        print(f"json_written={output_csv_path.with_suffix('.json')}")

    return 0


def run_workspace_sweep(config: SweepConfig) -> list[SweepPointResult]:
    results: list[SweepPointResult] = []
    for z_mm in _inclusive_range(config.z_min_mm, config.z_max_mm, config.z_step_mm):
        for y_mm in _inclusive_range(config.y_min_mm, config.y_max_mm, config.y_step_mm):
            for x_mm in _inclusive_range(config.x_min_mm, config.x_max_mm, config.x_step_mm):
                results.append(
                    _evaluate_point(
                        x_mm=x_mm,
                        y_mm=y_mm,
                        z_mm=z_mm,
                        theta_min_deg=config.theta_min_deg,
                        theta_max_deg=config.theta_max_deg,
                        roundtrip_tolerance_mm=config.roundtrip_tolerance_mm,
                    )
                )
    return results


def write_results_csv(results: Iterable[SweepPointResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "x_mm",
                "y_mm",
                "z_mm",
                "theta_min_deg_limit",
                "theta_max_deg_limit",
                "status",
                "reason",
                "ik_failure_summary",
                "ik_arm1_status",
                "ik_arm2_status",
                "ik_arm3_status",
                "theta1_deg",
                "theta2_deg",
                "theta3_deg",
                "fk_x_mm",
                "fk_y_mm",
                "fk_z_mm",
                "roundtrip_error_mm",
                "fk_iterations",
                "fk_max_residual_mm2",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def write_summary_json(summary: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(summary, json_file, ensure_ascii=True, indent=2)


def _evaluate_point(
    *,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    theta_min_deg: float,
    theta_max_deg: float,
    roundtrip_tolerance_mm: float,
) -> SweepPointResult:
    ik_diagnostic = diagnose_delta_ik(
        x_mm,
        y_mm,
        z_mm,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
    )
    arm_statuses = tuple(arm.status for arm in ik_diagnostic.arm_diagnostics)
    if ik_diagnostic.result is None:
        return SweepPointResult(
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            theta_min_deg_limit=theta_min_deg,
            theta_max_deg_limit=theta_max_deg,
            status="fail",
            reason="ik_reject",
            ik_failure_summary=ik_diagnostic.failure_summary,
            ik_arm1_status=arm_statuses[0],
            ik_arm2_status=arm_statuses[1],
            ik_arm3_status=arm_statuses[2],
            theta1_deg=None,
            theta2_deg=None,
            theta3_deg=None,
            fk_x_mm=None,
            fk_y_mm=None,
            fk_z_mm=None,
            roundtrip_error_mm=None,
            fk_iterations=None,
            fk_max_residual_mm2=None,
        )

    theta_tuple = ik_diagnostic.result.as_tuple()
    try:
        fk_result = delta_fk(*theta_tuple)
    except ForwardKinematicsError:
        return SweepPointResult(
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            theta_min_deg_limit=theta_min_deg,
            theta_max_deg_limit=theta_max_deg,
            status="fail",
            reason="fk_fail",
            ik_failure_summary=None,
            ik_arm1_status=arm_statuses[0],
            ik_arm2_status=arm_statuses[1],
            ik_arm3_status=arm_statuses[2],
            theta1_deg=theta_tuple[0],
            theta2_deg=theta_tuple[1],
            theta3_deg=theta_tuple[2],
            fk_x_mm=None,
            fk_y_mm=None,
            fk_z_mm=None,
            roundtrip_error_mm=None,
            fk_iterations=None,
            fk_max_residual_mm2=None,
        )

    fk_tuple = fk_result.as_tuple()
    roundtrip_error_mm = _distance_mm((x_mm, y_mm, z_mm), fk_tuple)
    if roundtrip_error_mm > roundtrip_tolerance_mm:
        status = "fail"
        reason = "roundtrip_error_exceeded"
    else:
        status = "ok"
        reason = "ok"

    return SweepPointResult(
        x_mm=x_mm,
        y_mm=y_mm,
        z_mm=z_mm,
        theta_min_deg_limit=theta_min_deg,
        theta_max_deg_limit=theta_max_deg,
        status=status,
        reason=reason,
        ik_failure_summary=None,
        ik_arm1_status=arm_statuses[0],
        ik_arm2_status=arm_statuses[1],
        ik_arm3_status=arm_statuses[2],
        theta1_deg=theta_tuple[0],
        theta2_deg=theta_tuple[1],
        theta3_deg=theta_tuple[2],
        fk_x_mm=fk_tuple[0],
        fk_y_mm=fk_tuple[1],
        fk_z_mm=fk_tuple[2],
        roundtrip_error_mm=roundtrip_error_mm,
        fk_iterations=fk_result.iterations,
        fk_max_residual_mm2=fk_result.max_residual_mm2,
    )


def build_summary(config: SweepConfig, results: list[SweepPointResult]) -> dict[str, object]:
    total_points = len(results)
    reason_counts: dict[str, int] = {}
    ok_results: list[SweepPointResult] = []
    for result in results:
        reason_counts[result.reason] = reason_counts.get(result.reason, 0) + 1
        if result.status == "ok":
            ok_results.append(result)

    summary: dict[str, object] = {
        "sweep_config": {
            "x_min_mm": config.x_min_mm,
            "x_max_mm": config.x_max_mm,
            "x_step_mm": config.x_step_mm,
            "y_min_mm": config.y_min_mm,
            "y_max_mm": config.y_max_mm,
            "y_step_mm": config.y_step_mm,
            "z_min_mm": config.z_min_mm,
            "z_max_mm": config.z_max_mm,
            "z_step_mm": config.z_step_mm,
            "theta_min_deg": config.theta_min_deg,
            "theta_max_deg": config.theta_max_deg,
            "roundtrip_tolerance_mm": config.roundtrip_tolerance_mm,
        },
        "total_points": total_points,
        "ok_points": len(ok_results),
        "fail_points": total_points - len(ok_results),
        "reason_counts": dict(sorted(reason_counts.items())),
    }
    arm_reason_counts: dict[str, dict[str, int]] = {
        "arm1": {},
        "arm2": {},
        "arm3": {},
    }
    for result in results:
        for arm_name, arm_status in (
            ("arm1", result.ik_arm1_status),
            ("arm2", result.ik_arm2_status),
            ("arm3", result.ik_arm3_status),
        ):
            if arm_status is None:
                continue
            arm_reason_counts[arm_name][arm_status] = arm_reason_counts[arm_name].get(arm_status, 0) + 1
    summary["ik_arm_status_counts"] = {
        arm_name: dict(sorted(counts.items()))
        for arm_name, counts in arm_reason_counts.items()
    }
    if ok_results:
        max_roundtrip = max(result.roundtrip_error_mm or 0.0 for result in ok_results)
        avg_roundtrip = sum(result.roundtrip_error_mm or 0.0 for result in ok_results) / len(ok_results)
        max_iterations = max(result.fk_iterations or 0 for result in ok_results)
        summary["ok_metrics"] = {
            "max_roundtrip_error_mm": max_roundtrip,
            "avg_roundtrip_error_mm": avg_roundtrip,
            "max_fk_iterations": max_iterations,
        }

    sample_failures = [result for result in results if result.status != "ok"][:10]
    if sample_failures:
        summary["sample_failures"] = [
            {
                "x_mm": result.x_mm,
                "y_mm": result.y_mm,
                "z_mm": result.z_mm,
                "reason": result.reason,
            }
            for result in sample_failures
        ]
    return summary


def _print_summary(summary: dict[str, object]) -> None:
    config = summary["sweep_config"]
    print(
        "sweep_config="
        f"x[{config['x_min_mm']},{config['x_max_mm']}] step {config['x_step_mm']}, "
        f"y[{config['y_min_mm']},{config['y_max_mm']}] step {config['y_step_mm']}, "
        f"z[{config['z_min_mm']},{config['z_max_mm']}] step {config['z_step_mm']}, "
        f"theta[{config['theta_min_deg']},{config['theta_max_deg']}], "
        f"roundtrip_tolerance_mm={config['roundtrip_tolerance_mm']}"
    )
    print(f"total_points={summary['total_points']}")
    print(f"ok_points={summary['ok_points']}")
    print(f"fail_points={summary['fail_points']}")
    for reason, count in summary["reason_counts"].items():
        print(f"{reason}={count}")
    for arm_name, counts in summary["ik_arm_status_counts"].items():
        print(f"{arm_name}_status_counts={counts}")

    ok_metrics = summary.get("ok_metrics")
    if ok_metrics is not None:
        print(f"max_roundtrip_error_mm={ok_metrics['max_roundtrip_error_mm']:.6f}")
        print(f"avg_roundtrip_error_mm={ok_metrics['avg_roundtrip_error_mm']:.6f}")
        print(f"max_fk_iterations={ok_metrics['max_fk_iterations']}")

    sample_failures = summary.get("sample_failures")
    if sample_failures:
        print("sample_failures:")
        for result in sample_failures:
            print(
                f"  point=({result['x_mm']:.3f}, {result['y_mm']:.3f}, {result['z_mm']:.3f}) "
                f"reason={result['reason']}"
            )


def _inclusive_range(start: float, stop: float, step: float) -> list[float]:
    if step <= 0.0:
        raise ValueError("range step must be positive.")
    values: list[float] = []
    current = start
    epsilon = step * 1e-9
    while current <= stop + epsilon:
        values.append(round(current, 10))
        current += step
    return values


def _distance_mm(
    lhs: tuple[float, float, float],
    rhs: tuple[float, float, float],
) -> float:
    return math.sqrt(
        (lhs[0] - rhs[0]) ** 2
        + (lhs[1] - rhs[1]) ** 2
        + (lhs[2] - rhs[2]) ** 2
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a coarse workspace sweep against the current IK/FK implementation."
    )
    parser.add_argument("--x-min", type=float, default=-30.0)
    parser.add_argument("--x-max", type=float, default=30.0)
    parser.add_argument("--x-step", type=float, default=15.0)
    parser.add_argument("--y-min", type=float, default=-30.0)
    parser.add_argument("--y-max", type=float, default=30.0)
    parser.add_argument("--y-step", type=float, default=15.0)
    parser.add_argument("--z-min", type=float, default=-260.0)
    parser.add_argument("--z-max", type=float, default=-180.0)
    parser.add_argument("--z-step", type=float, default=20.0)
    parser.add_argument("--theta-min", type=float, default=0.0)
    parser.add_argument("--theta-max", type=float, default=90.0)
    parser.add_argument("--roundtrip-tolerance", type=float, default=1e-3)
    parser.add_argument("--output-csv", type=str, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
