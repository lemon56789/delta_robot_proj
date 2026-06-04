# Plan

## Goal
Y가 제공한 hardware base config 내용을 Markdown 구조에 맞게 정리하고, 영어 설명을 한글 중심 문서로 바꾼다.

## Files
- `docs/plans/2026-06-04_001_cleanup_hardware_base_config.md`
- `docs/hardware_experiment_base_config.md`
- `docs/daily_notes/2026-06-04.md`

## Changes
- 다중 라인 설명을 하위 bullet 또는 들여쓰기 문단으로 정리한다.
- Power, Arduino, Measurement Interface 섹션의 영어 설명을 한글화한다.
- firmware 경로는 아직 repo에 추가되지 않은 예정 경로로 명시한다.
- `STOP` 명령은 현재 미구현으로 두고, Run 00에서는 물리 전원 차단을 우선한다고 기록한다.
- `theta*_meas`는 실제 하드웨어 각도와 SoT 기준 각도 사이 offset을 기록한 뒤 SoT 기준으로 변환해야 한다고 명시한다.
- 전압 정보는 공칭 7.4 V, 완충 8.4 V 초과 금지, 성능 표기 7.4 V 기준으로 충돌 없이 정리한다.
- 오타와 깨진 따옴표를 수정한다.

## Impact
- 문서 구조와 실험 준비 기준만 정리한다.
- CSV 포맷, 코드, 폴더 구조, 제어 인터페이스 계약은 변경하지 않는다.
- Run 00 문서는 offset 값 입력 이후 별도 계획으로 작성한다.

## Risk
- Y가 준 실제 firmware 구현과 문서의 명령 예시가 다를 수 있다.
- 실제 하드웨어 angle offset 값이 아직 없어 `theta*_meas` 변환 표는 TBD로 남는다.

## Validation
- Markdown 구조가 깨지는 다중 라인 항목이 남지 않았는지 확인한다.
- 영어 설명이 필요한 기술 식별자 외에는 한글화되었는지 확인한다.
- `git diff --check`로 공백 오류를 확인한다.
