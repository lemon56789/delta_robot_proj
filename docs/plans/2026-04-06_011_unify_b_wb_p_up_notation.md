# Plan

## Goal
IK 메모에서 base point `B_i`는 `wB` 기준으로, platform point `P_i`는 `uP` 기준으로만 표현하도록 표기를 통일한다.
좌표식 이해를 단순화하고, `sB/sP`를 직접 쓰는 혼합 표현을 제거한다.

## Files
- `docs/plans/2026-04-06_011_unify_b_wb_p_up_notation.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/ik_structure_note.md`에서 `B_i` 좌표식을 `wB` 기준으로만 정리한다.
- `docs/ik_structure_note.md`에서 `P_i` 좌표식을 `uP` 기준으로만 정리한다.
- `sB/sP`를 직접 쓰는 좌표 표현은 제거한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- base/platform 점 좌표식이 더 일관되게 읽힌다.
- 후속 `E/F/G` 전개에서 불필요한 변수 혼용을 줄일 수 있다.
- 기구 파라미터 정의 자체는 바뀌지 않는다.

## Risk
- 다른 문서나 대화에서 이미 `sB/sP` 기준 표현을 쓰고 있으면 잠깐 혼동이 생길 수 있다.

## Validation
- `B_i`가 모두 `wB`만으로 표현되는지 확인한다.
- `P_i`가 모두 `uP`만으로 표현되는지 확인한다.
- arm 1 길이 제약식이 동일하게 이어지는지 검토한다.
