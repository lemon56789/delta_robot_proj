# Plan

## Goal
2026-05-25 `IK/FK` 기준 정리 이후 남아 있던 요약 문서 불일치를 해소한다. `fulltext.md`의 부호/우선순위 서술을 현재 SoT와 맞추고, `docs/roadmap.md`의 상태 snapshot 기준일 라벨을 실제 반영 범위와 정렬한다.

## Files
- `docs/plans/2026-05-26_001_update_fulltext_and_roadmap_after_ik_fk_review.md`
- `fulltext.md`
- `docs/roadmap.md`
- `docs/daily_notes/2026-05-26.md`

## Changes
- `fulltext.md`의 갱신일을 오늘 기준으로 올리고, `IK` 현재 코드 상태에서 낡은 `theta` 부호 보정 서술을 제거하거나 현재 SoT 기준 설명으로 교체한다.
- `fulltext.md`의 alignment/correction 요약에 현재 provisional `20 ms` lag와 `error_* = measured_position - sim_position` 의미를 반영한다.
- `fulltext.md`의 바로 다음 작업 우선순위를 `virtual_sensor baseline` 선행이 아니라 `Simscape-Python alignment` 선행 기준으로 갱신한다.
- `docs/roadmap.md`의 `Current Status Snapshot` 기준일 라벨을 현재 상세 상태와 맞춘다.
- 오늘 변경 사유와 결과를 `docs/daily_notes/2026-05-26.md`에 기록한다.

## Impact
- 외부 요약 문서가 현재 `docs/*` SoT와 같은 `IK/FK` 의미 체계를 사용하게 된다.
- 다음 작업 우선순위를 읽는 사람이 simulation alignment 선행 원칙을 잘못 해석할 위험이 줄어든다.
- `roadmap` 상단 snapshot 날짜와 하단 상세 상태의 일관성이 좋아진다.

## Risk
- `fulltext.md`는 요약본이므로 세부 설명을 과하게 넣으면 SoT 대비 중복 관리 부담이 커질 수 있다.
- snapshot 날짜를 올리더라도 향후 세부 상태가 다시 바뀌면 추가 갱신이 필요하다.

## Validation
- `fulltext.md`에 더 이상 현재 기준과 어긋나는 `theta` 부호 보정 서술이 없는지 확인한다.
- `fulltext.md`의 다음 작업 1순위가 `Simscape-Python alignment` 선행으로 읽히는지 확인한다.
- `docs/roadmap.md`의 snapshot 기준일과 Stage 4 상세 상태가 서로 모순되지 않는지 확인한다.
