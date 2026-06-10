# Plan

## Goal
Run 02 OFF/ON 결과의 원인 진단에서 확인한 servo command 양자화, run 간
home 위치 이동, circle 위상 정렬 문제와 현재 결과 해석의 제한을 Daily
Note에 기록한다.

## Files
- `docs/plans/2026-06-07_003_record_run02_diagnostic_findings.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 모델 correction sign 자체는 정상이라는 근거를 기록한다.
- fractional corrected theta가 Arduino의 integer servo command 변환에서
  대부분 소실되는 비율을 trajectory별로 기록한다.
- 동일 home command에서도 OFF/ON 초기 위치가 이동한 최대값과 반복성
  문제를 기록한다.
- circle 단일 departure alignment 결과와 phase shift 재평가 결과의
  차이를 기록한다.
- 현재 comparison 결과를 최종 모델 실패로 해석하지 않고 재분석이
  필요한 상태로 정리한다.

## Impact
- 문서와 작업 기록만 변경한다.
- 코드, raw/processed CSV, comparison JSON과 인터페이스는 변경하지
  않는다.

## Risk
- baseline-normalized 또는 phase-shift 결과를 기존 공식 metric과
  혼동하면 결과를 과대 해석할 수 있다.
- 읽기 전용 진단값은 후속 정식 분석 구현에서 다시 재현해야 한다.

## Validation
- Daily Note에 무엇을, 왜, 어떻게, 결과, 변경 파일, 다음 작업이
  포함되는지 확인한다.
- trajectory별 servo command 변경 비율과 circle shift 결과가 계산값과
  일치하는지 확인한다.
- 기존 Entry 001/002를 변경하지 않고 새 entry로 추가했는지 확인한다.
