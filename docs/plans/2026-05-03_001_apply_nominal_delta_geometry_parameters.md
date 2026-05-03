# Plan

## Goal
모델링 기준으로 확보한 델타 로봇 기하 파라미터 `L=125 mm`, `l=300 mm`, `wB=24.051 mm`, `uP=27.177 mm`를 현재 리포지토리의 운동학 기준값으로 반영하고, 해당 값을 사용하는 최소 동작 가능한 inverse kinematics 구현 기반을 추가한다.

## Files
- `kinematics/README.md`
- `kinematics/geometry.py`
- `kinematics/inverse_kinematics.py`
- `docs/daily_notes/2026-05-03.md`

## Changes
- `kinematics/README.md`에 현재 운동학 모듈 구성과 nominal geometry parameter를 명시한다.
- `kinematics/geometry.py`에 델타 로봇 기하 파라미터 dataclass와 기본 nominal parameter 상수를 추가한다.
- `kinematics/inverse_kinematics.py`에 현재 문서화된 `E/F/G` 및 `2atan(t)` 구조를 따르는 inverse kinematics 함수를 구현한다.
- 구현은 입력 `(x, y, z)` 단위 `mm`, 출력 `(theta1, theta2, theta3)` 단위 `deg`, 실패 시 `reject` 원칙을 유지한다.
- 구현 시 현재 문서 기준 임시 working range `0 deg <= theta_i <= 90 deg`를 사용한다.
- 작업 후 `docs/daily_notes/2026-05-03.md`에 변경 이유, 방법, 결과, 다음 작업을 기록한다.

## Impact
- `kinematics/` 아래에 실제 재사용 가능한 Python 구현이 처음 추가된다.
- 이후 `control/`, `simulation/`, `virtual_sensor/`에서 공통으로 참조할 수 있는 nominal geometry 기준점이 생긴다.
- 공개 데이터 포맷이나 기존 문서 계약은 변경하지 않는다.

## Risk
- 현재 파라미터는 모델링 기준값이므로 실제 하드웨어와 오차가 있을 수 있다.
- arm 2, arm 3의 일반화 식과 root selection 규칙이 문서 기준과 구현 기준 사이에서 부호 혼동을 일으킬 수 있다.
- 실제 reachable workspace와 임시 각도 범위 `0~90 deg`가 완전히 일치하지 않을 수 있다.

## Validation
- 정적 코드 검토로 구현이 `docs/system_data_flow.md` 및 `docs/ik_structure_note.md`의 계약과 일치하는지 확인한다.
- 간단한 샘플 position에 대해 함수가 각도 3개 또는 `reject`를 일관되게 반환하는지 실행 검증한다.
- Python 구문 검증과 최소 실행 테스트를 수행한다.
