from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kinematics.forward_kinematics import ForwardKinematicsError, delta_fk
from kinematics.inverse_kinematics import InverseKinematicsError, delta_ik


@dataclass(frozen=True)
class RoundTripSample:
    x_mm: float
    y_mm: float
    z_mm: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x_mm, self.y_mm, self.z_mm)


SAMPLES: tuple[RoundTripSample, ...] = (
    RoundTripSample(0.0, 0.0, -200.0),
    RoundTripSample(0.0, 0.0, -250.0),
    RoundTripSample(20.0, 0.0, -220.0),
    RoundTripSample(0.0, 20.0, -220.0),
    RoundTripSample(-15.0, 10.0, -215.0),
)


def main() -> int:
    max_position_error_mm = 0.0
    for sample in SAMPLES:
        original = sample.as_tuple()
        try:
            ik_result = delta_ik(*original)
            fk_result = delta_fk(*ik_result.as_tuple())
        except (InverseKinematicsError, ForwardKinematicsError) as exc:
            print(f"{original} -> validation failed: {exc}")
            return 1

        reconstructed = fk_result.as_tuple()
        error = _distance_mm(original, reconstructed)
        max_position_error_mm = max(max_position_error_mm, error)
        print(
            f"{original} -> theta={_format_tuple(ik_result.as_tuple())} -> "
            f"fk={_format_tuple(reconstructed)} | "
            f"position_error_mm={error:.6f} | iterations={fk_result.iterations}"
        )

    print(f"max_position_error_mm={max_position_error_mm:.6f}")
    return 0


def _distance_mm(
    lhs: tuple[float, float, float],
    rhs: tuple[float, float, float],
) -> float:
    return math.sqrt(
        (lhs[0] - rhs[0]) ** 2
        + (lhs[1] - rhs[1]) ** 2
        + (lhs[2] - rhs[2]) ** 2
    )


def _format_tuple(values: tuple[float, float, float]) -> str:
    return "(" + ", ".join(f"{value:.6f}" for value in values) + ")"


if __name__ == "__main__":
    raise SystemExit(main())
