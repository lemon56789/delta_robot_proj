# experiments

실험 계획, 실행 로그, 성능 검증 결과를 관리하는 폴더입니다.

현재 포함 예시:
- `fake_pipeline.py`: 실제 하드웨어 없이 end-to-end fake dataset을 생성하는 스크립트
- `run01_main_logger.py`: 컴퓨터 2(Y)에서 Arduino serial에 `ALL theta1 theta2 theta3` 명령을 보내고 Run 01 main CSV를 저장하는 PC-side logger
- `run01_main_logger_computer2_powershell.md`: 컴퓨터 2(Y)에 전달할 PowerShell 실행 안내
- `run01_preprocess.py`: Run 01 raw main, vision, Simscape CSV를 읽어 angle-derived measured position과 processed merged dataset을 생성하는 스크립트
- `run02_offline_validate.py`: serial 없이 gain/clamp 후보, corrected-target
  IK, fallback을 Run 01-main/holdout에서 replay하는 검증기
- `run02_logger.py`: 확정된 Run 02 24회 matrix의 deterministic OFF/ON
  serial logger와 manifest 생성기
- `run02_preprocess.py`: Run 02의 phase 없는 vision log를 trajectory
  event로 정렬하고 24개 merged dataset과 12개 OFF/ON comparison
  report를 생성하는 스크립트
- `test_run02_preprocess.py`: step/circle anchor와 marker-gap interpolation
  제한을 검증하는 단위 테스트
- `run02_logger_computer2_powershell.md`: Computer 2 실행 안내
- `run02_computer2_codex_handoff.md`: Git 없이 Computer 2 실행 환경을
  재구성하는 Codex용 독립형 인수인계
- `home_repeatability_computer2_codex_handoff.md`: `+40/+60 mm` X preload
  후 home 반복성을 6개 확정 run ID로 측정하는 Computer 2 Codex용
  독립형 지시서
- `home_repeatability_vision_windows_codex_handoff.md`: 같은 6개 run의
  vision raw CSV를 Windows에서 기록하고 품질 검사하는 Vision Codex용
  독립형 지시서

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
- current main: `static_center_hold`, `cross_pm40`, `square_pm40`, `circle_r40`, `grid_3x3_pm40`
- current holdout: `static_center_holdout`, `cross_pm30_holdout`, `square_pm30_holdout`, `circle_r40_holdout`, `grid_3x3_pm40_holdout`
- compatibility: `cross_pm20`, `square_pm20`, `cross_pm15_holdout`, `square_pm15_holdout`

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

## Run 02 offline correction validation

```bash
python3 experiments/run02_offline_validate.py
```

기본 후보는 gain `0.25/0.5/1.0`, XY vector clamp `2/4/6 mm`다. main은
configuration safety 분석에 사용하고, holdout은 replay/IK 호환성만
확인한다. 검증기는 holdout `error_*` label을 읽지 않는다.

산출물:

- `experiments/results/run02_correction_offline_validation_2026-06-06.json`

현재 main-only 초기 hardware gate 후보는 gain `0.25`, XY clamp `2 mm`다.
이 단계는 serial command를 전송하지 않는다.

## Run 02 serial logger

24개 run ID manifest:

```bash
python3 experiments/run02_logger.py manifest \
  --date 2026-06-07 \
  --output experiments/run02_24_run_manifest.json
```

OFF dry-run:

```bash
python3 experiments/run02_logger.py run cross_pm30 \
  --correction off \
  --run-id 2026-06-07_run02_cross_pm30_off_r01 \
  --dry-run
```

ON 실행은 deterministic schedule과 time axis가 정확히 같은 nominal
Simscape CSV가 필수다.

```bash
python3 experiments/run02_logger.py run cross_pm30 \
  --correction on \
  --run-id 2026-06-07_run02_cross_pm30_on_r01 \
  --simscape-csv data/simulation/raw/simscape_run02_nominal_cross_pm30.csv \
  --port COM3
```

최종 matrix는 cross, reverse grid, diamond, circle 각각 OFF/ON 3회로
총 24회다. 기본값은 gain `0.25`, XY clamp `2 mm`, waypoint hold `5 s`,
circle `72` points / `30 s`, circle start/end hold `2 s`다.

## Run 02 preprocessing and comparison

24개 raw run과 네 개 nominal Simscape CSV를 한 번에 처리한다.

```bash
PYTHONPATH=venv/lib/python3.12/site-packages \
python3 experiments/run02_preprocess.py
```

일반 Python 환경에 `numpy`가 설치되어 있으면 `PYTHONPATH` 지정은
필요하지 않다.

정렬 정책:

- cross/reverse-grid/diamond: 첫 vision position jump를 첫 main phase
  전환에 맞추고 모든 후속 jump residual이 `500 ms` 이내인지 검증한다.
- circle: 시작 hold에서 원운동으로 출발하는 최초 persistent departure를
  main의 첫 `circle_ccw_*` 시작에 맞춘다. 종료 hold는 별도로 검증하며
  time warping은 적용하지 않는다.
- 유효 vision sample 간격이 `500 ms`를 초과하면 해당 구간은 보간하지
  않는다.

산출물:

- `data/real/derived/measured_position_<run_id>.csv`
- `data/processed/merged_<run_id>.csv`
- `data/processed/alignment_<run_id>.json`
- `experiments/results/run02_comparison_2026-06-07.json`

비교는 같은 trajectory/repetition OFF/ON의 공통 timestamp에서 수행한다.
주 지표는 `tracking_xy_rmse`이며 trajectory별 세 repetition과 전체
trajectory를 동일 가중한다.
