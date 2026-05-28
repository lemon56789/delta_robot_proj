# Plan

## Goal
`run_fake_pipeline_simscape.m`의 `error_*` 처리 방향을 SoT 의미와 충돌하지 않도록 정리하고, 추후 `error_* = measured_position - sim_position`을 계산하기 위해 필요한 `measured_position` 데이터 확보 경로를 정의한다.

현재 SoT에서 `error_x`, `error_y`, `error_z`는 correction field이며 의미는 `measured_position - sim_position`이다. 반면 현재 Simscape export는 `target_position - sim_position`을 diagnostic 값으로 `error_*`에 기록하고 있으므로, 이 값이 학습 라벨 또는 계약 필드로 오해되지 않도록 분리해야 한다.

## Files
- `docs/plans/2026-05-28_002_simscape_error_semantics_and_measured_position_plan.md`
- `docs/daily_notes/2026-05-28.md`
- `docs/system_data_flow.md`

후속 구현 또는 문서 보강 시 검토 대상:
- `simulation/simulink/run_fake_pipeline_simscape.m`
- `simulation/simulink/model_notes.md`
- `docs/system_data_flow.md`
- `docs/vision_tracking.md`

## Changes
- 이번 변경은 우선 계획서 작성과 Daily Note 기록만 수행한다.
- `docs/system_data_flow.md`에 `error_*`는 raw Simscape export가 아니라 measured data가 정렬된 processed/merged dataset 단계에서 생성한다는 기준을 짧게 반영한다.
- 후속 작업의 우선순위는 `run_fake_pipeline_simscape.m` 수정이 아니라 실제 measured data 구조 정의로 전환한다.
- `target_position - sim_position`이 필요하면 계약 필드인 `error_*`가 아니라 diagnostic으로만 취급한다. 단, 현재 CSV 고정 계약에 optional column 정책이 비어 있으므로 새 컬럼 추가는 별도 Contract Change 검토가 필요하다.
- `measured_position` 확보 경로를 아래 기준으로 정리한다.

### measured_position 데이터 확보 방안
초기 학습 및 검증 단계의 `measured_position`은 운영 센서가 아니라 외부 ground-truth 또는 후처리 추정값으로 확보한다.

1. XY measured position
- 기본 출처: top-view vision log의 `vision_x`, `vision_y`
- 저장 위치: `data/vision/raw/vision_<run_id>.csv`
- 좌표계: `base_frame`
- 단위: `mm`
- 전처리: camera calibration, lens distortion correction, homography 또는 동등한 평면 좌표 변환
- 정렬: `vision_time`을 PC logger 기준 시간축 또는 공통 이벤트 기준으로 main log와 post-alignment
- 병합 결과: 정렬된 row마다 `measured_x`, `measured_y`로 사용할 수 있다.

2. Z measured position
- 현재 top-view 단일 웹캠 구성에서는 Z ground-truth를 별도로 측정하지 않는다.
- 초기 기준에서는 `theta*_meas`로부터 FK 또는 estimator를 통해 도출한 Z 값을 `measured_z`로 사용한다.
- 이 `measured_z`는 별도 외부 ground-truth가 아니라 angle-derived estimate이므로, 문서와 실험 로그에서 그 출처를 명확히 남긴다.
- 초기 평가와 학습 해석의 주축은 `x-y` 오차로 둔다. `error_z = measured_z - sim_z`는 보조 label 또는 diagnostic 성격으로 취급한다.

3. theta-based measured position
- `theta*_meas`만으로 FK를 수행해 얻는 위치는 실제 엔드이펙터 외부 ground-truth가 아니라 encoder/estimator 기반 위치 추정값이다.
- 이 값은 Z 방향 `measured_z`의 초기 출처로 사용한다.
- XY도 계산할 수는 있지만, 초기 XY 기준값은 vision 기반 `measured_x/y`를 우선한다.
- 사용할 경우 실험 메타데이터에 estimator-derived position임을 기록한다.

4. merged dataset 생성 원칙
- main CSV의 `time`, `target_*`, `theta*_cmd`, `theta*_meas`, `sim_*`를 기준 데이터로 둔다.
- vision raw log는 메인 CSV에 실시간으로 섞지 않고 후처리에서 정렬한다.
- 정렬 후 `measured_x`, `measured_y`를 계산하고, 유효한 측정 row에 대해서만 `error_x = measured_x - sim_x`, `error_y = measured_y - sim_y`를 계산한다.
- `measured_z`는 `theta*_meas` 기반 FK 또는 estimator에서 도출하고, `error_z = measured_z - sim_z`로 계산한다.
- 단, `error_z`는 외부 ground-truth 기반 label이 아니므로 초기 성능 판단에서는 XY 결과와 분리해 해석한다.
- marker miss, timestamp 누락, calibration 실패 row는 invalid로 분류하고 학습/평가에서 제외한다.

## Impact
- Stage 4 simulation/data path에서 `error_*` 의미 혼동을 줄인다.
- Stage 5~7의 real log, vision ground-truth, alignment 준비 작업과 직접 연결된다.
- Stage 8 가상센서 학습 전에 label 정의가 흔들리는 위험을 줄인다.
- 이번 계획서 자체는 코드, CSV 계약, 폴더 구조를 변경하지 않는다.
- `error_*` 생성 책임을 raw simulation export가 아니라 measured/sim/vision 병합 이후의 processed dataset 단계로 이동시킨다.

## Risk
- `measured_z`가 angle-derived estimate이므로 실제 Z 위치 오차와 estimator 오차가 분리되지 않을 수 있다.
- optional diagnostic column을 추가하려면 CSV contract와 loader 영향 검토가 필요하다.
- vision 기반 `measured_x/y`는 calibration 품질, marker detection 품질, timestamp alignment 품질에 영향을 받는다.
- `theta*_meas` 기반 FK 위치를 외부 ground-truth처럼 해석하면 실제 구조 오차와 encoder/estimator 오차가 섞여 label 품질을 과대평가할 수 있다.

## Validation
- `docs/system_data_flow.md`의 `error_* = measured_position - sim_position` 의미와 계획서가 충돌하지 않는지 확인한다.
- `docs/vision_tracking.md`의 vision output이 `measured_x/y` 확보 경로와 일치하는지 확인한다.
- `docs/system_data_flow.md`에 `error_*` 생성 시점이 processed merge 단계로 기록되었는지 확인한다.
- 후속 데이터 병합 시 invalid row, marker miss row, timestamp 누락 row가 학습/평가에서 제외되는지 확인한다.
