# Plan

## Goal
`docs/workspace_envelope.md`를 추가해 2026-05-08 기준 설치 높이와 `XY` 작업공간 계산 결과를 재사용 가능한 문서로 정리한다.

## Files
- `docs/plans/2026-05-08_001_workspace_envelope_doc.md`
- `docs/workspace_envelope.md`
- `docs/daily_notes/2026-05-08.md`

## Changes
- 현재 nominal geometry와 좌표계 기준을 바탕으로 workspace envelope 요약 문서를 작성한다.
- `theta = -45..90 deg` 확장 범위를 설치 높이 탐색용 가정으로 명시한다.
- 최대 `XY` 단면이 나오는 `z`, `H=255/265/290 mm` 비교, `H=290 mm` 바닥 기준 단면 표를 정리한다.
- 오늘 문서화 작업을 daily note에 기록한다.

## Impact
- 설치 높이, 바닥 여유, 작업면 선택에 대한 설계 판단 근거가 문서로 남는다.
- 기존 데이터 계약이나 인터페이스는 변경하지 않는다.

## Risk
- `theta = -45..90 deg`는 현재 hardware-safe SoT 범위가 아니므로, 이를 최종 하드웨어 운용 범위로 오해하면 안 된다.
- `platform-ground clearance`는 platform 기준점 가정이므로 실제 그리퍼 팁 높이와는 차이가 날 수 있다.

## Validation
- 문서의 수치가 오늘 계산한 `z=-175 mm`, `H=255/265/290 mm` 결과와 일치하는지 확인한다.
- 문서 안에 재현용 커맨드와 가정이 포함되어 있는지 점검한다.
