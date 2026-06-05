# Hardware Experiment Run 01 - Baseline Data Collection

이 문서는 오차 학습용 baseline 데이터를 수집하기 위한 run protocol이다. 보정은 끄고, measured/sim/vision 로그를 수집해 processed merged dataset에서 `error_*` label을 생성한다.

Run 01은 하나의 긴 궤적 실험이 아니라 아래 세 단계로 나눈다.

1. `Run 01-pre`: pipeline validation.
2. `Run 01-main`: virtual sensor 학습용 baseline dataset.
3. `Run 01-holdout`: Run 02 corrected comparison에 사용할 baseline reference.

## 1. 실험 범위
- 실험 목적:
  - correction off 상태에서 real main log, vision raw log, Simscape output, angle-derived measured position을 수집한다.
  - post-alignment 후 processed merged dataset을 생성한다.
  - final CSV contract의 `error_x/y/z` label을 생성한다.
  - virtual sensor training/validation에 사용할 baseline dataset과 Run 02 comparison용 holdout baseline을 분리한다.
- 예상 산출물:
  - main CSV: `data/real/raw/main_<run_id>.csv`.
  - vision CSV: `data/vision/raw/vision_<run_id>.csv`.
  - angle-derived position CSV: `data/real/derived/measured_position_<run_id>.csv`.
  - Simscape output CSV: `data/simulation/raw/simscape_<run_id>.csv`.
  - processed merged dataset: `data/processed/merged_<run_id>.csv`.
  - run metadata: `experiments/run_metadata/<run_id>.md` 또는 `.json`.
- 대상 단계:
  - Stage 7 real data collection.
  - Stage 8 training data preparation.
- 담당자:
  - team lead / operator coordination: S.
  - hardware fabrication/assembly and experiment support: S / T / N.
  - Arduino/control and circuit/wiring: Y.
  - vision/logger: L.
  - Simscape/data processing and merge/training: L.
  - safety observer / power cutoff: Y 또는 지정된 담당자.
- 실행 컴퓨터 분담:
  - 컴퓨터 1(L): vision logger 실행, vision CSV 저장, 후처리/merge/학습 수행.
  - 컴퓨터 2(Y): Arduino IDE 실행, Arduino serial 연결, main logger 실행, main CSV 저장.
- date: `2026-06-05` 예정.
- run_id 형식:
  - `YYYY-MM-DD_run01_<phase>_<trajectory>_<repeat>`.
  - 예시: `2026-06-05_run01_pre_cross_pm40_r01`.
- correction enabled: `no`.
- 선행 조건:
  - Run 00 A/B/C gate가 pass 상태여야 한다.

## 2. 궤적 계획
모든 trajectory target은 `base_frame` 기준 `mm` 좌표를 사용한다. 별도 승인 없이 `z`는 현재 안전 home 높이 `z0`로 고정한다.

### 2-A. Run 01-pre - Pipeline Validation
Run 01-pre는 최종 학습 데이터셋이 아니다. raw log, Simscape output, alignment, merge, `error_*` label 생성이 end-to-end로 동작하는지 확인하는 단계다.

| trajectory | target range | 반복 | 목적 |
|---|---:|---:|---|
| `static_center_pre` | `(0, 0, z0)` hold | 1 | timestamp, static noise, bias 확인 |
| `cross_pm40_pre` | `x/y = ±40 mm` | 1 | 방향성과 alignment sanity check |
| `square_pm40_pre` | corner `x/y = ±40 mm` | 1 | corner/segment merge sanity check |

`square_pm40_pre` target order:
1. home: `(0, 0, z0)`
2. 1사분면: `(40, 40, z0)`
3. 2사분면: `(-40, 40, z0)`
4. 3사분면: `(-40, -40, z0)`
5. 4사분면: `(40, -40, z0)`
6. 1사분면 재방문: `(40, 40, z0)`
7. home: `(0, 0, z0)`

Vision logger handoff for `square_pm40_pre`:
- vision `run_id`는 main logger와 같은 `2026-06-05_run01_pre_square_pm40_r01`을 사용한다.
- vision 측 target label 또는 segment note가 가능하면 위 target order와 같은 순서로 기록한다.
- marker loss, occlusion, corner 도달 전후 흔들림이 있으면 해당 frame range 또는 segment를 note에 남긴다.
- Arduino/controller position gain `1.25`를 적용했다면 vision note에도 같은 조건을 적어 main/vision metadata 조건이 일치하게 한다.

Run 01-pre hardware compensation note:
- cross 실행 중 command 대비 실제 이동량이 작게 나타났다. 예: `40 mm` command에서 실제 vision 이동은 약 `30 mm`.
- 다른 거리에서는 같은 비율로 오차가 나지 않아 완전 선형 gain error로 판단하지 않는다.
- Arduino/controller 쪽 position gain `1.25`를 Run 01-pre용 coarse hardware compensation으로 적용할 수 있다.
- `1.25`는 한 점 기준 정밀 보정값이 아니라 실제 이동량을 목표 범위 근처로 끌어올리는 보수적 1차 보정값이다.
- 이 gain은 virtual sensing correction 또는 feedback correction으로 취급하지 않는다. Run 01의 correction enabled 상태는 계속 `no`다.
- gain 적용 여부와 값은 run metadata에 반드시 기록한다. gain이 다른 데이터는 같은 training/validation set에 섞지 않는다.
- 현재 Run 01-pre 기록 기준:
  - `2026-06-05_run01_pre_cross_pm40_r01`: Arduino/controller position gain `1.25` 적용 전 데이터.
  - `2026-06-05_run01_pre_square_pm40_r01`: Arduino/controller position gain `1.25` 적용 후 데이터.
  - 따라서 cross와 square는 hardware calibration condition이 다르며, processed dataset 또는 virtual sensor 학습에서 같은 조건의 반복 데이터처럼 섞지 않는다.

Run 01-pre 통과 기준:
- main log가 생성된다.
- vision log가 생성된다.
- 같은 target/command sequence에서 Simscape output이 존재하거나 생성 가능하다.
- `theta*_meas`에서 angle-derived measured position을 생성할 수 있다.
- processed merged dataset이 생성된다.
- final merged dataset에 `error_x`, `error_y`, `error_z`가 포함된다.
- main/vision `run_id`가 일치한다.
- main과 vision timestamp가 단조 증가한다.

Run 01-pre가 실패하면 Run 01-main으로 넘어가지 않는다.

Current Run 01-pre status as of 2026-06-06:
- static/cross/square main log, vision log, and Simscape output exist.
- `experiments/run01_preprocess.py` generated angle-derived measured position CSVs and processed merged datasets.
- `virtual_sensor/check_dataset.py` passed for all three Run 01-pre merged CSVs with `has_nan=False`.
- static merged rows: `299`; cross merged rows: `450`; square merged rows: `350`.
- Run 01-pre is considered complete for pipeline validation.
- Limitations: cross marker/valid ratio was about `92.98%`, square was about `93.21%`, and current `theta*_meas` is `command_echo_no_encoder`. Therefore Run 01-pre artifacts are not final training data.

### 2-B. Run 01-main - Training Baseline Dataset
Run 01-main은 virtual sensor 초기 학습에 사용할 baseline dataset이다. 모든 run에서 correction은 끈다.

| trajectory | target range | 반복 | split 역할 |
|---|---:|---:|---|
| `static_center_hold` | center hold, `20-30 s` | 3 | train, bias/noise support |
| `cross_pm20` | `x/y = ±20 mm` | 3 | train |
| `square_pm20` | `x/y = ±20 mm` | 3 | train |
| `circle_r15` | `r = 15 mm` | 3 | train 또는 validation |
| `grid_3x3_pm20` | `x, y = -20, 0, +20 mm`, `1-2 s` hold per point | 3 | train |

Training/validation split 기준:
- training:
  - `static_center_hold`
  - `cross_pm20`
  - `square_pm20`
  - `grid_3x3_pm20`
- validation:
  - `circle_r15` 중 1회 반복, 또는 fitting에 쓰지 않은 main trajectory 1회 반복.

Static data는 bias/noise 확인에 유용하지만 training batch에서 과도한 비중을 차지하지 않게 한다.

Initial virtual sensor modeling policy:
- 시간 제약상 Stage 8의 첫 virtual sensor model은 PyTorch neural network가 아니라 linear regression 또는 Ridge regression으로 구현한다.
- 기본 입력 feature는 `virtual_sensor.dataset.FEATURE_COLUMNS`와 같은 `theta1_cmd`, `theta2_cmd`, `theta3_cmd`, `theta1_meas`, `theta2_meas`, `theta3_meas`, `sim_x`, `sim_y`, `sim_z`를 사용한다.
- 출력 target은 processed merged dataset의 `error_x`, `error_y`, `error_z`다.
- Ridge의 regularization strength는 validation split에서만 선택한다. Run 01-holdout은 alpha 선택, feature 선택, 재학습 판단에 사용하지 않는다.
- `error_x/y`는 vision 기반 XY ground-truth label이므로 주 평가 대상이다. `error_z`는 현재 `theta*_meas` 기반 angle-derived estimate에서 나온 보조/diagnostic label로 해석한다.
- PyTorch MLP는 linear/Ridge baseline보다 명확한 성능 개선 필요성이 확인될 때의 future extension으로 둔다.

### 2-C. Run 01-holdout - Run 02 Comparison Baseline
Run 01-holdout은 virtual sensor 학습에 사용하지 않는다. Run 02에서는 같은 holdout trajectory를 correction on 상태로 다시 실행한다.

| trajectory | target range | 반복 | split 역할 |
|---|---:|---:|---|
| `cross_pm15_holdout` | `x/y = ±15 mm` | 1-2 | test / Run 02 comparison |
| `square_pm15_holdout` | `x/y = ±15 mm` | 1-2 | test / Run 02 comparison |
| `circle_r15_holdout` | `r = 15 mm` | 1-2 | test / Run 02 comparison |

시간이 허용되면 아래 trajectory를 추가할 수 있다.
- `pick_place_like_holdout`, `±20 mm` 내부의 작은 2D point-to-point path.

Holdout 규칙:
- Run 01-holdout row는 training이나 validation에 넣지 않는다.
- Run 02 comparison은 같은 trajectory 정의와 비교 가능한 실행 조건을 사용해야 한다.

## 3. 필수 로그
- main log:
  - path: `data/real/raw/main_<run_id>.csv`.
  - 최소 필드: `run_id`, `time`, `target_x`, `target_y`, `target_z`, `theta1_cmd`, `theta2_cmd`, `theta3_cmd`, `theta1_meas`, `theta2_meas`, `theta3_meas`, `valid`.
  - Run 01-pre provisional logger: `experiments/run01_main_logger.py`.
  - 실행 위치: Arduino가 연결된 컴퓨터 2(Y).
  - 주의: 현재 `theta*_meas`는 encoder 측정값이 아니라 `command_echo_no_encoder`다.
- vision raw log:
  - path: `data/vision/raw/vision_<run_id>.csv`.
  - 최소 필드: `run_id`, `vision_time`, `vision_x`, `vision_y`, `marker_detected`, `frame_id`, `valid`.
  - 선택 필드: `marker_id`, `reprojection_error`, `confidence`, `video_file`.
- raw video:
  - Run 01-pre와 holdout에서는 저장을 권장한다.
  - 저장 시 경로: `data/vision/raw/video_<run_id>.mp4`.
- angle-derived position log:
  - path: `data/real/derived/measured_position_<run_id>.csv`.
  - 최소 필드: `run_id`, `time`, `measured_x_est`, `measured_y_est`, `measured_z_est`, `estimator_method`, `valid`.
- Simscape output:
  - path: `data/simulation/raw/simscape_<run_id>.csv`.
  - source: 실제 run과 같은 target/command trajectory.
  - main log `time`과 alignment 가능한 time axis에서 `sim_x`, `sim_y`, `sim_z`를 제공해야 한다.
- processed merged dataset:
  - path: `data/processed/merged_<run_id>.csv`.
  - 고정 final columns: `time`, `target_x`, `target_y`, `target_z`, `theta1_cmd`, `theta2_cmd`, `theta3_cmd`, `theta1_meas`, `theta2_meas`, `theta3_meas`, `sim_x`, `sim_y`, `sim_z`, `error_x`, `error_y`, `error_z`.

## 4. 실행 절차
1. Run 00 상태 확인.
   - A/B/C gate가 pass여야 한다.
2. `run_id` 지정.
   - main logger, vision logger, Simscape output, derived position, processed dataset, metadata에 같은 `run_id`를 사용한다.
3. Run 01 phase와 trajectory 선택.
   - Run 01-pre부터 시작한다.
   - Run 01-pre가 통과하기 전에는 Run 01-main을 시작하지 않는다.
4. correction off 확인.
   - virtual sensing correction이나 feedback correction을 적용하지 않는다.
5. base config 로드.
   - `docs/hardware_experiment_base_config.md`, 2026-06-04 기준을 사용한다.
6. 전원 인가와 zeroing 수행.
   - Run 00 power/safety 절차를 따른다.
   - `theta_i=0 deg`와 `center_cmd_i=84/86/88 deg` 기준을 확인한다.
7. main logger 시작.
   - `data/real/raw/main_<run_id>.csv`에 저장한다.
   - 컴퓨터 2(Y)에서 Arduino IDE Serial Monitor를 닫고 `experiments/run01_main_logger.py`를 실행한다.
   - 예: `python run01_main_logger.py static_center_pre --run-id 2026-06-05_run01_pre_static_center_r01 --port COM3`.
8. vision logger 시작.
   - `data/vision/raw/vision_<run_id>.csv`에 저장한다.
   - homography/calibration file을 로드하고 경로를 metadata에 기록한다.
9. common start event 기록.
   - 가능하면 두 로그에 명확한 start marker 또는 동기화 timestamp를 남긴다.
10. baseline trajectory 실행.
    - 승인된 trajectory 범위를 지킨다.
    - marker detection, vibration, interference, zero return을 관찰한다.
11. common stop event 기록.
    - 가능하면 stop marker 또는 동기화 timestamp를 남긴다.
12. logger 정지.
    - 파일 존재와 row count가 0이 아님을 확인한다.
13. Simscape output 생성.
    - 같은 target/command sequence를 사용한다.
    - `data/simulation/raw/simscape_<run_id>.csv`에 저장한다.
14. angle-derived measured position 생성.
    - `theta*_meas`와 FK 또는 승인된 estimator를 사용한다.
    - estimator 이름과 버전을 `estimator_method`에 기록한다.
15. main, vision, Simscape, angle-derived data 정렬.
    - main log `time`을 기본 alignment axis로 사용한다.
    - invalid row, marker miss, timestamp gap은 제외한다.
16. processed merged dataset 생성.
    - `data/processed/merged_<run_id>.csv`에 저장한다.
    - `error_x/y/z`는 이 processed 단계에서만 생성한다.
17. dataset split 지정.
    - `train`, `validation`, 또는 `holdout`.
    - holdout row는 model fitting에 사용하지 않는다.
18. run metadata 저장.
    - command, data file, trajectory parameter, calibration file, Simscape model, code version, acceptance decision을 포함한다.
    - Run 01-pre에서 Arduino/controller position gain을 적용한 경우 gain value와 적용 위치를 포함한다.

## 5. Run별 중지 조건
- base stop conditions 적용: yes.
- marker loss threshold:
  - marker가 `1 s` 넘게 사라지면 중지하거나 해당 segment를 invalid로 표시한다.
- valid row ratio threshold:
  - Run 01-pre: 진행 조건은 `>= 95%`.
  - Run 01-main/holdout: `>= 95%`를 권장하며, 미달 시 rerun 또는 명시적 rejection note가 필요하다.
- timestamp threshold:
  - main `time` 또는 vision `vision_time`이 단조 증가하지 않으면 run invalid.
- run_id mismatch:
  - main/vision/processed dataset의 `run_id`가 불일치하면 run invalid.
- theta range threshold:
  - 현재 hardware-safe provisional range `-45 deg <= theta_i <= 90 deg`를 지킨다.
  - controller 또는 observer가 range violation을 확인하면 즉시 중지한다.
- target range threshold:
  - Run 01-pre: `±40 mm`를 넘지 않는다.
  - Run 01-main/holdout: 계획된 범위를 넘지 않는다. 기본 범위는 `±20 mm` 또는 `r=15 mm`다.
- hardware safety:
  - link interference, abnormal vibration, servo stalling, abnormal noise, operator safety judgment가 있으면 즉시 중지한다.

## 6. 실행 후 검증
- 필수 파일 존재: 예/아니오.
- 파일 row count가 0보다 큼: 예/아니오.
- main/vision `run_id` 일치: 예/아니오.
- timestamp monotonic:
  - main `time`: 예/아니오.
  - vision `vision_time`: 예/아니오.
- 필수 컬럼 존재:
  - main log: 예/아니오.
  - vision log: 예/아니오.
  - Simscape output: 예/아니오.
  - angle-derived measured position: 예/아니오.
  - processed merged dataset: 예/아니오.
- marker detection ratio: `%` 기록.
- valid row ratio: `%` 기록.
- Simscape output 생성: 예/아니오.
- angle-derived measured position 생성: 예/아니오.
- alignment check 완료: 예/아니오.
- processed merged dataset 생성: 예/아니오.
- processed error label 생성:
  - `error_x`: 예/아니오.
  - `error_y`: 예/아니오.
  - `error_z`: 예/아니오.
- dataset split 지정:
  - `pre_validation`, `train`, `validation`, 또는 `holdout`.
- baseline dataset 채택: 예/아니오.
- 채택하지 않으면 rejection reason과 rerun 필요 여부를 기록한다.

### Error Label 해석
- `error_x = measured_x_vision - sim_x`.
- `error_y = measured_y_vision - sim_y`.
- `error_z = measured_z_est - sim_z`.
- `error_x/y`는 vision 기반 XY ground-truth에서 생성한다.
- `error_z`는 angle-derived `measured_z_est` 기반이므로 외부 3D ground-truth 성능으로 제시하지 않는다.
- Run 01-pre provisional main logger의 `theta*_meas`는 `command_echo_no_encoder`이므로, 이 단계의 `error_z`는 pipeline 확인용 diagnostic으로만 사용한다.
- 초기 Run 02 성능 개선 주장은 XY metric 중심으로 판단한다.

## 7. Run Metadata
- run_id: run별 TBD.
- operator / team lead: S.
- date/time: TBD.
- phase: `pre`, `main`, 또는 `holdout`.
- trajectory name: run별 TBD.
- repeat index: TBD.
- dataset split: TBD.
- hardware configuration version: `docs/hardware_experiment_base_config.md`, 2026-06-04 기준.
- firmware version or commit:
  - status: Y 확인 전까지 pending.
- correction enabled: `no`.
- calibration file:
  - path: run별 TBD.
- Simscape model:
  - 권장: `simulation/simulink/simscape_delta_robot_trajectory_axisfix.slx` 또는 최신 validated trajectory model.
- code version or commit:
  - logger: TBD.
  - IK/FK: TBD.
  - alignment/merge: TBD.
- commands:
  - trajectory generation command: TBD.
  - Simscape export command: TBD.
  - angle-derived position command: TBD.
  - merge command: TBD.
- notes:
  - Run 01-main 수집 전 Run 01-pre가 반드시 통과해야 한다.
  - Run 01-holdout은 training과 validation fitting에서 제외해야 한다.
  - 현재 `run01_main_logger.py`는 pre trajectory만 지원하므로 Run 01-main/holdout 실행 전 trajectory 지원 추가가 필요하다.
