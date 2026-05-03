from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from virtual_sensor.dataset import (
    FEATURE_COLUMNS,
    TARGET_COLUMNS,
    dataset_has_nan,
    load_virtual_sensor_dataset,
    summarize_dataset,
)


def main() -> int:
    args = _parse_args()
    dataset = load_virtual_sensor_dataset(args.csv_path)
    summaries = summarize_dataset(dataset)

    print(f"csv_path={args.csv_path}")
    print(f"row_count={dataset.row_count}")
    print(f"feature_columns={list(dataset.feature_columns)}")
    print(f"target_columns={list(dataset.target_columns)}")
    print(f"feature_shape=({dataset.row_count}, {dataset.feature_count})")
    print(f"target_shape=({dataset.row_count}, {dataset.target_count})")
    print(f"has_nan={dataset_has_nan(dataset)}")
    for column_name in (*FEATURE_COLUMNS, *TARGET_COLUMNS):
        summary = summaries[column_name]
        print(
            f"{column_name}: "
            f"min={summary.min_value:.6f}, "
            f"max={summary.max_value:.6f}, "
            f"mean={summary.mean_value:.6f}"
        )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate fake pipeline CSV shape for virtual sensor input/output usage."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="data/fake_pipeline/fake_pipeline_sample_2026-05-04.csv",
        help="Path to the CSV dataset to validate.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
