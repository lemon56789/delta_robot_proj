from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from kinematics.geometry import DeltaGeometry, NOMINAL_DELTA_GEOMETRY
from kinematics.inverse_kinematics import ARM_OUTWARD_UNIT_VECTORS


class ForwardKinematicsError(ValueError):
    """Raised when forward kinematics cannot converge to a valid solution."""


@dataclass(frozen=True)
class ForwardKinematicsResult:
    x_mm: float
    y_mm: float
    z_mm: float
    iterations: int
    max_residual_mm2: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x_mm, self.y_mm, self.z_mm)


def delta_fk(
    theta1_deg: float,
    theta2_deg: float,
    theta3_deg: float,
    *,
    geometry: DeltaGeometry = NOMINAL_DELTA_GEOMETRY,
    initial_guess_mm: Iterable[float] | None = None,
    max_iterations: int = 25,
    residual_tolerance_mm2: float = 1e-6,
    step_tolerance_mm: float = 1e-9,
) -> ForwardKinematicsResult:
    """Solve forward kinematics for the project delta robot.

    The nonlinear system is solved numerically from the same algebraic
    constraint set used by the current IK implementation.
    """

    sphere_centers = _constraint_sphere_centers(
        (theta1_deg, theta2_deg, theta3_deg),
        geometry,
    )
    if initial_guess_mm is None:
        current = _initial_guess_from_spheres(sphere_centers, geometry.l)
    else:
        current = _tuple3(initial_guess_mm, "initial_guess_mm")

    residuals = _residuals(current, sphere_centers, geometry.l)
    for iteration in range(1, max_iterations + 1):
        max_residual = max(abs(value) for value in residuals)
        if max_residual <= residual_tolerance_mm2:
            return ForwardKinematicsResult(*current, iteration - 1, max_residual)

        jacobian = _jacobian(current, sphere_centers)
        step = _solve_linear_system(
            jacobian,
            [-value for value in residuals],
        )
        current, residuals = _apply_damped_step(
            current=current,
            step=step,
            sphere_centers=sphere_centers,
            link_length_mm=geometry.l,
        )

        if _vector_norm(step) <= step_tolerance_mm:
            max_residual = max(abs(value) for value in residuals)
            if max_residual <= residual_tolerance_mm2:
                return ForwardKinematicsResult(*current, iteration, max_residual)
            raise ForwardKinematicsError("forward kinematics stagnated before convergence")

    max_residual = max(abs(value) for value in residuals)
    raise ForwardKinematicsError(
        f"forward kinematics did not converge within {max_iterations} iterations "
        f"(max residual: {max_residual:.6e} mm^2)"
    )


def _constraint_sphere_centers(
    theta_deg: tuple[float, float, float],
    geometry: DeltaGeometry,
) -> tuple[tuple[float, float, float], ...]:
    delta_offset = geometry.uP - geometry.wB
    centers: list[tuple[float, float, float]] = []
    for angle_deg, arm_vector in zip(theta_deg, ARM_OUTWARD_UNIT_VECTORS, strict=True):
        angle_rad = math.radians(angle_deg)
        radial_component = geometry.L * math.cos(angle_rad) - delta_offset
        z_component = geometry.L * math.sin(angle_rad)
        centers.append(
            (
                radial_component * arm_vector[0],
                radial_component * arm_vector[1],
                z_component,
            )
        )
    return tuple(centers)


def _initial_guess_from_spheres(
    sphere_centers: tuple[tuple[float, float, float], ...],
    link_length_mm: float,
) -> tuple[float, float, float]:
    c1, c2, c3 = sphere_centers
    normal_a = _vector_subtract(c2, c1)
    normal_b = _vector_subtract(c3, c1)
    line_direction = _cross(normal_a, normal_b)
    line_direction_norm_sq = _dot(line_direction, line_direction)
    if line_direction_norm_sq <= 1e-12:
        centroid = _vector_scale(
            _vector_add(_vector_add(c1, c2), c3),
            1.0 / 3.0,
        )
        return (centroid[0], centroid[1], centroid[2] - link_length_mm)

    plane_offset_a = (_dot(c2, c2) - _dot(c1, c1)) / 2.0
    plane_offset_b = (_dot(c3, c3) - _dot(c1, c1)) / 2.0
    line_point = _vector_scale(
        _vector_add(
            _vector_scale(_cross(normal_b, line_direction), plane_offset_a),
            _vector_scale(_cross(line_direction, normal_a), plane_offset_b),
        ),
        1.0 / line_direction_norm_sq,
    )

    return line_point


def _residuals(
    position_mm: tuple[float, float, float],
    sphere_centers: tuple[tuple[float, float, float], ...],
    link_length_mm: float,
) -> list[float]:
    link_length_sq = link_length_mm * link_length_mm
    return [
        _dot(_vector_subtract(position_mm, center), _vector_subtract(position_mm, center))
        - link_length_sq
        for center in sphere_centers
    ]


def _jacobian(
    position_mm: tuple[float, float, float],
    sphere_centers: tuple[tuple[float, float, float], ...],
) -> list[list[float]]:
    return [
        [
            2.0 * (position_mm[0] - center[0]),
            2.0 * (position_mm[1] - center[1]),
            2.0 * (position_mm[2] - center[2]),
        ]
        for center in sphere_centers
    ]


def _apply_damped_step(
    *,
    current: tuple[float, float, float],
    step: tuple[float, float, float],
    sphere_centers: tuple[tuple[float, float, float], ...],
    link_length_mm: float,
) -> tuple[tuple[float, float, float], list[float]]:
    current_residuals = _residuals(current, sphere_centers, link_length_mm)
    current_norm = _max_abs(current_residuals)
    damping = 1.0
    for _ in range(12):
        candidate = (
            current[0] + damping * step[0],
            current[1] + damping * step[1],
            current[2] + damping * step[2],
        )
        residuals = _residuals(candidate, sphere_centers, link_length_mm)
        if _max_abs(residuals) < current_norm:
            return candidate, residuals
        damping *= 0.5
    raise ForwardKinematicsError("forward kinematics step damping failed to reduce residuals")


def _solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> tuple[float, float, float]:
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs, strict=True)]
    size = 3

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row: abs(augmented[row][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) <= 1e-12:
            raise ForwardKinematicsError("forward kinematics Jacobian is singular")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot_value = augmented[pivot_index][pivot_index]
        for column in range(pivot_index, size + 1):
            augmented[pivot_index][column] /= pivot_value

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column in range(pivot_index, size + 1):
                augmented[row_index][column] -= factor * augmented[pivot_index][column]

    return (augmented[0][3], augmented[1][3], augmented[2][3])


def _tuple3(values: Iterable[float], name: str) -> tuple[float, float, float]:
    result = tuple(values)
    if len(result) != 3:
        raise ValueError(f"{name} must contain exactly three values.")
    return (float(result[0]), float(result[1]), float(result[2]))


def _vector_add(
    lhs: tuple[float, float, float],
    rhs: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (lhs[0] + rhs[0], lhs[1] + rhs[1], lhs[2] + rhs[2])


def _vector_subtract(
    lhs: tuple[float, float, float],
    rhs: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (lhs[0] - rhs[0], lhs[1] - rhs[1], lhs[2] - rhs[2])


def _vector_scale(
    vector: tuple[float, float, float],
    scalar: float,
) -> tuple[float, float, float]:
    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _dot(lhs: tuple[float, float, float], rhs: tuple[float, float, float]) -> float:
    return lhs[0] * rhs[0] + lhs[1] * rhs[1] + lhs[2] * rhs[2]


def _cross(lhs: tuple[float, float, float], rhs: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        lhs[1] * rhs[2] - lhs[2] * rhs[1],
        lhs[2] * rhs[0] - lhs[0] * rhs[2],
        lhs[0] * rhs[1] - lhs[1] * rhs[0],
    )


def _vector_norm(vector: tuple[float, float, float]) -> float:
    return math.sqrt(_dot(vector, vector))


def _max_abs(values: Iterable[float]) -> float:
    return max(abs(value) for value in values)
