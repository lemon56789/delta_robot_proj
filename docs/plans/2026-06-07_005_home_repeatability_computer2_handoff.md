# Plan

## Goal
`+X preload -> home` 접근 방향에 따른 home 반복성을 최소 하드웨어
실험으로 확인할 수 있도록 6개 run ID와 Computer 2 Codex용 실행 절차를
고정한다.

## Files
- `docs/plans/2026-06-07_005_home_repeatability_computer2_handoff.md`
- `experiments/home_repeatability_computer2_codex_handoff.md`
- `experiments/README.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- `+40 mm` 및 `+60 mm` preload 조건을 각각 3회 수행하는 6개 run ID를
  확정한다.
- Computer 2에서 Arduino Serial Monitor를 사용해 preload, hold, home,
  stabilization 순서로 실행하는 독립형 지시서를 추가한다.
- Windows vision 담당자와 공유할 run ID, 기록 시작/종료 handshake,
  파일명과 필수 CSV 필드를 포함한다.
- +X 진동, 소음, 간섭 및 stall에 대한 중단 조건과 실험 후 회수 파일을
  명시한다.
- `experiments/README.md`에서 새 인수인계 문서를 찾을 수 있게 연결한다.

## Impact
- 문서만 추가 또는 갱신한다.
- Python logger, Arduino firmware, 데이터 포맷과 기존 Run 02 결과는
  변경하지 않는다.

## Risk
- Computer 2에서 시리얼 포트를 다시 열면 Arduino가 리셋되고 HOME으로
  초기화되므로 한 세션 안에서 명령 순서를 지켜야 한다.
- `+60 mm` 이동은 관찰상 진동이 더 클 수 있으므로 `+40 mm` 조건을 먼저
  완료하고 안전 확인 후 진행해야 한다.
- vision 기록에 preload 이동과 home 안정화 구간이 모두 포함되지 않으면
  반복성 분석이 불가능하다.

## Validation
- 6개 run ID가 중복 없이 조건별 3개인지 확인한다.
- 지시서에 Computer 2와 vision의 동일 run ID 사용, 명령값, hold 시간,
  중단 조건과 회수 파일이 모두 포함되는지 확인한다.
- Markdown 형식과 경로 참조를 확인한다.
