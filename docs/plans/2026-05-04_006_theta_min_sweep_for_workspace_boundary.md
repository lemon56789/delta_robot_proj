# Plan

## Goal
현재 `ik_reject`의 주요 원인이 `angle_out_of_range`로 확인된 상태에서, `theta_max=90 deg`는 유지하고 `theta_min`만 음수 방향으로 단계적으로 완화해 reject가 줄어드는지 확인한다. 목적은 현재 `theta_min=0 deg` 제한이 실제 workspace를 과도하게 자르고 있는지 판단하는 것이다.

## Files
- `kinematics/inverse_kinematics.py`
- `kinematics/workspace_sweep.py`
- `kinematics/README.md`
- `experiments/kinematics/theta_min_sweep_z260_band_2026-05-04.csv`
- `experiments/kinematics/theta_min_sweep_z260_band_2026-05-04.json`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `workspace_sweep.py`가 `theta_min_deg`, `theta_max_deg`를 실행 인자로 받을 수 있게 확장한다.
- sweep 결과 CSV/JSON에 사용한 `theta_min_deg`, `theta_max_deg`를 함께 기록한다.
- `z=-265..-255 mm`, `x,y=-30..30 mm`, `step=5 mm` 범위에 대해 `theta_min = 0, -5, -10, -15 deg`를 순차적으로 적용해 같은 band를 반복 스캔한다.
- 결과는 한 번의 비교용 CSV/JSON 또는 run별 구분 가능한 구조로 저장해 `theta_min`별 `ik_reject` 감소량을 비교할 수 있게 한다.
- `kinematics/README.md`에 angle range sweep 가능 여부를 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 실행 조건과 비교 결과를 기록한다.

## Impact
- 현재 `theta_min=0 deg` 제한이 nominal workspace 경계를 인위적으로 자르는지 판단할 근거가 생긴다.
- 이후 하드웨어 허용 범위와 수학적 허용 범위를 분리해 논의할 수 있게 된다.
- 기존 IK/FK 기본 동작은 유지한다.

## Risk
- 음수 `theta_min`에서 수학적으로 살아나는 점이 실제 하드웨어에서는 간섭이나 조립 제약 때문에 불가능할 수 있다.
- 여러 설정을 한 파일에 섞어 저장하면 비교는 쉬워도 후처리 코드가 약간 복잡해질 수 있다.
- `theta_min`을 풀어도 reject가 거의 줄지 않으면 원인이 다른 규칙이나 기하 경계일 수 있다.

## Validation
- Python 구문 검증을 수행한다.
- 기존 `validate_roundtrip.py`가 계속 통과하는지 확인한다.
- `theta_min=0,-5,-10,-15 deg` 비교 sweep를 실행해 `ik_reject`와 arm별 `angle_out_of_range`가 어떻게 변하는지 확인한다.
- 결과 CSV/JSON에서 `theta_min`별 통계 비교가 가능한지 확인한다.
