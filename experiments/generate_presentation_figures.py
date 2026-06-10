#!/usr/bin/env python3
"""Generate dependency-free Run 01/02 presentation figures as PNG and SVG."""

from __future__ import annotations

import json
import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "experiments" / "figures"
RUN01_JSON = ROOT / "experiments" / "results" / "ridge_run01_holdout_2026-06-06.json"
RUN02_JSON = ROOT / "experiments" / "results" / "run02_reanalysis_2026-06-07.json"

WIDTH = 1600
HEIGHT = 900

WHITE = "#FFFFFF"
INK = "#172033"
MUTED = "#5B6475"
GRID = "#D9DEE8"
OFF = "#7A8599"
ON = "#2374E1"
POSITIVE = "#159A68"
NEGATIVE = "#D94A4A"
ABSOLUTE = "#2374E1"
NORMALIZED = "#F59E0B"
HIGHLIGHT = "#EAF7F1"
PANEL = "#F7F9FC"


FONT: dict[str, tuple[str, ...]] = {
    " ": ("00000",) * 7,
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    ",": ("00000", "00000", "00000", "00000", "00110", "00110", "00100"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    ";": ("00000", "00110", "00110", "00000", "00110", "00110", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00100", "01000", "10110", "00110", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def rgb(color: str) -> tuple[int, int, int]:
    return tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]


@dataclass
class Raster:
    width: int = WIDTH
    height: int = HEIGHT

    def __post_init__(self) -> None:
        self.pixels = bytearray(rgb(WHITE) * (self.width * self.height))

    def rectangle(self, x: float, y: float, w: float, h: float, fill: str) -> None:
        x0 = max(0, int(round(x)))
        y0 = max(0, int(round(y)))
        x1 = min(self.width, int(round(x + w)))
        y1 = min(self.height, int(round(y + h)))
        color = bytes(rgb(fill))
        row = color * max(0, x1 - x0)
        for py in range(y0, y1):
            start = (py * self.width + x0) * 3
            self.pixels[start : start + len(row)] = row

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str, width: int = 1) -> None:
        dx = x2 - x1
        dy = y2 - y1
        steps = max(1, int(max(abs(dx), abs(dy))))
        for step in range(steps + 1):
            x = x1 + dx * step / steps
            y = y1 + dy * step / steps
            self.rectangle(x - width / 2, y - width / 2, width, width, color)

    def text_width(self, text: str, scale: int) -> int:
        return max(0, len(text) * 6 * scale - scale)

    def text(
        self,
        x: float,
        y: float,
        text: str,
        color: str = INK,
        scale: int = 4,
        anchor: str = "start",
    ) -> None:
        text = text.upper()
        width = self.text_width(text, scale)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        for index, char in enumerate(text):
            glyph = FONT.get(char, FONT[" "])
            gx = int(round(x + index * 6 * scale))
            gy = int(round(y))
            for row_index, row in enumerate(glyph):
                for col_index, bit in enumerate(row):
                    if bit == "1":
                        self.rectangle(
                            gx + col_index * scale,
                            gy + row_index * scale,
                            scale,
                            scale,
                            color,
                        )

    def save_png(self, path: Path) -> None:
        raw_rows = []
        stride = self.width * 3
        for y in range(self.height):
            start = y * stride
            raw_rows.append(b"\x00" + bytes(self.pixels[start : start + stride]))
        raw = b"".join(raw_rows)

        def chunk(kind: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b"")
        )
        path.write_bytes(png)


@dataclass
class SVG:
    width: int = WIDTH
    height: int = HEIGHT

    def __post_init__(self) -> None:
        self.items: list[str] = [
            f'<rect width="{self.width}" height="{self.height}" fill="{WHITE}"/>'
        ]

    @staticmethod
    def escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def rectangle(self, x: float, y: float, w: float, h: float, fill: str) -> None:
        self.items.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"/>'
        )

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str, width: int = 1) -> None:
        self.items.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width}"/>'
        )

    def text(
        self,
        x: float,
        y: float,
        text: str,
        color: str = INK,
        scale: int = 4,
        anchor: str = "start",
    ) -> None:
        size = scale * 8
        weight = 700 if scale >= 5 else 500
        self.items.append(
            f'<text x="{x:.2f}" y="{y + size * 0.82:.2f}" fill="{color}" '
            f'font-family="Arial, DejaVu Sans, sans-serif" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{self.escape(text)}</text>'
        )

    def save_svg(self, path: Path) -> None:
        content = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
            + "".join(self.items)
            + "</svg>\n"
        )
        path.write_text(content, encoding="utf-8")


Canvas = Raster | SVG


def title(canvas: Canvas, heading: str, subtitle: str) -> None:
    canvas.text(80, 48, heading, INK, 5)
    canvas.text(80, 106, subtitle, MUTED, 2)


def footer(canvas: Canvas, text: str) -> None:
    canvas.text(80, 858, text, MUTED, 2)


def legend(canvas: Canvas, entries: Sequence[tuple[str, str]], x: float, y: float) -> None:
    cursor = x
    for label, color in entries:
        canvas.rectangle(cursor, y + 4, 28, 20, color)
        canvas.text(cursor + 40, y, label, INK, 3)
        cursor += 40 + max(120, len(label) * 18)


def nice_ceiling(value: float) -> float:
    if value <= 0:
        return 1.0
    exponent = 10 ** math.floor(math.log10(value))
    normalized = value / exponent
    for step in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if normalized <= step:
            return step * exponent
    return 10 * exponent


def axis_y(
    canvas: Canvas,
    x0: float,
    y0: float,
    plot_h: float,
    minimum: float,
    maximum: float,
    ticks: int,
    formatter: Callable[[float], str],
) -> Callable[[float], float]:
    def map_y(value: float) -> float:
        return y0 + plot_h - (value - minimum) / (maximum - minimum) * plot_h

    for index in range(ticks + 1):
        value = minimum + (maximum - minimum) * index / ticks
        y = map_y(value)
        canvas.line(x0, y, 1510, y, GRID, 2 if abs(value) < 1e-9 else 1)
        canvas.text(x0 - 20, y - 12, formatter(value), MUTED, 2, "end")
    return map_y


def grouped_bar_chart(
    canvas: Canvas,
    heading: str,
    subtitle: str,
    categories: Sequence[str],
    series: Sequence[tuple[str, str, Sequence[float]]],
    y_label: str,
    minimum: float = 0.0,
    maximum: float | None = None,
    percent: bool = False,
    highlight_index: int | None = None,
) -> None:
    title(canvas, heading, subtitle)
    legend(canvas, [(name, color) for name, color, _ in series], 1010, 148)
    x0, y0, plot_w, plot_h = 150.0, 220.0, 1360.0, 500.0
    all_values = [value for _, _, values in series for value in values]
    if maximum is None:
        maximum = nice_ceiling(max(all_values) * 1.18)
    if highlight_index is not None:
        group_w = plot_w / len(categories)
        canvas.rectangle(x0 + group_w * highlight_index + 8, y0, group_w - 16, plot_h, HIGHLIGHT)
    map_y = axis_y(
        canvas,
        x0,
        y0,
        plot_h,
        minimum,
        maximum,
        5,
        lambda value: f"{value:.0f}%" if percent else f"{value:.1f}",
    )
    canvas.text(x0, 166, y_label, MUTED, 2)
    group_w = plot_w / len(categories)
    bar_w = min(105.0, group_w * 0.24)
    gap = 16.0
    series_span = len(series) * bar_w + (len(series) - 1) * gap
    zero_y = map_y(0.0)
    canvas.line(x0, zero_y, x0 + plot_w, zero_y, INK, 3)
    for category_index, category in enumerate(categories):
        center = x0 + group_w * (category_index + 0.5)
        start = center - series_span / 2
        for series_index, (_, color, values) in enumerate(series):
            value = values[category_index]
            x = start + series_index * (bar_w + gap)
            value_y = map_y(value)
            top = min(value_y, zero_y)
            height = max(2.0, abs(zero_y - value_y))
            canvas.rectangle(x, top, bar_w, height, color)
            label = f"{value:+.1f}%" if percent else f"{value:.2f}"
            label_y = top - 36 if value >= 0 else top + height + 12
            canvas.text(x + bar_w / 2, label_y, label, color, 2 if percent else 3, "middle")
        canvas.text(center, y0 + plot_h + 38, category, INK, 3, "middle")
    footer(canvas, "SOURCE: EXISTING RUN ARTIFACTS ONLY | NO ADDITIONAL HARDWARE TEST")


def signed_bar_chart(
    canvas: Canvas,
    heading: str,
    subtitle: str,
    categories: Sequence[str],
    values: Sequence[float],
    y_label: str,
    minimum: float,
    maximum: float,
    footer_text: str = "POSITIVE = LOWER RMSE WITH CORRECTION ON",
) -> None:
    title(canvas, heading, subtitle)
    x0, y0, plot_w, plot_h = 150.0, 220.0, 1360.0, 500.0
    map_y = axis_y(canvas, x0, y0, plot_h, minimum, maximum, 6, lambda value: f"{value:.0f}%")
    zero_y = map_y(0)
    canvas.line(x0, zero_y, x0 + plot_w, zero_y, INK, 4)
    canvas.text(x0, 166, y_label, MUTED, 2)
    group_w = plot_w / len(categories)
    bar_w = 150.0
    for index, (category, value) in enumerate(zip(categories, values)):
        center = x0 + group_w * (index + 0.5)
        value_y = map_y(value)
        color = POSITIVE if value >= 0 else NEGATIVE
        top = min(value_y, zero_y)
        height = max(2.0, abs(value_y - zero_y))
        canvas.rectangle(center - bar_w / 2, top, bar_w, height, color)
        label_y = top - 38 if value >= 0 else top + height + 14
        canvas.text(center, label_y, f"{value:+.1f}%", color, 4, "middle")
        canvas.text(center, y0 + plot_h + 38, category, INK, 3, "middle")
    legend(canvas, [("IMPROVED", POSITIVE), ("WORSENED", NEGATIVE)], 1030, 148)
    footer(canvas, footer_text)


def circle_decomposition(canvas: Canvas, circle: dict[str, dict[str, float]]) -> None:
    title(
        canvas,
        "RUN 02 CIRCLE ERROR DECOMPOSITION",
        "RADIAL RMSE DECREASED, WHILE TANGENTIAL ERROR AND PHASE LAG INCREASED",
    )
    off = circle["off"]
    on = circle["on"]
    left_x, panel_y, panel_w, panel_h = 80.0, 190.0, 900.0, 590.0
    right_x = 1020.0
    canvas.rectangle(left_x, panel_y, panel_w, panel_h, PANEL)
    canvas.rectangle(right_x, panel_y, 500.0, panel_h, PANEL)
    canvas.text(left_x + 35, panel_y + 30, "ERROR RMSE [MM]", INK, 3)
    canvas.text(right_x + 35, panel_y + 30, "PHASE LAG [MS]", INK, 3)
    legend(canvas, [("OFF", OFF), ("ON", ON)], left_x + 510, panel_y + 25)

    base_y = panel_y + 430
    max_rmse = 5.0
    scale = 360 / max_rmse
    metrics = [
        ("RADIAL", off["radial_rmse_mean_mm"], on["radial_rmse_mean_mm"]),
        ("TANGENTIAL", off["tangential_rmse_mean_mm"], on["tangential_rmse_mean_mm"]),
    ]
    centers = [left_x + 260, left_x + 650]
    for center, (label, off_value, on_value) in zip(centers, metrics):
        for x, value, color in (
            (center - 100, off_value, OFF),
            (center + 20, on_value, ON),
        ):
            height = value * scale
            canvas.rectangle(x, base_y - height, 80, height, color)
            canvas.text(x + 40, base_y - height - 36, f"{value:.2f}", color, 3, "middle")
        canvas.text(center, base_y + 28, label, INK, 2, "middle")
    canvas.line(left_x + 60, base_y, left_x + panel_w - 40, base_y, INK, 2)
    canvas.text(left_x + 260, panel_y + 510, "RADIAL DOWN 14.3%", POSITIVE, 2, "middle")
    canvas.text(left_x + 650, panel_y + 510, "TANGENTIAL UP 23.6%", NEGATIVE, 2, "middle")

    phase_base = panel_y + 430
    phase_max = 400.0
    phase_scale = 360 / phase_max
    phase_values = [off["phase_lag_mean_ms"], on["phase_lag_mean_ms"]]
    phase_centers = [right_x + 155, right_x + 350]
    for center, value, color, label in zip(phase_centers, phase_values, (OFF, ON), ("OFF", "ON")):
        height = max(2.0, value * phase_scale)
        canvas.rectangle(center - 55, phase_base - height, 110, height, color)
        canvas.text(center, phase_base - height - 38, f"{value:.1f}", color, 4, "middle")
        canvas.text(center, phase_base + 28, label, INK, 2, "middle")
    canvas.line(right_x + 55, phase_base, right_x + 445, phase_base, INK, 2)
    canvas.text(right_x + 250, panel_y + 510, "PHASE LAG UP", NEGATIVE, 3, "middle")
    footer(canvas, "CIRCLE R=40 MM | THREE OFF/ON PAIRS | MEAN DIAGNOSTIC VALUES")


def save_pair(name: str, draw: Callable[[Canvas], None]) -> None:
    raster = Raster()
    vector = SVG()
    draw(raster)
    draw(vector)
    raster.save_png(FIGURE_DIR / f"{name}.png")
    vector.save_svg(FIGURE_DIR / f"{name}.svg")


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    run02 = load_json(RUN02_JSON)
    run01 = load_json(RUN01_JSON)

    run02_order = [
        ("cross_pm30", "CROSS"),
        ("reverse_grid_3x3_pm40", "REV. GRID"),
        ("diamond_pm35", "DIAMOND"),
        ("circle_r40", "CIRCLE"),
    ]
    categories = [label for _, label in run02_order]
    absolute = [
        run02["trajectory_summaries"][key]["absolute"]["tracking_xy_rmse"]
        for key, _ in run02_order
    ]
    normalized = [
        run02["trajectory_summaries"][key]["home_normalized"]["tracking_xy_rmse"]
        for key, _ in run02_order
    ]
    off_rmse = [item["off_mean_mm"] for item in absolute]
    on_rmse = [item["on_mean_mm"] for item in absolute]
    absolute_improvement = [item["improvement"]["percent"] for item in absolute]
    normalized_improvement = [item["improvement"]["percent"] for item in normalized]
    command_rate = [
        100
        * run02["trajectory_summaries"][key]["actuator_command"][
            "actual_integer_servo_changed_ratio_mean"
        ]
        for key, _ in run02_order
    ]

    save_pair(
        "run02_rmse_by_trajectory",
        lambda canvas: grouped_bar_chart(
            canvas,
            "RUN 02 TRACKING XY RMSE BY TRAJECTORY",
            "OFF/ON MEAN OF THREE PAIRED REPETITIONS | OFFICIAL ABSOLUTE METRIC",
            categories,
            [("OFF", OFF, off_rmse), ("ON", ON, on_rmse)],
            "TRACKING XY RMSE [MM]",
            maximum=9.0,
        ),
    )
    save_pair(
        "run02_improvement_by_trajectory",
        lambda canvas: signed_bar_chart(
            canvas,
            "RUN 02 RMSE IMPROVEMENT BY TRAJECTORY",
            "POSITIVE VALUES INDICATE LOWER OFFICIAL ABSOLUTE RMSE WITH CORRECTION ON",
            categories,
            absolute_improvement,
            "IMPROVEMENT [%]",
            minimum=-30.0,
            maximum=30.0,
        ),
    )
    save_pair(
        "run02_absolute_vs_home_normalized",
        lambda canvas: grouped_bar_chart(
            canvas,
            "RUN 02 ABSOLUTE VS HOME-NORMALIZED IMPROVEMENT",
            "DIAMOND IMPROVED CONSISTENTLY UNDER BOTH ERROR DEFINITIONS",
            categories,
            [
                ("ABSOLUTE", ABSOLUTE, absolute_improvement),
                ("HOME-NORM.", NORMALIZED, normalized_improvement),
            ],
            "IMPROVEMENT [%]",
            minimum=-40.0,
            maximum=25.0,
            percent=True,
            highlight_index=2,
        ),
    )
    save_pair(
        "run02_circle_error_decomposition",
        lambda canvas: circle_decomposition(
            canvas,
            run02["trajectory_summaries"]["circle_r40"]["circle"],
        ),
    )
    save_pair(
        "run02_actuator_command_change_rate",
        lambda canvas: grouped_bar_chart(
            canvas,
            "RUN 02 INTEGER SERVO COMMAND CHANGE RATE",
            "SHARE OF CORRECTION-ON COMMAND EVENTS THAT CHANGED THE PROJECTED INTEGER SERVO COMMAND",
            categories,
            [("ACTUAL INTEGER CHANGE", ON, command_rate)],
            "COMMAND EVENTS [%]",
            maximum=55.0,
            percent=True,
        ),
    )

    run01_order = [
        ("static_center_hold", "STATIC"),
        ("cross_pm30", "CROSS"),
        ("square_pm30", "SQUARE"),
        ("grid_3x3_pm40", "GRID"),
    ]
    complete_by_trajectory = {item["trajectory"]: item for item in run01["complete_runs"]}
    run01_categories = [label for _, label in run01_order]
    baseline = [
        complete_by_trajectory[key]["baseline_zero_prediction_metrics"]["xy_rmse"]
        for key, _ in run01_order
    ]
    residual = [
        complete_by_trajectory[key]["model_metrics"]["xy_rmse"]
        for key, _ in run01_order
    ]
    expected_improvement = [
        complete_by_trajectory[key]["xy_rmse_improvement_percent"]
        for key, _ in run01_order
    ]
    save_pair(
        "run01_holdout_rmse_by_trajectory",
        lambda canvas: grouped_bar_chart(
            canvas,
            "RUN 01 OFFLINE HOLDOUT RMSE BY TRAJECTORY",
            "ZERO-PREDICTION ERROR VS FROZEN RIDGE RESIDUAL | COMPLETE HOLDOUTS",
            run01_categories,
            [("ZERO PRED.", OFF, baseline), ("RIDGE RESIDUAL", ON, residual)],
            "ERROR XY RMSE [MM]",
            maximum=6.0,
        ),
    )
    save_pair(
        "run01_expected_improvement_by_trajectory",
        lambda canvas: signed_bar_chart(
            canvas,
            "RUN 01 EXPECTED RMSE REDUCTION BY TRAJECTORY",
            "OFFLINE ESTIMATOR RESIDUAL ONLY | NOT ACTUAL HARDWARE CORRECTION PERFORMANCE",
            run01_categories,
            expected_improvement,
            "EXPECTED REDUCTION [%]",
            minimum=0.0,
            maximum=55.0,
            footer_text="OFFLINE RIDGE RESIDUAL REDUCTION | NOT ACTUAL CORRECTION-ON TRACKING",
        ),
    )

    expected_files = 14
    generated = list(FIGURE_DIR.glob("run0[12]_*.png")) + list(
        FIGURE_DIR.glob("run0[12]_*.svg")
    )
    if len(generated) != expected_files:
        raise RuntimeError(f"Expected {expected_files} figure files, found {len(generated)}")
    print(f"Generated {expected_files} figure files in {FIGURE_DIR}")


if __name__ == "__main__":
    main()
