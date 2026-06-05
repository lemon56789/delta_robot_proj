# Plan

## Goal
실제 Run 01-pre 데이터와 혼동되는 `data/real/raw` dry-run 산출물을 삭제한다.

## Files
- `docs/plans/2026-06-06_001_remove_dry_run_real_raw_files.md`
- `docs/daily_notes/2026-06-06.md`
- `data/real/raw/main_2026-06-05_run01_pre_square_pm20_r01.csv`
- `data/real/raw/main_2026-06-05_run01_pre_square_pm20_r01.json`
- `data/real/raw/serial_2026-06-05_run01_pre_square_pm20_r01.txt`
- `data/real/raw/main_2026-06-05_run01_pre_square_pm40_r01.csv`
- `data/real/raw/main_2026-06-05_run01_pre_square_pm40_r01.json`
- `data/real/raw/serial_2026-06-05_run01_pre_square_pm40_r01.txt`

## Changes
- JSON metadata에서 `"dry_run": true`로 확인된 real/raw main CSV, metadata JSON, serial TXT만 삭제한다.
- 실제 run으로 확인된 `static_center`와 `cross_pm40` 파일은 유지한다.
- vision raw CSV는 삭제하지 않는다.

## Impact
- square vision raw 파일은 유지되지만, square real/raw main 파일은 실제 run 파일을 다시 받아와야 한다.
- dry-run 산출물이 실제 데이터셋에 섞일 위험을 줄인다.

## Risk
- 같은 run_id의 실제 square main 파일을 아직 다시 받기 전까지 square main/vision alignment는 진행할 수 없다.

## Validation
- 삭제 전 JSON metadata의 `"dry_run": true`를 확인한다.
- 삭제 후 `data/real/raw` 목록에서 해당 6개 파일이 없는지 확인한다.
- `static_center`, `cross_pm40`, vision raw 파일이 남아 있는지 확인한다.
