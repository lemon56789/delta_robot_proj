# Plan

## Goal
`docs/hardware_experiment_procedure.md`의 각 입력 항목에 한국어 작성 안내를 추가해, 하드웨어/제어/비전 담당자가 어떤 정보를 채워야 하는지 명확히 한다.

## Files
- `docs/plans/2026-05-28_006_annotate_hardware_experiment_template.md`
- `docs/hardware_experiment_procedure.md`
- `docs/daily_notes/2026-05-28.md`

## Changes
- 각 빈칸 항목 뒤에 한국어 설명을 추가한다.
- 기존 섹션 구조는 유지한다.
- 실제 스펙 값은 입력하지 않고, 작성 가이드만 추가한다.
- Daily Note에 변경 이유와 결과를 기록한다.

## Impact
- 팀원이 템플릿을 채울 때 필요한 정보의 의미와 단위를 빠르게 이해할 수 있다.
- 데이터 계약, 코드, 폴더 구조는 변경하지 않는다.

## Risk
- 설명이 지나치게 길면 실험 절차서가 장황해질 수 있으므로 항목별로 짧은 작성 안내만 둔다.
- 실제 스펙 입력 후에는 안내 문구 일부를 정리할 필요가 있을 수 있다.

## Validation
- 각 주요 입력 항목에 한국어 작성 안내가 포함되어 있는지 확인한다.
- 기존 기준 문서 참조와 required field 목록이 유지되는지 확인한다.
- `git diff --check`로 문서 포맷 문제를 확인한다.
