from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any

import numpy as np
import numpy.typing as npt

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual_sensor.dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
    load_virtual_sensor_dataset,
)
from virtual_sensor.ridge_model import RidgeModel, fit_ridge


DEFAULT_ALPHA_GRID: tuple[float, ...] = (
    0.0,
    1e-4,
    1e-3,
    1e-2,
    1e-1,
    1.0,
    10.0,
    100.0,
    1000.0,
)
RUN_ID_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})_run01_main_"
    r"(?P<trajectory>.+)_(?P<repetition>r0[1-3])$"
)


def main() -> int:
    args = _parse_args()
    run_data = _discover_runs(args.input_dir, args.input_pattern)
    alpha_grid = tuple(args.alpha) if args.alpha else DEFAULT_ALPHA_GRID
    _validate_run_set(run_data)

    cv_results = [
        _cross_validate_alpha(run_data, alpha=alpha)
        for alpha in alpha_grid
    ]
    selected = min(
        cv_results,
        key=lambda result: (
            result["aggregate"]["mean_xy_rmse"],
            result["aggregate"]["mean_xy_mae"],
            result["alpha"],
        ),
    )
    selected_alpha = float(selected["alpha"])

    all_run_ids = tuple(sorted(run_data))
    all_features = np.concatenate(
        [run_data[run_id]["features"] for run_id in all_run_ids], axis=0
    )
    all_targets = np.concatenate(
        [run_data[run_id]["targets"] for run_id in all_run_ids], axis=0
    )
    final_model = fit_ridge(
        all_features,
        all_targets,
        alpha=selected_alpha,
        feature_names=FEATURE_COLUMNS,
        target_names=TARGET_COLUMNS,
        training_run_ids=all_run_ids,
    )
    final_model.save(args.model_output)
    reloaded_model = RidgeModel.load(args.model_output)
    reload_max_abs_difference = float(
        np.max(
            np.abs(
                final_model.predict(all_features)
                - reloaded_model.predict(all_features)
            )
        )
    )

    report = {
        "report_type": "ridge_run01_main_cv",
        "input_pattern": str(args.input_dir / args.input_pattern),
        "feature_columns": list(FEATURE_COLUMNS),
        "target_columns": list(TARGET_COLUMNS),
        "alpha_grid": list(alpha_grid),
        "selection_policy": {
            "primary": "lowest mean per-run XY Euclidean RMSE",
            "tie_break": [
                "lowest mean per-run XY Euclidean MAE",
                "smallest alpha",
            ],
        },
        "fit_weighting": "row_weighted_within_each_training_fold",
        "fold_policy": {
            "r01": "validate r01; train r02+r03",
            "r02": "validate r02; train r01+r03",
            "r03": "validate r03; train r01+r02",
        },
        "runs": [
            {
                "run_id": run_id,
                "trajectory": run_data[run_id]["trajectory"],
                "repetition": run_data[run_id]["repetition"],
                "row_count": int(run_data[run_id]["features"].shape[0]),
                "csv_path": str(run_data[run_id]["path"]),
            }
            for run_id in all_run_ids
        ],
        "alpha_results": cv_results,
        "selected_alpha": selected_alpha,
        "selected_aggregate_metrics": selected["aggregate"],
        "final_model": {
            "path": str(args.model_output),
            "training_run_ids": list(all_run_ids),
            "training_row_count": int(all_features.shape[0]),
            "reload_max_abs_prediction_difference": reload_max_abs_difference,
        },
        "commands": {
            "training": shlex.join([sys.executable, *sys.argv]),
        },
        "code_version": _git_version(),
        "limitations": [
            "theta*_meas is command_echo_no_encoder, not independent encoder data",
            "error_z is angle-derived and diagnostic, not external 3D ground truth",
        ],
    }
    _write_json(args.report_output, report)

    print(f"runs={len(all_run_ids)} rows={all_features.shape[0]}")
    print(f"alpha_grid={list(alpha_grid)}")
    print(f"selected_alpha={selected_alpha:g}")
    print(
        "selected_mean_xy_rmse="
        f"{selected['aggregate']['mean_xy_rmse']:.6f}"
    )
    print(f"model_output={args.model_output}")
    print(f"report_output={args.report_output}")
    return 0


def _discover_runs(
    input_dir: Path,
    input_pattern: str,
) -> dict[str, dict[str, Any]]:
    run_data: dict[str, dict[str, Any]] = {}
    for csv_path in sorted(input_dir.glob(input_pattern)):
        run_id = csv_path.stem.removeprefix("merged_")
        match = RUN_ID_PATTERN.fullmatch(run_id)
        if match is None:
            raise ValueError(f"unexpected Run 01-main file name: {csv_path}")
        dataset = load_virtual_sensor_dataset(csv_path)
        features = np.asarray(dataset.feature_matrix(), dtype=np.float64)
        targets = np.asarray(dataset.target_matrix(), dtype=np.float64)
        times = np.asarray([row["time"] for row in dataset.rows], dtype=np.float64)
        if dataset.row_count == 0:
            raise ValueError(f"dataset is empty: {csv_path}")
        if not np.isfinite(features).all() or not np.isfinite(targets).all():
            raise ValueError(f"dataset contains non-finite values: {csv_path}")
        if np.any(np.diff(times) <= 0.0):
            raise ValueError(f"timestamps are not strictly increasing: {csv_path}")
        run_data[run_id] = {
            "path": csv_path,
            "trajectory": match.group("trajectory"),
            "repetition": match.group("repetition"),
            "features": features,
            "targets": targets,
        }
    if not run_data:
        raise ValueError(
            f"no datasets matched {input_dir / input_pattern}"
        )
    return run_data


def _validate_run_set(run_data: dict[str, dict[str, Any]]) -> None:
    by_trajectory: dict[str, set[str]] = defaultdict(set)
    for run in run_data.values():
        by_trajectory[run["trajectory"]].add(run["repetition"])
    expected_repetitions = {"r01", "r02", "r03"}
    incomplete = {
        trajectory: sorted(repetitions)
        for trajectory, repetitions in by_trajectory.items()
        if repetitions != expected_repetitions
    }
    if len(run_data) != 15 or len(by_trajectory) != 5 or incomplete:
        raise ValueError(
            "expected five trajectories with r01/r02/r03 (15 runs); "
            f"found runs={len(run_data)}, trajectories={len(by_trajectory)}, "
            f"incomplete={incomplete}"
        )


def _cross_validate_alpha(
    run_data: dict[str, dict[str, Any]],
    *,
    alpha: float,
) -> dict[str, Any]:
    fold_results: list[dict[str, Any]] = []
    for validation_repetition in ("r01", "r02", "r03"):
        validation_run_ids = tuple(
            sorted(
                run_id
                for run_id, run in run_data.items()
                if run["repetition"] == validation_repetition
            )
        )
        training_run_ids = tuple(
            sorted(set(run_data) - set(validation_run_ids))
        )
        if set(validation_run_ids) & set(training_run_ids):
            raise AssertionError("validation and training run IDs overlap")

        training_features = np.concatenate(
            [run_data[run_id]["features"] for run_id in training_run_ids],
            axis=0,
        )
        training_targets = np.concatenate(
            [run_data[run_id]["targets"] for run_id in training_run_ids],
            axis=0,
        )
        model = fit_ridge(
            training_features,
            training_targets,
            alpha=alpha,
            feature_names=FEATURE_COLUMNS,
            target_names=TARGET_COLUMNS,
            training_run_ids=training_run_ids,
        )

        run_metrics = []
        for run_id in validation_run_ids:
            run = run_data[run_id]
            predictions = model.predict(run["features"])
            run_metrics.append(
                {
                    "run_id": run_id,
                    "trajectory": run["trajectory"],
                    "repetition": run["repetition"],
                    "row_count": int(run["features"].shape[0]),
                    "metrics": compute_metrics(run["targets"], predictions),
                }
            )
        trajectory_metrics = _aggregate_by_trajectory(run_metrics)
        fold_results.append(
            {
                "validation_repetition": validation_repetition,
                "training_run_ids": list(training_run_ids),
                "validation_run_ids": list(validation_run_ids),
                "training_row_count": int(training_features.shape[0]),
                "validation_row_count": sum(
                    result["row_count"] for result in run_metrics
                ),
                "run_metrics": run_metrics,
                "trajectory_metrics": trajectory_metrics,
                "aggregate": _mean_metric_records(
                    [result["metrics"] for result in run_metrics]
                ),
            }
        )

    all_run_metrics = [
        run_result["metrics"]
        for fold_result in fold_results
        for run_result in fold_result["run_metrics"]
    ]
    return {
        "alpha": alpha,
        "folds": fold_results,
        "aggregate": _mean_metric_records(all_run_metrics),
    }


def compute_metrics(
    targets: npt.ArrayLike,
    predictions: npt.ArrayLike,
) -> dict[str, float]:
    target_array = np.asarray(targets, dtype=np.float64)
    prediction_array = np.asarray(predictions, dtype=np.float64)
    if target_array.shape != prediction_array.shape:
        raise ValueError("target and prediction shapes do not match")
    if target_array.ndim != 2 or target_array.shape[1] != 3:
        raise ValueError("metrics require an N x 3 target matrix")

    residual = prediction_array - target_array
    absolute = np.abs(residual)
    xy_euclidean = np.hypot(residual[:, 0], residual[:, 1])
    return {
        "x_rmse": float(np.sqrt(np.mean(residual[:, 0] ** 2))),
        "y_rmse": float(np.sqrt(np.mean(residual[:, 1] ** 2))),
        "xy_rmse": float(np.sqrt(np.mean(xy_euclidean**2))),
        "x_mae": float(np.mean(absolute[:, 0])),
        "y_mae": float(np.mean(absolute[:, 1])),
        "xy_mae": float(np.mean(xy_euclidean)),
        "xy_max_error": float(np.max(xy_euclidean)),
        "z_rmse": float(np.sqrt(np.mean(residual[:, 2] ** 2))),
        "z_mae": float(np.mean(absolute[:, 2])),
    }


def _aggregate_by_trajectory(
    run_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    for result in run_metrics:
        grouped[result["trajectory"]].append(result["metrics"])
    return [
        {
            "trajectory": trajectory,
            "run_count": len(metrics),
            "metrics": _mean_metric_records(metrics),
        }
        for trajectory, metrics in sorted(grouped.items())
    ]


def _mean_metric_records(
    records: list[dict[str, float]],
) -> dict[str, float]:
    if not records:
        raise ValueError("cannot aggregate an empty metric list")
    return {
        f"mean_{metric_name}": float(
            np.mean([record[metric_name] for record in records])
        )
        for metric_name in records[0]
    }


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
        description="Train and cross-validate the Run 01-main Ridge baseline."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/processed"),
    )
    parser.add_argument(
        "--input-pattern",
        default="merged_2026-06-06_run01_main_*.csv",
    )
    parser.add_argument(
        "--alpha",
        action="append",
        type=float,
        help="Ridge alpha candidate. May be passed more than once.",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=Path(
            "virtual_sensor/models/ridge_run01_main_2026-06-06.npz"
        ),
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path(
            "experiments/results/ridge_run01_main_cv_2026-06-06.json"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
