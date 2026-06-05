# Plan

## Goal
Run 01-pre square 이동 궤적을 최신 순서로 갱신한다.

## Files
- `docs/plans/2026-06-05_013_update_square_pm40_latest_path.md`
- `experiments/run01_main_logger.py`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- `square_pm40_pre` point order를 `home -> (40,40) -> (-40,40) -> (-40,-40) -> (40,-40) -> (40,40) -> home`으로 변경한다.
- Run 01 문서의 `square_pm40_pre` target order와 vision handoff 내용을 최신 경로로 갱신한다.
- daily note에 변경 이유와 결과를 기록한다.

## Impact
- CSV 포맷, run_id 형식, logger CLI 이름은 변경하지 않는다.
- trajectory 내부 point order만 변경한다.

## Risk
- vision logger 또는 operator note가 이전 corner order를 기준으로 되어 있으면 segment 해석이 어긋날 수 있다.
- 같은 run_id로 dry-run 파일이 생성되어 있으면 실제 run 파일과 혼동할 수 있다.

## Validation
- `square_pm40_pre` dry-run으로 target order와 theta range를 확인한다.
- `python3 -m py_compile experiments/run01_main_logger.py`로 구문을 확인한다.
- 수정 범위에 대해 `git diff --check`를 실행한다.
