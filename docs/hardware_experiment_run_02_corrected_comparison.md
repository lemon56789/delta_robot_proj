# Hardware Experiment Run 02 - Corrected Comparison

이 문서는 가상센싱 보정을 적용한 뒤 baseline 데이터와 비교할 검증 데이터를 수집하기 위한 run protocol이다.

## 1. Experiment Scope
- experiment purpose: (작성: 보정 적용 후 baseline 대비 성능 개선을 확인하는 목적을 적는다)
- expected output: (작성: corrected main CSV, vision CSV, processed dataset, comparison report 등 산출물을 적는다)
- target stage: (작성: Stage 9 폐루프 적용 및 성능 검증 등으로 적는다)
- responsible members: (작성: 실험 진행, virtual sensor, Arduino, vision, data analysis 담당자를 적는다)
- date: (작성: 실험 수행일을 `YYYY-MM-DD`로 적는다)
- run_id: (작성: 이번 run 식별자를 적는다)
- baseline run_id: (작성: 비교 대상 baseline run_id를 적는다)
- correction enabled: (작성: corrected run이므로 원칙적으로 `yes`)

## 2. Correction Setup
- virtual sensor model:
  `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`, alpha `100`,
  Run 01-main 15 runs / `5,158` rows
- correction input fields: artifact order의 `theta1_cmd`, `theta2_cmd`,
  `theta3_cmd`, `theta1_meas`, `theta2_meas`, `theta3_meas`, `sim_x`,
  `sim_y`, `sim_z`
- correction output fields: predicted `error_x/y/z`; 제어 적용은 XY만 사용
- correction injection point:
  `corrected_target_xy = target_xy - gain * predicted_error_xy`, 이후 IK
- safety clamp: XY vector norm clamp. 초기 hardware gate 후보는 gain
  `0.25`, clamp `2 mm`이며 최종 실행값은 hardware gate 전에 고정한다.
- fallback behavior: feature/inference 오류 또는 corrected-target IK reject
  시 uncorrected target과 nominal theta command 사용
- Z policy: `error_z`는 diagnostic으로만 기록하고 Z correction은 적용하지
  않는다.
- current control classification: `theta*_meas=command_echo_no_encoder`이므로
  encoder feedback closed loop가 아닌 PC-side feedforward correction이다.

### 2-A. Offline Preparation Result

- command: `python3 experiments/run02_offline_validate.py`
- report:
  `experiments/results/run02_correction_offline_validation_2026-06-06.json`
- input: Run 01-main 15 runs / `5,158` rows, complete holdout 4 runs /
  `1,356` rows
- candidates: gain `0.25/0.5/1.0` x XY clamp `2/4/6 mm`
- 모든 후보에서 fallback, correction limit violation, theta limit
  violation은 `0`
- corrected theta 전체 범위: 약 `-11.467 deg` to `16.501 deg`
- provisional hardware start candidate:
  - gain `0.25`
  - XY vector clamp `2 mm`
  - main clamp `4/5,158` rows (`0.077549%`)
  - holdout clamp `0/1,356` rows
- holdout의 `error_*` label은 설정 선택에 사용하지 않았다. 이 결과는
  수치/IK 안전성 검증이며 실제 성능 개선 검증은 아니다.

### 2-B. Correction Auxiliary Log Fields

Run 02 serial-enabled logger는 fixed 16-column processed CSV와 별도로 다음
auxiliary correction log를 남긴다.

- `run_id`, `time`
- `target_x`, `target_y`, `target_z`
- `predicted_error_x`, `predicted_error_y`, `predicted_error_z`
- `requested_correction_x`, `requested_correction_y`,
  `requested_correction_z`
- `applied_correction_x`, `applied_correction_y`, `applied_correction_z`
- `corrected_target_x`, `corrected_target_y`, `corrected_target_z`
- `corrected_theta1`, `corrected_theta2`, `corrected_theta3`
- `correction_gain`, `max_xy_correction_mm`
- `correction_clamped`, `fallback_used`, `correction_status`

이 auxiliary log는 processed merged dataset의 fixed 16-column contract를
변경하지 않는다.

## 3. Trajectory

### 3-A. Optional 24-Run Candidate

아래 구성은 재사용을 위해 기록한 candidate이며 아직 최종 Run 02 실행
구성으로 확정하지 않았다.

| trajectory | correction state | repetitions | run count |
|---|---|---:|---:|
| cross `+/-30 mm` | OFF / ON | 상태별 3회 | 6 |
| reverse grid 3x3 `+/-40 mm` | OFF / ON | 상태별 3회 | 6 |
| diamond `+/-35 mm` | OFF / ON | 상태별 3회 | 6 |
| circle `r=40 mm` | OFF / ON | 상태별 3회 | 6 |
| **total** | | | **24** |

계산: 4 trajectories x 2 correction states x 3 repetitions = 24 runs.

### 3-B. Waypoint and Direction Definitions

모든 좌표 단위는 `mm`이며 XY 좌표만 아래에 표시한다. Z는 Run 02 실행
전에 확정한 공통 `target_z`를 유지한다.

#### Cross `+/-30 mm`

기존 `cross_pm30_holdout` 순서를 유지한다.

```text
home
-> (30, 0)
-> home
-> (-30, 0)
-> home
-> (0, 30)
-> home
-> (0, -30)
-> home
```

#### Reverse Grid 3x3 `+/-40 mm`

기존 `grid_3x3_pm40` waypoint 목록의 정확한 역순이다. 기존 경로와
마찬가지로 row 전환 시 긴 대각 이동이 포함되며 serpentine 경로가 아니다.

```text
home
-> (40, 40)
-> (0, 40)
-> (-40, 40)
-> (40, 0)
-> (0, 0)
-> (-40, 0)
-> (40, -40)
-> (0, -40)
-> (-40, -40)
-> home
```

#### Diamond `+/-35 mm`

`(35, 0)`에서 시작해 `base_frame` 기준 반시계 방향으로 한 바퀴 이동한다.

```text
home
-> (35, 0)
-> (0, 35)
-> (-35, 0)
-> (0, -35)
-> (35, 0)
-> home
```

#### Circle `r=40 mm`

기존 circle 정의와 동일하게 `(40, 0)`에서 시작해 반시계 방향으로 한
바퀴 이동한다.

```text
home
-> (40, 0)
-> counterclockwise radius-40 circle
-> home
```

### 3-C. Items to Freeze Before Implementation

- optional candidate 사용 여부
- 공통 `target_z`
- waypoint hold time
- circle duration과 point count
- command/sample rate
- OFF/ON 실행 순서
- run_id와 repetition naming
- max velocity/acceleration 및 예상 theta 범위

## 4. Required Logs
- corrected main log: (작성: correction on 상태의 main log 경로를 적는다)
- vision raw log: (작성: corrected run의 vision CSV 경로를 적는다)
- correction log: (작성: model input/output, clamp 여부, fallback 여부를 저장할 로그 경로를 적는다)
- angle-derived position log: (작성: `measured_z_est` 생성 로그 경로를 적는다)
- processed merged dataset: (작성: corrected processed dataset 경로를 적는다)
- comparison report: (작성: baseline 대비 비교 결과 저장 경로를 적는다)

## 5. Run Procedure
1. Assign `run_id`: (작성: corrected run_id를 정한다)
2. Load baseline reference: (작성: 비교 대상 baseline run_id와 dataset을 확인한다)
3. Load virtual sensor model: (작성: 모델 파일과 설정을 로드한다)
4. Power on and zero: (작성: 전원 인가와 zeroing 수행 결과를 적는다)
5. Start main logger: (작성: main logger 시작 명령과 저장 파일을 적는다)
6. Start vision logger: (작성: vision logger 시작 명령과 저장 파일을 적는다)
7. Start correction logger: (작성: correction log 시작 방법을 적는다)
8. Trigger common start event: (작성: 정렬용 공통 시작 이벤트를 적는다)
9. Execute corrected trajectory: (작성: correction on 상태의 trajectory 실행 명령을 적는다)
10. Trigger common stop event: (작성: 정렬용 공통 종료 이벤트를 적는다)
11. Stop loggers: (작성: logger 종료와 파일 저장 확인 방법을 적는다)
12. Generate processed merged dataset: (작성: alignment와 merge 실행 방법을 적는다)
13. Compare against baseline: (작성: RMSE, max error, trajectory error 비교 방법을 적는다)
14. Save run metadata: (작성: metadata 저장 위치를 적는다)

## 6. Run-Specific Stop Conditions
- use base stop conditions: (작성: base config의 공통 중지 조건을 적용하는지 적는다)
- correction clamp exceeded: (작성: correction이 어느 기준을 넘으면 중지할지 적는다)
- model inference failure: (작성: 추론 실패가 몇 번 발생하면 중지할지 적는다)
- tracking error threshold: (작성: vision 기준 오차가 어느 값을 넘으면 중지할지 적는다)

## 7. Post-Run Validation
- required files exist: (작성: 필요한 파일이 모두 생성됐는지 확인한다)
- correction log valid: (작성: correction input/output, clamp, fallback 로그가 정상인지 확인한다)
- processed dataset generated: (작성: corrected processed dataset 생성 여부를 확인한다)
- baseline comparison completed: (작성: baseline 대비 비교가 완료됐는지 확인한다)
- RMSE comparison: (작성: baseline/corrected RMSE를 적는다)
- max error comparison: (작성: baseline/corrected max error를 적는다)
- corrected run accepted: (작성: 성능 비교 데이터로 채택할지 여부와 이유를 적는다)

## 8. Run Metadata
- run_id: (작성: 실험 실행 식별자를 적는다)
- baseline run_id: (작성: 비교 대상 baseline run_id를 적는다)
- operator: (작성: 실험 수행자를 적는다)
- date/time: (작성: 실험 시작/종료 시간을 적는다)
- hardware configuration version: (작성: base config 버전 또는 갱신일을 적는다)
- firmware version or commit: (작성: Arduino 펌웨어 버전 또는 commit을 적는다)
- virtual sensor model version: (작성: 모델 버전과 학습 데이터셋을 적는다)
- trajectory name: (작성: 사용한 trajectory 이름을 적는다)
- calibration file: (작성: vision calibration/homography 파일 경로를 적는다)
- code version or commit: (작성: logger, processing script, model inference 코드 버전 또는 commit을 적는다)
- notes: (작성: 특이사항을 적는다)
