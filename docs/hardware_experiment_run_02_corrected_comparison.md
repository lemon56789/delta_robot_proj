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
- collected data provenance: 이번 24개 Run 02 데이터의 실제 실험일은
  `2026-06-07`이다. 기존 준비 과정에서 사용한 식별자와의 연속성을
  유지하기 위해 raw run ID와 calibration run ID의 `2026-06-06` 표기는
  변경하지 않는다. 이 날짜 차이는 파일 중복이 아니라 식별자 유지에
  따른 의도된 기록이다.
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

실제 실행에서는 trajectory 하나를 선택한 뒤 `r01`부터 `r03`까지
수집하고, 각 repetition 안에서 OFF 직후 ON을 수행했다.

```text
cross:        r01 OFF -> ON -> r02 OFF -> ON -> r03 OFF -> ON
reverse grid: r01 OFF -> ON -> r02 OFF -> ON -> r03 OFF -> ON
diamond:      r01 OFF -> ON -> r02 OFF -> ON -> r03 OFF -> ON
circle:       r01 OFF -> ON -> r02 OFF -> ON -> r03 OFF -> ON
```

trajectory 실행 순서는 cross, reverse grid, diamond, circle이었다.
각 repetition의 OFF/ON을 바로 이어서 수행해 pair 사이의 camera, marker,
calibration, gain, 배선 및 기구 상태 변화를 줄였다.

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
10. 같은 trajectory에서 r01-r03을 완료한 뒤 다음 trajectory로 이동한다.
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

## 8. Analysis Workflow

### 8-A. Input Inventory and Raw Validation

1. 확정된 24개 run ID를 기준으로 다음 파일의 존재 여부를 확인한다.
   - `main_<run_id>.csv`
   - `main_<run_id>.json`
   - `serial_<run_id>.txt`
   - `correction_<run_id>.csv`
   - `vision_<run_id>.csv`
2. trajectory별 예상 main/correction row 수를 확인한다.
   - cross: `450`
   - reverse grid: `550`
   - diamond: `350`
   - circle: `500`
3. main과 correction의 `run_id`, row 수, scheduled `time` 축이 같은지
   확인한다.
4. vision은 timestamp 단조 증가, valid ratio `>=90%`, 연속 marker loss
   `<1 s`를 확인한다.
5. correction은 applied XY norm `<=2 mm`, applied Z `=0`, fallback,
   clamp, status와 schedule lag를 확인한다.
6. invalid vision row는 원본에 유지하되 정렬과 metric 계산에서는
   제외한다. 긴 invalid 구간을 임의 보간해 복원하지 않는다.

### 8-B. Pair Definition

- 비교 단위는 파일 생성 순서가 아니라
  `(trajectory, repetition)`이 같은 OFF/ON 두 run이다.
- 총 pair 수는 `4 trajectories x 3 repetitions = 12`다.
- 각 pair는 같은 nominal Simscape trajectory와 같은 alignment 정책을
  사용한다.
- trajectory가 다른 run 또는 repetition이 다른 run을 서로 pairing하지
  않는다.

### 8-C. Time Alignment

#### Cross, Reverse Grid, Diamond

- main의 phase 전환과 vision의 위치 departure/arrival event를 사용한다.
- 각 waypoint의 stable 구간에서 다음 target 방향으로 출발하는 vision
  event를 대응 main phase 시작에 연결한다.
- alignment anchor가 순서대로 증가하는지 확인하고, waypoint 누락이나
  잘못된 순서가 있으면 해당 run을 rejection 후보로 기록한다.
- 정렬 후에도 vision의 실제 timestamp 간격은 보존한다.

#### Circle

- main 기준 `t=0`은 첫 `circle_ccw_*` phase가 시작되는 scheduled
  timestamp다.
- vision 기준 `t=0`은 `(40, 0)` 시작 hold의 stable 영역을 벗어나
  반시계 원운동을 시작한 최초 유효 departure timestamp다.
- 두 departure anchor를 같은 `t=0`으로 맞춘다.
- vision timestamp는 `vision_time - departure_time`으로 변환하고,
  main timestamp는 `time - circle_motion_start_time`으로 변환한다.
- 원 시작점으로 돌아온 뒤의 end hold는 종료 anchor 검증에 사용한다.
- 시작 anchor 정렬 이후 실제 timestamp 간격과 실제 회전 시간은
  유지한다. 고정 10 Hz 시간축 재생성, 종료점 강제 일치, 전체 구간
  time warping은 적용하지 않는다.
- start/end hold가 모두 검출되지 않거나 출발 event가 불명확하면 해당
  circle run을 metric 계산에서 제외하고 reason을 기록한다.

### 8-D. Aligned Dataset Generation

1. main scheduled time을 기준으로 nominal target, command angle과
   Simscape position을 준비한다.
2. 유효 vision XY를 trajectory별 alignment 정책으로 main 시간축에
   대응시킨다.
3. correction 성능 비교용 target tracking XY 오차를 계산한다. 이
   diagnostic 이름은 processed CSV contract의 `error_x/y`와 구분한다.

```text
tracking_error_x = vision_x - target_x
tracking_error_y = vision_y - target_y
tracking_xy_error = sqrt(tracking_error_x^2 + tracking_error_y^2)
```

4. processed CSV의 `error_x/y`는 기존 contract대로 Simscape 기준
   오차를 사용한다.

```text
error_x = vision_x - sim_x
error_y = vision_y - sim_y
```

5. processed merged dataset을 생성할 경우
   `docs/measured_data_structure.md`의 fixed 16-column contract를
   유지한다.
6. 각 output에는 source run ID, alignment method, anchor timestamp,
   source/valid/output row 수를 sidecar JSON 또는 comparison report에
   기록한다.

### 8-E. Run-Level Metrics

각 run에서 유효하고 정렬된 XY sample만 사용해 다음 값을 계산한다.

- `tracking_x_rmse`, `tracking_y_rmse`, `tracking_xy_rmse`
- `tracking_x_mae`, `tracking_y_mae`, `tracking_xy_mae`
- `tracking_xy_max_error`
- valid/aligned row count와 coverage ratio
- trajectory duration
- correction ON의 clamp count, fallback count, max/mean schedule lag

RMSE와 MAE는 OFF와 ON에 동일한 구간 선택 규칙을 적용한다. OFF/ON 중
한쪽에만 존재하는 긴 누락 구간을 임의 보간해 sample 수를 맞추지 않는다.

### 8-F. Paired OFF/ON Comparison

각 `(trajectory, repetition)` pair에 대해 다음을 계산한다.

```text
absolute_improvement = metric_off - metric_on
improvement_percent = 100 * (metric_off - metric_on) / metric_off
```

- positive improvement는 ON 오차가 감소했음을 의미한다.
- `metric_off = 0`인 경우 percent는 계산하지 않고 absolute difference만
  기록한다.
- 주 성능 지표는 `tracking_xy_rmse`, 보조 지표는
  `tracking_xy_mae`, `tracking_xy_max_error`다.
- 각 pair의 개선/악화 여부와 alignment/rejection note를 함께 기록한다.

### 8-G. Repetition and Trajectory Summary

- trajectory별 세 repetition의 pair metric을 동일 가중한다.
- trajectory별 mean, standard deviation, 개선된 repetition 수를
  기록한다.
- 전체 aggregate는 먼저 trajectory별 summary를 만든 뒤 네 trajectory를
  동일 가중한다. row 수가 많은 trajectory가 전체 결과를 지배하지
  않도록 모든 raw row를 한 번에 합쳐 계산하지 않는다.
- circle은 시작 departure 정렬 결과와 end hold 검출 여부를 별도로
  보고한다.

### 8-H. Outputs and Acceptance

- aligned/processed data:
  `data/processed/merged_<run_id>.csv`
- alignment sidecar:
  `data/processed/alignment_<run_id>.json`
- comparison report:
  `experiments/results/run02_comparison_<date>.json`
- 권장 plot:
  - OFF/ON XY trajectory overlay
  - target, vision, Simscape의 time-series
  - pair별 `tracking_xy_error` time-series
  - trajectory별 repetition metric과 improvement plot

Run 02 correction은 다음을 모두 만족할 때 개선으로 결론낸다.

- raw/vision safety 및 quality gate를 통과한다.
- 12개 pair의 rejection과 사용 여부가 모두 설명된다.
- trajectory별 `tracking_xy_rmse` summary에서 ON/OFF 차이가 보고된다.
- 전체 평균만이 아니라 repetition 간 일관성과 악화 case를 함께
  제시한다.

### 8-I. Implemented Processing Result - 2026-06-07

- command:
  `PYTHONPATH=venv/lib/python3.12/site-packages python3 experiments/run02_preprocess.py`
- implementation: `experiments/run02_preprocess.py`
- unit test: `experiments/test_run02_preprocess.py`
- comparison report:
  `experiments/results/run02_comparison_2026-06-07.json`
- generated:
  - measured-position CSV `24`
  - merged fixed 16-column CSV `24`
  - alignment sidecar JSON `24`
  - OFF/ON pair comparison `12`
- merged coverage: `94.6%` to `100%`
- step maximum anchor residual: `232.522 ms`, limit `500 ms` 이내
- circle end hold duration: `2.127 s` to `2.684 s`, 전체 6개 run 검출
- fallback: 전체 ON run `0`
- output validation:
  - merged file count `24`
  - fixed 16-column order pass
  - finite value pass
  - timestamp monotonic pass

`tracking_xy_rmse`의 trajectory별 3회 평균 결과:

| trajectory | OFF mean mm | ON mean mm | mean improvement | improved pairs |
|---|---:|---:|---:|---:|
| cross | `5.6003` | `5.9854` | `-7.73%` | `1/3` |
| reverse grid | `7.9846` | `7.0663` | `+11.05%` | `3/3` |
| diamond | `5.6410` | `4.8702` | `+13.67%` | `3/3` |
| circle | `6.2069` | `7.7670` | `-25.41%` | `0/3` |

네 trajectory 동일가중 결과는 OFF `6.3582 mm`, ON `6.4222 mm`로
`tracking_xy_rmse`가 `2.10%` 악화됐다. `tracking_xy_mae`는 `6.03%`
개선됐지만 `tracking_xy_max_error`는 `5.28%` 악화됐다.

현재 gain `0.25`, clamp `2 mm` 설정은 reverse grid와 diamond에서는
일관된 개선을 보였지만 cross와 circle에서는 악화됐다. 따라서 Run 02
전체 correction이 개선됐다고 결론내리지 않으며, trajectory별 error
phase와 correction 방향을 분석한 뒤 gain 또는 적용 정책을 재검토한다.

### 8-J. Existing Data Reanalysis - 2026-06-07

- command:
  `PYTHONPATH=venv/lib/python3.12/site-packages python3 experiments/run02_reanalyze.py`
- implementation: `experiments/run02_reanalyze.py`
- unit test: `experiments/test_run02_reanalyze.py`
- report: `experiments/results/run02_reanalysis_2026-06-07.json`
- input: 기존 Run 02 raw main/correction CSV와 merged CSV 24개
- raw, processed CSV와 기존 comparison report는 변경하지 않았다.
- 12개 pair의 absolute `tracking_xy_rmse`는 기존 공식 comparison
  report와 차이 `0`으로 재현됐다.

각 run의 초기 `home_1`에서 `vision - target` 중앙값을 home offset으로
정의하고 이를 전체 vision XY에서 제거한 home-normalized 결과:

| trajectory | OFF mean mm | ON mean mm | improvement | improved pairs |
|---|---:|---:|---:|---:|
| cross | `4.2138` | `5.1725` | `-22.75%` | `1/3` |
| reverse grid | `7.1461` | `6.9019` | `+3.42%` | `3/3` |
| diamond | `4.8680` | `4.1399` | `+14.96%` | `3/3` |
| circle | `5.4864` | `7.3527` | `-34.02%` | `0/3` |

home-normalized metric은 zero drift 영향을 줄인 진단값이며 absolute 위치
정확도를 대체하지 않는다. Diamond만 absolute와 normalized 결과 모두
세 repetition에서 개선됐다. Reverse grid normalized 개선은 작고,
cross와 circle은 초기 home 차이를 제거한 뒤에도 악화됐다.

Arduino firmware의
`round(center + sign * theta * 1.25)` mapping을 main CSV에 기록된 실제
전송 theta에 적용한 결과:

| trajectory | actual integer command changed | fractional theta theoretical |
|---|---:|---:|
| cross | `11.1%` | `33.3%` |
| reverse grid | `45.5%` | `63.6%` |
| diamond | `27.1%` | `57.1%` |
| circle | `33.0%` | `57.0%` |

따라서 fractional corrected theta가 이론상 servo command를 바꿀 수 있는
경우도 실제 전송 theta와 최종 integer command 단계에서 추가로
소실됐다. 특히 cross 결과는 correction model뿐 아니라 actuator command
해상도의 영향을 크게 받는다.

Step trajectory는 각 non-initial phase 시작 후 첫 `1 s`를 transition,
나머지를 stable로 분리했다.

- cross: absolute transition은 `6.68%` 개선됐지만 stable은 `9.51%`
  악화됐다. home-normalized에서는 transition과 stable 모두 악화됐다.
- reverse grid: absolute transition `11.64%`, stable `12.64%` 개선됐다.
  home-normalized transition은 `9.18%` 악화되고 stable은 `5.00%`
  개선되어 baseline drift 영향이 남아 있다.
- diamond: absolute transition `23.29%`, stable `12.20%`, normalized
  transition `30.97%`, stable `17.31%` 개선됐다.

Circle 원운동 구간 진단:

| metric | OFF mean | ON mean |
|---|---:|---:|
| radial error RMSE | `3.319 mm` | `2.843 mm` |
| tangential error RMSE | `3.593 mm` | `4.442 mm` |
| mean tangential error | `0.048 mm` | `3.037 mm` |
| equivalent median phase lag | `2.2 ms` | `361.7 ms` |
| diagnostic best shift | `33 ms` | `350 ms` |
| best-shift RMSE | `4.791 mm` | `4.220 mm` |

Circle ON은 radial error는 감소했지만 tangential error와 phase lag가
증가했다. ON 세 repetition 모두 best shift가 `350 ms`였으므로 기존
time-domain 악화가 우연한 단일 run 정렬 오류만으로 설명되지는 않는다.
Best-shift RMSE는 path-shape diagnostic이며 실제 동적 lag를 제거하므로
공식 time-domain 성능값을 대체하지 않는다.

## 9. Run Metadata
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
