# Plan

## Goal
하드웨어 담당 팀원이 실험 절차 작성에 필요한 스펙과 운영 조건을 채울 수 있도록 `docs/hardware_experiment_procedure.md` 템플릿을 추가한다.

## Files
- `docs/plans/2026-05-28_005_hardware_experiment_procedure_template.md`
- `docs/hardware_experiment_procedure.md`
- `docs/daily_notes/2026-05-28.md`

## Changes
- 하드웨어 실험 절차서 초안을 신규 문서로 추가한다.
- 아직 미확정인 장비 스펙, 제어기 설정, 비전 측정계 설정, 로그 경로, 안전 조건은 빈칸으로 둔다.
- 현재 SoT의 measured data 구조와 alignment 정책을 참조하도록 한다.
- Daily Note에 추가 이유와 후속 작업을 기록한다.

## Impact
- 하드웨어 팀원이 필요한 정보를 채워 넣을 기준 문서가 생긴다.
- 실제 실행 절차는 스펙 입력 후 확정한다.
- 코드, 데이터 포맷, 시스템 계약은 변경하지 않는다.

## Risk
- 빈칸이 채워지기 전에는 실행 가능한 실험 프로토콜이 아니라 정보 수집용 템플릿이다.
- 장비 스펙이 실제와 다르게 입력되면 안전 조건과 trajectory 조건이 잘못 설정될 수 있다.

## Validation
- 문서에 하드웨어 구성, Arduino 제어기, 비전 측정계, 로그/동기화, 안전 조건, 실행 절차 섹션이 포함되어 있는지 확인한다.
- 미확정 항목이 빈칸으로 남아 있는지 확인한다.
- Daily Note에 변경 기록이 남았는지 확인한다.
