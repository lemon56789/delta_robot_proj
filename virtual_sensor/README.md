# virtual_sensor

가상 센싱(Physics + data-driven correction) 모델 학습/추론 코드를 관리하는 폴더입니다.

현재 포함 모듈:
- `dataset.py`: fake pipeline CSV를 읽고 feature/target shape를 검증하는 loader
- `check_dataset.py`: CLI로 dataset shape, NaN 여부, 기본 통계를 확인하는 스크립트

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
- Ridge regularization strength는 validation split에서만 고르고, Run 01-holdout은 fitting/tuning에 사용하지 않는다.
- PyTorch MLP는 linear/Ridge baseline보다 명확한 개선 필요성이 확인될 때 추가한다.
