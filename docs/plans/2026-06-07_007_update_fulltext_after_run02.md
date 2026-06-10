# Plan

## Goal
`fulltext.md`의 Run 01-main 이전 상태를 2026-06-07 기준 실제 진행 상태로
갱신해 외부 AI가 Run 01 학습, Run 02 보정 비교, 재분석과 최소
하드웨어 후속 실험을 정확히 이해할 수 있게 한다.

## Files
- `docs/plans/2026-06-07_007_update_fulltext_after_run02.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 갱신일을 `2026-06-07`로 변경한다.
- Run 01-main/holdout 수집, alignment, Ridge 학습 및 correction engine
  상태를 반영한다.
- Run 02 24개 OFF/ON 실험과 12 pair 공식 비교 결과를 요약한다.
- absolute/home-normalized 재분석, integer servo command 반영률, step
  segment와 circle radial/tangential/phase 진단 결과를 반영한다.
- Diamond의 일관된 개선과 cross/reverse grid/circle의 제한을 구분해
  기록한다.
- `+40/+60 mm` preload home repeatability 6개 확정 run ID와 Computer
  2/Vision Codex 인수인계 문서를 반영한다.
- Stage 7~9 상태, 바로 다음 작업과 blocker를 현재 상태로 갱신한다.

## Impact
- 요약 문서와 변경 기록만 수정한다.
- 코드, raw/processed 데이터, 결과 JSON, 인터페이스와 실험 계약은
  변경하지 않는다.

## Risk
- 기존 공식 comparison과 diagnostic 재분석 결과를 혼동하면 correction
  효과를 과대 해석할 수 있다.
- `fulltext.md`는 요약본이므로 세부 수치와 계약은 기존 `docs/*` 및 결과
  JSON을 우선해야 한다.

## Validation
- `fulltext.md`에서 Run 01-main 미착수, Stage 8 미착수, Run 02 미착수
  같은 오래된 상태가 제거됐는지 확인한다.
- Run 02 공식 metric과 재분석 metric이 원본 결과 JSON 및 Run 02
  문서와 일치하는지 확인한다.
- 6개 home repeatability run ID와 두 인수인계 문서 경로가 정확한지
  확인한다.
- Markdown 형식과 whitespace를 검증한다.
