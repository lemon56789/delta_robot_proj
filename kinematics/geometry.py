from dataclasses import dataclass


@dataclass(frozen=True)
class DeltaGeometry:
    """Nominal delta robot geometry parameters in millimeters."""

    upper_arm_length_mm: float
    parallelogram_link_length_mm: float
    base_center_to_side_mm: float
    platform_center_to_vertex_mm: float

    @property
    def L(self) -> float:
        return self.upper_arm_length_mm

    @property
    def l(self) -> float:
        return self.parallelogram_link_length_mm

    @property
    def wB(self) -> float:
        return self.base_center_to_side_mm

    @property
    def uP(self) -> float:
        return self.platform_center_to_vertex_mm


NOMINAL_DELTA_GEOMETRY = DeltaGeometry(
    upper_arm_length_mm=125.0,
    parallelogram_link_length_mm=300.0,
    base_center_to_side_mm=24.051,
    platform_center_to_vertex_mm=27.177,
)
