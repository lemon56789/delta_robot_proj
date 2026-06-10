# Plan

## Goal
Run 02의 24개 raw main/vision/correction log와 네 개 nominal Simscape
CSV를 정렬·병합하고, 12개 OFF/ON pair의 XY tracking 성능을 비교한다.

## Files
- `docs/plans/2026-06-07_002_run02_preprocess_and_comparison.md`
- `experiments/run02_preprocess.py`
- `experiments/test_run02_preprocess.py`
- `experiments/README.md`
- `data/real/derived/measured_position_<run_id>.csv` 24개
- `data/processed/merged_<run_id>.csv` 24개
- `data/processed/alignment_<run_id>.json` 24개
- `experiments/results/run02_comparison_2026-06-07.json`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- step trajectory의 vision 위치 jump를 main phase 전환과 대응시켜 단일
  offset alignment를 수행한다.
- circle start hold departure를 원운동 시작 `t=0` anchor로 사용하고 end
  hold 검출을 검증한다.
- 유효 vision sample 사이의 짧은 구간만 보간해 fixed 16-column merged
  dataset을 생성한다.
- command echo angle의 FK measured-position auxiliary CSV를 생성한다.
- 동일 trajectory/repetition의 OFF/ON 공통 timestamp에서 tracking
  RMSE, MAE, max error를 비교한다.
- trajectory별 세 repetition과 전체 trajectory 동일가중 summary를
  JSON으로 저장한다.

## Impact
- raw main/vision/correction CSV와 nominal Simscape CSV는 변경하지 않는다.
- processed fixed 16-column contract와 기존 error 의미를 유지한다.
- 새 전처리 코드, 테스트, derived/processed/result output이 추가된다.

## Risk
- 잘못 검출된 vision jump를 phase 전환으로 사용하면 시간 정렬과 metric이
  왜곡될 수 있다.
- marker loss 구간을 과도하게 보간하면 실제 관측되지 않은 위치를
  성능 계산에 포함할 수 있다.
- OFF/ON의 서로 다른 timestamp 집합을 그대로 비교하면 sample coverage
  차이가 metric 차이로 나타날 수 있다.

## Validation
- synthetic unit test로 step/circle anchor 검출과 interpolation gap 제한을
  검증한다.
- 24개 run에서 expected event count, anchor residual, circle end hold,
  main/Simscape exact time axis를 확인한다.
- 모든 merged CSV의 16-column, finite value, monotonic timestamp를
  검사한다.
- 12개 pair가 같은 timestamp intersection으로 비교되는지 확인한다.
- comparison JSON에 run, pair, trajectory, overall summary가 모두
  기록되는지 확인한다.
