# Plan

## Goal
하드웨어 실험 문서 인덱스 역할을 하는 `docs/hardware_experiment_procedure.md`를 `docs/hardware_experiment_index.md`로 rename하고 관련 참조를 갱신한다.

## Files
- `docs/plans/2026-05-28_008_rename_hardware_experiment_index.md`
- `docs/hardware_experiment_procedure.md`
- `docs/hardware_experiment_index.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-28.md`

## Changes
- `docs/hardware_experiment_procedure.md`를 삭제한다.
- 동일 내용을 `docs/hardware_experiment_index.md`로 추가한다.
- `fulltext.md`에서 인덱스 문서 참조를 새 파일명으로 변경한다.
- Daily Note에 rename 이유와 결과를 기록한다.

## Impact
- 문서 역할이 파일명에 명확히 드러난다.
- 실험별 실제 절차는 `docs/hardware_experiment_run_*.md`에 남고, 인덱스는 `docs/hardware_experiment_index.md`가 담당한다.
- 코드, 데이터 계약, 실험 구조는 변경하지 않는다.

## Risk
- 이전 파일명을 참조하는 외부 링크가 있으면 깨질 수 있다.
- 리포 내부 참조는 함께 갱신한다.

## Validation
- `docs/hardware_experiment_index.md`가 생성되었는지 확인한다.
- `docs/hardware_experiment_procedure.md`가 제거되었는지 확인한다.
- `fulltext.md`가 새 파일명을 참조하는지 확인한다.
- `git diff --check`로 포맷 문제를 확인한다.
