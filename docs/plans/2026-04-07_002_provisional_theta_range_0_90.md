# Plan

## Goal
IK 해 선택 규칙에서 사용할 임시 working range를 `0 deg <= theta_i <= 90 deg`로 문서에 반영한다.
현재 단계에서는 branch 선택용 임시 범위로만 사용하고, 최종 `theta_min`, `theta_max`는 기구 파라미터와 하드웨어 제약 확정 후 다시 갱신한다.

## Files
- `docs/plans/2026-04-07_002_provisional_theta_range_0_90.md`
- `docs/ik_structure_note.md`
- `docs/daily_notes/2026-04-07.md`

## Changes
- `docs/ik_structure_note.md`의 root selection rule에 임시 각도 범위 `0 deg <= theta_i <= 90 deg`를 명시한다.
- 해당 범위가 현재 단계의 provisional working range이며 추후 수정 가능하다는 점을 함께 적는다.
- 변경 기록을 `docs/daily_notes/2026-04-07.md`에 추가한다.

## Impact
- 구현과 테스트에서 사용할 1차 branch 선택 범위가 생긴다.
- 아직 미확정인 기구 파라미터 없이도 해 선택 규칙을 운용할 수 있다.

## Risk
- 실제 하드웨어 범위가 더 좁으면 추후 수정이 필요하다.
- 임시 범위를 최종 확정값으로 오해하지 않도록 문구가 분명해야 한다.

## Validation
- 문서가 `0 deg <= theta_i <= 90 deg`를 임시 working range로 명시하는지 확인한다.
- 추후 수정 가능성이 함께 드러나는지 검토한다.
