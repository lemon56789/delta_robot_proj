from __future__ import annotations

import argparse
from collections import defaultdict
import csv
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
from virtual_sensor.train_ridge import compute_metrics


FloatArray = npt.NDArray[np.float64]
REPETITION_PATTERN = re.compile(r"_(r0[1-3])$")
AGE_WINDOWS: tuple[tuple[str, float, float | None], ...] = (
    ("0_0.5s", 0.0, 500.0),
    ("0.5_1.5s", 500.0, 1500.0),
    ("1.5s_plus", 1500.0, None),
)


def main() -> int:
    args = _parse_args()
    selected_alpha = _selected_alpha(args.cv_report)
    main_runs = _load_runs(
        processed_dir=args.processed_dir,
        real_raw_dir=args.real_raw_dir,
        pattern=args.main_pattern,
    )
    holdout_runs = _load_runs(
        processed_dir=args.processed_dir,
        real_raw_dir=args.real_raw_dir,
        pattern=args.holdout_pattern,
    )
    if len(main_runs) != 15:
        raise ValueError(f"expected 15 main runs, found {len(main_runs)}")
    if len(holdout_runs) != 4:
        raise ValueError(
            f"expected four complete holdout runs, found {len(holdout_runs)}"
        )

    main_predictions = _main_oof_predictions(main_runs, selected_alpha)
    final_model = RidgeModel.load(args.model)
    if set(holdout_runs) & set(final_model.training_run_ids):
        raise ValueError("holdout run IDs overlap final model training IDs")
    holdout_predictions = {
        run_id: final_model.predict(run["features"])
        for run_id, run in holdout_runs.items()
    }

    main_analysis = _analyze_split(
        runs=main_runs,
        predictions=main_predictions,
        split_name="main_oof",
    )
    holdout_analysis = _analyze_split(
        runs=holdout_runs,
        predictions=holdout_predictions,
        split_name="holdout_frozen",
    )
    diagnosis = _diagnose_holdout(holdout_analysis)

    report = {
        "report_type": "ridge_run01_phase_analysis",
        "selected_alpha": selected_alpha,
        "model_path": str(args.model),
        "feature_columns": list(FEATURE_COLUMNS),
        "target_columns": list(TARGET_COLUMNS),
        "age_windows_ms": [
            {"name": name, "start": start, "end": end}
            for name, start, end in AGE_WINDOWS
        ],
        "prediction_policy": {
            "main": "out_of_fold_by_repetition_r01_r02_r03",
            "holdout": "frozen_final_model",
            "holdout_isolation_confirmed": not bool(
                set(holdout_runs) & set(final_model.training_run_ids)
            ),
            "final_model_training_run_ids": list(
                final_model.training_run_ids
            ),
        },
        "main": main_analysis,
        "holdout": holdout_analysis,
        "diagnosis": diagnosis,
        "commands": {
            "analysis": shlex.join([sys.executable, *sys.argv]),
        },
        "code_version": _git_version(),
        "limitations": [
            "phase labels are commanded intervals, not measured settling",
            "vision/main alignment can shift apparent transition timing",
            "theta*_meas is command_echo_no_encoder",
            "holdout results are diagnostic and were not used for fitting",
        ],
    }
    _write_json(args.json_output, report)
    _write_markdown(args.markdown_output, report)

    holdout_summary = holdout_analysis["overall"]
    print(f"main_runs={len(main_runs)} holdout_runs={len(holdout_runs)}")
    print(
        "holdout_model_xy_rmse="
        f"{holdout_summary['model_metrics']['xy_rmse']:.6f}"
    )
    print(
        "holdout_improvement_percent="
        f"{holdout_summary['xy_rmse_improvement_percent']:.6f}"
    )
    for item in diagnosis:
        print(
            f"diagnosis={item['trajectory']}:{item['classification']}"
        )
    print(f"json_output={args.json_output}")
    print(f"markdown_output={args.markdown_output}")
    return 0


def _load_runs(
    *,
    processed_dir: Path,
    real_raw_dir: Path,
    pattern: str,
) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for merged_path in sorted(processed_dir.glob(pattern)):
        run_id = merged_path.stem.removeprefix("merged_")
        raw_path = real_raw_dir / f"main_{run_id}.csv"
        dataset = load_virtual_sensor_dataset(merged_path)
        features = np.asarray(dataset.feature_matrix(), dtype=np.float64)
        targets = np.asarray(dataset.target_matrix(), dtype=np.float64)
        times = np.asarray(
            [row["time"] for row in dataset.rows],
            dtype=np.float64,
        )
        phase_records = _phase_records(raw_path)
        phases: list[str] = []
        phase_ages_ms: list[float] = []
        phase_remaining_ms: list[float] = []
        targets_xyz: list[list[float]] = []
        for row, time_ms in zip(dataset.rows, times, strict=True):
            key = _time_key(time_ms)
            if key not in phase_records:
                raise ValueError(
                    f"merged timestamp {time_ms} not found in {raw_path}"
                )
            record = phase_records[key]
            phases.append(record["phase"])
            phase_ages_ms.append(time_ms - record["phase_start_ms"])
            phase_remaining_ms.append(record["phase_end_ms"] - time_ms)
            targets_xyz.append(
                [row["target_x"], row["target_y"], row["target_z"]]
            )
        if len(phases) != dataset.row_count:
            raise AssertionError("phase row count mismatch")
        runs[run_id] = {
            "merged_path": merged_path,
            "raw_path": raw_path,
            "trajectory": _trajectory_name(run_id),
            "repetition": _repetition(run_id),
            "features": features,
            "targets": targets,
            "times": times,
            "phases": np.asarray(phases),
            "phase_categories": np.asarray(
                [_phase_category(phase) for phase in phases]
            ),
            "phase_ages_ms": np.asarray(
                phase_ages_ms,
                dtype=np.float64,
            ),
            "phase_remaining_ms": np.asarray(
                phase_remaining_ms,
                dtype=np.float64,
            ),
            "target_xyz": np.asarray(targets_xyz, dtype=np.float64),
        }
    return runs


def _phase_records(raw_path: Path) -> dict[str, dict[str, Any]]:
    with raw_path.open("r", encoding="utf-8", newline="") as raw_file:
        rows = list(csv.DictReader(raw_file))
    records: dict[str, dict[str, Any]] = {}
    segment_start = 0
    for index in range(1, len(rows) + 1):
        phase_changed = (
            index == len(rows)
            or rows[index]["phase"] != rows[segment_start]["phase"]
        )
        if not phase_changed:
            continue
        phase_start_ms = float(rows[segment_start]["time"])
        phase_end_ms = float(rows[index - 1]["time"])
        for row in rows[segment_start:index]:
            time_ms = float(row["time"])
            records[_time_key(time_ms)] = {
                "phase": row["phase"],
                "phase_start_ms": phase_start_ms,
                "phase_end_ms": phase_end_ms,
            }
        segment_start = index
    return records


def _main_oof_predictions(
    runs: dict[str, dict[str, Any]],
    alpha: float,
) -> dict[str, FloatArray]:
    predictions: dict[str, FloatArray] = {}
    for validation_repetition in ("r01", "r02", "r03"):
        validation_ids = sorted(
            run_id
            for run_id, run in runs.items()
            if run["repetition"] == validation_repetition
        )
        training_ids = sorted(set(runs) - set(validation_ids))
        if set(training_ids) & set(validation_ids):
            raise AssertionError("OOF training and validation IDs overlap")
        model = fit_ridge(
            np.concatenate(
                [runs[run_id]["features"] for run_id in training_ids],
                axis=0,
            ),
            np.concatenate(
                [runs[run_id]["targets"] for run_id in training_ids],
                axis=0,
            ),
            alpha=alpha,
            feature_names=FEATURE_COLUMNS,
            target_names=TARGET_COLUMNS,
            training_run_ids=tuple(training_ids),
        )
        for run_id in validation_ids:
            if run_id in model.training_run_ids:
                raise AssertionError("OOF validation run was used for fitting")
            predictions[run_id] = model.predict(runs[run_id]["features"])
    if set(predictions) != set(runs):
        raise AssertionError("OOF predictions do not cover every main run")
    return predictions


def _analyze_split(
    *,
    runs: dict[str, dict[str, Any]],
    predictions: dict[str, FloatArray],
    split_name: str,
) -> dict[str, Any]:
    row_records: list[dict[str, Any]] = []
    run_results: list[dict[str, Any]] = []
    for run_id in sorted(runs):
        run = runs[run_id]
        prediction = predictions[run_id]
        if prediction.shape != run["targets"].shape:
            raise ValueError(f"prediction shape mismatch for {run_id}")
        indices = np.arange(run["targets"].shape[0])
        result = _group_result(
            run["targets"],
            prediction,
            indices,
        )
        result.update(
            {
                "run_id": run_id,
                "trajectory": run["trajectory"],
                "row_count": int(len(indices)),
            }
        )
        run_results.append(result)
        row_records.extend(_row_records(run_id, run, prediction))

    all_targets = np.concatenate(
        [runs[run_id]["targets"] for run_id in sorted(runs)],
        axis=0,
    )
    all_predictions = np.concatenate(
        [predictions[run_id] for run_id in sorted(runs)],
        axis=0,
    )
    all_indices = np.arange(all_targets.shape[0])
    phase_categories = np.concatenate(
        [runs[run_id]["phase_categories"] for run_id in sorted(runs)]
    )
    phase_ages = np.concatenate(
        [runs[run_id]["phase_ages_ms"] for run_id in sorted(runs)]
    )
    phase_remaining = np.concatenate(
        [runs[run_id]["phase_remaining_ms"] for run_id in sorted(runs)]
    )
    trajectories = np.concatenate(
        [
            np.full(
                runs[run_id]["targets"].shape[0],
                runs[run_id]["trajectory"],
            )
            for run_id in sorted(runs)
        ]
    )

    by_phase = _grouped_results(
        labels=phase_categories,
        targets=all_targets,
        predictions=all_predictions,
    )
    by_age = _age_results(
        phase_ages=phase_ages,
        targets=all_targets,
        predictions=all_predictions,
    )
    by_trajectory = []
    for trajectory in sorted(set(trajectories)):
        trajectory_indices = np.flatnonzero(trajectories == trajectory)
        item = _group_result(
            all_targets,
            all_predictions,
            trajectory_indices,
        )
        item["trajectory"] = trajectory
        item["phase_age_windows"] = _age_results(
            phase_ages=phase_ages[trajectory_indices],
            targets=all_targets[trajectory_indices],
            predictions=all_predictions[trajectory_indices],
        )
        item["phase_edge_windows"] = _edge_results(
            phase_ages=phase_ages[trajectory_indices],
            phase_remaining=phase_remaining[trajectory_indices],
            targets=all_targets[trajectory_indices],
            predictions=all_predictions[trajectory_indices],
        )
        item["phase_categories"] = _grouped_results(
            labels=phase_categories[trajectory_indices],
            targets=all_targets[trajectory_indices],
            predictions=all_predictions[trajectory_indices],
        )
        by_trajectory.append(item)

    return {
        "split": split_name,
        "run_count": len(runs),
        "row_count": int(all_targets.shape[0]),
        "overall": _group_result(
            all_targets,
            all_predictions,
            all_indices,
        ),
        "runs": run_results,
        "phase_categories": by_phase,
        "phase_age_windows": by_age,
        "phase_edge_windows": _edge_results(
            phase_ages=phase_ages,
            phase_remaining=phase_remaining,
            targets=all_targets,
            predictions=all_predictions,
        ),
        "trajectories": by_trajectory,
        "worst_model_rows": sorted(
            row_records,
            key=lambda row: row["model_xy_residual"],
            reverse=True,
        )[:20],
        "worst_harmful_rows": sorted(
            row_records,
            key=lambda row: row["residual_change"],
            reverse=True,
        )[:20],
    }


def _grouped_results(
    *,
    labels: npt.NDArray[np.str_],
    targets: FloatArray,
    predictions: FloatArray,
) -> list[dict[str, Any]]:
    results = []
    for label in sorted(set(labels)):
        indices = np.flatnonzero(labels == label)
        item = _group_result(targets, predictions, indices)
        item["phase_category"] = str(label)
        results.append(item)
    return results


def _age_results(
    *,
    phase_ages: FloatArray,
    targets: FloatArray,
    predictions: FloatArray,
) -> list[dict[str, Any]]:
    results = []
    covered_rows = 0
    for name, start_ms, end_ms in AGE_WINDOWS:
        mask = phase_ages >= start_ms
        if end_ms is not None:
            mask &= phase_ages < end_ms
        indices = np.flatnonzero(mask)
        covered_rows += len(indices)
        item = _group_result(targets, predictions, indices)
        item["window"] = name
        results.append(item)
    if covered_rows != len(phase_ages):
        raise AssertionError("phase-age windows do not cover every row")
    return results


def _edge_results(
    *,
    phase_ages: FloatArray,
    phase_remaining: FloatArray,
    targets: FloatArray,
    predictions: FloatArray,
) -> list[dict[str, Any]]:
    labels = np.full(len(phase_ages), "interior", dtype="<U16")
    labels[phase_remaining < 500.0] = "final_0.5s"
    labels[phase_ages < 500.0] = "first_0.5s"
    results = []
    covered_rows = 0
    for label in ("first_0.5s", "interior", "final_0.5s"):
        indices = np.flatnonzero(labels == label)
        covered_rows += len(indices)
        item = _group_result(targets, predictions, indices)
        item["window"] = label
        results.append(item)
    if covered_rows != len(phase_ages):
        raise AssertionError("phase-edge windows do not cover every row")
    return results


def _group_result(
    targets: FloatArray,
    predictions: FloatArray,
    indices: npt.NDArray[np.int64],
) -> dict[str, Any]:
    if len(indices) == 0:
        return {
            "row_count": 0,
            "baseline_metrics": None,
            "model_metrics": None,
            "xy_rmse_improvement_percent": None,
            "harmful": None,
        }
    selected_targets = targets[indices]
    selected_predictions = predictions[indices]
    baseline = compute_metrics(
        selected_targets,
        np.zeros_like(selected_targets),
    )
    model = compute_metrics(selected_targets, selected_predictions)
    return {
        "row_count": int(len(indices)),
        "baseline_metrics": baseline,
        "model_metrics": model,
        "xy_rmse_improvement_percent": _improvement_percent(
            baseline["xy_rmse"],
            model["xy_rmse"],
        ),
        "harmful": model["xy_rmse"] > baseline["xy_rmse"],
    }


def _row_records(
    run_id: str,
    run: dict[str, Any],
    predictions: FloatArray,
) -> list[dict[str, Any]]:
    records = []
    for index in range(run["targets"].shape[0]):
        target = run["targets"][index]
        prediction = predictions[index]
        baseline_xy = float(np.hypot(target[0], target[1]))
        model_xy = float(
            np.hypot(
                prediction[0] - target[0],
                prediction[1] - target[1],
            )
        )
        records.append(
            {
                "run_id": run_id,
                "trajectory": run["trajectory"],
                "time_ms": float(run["times"][index]),
                "phase": str(run["phases"][index]),
                "phase_category": str(run["phase_categories"][index]),
                "phase_age_ms": float(run["phase_ages_ms"][index]),
                "phase_remaining_ms": float(
                    run["phase_remaining_ms"][index]
                ),
                "target_xyz": run["target_xyz"][index].tolist(),
                "true_error_xyz": target.tolist(),
                "prediction_xyz": prediction.tolist(),
                "baseline_xy_residual": baseline_xy,
                "model_xy_residual": model_xy,
                "residual_change": model_xy - baseline_xy,
            }
        )
    return records


def _diagnose_holdout(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    diagnosis = []
    for trajectory in analysis["trajectories"]:
        windows = {
            item["window"]: item
            for item in trajectory["phase_age_windows"]
        }
        early = windows["0_0.5s"]
        settled = windows["1.5s_plus"]
        edges = {
            item["window"]: item
            for item in trajectory["phase_edge_windows"]
        }
        interior = edges["interior"]
        final = edges["final_0.5s"]
        overall_improvement = trajectory["xy_rmse_improvement_percent"]
        harmful_phases = [
            item["phase_category"]
            for item in trajectory["phase_categories"]
            if item["harmful"]
        ]
        early_rmse = _metric(early, "model_metrics", "xy_rmse")
        settled_rmse = _metric(settled, "model_metrics", "xy_rmse")
        interior_rmse = _metric(interior, "model_metrics", "xy_rmse")
        final_rmse = _metric(final, "model_metrics", "xy_rmse")
        if settled["row_count"] == 0:
            classification = "insufficient_settled_rows"
        elif (
            final["row_count"] > 0
            and interior["row_count"] > 0
            and final_rmse > 1.5 * interior_rmse
        ):
            classification = "phase_end_alignment_sensitive"
        elif early_rmse > 1.5 * settled_rmse:
            classification = "transition_sensitive"
        elif overall_improvement < 5.0 or harmful_phases:
            classification = "persistent_model_limitation"
        else:
            classification = "mixed_or_moderate_improvement"
        diagnosis.append(
            {
                "trajectory": trajectory["trajectory"],
                "classification": classification,
                "overall_improvement_percent": overall_improvement,
                "early_model_xy_rmse": early_rmse,
                "settled_model_xy_rmse": settled_rmse,
                "interior_model_xy_rmse": interior_rmse,
                "final_0.5s_model_xy_rmse": final_rmse,
                "harmful_phase_categories": harmful_phases,
            }
        )
    return diagnosis


def _metric(
    result: dict[str, Any],
    group: str,
    metric: str,
) -> float:
    metrics = result[group]
    if metrics is None:
        return 0.0
    return float(metrics[metric])


def _phase_category(phase: str) -> str:
    if phase.startswith("home_"):
        return "home"
    if phase == "static_center_hold" or phase == "center":
        return "center"
    if phase.startswith("circle_"):
        return "circle_motion"
    if phase.startswith("q1_"):
        return "square_q1_x_plus_y_plus"
    if phase.startswith("q2_"):
        return "square_q2_x_minus_y_plus"
    if phase.startswith("q3_"):
        return "square_q3_x_minus_y_minus"
    if phase.startswith("q4_"):
        return "square_q4_x_plus_y_minus"
    return phase


def _trajectory_name(run_id: str) -> str:
    marker = "_run01_main_" if "_run01_main_" in run_id else "_run01_holdout_"
    suffix = run_id.split(marker, 1)[1]
    return REPETITION_PATTERN.sub("", suffix)


def _repetition(run_id: str) -> str:
    match = REPETITION_PATTERN.search(run_id)
    if match is None:
        raise ValueError(f"run ID has no repetition suffix: {run_id}")
    return match.group(1)


def _selected_alpha(report_path: Path) -> float:
    with report_path.open("r", encoding="utf-8") as report_file:
        report = json.load(report_file)
    return float(report["selected_alpha"])


def _improvement_percent(baseline_value: float, model_value: float) -> float:
    if baseline_value == 0.0:
        return 0.0 if model_value == 0.0 else float("-inf")
    return 100.0 * (baseline_value - model_value) / baseline_value


def _time_key(time_ms: float) -> str:
    return f"{time_ms:.9f}".rstrip("0").rstrip(".")


def _write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output_file:
        json.dump(report, output_file, ensure_ascii=True, indent=2)
        output_file.write("\n")


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    holdout = report["holdout"]
    holdout_edges = {
        item["window"]: item
        for item in holdout["phase_edge_windows"]
    }
    interior = holdout_edges["interior"]
    final = holdout_edges["final_0.5s"]
    lines = [
        "# Ridge Run 01 Phase Error Analysis",
        "",
        "## Summary",
        (
            "- Holdout zero-prediction XY RMSE: "
            f"`{holdout['overall']['baseline_metrics']['xy_rmse']:.3f} mm`"
        ),
        (
            "- Holdout Ridge XY RMSE: "
            f"`{holdout['overall']['model_metrics']['xy_rmse']:.3f} mm`"
        ),
        (
            "- Holdout row-weighted improvement: "
            f"`{holdout['overall']['xy_rmse_improvement_percent']:.2f}%`"
        ),
        (
            "- Holdout interior XY RMSE: "
            f"`{interior['baseline_metrics']['xy_rmse']:.3f} -> "
            f"{interior['model_metrics']['xy_rmse']:.3f} mm` "
            f"(`{interior['xy_rmse_improvement_percent']:.2f}%`)"
        ),
        (
            "- Holdout final 0.5 s XY RMSE: "
            f"`{final['baseline_metrics']['xy_rmse']:.3f} -> "
            f"{final['model_metrics']['xy_rmse']:.3f} mm`"
        ),
        "",
        "## Trajectory Diagnosis",
        "",
        "| Trajectory | Improvement | Interior RMSE | Final 0.5 s RMSE | Diagnosis |",
        "|---|---:|---:|---:|---|",
    ]
    for item in report["diagnosis"]:
        lines.append(
            f"| {item['trajectory']} "
            f"| {item['overall_improvement_percent']:.2f}% "
            f"| {item['interior_model_xy_rmse']:.3f} mm "
            f"| {item['final_0.5s_model_xy_rmse']:.3f} mm "
            f"| {item['classification']} |"
        )
    lines.extend(
        [
            "",
            "## Worst Holdout Rows",
            "",
            "| Run | Phase | Age | Baseline | Ridge | Change |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in holdout["worst_model_rows"][:10]:
        lines.append(
            f"| {row['run_id']} | {row['phase']} "
            f"| {row['phase_age_ms']:.0f} ms "
            f"| {row['baseline_xy_residual']:.3f} mm "
            f"| {row['model_xy_residual']:.3f} mm "
            f"| {row['residual_change']:+.3f} mm |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Rule",
            "",
            "- `transition_sensitive`: early-window RMSE exceeds settled RMSE by 50%.",
            "- `phase_end_alignment_sensitive`: final 0.5 s RMSE exceeds interior by 50%.",
            "- `persistent_model_limitation`: improvement is below 5% or a phase is harmed.",
            "- Holdout findings remain diagnostic and are not used to tune the model.",
            "- Correct phase-boundary alignment before changing model capacity.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze frozen Ridge errors by command phase."
    )
    parser.add_argument(
        "--processed-dir",
        type=Path,
        default=Path("data/processed"),
    )
    parser.add_argument(
        "--real-raw-dir",
        type=Path,
        default=Path("data/real/raw"),
    )
    parser.add_argument(
        "--main-pattern",
        default="merged_2026-06-06_run01_main_*.csv",
    )
    parser.add_argument(
        "--holdout-pattern",
        default="merged_2026-06-06_run01_holdout_*.csv",
    )
    parser.add_argument(
        "--cv-report",
        type=Path,
        default=Path(
            "experiments/results/ridge_run01_main_cv_2026-06-06.json"
        ),
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(
            "virtual_sensor/models/ridge_run01_main_2026-06-06.npz"
        ),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path(
            "experiments/results/ridge_run01_phase_analysis_2026-06-06.json"
        ),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path(
            "experiments/results/ridge_run01_phase_analysis_2026-06-06.md"
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
