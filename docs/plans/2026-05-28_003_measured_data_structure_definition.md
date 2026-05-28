# Plan

## Goal
실제 measured data를 받기 전에 raw log와 processed merged dataset의 구조를 먼저 정의한다. 목적은 `error_*`를 raw Simscape export에서 임시로 계산하지 않고, 실제 측정 데이터와 simulation output이 post-alignment된 뒤 일관된 방식으로 생성하기 위한 기준을 만드는 것이다.

## Files
- `docs/plans/2026-05-28_003_measured_data_structure_definition.md`
- `docs/daily_notes/2026-05-28.md`

후속 문서화 대상:
- `docs/system_data_flow.md`
- `docs/vision_tracking.md`
- 필요 시 신규 measured data 구조 문서

## Changes
- 이번 변경은 measured data 구조 정의를 위한 계획서 작성과 Daily Note 기록만 수행한다.
- 후속 작업에서는 아래 네 가지 데이터 계층을 구분해 문서화한다.

1. Real main log
- 목적: controller/robot 실행 중 기준 시간축과 command/measured angle을 기록한다.
- 최소 필드 후보:
  - `run_id`
  - `time`
  - `target_x`
  - `target_y`
  - `target_z`
  - `theta1_cmd`
  - `theta2_cmd`
  - `theta3_cmd`
  - `theta1_meas`
  - `theta2_meas`
  - `theta3_meas`
  - `valid`

2. Vision raw log
- 목적: XY external ground-truth를 별도 raw log로 보존한다.
- 최소 필드 후보:
  - `run_id`
  - `vision_time`
  - `vision_x`
  - `vision_y`
  - `marker_detected`
  - `frame_id`
  - `valid`
- 선택 필드 후보:
  - `marker_id`
  - `reprojection_error`
  - `confidence`
  - `video_file`

3. Angle-derived measured position
- 목적: `theta*_meas`에서 FK 또는 estimator를 통해 도출한 measured position을 기록한다.
- 초기 사용 방침:
  - `measured_z`는 이 경로를 기본 출처로 사용한다.
  - `measured_x`, `measured_y`도 계산 가능하지만 초기 XY 기준값은 vision 기반 값을 우선한다.
- 최소 필드 후보:
  - `run_id`
  - `time`
  - `measured_x_est`
  - `measured_y_est`
  - `measured_z_est`
  - `estimator_method`
  - `valid`

4. Processed merged dataset
- 목적: main log, Simscape output, vision raw log, angle-derived position을 post-alignment해 학습/평가용 row를 만든다.
- 최소 필드 후보는 현재 CSV contract의 16개 고정 컬럼을 유지한다.
  - `time`
  - `target_x`
  - `target_y`
  - `target_z`
  - `theta1_cmd`
  - `theta2_cmd`
  - `theta3_cmd`
  - `theta1_meas`
  - `theta2_meas`
  - `theta3_meas`
  - `sim_x`
  - `sim_y`
  - `sim_z`
  - `error_x`
  - `error_y`
  - `error_z`
- `error_x = measured_x_vision - sim_x`
- `error_y = measured_y_vision - sim_y`
- `error_z = measured_z_est - sim_z`
- `error_z`는 angle-derived estimate 기반이므로 초기 성능 해석에서 XY ground-truth error와 분리한다.

## Impact
- 실제 측정 데이터 수집 전에 raw/processed 데이터 계층이 분리된다.
- `error_*` 생성 책임이 processed merged dataset 단계로 명확해진다.
- 현재 16개 컬럼 CSV contract를 유지하면서, raw log에는 필요한 별도 필드를 둘 수 있다.
- Stage 5~7 실데이터 수집 준비로 이어진다.

## Risk
- `run_id`, `valid`, `measured_*_est` 같은 raw/auxiliary 필드는 현재 final CSV contract 밖에 있으므로 저장 위치와 파일별 계약을 별도로 문서화해야 한다.
- `time`과 `vision_time`의 clock source가 불명확하면 alignment 품질이 낮아진다.
- `error_z`는 외부 ground-truth 기반이 아니므로 3D 성능 수치로 직접 해석하면 안 된다.

## Validation
- measured data 구조 문서가 `docs/system_data_flow.md`의 CSV contract와 충돌하지 않는지 확인한다.
- `docs/vision_tracking.md`의 vision raw log 필드와 중복/불일치가 없는지 확인한다.
- processed merged dataset의 16개 컬럼 순서가 현재 CSV contract와 일치하는지 확인한다.
- `error_x/y`와 `error_z`의 출처 차이가 명시되어 있는지 확인한다.
