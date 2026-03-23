# Delta Robot Virtual Sensing - Full Context

문서 목적: 외부 AI 모델이 이 리포지토리를 빠르게 이해하고, 분석/코드 지원을 수행할 수 있도록 프로젝트 전반을 한 파일로 정리한다.
갱신일: 2026-03-22

## 1) 프로젝트 개요
저가형 델타 로봇의 하드웨어 한계를 가상 센싱(Virtual Sensing)과 모델 기반 보정으로 보완해 위치 정밀도를 높이는 프로젝트다.

핵심 접근:
- 저가 모터 + 3D 프린팅 기반 하드웨어
- 시뮬레이션 기반 디지털 트윈
- 실측 + 시뮬레이션 + AI 결합 보정

## 2) 시스템 흐름
Target Trajectory
-> Controller
-> Real Robot
-> Measured Data
-> Virtual Sensor
-> Correction
-> Feedback

의도:
- 실제 로봇에서 발생하는 오차를 가상 센서가 추정/보정
- 보정값을 제어 루프에 반영하여 목표 궤적 추종 성능 개선

## 3) 주요 폴더 역할
- `docs/`: 프로젝트 문서(요구사항, 설계, 회의 기록)
- `docs/plans/`: 작업 계획서
- `docs/daily_notes/`: 날짜별 작업 기록
- `docs/templates/`: 문서 템플릿
- `kinematics/`: 역기구학/순기구학 수식 및 검증
- `simulation/`: RecurDyn, Nastran, Simscape 기반 시뮬레이션 자산
- `hardware/`: 실물 제작/배선/BOM/조립 자료
- `control/`: Arduino 제어 로직 및 파라미터
- `virtual_sensor/`: 가상 센서 학습/추론 코드
- `data/`: 실험/시뮬레이션 원본 및 가공 데이터
- `cad/`: CAD 모델(STEP/STL)
- `experiments/`: 실험 계획/로그/성능 검증

## 4) 데이터 계약(CSV)
기본 컬럼 순서:
- time
- target_x, target_y, target_z
- motor1_cmd, motor2_cmd, motor3_cmd
- motor1_meas, motor2_meas, motor3_meas
- sim_x, sim_y, sim_z
- error_x, error_y, error_z

원칙:
- 컬럼 순서는 고정
- 인터페이스/데이터 포맷 변경은 Contract Change로 취급

## 5) 인터페이스 계약
- 역기구학: input `(x, y, z)`, output `(theta1, theta2, theta3)`
- 제어기: input `target`, output `motor command`
- 가상 센서: input `motor + simulation (+ measured)`, output `corrected position / correction`

## 6) 개발 및 변경 원칙 (요약)
- Source of Truth 우선순위: `docs/*` -> `AGENTS.md` -> `README.md` -> 코드
- 변경 전 계획서 작성 및 승인 필수
- 승인 전 파일 변경 금지
- 변경 후 Daily Notes 기록
- placeholder/dummy 코드 금지
- 인터페이스 무단 변경 금지

## 7) 현재 기술 스택(명시)
- Python 3.12.3
- MATLAB / Simulink / Simscape
- Arduino
- PyTorch
- GitHub

## 8) 현재 상태와 다음 확장 포인트
현재 리포는 폴더 구조와 역할 정의 중심의 초기 정리 단계다. 세부 구현/실험 산출물은 앞으로 축적될 수 있으며, 아래 항목을 우선 채워나갈 필요가 있다.

- `docs/plans/`에 작업 계획서 누적
- `docs/daily_notes/`에 작업 이력 누적
- `data/`에 실측/시뮬레이션 데이터셋 축적
- `virtual_sensor/`, `control/`, `kinematics/` 구현 구체화

## 9) 유지보수 규칙 (이 파일)
- 본 파일은 외부 AI 분석용 요약본이다.
- 구조/규약/데이터 계약이 바뀌면 즉시 동기화한다.
- 상세 근거는 각 원문 문서(`AGENTS.md`, `README.md`, `docs/*`)를 우선 참조한다.
