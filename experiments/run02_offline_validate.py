from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any, Iterable

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual_sensor.correction_engine import (
    CorrectionConfig,
    CorrectionEngine,
    CorrectionResult,
)
from virtual_sensor.ridge_model import RidgeModel


DEFAULT_GAINS: tuple[float, ...] = (0.25, 0.5, 1.0)
DEFAULT_CLAMPS_MM: tuple[float, ...] = (2.0, 4.0, 6.0)
MAIN_PATTERN = "merged_2026-06-06_run01_main_*.csv"
HOLDOUT_PATTERN = "merged_2026-06-06_run01_holdout_*.csv"


def main() -> int:
    args = _parse_args()
    model = RidgeModel.load(args.model)
    main_paths = sorted(args.input_dir.glob(args.main_pattern))
    holdout_paths = sorted(args.input_dir.glob(args.holdout_pattern))
    if not main_paths:
        raise ValueError("no Run 01-main input files found")
    if not holdout_paths:
        raise ValueError("no Run 01-holdout input files found")

    main_rows = _load_rows(main_paths, feature_names=model.feature_names)
    holdout_rows = _load_rows(holdout_paths, feature_names=model.feature_names)
    gains = _unique_sorted(args.gain or DEFAULT_GAINS)
    clamps_mm = _unique_sorted(args.clamp_mm or DEFAULT_CLAMPS_MM)

    candidates: list[dict[str, Any]] = []
    for gain in gains:
        for clamp_mm in clamps_mm:
            config = CorrectionConfig(
                gain=gain,
                max_xy_correction_mm=clamp_mm,
                theta_min_deg=args.theta_min_deg,
                theta_max_deg=args.theta_max_deg,
            )
            engine = CorrectionEngine(model, config)
            candidates.append(
                {
                    "gain": gain,
                    "max_xy_correction_mm": clamp_mm,
                    "main": _evaluate_rows(engine, main_rows),
                    "holdout_safety_only": _evaluate_rows(engine, holdout_rows),
                }
            )

    start_candidate = _select_main_only_start_candidate(candidates)
    report = {
        "report_type": "run02_correction_offline_validation",
        "model_path": str(args.model),
        "model_alpha": model.alpha,
        "feature_columns": list(model.feature_names),
        "target_columns": list(model.target_names),
        "correction_policy": {
            "equation": "target_xy - gain * predicted_error_xy",
            "xy_clamp": "vector_norm",
            "z_correction_enabled": False,
            "fallback": "nominal target and nominal theta command",
            "theta_limits_deg": [args.theta_min_deg, args.theta_max_deg],
        },
        "input_groups": {
            "main": {
                "role": "configuration safety analysis",
                "files": [str(path) for path in main_paths],
                "row_count": len(main_rows),
            },
            "holdout": {
                "role": "replay compatibility and IK safety only",
                "files": [str(path) for path in holdout_paths],
                "row_count": len(holdout_rows),
                "target_error_columns_used": False,
            },
        },
        "candidate_grid": {
            "gains": list(gains),
            "max_xy_correction_mm": list(clamps_mm),
            "ranking_by_holdout_error": False,
        },
        "candidates": candidates,
        "provisional_hardware_start_candidate": start_candidate,
        "start_candidate_policy": (
            "main-only safety filter: zero fallback, zero limit violation, "
            "at most 5 percent clamp rate; then lowest gain and lowest clamp"
        ),
        "commands": {
            "offline_validation": shlex.join([sys.executable, *sys.argv]),
        },
        "code_version": _git_version(),
        "limitations": [
            "offline replay does not prove real hardware improvement",
            "theta*_meas is command_echo_no_encoder",
            "holdout labels are not read or used to tune gain or clamp",
            "physical execution still requires a staged low-gain hardware gate",
        ],
    }
    _write_json(args.report_output, report)

    print(f"main_files={len(main_paths)} main_rows={len(main_rows)}")
    print(f"holdout_files={len(holdout_paths)} holdout_rows={len(holdout_rows)}")
    print(f"candidate_count={len(candidates)}")
    print(
        "provisional_hardware_start_candidate="
        f"{json.dumps(start_candidate, sort_keys=True)}"
    )
    print(f"report_output={args.report_output}")
    return 0


def _load_rows(
    paths: Iterable[Path],
    *,
    feature_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    required_columns = (
        "target_x",
        "target_y",
        "target_z",
        "theta1_cmd",
        "theta2_cmd",
        "theta3_cmd",
        *feature_names,
    )
    rows: list[dict[str, Any]] = []
    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None:
                raise ValueError(f"CSV header is missing: {path}")
            missing = [
                column
                for column in required_columns
                if column not in reader.fieldnames
            ]
            if missing:
                raise ValueError(f"{path} is missing columns: {missing}")
            for row_index, raw_row in enumerate(reader, start=2):
                parsed = {
                    column: _parse_finite_float(
                        raw_row.get(column),
                        path=path,
                        row_index=row_index,
                        column=column,
                    )
                    for column in required_columns
                }
                rows.append(
                    {
                        "run_id": path.stem.removeprefix("merged_"),
                        "target_xyz_mm": (
                            parsed["target_x"],
                            parsed["target_y"],
                            parsed["target_z"],
                        ),
                        "nominal_theta_deg": (
                            parsed["theta1_cmd"],
                            parsed["theta2_cmd"],
                            parsed["theta3_cmd"],
                        ),
                        "feature_values": tuple(
                            parsed[name] for name in feature_names
                        ),
                    }
                )
    return rows


def _parse_finite_float(
    raw_value: str | None,
    *,
    path: Path,
    row_index: int,
    column: str,
) -> float:
    if raw_value is None or raw_value == "":
        raise ValueError(f"{path}:{row_index} empty column {column}")
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"{path}:{row_index} non-numeric column {column}: {raw_value}"
        ) from exc
    if not math.isfinite(value):
        raise ValueError(f"{path}:{row_index} non-finite column {column}")
    return value


def _evaluate_rows(
    engine: CorrectionEngine,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    results = [
        engine.apply(
            target_xyz_mm=row["target_xyz_mm"],
            nominal_theta_deg=row["nominal_theta_deg"],
            feature_names=engine.feature_names,
            feature_values=row["feature_values"],
        )
        for row in rows
    ]
    return _summarize_results(results, config=engine.config)


def _summarize_results(
    results: list[CorrectionResult],
    *,
    config: CorrectionConfig,
) -> dict[str, Any]:
    if not results:
        raise ValueError("cannot summarize empty correction results")

    prediction_norms = np.asarray(
        [math.hypot(*result.predicted_error_xyz_mm[:2]) for result in results]
    )
    requested_norms = np.asarray(
        [
            math.hypot(*result.requested_correction_xyz_mm[:2])
            for result in results
        ]
    )
    applied_norms = np.asarray(
        [
            math.hypot(*result.applied_correction_xyz_mm[:2])
            for result in results
        ]
    )
    theta_values = np.asarray(
        [result.corrected_theta_deg for result in results],
        dtype=np.float64,
    )
    status_counts = Counter(result.status for result in results)
    clamp_count = sum(result.correction_clamped for result in results)
    fallback_count = sum(result.fallback_used for result in results)
    correction_limit_violation_count = int(
        np.count_nonzero(
            applied_norms > config.max_xy_correction_mm + 1e-9
        )
    )
    theta_limit_violation_count = int(
        np.count_nonzero(
            (theta_values < config.theta_min_deg - 1e-9)
            | (theta_values > config.theta_max_deg + 1e-9)
        )
    )
    max_z_correction = max(
        abs(result.applied_correction_xyz_mm[2]) for result in results
    )

    return {
        "row_count": len(results),
        "prediction_xy_norm_mm": _distribution(prediction_norms),
        "requested_correction_xy_norm_mm": _distribution(requested_norms),
        "applied_correction_xy_norm_mm": _distribution(applied_norms),
        "clamp_count": clamp_count,
        "clamp_rate_percent": 100.0 * clamp_count / len(results),
        "fallback_count": fallback_count,
        "fallback_rate_percent": 100.0 * fallback_count / len(results),
        "correction_limit_violation_count": correction_limit_violation_count,
        "theta_limit_violation_count": theta_limit_violation_count,
        "status_counts": dict(sorted(status_counts.items())),
        "corrected_theta_min_deg": [
            float(value) for value in theta_values.min(axis=0)
        ],
        "corrected_theta_max_deg": [
            float(value) for value in theta_values.max(axis=0)
        ],
        "max_abs_applied_z_correction_mm": float(max_z_correction),
    }


def _distribution(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(values.mean()),
        "p50": float(np.quantile(values, 0.50)),
        "p90": float(np.quantile(values, 0.90)),
        "p95": float(np.quantile(values, 0.95)),
        "p99": float(np.quantile(values, 0.99)),
        "max": float(values.max()),
    }


def _select_main_only_start_candidate(
    candidates: list[dict[str, Any]],
) -> dict[str, float] | None:
    eligible = [
        candidate
        for candidate in candidates
        if candidate["main"]["fallback_count"] == 0
        and candidate["main"]["correction_limit_violation_count"] == 0
        and candidate["main"]["theta_limit_violation_count"] == 0
        and candidate["main"]["max_abs_applied_z_correction_mm"] == 0.0
        and candidate["main"]["clamp_rate_percent"] <= 5.0
    ]
    if not eligible:
        return None
    selected = min(
        eligible,
        key=lambda candidate: (
            candidate["gain"],
            candidate["max_xy_correction_mm"],
        ),
    )
    return {
        "gain": selected["gain"],
        "max_xy_correction_mm": selected["max_xy_correction_mm"],
        "main_clamp_rate_percent": selected["main"]["clamp_rate_percent"],
        "main_fallback_rate_percent": selected["main"][
            "fallback_rate_percent"
        ],
    }


def _unique_sorted(values: Iterable[float]) -> tuple[float, ...]:
    result = tuple(sorted(set(float(value) for value in values)))
    if not result:
        raise ValueError("candidate list must not be empty")
    return result


def _git_version() -> dict[str, Any]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return {"commit": revision, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def _write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(content, json_file, ensure_ascii=True, indent=2)
        json_file.write("\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay the frozen virtual sensor through the Run 02 correction "
            "engine without serial or hardware access."
        )
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            "virtual_sensor/models/ridge_run01_main_2026-06-06.npz"
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/processed"),
    )
    parser.add_argument("--main-pattern", default=MAIN_PATTERN)
    parser.add_argument("--holdout-pattern", default=HOLDOUT_PATTERN)
    parser.add_argument("--gain", action="append", type=float)
    parser.add_argument("--clamp-mm", action="append", type=float)
    parser.add_argument("--theta-min-deg", type=float, default=-45.0)
    parser.add_argument("--theta-max-deg", type=float, default=90.0)
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path(
            "experiments/results/"
            "run02_correction_offline_validation_2026-06-06.json"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
