# Plan

## Goal
추가 하드웨어 실험 없이 기존 Run 02 artifact만 사용해 trajectory별
OFF/ON `tracking_xy_rmse`와 핵심 진단 결과를 발표용 요약으로 정리한다.

## Files
- `docs/plans/2026-06-07_008_run02_presentation_summary.md`
- `experiments/results/run02_presentation_summary_2026-06-07.md`
- `experiments/results/run02_presentation_summary_2026-06-07.csv`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 공식 absolute RMSE와 home-normalized RMSE의 trajectory별 OFF mean,
  ON mean, improvement percent, improved pair count를 표로 작성한다.
- 네 trajectory 동일가중 전체 평균을 absolute와 home-normalized 각각
  기록한다.
- Diamond, reverse grid, cross, circle의 결과를 반복 일관성, home
  offset 의존성, integer actuator command 해상도, radial/tangential 및
  phase lag 관점에서 발표용 bullet로 정리한다.
- CSV에는 두 analysis scope의 trajectory 행과 overall 행을 함께
  기록한다.
- improvement percent는 표에 표시된 평균과 일관되도록
  `100 * (OFF mean - ON mean) / OFF mean`으로 계산한다.

## Impact
- 발표용 Markdown/CSV와 작업 기록만 추가한다.
- 기존 comparison/reanalysis JSON, raw/processed CSV, 코드, 데이터
  contract와 시스템 인터페이스는 변경하지 않는다.

## Risk
- home-normalized 결과만 제시하면 절대 위치 오차를 숨길 수 있으므로
  official absolute 결과와 항상 함께 제시한다.
- 기존 comparison JSON의 `improvement_percent_mean`은 pair별 percent의
  산술평균이므로 평균 RMSE에서 다시 계산한 발표 표 percent와 다를 수
  있다. 두 정의를 혼용하지 않도록 주석을 포함한다.
- 전체 동일가중 평균은 trajectory별 상반된 결과를 가릴 수 있으므로
  결론은 trajectory별 결과와 improved pair count를 중심으로 작성한다.

## Validation
- 두 source JSON 외의 새 실험 데이터를 사용하지 않았는지 확인한다.
- absolute 값이 official comparison/reanalysis artifact의 trajectory
  mean과 일치하는지 확인한다.
- home-normalized 값과 circle/actuator 진단값이 reanalysis artifact와
  일치하는지 확인한다.
- CSV의 두 scope에 trajectory 4행과 overall 1행씩 총 10개 data row가
  있는지 확인한다.
- Markdown 표와 CSV의 OFF/ON mean, improvement percent, improved pair
  count가 일치하는지 확인한다.
