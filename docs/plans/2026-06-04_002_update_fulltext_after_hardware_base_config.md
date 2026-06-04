# Plan

## Goal
최근 하드웨어 기준 정리 내용을 `fulltext.md` 요약본에 반영한다.

## Files
- `docs/plans/2026-06-04_002_update_fulltext_after_hardware_base_config.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-04.md`

## Changes
- `fulltext.md` 갱신일을 2026-06-04로 올린다.
- `wB = 46.0 mm`, `uP = 27.177 mm`, `H = 285 mm`, `sB/sP` reference-only 의미를 요약한다.
- Simscape 재생성/검증 상태와 `error_*` diagnostic 주의사항을 최신 상태로 정리한다.
- 하드웨어 base config에 확정된 전원, `STOP` 미구현/물리 차단 우선, Arduino command mapping, `center_cmd_i` 값을 요약한다.
- Run 00 목적을 커미셔닝, zeroing, direction, safety, logging, vision 위치 확인으로 정리한다.
- 다음 작업 우선순위를 Run 00 절차 작성과 실제 커미셔닝 준비 중심으로 갱신한다.

## Impact
- 외부 AI 분석용 요약 문서만 갱신한다.
- 코드, CSV 포맷, 시스템 인터페이스 계약은 변경하지 않는다.

## Risk
- `fulltext.md`는 요약본이므로 세부값이 SoT 문서와 중복된다. 상충 시 `docs/*`를 우선한다는 기존 원칙을 유지한다.

## Validation
- `fulltext.md`에서 날짜와 최신 하드웨어 상태가 반영되었는지 확인한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
