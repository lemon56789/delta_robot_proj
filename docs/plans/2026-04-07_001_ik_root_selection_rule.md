# Plan

## Goal
`2atan(t)` 기반 IK의 `+/-` 해 선택 규칙을 문서에 반영한다.
판별식, 각도 범위, downward-working branch, 이전 각도 기반 연속성 기준을 순서대로 정리해 후속 구현 기준으로 사용할 수 있게 한다.

## Files
- `docs/plans/2026-04-07_001_ik_root_selection_rule.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-07.md`

## Changes
- `docs/ik_structure_note.md`에 `IK Root Selection Rule` 섹션을 추가한다.
- 판별식 기반 reject, 각도 범위 검사, downward-working branch 검사, 연속성 기반 선택 순서를 문장으로 정리한다.
- `previous_theta_i`가 없는 초기 시점 처리 규칙도 포함한다.
- 변경 기록을 `docs/daily_notes/2026-04-07.md`에 추가한다.

## Impact
- `+/-` 해 처리 기준이 문서로 고정된다.
- 후속 구현과 테스트에서 branch jump를 줄일 수 있다.
- 아직 구체 수치가 없는 `theta_min`, `theta_max`는 후속 확정 항목으로 남긴다.

## Risk
- `theta_min`, `theta_max` 수치가 아직 없으므로 구현 시 추가 확정이 필요하다.
- downward-working branch 판정 문장이 모호하면 구현 해석이 다시 갈릴 수 있다.

## Validation
- 규칙이 판별식, 각도 범위, branch, 연속성 순으로 읽히는지 확인한다.
- 현재 `theta_i` 정의와 충돌하지 않는지 검토한다.
- 구현 규칙으로 바로 옮길 수 있을 정도로 명확한지 확인한다.
