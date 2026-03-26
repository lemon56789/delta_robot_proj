# Plan

## Goal
- `docs/system_data_flow.md`의 좌표계 미정 항목을 팀 합의 기준으로 확정한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- `+X`, `+Y`, `+Z` 방향을 사용자 제공 정의에 맞춰 명시한다.
- base/platform/링크 관련 기호 정의를 `Units & Coordinate Frame` 비고에 추가한다.

## Impact
- IK, geometry, simulation 문서에서 동일한 좌표축과 기호를 재사용할 수 있다.

## Risk
- 현재 정의가 다른 문서 또는 기존 수식 구현과 다를 경우 후속 정합성 검토가 필요하다.

## Validation
- `docs/system_data_flow.md`에 `TBD`가 제거되었는지 확인
- 축 방향과 기호 정의가 사용자 제공 내용과 일치하는지 확인
