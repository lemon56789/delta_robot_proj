# Plan

## Goal
`recomputed` 및 `positive_theta` 기준 CSV와 `Simscape` 결과 CSV 비교에서 확인된 정렬 결과를 SoT 문서에 반영한다. 목적은 현재 comparison path에서 필요한 `lag` 보정을 기록하고, `error_x/y/z`의 의미를 SoT 기준으로 유지하며, 추후 `measured_position` 확보 시 `Simscape` CSV export를 수정해야 한다는 점을 명시하는 것이다.

## Files
- `docs/plans/2026-05-25_005_record_simscape_lag_and_error_semantics.md`
- `docs/system_data_flow.md`
- `docs/roadmap.md`
- `docs/daily_notes/2026-05-25.md`

## Changes
- `docs/system_data_flow.md`에 현재 `Simscape` comparison path의 provisional alignment 결과를 반영한다.
  - current fake pipeline comparison 기준 `1 sample = 20 ms` lag를 기록한다.
  - `theta_*`는 Python 기준과 정렬되며, `sim_*`는 `post-alignment` 후 비교한다는 점을 명시한다.
  - `error_x/y/z`는 SoT 기준으로 `measured_position - sim_position` 의미를 유지한다고 명시한다.
  - 현재 `Simscape` CSV의 `error_*`는 `target_position - sim_position` diagnostic 값이므로 계약 기준으로 사용하지 않으며, 추후 `measured_position` 확보 시 `Simulink/Simscape` export를 수정해야 한다는 점을 적는다.
- `docs/roadmap.md` Stage 4 current status에 비교 결과와 남은 작업을 추가한다.
- `docs/daily_notes/2026-05-25.md`에 이번 문서 반영 작업과 이유, 결과, 후속 수정 필요 사항을 기록한다.

## Impact
- 가상센서 모델 구현 전 simulation path와 correction field 의미가 문서 기준으로 고정된다.
- 현재 `Simscape` CSV의 `error_*`를 학습/계약 입력으로 오해하는 위험을 줄인다.
- 추후 하드웨어 `measured_position` 확보 후 `Simulink/Simscape` export 수정이 필요한 이유가 기록된다.

## Risk
- 현재 `lag=20 ms`는 fake pipeline 기준 comparison 결과이므로, 실제 hardware logging path에서는 다시 검증이 필요하다.
- `measured_position` 입력원이 아직 없으므로 `error_*`의 실제 생성 경로는 후속 구현까지 문서 기준 상태로만 유지된다.
- `roadmap` status snapshot 날짜 자체는 이번 작업에서 갱신하지 않으므로, 일부 상단 상태 요약은 최신 상세 상태보다 덜 구체적일 수 있다.

## Validation
- `docs/system_data_flow.md`에 `lag=20 ms`와 `error_*` 의미가 명시되었는지 확인한다.
- `docs/roadmap.md` Stage 4 current status가 현재 comparison 결과와 모순되지 않는지 확인한다.
- `docs/daily_notes/2026-05-25.md`에 변경 이유와 “나중에 Simscape CSV error 수정 필요”가 기록되었는지 확인한다.
