# Hardware Experiment Index

이 문서는 하드웨어 실험 문서의 인덱스다. 고정 장비/제어/비전/로그 설정은 base config 문서에서 관리하고, 실험 목적에 따라 달라지는 항목은 run protocol 문서에서 관리한다.

관련 기준 문서:
- `docs/system_data_flow.md`
- `docs/measured_data_structure.md`
- `docs/vision_tracking.md`
- `docs/workspace_envelope.md`

## Document Structure
- `docs/hardware_experiment_base_config.md`
  - 하드웨어 구성, Arduino 제어기, 비전 측정계, 데이터 로깅 구조, 동기화, 공통 안전 조건처럼 실험 종류와 무관하게 고정되는 내용을 적는다.
- `docs/hardware_experiment_run_00_commissioning.md`
  - 하드웨어 커미셔닝, 안전 검증, 모터 방향/zeroing/limit 확인을 위한 절차를 적는다.
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
  - 오차 학습용 baseline 데이터를 수집하는 절차를 적는다.
- `docs/hardware_experiment_run_02_corrected_comparison.md`
  - 가상센싱 보정 적용 후 baseline과 비교할 데이터를 수집하는 절차를 적는다.
- `docs/hardware_experiment_run_03_final_demo.md`
  - 최종 시연용 움직임과 최소 검증 절차를 적는다.

## Fixed vs Run-Specific
고정 항목은 base config에만 적는다.
- robot geometry
- motor/driver/power spec
- Arduino firmware and command/log interface
- vision camera/marker/calibration setup
- raw/processed data field structure
- default synchronization/alignment policy
- common stop condition policy

실험별 항목은 각 run protocol에 적는다.
- experiment purpose
- expected output
- trajectory
- correction on/off
- run command
- run-specific safety threshold
- post-run validation
- run metadata

## Update Rule
- 장비나 제어기 스펙이 바뀌면 `docs/hardware_experiment_base_config.md`를 갱신한다.
- 특정 실험의 trajectory나 검증 기준이 바뀌면 해당 `hardware_experiment_run_*.md`만 갱신한다.
- 모든 변경은 `docs/daily_notes/YYYY-MM-DD.md`에 기록한다.
