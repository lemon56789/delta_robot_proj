# Plan

## Goal
컴퓨터 2(Y)에 전달할 Run 01-pre main logger PowerShell 실행 안내 파일을 작성한다.

## Files
- `docs/plans/2026-06-05_008_run01_main_logger_computer2_handoff.md`
- `experiments/run01_main_logger_computer2_powershell.md`
- `experiments/README.md`
- `docs/daily_notes/2026-06-05.md`

## Changes
- PowerShell 기준 실행 순서를 한 파일로 정리한다.
- `pyserial` 설치, COM port 확인, Arduino IDE Serial Monitor 종료, dry-run, 실제 static/cross/square 실행 명령을 포함한다.
- 생성 파일을 컴퓨터 1 repo의 `data/real/raw/`로 전달해야 한다는 절차를 명시한다.
- `theta*_meas=command_echo_no_encoder`, `time_source=pc_elapsed_ms` 주의사항을 포함한다.

## Impact
- 문서 안내만 추가한다.
- 코드, CSV 계약, Arduino firmware는 변경하지 않는다.

## Risk
- 컴퓨터 2의 Python 실행 명령이 `python`이 아니라 `py`일 수 있다.
- COM port 번호가 환경마다 다르므로 Y가 장치 관리자에서 확인해야 한다.

## Validation
- 안내 문서에 PowerShell 명령이 포함되어 있는지 확인한다.
- `git diff --check`로 문서 공백 오류를 확인한다.
