# virtual_sensor

가상 센싱(AI + Physics Hybrid) 모델 학습/추론 코드를 관리하는 폴더입니다.

현재 포함 모듈:
- `dataset.py`: fake pipeline CSV를 읽고 feature/target shape를 검증하는 loader
- `check_dataset.py`: CLI로 dataset shape, NaN 여부, 기본 통계를 확인하는 스크립트

현재 기본 feature columns:
- `theta1_cmd`, `theta2_cmd`, `theta3_cmd`
- `theta1_meas`, `theta2_meas`, `theta3_meas`
- `sim_x`, `sim_y`, `sim_z`

현재 기본 target columns:
- `error_x`, `error_y`, `error_z`
