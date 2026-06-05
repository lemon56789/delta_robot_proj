# Plan

## Goal
Run 01-pre에서 관측된 비선형 추종 부족과 Arduino gain `1.25` 적용 판단을 문서화하고, 다음 square 실행을 `square_pm20_pre`로 맞춘다.

## Files
- `docs/plans/2026-06-05_011_record_run01_pre_gain_and_square_pm20.md`
- `experiments/run01_main_logger.py`
- `experiments/run01_main_logger_computer2_powershell.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- Run 01 문서에 Arduino position gain `1.25`를 Run 01-pre용 coarse hardware compensation으로 기록한다.
- 이 gain은 정밀 보정이나 virtual sensing correction이 아니라, 실제 이동량을 목표 범위 근처로 끌어올리는 하드웨어 1차 보정이라고 명시한다.
- 오차가 완전 선형이 아니므로 `40 mm -> 30 mm` 한 점 기준의 `1.33` 보정보다 `1.25`를 보수적으로 선택했다는 근거를 남긴다.
- `square_pm20_pre`를 main logger trajectory 선택지에 추가한다.
- Run 01-pre 다음 square 실행을 `x/y = +-20 mm` 코너 기준으로 문서와 PowerShell 안내에 반영한다.
- gain 적용 상태는 이후 데이터셋/metadata에 반드시 기록하고, gain이 다른 데이터는 섞지 않는다는 주의사항을 추가한다.

## Impact
- CSV 포맷, run_id 형식, final dataset contract는 변경하지 않는다.
- correction off 원칙은 유지한다.
- Arduino gain `1.25`는 virtual sensing correction이 아니라 hardware calibration condition으로 기록한다.

## Risk
- gain이 firmware에만 반영되고 metadata에 누락되면 같은 trajectory라도 시스템 조건이 다른 데이터가 섞일 수 있다.
- square corner에서는 cross보다 link interference, vibration, marker occlusion이 커질 수 있으므로 첫 실행은 관찰 우선으로 진행한다.

## Validation
- `square_pm20_pre` dry-run으로 CSV 생성과 timestamp 단조 증가를 확인한다.
- 계산된 theta가 provisional range `-45..90 deg` 안에 있는지 확인한다.
- `git diff --check`로 문서/코드 공백 오류를 확인한다.
