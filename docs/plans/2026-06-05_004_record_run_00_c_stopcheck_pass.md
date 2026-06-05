# Plan

## Goal
Run 00-C vision readiness stopcheck 결과를 Run 00 문서에 반영하고, Run 00을 baseline data collection 전 gate 통과 상태로 정리한다.

## Files
- `docs/plans/2026-06-05_004_record_run_00_c_stopcheck_pass.md`
- `docs/hardware_experiment_run_00_commissioning.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- `data/vision/raw/vision_stopcheck_2026-06-04_run00_c_stopcheck_001.csv`를 Run 00-C vision readiness 근거 파일로 기록한다.
- 파일/run_id 날짜가 2026-06-04로 남아 있지만 2026-06-05 검토 기준 Run 00-C 근거로 사용한다고 명시한다.
- marker detection, valid row ratio, `vision_x/y` direction match, static coordinate noise 결과를 기록한다.
- main log와 같은 run_id 여부는 별도 main log 파일이 없으므로 not verified로 기록한다.
- Run 01 readiness는 vision readiness 기준으로 yes로 전환하되, Run 01부터 main/vision log run_id를 반드시 일치시켜야 한다는 조건을 남긴다.

## Impact
- 문서 기록만 변경한다.
- raw CSV, data format, code, controller interface는 변경하지 않는다.

## Risk
- Run 00-C 근거 파일의 run_id 날짜가 실제 검토 날짜와 다르므로, provenance note 없이는 혼동될 수 있다.
- Run 00-C에서는 main log run_id match가 검증되지 않았으므로 Run 01에서는 같은 run_id 로깅을 별도 확인해야 한다.

## Validation
- Run 00 문서가 A/B/C pass와 남은 main-log 주의사항을 구분하는지 확인한다.
- Daily Note에 무엇을/왜/어떻게/결과/변경 파일/다음 작업이 남는지 확인한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
