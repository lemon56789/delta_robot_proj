# Plan

## Goal
`simulation/` 아래에 `simulink/` 하위 폴더를 추가해, Simulink 관련 원본 파일을 별도 영역에 정리할 최소 구조를 마련한다.

## Files
- `docs/plans/2026-05-27_001_add_simulink_subfolder.md`
- `simulation/README.md`
- `simulation/simulink/README.md`
- `docs/daily_notes/2026-05-27.md`

## Changes
- 오늘 작업용 계획서를 추가한다.
- `simulation/README.md`에 `Simulink`를 포함한 폴더 목적을 반영한다.
- `simulation/simulink/README.md`를 추가해 Git이 추적할 수 있는 하위 폴더를 만든다.
- `docs/daily_notes/2026-05-27.md`에 이번 변경의 목적과 결과를 기록한다.

## Impact
- Simulink 관련 파일을 `simulation/simulink/` 아래에 모아 둘 기준점이 생긴다.
- 현재 상대경로 의존성이 있는 `.slx`와 보조 파일을 같은 하위 폴더 아래에 보관할 수 있다.
- 데이터 계약, 인터페이스, 제어 흐름은 변경하지 않는다.

## Risk
- 현재는 빈 구조와 안내 문서만 추가하므로 기능적 리스크는 낮다.
- 이후 실제 파일을 옮길 때 외부 MATLAB 작업 디렉터리 기준과 경로 의존성을 다시 확인해야 한다.

## Validation
- `simulation/simulink/README.md`가 생성되었는지 확인한다.
- `simulation/README.md`가 `Simulink` 포함 목적과 모순되지 않는지 확인한다.
- Daily Note에 무엇을, 왜, 어떻게, 결과, 다음 작업이 기록되었는지 확인한다.
