# Plan

## Goal
기존에 생성한 Run 02 발표 요약과 figure는 변경하지 않고, 미완료된
failure mode 표와 발표 수치 검증 문서를 추가한다.

## Files
- `docs/plans/2026-06-07_011_run02_failure_modes_and_numbers_check.md`
- `experiments/results/run02_failure_mode_table_2026-06-07.md`
- `experiments/results/run02_presentation_numbers_check_2026-06-07.md`
- `docs/daily_notes/2026-06-07.md`

## Changes
- Trajectory별 관측 결과, 근거 수치, failure mode, 해석, 발표 문구와
  연결 figure를 한 표로 정리한다.
- Correction sign, actuator integer resolution, home offset, Circle
  radial/tangential/phase lag를 서로 다른 failure mode로 분리한다.
- 발표 요약 Markdown/CSV와 source JSON의 수치를 항목별로 대조한다.
- Improvement percent의 두 정의인 mean-based percent와 pair-level
  percent mean을 구분해 기록한다.
- `95.6~100%` direction match는 JSON에 저장되지 않고 기존 Daily Note와
  `fulltext.md`에 기록된 진단값임을 source limitation으로 명시한다.
- 기존 summary, CSV, PNG/SVG는 덮어쓰거나 변경하지 않는다.

## Impact
- 발표 보조 문서와 작업 기록만 추가한다.
- 기존 결과 JSON/CSV, figure, raw/processed data, run ID, 데이터 contract와
  시스템 인터페이스는 변경하지 않는다.

## Risk
- Failure mode는 현재 artifact에 대한 원인 해석이며 단독 인과관계를
  실험적으로 확정한 결과가 아니다.
- Direction match 값의 pair별 상세 결과가 machine-readable JSON에 없어
  재현성 수준이 다른 지표보다 낮다.
- Pair-level percent mean과 mean-based percent를 혼용하면 같은 결과가
  서로 다른 수치로 보일 수 있다.

## Validation
- 두 신규 문서가 요구 경로에 생성됐는지 확인한다.
- 12 pair, 24 merged CSV와 다섯 presentation PNG의 존재를 확인한다.
- Summary CSV의 10개 data row를 reanalysis JSON과 대조한다.
- Failure mode 표의 핵심 수치가 source artifact와 일치하는지 확인한다.
- 기존 summary/CSV/figure와 source JSON/processed CSV가 변경되지
  않았는지 확인한다.
