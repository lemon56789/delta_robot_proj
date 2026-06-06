# Plan

## Goal
Git 저장소 구조가 없는 Computer 2에서 Codex가 Run 02 실행 환경을 재구성하고,
Simscape 연계 및 24회 실험을 동일한 조건으로 수행할 수 있는 독립형 인수인계 문서를 작성한다.

## Files
- `experiments/run02_computer2_codex_handoff.md`
- `experiments/README.md`
- `docs/daily_notes/2026-06-06.md`
- `docs/plans/2026-06-06_020_computer2_codex_run02_handoff.md`

## Changes
- Computer 2에 전달할 필수 파일과 생성할 폴더 구조를 명시한다.
- Python 환경, 파일 무결성, import 및 테스트 검증 절차를 명시한다.
- OFF dry-run에서 Simscape 입력 스케줄을 생성하고 명목 시뮬레이션 CSV를 준비하는 절차를 명시한다.
- OFF/ON 24회 실험 순서, 실행 전후 점검, 중단 조건과 회수 파일을 명시한다.
- 기존 PowerShell 명령 안내서와 새 독립형 인수인계 문서의 역할을 구분한다.

## Impact
- 문서만 추가 및 갱신한다.
- Run 02 코드, 데이터 포맷, 모델, 실험 파라미터는 변경하지 않는다.

## Risk
- 전달 과정에서 파일 누락 또는 수정이 발생하면 Computer 2 결과가 현재 저장소와 달라질 수 있다.
- dry-run 출력과 실제 실험 출력을 같은 경로에 저장하면 파일을 혼동할 수 있다.
- Simscape CSV의 시간축이 명령 스케줄과 다르면 ON 실험을 진행할 수 없다.

## Validation
- 문서에 필수 파일, SHA-256, 24회 매트릭스, 네 개의 Simscape 파일명 및 중단 조건이 모두 포함됐는지 확인한다.
- 변경 문서에 대해 `git diff --check`를 수행한다.
