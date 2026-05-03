# Plan

## Goal
기본 coarse workspace sweep에서 `ik_reject`가 집중된 `z=-260 mm` 근처를 finer resolution으로 다시 스캔해, 현재 reject가 실제 workspace 경계 때문인지 아니면 각도 범위/branch 규칙이 과도하게 보수적인지 판단할 수 있는 데이터를 확보한다.

## Files
- `experiments/kinematics/workspace_sweep_z260_band_2026-05-04.csv`
- `experiments/kinematics/workspace_sweep_z260_band_2026-05-04.json`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `workspace_sweep.py`는 수정하지 않고 기존 스크립트를 finer range로 실행한다.
- sweep 범위는 우선 `x=-30..30 mm`, `y=-30..30 mm`, `z=-265..-255 mm`로 두고, step은 `5 mm`로 설정한다.
- 실행 결과를 `experiments/kinematics/workspace_sweep_z260_band_2026-05-04.csv`와 같은 stem의 JSON으로 저장한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 실행 범위와 결과 요약을 기록한다.

## Impact
- `ik_reject`가 나타나는 경계 구간을 coarse sweep보다 더 촘촘하게 관찰할 수 있게 된다.
- 이후 `theta` 범위 조정, branch 선택 규칙 검토, trajectory safe zone 결정의 근거가 생긴다.
- 코드나 인터페이스는 변경하지 않고 검증 결과 파일만 추가된다.

## Risk
- `5 mm` 해상도도 경계의 매우 좁은 변화는 놓칠 수 있다.
- 현재 nominal parameter 기준 결과이므로 실제 하드웨어 workspace와 동일하다고 볼 수는 없다.
- reject 원인이 단순 workspace 경계가 아니라 sign/branch 규칙 문제라면 추가 진단이 필요하다.

## Validation
- CSV와 JSON 파일이 정상 생성되는지 확인한다.
- `reason_counts`에서 `ik_reject` 분포가 기본 coarse sweep보다 더 세밀하게 드러나는지 확인한다.
- `z=-255`, `-260`, `-265 mm` 사이에서 valid/invalid 패턴이 어떻게 바뀌는지 검토한다.
