# Plan

## Goal
델타 로봇 IK의 `2atan(t)` 기반 대수적 풀이 구조를 메모 형태로 정리하고, 논문식 일반 변수와 현재 프로젝트 좌표계 및 기구 변수 사이의 매핑 기준을 문서화한다.
현재 단계에서는 참고용 구조와 기호 연결만 정리하며, `E`, `F`, `G`의 최종 프로젝트 식 유도나 구현 채택안까지는 확정하지 않는다.

## Files
- `docs/plans/2026-04-06_006_ik_structure_note_and_variable_mapping.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/ik_structure_note.md`를 신규 작성한다.
- `2atan(t)` 기반 IK 풀이의 핵심 흐름을 길이 제약식, 삼각함수 방정식, 반각 치환, 해 복원 순으로 정리한다.
- 논문식 일반 표현과 프로젝트 좌표계(`base_frame`) 및 기구 변수(`B1~B3`, `P1~P3`, `L`, `l`, `uB`, `uP`, `wB`, `wP`)의 연결 관계를 문서화한다.
- arm index `i = 1, 2, 3` 관점에서 `theta_i`, `B_i`, `P_i`, end-effector center position의 의미를 정리한다.
- 아직 미확정인 항목은 `E`, `F`, `G`의 최종 식, 해 선택 규칙, 각도 범위, reject 조건으로 분리한다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- IK 구현 전 단계에서 수식 구조와 프로젝트 변수 관계를 팀이 같은 언어로 볼 수 있게 된다.
- 현재 IK 인터페이스 계약은 유지된다.
- 구현 기준과 reference 자료 사이의 간극을 줄일 수 있다.

## Risk
- 아직 유도되지 않은 식을 과도하게 확정적으로 쓰면 잘못된 기준 문서가 될 수 있다.
- reference 기반 메모와 프로젝트 채택안이 혼동되면 후속 구현에서 해석 차이가 생길 수 있다.

## Validation
- 문서가 `2atan(t)` 구조를 단계별로 명확히 설명하는지 확인한다.
- 변수 매핑이 현재 `docs/system_data_flow.md`의 좌표계와 기구 기호를 기준으로 일관되는지 확인한다.
- 미확정 항목이 확정된 것처럼 쓰이지 않았는지 검토한다.
