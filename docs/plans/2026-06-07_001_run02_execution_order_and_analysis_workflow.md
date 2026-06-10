# Plan

## Goal
Run 02 문서를 실제 수행한 trajectory별 반복 순서에 맞추고, circle의
출발 시점 기준 정렬 정책과 raw data 이후 OFF/ON 성능 분석 절차를
명확히 기록한다.

## Files
- `docs/plans/2026-06-07_001_run02_execution_order_and_analysis_workflow.md`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 실제 실행 순서를 trajectory별 `r01 -> r03`, 각 반복의 `OFF -> ON`
  순서로 수정한다.
- Run 02 데이터의 실제 실험일은 2026-06-07이지만 기존 run ID와
  calibration ID의 2026-06-06 표기를 식별자로 유지한 배경을 기록한다.
- circle은 시작점 hold를 벗어나는 출발 시점을 공통 `t=0` anchor로
  정의하고 실제 timestamp 간격을 보존하도록 명시한다.
- raw validation, alignment, processed dataset 생성, run별 metric,
  paired OFF/ON 비교, repetition 집계와 결과 저장 순서를 정리한다.

## Impact
- 문서와 작업 기록만 변경한다.
- raw CSV, calibration file, logger code, processed CSV contract와 제어
  인터페이스는 변경하지 않는다.

## Risk
- circle 시간을 고정 10 Hz로 재생성하면 실제 움직임의 시간 특성이
  왜곡될 수 있다.
- OFF/ON을 repetition 번호가 아닌 파일 순서로 pairing하면 잘못된
  비교가 발생할 수 있다.
- vision invalid row와 marker loss 구간을 보간에 포함하면 metric이
  왜곡될 수 있다.

## Validation
- 문서의 실행 순서가 실제 수집 순서와 일치하는지 확인한다.
- circle 정렬이 단일 출발 anchor와 실제 timestamp 보존을 모두
  명시하는지 확인한다.
- 분석 절차가 24개 raw run부터 trajectory별 paired 결과까지 누락 없이
  이어지는지 확인한다.
- 변경 파일과 결과를 Daily Note에 기록한다.
