# Plan

## Goal
- `docs/system_data_flow.md`의 `IK Interface Contract` 섹션에 합의된 필드명과 실패 처리 정책을 반영한다.

## Files
- `docs/system_data_flow.md`
- `docs/daily_notes/2026-03-26.md`

## Changes
- IK 입력 필드명을 `target_x`, `target_y`, `target_z`로 명시한다.
- IK 출력 필드명을 `theta1_cmd`, `theta2_cmd`, `theta3_cmd`로 명시한다.
- IK 실패 동작을 `reject`로 명시한다.

## Impact
- 이후 CSV, controller, virtual sensor 문서에서 IK 출력 인터페이스를 같은 이름으로 참조할 수 있다.

## Risk
- 기존 AGENTS의 CSV 예시가 `motor*_cmd`를 사용하고 있어, 후속 CSV 계약 정리 시 정합성 검토가 필요하다.

## Validation
- `docs/system_data_flow.md`에 IK 필드명과 실패 정책이 반영되었는지 확인
- Daily Note에 변경 이유와 결과가 기록되었는지 확인
