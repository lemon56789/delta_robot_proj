# Delta Robot Virtual Sensing - Full Context

문서 목적: 외부 AI 모델이 이 리포지토리를 빠르게 이해하고, 분석/코드 지원을 수행할 수 있도록 프로젝트 전반을 한 파일로 요약한다.
갱신일: 2026-05-03

주의: 이 파일은 요약본이다. 상충 시 Source of Truth는 `docs/*` -> `AGENTS.md` -> `README.md` -> 코드 순서를 따른다.

## 1) 프로젝트 개요
이 프로젝트는 저가형 델타 로봇의 하드웨어 한계를 가상 센싱(Virtual Sensing)과 모델 기반 보정으로 보완해 위치 정밀도를 높이는 것을 목표로 한다.

핵심 접근:
- 저가 모터와 3D 프린팅 기반 하드웨어를 사용한다.
- Simscape 중심의 시뮬레이션 경로를 구축한다.
- 실제 로봇 로그, 시뮬레이션 데이터, 외부 ground-truth, AI 기반 가상센서를 연결한다.
- 최종 운영 단계에서는 외부 비전 측정계를 제거하고, 모터 명령/실측 각도/시뮬레이션 데이터 기반 보정만 사용한다.

## 2) 현재 시스템 흐름
기본 시스템 흐름은 아래와 같다.

```text
Target Trajectory
-> Inverse Kinematics
-> Arduino Controller
-> Delta Robot Hardware
-> Measured Data
-> Simulation Data
-> Virtual Sensor
-> Correction
-> Feedback Controller
```

의도:
- 목표 위치를 IK로 `theta*_cmd`로 변환한다.
- 실제 로봇에서 `theta*_meas`와 위치 오차 관련 데이터를 수집한다.
- Simscape 결과와 실제 로그를 시간축 기준으로 정렬한다.
- 가상센서가 위치 오차 또는 보정값을 추정한다.
- 보정값은 현재 정책상 `target_position`에 주입한다.

## 3) 주요 폴더 역할
- `docs/`: 프로젝트 문서, 시스템 설계, 운동학 메모, 비전 측정계 문서, 로드맵
- `docs/plans/`: 작업 전 승인용 계획서
- `docs/daily_notes/`: 날짜별 변경 기록
- `docs/templates/`: 계획서와 Daily Note 템플릿
- `docs/references/`: 참고 논문 및 외부 자료 보관 경로. SoT나 채택안을 의미하지 않는다.
- `kinematics/`: 역기구학/순기구학 구현 및 검증 예정 위치
- `simulation/`: RecurDyn, Nastran, Simscape 기반 시뮬레이션 자산 예정 위치
- `hardware/`: 실물 제작, 배선, BOM, 조립 자료
- `control/`: Arduino 제어 로직 및 파라미터
- `virtual_sensor/`: 가상 센서 학습/추론 코드
- `data/`: 실험/시뮬레이션 원본 및 가공 데이터
- `data/vision/raw/`: 비전 기반 raw ground-truth 로그 저장 기준 경로
- `cad/`: CAD 모델
- `experiments/`: 실험 계획, 로그, 성능 검증 자료

## 4) 좌표계와 단위
현재 기준 문서: `docs/system_data_flow.md`

기본 정의:
- position unit: `mm`
- angle unit: `deg`
- coordinate frame: `base_frame`
- origin: base center `O`
- `+x`: `B1` 방향에서 반시계 90도 회전한 방향
- `+y`: `O -> B1`의 반대 방향
- `+z`: base에서 바깥으로 나오는 방향
- workspace direction: `-z`
- right-hand rule: 사용

기구 변수:
- `sB`: base 정삼각형 변 길이
- `sP`: platform 정삼각형 변 길이
- `uB`: base 중심에서 꼭짓점까지의 거리
- `uP`: platform 중심에서 꼭짓점까지의 거리
- `wB`: base 중심에서 변까지의 거리
- `wP`: platform 중심에서 변까지의 거리
- `L`: motor-driven upper arm length
- `l`: parallelogram link length
- `B1`, `B2`, `B3`: 각 motor/base side center
- `P1`, `P2`, `P3`: 각 platform 연결점

현재 nominal geometry parameter:
- `L = 125.0 mm`
- `l = 300.0 mm`
- `wB = 24.051 mm`
- `uP = 27.177 mm`

## 5) 데이터 계약과 시간 정책
현재 기준 문서: `docs/system_data_flow.md`

Timestamp:
- field name: `time`
- format: `boot_ms`
- resolution: `ms`
- Arduino와 PC logger가 각각 timestamp를 기록한다.
- 이후 `post-alignment`로 정렬한다.
- 누락 timestamp row는 `invalid`로 표기하고 후처리에서 제외한다.

현재 CSV 고정 컬럼 순서:
1. `time`
2. `target_x`
3. `target_y`
4. `target_z`
5. `theta1_cmd`
6. `theta2_cmd`
7. `theta3_cmd`
8. `theta1_meas`
9. `theta2_meas`
10. `theta3_meas`
11. `sim_x`
12. `sim_y`
13. `sim_z`
14. `error_x`
15. `error_y`
16. `error_z`

중요:
- 기존 초기 예시의 `motor*_cmd`, `motor*_meas` 대신 현재 문서에서는 `theta*_cmd`, `theta*_meas`를 사용한다.
- correction 관련 필드는 `corr_*`가 아니라 `error_*`를 사용한다.
- CSV 구조 변경은 Contract Change로 취급한다.

## 6) 인터페이스 계약
IK:
- input order: `target_x`, `target_y`, `target_z`
- output order: `theta1_cmd`, `theta2_cmd`, `theta3_cmd`
- position 기준: `base_frame`, `mm`
- angle 기준: `deg`
- fail behavior: `reject`

Simulation:
- primary source: `Simscape`
- input: `target_x`, `target_y`, `target_z`
- output: `sim_x`, `sim_y`, `sim_z`
- `RecurDyn` 결과는 추후 cross-check용 secondary reference가 될 수 있다.

Alignment:
- 기준 clock: `PC logger`
- resampling: `linear interpolation`
- delay compensation: `post-alignment`
- `invalid` row는 alignment와 비교에서 제외한다.

Correction:
- correction target: `target_position`
- correction fields: `error_x`, `error_y`, `error_z`
- correction unavailable fallback: uncorrected target position 사용
- safety clamp 범위는 아직 미정이다.

## 7) 비전 기반 Ground-Truth 측정계
현재 기준 문서: `docs/vision_tracking.md`

역할:
- 운영 센서가 아니다.
- 학습 및 검증 단계에서만 사용하는 외부 `XY ground-truth` 측정계다.
- 최종 운영 경로는 `motor command + measured motor angle + simulation data + virtual sensing` 기준을 유지한다.

구성:
- top-view USB webcam
- ArUco marker 우선
- OpenCV 기반 marker detection
- calibration, lens distortion correction, planar homography 적용
- 좌표 결과는 `base_frame` 기준 `mm`로 변환

범위:
- 단일 top-view webcam 기준으로 `XY` 위치를 측정한다.
- `Z` 위치는 직접 ground-truth로 제공하지 않는다.
- 비전 로그는 메인 CSV 필수 컬럼에 직접 편입하지 않는다.
- timestamp 기준 후처리로 메인 로그와 병합한다.

비전 로그 저장 기준:
- 기본 경로: `data/vision/raw/`
- 최소 파일명 규칙: `vision_<run_id>.csv`
- 최소 필드: `vision_time`, `vision_x`, `vision_y`, `marker_detected`, `frame_id`
- 선택 필드: `marker_id`, `reprojection_error`, `confidence`, `video_file`

## 8) IK 구조 정리 상태
현재 기준 문서: `docs/ik_structure_note.md`

문서 성격:
- 구현 채택안 자체라기보다, `2atan(t)` 기반 IK를 프로젝트 변수로 해석하기 위한 reference 메모다.
- 현재는 문서 기준 수식 구조와 branch 선택 규칙이 정리되어 있고, 이를 따르는 최소 Python 구현이 추가되어 있다.

`theta_i` 정의:
- `theta_i`는 arm `i`의 local actuation plane에서 정의되는 upper arm 회전각이다.
- `theta_i = 0 deg`: upper arm이 `base plane`에 놓인 자세
- `theta_i = +90 deg`: upper arm이 workspace direction인 `-z`와 평행한 자세
- 양의 방향: upper arm이 base plane에서 workspace 방향으로 내려가는 회전 방향

핵심 IK 흐름:
1. 입력 `(x, y, z)`를 `base_frame` 기준 `mm`로 받는다.
2. 각 arm의 `B_i`, `P_i`, `J_i(theta_i)`를 정의한다.
3. 길이 제약식 `|P_i - J_i(theta_i)|^2 = l^2`를 둔다.
4. 각 arm에 대해 `E_i cos(theta_i) + F_i sin(theta_i) + G_i = 0` 형태로 정리한다.
5. `t_i = tan(theta_i / 2)` 치환을 적용한다.
6. `t_i`에 대한 2차식 해를 구한다.
7. `theta_i = 2 atan(t_i)`로 각도를 복원한다.
8. 판별식, 임시 각도 범위, downward-working branch, 이전 각도 연속성 기준으로 root를 선택한다.

arm outward unit vector:
- `e_1 = (0, -1)`
- `e_2 = ((sqrt(3) / 2), (1 / 2))`
- `e_3 = (-(sqrt(3) / 2), (1 / 2))`

대표 좌표식:
- `B_i = wB e_i`
- `P_i = (x, y) + uP e_i`
- `J_i(theta_i) = (wB + L cos(theta_i)) e_i + (-L sin(theta_i)) k`

arm 1 예시:
- `P_1 = (x, y - uP, z)`
- `J_1(theta_1) = (0, -wB - L cos(theta_1), -L sin(theta_1))`
- `E_1 = 2 L (y - uP + wB)`
- `F_1 = 2 L z`
- `G_1 = x^2 + (y - uP + wB)^2 + z^2 + L^2 - l^2`

일반화:
- `r = (x, y)`
- `p_i = r · e_i`
- `E_i = -2 L (p_i + uP - wB)`
- `F_i = 2 L z`
- `G_i = x^2 + y^2 + (uP - wB)^2 + 2 (uP - wB) p_i + z^2 + L^2 - l^2`

반각 해:
- `t_i = (-F_i ± sqrt(E_i^2 + F_i^2 - G_i^2)) / (G_i - E_i)`
- `theta_i = 2 atan(t_i)`

root selection:
- 판별식 `E_i^2 + F_i^2 - G_i^2 < 0`이면 reject
- 현재 hardware-safe provisional range는 `0 deg <= theta_i <= 90 deg`
- downward-working branch에 속하는 해만 유효 후보로 둔다.
- 후보가 둘이면 `previous_theta_i`와 가장 가까운 해를 선택한다.
- 후보가 없으면 reject한다.

남은 IK 관련 미정 항목:
- `theta_cmd`와 실제 모터 구동축/드라이버 명령의 정확한 연결
- 최종 `theta_min`, `theta_max`
- FK 기반 역검증 절차

현재 코드 상태:
- `kinematics/geometry.py`에 `DeltaGeometry` dataclass와 `NOMINAL_DELTA_GEOMETRY`가 정의되어 있다.
- `kinematics/inverse_kinematics.py`에 `delta_ik(x_mm, y_mm, z_mm)`가 구현되어 있다.
- 구현은 각 arm별 일반화된 `E_i`, `F_i`, `G_i` 식, 판별식 기반 reject, 임시 각도 범위, `previous_theta_deg` 기반 해 선택을 사용한다.
- 반각 해를 프로젝트 `+theta = downward` 정의에 맞추기 위해 코드에서 각도 부호 보정을 적용한다.
- 간단한 sample point에 대해 실제 각도 계산이 수행되는 최소 실행 검증은 완료되었다.
- 현재 nominal-analysis candidate range는 `-10 deg <= theta_i <= 90 deg`이고, hardware-safe provisional range는 `0 deg <= theta_i <= 90 deg`로 분리해 관리한다.

## 9) 프로젝트 로드맵
현재 기준 문서: `docs/roadmap.md`

전체 단계:
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

현재 상태 요약:
- Stage 1 설계 기준 확정: 완료
- Stage 2 운동학 정의 및 구현: nominal geometry 및 IK 최소 구현 완료, FK/정식 검증은 미완료
- Stage 3 FK 검증 및 기본 해석: 미착수
- Stage 4 시뮬레이션 및 데이터 경로 정리: 부분 완료
- Stage 5 외부 ground-truth 측정계 구축: 문서화 완료, 구현 미착수
- Stage 6 fake pipeline 구성: 미착수
- Stage 7 실제 데이터 수집: 미착수
- Stage 8 가상센서 학습 및 보정: 미착수
- Stage 9 폐루프 적용 및 성능 검증: 미착수
- Stage 10 외부 측정계 제거 후 운영 검증: 미착수

## 10) 개발 및 변경 원칙
AGENTS.md 기준 핵심 원칙:
- 변경 전 계획서 작성 및 사용자 승인 필수
- 승인 전 파일 변경 금지
- 어떤 파일이든 수정/추가/삭제하면 `docs/daily_notes/YYYY-MM-DD.md`에 기록
- placeholder/dummy 구현 금지
- 데이터 포맷, 함수 입력/출력, 폴더 구조, 시스템 데이터 흐름 임의 변경 금지
- Contract Change는 명시 승인 필요
- 모든 실험은 실행 커맨드, 사용 데이터, 파라미터, 코드 버전을 기록

## 11) 현재 기술 스택
- Python 3.12.3
- MATLAB / Simulink / Simscape
- Arduino
- PyTorch
- OpenCV
- GitHub

## 12) 바로 다음 작업
우선순위:
1. FK 최소 구현을 추가하고 IK→FK 왕복 검증을 붙인다.
2. sample/workspace 검증 스크립트를 추가해 reachable 영역과 branch 선택을 점검한다.
3. `theta_cmd`와 실제 모터 구동축 명령 매핑을 하드웨어 기준으로 정리한다.
4. fake pipeline 범위와 출력 형식을 계획서로 고정한다.
5. 현재 CSV 계약에 맞는 fake dataset 생성 스크립트를 구현한다.

BLOCKER 가능성이 있는 항목:
- 모터 축과 `theta_cmd`의 실제 연결이 확정되지 않으면 hardware-level command mapping은 보류해야 한다.
- nominal parameter와 실제 조립 치수 차이가 크면 FK/validation 결과 해석이 흔들릴 수 있다.
- vision calibration 데이터가 없으면 비전 ground-truth는 문서 기준만 있고 실제 측정 정확도 검증은 할 수 없다.

## 13) 유지보수 규칙
- 이 파일은 외부 AI 분석용 요약본이다.
- 구조, 규약, 데이터 계약, 로드맵 상태가 바뀌면 함께 갱신한다.
- 상세 근거는 `docs/system_data_flow.md`, `docs/vision_tracking.md`, `docs/ik_structure_note.md`, `docs/roadmap.md`, `AGENTS.md`를 우선 참조한다.
