# Plan

## Goal
`simulation/simulink/` 안에서 현재 기준 모델과 주요 스크립트 역할을 문서화하고, 버전관리 불필요 생성물을 제거해 Simulink 원본 관리 기준을 명확히 한다.

## Files
- `docs/plans/2026-05-27_002_document_simulink_latest_model_and_cleanup_generated_files.md`
- `simulation/simulink/.gitignore`
- `simulation/simulink/README.md`
- `simulation/simulink/model_notes.md`
- `simulation/simulink/simscape_delta_robot_trajectory.slxc`
- `simulation/simulink/simscape_delta_robot_trajectory_axisfix.slxc`
- `simulation/simulink/simscape_delta_robot_trajectory.avi`
- `docs/daily_notes/2026-05-27.md`

## Changes
- 오늘 작업용 계획서를 추가한다.
- `simulation/simulink/model_notes.md`를 추가해 최신 기준 `slx` 파일과 주요 `m` 파일 역할을 정리한다.
- `simulation/simulink/README.md`에 세부 기준 문서 위치를 연결한다.
- `simulation/simulink/.gitignore`를 추가해 `slprj`, `*.slxc`, `*.avi`, autosave 등 생성물을 기본 제외 대상으로 설정한다.
- 현재 들어와 있는 `*.slxc` 두 개와 `*.avi` 한 개를 삭제한다.
- `docs/daily_notes/2026-05-27.md`에 이번 정리 작업과 이유, 결과를 기록한다.

## Impact
- 어떤 `slx`가 최신 기준 모델인지 저장소 안에서 바로 확인할 수 있다.
- 주요 Simulink 보조 스크립트의 역할을 후속 작업자가 빠르게 파악할 수 있다.
- 생성물 재유입을 줄여 Simulink 원본 관리가 쉬워진다.

## Risk
- `.gitignore`는 새 파일 추적만 막으므로, 이미 추적 중인 생성물은 직접 삭제해야 한다.
- `run_fake_pipeline_simscape.m`의 `error_*` 재계산은 현재 SoT의 correction 의미와 다르므로 문서에서 diagnostic 용도임을 분명히 적어야 한다.

## Validation
- `simulation/simulink/model_notes.md`에 최신 기준 모델명이 명시되었는지 확인한다.
- `.gitignore`가 `*.slxc`, `*.avi`, `slprj/`를 포함하는지 확인한다.
- 삭제 대상 파일이 작업 후 존재하지 않는지 확인한다.
- Daily Note에 무엇을, 왜, 어떻게, 결과, 다음 작업이 기록되었는지 확인한다.
