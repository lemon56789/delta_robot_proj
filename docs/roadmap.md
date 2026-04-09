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

## 12. Stage 8. 가상센서 학습 및 보정
### Goal
모터 명령, 모터 실측, 시뮬레이션 데이터를 사용해 위치 오차 또는 보정값을 추정하는 모델을 만든다.

### Main Tasks
- feature/label 정의
- 학습 데이터셋 분리
- baseline 모델 구성
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
1. 기구 파라미터 수치 확정
2. IK 실제 코드 구현
3. FK 검증 구조 준비
4. fake pipeline 실행
5. 실험 로그 저장 구조 점검
6. vision ground-truth 수집 절차 초기 검증

## 16. Open Items
- 최종 기구 파라미터 값
- `theta_cmd`와 실제 구동축의 정확한 연결
- 최종 `theta_min`, `theta_max`
- FK 구현 범위와 검증 기준
- fake pipeline 출력 수준
- virtual sensor baseline 모델 형태
- correction safety limits
- merged dataset 저장 규칙

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
