# Plan

## Goal
Windows vision Codex가 `+40/+60 mm` X preload home 반복성 실험의 6개
run을 Computer 2와 같은 run ID로 기록하고 검증할 수 있는 독립형
지시서를 제공한다.

## Files
- `docs/plans/2026-06-07_006_home_repeatability_vision_handoff.md`
- `experiments/home_repeatability_vision_windows_codex_handoff.md`
- `experiments/README.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 확정된 6개 home repeatability run ID와 실행 순서를 vision 측 문서에
  고정한다.
- Computer 2와의 `VISION READY` 및 `RUN END` handshake를 정의한다.
- vision raw CSV 파일명, 필수 컬럼, timestamp, valid/marker 정책과
  기록 시작/종료 범위를 명시한다.
- calibration, camera, marker, homography와 좌표 원점을 6개 run 동안
  변경하지 않는 규칙을 명시한다.
- run 직후 품질 검사, 중단 조건, 메모와 원래 컴퓨터로 반환할 파일을
  정의한다.

## Impact
- 문서만 추가 또는 갱신한다.
- vision logger 코드, calibration artifact, raw CSV 계약과 기존 데이터는
  변경하지 않는다.

## Risk
- Vision 기록 시작이 preload 명령보다 늦으면 초기 home과 전체 이동을
  잃어 반복성 분석이 불가능하다.
- run별 calibration 또는 원점 재설정은 실제 home shift를 제거하므로
  금지해야 한다.
- 파일명과 CSV 내부 run ID가 다르면 Computer 2 로그와 pairing할 수
  없다.

## Validation
- 6개 run ID가 Computer 2 인수인계 문서와 정확히 일치하는지 확인한다.
- 필수 CSV 컬럼과 파일명 규칙이 `docs/vision_tracking.md` 계약과
  일치하는지 확인한다.
- handshake, 기록 범위, 품질 검사, 중단 조건과 반환 파일이 모두
  포함되는지 확인한다.
