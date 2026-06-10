# Plan

## Goal
Run 02 기존 24개 run을 다시 수집하지 않고 재분석해 correction 효과와
home 반복성, actuator 정수 해상도, circle 동적 위상 오차의 영향을
분리한다.

## Files
- `docs/plans/2026-06-07_004_run02_existing_data_reanalysis.md`
- `experiments/run02_reanalyze.py`
- `experiments/test_run02_reanalyze.py`
- `experiments/results/run02_reanalysis_2026-06-07.json`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- 기존 merged dataset에서 absolute tracking metric과 run 초기 home
  offset을 제거한 home-normalized metric을 함께 계산한다.
- Arduino firmware의 theta-to-servo mapping과 같은 계산으로 nominal 및
  corrected integer servo command를 재현하고 correction이 실제 actuator
  command를 바꾼 비율을 계산한다.
- step trajectory는 phase 전환 후 초기 구간과 이후 stable hold 구간으로
  나눠 tracking metric을 계산한다.
- circle은 기존 time-domain metric을 유지하면서 원운동 구간의 center,
  angle, radial error, tangential error와 phase lag 민감도를 별도
  diagnostic으로 계산한다.
- 결과를 기존 공식 comparison JSON과 분리된 재분석 JSON에 저장하고
  Run 02 문서와 Daily Note에 해석 제한을 포함해 기록한다.

## Impact
- 분석 코드, 테스트, 결과 JSON과 문서만 추가 또는 갱신한다.
- raw CSV, processed fixed 16-column CSV, 기존 comparison JSON, firmware,
  logger와 공개 인터페이스는 변경하지 않는다.

## Risk
- home-normalized metric은 절대 위치 정확도를 숨길 수 있으므로 absolute
  metric과 함께만 해석한다.
- circle phase shift 최적화는 실제 동적 lag를 제거할 수 있으므로 기존
  time-domain metric을 대체하지 않고 diagnostic으로만 사용한다.
- integer servo command는 firmware mapping을 재현한 추정값이며 serial
  RX 로그와 일치 여부를 검증해야 한다.

## Validation
- 재분석 단위 테스트를 실행한다.
- 12개 OFF/ON pair가 모두 결과에 포함되는지 확인한다.
- 기존 absolute metric이 기존 comparison report 값과 허용 오차 내에서
  일치하는지 확인한다.
- home-normalized, actuator command, step segment, circle diagnostic 값이
  finite인지 확인한다.
- 기존 raw/processed CSV와 comparison JSON이 변경되지 않았는지
  확인한다.
