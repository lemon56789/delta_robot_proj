# Plan

## Goal
- `docs/system_data_flow.md`의 `Real-Sim Alignment Policy` 섹션에 시간 정렬 기준을 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- alignment reference clock을 `PC logger`로 명시한다.
- resampling method를 `linear interpolation`으로 반영한다.
- delay compensation을 `post-alignment`로 정의한다.
- `invalid` row 제외 정책과 serial delay 한계를 notes에 추가한다.

## Impact
- 실물 데이터와 simulation 데이터를 후처리에서 어떻게 정렬할지 문서 기준이 고정된다.

## Risk
- 고속 제어 검증에서는 `PC logger` 기준이 실제 장치 시간과 차이를 만들 수 있다.

## Validation
- `docs/system_data_flow.md`에 alignment policy가 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
