# Plan

## Goal
문서 SoT의 `theta`/`J_i` 기하 정의와 현재 Python `IK/FK` 구현 사이의 부호 불일치를 수정해, `target_z`, `theta_i`, `J_i`, `P_i`가 동일한 물리 의미를 갖도록 맞춘다.

## Files
- `docs/plans/2026-05-25_001_fix_ik_fk_theta_sign_consistency.md`
- `kinematics/inverse_kinematics.py`
- `kinematics/forward_kinematics.py`
- `experiments/fake_pipeline.py`
- `docs/daily_notes/2026-05-25.md`

## Changes
- `inverse_kinematics.py`의 `t -> theta` 복원 부호를 문서 SoT와 일치하도록 수정한다.
- `forward_kinematics.py`의 elbow/sphere center `z` 부호를 문서 SoT와 일치하도록 수정한다.
- `fake_pipeline.py`의 angle range를 현재 SoT `-45..90 deg`에 맞춘다.
- 수정 근거와 검증 결과를 daily note에 기록한다.

## Impact
- Python `IK/FK`의 물리 의미가 문서 SoT와 일치한다.
- fake pipeline CSV의 `theta_cmd/theta_meas/sim_*` 의미가 현재 기하 정의와 정렬된다.
- 기존 데이터와 수치 결과는 달라질 수 있다.

## Risk
- 기존 `workspace_sweep`/fake pipeline 산출물과 값이 달라질 수 있다.
- angle sign이 바뀌면 Simulink/Simscape 비교 스크립트도 재해석이 필요하다.

## Validation
- `delta_fk(45, 45, 45)`가 문서 기하 기준 대칭 해와 일치하는지 확인한다.
- 대표 점들에 대해 `IK -> FK` roundtrip 검증을 다시 수행한다.
- 첫 row 수준의 샘플에서 `target_z`가 음수 `theta` 해와 일관되는지 확인한다.
