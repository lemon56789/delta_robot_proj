# System Data Flow

이 문서는 델타 로봇 프로젝트에서 목표 궤적, 역기구학, 제어, 실물 데이터, 시뮬레이션 데이터, 가상센싱, 보정값이 어떻게 연결되는지 정의한다.
모든 팀원은 구현 전에 이 문서의 데이터 흐름과 인터페이스를 기준으로 작업한다.

## 0. Meta
- 작성일: 2026-03-26
- 작성자: 이진성(L)
- 버전: v0.1-draft
- 관련 문서(SoT): AGENTS.md, README.md

## 1. Units & Coordinate Frame
- position unit: `mm`
- angle unit: `deg`
- coordinate frame name: `base_frame`
- origin definition: `base center (O)`
- +x direction: direction rotated 90 degrees counterclockwise from `B1` around `O`
- +y direction: opposite direction of `O -> B1`
- +z direction: direction coming out through the base
- workspace direction: `-z`
- right-hand rule 사용 여부: `yes`
- 비고: 모든 position-related fields는 `base_frame` 기준으로 기록한다. `sB`는 base 정삼각형의 변 길이, `sP`는 platform 정삼각형의 변 길이, `uB`는 base 중심에서 꼭짓점까지의 길이, `uP`는 platform 중심에서 꼭짓점까지의 길이, `wB`는 base 중심에서 변까지의 길이, `wP`는 platform 중심에서 변까지의 길이, `L`은 link arm length, `l`은 crank의 parallelogram length를 의미한다. `B1`, `B2`, `B3`는 `sB` 각 변의 중심에 위치한 step motor 위치이며, `B1`은 `O`에서 `-y` 방향으로 향할 때 만나는 점이고 이후 반시계방향으로 `B2`, `B3`가 배치된다. `P1`, `P2`, `P3`는 각각 `B1`, `B2`, `B3`에 연결된 platform 점이며 `sP`의 꼭짓점이다.

## 2. Timestamp Policy
- timestamp field name: `time`
- timestamp source: `both`
- format: `boot_ms`
- resolution: `ms`
- sync method: Arduino와 PC logger가 각각 timestamp를 기록하고, 이후 `post-alignment`로 정렬한다.
- timezone handling: `boot_ms` 기준이므로 not applicable
- missing timestamp 처리 규칙: 해당 row는 `invalid`로 표기하고 후처리에서 제외한다.

## 3. IK Interface Contract
- input fields (order fixed):
  1. `target_x`
  2. `target_y`
  3. `target_z`
- output fields (order fixed):
  1. `theta1_cmd`
  2. `theta2_cmd`
  3. `theta3_cmd`
- input range limits:
- output angle limits:
- fail behavior: `reject`
- notes: 입력 position은 `base_frame` 기준이며 unit은 `mm`이다. 출력 angle unit은 `deg`이다. `theta_i`는 arm `i`의 local actuation plane에서 정의되는 upper arm 회전각이다. `theta_i = 0 deg`는 upper arm이 `base plane`에 놓인 자세이고, `theta_i = +90 deg`는 upper arm이 workspace direction인 `-z` 방향과 평행한 자세다. `theta_i`의 양의 방향은 upper arm이 `base plane`에서 workspace 방향으로 내려가는 회전 방향이다.

## 4. Real Measurement Definition
- theta_meas source: (`encoder` / `estimation`)
- sensor model/name:
- sampling rate (Hz):
- expected noise level:
- calibration method:
- dropout handling:
- notes:

## 5. Simulation Path Definition
- primary simulation source: `Simscape`
- simulation input fields:
  1. `target_x`
  2. `target_y`
  3. `target_z`
- simulation output fields:
  1. `sim_x`
  2. `sim_y`
  3. `sim_z`
- simulation step/sampling rate:
- parameter source (geometry, mass, friction):
- notes: `RecurDyn` result may be used later as a secondary reference for cross-checking, but the current system data flow is defined around `Simscape`.

## 6. Real-Sim Alignment Policy
- alignment reference clock: `PC logger`
- resampling method: `linear interpolation`
- delay compensation method: `post-alignment`
- comparison window:
- outlier handling: rows marked as `invalid` are excluded from alignment and comparison
- notes: `PC logger` time is used as the alignment reference for merged dataset generation, but it may include serial communication delay.

## 7. Correction Injection Point (Single Policy)
- correction target: `target_position`
- correction fields:
  1. `error_x`
  2. `error_y`
  3. `error_z`
- application timing: (예: each control tick)
- safety limits/clamps:
- fallback when correction unavailable: use uncorrected target position
- notes: `error_x`, `error_y`, `error_z` are the estimated position-domain correction terms applied to the target position.

## 8. CSV Contract (Final)
- file path convention:
- encoding:
- delimiter:
- header required: `yes`
- fixed column order:
  1. time
  2. target_x
  3. target_y
  4. target_z
  5. theta1_cmd
  6. theta2_cmd
  7. theta3_cmd
  8. theta1_meas
  9. theta2_meas
  10. theta3_meas
  11. sim_x
  12. sim_y
  13. sim_z
  14. error_x
  15. error_y
  16. error_z
- required columns:
- optional columns:
- current SoT 대비 변경 여부: `contract_change`
- contract change detail (if any): 기존 AGENTS 예시의 `motor*_cmd`, `motor*_meas` 명명 대신 `theta*_cmd`, `theta*_meas`를 사용하고, correction-related field는 `corr_*` 대신 `error_*`를 사용한다.

## 9. Owner Mapping
- S = dynamics analysis, vibration analysis
- L = system integration, virtual sensing
- Y = Arduino control
- T = mechanical design
- Team = shared ownership across all members
- block별 owner:
  - Target Trajectory Generator: Team
  - Inverse Kinematics: S, L
  - Arduino Controller: Y
  - Delta Robot Hardware: T, Y
  - Data Logger: Y, L
  - Simulation Model: S, L
  - Virtual Sensor: L
  - Feedback Controller: L, Y

## 10. Validation Criteria
- primary metrics: `RMSE_x`, `RMSE_y`, `RMSE_z`, `max_error`
- pass/fail thresholds:
- test dataset IDs:
- fixed test conditions:
- experiment command/log policy: 모든 실험은 실행 커맨드, 데이터셋, 파라미터, 코드 버전을 함께 기록한다.
- reproducibility checklist:
  1. 실행 커맨드 기록
  2. 사용 데이터 기록
  3. 파라미터 및 코드 버전 기록

## 11. Open Questions
1. `theta_meas`는 encoder 실측값으로 취득할 것인가, estimation으로 시작할 것인가?
2. simulation step/sampling rate는 최종적으로 얼마로 고정할 것인가?
3. correction safety limits/clamps는 어떤 범위로 제한할 것인가?
4. CSV file path convention과 optional columns는 어떻게 정할 것인가?
