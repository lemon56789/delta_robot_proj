# kinematics

델타 로봇 역기구학/순기구학 수식과 검증 스크립트를 관리하는 폴더입니다.

현재 nominal geometry parameter 기준:
- `L = 125.0 mm`
- `l = 300.0 mm`
- `wB = 24.051 mm`
- `uP = 27.177 mm`

현재 포함 모듈:
- `geometry.py`: 델타 로봇 기하 파라미터 dataclass와 nominal parameter 정의
- `inverse_kinematics.py`: `E/F/G + 2atan(t)` 구조 기반 inverse kinematics 구현
- `forward_kinematics.py`: 현재 IK algebraic constraint와 맞춘 수치해석 기반 forward kinematics 구현
- `validate_roundtrip.py`: sample point 기준 `IK -> FK` 왕복 검증 스크립트
- `workspace_sweep.py`: coarse grid 기준 reachable 영역, FK 수렴, round-trip 오차를 확인하고 IK reject cause까지 포함한 CSV + sidecar JSON 결과를 저장할 수 있는 workspace sweep 스크립트

비고:
- `workspace_sweep.py`는 `--theta-min`, `--theta-max` 인자를 받아 angle range가 workspace 경계에 미치는 영향을 비교할 수 있다.
