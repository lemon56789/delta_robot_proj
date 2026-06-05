# Delta Robot Virtual Sensing - Full Context

문서 목적: 외부 AI 모델이 이 리포지토리를 빠르게 이해하고, 분석/코드 지원을 수행할 수 있도록 프로젝트 전반을 한 파일로 요약한다.
갱신일: 2026-06-04

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
- `docs/`: 프로젝트 문서, 시스템 설계, 운동학 메모, 비전 측정계 문서, measured data 구조 문서, 로드맵
- `docs/plans/`: 작업 전 승인용 계획서
- `docs/daily_notes/`: 날짜별 변경 기록
- `docs/templates/`: 계획서와 Daily Note 템플릿
- `docs/references/`: 참고 논문 및 외부 자료 보관 경로. SoT나 채택안을 의미하지 않는다.
- `docs/workspace_envelope.md`: 설치 높이와 `XY` 작업공간 관계를 정리한 설계 참고 문서
- `docs/measured_data_structure.md`: real main log, vision raw log, angle-derived measured position, processed merged dataset 구조
- `docs/hardware_experiment_index.md`: 하드웨어 실험 문서 인덱스
- `docs/hardware_experiment_base_config.md`: 하드웨어/제어/전원/비전/로그 공통 설정
- `docs/hardware_experiment_run_*.md`: 커미셔닝, baseline 수집, 보정 비교, 최종 시연용 run protocol
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
- `wB`: base 중심에서 motor/upper-arm joint 기준점까지의 거리
- `wP`: platform 중심에서 변까지의 거리
- `L`: motor-driven upper arm length
- `l`: parallelogram link length
- `B1`, `B2`, `B3`: 각 motor/base side center
- `P1`, `P2`, `P3`: 각 platform 연결점

현재 nominal geometry parameter:
- `L = 125.0 mm`
- `l = 300.0 mm`
- `wB = 46.0 mm`
- `uP = 27.177 mm`

현재 하드웨어 참고 치수:
- `sB = 199 mm`: base 외곽 정삼각형 변 길이이며 IK/FK 기준값이 아니다.
- `sP = 57.5 mm`: platform 외곽 정삼각형 변 길이이며 IK/FK 기준값이 아니다.
- `H = 285 mm`: base origin/base center O에서 ground plane까지의 설치 높이다.
- 기구학 계산에서는 외곽 치수보다 `wB`, `uP`를 우선한다.

## 5) 데이터 계약과 시간 정책
현재 기준 문서: `docs/system_data_flow.md`, `docs/measured_data_structure.md`

Timestamp:
- field name: `time`
- format: `boot_ms`
- resolution: `ms`
- Arduino와 PC logger가 각각 timestamp를 기록한다.
- 이후 `post-alignment`로 정렬한다.
- 누락 timestamp row는 `invalid`로 표기하고 후처리에서 제외한다.

현재 final processed CSV 고정 컬럼 순서:
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
- 위 16개 컬럼은 raw log가 아니라 학습/평가용 processed merged dataset의 fixed column order다.
- real main log, vision raw log, angle-derived measured position은 별도 raw/auxiliary 계층으로 관리한다.
- contract-compliant `error_*`는 measured data, simulation output, vision data가 post-alignment된 processed merged dataset 단계에서만 생성한다.

Measured data 계층:
- Real main log: `run_id`, `time`, `target_*`, `theta*_cmd`, `theta*_meas`, `valid`를 기록한다.
- Vision raw log: `run_id`, `vision_time`, `vision_x`, `vision_y`, `marker_detected`, `frame_id`, `valid`를 기록한다.
- Angle-derived measured position: `theta*_meas` 기반 FK 또는 estimator로 `measured_x_est`, `measured_y_est`, `measured_z_est`를 생성한다.
- Processed merged dataset: real main log, Simscape output, vision raw log, angle-derived measured position을 정렬해 16개 final CSV 컬럼을 만든다.

`error_*` 생성 기준:
- `error_x = measured_x_vision - sim_x`
- `error_y = measured_y_vision - sim_y`
- `error_z = measured_z_est - sim_z`
- `error_x/y`는 vision 기반 XY ground-truth에서 생성한다.
- `error_z`는 angle-derived estimate 기반이므로 외부 ground-truth 기반 3D 성능 수치로 해석하지 않는다.

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
- 현재 fake pipeline 기준 `Simscape` 비교에서는 provisional `1 sample = 20 ms` lag 보정을 사용한다.
- `invalid` row는 alignment와 비교에서 제외한다.

Correction:
- correction target: `target_position`
- correction fields: `error_x`, `error_y`, `error_z`
- correction unavailable fallback: uncorrected target position 사용
- SoT 의미는 `measured_position - sim_position`이며, 현재 `Simscape` CSV의 `target_position - sim_position` 값은 임시 diagnostic으로만 해석한다.
- `error_*`는 raw Simscape export에서 확정하지 않고, measured data 구조가 정렬된 processed merged dataset 단계에서 생성한다.
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
- 최소 필드: `run_id`, `vision_time`, `vision_x`, `vision_y`, `marker_detected`, `frame_id`, `valid`
- 선택 필드: `marker_id`, `reprojection_error`, `confidence`, `video_file`

Run 00에서 vision system은 marker 검출뿐 아니라 좌표계 방향 확인에도 사용한다.
- 정지 상태에서 `vision_x/y`가 `base_frame` 기준 mm 좌표로 안정적으로 기록되는지 확인한다.
- 작은 +x/+y 수동 이동을 만들었을 때 vision 좌표 증가 방향이 SoT 좌표계와 일치해야 한다.
- 초기 motor direction/zeroing 확인 단계에서 marker loss는 hard stop은 아니지만, vision 위치 확인 단계에서 `1 s` 이상 marker가 연속 미검출되거나 좌표 방향이 반대이면 해당 run은 invalid로 표시하고 trajectory test로 넘어가지 않는다.

WSL/Windows 비전 실행 방침:
- repo의 Source of Truth는 WSL의 `/home/lemon56789/delta_robot`에 둔다.
- Windows 환경은 C-pre camera I/O 실행에만 사용한다. repo 전체를 Windows로 복제하지 않는다.
- WSL에서 webcam이 `/dev/video*`로 노출되지 않을 수 있으므로, C-pre에서는 Windows Python에서 OpenCV를 실행하는 방식을 우선한다.
- Windows Python에서 `opencv-contrib-python`과 `numpy`를 설치한 뒤 camera open, ArUco ID detection, platform marker pixel CSV 저장을 확인한다.
- C-pre pixel log는 homography 전 사전 점검용이며, Run 00 C 최종 `vision_x/y` mm 로그와 구분한다.
- C-pre pixel CSV 권장 컬럼:
  - `run_id`
  - `vision_time`
  - `frame_id`
  - `marker_id`
  - `marker_px`
  - `marker_py`
  - `marker_detected`
  - `valid`
- C-pre pixel CSV 권장 파일명: `data/vision/raw/vision_pixel_<run_id>.csv`
- Windows에서 WSL repo에 바로 저장할 경우 예시 경로:
  - `\\wsl$\<distro>\home\lemon56789\delta_robot\data\vision\raw`
  - `<distro>` 이름은 PowerShell의 `wsl -l -v`로 확인한다.
- `\\wsl$` 경로 저장이 느리거나 권한 문제가 있으면 Windows 임시 경로에 저장한 뒤 WSL repo로 복사한다.

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
- 현재 hardware-safe provisional range는 `-45 deg <= theta_i <= 90 deg`
- downward-working branch에 속하는 해만 유효 후보로 둔다.
- 후보가 둘이면 `previous_theta_i`와 가장 가까운 해를 선택한다.
- 후보가 없으면 reject한다.

남은 IK/하드웨어 연결 관련 미정 항목:
- 실제 하드웨어 반복 구동 후 hardware-confirmed `theta_min`, `theta_max` 확정
- Run 00에서 arm별 `center_cmd_i`, `sign_i`, `fine_offset_i` 재확인
- FK 기반 역검증 절차

현재 코드 상태:
- `kinematics/geometry.py`에 `DeltaGeometry` dataclass와 `NOMINAL_DELTA_GEOMETRY`가 정의되어 있다.
- `kinematics/inverse_kinematics.py`에 `delta_ik(x_mm, y_mm, z_mm)`가 구현되어 있다.
- 구현은 각 arm별 일반화된 `E_i`, `F_i`, `G_i` 식, 판별식 기반 reject, 임시 각도 범위, `previous_theta_deg` 기반 해 선택을 사용한다.
- 현재 구현은 `theta_i = 2 atan(t_i)`와 `J_i/FK z = -L sin(theta_i)` 정의를 문서 SoT와 같은 부호 체계로 사용한다.
- 간단한 sample point에 대해 실제 각도 계산이 수행되는 최소 실행 검증은 완료되었다.
- 현재 nominal-analysis candidate range와 hardware-safe provisional range는 모두 `-45 deg <= theta_i <= 90 deg`로 관리하고, hardware-confirmed range는 별도 미확정 상태로 둔다.

## 9) 하드웨어 실험 준비 상태
현재 기준 문서: `docs/hardware_experiment_base_config.md`, `docs/hardware_experiment_run_00_commissioning.md`

Run 00의 성격:
- 데이터 수집 실험이 아니라 실제 장비 커미셔닝 실험이다.
- 목적은 전원, Arduino 명령, motor 방향, zeroing 기준, 안전 중지 조건, 기본 로그, vision 위치 확인이 SoT 기준과 일치하는지 검증하는 것이다.
- Run 00을 통과해야 Run 01 baseline 데이터 수집으로 넘어갈 수 있다.

전원과 안전:
- servo 전원은 2S Li-Po battery 기준 공칭 `7.4 V`, 완충 `8.4 V`이며 servo 입력은 `8.4 V`를 초과하지 않는다.
- pump 전원은 `12 V DC supply`, Arduino logic 전원은 PC USB `5 V`다.
- 현재 dedicated fuse와 software `STOP` command는 미구현이다.
- Run 00에서는 Y가 power cutoff operator로 참석하고, 이상 동작 시 Li-Po servo power를 물리적으로 차단하는 방식을 우선한다.
- absolute no-go pose는 `theta_i <= -65 deg` 또는 `theta_i >= +90 deg`다.

Arduino command mapping:
- 입력 command는 raw servo angle이 아니라 SoT 기준 `theta_cmd` [deg]다.
- 기본 변환식은 `servo_angle_i = center_cmd_i + sign_i * theta_cmd_i + fine_offset_i`다.
- 현재 기록값:
  - `center_cmd_1 = 84 deg`
  - `center_cmd_2 = 86 deg`
  - `center_cmd_3 = 88 deg`
  - `sign_i = +1`
  - `fine_offset_i = 0 deg`
- `center_cmd_i`는 SoT 기준 `theta_i = 0 deg`가 실제 servo command angle 몇 도에 해당하는지 나타내는 값이다.
- 현재 확인 기준에서는 `+90 deg` command가 실제 `+90 deg`만큼 이동하므로 추가 fine offset은 없는 것으로 둔다.
- firmware 예정 경로는 `control/motor_test.ino`, `control/pick_place_state_machine.ino`지만 아직 repo에는 추가되지 않았다.

Run 00 기본 확인 순서:
- 모든 arm을 `theta_i = 0 deg`에서 시작한다.
- A 단계에서는 조립 상태에서 각 motor에 대해 단일축 `0 -> +3 -> 0 -> -3 -> 0 deg`를 먼저 확인하고, 통과하면 `+/-5 deg`로 확장한다.
- B 단계에서는 IK 기반 target command로 `x/y` 방향 `+/-3 mm` 이동을 확인하고, 통과하면 `+/-5 mm`로 확장한다. 실제 좌표 정확도는 평가하지 않는다.
- C 단계에서는 B와 같은 작은 x/y 이동을 vision logger로 읽어 marker 검출, `vision_x/y` 좌표 방향, static noise, 같은 `run_id` 여부를 확인한다.
- A가 실패하면 B로 가지 않고, B가 실패하면 C로 가지 않는다.

## 10) 프로젝트 로드맵
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
- Stage 2 운동학 정의 및 구현: nominal geometry, IK, workspace/angle range 진단까지 1차 완료
- Stage 3 FK 검증 및 기본 해석: FK 최소 구현 및 round-trip/workspace 검증 진행 중
- Stage 4 시뮬레이션 및 데이터 경로 정리: 부분 완료
- Stage 5 외부 ground-truth 측정계 구축: 문서화 완료, 구현 미착수
- Stage 6 fake pipeline 구성: 진행 중
- Stage 7 실제 데이터 수집: Run 00 커미셔닝 준비 중
- Stage 8 가상센서 학습 및 보정: 미착수
- Stage 9 폐루프 적용 및 성능 검증: 미착수
- Stage 10 외부 측정계 제거 후 운영 검증: 미착수

현재 구현 기준 핵심 상태:
- `kinematics/geometry.py`, `kinematics/inverse_kinematics.py`에 nominal geometry와 IK가 반영되어 있다.
- `kinematics/forward_kinematics.py`, `kinematics/validate_roundtrip.py`, `kinematics/workspace_sweep.py`로 FK, 왕복 검증, workspace sweep이 가능하다.
- `2026-05-25` 기준 `IK/FK`의 `theta` 및 `z` 부호 정의가 문서 SoT와 정렬되었고, representative `IK -> FK` roundtrip 검증이 다시 통과했다.
- 현재 angle range는 `hardware-safe provisional: -45..90 deg`, `nominal-analysis candidate: -45..90 deg`로 관리하고, `hardware-confirmed`는 별도 확정 전 상태로 둔다.
- `docs/workspace_envelope.md`에 설치 높이와 `XY` reachable area 참고 결과가 정리되어 있으며, 현재 기준 추천 설치 높이는 일반적인 pick-and-place 기준 `H = 290 mm`, 대안은 `H = 310 mm`다.
- 실제 현재 hardware base-ground 설치 높이는 `H = 285 mm`로 base config에 기록되어 있고, 이 높이 기준의 Run 00 준비를 진행한다.
- `experiments/fake_pipeline.py`가 현재 CSV 계약을 따르는 fake dataset CSV/JSON을 생성한다.
- `virtual_sensor/dataset.py`, `virtual_sensor/check_dataset.py`로 fake pipeline CSV를 읽고 feature/target shape와 NaN 여부를 확인할 수 있다.
- `wB = 46.0 mm` 기준 Python fake pipeline CSV/JSON과 workspace sweep artifact가 다시 생성되었다.
- Simulink/Simscape에서 새 `sim_*` CSV를 받아 비교한 결과, header/row/time/input field는 일치했고 `sim_*`는 예상대로 약 `1 sample = 20 ms` lag를 보였다.
- 현재 Simscape CSV의 `error_*`는 `target_position - sim_position` diagnostic 값이므로 SoT correction field인 `measured_position - sim_position`으로 직접 사용하지 않는다.
- `docs/measured_data_structure.md`가 추가되어 real main log, vision raw log, angle-derived measured position, processed merged dataset의 네 계층이 정리되었다.
- 초기 `error_x/y`는 vision 기반 XY에서 생성하고, `error_z`는 `theta*_meas` 기반 `measured_z_est`에서 생성한다. `error_z`는 외부 ground-truth 기반 3D 성능 수치로 해석하지 않는다.
- `error_*`는 raw Simscape export가 아니라 processed merged dataset 단계에서 생성한다.
- 하드웨어 실험 문서는 고정 설정 `docs/hardware_experiment_base_config.md`와 실험별 run protocol `docs/hardware_experiment_run_*.md`로 분리되었다.
- base config에는 `wB=46 mm`, `H=285 mm`, 전원 구조, `STOP` 미구현/물리 차단 우선, `center_cmd_i=84/86/88 deg`, Run 00 단계적 theta test range, vision 위치 확인 기준이 반영되었다.
- Run 00 문서는 A/B/C gate 구조로 작성되었고, 실제 실험 전 `z0`, firmware path/status, logger 저장 경로, vision calibration file을 채워야 한다.

## 11) 개발 및 변경 원칙
AGENTS.md 기준 핵심 원칙:
- 변경 전 계획서 작성 및 사용자 승인 필수
- 승인 전 파일 변경 금지
- 어떤 파일이든 수정/추가/삭제하면 `docs/daily_notes/YYYY-MM-DD.md`에 기록
- placeholder/dummy 구현 금지
- 데이터 포맷, 함수 입력/출력, 폴더 구조, 시스템 데이터 흐름 임의 변경 금지
- Contract Change는 명시 승인 필요
- 모든 실험은 실행 커맨드, 사용 데이터, 파라미터, 코드 버전을 기록

## 12) 현재 기술 스택
- Python 3.12.3
- MATLAB / Simulink / Simscape
- Arduino
- PyTorch
- OpenCV
- GitHub

## 13) 바로 다음 작업
우선순위:
1. Run 00 실행 전 `z0`, firmware path/status, logger 저장 경로, vision calibration file을 채운다.
2. Run 00 A 단계에서 `center_cmd_i = 84/86/88 deg`, `sign_i = +1`, `fine_offset_i = 0 deg`가 arm별로 유지되는지 `±3 deg -> ±5 deg` 저속 확인한다.
3. Run 00 B 단계에서 IK 기반 `x/y` 방향 `±3 mm -> ±5 mm` 이동 방향과 platform 평행 이동 상태를 확인한다.
4. Run 00 C 단계에서 vision marker, homography/calibration file, `vision_x/y` 좌표 방향, static noise, 같은 `run_id` 여부를 확인한다.
5. Y와 함께 power cutoff, firmware 파일, serial command/log format, timeout 기준을 실제 구현 기준으로 확인한다.
6. real main log, vision raw log, Simscape output의 post-alignment 절차를 실제 실험 로그 기준으로 구체화한다.
7. processed merged dataset의 저장 경로, 파일명 규칙, `estimator_method` 기록 규칙을 정한다.
8. `virtual_sensor/` baseline model 학습/추론 뼈대는 processed dataset 규칙이 정리된 뒤 추가한다.

BLOCKER 가능성이 있는 항목:
- Run 00에서 `center_cmd_i`, `sign_i`, `fine_offset_i`가 문서 기준과 다르게 나오면 Arduino command mapping을 다시 정리해야 한다.
- 물리 전원 차단 담당과 절차가 확정되지 않으면 motor-powered test를 진행하면 안 된다.
- vision calibration 데이터가 없으면 비전 ground-truth는 문서 기준만 있고 실제 측정 정확도 검증은 할 수 없다.
- measured data 구조가 실제 logger 구현과 다르면 processed dataset 생성 규칙을 다시 조정해야 한다.

## 14) 유지보수 규칙
- 이 파일은 외부 AI 분석용 요약본이다.
- 구조, 규약, 데이터 계약, 로드맵 상태가 바뀌면 함께 갱신한다.
- 상세 근거는 `docs/system_data_flow.md`, `docs/measured_data_structure.md`, `docs/vision_tracking.md`, `docs/ik_structure_note.md`, `docs/workspace_envelope.md`, `docs/roadmap.md`, `AGENTS.md`를 우선 참조한다.
