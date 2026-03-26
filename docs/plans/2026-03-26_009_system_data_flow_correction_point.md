# Plan

## Goal
- `docs/system_data_flow.md`의 `Correction Injection Point` 섹션에 보정 주입 정책을 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- correction target을 `target_position`으로 명시한다.
- correction field 기본 이름을 `corr_x`, `corr_y`, `corr_z`로 채운다.
- correction unavailable 시 fallback 정책을 기본 초안으로 추가한다.

## Impact
- virtual sensor의 correction output이 제어 흐름 어디에 들어가는지 문서 기준이 고정된다.

## Risk
- 이후 controller 설계가 motor command 직접 보정을 요구하면 contract 재검토가 필요하다.

## Validation
- `docs/system_data_flow.md`에 correction target이 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
