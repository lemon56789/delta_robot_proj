# Plan

## Goal
Windows 환경에서 C-pre 비전 카메라 체크를 수행할 수 있도록 `fulltext.md`에 운영 권장사항을 반영한다.

## Files
- `docs/plans/2026-06-04_005_update_fulltext_windows_vision_cpre.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-04.md`

## Changes
- WSL repo를 SoT로 유지하고, Windows Python은 camera I/O 실행 환경으로만 쓰는 방침을 추가한다.
- C-pre 단계는 camera open, ArUco detection, platform marker pixel CSV 저장까지로 정의한다.
- pixel CSV는 `vision_x/y` 대신 `marker_px/marker_py`를 사용하도록 명시한다.
- Windows에서 WSL repo 경로 `\\wsl$\<distro>\home\lemon56789\delta_robot\data\vision\raw` 또는 Windows 임시 경로를 사용할 수 있음을 기록한다.

## Impact
- 외부 AI 분석용 요약 문서만 갱신한다.
- 코드, CSV 계약, Run 00 최종 pass/fail 기준은 변경하지 않는다.

## Risk
- Windows 배포판 이름은 환경마다 다르므로 `wsl -l -v`로 확인해야 한다.
- C-pre pixel CSV는 homography 전 사전 점검용이며, Run 00 C 최종 통과 로그와 혼동하면 안 된다.

## Validation
- `fulltext.md`에 Windows vision C-pre 지침이 들어갔는지 확인한다.
- `git diff --check`로 Markdown 공백 오류를 확인한다.
