# Plan

## Goal
`workspace_sweep.py` 실행 시 CSV 결과와 함께 sweep 설정 및 요약 통계를 담은 sidecar JSON 파일을 자동 생성해, 결과 파일만으로도 실행 범위와 검증 조건을 재현할 수 있게 한다.

## Files
- `kinematics/workspace_sweep.py`
- `kinematics/README.md`
- `experiments/kinematics/workspace_sweep_default_2026-05-04.json`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `workspace_sweep.py`에 JSON sidecar 저장 기능을 추가한다.
- JSON에는 최소한 sweep 범위, step, round-trip tolerance, total/ok/fail count, reason별 count, max/avg round-trip error, max FK iteration을 기록한다.
- CSV 저장 경로가 주어지면 같은 stem 이름의 `.json` 파일을 함께 저장하도록 한다.
- `kinematics/README.md`에 CSV + JSON 결과 저장 동작을 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유, 결과 파일 경로, 메타데이터 구조를 기록한다.

## Impact
- sweep 결과 재현성이 좋아진다.
- 이후 finer sweep, boundary scan, ik_reject 분석 결과와 baseline coarse sweep를 쉽게 비교할 수 있다.
- CSV 포맷 자체는 유지되므로 기존 결과 활용 방식은 깨지지 않는다.

## Risk
- JSON 스키마를 너무 자주 바꾸면 이후 비교 스크립트 작성 시 혼선이 생길 수 있다.
- CSV 저장 없이 JSON만 생성하는 흐름이 필요할지 여부는 아직 미정이다.

## Validation
- 기본 coarse sweep 실행 시 CSV와 같은 stem의 JSON 파일이 생성되는지 확인한다.
- JSON 안의 범위/step/통계가 터미널 요약과 일치하는지 확인한다.
- README와 Daily Note가 새 저장 구조를 반영하는지 확인한다.
