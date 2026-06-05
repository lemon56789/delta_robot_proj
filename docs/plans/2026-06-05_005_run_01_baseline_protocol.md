# Plan

## Goal
Run 01 baseline data collection 문서를 실제 실행 가능한 baseline dataset 수집 프로토콜로 구체화한다.

## Files
- `docs/plans/2026-06-05_005_run_01_baseline_protocol.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- Run 01을 `pre`, `main`, `holdout` 단계로 나눈다.
- Run 01-pre는 pipeline validation용으로 static, cross `±10 mm`, square `±10 mm`를 1회 실행하도록 정의한다.
- Run 01-main은 학습용 baseline dataset으로 static, cross `±20 mm`, square `±20 mm`, circle, grid 3x3을 3회 반복하도록 정의한다.
- Run 01-holdout은 Run 02 비교용으로 학습에 넣지 않는 trajectory를 별도 정의한다.
- 필수 로그, 실행 절차, 중지 조건, 실행 후 검증을 실제 실행 체크리스트로 채운다.
- `error_x/y`는 vision 기반 XY ground-truth, `error_z`는 angle-derived estimate 기반이라는 해석 제한을 명시한다.

## Impact
- 문서 프로토콜만 변경한다.
- CSV final contract, 코드, 제어 인터페이스, raw data는 변경하지 않는다.
- Run 02 comparison과 virtual sensor training split의 기준이 Run 01 문서에 고정된다.

## Risk
- 실제 logger, Simscape export, merge script가 아직 완성되지 않았으면 Run 01-pre에서 blocker가 발생할 수 있다.
- 15회 이상의 Run 01-main 반복은 시간 부담이 있으므로, Run 01-pre 통과 후 실행량을 조정해야 한다.
- Holdout trajectory를 학습에 섞으면 Run 02 비교 의미가 약해진다.

## Validation
- Run 01 문서가 placeholder 없이 실행 가능한 절차와 판정 기준을 포함하는지 확인한다.
- `docs/measured_data_structure.md`의 raw/processed 계층과 final CSV 16컬럼 계약을 위반하지 않는지 확인한다.
- Daily Note에 무엇을/왜/어떻게/결과/변경 파일/다음 작업을 기록한다.
- `git diff --check`로 문서 공백 오류를 확인한다.
