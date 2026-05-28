# Plan

## Goal
최근 정리된 `error_*` 정책과 measured data 구조를 `fulltext.md` 요약본에 반영한다. 목적은 외부 AI 모델이 현재 프로젝트 상태를 볼 때 raw log, processed merged dataset, `measured_z_est`, `error_*` 생성 시점을 최신 SoT와 일치하게 이해하도록 만드는 것이다.

## Files
- `docs/plans/2026-05-28_004_update_fulltext_after_measured_data_structure.md`
- `fulltext.md`
- `docs/daily_notes/2026-05-28.md`

## Changes
- `fulltext.md` 갱신일을 `2026-05-28`로 변경한다.
- 주요 문서/폴더 역할에 `docs/measured_data_structure.md`를 추가한다.
- 데이터 계약 설명에 raw/auxiliary log와 final processed CSV contract의 분리를 반영한다.
- `error_*`는 raw Simscape export가 아니라 measured/sim/vision data가 정렬된 processed merged dataset 단계에서 생성한다고 명시한다.
- measured data 구조 요약을 추가한다.
- vision raw log 최소 필드에 `run_id`, `valid`를 반영한다.
- 현재 상태와 바로 다음 작업을 2026-05-28 기준 우선순위와 맞춘다.
- Daily Note에 변경 이유와 결과를 기록한다.

## Impact
- 외부 AI 분석용 요약본이 최신 SoT와 일치한다.
- 코드, 데이터 파일, CSV contract 자체는 변경하지 않는다.
- 문서 참조 기준이 `docs/system_data_flow.md`, `docs/measured_data_structure.md`, `docs/vision_tracking.md`로 확장된다.

## Risk
- `fulltext.md`는 요약본이므로 세부 필드 설명은 원문 SoT보다 축약된다.
- 실제 measured data 저장 경로와 `estimator_method` 규칙은 아직 open question으로 남는다.

## Validation
- `fulltext.md`의 `error_*` 설명이 `docs/system_data_flow.md`와 충돌하지 않는지 확인한다.
- `fulltext.md`의 measured data 요약이 `docs/measured_data_structure.md`와 충돌하지 않는지 확인한다.
- vision raw field 요약이 `docs/vision_tracking.md`와 일치하는지 확인한다.
- `git diff --check`로 문서 포맷 문제를 확인한다.
