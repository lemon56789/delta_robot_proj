# Plan

## Goal
Run 01-pre real/raw metadata의 잘못된 trajectory 값을 정정하고, Arduino/controller gain `1.25` 적용 범위를 run별로 명확히 기록한다.

## Files
- `docs/plans/2026-06-06_002_correct_square_metadata_and_gain_scope.md`
- `data/real/raw/main_2026-06-05_run01_pre_cross_pm40_r01.json`
- `data/real/raw/main_2026-06-05_run01_pre_square_pm40_r01.json`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- `main_2026-06-05_run01_pre_cross_pm40_r01.json`의 `"trajectory"` 값을 `cross_pm10_pre`에서 `cross_pm40_pre`로 정정한다.
- `main_2026-06-05_run01_pre_square_pm40_r01.json`의 `"trajectory"` 값을 `square_pm10_pre`에서 `square_pm40_pre`로 정정한다.
- Run 01 문서에 gain 적용 범위를 명확히 적는다.
  - `cross_pm40`: Arduino/controller position gain `1.25` 적용 전 데이터
  - `square_pm40`: Arduino/controller position gain `1.25` 적용 후 데이터
- Daily note에 metadata 정정 이유와 gain 조건 분리 필요성을 기록한다.
- CSV 구조와 main/vision raw CSV 값은 변경하지 않는다.

## Impact
- square metadata label이 실제 target range와 일치한다.
- cross와 square를 같은 하드웨어 조건의 baseline으로 섞으면 안 된다는 점이 명확해진다.
- 이후 processed/merged dataset이나 virtual sensor 학습 split에서 gain condition을 run metadata 기준으로 분리할 수 있다.

## Risk
- JSON에 gain field를 새로 추가하면 metadata schema가 느슨하게 확장될 수 있다. 그래서 우선 문서/daily note에 명확히 기록하고, JSON은 잘못된 `trajectory` 값만 정정한다.
- 이후 metadata schema를 정식으로 확장하려면 별도 Contract Change 검토가 필요하다.

## Validation
- JSON 파싱 확인.
- `trajectory == cross_pm40_pre`와 `trajectory == square_pm40_pre` 확인.
- 문서에서 cross/square gain 조건이 서로 구분되어 있는지 확인.
- 수정 범위 `git diff --check`.
