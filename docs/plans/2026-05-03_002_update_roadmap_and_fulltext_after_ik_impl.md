# Plan

## Goal
`docs/roadmap.md`와 `fulltext.md`를 현재 리포지토리 상태에 맞게 갱신해, nominal geometry parameter 확정과 inverse kinematics 최소 구현 완료 사실을 반영한다.

## Files
- `docs/roadmap.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-03.md`

## Changes
- `docs/roadmap.md`에 현재 Stage 진행 상태를 실제 구현 기준으로 갱신한다.
- `docs/roadmap.md`의 Stage 2 관련 설명에 nominal geometry parameter 정의와 IK 최소 구현 완료 상태를 반영한다.
- `fulltext.md`의 IK 관련 상태 요약을 현재 코드 기준으로 수정한다.
- `fulltext.md`의 현재 상태 요약과 바로 다음 작업 항목을 FK 검증 및 sample/workspace 검증 중심으로 갱신한다.
- 변경 기록을 `docs/daily_notes/2026-05-03.md`에 추가한다.

## Impact
- 문서와 실제 구현 상태 사이의 불일치를 줄인다.
- 이후 작업자가 현재 프로젝트 위치를 문서만 읽고도 정확히 파악할 수 있게 된다.
- 코드, 데이터 포맷, 인터페이스 계약은 변경하지 않는다.

## Risk
- 진행 상태 표현이 과장되면 실제 구현 범위보다 완료도가 높게 읽힐 수 있다.
- Stage 2와 Stage 3 경계를 모호하게 쓰면 다음 작업 우선순위가 흐려질 수 있다.

## Validation
- 문서에 적힌 현재 상태가 실제 파일 상태와 일치하는지 검토한다.
- `kinematics/geometry.py`, `kinematics/inverse_kinematics.py` 존재와 역할이 문서에 정확히 반영됐는지 확인한다.
- 다음 작업이 FK 검증 및 sample/workspace 검증으로 자연스럽게 이어지는지 확인한다.
