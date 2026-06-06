# Plan

## Goal
Computer 2에서 생성해 저장소 루트로 가져온 Run 02 dry-run schedule CSV 4개를
Simscape 입력 전용 폴더에 정리한다.

## Files
- `schedule_exports/main_schedule_cross_pm30.csv`
- `schedule_exports/main_schedule_reverse_grid_3x3_pm40.csv`
- `schedule_exports/main_schedule_diamond_pm35.csv`
- `schedule_exports/main_schedule_circle_r40.csv`
- `docs/daily_notes/2026-06-06.md`
- `docs/plans/2026-06-06_021_store_run02_schedule_exports.md`

## Changes
- 저장소 루트에 있는 `main_schedule_*.csv` 4개를 `schedule_exports/`로 이동한다.
- CSV 내용과 파일명은 변경하지 않는다.
- 이동 전후 SHA-256을 비교한다.

## Impact
- Simscape 입력 스케줄과 실제 하드웨어 raw 데이터를 경로상 분리한다.
- CSV 데이터 포맷과 Run 02 실행 코드는 변경하지 않는다.

## Risk
- 이동 중 파일명이 바뀌거나 내용이 변경되면 Simscape 입력 재현성이 손상될 수 있다.

## Validation
- 네 파일이 저장소 루트에서 제거되고 `schedule_exports/`에 존재하는지 확인한다.
- 데이터 행 수가 cross 450, reverse grid 550, diamond 350, circle 500인지 확인한다.
- 이동 전후 SHA-256이 동일한지 확인한다.
