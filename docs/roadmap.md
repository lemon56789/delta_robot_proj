# Delta Robot Project Roadmap

## 1. Goal
본 문서는 델타 로봇 가상센싱 프로젝트의 전체 실행 로드맵을 정리한다.
프로젝트의 목표는 저가형 델타 로봇의 위치 정확도를 향상시키고, 최종적으로는 외부 측정계 없이도 가상센싱 기반 보정이 가능한 시스템을 만드는 것이다.

## 2. Final Target
- 델타 로봇 하드웨어와 제어 시스템을 구축한다.
- 좌표계, 기구 변수, IK/FK, 데이터 계약을 일관되게 정리한다.
- 실제 구동 데이터와 시뮬레이션 데이터를 비교 가능한 형태로 정렬한다.
- 초기에는 외부 비전 기반 `XY ground-truth` 측정계를 사용한다.
- 가상센서를 통해 위치 오차 또는 보정값을 추정한다.
- 운영 단계에서는 외부 비전 시스템을 제거하고, 모터 각도 실측값과 시뮬레이션 데이터 기반 가상센싱만 사용한다.

## 3. Project Principles
- 모든 구현과 문서는 현재 SoT(`docs/*`) 기준으로 정렬한다.
- 좌표계, 시스템 데이터 흐름, CSV 구조, 인터페이스는 임의 변경하지 않는다.
- 변경 전 계획서 작성, 변경 후 Daily Note 기록 원칙을 따른다.
- 실험은 실행 커맨드, 데이터, 파라미터, 코드 버전을 함께 기록한다.
- 초기에는 최소 기능 동작을 우선 확보하고, 이후 정확도와 안정성을 개선한다.

## 4. Stage Overview
1. 설계 기준 확정
2. 운동학 정의 및 구현
3. FK 검증 및 기본 해석
4. 시뮬레이션 및 데이터 경로 정리
5. 외부 ground-truth 측정계 구축
6. fake pipeline 구성
7. 실제 데이터 수집
8. 가상센서 학습 및 보정
9. 폐루프 적용 및 성능 검증
10. 외부 측정계 제거 후 운영 검증

## 4-A. Current Status Snapshot
- 기준일: `2026-06-10`
- Stage 1 설계 기준 확정: 완료
- Stage 2 운동학 정의 및 구현: 진행 중
- Stage 3 FK 검증 및 기본 해석: 진행 중
- Stage 4 시뮬레이션 및 데이터 경로 정리: Run 01/02 Simscape 및
  alignment/merge 경로 구현 완료
- Stage 5 외부 ground-truth 측정계 구축: Run 00/01/02 vision XY 수집과
  후처리 검증 완료, home 반복성 품질 확인 필요
- Stage 6 fake pipeline 구성: 최소 경로 완료
- Stage 7 실제 데이터 수집: Run 00, Run 01-pre, Run 01-main, holdout 및
  Run 02 24개 run 수집 완료
- Stage 8 가상센서 학습 및 보정: Ridge baseline 학습, holdout 평가 및
  correction engine 구현 완료
- Stage 9 폐루프 적용 및 성능 검증: PC-side feedforward Run 02 검증과
  재분석 완료, 전체 개선은 확인되지 않음
- Stage 10 외부 측정계 제거 후 운영 검증: 미착수

현재 구현 기준 핵심 상태:
- `docs/system_data_flow.md`, `docs/ik_structure_note.md`, `docs/vision_tracking.md`가 현재 SoT 역할을 수행한다.
- nominal geometry parameter `L=125.0 mm`, `l=300.0 mm`, `wB=46.0 mm`, `uP=27.177 mm`가 코드 기준값으로 반영되었다.
- `kinematics/geometry.py`에 geometry dataclass와 nominal parameter가 추가되었다.
- `kinematics/inverse_kinematics.py`에 `delta_ik(x_mm, y_mm, z_mm)` 최소 구현과 arm별 reject 진단이 추가되었다.
- `kinematics/forward_kinematics.py`, `kinematics/validate_roundtrip.py`, `kinematics/workspace_sweep.py`가 추가되어 IK↔FK round-trip 검증과 workspace sweep이 가능해졌다.
- `-45..90 deg`를 현재 `hardware-safe provisional range`이자 `nominal-analysis candidate range`로 문서화했다.
- `experiments/fake_pipeline.py`가 current CSV 계약을 따르는 end-to-end fake dataset CSV/JSON을 생성한다.
- `virtual_sensor/dataset.py`, `virtual_sensor/check_dataset.py`로 fake pipeline CSV를 읽는 최소 loader와 shape check 경로를 확보했다.
- Run 00 A/B/C gate는 통과 상태로 정리되었다.
- Run 01-pre static/cross/square raw main, vision, Simscape CSV가 확보되었고, `experiments/run01_preprocess.py`로 angle-derived measured position과 processed merged dataset을 생성했다.
- Run 01-pre merged dataset은 `virtual_sensor/check_dataset.py`에서 16-column shape와 `has_nan=False`를 확인했다. 다만 pre 산출물은 pipeline validation용이며 최종 학습 데이터로 채택하지 않는다.
- Run 01-main 15개 processed dataset은 phase-boundary realignment 후
  총 `5,158` row로 확정되었고 Ridge 학습에 사용했다.
- Run 01 complete holdout 4개에서 frozen Ridge macro XY RMSE는
  `4.533 -> 2.848 mm`, `37.174%` 개선됐다.
- Run 02는 gain `0.25`, XY clamp `2 mm`로 24개 fresh hardware run과
  12개 OFF/ON pair를 수집했다.
- Run 02 네 trajectory 동일가중 absolute XY RMSE는 OFF `6.3582 mm`,
  ON `6.4222 mm`로 평균 RMSE 직접 비교 기준 `1.01%` 악화됐다.
  Diamond는 세 pair 모두 개선됐지만 전체 개선으로 판단하지 않는다.

## 5. Stage 1. 설계 기준 확정
### Goal
전체 구현이 동일한 기준 위에서 돌아가도록 좌표계, 기구 변수, 인터페이스, CSV 계약을 먼저 고정한다.

### Main Tasks
- `base_frame`, 원점, 축 방향, workspace 방향 확정
- `sB`, `sP`, `uB`, `uP`, `wB`, `wP`, `L`, `l` 의미 정리
- `theta_i` 정의, branch, 해 선택 규칙 정리
- IK 입력/출력 계약 확정
- CSV 컬럼 순서와 명명 규칙 정리
- 시스템 데이터 흐름 문서화

### Outputs
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- 관련 계획서 및 daily notes

### Exit Criteria
- 좌표계와 변수 의미가 문서로 정리되어 있다
- IK 입력/출력과 CSV 구조가 고정되어 있다
- fake pipeline과 구현 코드가 참조할 인터페이스가 존재한다

## 6. Stage 2. 운동학 정의 및 구현
### Goal
델타 로봇의 기구학 모델을 정의하고, IK를 실행 가능한 코드 형태로 구현한다.

### Main Tasks
- base/platform geometry 수치 확정
- 기구 파라미터 정의
- `B_i`, `P_i`, `J_i` 좌표식 정리
- arm direction symmetry 정리
- arm별 `E_i`, `F_i`, `G_i` 유도
- 반각 치환 기반 IK 해 구조 정리
- `+/-` 해 선택 규칙 반영
- `delta_IK(x, y, z)` 함수 구현
- sample point 테스트

### Outputs
- `kinematics/` IK 구현
- IK 관련 테스트 코드 또는 검증 스크립트
- 운동학 문서

### Exit Criteria
- `(x, y, z)` 입력에서 `(theta1, theta2, theta3)`를 계산할 수 있다
- reject 조건과 해 선택 규칙이 코드에 반영된다
- sample point에 대해 일관된 결과가 나온다

### Current Status
- nominal geometry parameter는 현재 `L=125.0 mm`, `l=300.0 mm`, `wB=46.0 mm`, `uP=27.177 mm`로 정의되어 있다.
- `kinematics/geometry.py`에서 geometry dataclass와 nominal parameter 상수를 제공한다.
- `kinematics/inverse_kinematics.py`에서 문서 기준 `E/F/G + 2atan(t)` 구조의 IK가 구현되어 있다.
- `reject` 처리, arm별 failure diagnostic, `previous_theta_deg` 기반 연속성 선택이 코드에 반영되어 있다.
- 간단한 sample point 실행 검증은 완료되었다.
- workspace sweep과 설치 높이/workspace envelope 검토를 통해 현재 provisional/analysis 기준 range `-45 deg <= theta_i <= 90 deg`를 사용한다.
- hardware-confirmed range는 실제 조립, 반복 구동, 간섭 및 구동 제약 확인 후 별도 확정한다.

## 7. Stage 3. FK 검증 및 기본 해석
### Goal
FK를 정리하고, IK↔FK 왕복 검증으로 운동학 일관성을 확인한다.

### Main Tasks
- elbow position 계산
- FK 구조 정리
- IK → FK 왕복 검증
- random/sample position 검증
- error metric 계산
- 필요 시 Jacobian 또는 singularity 기초 분석

### Outputs
- FK 구현 또는 검증 스크립트
- IK/FK 비교 결과
- 초기 오차 분석 메모

### Exit Criteria
- IK 결과를 FK에 넣었을 때 위치가 허용 오차 안에서 복원된다
- 주요 workspace 점에서 큰 모순이 없다

### Current Status
- `kinematics/forward_kinematics.py`에 수치해석 기반 FK 최소 구현이 추가되었다.
- `kinematics/validate_roundtrip.py`에서 sample point 기준 IK→FK 왕복 검증이 가능하다.
- `kinematics/workspace_sweep.py`에서 coarse sweep, `z=-260 mm` band sweep, IK reject cause 진단, `theta_min` sweep을 수행할 수 있다.
- 현재 coarse sweep과 band sweep에서는 FK 미수렴보다 angle range 제약이 주요 경계 요인으로 관찰된다.
- 남은 작업은 더 넓은 workspace 검증, 특이점/경계 근처 해석, 하드웨어 허용 범위와 nominal analysis 범위의 연결이다.

## 8. Stage 4. 시뮬레이션 및 데이터 경로 정리
### Goal
실제 시스템과 비교 가능한 시뮬레이션 경로와 데이터 저장 구조를 만든다.

### Main Tasks
- Simscape 기반 simulation input/output 정리
- geometry, mass, friction 파라미터 소스 연결
- real log와 sim log의 time alignment 정책 정리
- `data/`, `experiments/` 저장 규칙 정리
- merged dataset 생성 방식 정리

### Outputs
- simulation 관련 문서
- 실험 로그 구조
- 데이터 저장 규칙

### Exit Criteria
- 동일 target 기준으로 real/sim 비교가 가능하다
- timestamp alignment 정책이 문서화되어 있다
- 실험별 데이터 저장 구조가 재현 가능하다

### Current Status
- `data/fake_pipeline/fake_pipeline_sample_2026-05-04_recomputed.csv`와 `data/fake_pipeline/fake_pipeline_sample_2026-05-25_positive_theta.csv`는 `wB = 46.0 mm` 기준으로 다시 생성되었다.
- `data/fake_pipeline/fake_pipeline_sample_2026-05-04_recomputed_simscape.csv`와 `data/fake_pipeline/fake_pipeline_sample_2026-05-25_positive_theta_simscape.csv`는 `wB = 24.051 mm` 기준 old-geometry artifact이므로, Simscape comparison output은 다시 생성해야 한다.
- 기존 comparison에서는 `theta*_cmd`와 `theta*_meas`가 Python 기준과 직접 일치했고, `sim_x`, `sim_y`, `sim_z`는 provisional `1 sample = 20 ms` lag 보정 후 Python 기준과 매우 가깝게 정렬되었다.
- 다만 현재 `Simscape` CSV의 `error_x`, `error_y`, `error_z`는 `target_position - sim_position` diagnostic 값이며, SoT correction field 의미인 `measured_position - sim_position`과 다르다.
- 하드웨어 또는 estimator 경로에서 `measured_position`을 확보한 뒤 `Simulink/Simscape` export의 `error_*` 계산을 SoT 기준으로 수정해야 한다.
- Run 01-pre real/sim/vision 로그 기준으로 `data/real/derived/measured_position_<run_id>.csv`와 `data/processed/merged_<run_id>.csv` 생성 경로가 실제 파일로 검증되었다.
- Run 01-main과 Run 02에서는 trajectory-aware alignment와 phase-boundary
  realignment를 적용해 processed merged dataset을 생성했다.
- Run 02 전처리는 24개 measured-position CSV, fixed 16-column merged
  CSV와 alignment sidecar JSON을 생성하고 12개 OFF/ON pair를 비교한다.

## 9. Stage 5. 외부 Ground-Truth 측정계 구축
### Goal
초기 학습 및 검증에 사용할 외부 비전 기반 `XY ground-truth` 측정계를 구축한다.

### Main Tasks
- top-view 카메라 설치
- marker 방식 선택
- calibration 및 homography 정리
- `data/vision/raw/` 기준 raw 로그 저장
- vision log와 main log의 post-alignment 기준 정리

### Outputs
- `docs/vision_tracking.md`
- 비전 raw 로그
- ground-truth 생성 절차

### Exit Criteria
- 엔드이펙터 `XY` 위치를 외부 기준으로 기록할 수 있다
- main log와 vision log를 후처리로 정렬할 수 있다

### Current Status
- Run 00-C stopcheck와 Run 01-pre static/cross/square에서 `data/vision/raw/vision_<run_id>.csv` 형식의 vision raw log가 생성되었다.
- Run 01-pre 기준 static은 marker/valid ratio `100%`, cross는 약 `92.98%`, square는 약 `93.21%`로 확인되었다.
- Run 01-main, holdout과 Run 02에서 vision XY 수집 및 후처리 경로를
  사용했다.
- 초기 home 위치 차이가 correction 크기와 비슷하거나 더 크게 나타난
  pair가 있어 preload 기반 home 반복성 품질 확인이 후속 과제다.

## 10. Stage 6. Fake Pipeline 구성
### Goal
실제 전체 시스템 전에 데이터 흐름을 끝까지 통과시키는 최소 파이프라인을 만든다.

### Main Tasks
- target input 생성
- IK 계산
- fake `theta_meas` 생성
- fake `sim_x/y/z` 생성
- 현재 CSV 계약에 맞는 데이터 생성
- virtual sensor 입력 형식 확인
- correction output과 feedback path 연결 구조 점검

### Outputs
- fake dataset 생성 스크립트
- end-to-end CSV 샘플
- fake pipeline 실행 커맨드

### Exit Criteria
- 실제 하드웨어 없이도 전체 데이터 흐름을 한 번 실행할 수 있다
- CSV 형식이 현재 계약과 일치한다
- virtual sensor 학습/추론 입출력 구조를 점검할 수 있다

### Current Status
- `experiments/fake_pipeline.py`가 deterministic trajectory, IK, fake `theta_meas`, FK 기반 `sim_x/y/z`, `error_x/y/z`를 생성한다.
- 결과는 `data/fake_pipeline/fake_pipeline_sample_2026-05-04.csv`와 sidecar JSON으로 저장된다.
- 현재 목적은 realistic sensor model이 아니라 CSV 계약과 end-to-end wiring 검증이다.
- `virtual_sensor/dataset.py`와 `virtual_sensor/check_dataset.py`로 해당 CSV를 읽어 feature/target shape, NaN 여부, 기초 통계를 확인할 수 있다.
- Stage 6의 fake pipeline 목적은 달성됐으며, 실제 모델과 correction
  검증은 Stage 8~9 경로로 확장되었다.

## 11. Stage 7. 실제 데이터 수집
### Goal
실제 로봇, 시뮬레이션, 외부 ground-truth를 연결한 학습/검증용 데이터셋을 구축한다.

### Main Tasks
- target trajectory 실행
- `theta_cmd`, `theta_meas` 로깅
- sim output 수집
- vision 기반 `XY ground-truth` 수집
- invalid row 처리
- 실험 메타데이터 기록

### Outputs
- raw dataset
- 실험 로그
- 정렬된 비교 데이터셋

### Exit Criteria
- 재현 가능한 실험 세트가 확보된다
- real/sim/vision 데이터를 같은 기준으로 비교할 수 있다

### Current Status
- Run 00 A/B/C gate는 통과했다.
- Run 01-pre는 final training dataset이 아니라 pipeline validation 단계로 완료되었다.
- Run 01-pre 산출물:
  - `data/real/raw/main_2026-06-05_run01_pre_*.csv`
  - `data/vision/raw/vision_2026-06-05_run01_pre_*.csv`
  - `data/simulation/raw/simscape_2026-06-05_run01_pre_*.csv`
  - `data/real/derived/measured_position_2026-06-05_run01_pre_*.csv`
  - `data/processed/merged_2026-06-05_run01_pre_*.csv`
- Run 01-main은 5개 trajectory를 각 3회 수행한 총 15개 run이며,
  phase-boundary realignment 후 `5,158` processed row로 확정되었다.
- complete holdout 4개는 fitting과 tuning에서 제외하고 최종 일반화
  평가에 사용했다.
- Run 02는 4개 trajectory의 OFF/ON을 각 3회 수행해 총 24개 run과
  12개 paired comparison을 확보했다.

## 12. Stage 8. 가상센서 학습 및 보정
### Goal
모터 명령, 모터 실측, 시뮬레이션 데이터를 사용해 위치 오차 또는 보정값을 추정하는 모델을 만든다.

### Main Tasks
- feature/label 정의
- 학습 데이터셋 분리
- linear regression/Ridge baseline 모델 구성
- loss/metric 정의
- `error_x`, `error_y`, `error_z` 또는 위치 추정 출력 정리
- 성능 평가

### Outputs
- virtual sensor 모델
- 학습/추론 코드
- 성능 리포트

### Exit Criteria
- baseline 대비 오차 감소가 수치로 확인된다
- 모델 입출력이 현재 시스템 계약과 맞는다

### Current Status
- 첫 모델은 NumPy 기반 standardized Ridge regression으로 구현했다.
- 기본 feature는 `theta*_cmd`, `theta*_meas`, `sim_x/y/z`이고 target은
  processed merged dataset의 `error_x/y/z`다.
- repetition 단위 run-level 3-fold CV로 `alpha=100`을 선택하고 Run
  01-main 15개 전체로 최종 모델을 재학습했다.
- 최종 모델은
  `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`다.
- complete holdout 4개의 macro XY RMSE는 zero prediction `4.533 mm`,
  Ridge residual `2.848 mm`로 `37.174%` 개선됐다.
- `virtual_sensor/correction_engine.py`는 predicted error를 XY target
  correction, vector clamp, corrected-target IK와 nominal fallback으로
  변환한다.
- PyTorch MLP는 Ridge baseline보다 명확한 개선 필요성이 확인될 때의
  후속 확장으로 둔다.

## 13. Stage 9. 폐루프 적용 및 성능 검증
### Goal
가상센서 보정값을 제어 경로에 반영해 실제 추종 성능 개선 여부를 검증한다.

### Main Tasks
- correction injection point 적용
- safety clamp 설정
- baseline vs corrected 비교 실험
- RMSE, max error, trajectory error 평가
- 반복 실험으로 신뢰성 확인

### Outputs
- corrected control path
- 성능 비교 결과
- 검증 로그

### Exit Criteria
- baseline 대비 유의미한 성능 개선이 있다
- correction failure 시 fallback 동작이 가능하다

### Current Status
- 현재 제어는 encoder feedback closed loop가 아니라
  `theta*_meas=command_echo_no_encoder` 기반 PC-side feedforward
  correction이다.
- Run 02는 gain `0.25`, XY vector norm clamp `2 mm`, Z correction off로
  24개 fresh hardware run을 완료했다.
- 네 trajectory 동일가중 absolute XY RMSE는 OFF `6.3582 mm`, ON
  `6.4222 mm`로 평균 RMSE 직접 비교 기준 `1.01%` 악화됐다.
- Diamond는 absolute와 home-normalized 기준 모두 세 pair가 개선됐지만,
  Cross는 actuator integer resolution, reverse grid는 home offset,
  Circle은 tangential error와 약 `350 ms` phase lag 영향이 확인됐다.
- correction fallback 경로는 구현됐지만 전체 trajectory에서 일관된
  성능 개선이라는 Stage 9 exit criterion은 충족하지 못했다.

## 14. Stage 10. 외부 측정계 제거 후 운영 검증
### Goal
외부 비전 시스템 없이도 운영 가능한 가상센싱 기반 보정 시스템으로 전환한다.

### Main Tasks
- vision system 제거
- 운영 입력을 `theta_cmd`, `theta_meas`, `simulation data`로 제한
- 외부 ground-truth 없이도 안정 동작 확인
- 필요 시 재교정 절차 설계

### Outputs
- 운영 모드 정의
- 최종 시스템 구성 문서
- 제거 전/후 성능 비교 결과

### Exit Criteria
- 외부 측정계 없이도 시스템이 동작한다
- 프로젝트 최종 목표와 일치하는 운용 구조가 된다

## 15. Immediate Priorities
1. xp40 preload 후 home repeatability `r01-r03`을 수집한다.
2. xp40이 진동, 간섭, stall 없이 끝난 경우에만 xp60 `r01-r03`을
   수집한다.
3. 마지막 home stabilization 구간의 XY 중앙값, 표준편차, 반복 간
   최대 거리와 drift를 비교해 공통 preload를 선택한다.
4. 선택한 preload로 Diamond 최소 OFF/ON 1 pair 실행 절차를 확정한다.
5. 추가 Diamond 결과를 absolute, home-normalized, transition/stable
   metric으로 기존 Run 02와 비교한다.
6. Cross는 actuator command resolution 개선 전 재실험 우선순위를
   낮게 두고, Circle은 정적 correction과 dynamic lag 분리 정책을 먼저
   검토한다.

## 16. Open Items
- `theta_cmd`와 실제 구동축의 정확한 연결
- 최종 `theta_min`, `theta_max`
- FK 경계 및 특이점 근처 검증
- base config의 `sign_i=+1` 기록과 Run 02 firmware effective
  `sign_i=-1`, `theta_gain_i=1.25` 간 정합성
- preload 기반 home 반복성
- integer servo command resolution 개선
- Circle의 정적 오차와 동적 phase lag 분리
- encoder 또는 별도 motor angle measurement 확보

## 17. Document Relation
- 시스템 인터페이스 기준: `docs/system_data_flow.md`
- IK 구조 메모: `docs/ik_structure_note.md`
- 외부 비전 측정계: `docs/vision_tracking.md`
- 작업 규칙: `AGENTS.md`
- 프로젝트 요약: `README.md`

## 18. Update Rule
- 단계 구조가 바뀌면 본 문서를 갱신한다.
- 세부 구현이 바뀌더라도 단계 구조가 유지되면 하위 문서를 우선 수정한다.
- 단계 완료나 범위 변경 시 Daily Note에도 함께 기록한다.
