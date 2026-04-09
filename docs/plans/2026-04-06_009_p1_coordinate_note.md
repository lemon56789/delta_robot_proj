# Plan

## Goal
platform center `(x, y, z)` 기준에서 `P_1`의 좌표식을 메모 수준으로 확정하고, arm 1 길이 제약식 전개를 위한 출발점을 만든다.
현재 단계에서는 `P_1` 좌표식과 대칭 확장 방향까지만 정리하며, `E/F/G` 전개 자체는 다음 단계로 둔다.

## Files
- `docs/plans/2026-04-06_009_p1_coordinate_note.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/ik_structure_note.md`에 platform center 기준 `P_1` 좌표식을 추가한다.
- `P1`이 platform triangle의 `-y` 방향 vertex라는 해석을 문서에 명시한다.
- 필요 시 `P_2`, `P_3`의 대칭 방향도 참고 수준으로 함께 적는다.
- `|P_1 - J_1|^2 = l^2` 전개 전의 준비식을 추가한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- arm 1 IK 전개에 필요한 `P_1`과 `J_1` 좌표가 같은 문서 안에서 연결된다.
- 후속 `E_1`, `F_1`, `G_1` 유도 준비가 가능해진다.
- SoT contract field는 바뀌지 않는다.

## Risk
- platform orientation 해석이 later design과 다르면 `P_i` 좌표식을 다시 조정해야 할 수 있다.
- `uP`와 `wP` 사용 기준을 혼동하면 대칭 좌표 작성 시 실수가 생길 수 있다.

## Validation
- `P_1`이 platform center에서 `-y` 방향 vertex로 읽히는지 확인한다.
- `P_1` 좌표식이 `uP` 정의와 일치하는지 검토한다.
- `J_1`와 함께 길이 제약식 출발점으로 자연스럽게 이어지는지 확인한다.
