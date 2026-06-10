# Plan

## Goal
`fulltext.md`와 상위 Source of Truth인 `docs/roadmap.md`의 현재 상태를
2026-06-10 기준으로 정합화하고, Run 02 개선율의 계산 정의를 명확히
구분한다.

## Files
- `docs/plans/2026-06-10_001_fulltext_roadmap_consistency.md`
- `fulltext.md`
- `docs/roadmap.md`
- `docs/daily_notes/2026-06-10.md`

## Changes
- `fulltext.md`의 `kinematics/`, `simulation/` 폴더 설명에서 현재 구현
  상태와 맞지 않는 `예정` 표현을 제거한다.
- Run 02 trajectory별 표의 개선율이 pair별 개선율 평균임을 명시한다.
- OFF/ON trajectory 평균 RMSE를 직접 비교한 개선율을 별도로 기록해
  pair별 개선율 평균과 혼동되지 않게 한다.
- `docs/roadmap.md`의 기준일과 Stage 4~9 상태를 Run 01-main, Ridge
  학습, Run 02 수집 및 재분석 완료 상태로 갱신한다.
- 변경 내용과 검증 결과를 `docs/daily_notes/2026-06-10.md`에 기록한다.

## Impact
- 문서 상태와 지표 설명만 변경한다.
- 코드, 데이터, 모델, CSV 계약, 공개 인터페이스 및 제어 흐름은
  변경하지 않는다.

## Risk
- pair별 개선율 평균과 평균 RMSE 직접 비교 개선율을 하나의 수치로
  혼용하면 기존 실험 결과와 발표 자료의 해석이 달라질 수 있다.
- 로드맵을 과도하게 완료 처리하면 Stage 9 전체 성공으로 오해할 수
  있으므로 Run 02 전체 개선은 확인되지 않았음을 유지한다.

## Validation
- `fulltext.md`와 `docs/roadmap.md`의 Stage 4~9 상태가 서로 일치하는지
  확인한다.
- Run 02 원본 JSON 기준으로 pair별 개선율 평균과 평균 RMSE 직접 비교
  개선율을 각각 대조한다.
- 오래된 `Run 01-main 준비 중`, `Stage 8 미착수`, 구현 `예정` 표현이
  제거됐는지 검색한다.
- Markdown whitespace와 `git diff --check`를 검증한다.
