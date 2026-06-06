# experiments

실험 계획, 실행 로그, 성능 검증 결과를 관리하는 폴더입니다.

현재 포함 예시:
- `fake_pipeline.py`: 실제 하드웨어 없이 end-to-end fake dataset을 생성하는 스크립트
- `run01_main_logger.py`: 컴퓨터 2(Y)에서 Arduino serial에 `ALL theta1 theta2 theta3` 명령을 보내고 Run 01 main CSV를 저장하는 PC-side logger
- `run01_main_logger_computer2_powershell.md`: 컴퓨터 2(Y)에 전달할 PowerShell 실행 안내
- `run01_preprocess.py`: Run 01 raw main, vision, Simscape CSV를 읽어 angle-derived measured position과 processed merged dataset을 생성하는 스크립트

## Run 01 main logger

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

Run 01-main/holdout trajectory도 같은 logger로 실행한다.

지원 trajectory:
- pre: `static_center_pre`, `cross_pm10_pre`, `square_pm10_pre`, `cross_pm40_pre`, `square_pm40_pre`
- main: `static_center_hold`, `cross_pm20`, `square_pm20`, `circle_r40`, `grid_3x3_pm40`
- holdout: `cross_pm15_holdout`, `square_pm15_holdout`, `circle_r40_holdout`

`circle_r40`은 home -> `(40, 0)` -> 반지름 `40 mm` 반시계 방향 원 -> home 순서다. 원 회전 시간은 아직 고정하지 않았으므로 `--circle-duration-s`로 지정하고 metadata에 남긴다. 현재 Arduino serial protocol은 setpoint command만 지원하므로 logger는 원을 여러 setpoint로 나누어 천천히 전송한다.

## Run 01 preprocessing

Run 01-pre에서 검증된 후처리 흐름은 아래 스크립트를 사용한다.

```bash
python experiments/run01_preprocess.py --run-id 2026-06-05_run01_pre_cross_pm40_r01
```

입력 파일:
- `data/real/raw/main_<run_id>.csv`
- `data/vision/raw/vision_<run_id>.csv`
- `data/simulation/raw/simscape_<run_id>.csv`

출력 파일:
- `data/real/derived/measured_position_<run_id>.csv`
- `data/processed/merged_<run_id>.csv`

Run 01-main/holdout에서도 같은 후처리 흐름을 재사용한다. Run 01-main/holdout 수집용 main logger trajectory는 `run01_main_logger.py`에 포함되어 있다.
