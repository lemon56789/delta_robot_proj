# Plan

## Goal
오늘 작성한 Run 01 관련 문서를 AGENTS.md와 기존 문서 톤에 맞게 한국어 중심으로 정리한다.

## Files
- `docs/plans/2026-06-05_006_markdown_language_consistency.md`
- `docs/plans/2026-06-05_005_run_01_baseline_protocol.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- Run 01 문서의 영어 설명 문장과 판정 항목을 한국어 중심으로 바꾼다.
- 기술 계약 필드명, 파일명, `run_id`, `error_x/y/z`, `train/validation/holdout` 같은 데이터 split 명칭은 그대로 유지한다.
- `yes/no` 판정 표기는 한국어 `예/아니오`로 바꾼다.
- 후속 Run 02/03 템플릿의 `(작성: ...)` placeholder는 아직 실행 근거가 없으므로 이번 수정 범위에서 제외한다.

## Impact
- 문서 언어와 표현만 정리한다.
- CSV 포맷, 데이터 흐름, 인터페이스, 실험 절차의 의미는 변경하지 않는다.

## Risk
- 기술 용어를 과도하게 번역하면 코드/CSV 필드와 연결이 약해질 수 있으므로 계약명은 번역하지 않는다.
- 미래 실행 문서를 근거 없이 채우면 placeholder/dummy 문서가 될 수 있으므로 Run 02/03은 이번에 수정하지 않는다.

## Validation
- Run 01 문서가 한국어 중심 설명을 사용하면서도 계약 필드명을 유지하는지 확인한다.
- `git diff --check`로 문서 공백 오류를 확인한다.
