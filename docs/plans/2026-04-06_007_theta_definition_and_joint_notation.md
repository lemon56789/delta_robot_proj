# Plan

## Goal
`theta_i`의 기준 자세와 양의 회전 방향을 문서에 반영하고, `J_i`를 IK 유도용 보조기호로 정의한다.
arm 1 기준으로 `J_1(theta_1)`의 메모 수준 좌표식을 추가해 후속 `E`, `F`, `G` 유도 준비를 한다.

## Files
- `docs/plans/2026-04-06_007_theta_definition_and_joint_notation.md`
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/system_data_flow.md`의 IK notes에 `theta_i` 기준 자세와 양의 방향을 추가한다.
- `docs/ik_structure_note.md`에서 `J_i`를 upper arm 끝점이자 parallelogram link와 연결되는 elbow joint로 정의한다.
- arm 1 local plane 가정과 함께 `J_1(theta_1)`의 메모 수준 좌표식을 정리한다.
- 아직 확정되지 않은 항목은 local plane 일반화, `P_i` 좌표식, `E/F/G` 최종 유도로 남겨둔다.
- 변경 기록을 `docs/daily_notes/2026-04-06.md`에 추가한다.

## Impact
- `theta_i` 의미가 문서 기준으로 더 명확해진다.
- IK 유도에서 사용하는 `J_i` 기호의 의미가 고정된다.
- 후속 수식 유도와 구현 논의가 더 구체적인 좌표식 기준으로 이어질 수 있다.

## Risk
- `J_1(theta_1)` 좌표식을 너무 확정적으로 쓰면 아직 미정인 기구 기준과 혼동될 수 있다.
- local plane 가정이 명시되지 않으면 arm 2, arm 3 확장 시 해석 차이가 생길 수 있다.

## Validation
- `theta_i = 0 deg`와 `theta_i = +90 deg` 정의가 문서에 분명히 반영되었는지 확인한다.
- `J_i`가 보조기호이며 SoT contract field가 아니라는 점이 유지되는지 확인한다.
- `J_1(theta_1)` 식이 현재 `base_frame`과 `B1` 방향 정의에 맞게 읽히는지 검토한다.
