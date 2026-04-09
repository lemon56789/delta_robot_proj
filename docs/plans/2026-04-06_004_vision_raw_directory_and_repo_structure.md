# Plan

## Goal
비전 raw 로그 저장 경로를 실제 리포지토리 디렉터리로 생성하고, README와 비전 문서의 폴더 구조 설명에 해당 경로를 반영한다.
문서에 정의된 `data/vision/raw/` 정책과 실제 리포 구조를 일치시킨다.

## Files
- `docs/plans/2026-04-06_004_vision_raw_directory_and_repo_structure.md`
- `README.md`
- `docs/vision_tracking.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `data/vision/raw/` 디렉터리를 생성한다.
- `README.md`의 폴더 구조 섹션에 `data/vision/raw/` 경로를 최소 범위로 반영한다.
- `docs/vision_tracking.md`의 저장 경로 설명에 실제 생성된 경로를 기준 경로로 명시한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- 비전 raw 로그를 저장할 실제 경로가 리포지토리에 생긴다.
- README와 비전 문서가 같은 저장 경로를 참조하게 된다.
- 메인 CSV 계약과 시스템 데이터 흐름은 변경되지 않는다.

## Risk
- README 폴더 구조를 너무 상세하게 적으면 향후 구조 변경 시 유지보수 부담이 생길 수 있다.
- 디렉터리만 생성하고 실제 파일명 규칙을 따르지 않으면 문서와 구현이 다시 어긋날 수 있다.

## Validation
- `data/vision/raw/` 디렉터리가 실제로 생성되었는지 확인한다.
- README와 `docs/vision_tracking.md`가 동일한 경로를 가리키는지 확인한다.
- 변경이 메인 시스템 계약이나 CSV 구조를 건드리지 않았는지 검토한다.
