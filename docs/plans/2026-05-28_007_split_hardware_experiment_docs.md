# Plan

## Goal
하드웨어 실험 문서를 고정 설정과 실험별 실행 프로토콜로 분리한다. 목적은 모터/Arduino/비전/로그/동기화 같은 고정값은 한 곳에서 관리하고, 실험 목적에 따라 달라지는 scope, trajectory, run procedure, validation은 실험별 문서에서 관리하는 것이다.

## Files
- `docs/plans/2026-05-28_007_split_hardware_experiment_docs.md`
- `docs/hardware_experiment_procedure.md`
- `docs/hardware_experiment_base_config.md`
- `docs/hardware_experiment_run_00_commissioning.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/hardware_experiment_run_03_final_demo.md`
- `docs/daily_notes/2026-05-28.md`
- `fulltext.md`

## Changes
- 기존 `docs/hardware_experiment_procedure.md`는 문서 구조 설명과 링크를 담은 인덱스 문서로 정리한다.
- 고정 항목은 `docs/hardware_experiment_base_config.md`로 분리한다.
- 실험별 변동 항목은 아래 문서로 분리한다.
  - `00_commissioning`: 하드웨어 커미셔닝/안전 검증
  - `01_baseline_data_collection`: 오차 학습용 baseline 데이터 수집
  - `02_corrected_comparison`: 가상센싱 보정 적용 후 비교 데이터 수집
  - `03_final_demo`: 최종 시연용 움직임
- 각 문서는 실제 값 입력 전 상태로 두고, 한국어 작성 안내를 유지한다.
- `fulltext.md`에 하드웨어 실험 문서 구조를 요약 반영한다.
- Daily Note에 변경 기록을 남긴다.

## Impact
- 고정 장비/제어/비전 설정과 실험별 실행 조건이 분리되어 중복과 혼선을 줄인다.
- 실험별 문서를 채우면 그대로 run protocol로 사용할 수 있다.
- 코드와 CSV contract 자체는 변경하지 않는다.

## Risk
- 각 run protocol에서 base config와 중복되는 항목이 생기면 이후 정리가 필요하다.
- 실제 장비 스펙이 채워지기 전에는 여전히 실행 가능한 최종 절차가 아니라 템플릿이다.

## Validation
- base config와 4개 run protocol 문서가 생성되었는지 확인한다.
- `docs/hardware_experiment_procedure.md`가 새 문서들을 참조하는지 확인한다.
- `fulltext.md`와 Daily Note가 변경을 기록하는지 확인한다.
- `git diff --check`로 포맷 문제를 확인한다.
