# Plan

## Goal
현재 `ik_reject`로만 뭉뚱그려 기록되는 inverse kinematics 실패를 arm별 상세 사유로 분해해, reject가 실제 workspace 경계 때문인지 각도 범위/branch 선택 규칙 때문인지 판단할 수 있는 진단 경로를 추가한다.

## Files
- `kinematics/inverse_kinematics.py`
- `kinematics/workspace_sweep.py`
- `kinematics/README.md`
- `experiments/kinematics/workspace_sweep_z260_band_diagnosed_2026-05-04.csv`
- `experiments/kinematics/workspace_sweep_z260_band_diagnosed_2026-05-04.json`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `kinematics/inverse_kinematics.py`에 arm별 진단 정보를 담는 구조를 추가한다.
- 실패 사유는 최소한 `discriminant_negative`, `denominator_singular`, `angle_out_of_range`, `no_valid_branch` 수준으로 구분한다.
- 전체 `delta_ik` 호출에서 기존 public behavior는 유지하되, 선택적으로 상세 진단을 반환하거나 접근할 수 있게 한다.
- `kinematics/workspace_sweep.py`가 상세 진단을 받아 CSV/JSON에 기록하도록 확장한다.
- `z=-260 mm` 근처 finer scan을 진단 모드로 다시 실행해 새 CSV/JSON 결과를 저장한다.
- `kinematics/README.md`에 reject cause diagnosis 가능 여부를 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유, 방법, 진단 결과 요약을 기록한다.

## Impact
- `ik_reject`가 단순 카운트가 아니라 원인별 분포로 분석 가능해진다.
- 이후 `theta` 범위 조정, branch 규칙 수정, workspace safe zone 정의에 직접적인 근거가 생긴다.
- 기존 IK 함수의 정상 성공 경로와 CSV 계약은 유지한다.

## Risk
- public 함수 인터페이스를 건드리는 방식이 크면 기존 호출부와 충돌할 수 있다.
- 진단 컬럼이 과도하게 늘어나면 CSV 가독성이 떨어질 수 있다.
- 현재 수식 정의 자체가 잘못된 경우 원인 분류가 “증상”만 보여주고 근본 원인은 따로 분석해야 할 수 있다.

## Validation
- Python 구문 검증을 수행한다.
- 기존 `validate_roundtrip.py`가 계속 통과하는지 확인한다.
- 진단 모드로 `z=-260 mm` 근처 sweep를 다시 실행해 CSV/JSON에 상세 원인이 기록되는지 확인한다.
- arm별 reject cause 분포가 실제로 집계 가능한지 확인한다.
