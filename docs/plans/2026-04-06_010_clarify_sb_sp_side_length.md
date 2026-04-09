# Plan

## Goal
`sB`와 `sP`의 의미를 더 명확히 하기 위해, 각각 base/platform 정삼각형의 변 길이라는 점을 문서에 직접 명시한다.
기존 좌표계와 기구 변수 정의는 유지하고, 표현만 더 분명하게 정리한다.

## Files
- `docs/plans/2026-04-06_010_clarify_sb_sp_side_length.md`
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/system_data_flow.md`의 기구 변수 설명에서 `sB`, `sP`를 각각 base/platform 정삼각형의 변 길이라고 명시한다.
- `docs/ik_structure_note.md`의 변수 매핑 설명에도 같은 의미를 반영한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- 기구 변수 해석이 더 명확해진다.
- `sB`, `sP`, `uB`, `uP`, `wB`, `wP`의 관계를 읽기 쉬워진다.
- 기존 계약이나 좌표계 정의는 바뀌지 않는다.

## Risk
- 표현만 바꾸는 작업이라 기술적 리스크는 낮다.
- 다른 문서가 이전 축약 표현을 그대로 쓰면 해석 일관성이 잠시 흔들릴 수 있다.

## Validation
- `sB`, `sP`가 각각 side length로 읽히는지 확인한다.
- `uB`, `uP`, `wB`, `wP`와 함께 읽어도 의미 충돌이 없는지 검토한다.
