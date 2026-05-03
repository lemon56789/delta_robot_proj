# Plan

## Goal
실제 하드웨어 없이도 현재 SoT 기준 데이터 흐름을 끝까지 통과시키는 `fake pipeline` 최소 구현을 추가한다. 목적은 `target -> theta_cmd -> fake theta_meas -> fake sim_x/y/z -> error_x/y/z` 경로를 실제 CSV 계약 형식으로 생성해, 이후 virtual sensor 입력 형식과 end-to-end 데이터 구조를 검증하는 것이다.

## Files
- `experiments/fake_pipeline.py`
- `data/fake_pipeline/fake_pipeline_sample_2026-05-04.csv`
- `data/fake_pipeline/fake_pipeline_sample_2026-05-04.json`
- `experiments/README.md`
- `data/README.md`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `experiments/fake_pipeline.py`에 fake dataset 생성 스크립트를 추가한다.
- target trajectory는 현재 안전 구간에서 deterministic trajectory로 생성한다.
- `theta1_cmd`, `theta2_cmd`, `theta3_cmd`는 현재 IK 구현으로 계산한다.
- fake `theta*_meas`는 `theta*_cmd`에 deterministic bias/lag 성분을 더해 만든다.
- `sim_x/y/z`는 FK와 nominal model 기준으로 생성하고, 내부 fake measured position도 FK로 계산한다.
- `error_x/y/z`는 fake measured position과 nominal simulation position 차이로 계산해 correction field를 채운다.
- 출력 CSV는 현재 `docs/system_data_flow.md`의 고정 컬럼 순서를 정확히 따른다.
- sidecar JSON에는 실행 커맨드 수준의 설정, row 수, trajectory type, angle range, 생성 파라미터를 기록한다.
- `experiments/README.md`와 `data/README.md`에 fake pipeline 결과 위치를 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유, 방법, 결과, 다음 작업을 기록한다.

## Impact
- Stage 6 fake pipeline의 첫 실행 경로가 생긴다.
- virtual sensor 학습/추론 코드가 아직 없어도 입력 CSV 형식과 correction field 흐름을 점검할 수 있다.
- 실제 하드웨어나 외부 ground-truth 없이도 end-to-end dataset 생성 검증이 가능해진다.

## Risk
- fake `theta_meas`와 fake `error_*` 생성 규칙이 지나치게 단순하면 이후 실제 데이터와 분포 차이가 클 수 있다.
- trajectory를 workspace 경계 근처로 두면 IK reject가 섞여 fake pipeline 목적이 흐려질 수 있다.
- nominal-analysis range와 hardware-safe provisional range 중 어느 쪽을 쓸지 모호하면 결과 해석이 흔들릴 수 있다.

## Validation
- Python 구문 검증을 수행한다.
- fake pipeline 스크립트를 실제 실행해 CSV와 JSON 파일이 생성되는지 확인한다.
- 생성 CSV가 현재 고정 16개 컬럼 순서를 정확히 따르는지 확인한다.
- 샘플 row를 점검해 `theta_cmd`, `theta_meas`, `sim_x/y/z`, `error_x/y/z`가 모두 수치로 채워지는지 확인한다.
- 실행 로그 수준에서 row 수, trajectory 범위, IK reject 여부를 요약한다.
