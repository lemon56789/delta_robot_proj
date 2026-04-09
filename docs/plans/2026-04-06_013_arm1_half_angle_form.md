# Plan

## Goal
arm 1의 `E_1 cos(theta_1) + F_1 sin(theta_1) + G_1 = 0` 식에 반각 치환을 적용해 `t_1 = tan(theta_1 / 2)` 해 형태와 `theta_1 = 2 atan(t_1)` 복원식까지 정리한다.
현재 단계에서는 arm 1만 닫고, arm 2와 arm 3는 다음 단계로 둔다.

## Files
- `docs/plans/2026-04-06_013_arm1_half_angle_form.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/ik_structure_note.md`에 arm 1 반각 치환 과정을 추가한다.
- `t_1`에 대한 해 식을 명시한다.
- `theta_1 = 2 atan(t_1)` 복원식을 추가한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- arm 1 IK가 `2atan(t)` 구조로 실제 프로젝트 변수 기준까지 연결된다.
- 이후 arm 2, arm 3 대칭 확장과 코드 구현 준비가 쉬워진다.

## Risk
- 반각 치환 식의 분모/부호가 틀리면 전체 해가 흔들릴 수 있다.
- `±` 해 선택 규칙은 아직 없으므로, 해 식을 곧바로 구현 규칙처럼 읽지 않게 주의가 필요하다.

## Validation
- 반각 치환이 `E_1`, `F_1`, `G_1` 식과 일관되는지 확인한다.
- `t_1` 식이 일반 논문식 구조와 같은지 검토한다.
- `theta_1 = 2 atan(t_1)` 복원식이 문서에 분명히 드러나는지 확인한다.
