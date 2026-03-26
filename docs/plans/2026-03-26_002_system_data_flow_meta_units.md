# Plan

## Goal
- `docs/system_data_flow.md`의 `Meta` 및 `Units & Coordinate Frame` 초안 작성을 지원하기 위해 확정된 기준값을 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- `angle unit`을 `deg`로 명시한다.
- 좌표계 방향 정의에서 작업 공간 방향을 `-Z`로 명시한다.
- 원점을 `base center (O)`로 정의한다.

## Impact
- 이후 IK, CSV, simulation, correction 문서 작성의 기준 좌표계와 단위가 고정된다.

## Risk
- `+X`, `+Y` 방향이 아직 팀 기준으로 확정되지 않으면 후속 정합성 검토가 필요하다.

## Validation
- `docs/system_data_flow.md`에 확정된 값이 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
