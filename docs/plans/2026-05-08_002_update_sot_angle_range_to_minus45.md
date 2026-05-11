# Plan

## Goal
현재 SoT 문서에서 `theta_i` 임시 운용 범위를 `0..90 deg`에서 `-45..90 deg`로 갱신해, 현재 프로젝트의 설치 높이 및 workspace 검토 기준과 일치시키고 `hardware-confirmed`는 별도 미확정 상태로 유지한다.

## Files
- `docs/plans/2026-05-08_002_update_sot_angle_range_to_minus45.md`
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- `docs/roadmap.md`
- `docs/workspace_envelope.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-08.md`

## Changes
- `hardware-safe provisional angle limits`를 `-45 deg <= theta_i <= 90 deg`로 갱신한다.
- `nominal-analysis angle limits`도 같은 범위로 정렬한다.
- `hardware-confirmed angle limits`는 여전히 미확정으로 유지한다.
- workspace envelope 문서의 주의 문구를 현재 SoT 상태에 맞게 수정한다.
- 오늘 변경 근거를 daily note에 추가 기록한다.

## Impact
- 현재 문서상의 임시 운용 범위와 설치/작업공간 검토 문서가 서로 일치한다.
- 기존 데이터 포맷, 함수 계약, 폴더 구조는 변경하지 않는다.

## Risk
- 실제 하드웨어 구동 검증 전이므로 `hardware-confirmed`와 `hardware-safe provisional`을 혼동하면 안 된다.
- 과거 daily note/plan 문서에는 이전 판단 기준이 남아 있으므로, 현재 기준 문서는 최신 date 기준으로 읽어야 한다.

## Validation
- `docs/system_data_flow.md`, `docs/ik_structure_note.md`, `docs/roadmap.md`, `docs/workspace_envelope.md`, `fulltext.md`에서 현재 기준 표현이 서로 모순되지 않는지 확인한다.
- `hardware-confirmed = not yet finalized`, `provisional = -45..90 deg` 구조가 유지되는지 확인한다.
