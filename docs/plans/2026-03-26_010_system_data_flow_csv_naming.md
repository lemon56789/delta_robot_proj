# Plan

## Goal
- `docs/system_data_flow.md`의 CSV 관련 필드 명명 방향을 `theta_*`, `error_*` 기준으로 정리한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- correction field 초안을 `corr_x`, `corr_y`, `corr_z`에서 `error_x`, `error_y`, `error_z`로 변경한다.
- 이후 CSV Contract 초안이 `theta_*`와 `error_*` 기준을 따르도록 문서 방향을 맞춘다.

## Impact
- IK, measurement, correction, CSV naming이 같은 의미 체계로 정리된다.

## Risk
- `error_*`가 correction command인지 residual error인지 혼동될 수 있어 notes에서 의미를 보강해야 할 수 있다.

## Validation
- `docs/system_data_flow.md`에서 correction field가 `error_*`로 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
