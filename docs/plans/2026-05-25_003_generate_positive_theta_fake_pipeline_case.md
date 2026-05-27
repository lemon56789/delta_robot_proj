# Plan

## Goal
현재 수정된 `IK/FK` 기준에서 `theta_cmd`가 양수 영역에서 움직이는 fake pipeline CSV 케이스를 하나 생성한다.

## Files
- `docs/plans/2026-05-25_003_generate_positive_theta_fake_pipeline_case.md`
- `data/fake_pipeline/fake_pipeline_sample_2026-05-25_positive_theta.csv`
- `docs/daily_notes/2026-05-25.md`

## Changes
- 현재 운동학 기준으로 전 구간 `theta_cmd`가 양수가 되는 `z` 대역을 확인한다.
- 기존 fake pipeline 패턴과 같은 `x/y` 진동 형태를 사용하되, `z` 중심을 더 깊게 둔 별도 target trajectory로 CSV를 생성한다.
- 생성 결과와 선택 근거를 daily note에 기록한다.

## Impact
- 기존 CSV는 유지된다.
- 양수 `theta` branch에서의 데이터 거동을 별도 파일로 비교할 수 있다.

## Risk
- 현재는 fake measured angle 모델을 그대로 쓰므로, `theta_meas`는 일부 구간에서 0 근처까지 접근할 수 있다.
- 새 케이스는 현재 Python 기하 기준 reference이며, Simscape 비교 시 좌표/부호 규약을 다시 확인해야 한다.

## Validation
- 생성된 CSV가 목표 row 수를 가지는지 확인한다.
- 첫 row와 전체 구간에서 `theta_cmd`가 양수인지 확인한다.
- `sim_*`가 `target_*`를 `IK/FK` roundtrip 수준으로 재현하는지 확인한다.
