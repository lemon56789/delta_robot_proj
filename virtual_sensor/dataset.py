from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path


FEATURE_COLUMNS: tuple[str, ...] = (
    "theta1_cmd",
    "theta2_cmd",
    "theta3_cmd",
    "theta1_meas",
    "theta2_meas",
    "theta3_meas",
    "sim_x",
    "sim_y",
    "sim_z",
)

TARGET_COLUMNS: tuple[str, ...] = (
    "error_x",
    "error_y",
    "error_z",
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "time",
    "target_x",
    "target_y",
    "target_z",
    *FEATURE_COLUMNS,
    *TARGET_COLUMNS,
)


@dataclass(frozen=True)
class VirtualSensorDataset:
    rows: list[dict[str, float]]
    feature_columns: tuple[str, ...]
    target_columns: tuple[str, ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def feature_count(self) -> int:
        return len(self.feature_columns)

    @property
    def target_count(self) -> int:
        return len(self.target_columns)

    def feature_matrix(self) -> list[list[float]]:
        return [
            [row[column_name] for column_name in self.feature_columns]
            for row in self.rows
        ]

    def target_matrix(self) -> list[list[float]]:
        return [
            [row[column_name] for column_name in self.target_columns]
            for row in self.rows
        ]


@dataclass(frozen=True)
class ColumnSummary:
    min_value: float
    max_value: float
    mean_value: float


def load_virtual_sensor_dataset(
    csv_path: str | Path,
    *,
    feature_columns: tuple[str, ...] = FEATURE_COLUMNS,
    target_columns: tuple[str, ...] = TARGET_COLUMNS,
) -> VirtualSensorDataset:
    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("dataset header is missing")
        _validate_columns(
            available_columns=tuple(reader.fieldnames),
            required_columns=("time", "target_x", "target_y", "target_z", *feature_columns, *target_columns),
        )

        parsed_rows: list[dict[str, float]] = []
        for row_index, raw_row in enumerate(reader, start=1):
            parsed_rows.append(_parse_row(raw_row, reader.fieldnames, row_index))

    return VirtualSensorDataset(
        rows=parsed_rows,
        feature_columns=feature_columns,
        target_columns=target_columns,
    )


def summarize_dataset(dataset: VirtualSensorDataset) -> dict[str, ColumnSummary]:
    summaries: dict[str, ColumnSummary] = {}
    if dataset.row_count == 0:
        return summaries

    for column_name in ("time", "target_x", "target_y", "target_z", *dataset.feature_columns, *dataset.target_columns):
        values = [row[column_name] for row in dataset.rows]
        summaries[column_name] = ColumnSummary(
            min_value=min(values),
            max_value=max(values),
            mean_value=sum(values) / len(values),
        )
    return summaries


def dataset_has_nan(dataset: VirtualSensorDataset) -> bool:
    for row in dataset.rows:
        for value in row.values():
            if math.isnan(value):
                return True
    return False


def _validate_columns(
    *,
    available_columns: tuple[str, ...],
    required_columns: tuple[str, ...],
) -> None:
    missing_columns = [column_name for column_name in required_columns if column_name not in available_columns]
    if missing_columns:
        raise ValueError(f"dataset is missing required columns: {missing_columns}")


def _parse_row(
    raw_row: dict[str, str | None],
    column_order: list[str] | tuple[str, ...],
    row_index: int,
) -> dict[str, float]:
    parsed_row: dict[str, float] = {}
    for column_name in column_order:
        raw_value = raw_row.get(column_name)
        if raw_value is None or raw_value == "":
            raise ValueError(f"row {row_index} has empty value for column '{column_name}'")
        try:
            parsed_row[column_name] = float(raw_value)
        except ValueError as exc:
            raise ValueError(
                f"row {row_index} column '{column_name}' is not a float: {raw_value}"
            ) from exc
    return parsed_row
