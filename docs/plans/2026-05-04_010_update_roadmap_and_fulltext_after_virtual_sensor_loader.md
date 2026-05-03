# Plan

## Goal
`fake pipeline`과 `virtual_sensor`의 최소 데이터 경로 구현 상태를 `docs/roadmap.md`와 `fulltext.md`에 반영한다. 목적은 현재 구현 기준으로 Stage 진행도를 문서와 실제 리포 상태에 맞추는 것이다.

## Files
- `docs/roadmap.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `docs/roadmap.md`의 current status snapshot을 `2026-05-04` 기준으로 갱신한다.
- Stage 2에는 workspace sweep, angle range 정리까지 반영하고, Stage 3에는 FK 최소 구현과 IK↔FK round-trip 검증 반영, Stage 6에는 fake pipeline 및 virtual sensor loader/shape check 반영 상태를 추가한다.
- `fulltext.md`의 현재 상태 요약과 바로 다음 작업을 현재 구현 기준으로 갱신한다.
- `docs/daily_notes/2026-05-04.md`에 문서 반영 이유와 결과를 기록한다.

## Impact
- 로드맵 문서와 요약 문서가 실제 구현 상태를 더 정확히 나타내게 된다.
- 다음 작업 우선순위가 `virtual sensor baseline` 또는 `실제 데이터 수집 준비` 쪽으로 자연스럽게 이어진다.
- 데이터 계약이나 코드 인터페이스는 변경하지 않는다.

## Risk
- Stage 완료/진행중 판단이 과도하면 이후 우선순위 해석이 흔들릴 수 있다.
- 아직 실제 하드웨어/비전 데이터가 없으므로 fake pipeline 및 virtual sensor 관련 상태는 `최소 구현` 수준으로만 표현해야 한다.

## Validation
- 변경 후 `docs/roadmap.md`와 `fulltext.md`에서 현재 구현 상태가 상호 일관적인지 확인한다.
- fake pipeline과 virtual sensor loader의 현재 산출물 경로가 문서에 반영되었는지 확인한다.
