# Team Member Profiles

## Purpose
이 디렉터리는 외부 AI에 팀원별 맥락을 추가로 제공하기 위한 프로필 문서를 보관한다.

`fulltext.md`는 프로젝트 공통 컨텍스트를 설명하고, 이 디렉터리의 문서는 팀원별 역할과 우선순위를 설명한다.

## Usage
외부 AI 입력 시 다음 조합을 권장한다.

- 공통 이해: `fulltext.md`
- 팀원 최적화: 해당 팀원 프로필 문서 1개

예시:
- `fulltext.md` + `docs/member_profiles/L.md`
- `fulltext.md` + `docs/member_profiles/Y.md`

## Prompt Pattern
권장 입력 순서는 아래와 같다.

1. `fulltext.md`
2. 팀원 프로필 문서 1개
3. 팀원 프로필 문서의 `AI Prompt Seed` 한 줄
4. 현재 작업 요청

예시:
- `fulltext.md`
- `docs/member_profiles/L.md`
- `L은 시스템 통합과 가상센싱 관점에서 답변을 원한다. 제어 흐름, 데이터 계약, 시뮬레이션과 실측의 연결 구조를 우선해서 설명하라.`
- 현재 작업 요청

## Authoring Rules
- 프로젝트 공통 규칙은 `fulltext.md`와 원문 SoT 문서(`docs/*`, `AGENTS.md`)에 둔다.
- 이 디렉터리에는 팀원별 역할, 작업 범위, AI 지원 우선순위만 기록한다.
- 데이터 포맷, 인터페이스, 시스템 구조 같은 계약 정보는 여기서 정의하지 않는다.
- 역할 변경 시 해당 팀원 문서만 갱신한다.

## Files
- `S.md`: 동역학 해석, 진동 분석
- `L.md`: 시스템 통합, 가상센싱
- `Y.md`: 아두이노 제어
- `T.md`: 기구 설계
- `N.md`: 구조/응력 해석
