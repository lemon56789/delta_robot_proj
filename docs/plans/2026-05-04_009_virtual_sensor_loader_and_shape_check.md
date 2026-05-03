# Plan

## Goal
`fake pipeline`이 생성한 CSV를 `virtual_sensor/`에서 바로 읽을 수 있는 최소 loader와 shape check 경로를 추가한다. 목적은 아직 모델이 없어도 virtual sensor가 받을 feature/target 구조가 실제 파일 기준으로 일관적인지 검증하는 것이다.

## Files
- `virtual_sensor/dataset.py`
- `virtual_sensor/check_dataset.py`
- `virtual_sensor/README.md`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `virtual_sensor/dataset.py`에 fake pipeline CSV를 읽는 dataset loader를 추가한다.
- loader는 현재 CSV 계약 기준 컬럼 존재 여부, row count, float 변환 가능 여부를 검증한다.
- feature columns와 target columns를 명시적으로 정의하고, 기본 feature는 `theta*_cmd`, `theta*_meas`, `sim_x/y/z`로 잡는다.
- target columns는 현재 correction field인 `error_x`, `error_y`, `error_z`로 잡는다.
- `virtual_sensor/check_dataset.py`에 CLI shape check 스크립트를 추가해 CSV를 읽고 feature/target shape, NaN 여부, 간단한 통계를 출력하게 한다.
- `virtual_sensor/README.md`에 loader 사용 방법과 현재 feature/target 정의를 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유, 방법, 결과, 다음 작업을 기록한다.

## Impact
- virtual sensor 모델 코드가 없어도 데이터 입력 구조를 먼저 고정하고 검증할 수 있다.
- fake pipeline CSV가 실제 학습/추론 입력으로 이어질 준비가 되었는지 확인할 수 있다.
- 현재 CSV 계약이나 운동학 코드는 변경하지 않는다.

## Risk
- feature/target 정의를 너무 일찍 고정하면 나중에 실제 데이터 수집 단계에서 수정이 필요할 수 있다.
- 현재는 표준 라이브러리 기반으로 갈 가능성이 커서, 향후 PyTorch dataset 형태로 다시 감쌀 수 있다.
- fake pipeline 데이터는 synthetic이므로 shape가 맞아도 실제 분포 검증을 대신하진 못한다.

## Validation
- Python 구문 검증을 수행한다.
- `fake_pipeline_sample_2026-05-04.csv`를 입력으로 shape check 스크립트를 실제 실행한다.
- feature/target 컬럼 수, row 수, NaN 여부, 기본 통계가 출력되는지 확인한다.
- 컬럼 누락 시 명시적으로 실패하는지 확인한다.
