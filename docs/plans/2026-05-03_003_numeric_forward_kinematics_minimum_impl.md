# Plan

## Goal
현재 nominal geometry와 inverse kinematics 구현을 기준으로, 델타 로봇의 forward kinematics를 수치해석 방식으로 최소 구현한다. 구현 목적은 제어 투입용 최적화보다 먼저 `IK→FK` 왕복 검증이 가능한 기준 코드를 확보하는 것이다.

## Files
- `kinematics/forward_kinematics.py`
- `kinematics/validate_roundtrip.py`
- `kinematics/README.md`
- `docs/daily_notes/2026-05-03.md`

## Changes
- `kinematics/forward_kinematics.py`에 `theta1`, `theta2`, `theta3` 입력으로 `(x, y, z)`를 구하는 수치해석 기반 FK 함수를 추가한다.
- FK는 현재 문서 기준 `J_i(theta_i)` elbow point와 `|P_i - J_i|^2 = l^2` 제약식을 사용해 구성한다.
- 구현은 외부 패키지 의존성 없이 Python 표준 라이브러리 기반으로 진행하고, 최소 3변수 비선형 연립방정식을 반복적으로 푸는 방식으로 잡는다.
- 실패 시 수렴 실패/비유효 해를 명확히 구분할 수 있는 예외 또는 `reject` 성격의 실패 처리를 둔다.
- `kinematics/validate_roundtrip.py`에 sample point 기준 `IK -> FK` 왕복 검증 스크립트를 추가한다.
- `kinematics/README.md`에 FK 모듈과 검증 스크립트 역할을 반영한다.
- 작업 후 `docs/daily_notes/2026-05-03.md`에 변경 이유, 방법, 결과, 다음 작업을 기록한다.

## Impact
- `kinematics/`에 IK만 있던 상태에서 FK와 왕복 검증 경로가 추가된다.
- 이후 workspace sweep, fake pipeline, simulation consistency check의 기준이 생긴다.
- 데이터 계약이나 공개 CSV 구조는 변경하지 않는다.

## Risk
- 수치해석 FK는 초기값에 민감할 수 있고, 잘못된 branch 또는 비물리적 해로 수렴할 수 있다.
- 현재 nominal parameter와 실제 하드웨어 치수 차이가 크면 FK 검증 결과 해석에 혼선이 생길 수 있다.
- 부호 정의와 `theta_i` convention이 코드 사이에서 조금만 어긋나도 IK↔FK 왕복 오차가 커질 수 있다.
- 표준 라이브러리만 사용할 경우 선형계 풀이와 수렴 안정화 로직을 직접 다뤄야 한다.

## Validation
- Python 구문 검증을 수행한다.
- sample point 몇 개에 대해 `position -> IK -> FK` 왕복 검증을 수행하고 복원 오차를 확인한다.
- 대칭 위치와 중심축 위치를 포함한 기본 샘플에서 수렴 여부를 확인한다.
- 실패 케이스에 대해 수렴 실패가 조용히 통과되지 않고 명시적으로 보고되는지 확인한다.
