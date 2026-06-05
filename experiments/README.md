# experiments

실험 계획, 실행 로그, 성능 검증 결과를 관리하는 폴더입니다.

현재 포함 예시:
- `fake_pipeline.py`: 실제 하드웨어 없이 end-to-end fake dataset을 생성하는 스크립트
- `run01_main_logger.py`: 컴퓨터 2(Y)에서 Arduino serial에 `ALL theta1 theta2 theta3` 명령을 보내고 Run 01-pre main CSV를 저장하는 PC-side logger
- `run01_main_logger_computer2_powershell.md`: 컴퓨터 2(Y)에 전달할 PowerShell 실행 안내

## Run 01-pre main logger

컴퓨터 2(Y)에서 Arduino IDE Serial Monitor를 닫은 뒤 실행한다. 실제 serial logging에는 `pyserial`이 필요하다.
PowerShell 상세 실행 순서는 `run01_main_logger_computer2_powershell.md`를 따른다.

```bash
python run01_main_logger.py static_center_pre --run-id 2026-06-05_run01_pre_static_center_r01 --port COM3
```

serial 연결 없이 CSV 형식만 확인할 때는 `--dry-run`을 사용한다.

```bash
python run01_main_logger.py static_center_pre --run-id 2026-06-05_run01_pre_static_center_r01 --dry-run
```

현재 logger의 `theta*_meas`는 encoder 측정값이 아니라 `theta*_cmd`를 그대로 기록한 `command_echo_no_encoder`다. Run 01-pre pipeline validation에는 사용할 수 있지만, `error_z`를 외부 3D ground-truth 성능으로 해석하면 안 된다.
