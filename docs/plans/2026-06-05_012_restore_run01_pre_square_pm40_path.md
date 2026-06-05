# Plan

## Goal
Run 01-pre square 실행 조건을 `square_pm40_pre`로 되돌리고, square corner 순서를 `home -> 3사분면 -> 4사분면 -> 2사분면 -> 1사분면 -> home`으로 맞춘다.

## Files
- `docs/plans/2026-06-05_012_restore_run01_pre_square_pm40_path.md`
- `experiments/run01_main_logger.py`
- `experiments/run01_main_logger_computer2_powershell.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- Run 01-pre square trajectory를 `square_pm20_pre`에서 `square_pm40_pre`로 되돌린다.
- `square_pm40_pre`의 target corner order를 `home`, `(-40,-40)`, `(40,-40)`, `(-40,40)`, `(40,40)`, `home`으로 정의한다.
- `square_pm20_pre`는 main logger 선택지에서 제거한다.
- 컴퓨터 2 PowerShell 안내의 square 실행 명령과 run_id를 `pm40` 기준으로 되돌린다.
- vision 담당자에게 전달할 square run_id, corner order, gain 기록 조건을 Run 01 문서와 daily note에 남긴다.

## Impact
- CSV 포맷, run_id 형식, final dataset contract는 변경하지 않는다.
- correction off 원칙은 유지한다.
- Arduino gain `1.25`는 virtual sensing correction이 아니라 hardware calibration condition으로 유지한다.

## Risk
- `pm40` corner 이동은 `pm20`보다 이동 범위가 커서 link interference, vibration, marker occlusion 가능성이 더 크다.
- 기존 dry-run으로 생성된 `square_pm20_pre` 파일이 있으면 실제 run 파일과 혼동할 수 있다.

## Validation
- `square_pm40_pre` dry-run으로 target order와 theta range를 확인한다.
- `python3 -m py_compile experiments/run01_main_logger.py`로 구문을 확인한다.
- 수정 범위에 대해 `git diff --check`를 실행한다.
