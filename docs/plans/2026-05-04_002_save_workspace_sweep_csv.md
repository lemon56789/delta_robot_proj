# Plan

## Goal
현재 `workspace_sweep.py`의 기본 coarse sweep 결과를 CSV 파일로 저장해, 진행 상태와 reachable/invalid 분포를 파일 기반으로 확인할 수 있게 한다.

## Files
- `experiments/kinematics/workspace_sweep_default_2026-05-04.csv`
- `docs/daily_notes/2026-05-04.md`

## Changes
- 기본 `workspace_sweep.py` 실행 결과를 CSV로 저장한다.
- 출력 경로는 검증 결과물 성격에 맞춰 `experiments/kinematics/` 아래로 둔다.
- 현재 기본 실행 범위 `x,y=-30..30 mm`, `z=-260..-180 mm`, coarse step 결과를 저장한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 저장 이유, 경로, 실행 범위를 기록한다.

## Impact
- 터미널 출력만 있던 검증 결과가 파일로 남아 이후 비교와 시각화에 바로 사용할 수 있게 된다.
- 다음 단계에서 `z` slice별 분석이나 finer sweep 결과와 비교하기 쉬워진다.
- 코드, 인터페이스, 데이터 계약은 변경하지 않는다.

## Risk
- 기본 coarse sweep 결과만 저장하므로 경계 상세 정보는 부족할 수 있다.
- 출력 파일명이 sweep 설정과 다르면 나중에 비교 시 혼선이 생길 수 있다.

## Validation
- CSV 파일이 실제로 생성되는지 확인한다.
- 헤더와 row 수가 기본 sweep 결과와 일치하는지 확인한다.
- `ok`/`fail` 및 `reason` 컬럼이 기대대로 기록되는지 확인한다.
