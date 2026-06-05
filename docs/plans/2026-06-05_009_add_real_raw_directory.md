# Plan

## Goal
Run 01 main log 보관을 위해 `data/real/raw/` 경로를 GitHub에 반영할 수 있게 만든다.

## Files
- `docs/plans/2026-06-05_009_add_real_raw_directory.md`
- `data/real/raw/.gitkeep`
- `docs/daily_notes/2026-06-05.md`

## Changes
- `data/real/raw/` 디렉터리를 생성한다.
- GitHub가 빈 디렉터리를 추적할 수 있도록 `.gitkeep`을 추가한다.
- Daily Note에 변경 목적과 다음 작업을 기록한다.

## Impact
- 저장 경로만 추가한다.
- CSV 포맷, 코드, 제어 인터페이스는 변경하지 않는다.

## Risk
- 실제 main CSV 파일은 아직 생성하지 않는다.
- 컴퓨터 2에서 생성된 main log는 추후 이 경로로 복사해야 한다.

## Validation
- `data/real/raw/.gitkeep` 존재 여부를 확인한다.
- `git diff --check`로 공백 오류를 확인한다.
