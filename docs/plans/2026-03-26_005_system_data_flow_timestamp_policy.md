# Plan

## Goal
- `docs/system_data_flow.md`의 `Timestamp Policy` 섹션에 팀이 합의한 시간 기록 정책을 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- timestamp source를 `both`로 명시한다.
- 누락 row 처리 규칙을 `invalid` 표기로 정의한다.
- 시간 포맷과 정렬 방식에 대한 기본 초안을 문서에 채운다.

## Impact
- 실물 데이터와 PC logger 데이터의 시간 정렬 기준이 고정된다.

## Risk
- 실제 로거 구현이 `boot_ms` 외 형식을 사용할 경우 후속 정합성 조정이 필요하다.

## Validation
- `docs/system_data_flow.md`에 `Timestamp Policy` 항목이 채워졌는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
