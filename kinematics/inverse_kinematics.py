from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from kinematics.geometry import DeltaGeometry, NOMINAL_DELTA_GEOMETRY


SQRT_3_OVER_2 = math.sqrt(3.0) / 2.0
ARM_OUTWARD_UNIT_VECTORS: tuple[tuple[float, float], ...] = (
    (0.0, -1.0),
    (SQRT_3_OVER_2, 0.5),
    (-SQRT_3_OVER_2, 0.5),
)


class InverseKinematicsError(ValueError):
    """Raised when a target position cannot be mapped to a valid IK solution."""


@dataclass(frozen=True)
class InverseKinematicsResult:
    theta1_deg: float
    theta2_deg: float
    theta3_deg: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.theta1_deg, self.theta2_deg, self.theta3_deg)


@dataclass(frozen=True)
class SingleArmIkDiagnostic:
    arm_index: int
    p_i: float
    e_term: float
    f_term: float
    g_term: float
    discriminant: float
    denominator: float
    t_candidates: tuple[float, ...]
    theta_candidates_deg: tuple[float, ...]
    valid_thetas_deg: tuple[float, ...]
    selected_theta_deg: float | None
    status: str


@dataclass(frozen=True)
class InverseKinematicsDiagnostic:
    x_mm: float
    y_mm: float
    z_mm: float
    theta_min_deg: float
    theta_max_deg: float
    success: bool
    result: InverseKinematicsResult | None
    arm_diagnostics: tuple[SingleArmIkDiagnostic, ...]
    failure_summary: str | None


def delta_ik(
    x_mm: float,
    y_mm: float,
    z_mm: float,
    *,
    geometry: DeltaGeometry = NOMINAL_DELTA_GEOMETRY,
    previous_theta_deg: Iterable[float] | None = None,
    theta_min_deg: float = 0.0,
    theta_max_deg: float = 90.0,
) -> InverseKinematicsResult:
    """Solve inverse kinematics for the project delta robot.

    Input position unit is millimeters in `base_frame`.
    Output angle unit is degrees following the project `theta_i` convention.
    """

    diagnostic = diagnose_delta_ik(
        x_mm=x_mm,
        y_mm=y_mm,
        z_mm=z_mm,
        geometry=geometry,
        previous_theta_deg=previous_theta_deg,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
    )
    if diagnostic.result is None:
        raise InverseKinematicsError("reject")
    return diagnostic.result


def diagnose_delta_ik(
    x_mm: float,
    y_mm: float,
    z_mm: float,
    *,
    geometry: DeltaGeometry = NOMINAL_DELTA_GEOMETRY,
    previous_theta_deg: Iterable[float] | None = None,
    theta_min_deg: float = 0.0,
    theta_max_deg: float = 90.0,
) -> InverseKinematicsDiagnostic:
    previous = tuple(previous_theta_deg) if previous_theta_deg is not None else None
    if previous is not None and len(previous) != 3:
        raise ValueError("previous_theta_deg must contain exactly three angles.")

    arm_diagnostics: list[SingleArmIkDiagnostic] = []
    theta_candidates: list[float] = []
    failure_summary: str | None = None

    for arm_index, arm_vector in enumerate(ARM_OUTWARD_UNIT_VECTORS, start=1):
        arm_diagnostic = _diagnose_single_arm(
            arm_index=arm_index,
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            arm_vector=arm_vector,
            geometry=geometry,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
            previous_theta_deg=None if previous is None else previous[arm_index - 1],
        )
        arm_diagnostics.append(arm_diagnostic)
        if arm_diagnostic.selected_theta_deg is None:
            if failure_summary is None:
                failure_summary = f"arm{arm_index}:{arm_diagnostic.status}"
        else:
            theta_candidates.append(arm_diagnostic.selected_theta_deg)

    if failure_summary is not None:
        return InverseKinematicsDiagnostic(
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            theta_min_deg=theta_min_deg,
            theta_max_deg=theta_max_deg,
            success=False,
            result=None,
            arm_diagnostics=tuple(arm_diagnostics),
            failure_summary=failure_summary,
        )

    result = InverseKinematicsResult(*theta_candidates)
    return InverseKinematicsDiagnostic(
        x_mm=x_mm,
        y_mm=y_mm,
        z_mm=z_mm,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
        success=True,
        result=result,
        arm_diagnostics=tuple(arm_diagnostics),
        failure_summary=None,
    )


def _diagnose_single_arm(
    *,
    arm_index: int,
    x_mm: float,
    y_mm: float,
    z_mm: float,
    arm_vector: tuple[float, float],
    geometry: DeltaGeometry,
    theta_min_deg: float,
    theta_max_deg: float,
    previous_theta_deg: float | None,
) -> SingleArmIkDiagnostic:
    p_i = x_mm * arm_vector[0] + y_mm * arm_vector[1]
    delta_offset = geometry.uP - geometry.wB
    e_term = -2.0 * geometry.L * (p_i + delta_offset)
    f_term = 2.0 * geometry.L * z_mm
    g_term = (
        x_mm * x_mm
        + y_mm * y_mm
        + delta_offset * delta_offset
        + 2.0 * delta_offset * p_i
        + z_mm * z_mm
        + geometry.L * geometry.L
        - geometry.l * geometry.l
    )

    discriminant = e_term * e_term + f_term * f_term - g_term * g_term
    raw_discriminant = discriminant
    if discriminant < 0.0:
        if discriminant > -1e-9:
            discriminant = 0.0
        else:
            return SingleArmIkDiagnostic(
                arm_index=arm_index,
                p_i=p_i,
                e_term=e_term,
                f_term=f_term,
                g_term=g_term,
                discriminant=raw_discriminant,
                denominator=float("nan"),
                t_candidates=(),
                theta_candidates_deg=(),
                valid_thetas_deg=(),
                selected_theta_deg=None,
                status="discriminant_negative",
            )

    sqrt_discriminant = math.sqrt(discriminant)
    denominator = g_term - e_term

    t_candidates: list[float] = []
    if math.isclose(denominator, 0.0, abs_tol=1e-12):
        if math.isclose(f_term, 0.0, abs_tol=1e-12):
            return SingleArmIkDiagnostic(
                arm_index=arm_index,
                p_i=p_i,
                e_term=e_term,
                f_term=f_term,
                g_term=g_term,
                discriminant=raw_discriminant,
                denominator=denominator,
                t_candidates=(),
                theta_candidates_deg=(),
                valid_thetas_deg=(),
                selected_theta_deg=None,
                status="denominator_singular",
            )
        t_candidates.append(-g_term / (2.0 * f_term))
    else:
        t_candidates.extend(
            [
                (-f_term + sqrt_discriminant) / denominator,
                (-f_term - sqrt_discriminant) / denominator,
            ]
        )

    theta_candidates_deg = tuple(
        -math.degrees(2.0 * math.atan(t_value))
        for t_value in t_candidates
    )
    valid_thetas = _filter_valid_thetas(
        t_candidates=t_candidates,
        theta_min_deg=theta_min_deg,
        theta_max_deg=theta_max_deg,
    )
    if not valid_thetas:
        if theta_candidates_deg and all(
            theta_deg < theta_min_deg - 1e-9 or theta_deg > theta_max_deg + 1e-9
            for theta_deg in theta_candidates_deg
        ):
            status = "angle_out_of_range"
        else:
            status = "no_valid_branch"
        return SingleArmIkDiagnostic(
            arm_index=arm_index,
            p_i=p_i,
            e_term=e_term,
            f_term=f_term,
            g_term=g_term,
            discriminant=raw_discriminant,
            denominator=denominator,
            t_candidates=tuple(t_candidates),
            theta_candidates_deg=theta_candidates_deg,
            valid_thetas_deg=(),
            selected_theta_deg=None,
            status=status,
        )

    selected_theta = _select_theta(valid_thetas, previous_theta_deg)
    return SingleArmIkDiagnostic(
        arm_index=arm_index,
        p_i=p_i,
        e_term=e_term,
        f_term=f_term,
        g_term=g_term,
        discriminant=raw_discriminant,
        denominator=denominator,
        t_candidates=tuple(t_candidates),
        theta_candidates_deg=theta_candidates_deg,
        valid_thetas_deg=tuple(valid_thetas),
        selected_theta_deg=selected_theta,
        status="ok",
    )


def _filter_valid_thetas(
    *,
    t_candidates: Iterable[float],
    theta_min_deg: float,
    theta_max_deg: float,
) -> list[float]:
    valid: list[float] = []
    for t_value in t_candidates:
        # The algebraic half-angle form yields the opposite sign of the
        # project-facing `theta_i` convention, so we flip it here before
        # applying the documented working range.
        theta_deg = -math.degrees(2.0 * math.atan(t_value))
        if theta_deg < theta_min_deg - 1e-9 or theta_deg > theta_max_deg + 1e-9:
            continue
        if any(math.isclose(theta_deg, existing, abs_tol=1e-9) for existing in valid):
            continue
        valid.append(theta_deg)
    return valid


def _select_theta(valid_thetas: Iterable[float], previous_theta_deg: float | None) -> float:
    candidates = list(valid_thetas)
    if previous_theta_deg is None:
        return min(candidates)
    return min(candidates, key=lambda theta_deg: abs(theta_deg - previous_theta_deg))
