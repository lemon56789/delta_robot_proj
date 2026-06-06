# Hardware Experiment Run 02 - Corrected Comparison

이 문서는 가상센싱 보정을 적용한 뒤 baseline 데이터와 비교할 검증 데이터를 수집하기 위한 run protocol이다.

## 1. Experiment Scope
- experiment purpose: 동일한 fresh trajectory를 correction OFF/ON으로
  반복 실행해 PC-side virtual sensing correction의 실제 XY 성능을
  비교한다.
- expected output: 24개 main raw CSV, vision raw CSV, correction auxiliary
  CSV, metadata/serial log, processed dataset, OFF/ON comparison report.
- target stage: Stage 9 correction 적용 및 실제 하드웨어 성능 검증.
- responsible members: 실험/하드웨어 담당, Arduino/serial 담당,
  vision 담당, virtual sensor/data analysis 담당.
- date: 실제 실행일을 `YYYY-MM-DD`로 각 metadata에 기록한다.
- run count: `4 trajectories x OFF/ON x 3 repetitions = 24`.
- comparison policy: Run 02 내부의 같은 trajectory/repetition OFF/ON pair를
  우선 비교한다. Run 01 circle 결과는 시간 정렬 불확실성 때문에 Run 02
  성능 기준으로 사용하지 않는다.

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
- `actual_elapsed_ms`, `schedule_lag_ms`, `command_sent`
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

### 3-A. Finalized 24-Run Matrix

아래 구성을 최종 Run 02 실행 구성으로 사용한다.

| trajectory | correction state | repetitions | run count |
|---|---|---:|---:|
| cross `+/-30 mm` | OFF / ON | 상태별 3회 | 6 |
| reverse grid 3x3 `+/-40 mm` | OFF / ON | 상태별 3회 | 6 |
| diamond `+/-35 mm` | OFF / ON | 상태별 3회 | 6 |
| circle `r=40 mm` | OFF / ON | 상태별 3회 | 6 |
| **total** | | | **24** |

계산: 4 trajectories x 2 correction states x 3 repetitions = 24 runs.

실행 순서는 각 repetition 안에서 trajectory별 OFF 직후 ON을 수행한다.

```text
r01: cross OFF -> ON
     reverse grid OFF -> ON
     diamond OFF -> ON
     circle OFF -> ON
r02: same order
r03: same order
```

이 순서는 OFF/ON 사이의 camera, marker, calibration, gain, 배선 및 기구
상태 변화를 줄이기 위한 것이다.

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
바퀴 이동한다. 정렬 event를 명확히 하기 위해 원 시작점과 종료점에서
각각 `2 s` 정지한다.

```text
home hold 5 s
-> (40, 0) hold 2 s
-> counterclockwise radius-40 circle
-> (40, 0) hold 2 s
-> home hold 5 s
```

### 3-C. Frozen Execution Parameters

- common `target_z`: `-263.27731514697575 mm`
- non-circle waypoint hold: `5 s`
- circle home hold: `5 s`
- circle start/end hold at `(40, 0)`: `2 s` each
- circle discretization: `72` points, `30 s` revolution
- PC data schedule/sample period: `0.1 s`
- serial command update: phase 전환 시 또는 최대 `0.5 s` 간격
- serial: `9600 baud`, `ALL theta1 theta2 theta3`
- correction gain: `0.25`
- XY vector clamp: `2 mm`
- Z correction: disabled
- theta safety range: `-45 deg` to `90 deg`
- run ID:
  `YYYY-MM-DD_run02_<trajectory>_<off|on>_r01..r03`
- trajectories:
  `cross_pm30`, `reverse_grid_3x3_pm40`, `diamond_pm35`, `circle_r40`

Nominal theta 범위 dry-run 결과:

| trajectory | min theta | max theta | rows |
|---|---:|---:|---:|
| cross | `-7 deg` | `8 deg` | 450 |
| reverse grid | `-11 deg` | `16 deg` | 550 |
| diamond | `-8 deg` | `10 deg` | 350 |
| circle | `-9 deg` | `11 deg` | 500 |

### 3-D. Deterministic Schedule and Simscape

- `experiments/run02_logger.py`는 실제 wall-clock 측정값 대신 deterministic
  scheduled milliseconds를 main CSV `time`에 기록한다.
- 실제 송신 시각과 schedule lag는 correction auxiliary/serial log에
  별도로 기록한다.
- Arduino `ALL` smooth move가 blocking이므로 모든 0.1초 row마다 명령을
  보내지 않는다. `command_sent`로 실제 갱신 row를 구분한다.
- correction ON은 schedule과 `time` 축이 정확히 같은 Simscape CSV가
  없으면 실행하지 않는다.
- 네 trajectory별 nominal Simscape CSV를 한 번씩 생성하고 세 repetition
  및 OFF/ON pair에서 공통 사용한다.
- 권장 경로:
  `data/simulation/raw/simscape_run02_nominal_<trajectory>.csv`
- 이 파일은 nominal target/theta schedule의 simulation이며 corrected
  target simulation으로 대체하지 않는다.

## 4. Required Logs
- main raw: `data/real/raw/main_<run_id>.csv`
- main metadata: `data/real/raw/main_<run_id>.json`
- serial: `data/real/raw/serial_<run_id>.txt`
- correction auxiliary: `data/real/raw/correction_<run_id>.csv`
- vision raw: `data/vision/raw/vision_<run_id>.csv`
- nominal Simscape:
  `data/simulation/raw/simscape_run02_nominal_<trajectory>.csv`
- angle-derived position:
  `data/real/derived/measured_position_<run_id>.csv`
- processed merged: `data/processed/merged_<run_id>.csv`
- comparison report: `experiments/results/run02_comparison_<date>.json`

## 5. Run Procedure
1. `manifest` 명령으로 실행일 기준 24개 run ID를 생성한다.
2. 네 trajectory의 OFF dry-run schedule을 생성한다.
3. schedule별 nominal Simscape CSV를 만들고 exact time-axis 검증을 한다.
4. camera/marker/calibration과 robot zero를 고정한다.
5. vision logger를 먼저 시작해 초기 home hold를 포함시킨다.
6. 해당 pair의 OFF logger를 실행한다.
7. 파일과 stop condition을 확인한 직후 같은 trajectory ON logger를
   실행한다.
8. ON 실행에서는 frozen model, gain `0.25`, clamp `2 mm`, 해당 nominal
   Simscape CSV를 명시한다.
9. correction log의 fallback, clamp, schedule lag를 확인한다.
10. 같은 절차를 r01-r03에 반복한다.
11. OFF/ON 모두 같은 calibration과 동일 alignment 정책으로 처리한다.
12. trajectory/repetition pair별 XY RMSE, MAE, max error를 계산하고
    aggregate는 trajectory별 세 repetition을 동일 가중한다.

## 6. Run-Specific Stop Conditions
- base config의 공통 hardware stop condition을 모두 적용한다.
- applied XY correction이 `2 mm`를 넘으면 즉시 invalid 처리한다.
- corrected theta가 `-45..90 deg`를 벗어나면 즉시 중지한다.
- fallback이 연속 `3`회 또는 한 run에서 총 `5`회 발생하면 중지한다.
- schedule lag가 `500 ms`를 초과하면 해당 run을 중지하고 원인을
  확인한다.
- marker가 `1 s` 넘게 연속 소실되면 중지하거나 run을 rejection한다.
- abnormal noise, vibration, link interference, servo stall 발생 시 즉시
  중지한다.

## 7. Post-Run Validation
- 24개 run ID와 required file 존재 여부 확인
- main/correction row count 및 scheduled time axis 일치
- vision timestamp 단조 증가 및 valid ratio `>=90%`
- longest continuous marker loss `<1 s`
- correction norm `<=2 mm`, Z correction `0`
- fallback/clamp/status count 기록
- schedule lag max/mean 기록
- processed dataset fixed 16-column, finite, timestamp monotonic 확인
- OFF/ON pair별 XY RMSE, MAE, max error 비교
- circle은 start/end hold anchor가 모두 검출된 경우에만 채택
- rejection 시 reason과 rerun 여부 기록

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
