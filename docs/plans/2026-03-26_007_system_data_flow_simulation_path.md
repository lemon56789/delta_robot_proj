# Plan

## Goal
- `docs/system_data_flow.md`의 `Simulation Path Definition` 섹션에 시뮬레이션 기준 경로를 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- primary simulation source를 `Simscape`로 명시한다.
- simulation input/output 필드의 기본 초안을 채운다.
- `RecurDyn`는 secondary reference 용도로만 notes에 반영한다.

## Impact
- 데이터 흐름 문서에서 기준 시뮬레이터가 하나로 고정된다.

## Risk
- 이후 `RecurDyn`를 주 기준으로 병행 운영하려면 문서 구조를 다시 확장해야 할 수 있다.

## Validation
- `docs/system_data_flow.md`에 `Simulation Path Definition` 초안이 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
