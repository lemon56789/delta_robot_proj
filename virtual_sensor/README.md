# virtual_sensor

가상 센싱(Physics + data-driven correction) 모델 학습/추론 코드를 관리하는 폴더입니다.

전체 진행 과정과 결과 요약:
[`docs/virtual_sensing_progress.md`](../docs/virtual_sensing_progress.md)

현재 포함 모듈:
- `dataset.py`: fake pipeline CSV를 읽고 feature/target shape를 검증하는 loader
- `check_dataset.py`: CLI로 dataset shape, NaN 여부, 기본 통계를 확인하는 스크립트
- `ridge_model.py`: NumPy 기반 표준화/Ridge 학습, 추론, `.npz` 저장·로드
- `train_ridge.py`: Run 01-main run-level 3-fold CV와 최종 재학습
- `evaluate_ridge.py`: frozen model의 Run 01-holdout 격리 평가
- `correction_engine.py`: 예측을 XY target correction, vector clamp,
  corrected-target IK, nominal-command fallback으로 변환하는 공통 엔진
- `test_correction_engine.py`: correction sign, clamp, Z-off, feature schema,
  fallback 단위 테스트

현재 기본 feature columns:
- `theta1_cmd`, `theta2_cmd`, `theta3_cmd`
- `theta1_meas`, `theta2_meas`, `theta3_meas`
- `sim_x`, `sim_y`, `sim_z`

현재 기본 target columns:
- `error_x`, `error_y`, `error_z`

초기 학습 방침:
- 첫 baseline model은 PyTorch neural network가 아니라 linear regression 또는 Ridge regression으로 둔다.
- 모델은 위 feature columns에서 processed merged dataset의 `error_x/y/z`를 예측한다.
- `error_x/y`는 vision 기반 XY label이므로 주 평가 대상이고, `error_z`는 angle-derived Z 기반 보조/diagnostic target으로 해석한다.
- Ridge validation은 Run 01-main의 반복 번호를 이용한 run-level 3-fold
  cross-validation으로 수행한다.
  - Fold 1: `r01` validation, `r02+r03` training.
  - Fold 2: `r02` validation, `r01+r03` training.
  - Fold 3: `r03` validation, `r01+r02` training.
- 동일 run의 row를 무작위로 train/validation에 나누지 않는다.
- Ridge alpha는 세 fold의 run/trajectory 단위 XY RMSE 평균으로 선택하고,
  XY MAE와 max error를 함께 기록한다.
- alpha와 feature를 확정한 뒤 Run 01-main 전체 데이터로 최종 모델 하나를
  다시 학습한다. fold 모델 중 가장 좋은 한 개를 최종 모델로 사용하지
  않는다.
- Run 01-holdout은 fitting, cross-validation, alpha 선택, feature 선택에
  사용하지 않고 최종 평가에만 사용한다.
- PyTorch MLP는 linear/Ridge baseline보다 명확한 개선 필요성이 확인될 때 추가한다.

## Run 01 Ridge 실행

학습과 3-fold CV:

```bash
python3 virtual_sensor/train_ridge.py
```

기본 alpha grid는
`[0, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100, 1000]`이다.
phase-boundary realignment 이후 Run 01-main 15개 run, 총 5,158 row의 실행
결과로 `alpha=100`이 선택되었고 run-macro 평균 XY RMSE는
`4.886987 mm`였다.

산출물:
- 모델: `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`
- CV 보고서: `experiments/results/ridge_run01_main_cv_2026-06-06.json`

holdout Simscape CSV가 준비된 뒤 각 run을 전처리한다.

```bash
python3 experiments/run01_preprocess.py --run-id <holdout_run_id>
python3 virtual_sensor/evaluate_ridge.py
```

필요한 Simscape 입력 파일명은
`data/simulation/raw/simscape_<holdout_run_id>.csv`이며, 각 파일의 `time`
축은 대응하는 main CSV와 정확히 같아야 한다. holdout 평가 보고서는
`experiments/results/ridge_run01_holdout_2026-06-06.json`에 저장된다.
circle이 아직 없으면 네 complete run만 평가하고 report status를
`preliminary_complete_only`로 기록한다. circle merged CSV가 추가된 뒤 같은
명령을 다시 실행하면 status가 `final_with_partial_circle`로 바뀐다.
`circle_r40_holdout_r01`은 관측된 원운동 각도 구간만 전처리하며
`partial_diagnostic`으로 분리한다.

phase-boundary realignment 이후 complete holdout 4개 예비 결과:
- 보정 전 macro XY RMSE: `4.533414 mm`
- Ridge 적용 후 macro XY RMSE: `2.848173 mm`
- macro 개선율: `37.174%`
- run별 개선율: static `43.427%`, cross pm30 `16.933%`, square pm30
  `36.110%`, grid pm40 `45.895%`

이 결과는 circle이 빠진 예비 평가이며 Run 02 제어 적용 승인 기준을
단독으로 충족했다고 해석하지 않는다. 또한 같은 holdout에서 alignment
결함을 진단했으므로 이 수치는 retrospective corrected-pipeline
estimate이며, fresh Run 02 data가 다음 독립 성능 gate다.

## Phase 오차 분석

```bash
python3 virtual_sensor/analyze_phase_errors.py
```

산출물:
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.json`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.md`

main은 out-of-fold prediction, holdout은 frozen final model prediction으로
분석한다. phase-boundary realignment 이후 holdout row-weighted XY RMSE는
`4.597 -> 2.837 mm`로 `38.299%` 개선됐고, phase 마지막 `0.5 s` Ridge
RMSE는 `40.304 -> 2.444 mm`로 감소했다. 현재 남은 큰 오차는 주로 phase
시작 transient에 집중된다.

## Run 02 correction engine offline 검증

공통 엔진 정책:

- `corrected_target_xy = target_xy - gain * predicted_error_xy`
- XY vector norm clamp, Z correction off
- feature schema 불일치 시 실행 거부
- 입력/추론/IK 오류 시 nominal target/theta fallback

실행:

```bash
python3 -m unittest virtual_sensor.test_correction_engine -v
python3 experiments/run02_offline_validate.py
```

검증 결과:

- main 15 runs, `5,158` rows
- complete holdout 4 runs, `1,356` rows
- gain `0.25/0.5/1.0`, clamp `2/4/6 mm`의 9개 후보
- 모든 후보에서 fallback 및 correction/theta limit violation `0`
- main-only 초기 hardware gate 후보: gain `0.25`, XY clamp `2 mm`
- main clamp `4/5,158` rows (`0.077549%`), holdout clamp `0/1,356`

보고서:
`experiments/results/run02_correction_offline_validation_2026-06-06.json`

이 후보는 holdout 성능으로 최적화한 값이 아니며 실제 하드웨어 개선을
보장하지 않는다.

## 현재 제한

- `theta*_meas`는 `command_echo_no_encoder`이므로 독립적인 motor 측정값이
  아니다.
- `error_z`는 angle-derived FK 값이므로 외부 3D ground truth가 아니다.
- 2026-06-06 현재 complete holdout 4개 평가는 완료했지만 circle Simscape
  CSV가 없어 `final_with_partial_circle` 평가는 아직 남아 있다.
