# Plan

## Goal
현재 운동학 sweep 결과를 바탕으로 `theta` working range를 `nominal analysis range`와 `hardware-confirmed range`로 구분해 문서에 기록한다. 목적은 모델링/분석용 범위와 실제 하드웨어 확정 범위를 혼동하지 않도록 하는 것이다.

## Files
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `docs/system_data_flow.md`의 `IK Interface Contract`에 `hardware-confirmed angle limits`와 `nominal-analysis angle limits`를 구분해 기록한다.
- 현재 기준으로 `hardware-confirmed angle limits`는 미확정이지만 보수적 임시값 `0 deg <= theta_i <= 90 deg`를 유지한다는 점을 적는다.
- `nominal-analysis angle limits`는 현재 sweep 결과 기준 후보 범위로 `-10 deg <= theta_i <= 90 deg`를 기록한다.
- `docs/ik_structure_note.md`에는 왜 범위를 둘로 나누는지와 `theta_min` sweep 결과를 간단히 남긴다.
- `fulltext.md`에는 현재 상태 요약 수준에서 두 범위의 구분만 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유와 기록 내용을 남긴다.

## Impact
- 문서에서 angle range 해석이 더 명확해진다.
- 이후 fake pipeline, trajectory test, 하드웨어 연동 시 어떤 범위를 쓰는지 구분하기 쉬워진다.
- 데이터 계약이나 함수 시그니처는 변경하지 않는다.

## Risk
- `hardware-confirmed`와 `hardware-safe provisional` 표현이 모호하면 다시 혼선이 생길 수 있다.
- `nominal-analysis range`를 하드웨어 허용 범위로 오해하지 않도록 문구가 분명해야 한다.

## Validation
- `system_data_flow.md`에서 두 범위가 명확히 구분되어 보이는지 확인한다.
- `ik_structure_note.md`와 `fulltext.md`가 같은 해석을 유지하는지 검토한다.
- `-10 deg <= theta_i <= 90 deg`가 sweep 결과 근거와 모순되지 않는지 확인한다.
