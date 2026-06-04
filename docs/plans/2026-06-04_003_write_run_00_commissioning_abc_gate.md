# Plan

## Goal
Run 00 commissioning 문서를 A/B/C gate 구조로 재작성한다.

## Files
- `docs/plans/2026-06-04_003_write_run_00_commissioning_abc_gate.md`
- `docs/hardware_experiment_run_00_commissioning.md`
- `docs/hardware_experiment_base_config.md`
- `docs/daily_notes/2026-06-04.md`

## Changes
- Run 00 목적을 위치 정확도 평가가 아니라 방향성, 조립 안정성, 로그/비전 준비 상태 확인으로 명시한다.
- `A. Assembled Joint Small-Angle Check`, `B. Cartesian Direction / Parallel Motion Check`, `C. Vision Readiness Check` 구조로 정리한다.
- A 단계는 조립 상태에서 `±3 deg` 후 `±5 deg` 단일축 확인으로 제한한다.
- B 단계는 IK 기반 작은 `x/y` 방향 이동을 `±3 mm` 후 필요 시 `±5 mm`로 확인하되, 좌표 정확도는 평가하지 않는다.
- C 단계는 ArUco marker 검출, `vision_x/y`, 좌표 방향, static noise, 같은 `run_id` 확인으로 정리한다.
- A/B/C gate 조건과 stop/fail 조건을 명시한다.
- base config의 Run 00 commissioning theta test range를 A 단계 기준과 맞춘다.

## Impact
- 하드웨어 실험 문서만 갱신한다.
- 코드, CSV 포맷, 제어 인터페이스 계약은 변경하지 않는다.
- Run 01 baseline으로 넘어가기 전 gate 기준이 명확해진다.

## Risk
- `z0` 안전 기준 높이와 실제 IK target command 구현은 아직 미확정이므로 B 단계에는 `TBD`로 남긴다.
- vision calibration file과 marker 설정이 준비되지 않으면 C 단계는 실패 또는 보류될 수 있다.

## Validation
- Run 00 문서가 A/B/C 순서와 gate 조건을 포함하는지 확인한다.
- base config와 Run 00의 초기 small-angle 범위가 충돌하지 않는지 확인한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
