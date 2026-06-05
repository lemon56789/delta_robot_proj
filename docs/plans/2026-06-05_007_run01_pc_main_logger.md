# Plan

## Goal
컴퓨터 2(Y)에서 Arduino serial을 열어 Run 01-pre main log CSV를 저장할 수 있는 PC-side logger를 작성한다.

## Files
- `docs/plans/2026-06-05_007_run01_pc_main_logger.md`
- `experiments/run01_main_logger.py`
- `experiments/README.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- `experiments/run01_main_logger.py`를 추가한다.
- logger는 `static_center_pre`, `cross_pm10_pre`, `square_pm10_pre` trajectory를 지원한다.
- Arduino에는 `ALL theta1 theta2 theta3` serial command를 전송한다.
- main CSV는 `run_id`, `time`, `target_*`, `theta*_cmd`, `theta*_meas`, `valid` 최소 필드를 포함한다.
- 현재 encoder가 없으므로 `theta*_meas`는 실제 측정값이 아니라 `command_echo_no_encoder`로 기록한다.
- Arduino `millis()`가 serial output에 없으므로 `time`은 PC logger 기준 elapsed ms로 기록하고 `time_source=pc_elapsed_ms`를 metadata에 남긴다.
- `--dry-run` 모드로 serial 연결 없이 CSV 형식과 trajectory command를 검증할 수 있게 한다.

## Impact
- Python 실험 실행 스크립트를 추가한다.
- Arduino firmware, CSV final contract, control interface는 변경하지 않는다.
- Run 01-pre에서 main/vision log의 같은 `run_id` 저장을 검증할 수 있다.

## Risk
- 컴퓨터 2에 `pyserial`이 설치되어 있지 않으면 실제 serial logging은 실행되지 않는다.
- Arduino IDE Serial Monitor가 열려 있으면 Python이 COM port를 열 수 없다.
- 현재 `theta*_meas`는 encoder 측정값이 아니므로 `error_z`를 외부 ground-truth 성능으로 해석하면 안 된다.
- 컴퓨터 2에 repo 전체가 없을 수 있으므로 script는 필요한 IK 계산을 자체 포함한다.

## Validation
- `python experiments/run01_main_logger.py --dry-run ...`으로 CSV와 metadata 생성을 확인한다.
- 생성된 CSV에 minimum main log columns가 있는지 확인한다.
- `git diff --check`로 문서/코드 공백 오류를 확인한다.
