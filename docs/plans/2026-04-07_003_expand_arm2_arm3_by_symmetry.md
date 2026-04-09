# Plan

## Goal
arm 1 기준 IK 전개를 arm 2와 arm 3로 회전 대칭 확장한다.
방향벡터 기반으로 `B_i`, `P_i`, `J_i`를 일반화하고, arm 2/3의 `E_i`, `F_i`, `G_i`를 문서에 정리한다.

## Files
- `docs/plans/2026-04-07_003_expand_arm2_arm3_by_symmetry.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-07.md`

## Changes
- `docs/ik_structure_note.md`에 arm 방향 단위벡터 `e_1`, `e_2`, `e_3`를 추가한다.
- `B_i`, `P_i`, `J_i`를 방향벡터 기준으로 일반화한다.
- arm 2와 arm 3의 `E_i`, `F_i`, `G_i`를 명시한다.
- arm 1 식이 일반식의 특수한 경우라는 점을 정리한다.
- 변경 기록을 `docs/daily_notes/2026-04-07.md`에 추가한다.

## Impact
- 3개 arm 전체의 IK 구조가 같은 문서 안에서 정리된다.
- 이후 코드 구현에서 arm별 분기 없이 같은 패턴으로 계산할 수 있다.

## Risk
- 방향벡터 부호가 틀리면 arm 2/3 식이 전부 어긋난다.
- arm 1 식과 일반식의 대응을 명확히 보여주지 않으면 검증이 어렵다.

## Validation
- `e_1`, `e_2`, `e_3`가 현재 좌표계 정의와 맞는지 확인한다.
- arm 1 식이 일반식에서 그대로 복원되는지 검토한다.
- arm 2/3의 `E_i`, `F_i`, `G_i`가 회전 대칭 형태로 읽히는지 확인한다.
