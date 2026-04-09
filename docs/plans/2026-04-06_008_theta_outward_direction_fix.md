# Plan

## Goal
arm 1의 `theta_1 = 0 deg` 방향이 원점 `O`의 반대방향이어야 한다는 기준에 맞춰 IK 메모 문서의 좌표식과 설명을 수정한다.
`theta_i`의 기준 자세는 유지하면서, arm 1의 local horizontal direction 해석과 `J_1(theta_1)` 식의 부호를 바로잡는다.

## Files
- `docs/plans/2026-04-06_008_theta_outward_direction_fix.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/ik_structure_note.md`의 arm 1 local plane 설명에서 `theta_1 = 0 deg` 방향을 원점 `O` 반대방향으로 수정한다.
- `J_1(theta_1)`의 `y` 성분 부호를 수정해 outward 방향 기준으로 다시 쓴다.
- 식 해석 설명도 수정된 방향 기준에 맞게 바꾼다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- arm 1 기준 좌표식이 사용자 합의 방향과 일치하게 된다.
- 후속 `P_1` 좌표식과 `E/F/G` 유도에서 부호 혼선을 줄일 수 있다.
- IK interface contract 자체는 바뀌지 않는다.

## Risk
- arm 1 기준만 수정한 뒤 arm 2, arm 3 확장 규칙을 늦게 정하면 대칭 적용 시 다시 혼선이 생길 수 있다.
- local plane 기준 설명이 부족하면 outward/inward 해석이 다시 흔들릴 수 있다.

## Validation
- `theta_1 = 0 deg`일 때 `J_1`이 원점 반대방향으로 가는지 확인한다.
- `theta_1 = 90 deg`일 때 `J_1`이 `-z` 방향으로 내려가는지 확인한다.
- 문서 설명과 좌표식 부호가 서로 일치하는지 검토한다.
