# Plan

## Goal
Run 00 문서에 실험 전 확정/보류 상태를 반영한다.

## Files
- `docs/plans/2026-06-04_004_update_run_00_pending_values.md`
- `docs/hardware_experiment_run_00_commissioning.md`
- `docs/daily_notes/2026-06-04.md`

## Changes
- `z0`는 A 단계 수행 후 기록하는 값으로 명시한다.
- firmware path/status는 Y 확인 전까지 보류로 둔다.
- main/vision logger 저장 경로는 `data/real/raw/main_<run_id>.csv`, `data/vision/raw/vision_<run_id>.csv`로 기록한다.
- vision calibration/homography file은 다음 정보 수신 전까지 보류로 둔다.

## Impact
- Run 00 문서의 실험 전 준비 상태만 갱신한다.
- 코드, CSV 계약, 제어 인터페이스는 변경하지 않는다.

## Risk
- firmware와 vision calibration 정보가 보류 상태이므로, 실제 motor-powered test 또는 C 단계 실행 전 추가 확인이 필요하다.

## Validation
- Run 00 문서에 보류/확정 상태가 명확히 반영되었는지 확인한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
