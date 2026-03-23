# Plan

## Goal
외부 AI 입력용 팀원별 프로필 문서를 분리해, 공통 컨텍스트는 `fulltext.md`에 유지하고 팀원 최적화 정보는 별도 문서로 관리할 수 있게 한다.

## Files
- `docs/plans/2026-03-22_001_member_profiles.md`
- `docs/member_profiles/README.md`
- `docs/member_profiles/S.md`
- `docs/member_profiles/L.md`
- `docs/member_profiles/Y.md`
- `docs/member_profiles/T.md`
- `docs/member_profiles/N.md`
- `docs/daily_notes/2026-03-22.md`

## Changes
- `docs/member_profiles/` 디렉터리를 생성한다.
- 팀원 프로필 문서의 목적, 사용 방법, 공통 작성 원칙을 `README.md`에 정리한다.
- 현재 `README.md`의 팀원 역할 표를 기준으로 5명의 프로필 문서를 생성한다.
- 오늘 작업에 대한 기록을 Daily Note에 추가한다.

## Impact
- `fulltext.md`는 프로젝트 공통 컨텍스트 전용 문서로 유지된다.
- 팀원별 역할/관심사/우선순위를 독립적으로 관리할 수 있다.
- 외부 AI 입력 시 공통 문서와 개인화 문서를 조합하는 운영 방식이 명확해진다.

## Risk
- 현재 팀원별 상세 선호도 정보가 제한적이어서 초기 프로필은 역할 중심의 1차 버전이 된다.
- 역할이 바뀌면 각 프로필 문서를 함께 갱신해야 한다.

## Validation
- 생성된 문서 경로와 파일명을 검토한다.
- 각 프로필 문서가 역할, 담당 범위, 주요 폴더, 도구, AI 지원 유형, 답변 우선순위를 포함하는지 확인한다.
- `docs/daily_notes/2026-03-22.md`에 변경 내역이 기록되었는지 확인한다.
