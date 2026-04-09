# Plan

## Goal
IK 관련 논문을 프로젝트 채택안으로 선언하지 않고 참고 자료로만 보관할 수 있도록 `docs/references/` 경로를 추가한다.
논문 파일의 역할을 reference로 한정하고, 현재 SoT 문서와 구현 기준은 그대로 유지한다.

## Files
- `docs/plans/2026-04-06_005_reference_directory_for_ik_papers.md`
- `docs/references/README.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/references/` 디렉터리를 생성한다.
- `docs/references/README.md`를 추가해 이 경로가 참고 자료 보관용이며 프로젝트 채택안을 의미하지 않는다고 명시한다.
- IK 관련 논문을 이 경로에 저장할 수 있다는 기준과 파일명 작성 방향을 간단히 정리한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- IK 논문을 리포지토리 안에 reference로 정리할 수 있는 위치가 생긴다.
- 현재 SoT, CSV 계약, 시스템 구조, IK 인터페이스는 변경되지 않는다.
- 이후 구현 시 참고 출처를 리포 안에서 바로 찾을 수 있다.

## Risk
- reference와 프로젝트 채택 기준이 섞여 보이면 문서 해석이 흔들릴 수 있다.
- 논문 파일명 규칙이 불명확하면 자료 검색성이 떨어질 수 있다.

## Validation
- `docs/references/` 디렉터리와 안내 문서가 실제로 생성되었는지 확인한다.
- README 문구가 reference와 project decision을 명확히 구분하는지 확인한다.
- 기존 SoT 문서나 구현 기준을 변경하지 않았는지 검토한다.
