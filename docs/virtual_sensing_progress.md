# Virtual Sensing Progress

기준일: `2026-06-06`

## 1. 목적

이 프로젝트의 가상센서는 로봇 명령과 Simscape 결과로부터 실제 위치와
시뮬레이션 위치의 차이를 추정하는 offline error estimator다.

현재 모델의 입력과 출력은 다음과 같다.

- 입력:
  - `theta1_cmd`, `theta2_cmd`, `theta3_cmd`
  - `theta1_meas`, `theta2_meas`, `theta3_meas`
  - `sim_x`, `sim_y`, `sim_z`
- 출력:
  - `error_x`, `error_y`, `error_z`
- 오차 정의:
  - `error_x = measured_x_vision - sim_x`
  - `error_y = measured_y_vision - sim_y`
  - `error_z = measured_z_est - sim_z`

XY는 vision ground truth 기반 주 평가 항목이다. Z는 command-echo angle의
FK 결과이므로 진단 항목으로만 사용한다.

## 2. 데이터 구성

Run 01-main은 다섯 trajectory를 각 3회 실행한 총 15개 run으로 구성했다.

- static center
- cross `±40 mm`
- square `±40 mm`
- circle `r=40 mm`
- grid `3x3`, `±40 mm`

검증 정책은 repetition 단위 3-fold다.

- Fold 1: `r01` 검증, `r02+r03` 학습
- Fold 2: `r02` 검증, `r01+r03` 학습
- Fold 3: `r03` 검증, `r01+r02` 학습

같은 run의 인접 row를 임의 분할하지 않았다. alpha 선택 이후 main 15개
전체로 최종 모델 하나를 다시 학습했다.

현재 complete holdout은 다음 네 run이다.

- static center
- cross `±30 mm`
- square `±30 mm`
- grid `3x3`, `±40 mm`

circle holdout은 Simscape 파일이 아직 없어 최종 평가에 포함되지 않았다.

## 3. 첫 모델 선택

초기 데이터 규모와 설명 가능성을 고려해 신경망보다 standardized Ridge
regression을 먼저 구현했다. NumPy만 사용하며 feature scaler, coefficient,
intercept, alpha, feature/target 이름, training run ID를 하나의 `.npz`
파일에 저장한다.

alpha grid:

```text
0, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100, 1000
```

alpha는 세 fold의 run-macro XY RMSE로 선택하고, 동률이면 XY MAE와 작은
alpha 순으로 결정한다.

## 4. 최초 결과

최초 전처리와 학습 결과는 다음과 같았다.

- 선택 alpha: `1`
- main OOF macro XY RMSE: `10.007 mm`
- holdout 보정 전 macro XY RMSE: `11.946 mm`
- holdout Ridge macro XY RMSE: `11.033 mm`
- holdout 개선율: `7.638%`

Run별 개선율은 static `29.662%`, cross `5.196%`, square `2.928%`, grid
`6.997%`였다. 특히 grid와 square의 최대 오차가 각각 약 `88 mm`,
`64 mm`로 커서 바로 Run 02 제어에 적용하기에는 불충분했다.

## 5. Phase 오차 분석

신경망으로 바로 전환하지 않고 phase별 오차를 분석했다.

- main: repetition별 out-of-fold prediction
- holdout: frozen final model prediction
- 분석 구간:
  - phase 시작 `0-0.5 s`
  - `0.5-1.5 s`
  - `1.5 s+`
  - phase 첫 `0.5 s`, 내부, 마지막 `0.5 s`

분석 결과 holdout phase 내부의 Ridge RMSE는 `5.097 mm`였지만 phase 마지막
`0.5 s`는 `40.304 mm`였다. 최악 row는 대부분 phase 종료 직전이었다.

raw vision을 확인한 결과, vision phase 끝부분에 다음 setpoint로 이동한
sample이 포함되어 있었다. 기존 piecewise alignment는 이 이동을 현재 main
phase의 마지막 구간으로 늘려서 mapping했다. 따라서 큰 오차의 주원인은
모델 용량보다 phase-boundary alignment였다.

## 6. Alignment 수정

cross, square, grid에는 event-anchor alignment를 적용했다.

1. 현재 stable 위치에서 `5 mm` 이상 이탈한 vision sample을 departure로
   검출한다.
2. departure 직전 stable sample을 현재 main phase 끝에 mapping한다.
3. departure를 다음 main command phase 시작에 mapping한다.
4. 새 vision phase의 첫 valid sample을 Simscape가 새 target XY의 `3 mm`
   이내에 도달한 시점에 mapping한다.
5. phase 내부에 departure sample이 없으면 마지막 valid timestamp를
   boundary edge로 사용한다.

추가로 epoch-millisecond timestamp에 `math.isclose`의 상대오차를 사용하면
약 `100 ms` 차이도 같은 시각으로 판정되는 문제를 발견했다. timestamp
동일성은 절대오차 `1e-9 ms` 이하로 변경했다.

static과 circle의 기존 alignment 정책은 유지했다.

## 7. 재전처리와 재학습 결과

alignment 수정 후 main 15개와 complete holdout 4개를 재전처리했다.

- main row 수: `5,158`
- 선택 alpha: `100`
- main OOF macro XY RMSE: `4.887 mm`

### Holdout 비교

| 항목 | 최초 결과 | 재정렬 후 |
|---|---:|---:|
| 보정 전 macro XY RMSE | `11.946 mm` | `4.533 mm` |
| Ridge macro XY RMSE | `11.033 mm` | `2.848 mm` |
| Ridge 개선율 | `7.638%` | `37.174%` |
| main OOF macro XY RMSE | `10.007 mm` | `4.887 mm` |
| phase 마지막 0.5 s Ridge RMSE | `40.304 mm` | `2.444 mm` |

재정렬 후 run별 holdout 결과:

| Trajectory | 보정 전 XY RMSE | Ridge XY RMSE | 개선율 |
|---|---:|---:|---:|
| static center | `5.105 mm` | `2.888 mm` | `43.427%` |
| cross `±30 mm` | `3.506 mm` | `2.913 mm` | `16.933%` |
| square `±30 mm` | `4.496 mm` | `2.873 mm` | `36.110%` |
| grid `3x3 ±40 mm` | `5.026 mm` | `2.720 mm` | `45.895%` |

row-weighted phase 분석에서도 holdout XY RMSE가 `4.597 -> 2.837 mm`로
`38.299%` 개선됐다. 현재 큰 오차는 주로 phase 시작 transient에 남아 있다.

## 8. 현재 모델과 실행 방법

현재 모델:

- `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`
- alpha: `100`
- training rows: `5,158`

실행 명령:

```bash
python3 virtual_sensor/train_ridge.py
python3 virtual_sensor/evaluate_ridge.py
python3 virtual_sensor/analyze_phase_errors.py
```

주요 결과:

- `experiments/results/ridge_run01_main_cv_2026-06-06.json`
- `experiments/results/ridge_run01_holdout_2026-06-06.json`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.md`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.json`

## 9. 해석상의 제한

1. `theta*_meas`는 실제 encoder 측정이 아니라
   `command_echo_no_encoder`다.
2. `error_z`는 외부 3D ground truth가 아니다.
3. circle holdout 평가는 아직 남아 있다.
4. 기존 holdout에서 alignment 결함을 발견하고 수정했으므로 재정렬 후
   `37.174%`는 retrospective corrected-pipeline 결과다. 완전히 독립적인
   최종 일반화 성능으로 해석하면 안 된다.
5. 현재 모델은 offline estimator이며 아직 controller feedback에
   연결하지 않았다.

## 10. 다음 단계

1. circle holdout Simscape 파일을 추가하고 partial diagnostic 평가를
   완료한다.
2. Run 02 공통 보정 엔진과 offline safety replay는 완료했다.
   - frozen Ridge 모델 사용
   - `target_xy - gain * predicted_error_xy`
   - XY vector clamp, Z correction off, nominal-command fallback
   - main-only 초기 hardware gate 후보: gain `0.25`, clamp `2 mm`
   - main/holdout 전체 후보에서 IK fallback 및 limit violation `0`
3. 최종 trajectory와 대응 Simscape 파일을 확정한다.
4. serial-enabled Run 02 logger를 연결하고 static/small-motion hardware
   gate를 수행한다.
5. fresh Run 02 데이터에서 correction off/on을 동일 조건으로 비교한다.
6. fresh 데이터에서 개선이 재현된 뒤에 feature 확장 또는 작은 MLP 비교를
   검토한다.

## 11. 상세 기록

- 최초 학습과 평가: `docs/plans/2026-06-06_013_ridge_virtual_sensor_training.md`
- phase 원인 분석: `docs/plans/2026-06-06_014_phase_error_analysis.md`
- 재정렬과 재학습: `docs/plans/2026-06-06_015_phase_boundary_realignment_retrain.md`
- 작업 일지: `docs/daily_notes/2026-06-06.md`의 Entry 013-020
- Run 02 공통 엔진/offline 검증:
  `docs/plans/2026-06-06_017_run02_correction_engine_offline_validation.md`
