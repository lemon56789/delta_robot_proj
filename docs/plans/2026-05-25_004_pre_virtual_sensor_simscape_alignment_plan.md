# Plan

## Goal
가상센서 baseline 모델 구현 전에 필요한 선행 작업을 정리한다. 목적은 현재 완료된 `Simscape`의 `sim_x/y/z` 계산을 Python 운동학/CSV 계약/시간 정렬 정책과 같은 의미로 고정해, 이후 `virtual_sensor/` 모델이 잘못된 좌표계나 시간축 위에서 학습되지 않도록 하는 것이다.

## Files
- `docs/plans/2026-05-25_004_pre_virtual_sensor_simscape_alignment_plan.md`
- `docs/daily_notes/2026-05-25.md`

## Changes
- 모델 구현 전 선행 작업 범위를 세 단계로 고정한다.
  - `Stage 4`: `Simscape` 결과와 Python 기준 CSV를 직접 비교해 `theta_*`, `sim_*`, `error_*` 차이를 정리한다.
  - `Stage 4`: `joint sign`, `base_frame` orientation, `sim_*` output point, unit이 현재 SoT와 일치하는지 확인하고 필요 시 문서 기준을 보강한다.
  - `Stage 4`: simulation sampling/logging 방식과 `post-alignment` 기준을 실제 실험 로그 기준으로 구체화한다.
- 비교에 사용할 기준 데이터를 명시한다.
  - `data/fake_pipeline/fake_pipeline_sample_2026-05-04_recomputed.csv`
  - `data/fake_pipeline/fake_pipeline_sample_2026-05-25_positive_theta.csv`
  - 현재 또는 후속 생성될 `Simscape` 결과 CSV
- 모델 구현 진입 조건을 명시한다.
  - `sim_x/y/z` 의미가 SoT와 충돌하지 않는다.
  - Python/Simscape 불일치 원인이 좌표계, 부호, output point, time alignment 중 어디에 있는지 분리된다.
  - `virtual_sensor` 입력 feature와 target이 같은 시간축/좌표계 기준으로 해석 가능하다.
- 오늘은 계획만 추가하고 코드/데이터 계약 변경은 수행하지 않는다.

## Impact
- `virtual_sensor` baseline 모델 작업 시작 전 필요한 확인 항목이 문서로 고정된다.
- `Stage 4`와 `Stage 8`의 경계가 분명해져, simulation path가 정리되기 전에 학습 코드를 먼저 붙이는 위험을 줄인다.
- 이후 구현 계획서를 더 작은 작업 단위로 나눌 기준점이 생긴다.

## Risk
- 현재 `docs/roadmap.md`의 status snapshot 날짜가 `2026-05-04` 기준이라 오늘 상태와 일부 어긋날 수 있다.
- `Simscape` export 형식이 아직 고정되지 않았다면 비교 절차를 바로 코드화하기 어렵다.
- 실제 hardware/vision 로그가 없으므로 time alignment 정책은 이번 단계에서 문서/실험 규칙 수준까지만 확정될 수 있다.

## Validation
- 계획서가 `모델 구현 전 선행 작업`만 다루고 있는지 확인한다.
- 계획 내용이 `docs/system_data_flow.md`, `docs/roadmap.md`, `docs/daily_notes/2026-05-25.md`의 현재 방향과 충돌하지 않는지 확인한다.
- 다음 구현 작업이 `virtual_sensor` 모델 추가가 아니라 `Simscape-Python 비교 및 simulation path 정리`로 자연스럽게 이어지는지 확인한다.
