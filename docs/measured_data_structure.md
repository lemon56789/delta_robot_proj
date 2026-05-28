# Measured Data Structure

이 문서는 실제 측정 데이터 수집 전에 raw log, estimator-derived position, processed merged dataset의 구조를 정의한다. 목적은 `error_*`를 raw simulation export에서 임시로 계산하지 않고, measured data와 simulation output이 post-alignment된 뒤 일관된 방식으로 생성하는 것이다.

## 1. Scope
- 본 문서는 Stage 5~7 실데이터 수집 준비를 위한 데이터 계층과 필드 구조를 정의한다.
- 최종 학습/평가용 processed dataset은 `docs/system_data_flow.md`의 16개 CSV contract를 따른다.
- raw log와 auxiliary log는 processed dataset 생성을 위한 입력이며, final CSV contract와 분리한다.
- 모든 position field는 `base_frame` 기준 `mm` 단위를 사용한다.
- 모든 angle field는 `deg` 단위를 사용한다.

## 2. Data Layers
실제 데이터는 아래 네 계층으로 분리한다.

1. Real main log
- controller/robot 실행 중 기준 시간축, target, command angle, measured angle을 기록한다.
- processed merged dataset의 주 시간축 후보가 된다.

2. Vision raw log
- 외부 비전 기반 XY ground-truth를 별도 raw log로 기록한다.
- 메인 CSV에 실시간으로 섞지 않고, post-alignment 단계에서 병합한다.

3. Angle-derived measured position
- `theta*_meas`에서 FK 또는 estimator를 통해 도출한 measured position estimate이다.
- 초기 기준에서 `measured_z_est`의 기본 출처다.
- `measured_x_est`, `measured_y_est`도 계산 가능하지만 초기 XY 기준값은 vision 기반 값을 우선한다.

4. Processed merged dataset
- real main log, Simscape output, vision raw log, angle-derived measured position을 정렬한 학습/평가용 dataset이다.
- 이 단계에서만 contract-compliant `error_*`를 생성한다.

## 3. Real Main Log
### Purpose
실제 구동 중 controller/robot 기준 데이터를 보존한다.

### Path Convention
- raw main log 저장 위치는 후속 hardware logger 구현에서 확정한다.
- 권장 파일명 형식은 `main_<run_id>.csv`다.

### Minimum Fields
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

### Field Notes
- `time`은 `boot_ms` 의미를 유지한다.
- `theta*_cmd`와 `theta*_meas`는 `deg` 단위다.
- `valid=false` row는 post-alignment와 학습/평가에서 제외한다.

## 4. Vision Raw Log
### Purpose
외부 비전 기반 XY ground-truth를 raw 기준으로 보존한다.

### Path Convention
- 저장 위치: `data/vision/raw/`
- 파일명 형식: `vision_<run_id>.csv`

### Minimum Fields
- `run_id`
- `vision_time`
- `vision_x`
- `vision_y`
- `marker_detected`
- `frame_id`
- `valid`

### Optional Fields
- `marker_id`
- `reprojection_error`
- `confidence`
- `video_file`

### Field Notes
- `vision_x`, `vision_y`는 calibration과 homography 이후 `base_frame` 기준 `mm` 값이다.
- `marker_detected=false` row는 기본적으로 `valid=false`로 처리한다.
- `vision_time`은 후처리에서 `time` 기준축과 정렬된다.

## 5. Angle-Derived Measured Position
### Purpose
`theta*_meas`에서 FK 또는 estimator를 통해 position estimate를 생성한다.

### Minimum Fields
- `run_id`
- `time`
- `measured_x_est`
- `measured_y_est`
- `measured_z_est`
- `estimator_method`
- `valid`

### Field Notes
- `measured_z_est`는 초기 `measured_z`의 기본 출처다.
- `measured_x_est`, `measured_y_est`는 보조 추정값이며, 초기 XY ground-truth는 vision 기반 `vision_x/y`를 우선한다.
- 이 계층은 외부 ground-truth가 아니라 angle-derived estimate이다.
- `estimator_method`에는 사용한 FK 함수 또는 estimator 이름과 버전을 기록한다.

## 6. Processed Merged Dataset
### Purpose
학습/평가에 사용하는 최종 row-level dataset을 생성한다.

### Fixed Column Order
현재 final CSV contract의 16개 컬럼 순서를 유지한다.

1. `time`
2. `target_x`
3. `target_y`
4. `target_z`
5. `theta1_cmd`
6. `theta2_cmd`
7. `theta3_cmd`
8. `theta1_meas`
9. `theta2_meas`
10. `theta3_meas`
11. `sim_x`
12. `sim_y`
13. `sim_z`
14. `error_x`
15. `error_y`
16. `error_z`

### Error Generation
- `error_x = measured_x_vision - sim_x`
- `error_y = measured_y_vision - sim_y`
- `error_z = measured_z_est - sim_z`

### Interpretation
- `error_x`와 `error_y`는 vision 기반 XY ground-truth에서 생성한다.
- `error_z`는 angle-derived estimate 기반이므로 외부 ground-truth 기반 3D 성능 수치로 해석하지 않는다.
- 초기 성능 판단은 XY 결과를 주축으로 하고, Z는 보조 label 또는 diagnostic으로 분리해 해석한다.

## 7. Alignment Policy
- main log의 `time`을 기본 alignment 기준축으로 사용한다.
- vision log의 `vision_time`은 post-alignment로 `time` 기준축에 매핑한다.
- Simscape output은 같은 target/command trajectory 기준으로 `time`에 보간한다.
- 현재 fake pipeline comparison에서 관찰된 `20 ms` lag는 provisional이며, real hardware log에서 재검증한다.
- timestamp 누락, marker miss, invalid row는 processed merged dataset에서 제외한다.

## 8. Open Questions
1. real main log의 실제 저장 경로를 어디로 고정할 것인가?
2. `theta*_meas`의 실제 출처를 encoder로 둘 것인가, 초기에는 estimation으로 둘 것인가?
3. `estimator_method` 기록 형식을 어떤 문자열 규칙으로 고정할 것인가?
4. processed merged dataset의 저장 경로와 파일명 규칙을 어떻게 둘 것인가?
