from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual_sensor.dataset import load_virtual_sensor_dataset
from virtual_sensor.ridge_model import RidgeModel
from virtual_sensor.train_ridge import compute_metrics


HOLDOUT_RUN_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}_run01_holdout_(?P<trajectory>.+)_r01$"
)


def main() -> int:
    args = _parse_args()
    model = RidgeModel.load(args.model)
    holdout_paths = sorted(args.input_dir.glob(args.input_pattern))
    if len(holdout_paths) not in (4, 5):
        raise ValueError(
            "expected four complete holdouts, optionally plus one circle; "
            f"found {len(holdout_paths)} matching "
            f"{args.input_dir / args.input_pattern}"
        )

    results: list[dict[str, Any]] = []
    holdout_run_ids: list[str] = []
    for csv_path in holdout_paths:
        run_id = csv_path.stem.removeprefix("merged_")
        match = HOLDOUT_RUN_PATTERN.fullmatch(run_id)
        if match is None:
            raise ValueError(f"unexpected holdout file name: {csv_path}")
        if run_id in model.training_run_ids:
            raise ValueError(f"holdout run appears in model training IDs: {run_id}")
        dataset = load_virtual_sensor_dataset(
            csv_path,
            feature_columns=model.feature_names,
            target_columns=model.target_names,
        )
        features = np.asarray(dataset.feature_matrix(), dtype=np.float64)
        targets = np.asarray(dataset.target_matrix(), dtype=np.float64)
        predictions = model.predict(features)
        baseline_metrics = compute_metrics(targets, np.zeros_like(targets))
        model_metrics = compute_metrics(targets, predictions)
        is_partial = "circle_r40" in match.group("trajectory")
        results.append(
            {
                "run_id": run_id,
                "trajectory": match.group("trajectory"),
                "status": "partial_diagnostic" if is_partial else "complete",
                "row_count": dataset.row_count,
                "csv_path": str(csv_path),
                "baseline_zero_prediction_metrics": baseline_metrics,
                "model_metrics": model_metrics,
                "xy_rmse_improvement_percent": _improvement_percent(
                    baseline_metrics["xy_rmse"],
                    model_metrics["xy_rmse"],
                ),
            }
        )
        holdout_run_ids.append(run_id)

    complete_results = [
        result for result in results if result["status"] == "complete"
    ]
    partial_results = [
        result for result in results if result["status"] == "partial_diagnostic"
    ]
    if len(complete_results) != 4 or len(partial_results) not in (0, 1):
        raise ValueError(
            "holdout report requires four complete runs and at most one "
            "partial circle"
        )
    evaluation_status = (
        "final_with_partial_circle"
        if partial_results
        else "preliminary_complete_only"
    )
    complete_baseline_macro_average = _macro_average(
        complete_results,
        metric_key="baseline_zero_prediction_metrics",
    )
    complete_model_macro_average = _macro_average(
        complete_results,
        metric_key="model_metrics",
    )

    report = {
        "report_type": "ridge_run01_holdout",
        "evaluation_status": evaluation_status,
        "circle_evaluation_pending": not bool(partial_results),
        "model_path": str(args.model),
        "model_alpha": model.alpha,
        "model_training_run_ids": list(model.training_run_ids),
        "holdout_run_ids": holdout_run_ids,
        "holdout_isolation_confirmed": not bool(
            set(holdout_run_ids) & set(model.training_run_ids)
        ),
        "feature_columns": list(model.feature_names),
        "target_columns": list(model.target_names),
        "complete_runs": complete_results,
        "partial_diagnostic_runs": partial_results,
        "complete_baseline_macro_average": complete_baseline_macro_average,
        "complete_model_macro_average": complete_model_macro_average,
        "complete_xy_rmse_improvement_percent": _improvement_percent(
            complete_baseline_macro_average["mean_xy_rmse"],
            complete_model_macro_average["mean_xy_rmse"],
        ),
        "commands": {
            "evaluation": shlex.join([sys.executable, *sys.argv]),
        },
        "code_version": _git_version(),
        "limitations": [
            "theta*_meas is command_echo_no_encoder, not independent encoder data",
            "error_z is angle-derived and diagnostic, not external 3D ground truth",
        ],
    }
    if partial_results:
        report["limitations"].insert(
            0,
            "circle_r40_holdout_r01 has incomplete final circle/home vision coverage",
        )
    else:
        report["limitations"].insert(
            0,
            "circle holdout is pending and is not included in this preliminary report",
        )
    _write_json(args.report_output, report)
    print(f"evaluation_status={evaluation_status}")
    print(f"complete_holdouts={len(complete_results)}")
    print(f"partial_holdouts={len(partial_results)}")
    print(
        "complete_baseline_mean_xy_rmse="
        f"{complete_baseline_macro_average['mean_xy_rmse']:.6f}"
    )
    print(
        "complete_model_mean_xy_rmse="
        f"{complete_model_macro_average['mean_xy_rmse']:.6f}"
    )
    print(
        "complete_xy_rmse_improvement_percent="
        f"{report['complete_xy_rmse_improvement_percent']:.6f}"
    )
    print(f"report_output={args.report_output}")
    return 0


def _macro_average(
    results: list[dict[str, Any]],
    *,
    metric_key: str,
) -> dict[str, float]:
    if not results:
        raise ValueError("cannot aggregate an empty result list")
    metric_names = tuple(results[0][metric_key])
    return {
        f"mean_{metric_name}": float(
            np.mean(
                [result[metric_key][metric_name] for result in results]
            )
        )
        for metric_name in metric_names
    }


def _improvement_percent(baseline_value: float, model_value: float) -> float:
    if baseline_value == 0.0:
        return 0.0 if model_value == 0.0 else float("-inf")
    return 100.0 * (baseline_value - model_value) / baseline_value


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
        description="Evaluate a frozen Ridge model on Run 01-holdout data."
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
    parser.add_argument(
        "--input-pattern",
        default="merged_2026-06-06_run01_holdout_*.csv",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path(
            "experiments/results/ridge_run01_holdout_2026-06-06.json"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
