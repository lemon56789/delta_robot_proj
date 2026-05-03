# Plan

## Goal
현재 nominal geometry, inverse kinematics, forward kinematics 구현을 기준으로, 작업공간 내 샘플 점들을 체계적으로 검사하는 `workspace sweep` 검증 스크립트를 추가한다. 목적은 reachable 영역, branch 선택, FK 수렴성, IK→FK 왕복 오차를 한 번에 점검할 수 있는 기준 검증 도구를 확보하는 것이다.

## Files
- `kinematics/workspace_sweep.py`
- `kinematics/README.md`
- `docs/daily_notes/2026-05-04.md`

## Changes
- `kinematics/workspace_sweep.py`에 지정된 `(x, y, z)` 범위와 step으로 샘플 점을 순회하는 sweep 스크립트를 추가한다.
- 각 점에 대해 `IK` 성공 여부, `FK` 수렴 여부, `IK -> FK` 왕복 위치 오차, 각도 결과를 기록한다.
- 실패 케이스는 최소한 `ik_reject`, `fk_fail`, `roundtrip_error_exceeded` 같은 사유로 분류한다.
- 첫 구현은 Python 표준 라이브러리 기반으로 진행하고, 결과는 터미널 요약과 필요 시 CSV 저장이 가능하도록 구성한다.
- sweep 대상은 우선 안전한 범위의 coarse grid로 시작하고, 이후 finer sweep으로 확장 가능하게 한다.
- `kinematics/README.md`에 workspace sweep 검증 스크립트 역할을 반영한다.
- 작업 후 `docs/daily_notes/2026-05-04.md`에 변경 이유, 방법, 결과, 다음 작업을 기록한다.

## Impact
- `kinematics/`에 공간 전역 검증 도구가 추가된다.
- 이후 fake pipeline, trajectory test, simulation 연동 전에 사용할 안전한 검증 범위를 정할 수 있게 된다.
- reachable workspace와 실패 분포를 코드 기준으로 확인할 수 있게 된다.
- 데이터 계약이나 공개 CSV 구조는 변경하지 않는다.

## Risk
- sweep 범위가 너무 넓거나 step이 너무 촘촘하면 실행 시간이 불필요하게 커질 수 있다.
- 현재 nominal parameter와 실제 하드웨어 치수 차이가 크면 FK 검증 결과 해석에 혼선이 생길 수 있다.
- 부호 정의와 `theta_i` convention이 코드 사이에서 조금만 어긋나도 IK↔FK 왕복 오차가 커질 수 있다.
- coarse grid만으로는 경계 특이점이나 좁은 실패 구간을 놓칠 수 있다.

## Validation
- Python 구문 검증을 수행한다.
- 제한된 범위의 coarse sweep를 실제 실행해 valid/invalid 분류가 동작하는지 확인한다.
- 중심축, 대칭 위치, 경계 근처 점이 포함되도록 샘플 범위를 잡고 결과를 검토한다.
- 실패 케이스가 조용히 누락되지 않고 사유와 함께 요약되는지 확인한다.
