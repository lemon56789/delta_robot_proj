# Plan

## Goal
Run 02 발표 요약 Markdown을 한국어로 변환하고, Run 01 offline Ridge
평가에서 계산된 예상 RMSE 감소를 같은 발표용 형식으로 정리한다.

## Files
- `docs/plans/2026-06-07_009_korean_run02_and_run01_presentation_summary.md`
- `experiments/results/run02_presentation_summary_2026-06-07.md`
- `experiments/results/run01_presentation_summary_2026-06-07.md`
- `experiments/results/run01_presentation_summary_2026-06-07.csv`
- `docs/daily_notes/2026-06-07.md`

## Changes
- Run 02 발표 요약 Markdown의 제목, 설명, 표 머리글, trajectory 해석과
  결론을 한국어로 변환한다.
- Run 02의 기존 수치, improvement 계산 정의와 CSV는 변경하지 않는다.
- Run 01 complete holdout 4개의 zero-prediction XY RMSE와 frozen Ridge
  prediction residual XY RMSE, 예상 감소율을 trajectory별로 정리한다.
- Run 01 complete holdout macro 동일가중 결과와 main OOF 결과를
  기록한다.
- Partial Circle은 complete holdout 공식 평균에서 제외하고 별도
  diagnostic으로 표시한다.
- Run 01 offline residual 감소는 실제 controller correction ON 성능이
  아니며 Run 02 실측 결과와 직접 동일시할 수 없다는 제한을 명시한다.

## Impact
- 발표용 Markdown/CSV와 작업 기록만 추가 또는 갱신한다.
- 기존 Run 01/02 JSON, 모델, raw/processed CSV, 코드, 데이터 contract와
  시스템 인터페이스는 변경하지 않는다.

## Risk
- Run 01 Ridge residual RMSE를 실제 위치 tracking RMSE로 표현하면
  offline estimator 성능을 과대 해석할 수 있다.
- Run 01 complete holdout은 trajectory별 1개 run뿐이고 alignment 결함
  수정 후 재평가한 retrospective 결과다.
- Partial Circle은 완전한 trajectory coverage가 아니므로 complete
  holdout macro 평균에 포함할 수 없다.

## Validation
- Run 02 Markdown의 모든 표 수치가 기존 CSV와 일치하는지 확인한다.
- Run 01 trajectory별 값과 complete macro 값이
  `ridge_run01_holdout_2026-06-06.json`과 일치하는지 확인한다.
- Run 01 main OOF RMSE와 alpha가
  `ridge_run01_main_cv_2026-06-06.json`과 일치하는지 확인한다.
- Run 01 CSV에 complete holdout 4행, complete macro 1행, partial Circle
  1행이 포함되는지 확인한다.
- 원본 JSON과 processed CSV가 변경되지 않았는지 확인한다.
