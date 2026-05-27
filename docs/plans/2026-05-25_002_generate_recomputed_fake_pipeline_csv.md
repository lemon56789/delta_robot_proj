# Plan

## Goal
기존 `fake_pipeline_sample_2026-05-04.csv`의 `target_x/y/z` 전 구간을 그대로 사용하고, 현재 수정된 Python `IK/FK` 기준으로 각도와 시뮬레이션 결과를 다시 계산한 별도 CSV를 생성한다.

## Files
- `docs/plans/2026-05-25_002_generate_recomputed_fake_pipeline_csv.md`
- `data/fake_pipeline/fake_pipeline_sample_2026-05-04_recomputed.csv`
- `docs/daily_notes/2026-05-25.md`

## Changes
- 기존 2026-05-04 fake pipeline CSV에서 `time`, `target_x`, `target_y`, `target_z`를 읽는다.
- 현재 `IK/FK`와 fake measured angle 모델로 `theta_cmd`, `theta_meas`, `sim_*`, `error_*`를 다시 계산한다.
- 결과를 새 CSV 파일로 저장하고 기록한다.

## Impact
- 기존 CSV는 보존된다.
- 같은 target trajectory에 대해 수정된 운동학 기준 재계산 결과를 별도 비교할 수 있다.

## Risk
- 기존 2026-05-04 CSV와 값 차이가 커서 해석 시 파일 구분이 필요하다.
- `theta_meas`는 fake lag/bias/wobble 모델에 의존하므로 원본과 동일하지 않을 수 있다.

## Validation
- 새 CSV의 row 수가 원본과 같은지 확인한다.
- 첫 row의 `target`이 원본과 동일한지 확인한다.
- 첫 row의 `sim_*`가 현재 `IK/FK` 기준 값으로 계산되었는지 확인한다.
