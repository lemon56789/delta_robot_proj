# Hardware Experiment Run 00 - Commissioning

이 문서는 조립 후 하드웨어 커미셔닝과 안전 검증을 위한 run protocol이다. 고정 장비 설정은 `docs/hardware_experiment_base_config.md`를 따른다.

Run 00은 위치 정확도 평가가 아니라 방향성, 조립 안정성, 로그/비전 준비 상태를 확인하는 커미셔닝 실험이다.

## 1. Experiment Scope
- experiment purpose:
  - 조립 완료 상태에서 motor 방향, zeroing, link 간섭, platform 구속 상태, 기본 logging, vision 좌표 방향을 확인한다.
  - Run 01 baseline 데이터 수집으로 넘어가기 전 gate 역할을 한다.
- not in scope:
  - 위치 정확도 평가.
  - 반복 정밀도 평가.
  - 보정 전후 성능 비교.
  - 큰 workspace trajectory 실행.
- expected output:
  - Run 00 checklist 결과.
  - 안전하게 확인한 최대 joint angle 범위.
  - A/B/C 단계별 pass/fail와 issue list.
  - main log와 vision log 사용 가능 여부.
  - main log: `data/real/raw/main_<run_id>.csv`
  - vision log: `data/vision/raw/vision_<run_id>.csv`
- target stage: Stage 7 실제 데이터 수집 전 hardware commissioning.
- responsible members:
  - operator: TBD
  - Arduino/firmware: Y
  - power cutoff operator: Y
  - hardware/safety observer: TBD
  - vision/logger: TBD
- date: TBD
- run_id: `YYYY-MM-DD_run00_commissioning_001`

## 2. Commissioning Checks

### A. Assembled Joint Small-Angle Check
- lower arm과 moving platform까지 결합한 상태에서 수행한다.
- 각 motor에 대해 `0 -> +3 -> 0 -> -3 -> 0 deg`를 먼저 수행한다.
- platform이 약간 기울어지는 것은 정상으로 본다.
- 목적은 position accuracy 평가가 아니라 다음 항목 확인이다.
  - motor direction.
  - lower arm / parallelogram 연결 방향.
  - platform 구속 상태.
  - link interference.
  - servo stalling / abnormal vibration.
  - zero 복귀 여부.
- `±3 deg`가 통과하면 같은 절차를 `±5 deg`로 확장한다.
- `±5 deg`까지 통과해야 B 단계로 넘어간다.
- A 단계에서 `±10 deg` 이상은 수행하지 않는다. 더 큰 joint 범위 확인은 별도 승인 후 진행한다.

Command sequence:
```text
ALL 0 0 0

1 3
1 0
1 -3
1 0

2 3
2 0
2 -3
2 0

3 3
3 0
3 -3
3 0

1 5
1 0
1 -5
1 0

2 5
2 0
2 -5
2 0

3 5
3 0
3 -5
3 0
```

Success criteria:
- 각 motor의 +theta 명령이 SoT 기준 +theta 방향과 일치한다.
- `center_cmd_1=84 deg`, `center_cmd_2=86 deg`, `center_cmd_3=88 deg`가 `theta_i=0 deg` 기준으로 유지된다.
- `sign_i = +1`, `fine_offset_i = 0 deg` 가정이 깨지지 않는다.
- `0 deg` 복귀 시 platform과 arm이 비정상적으로 틀어지지 않는다.
- link interference, servo stalling, abnormal vibration, abnormal noise가 없다.

Fail / stop criteria:
- motor 방향이 SoT 기준과 반대다.
- lower arm 또는 parallelogram이 비정상 방향으로 구속된다.
- platform이 과도하게 비틀린다.
- link, frame, wiring, cable 접촉이 발생하거나 예상된다.
- servo stalling, 지속 진동, 비정상 소음이 발생한다.
- `0 deg` 복귀가 반복적으로 실패한다.

### B. Cartesian Direction / Parallel Motion Check
- IK 기반 target position command를 사용한다.
- 실제 좌표값의 정확도는 평가하지 않는다.
- 목적은 `target_x`, `target_y` 명령 방향과 실제 moving platform 이동 방향이 대략 일치하는지 확인하는 것이다.
- moving platform이 과도하게 기울지 않고 대략 평행 상태를 유지하며 이동하는지 육안으로 확인한다.
- 작은 이동량만 사용한다.

Preconditions:
- A 단계가 pass여야 한다.
- target 기반 command가 Arduino/controller에서 사용 가능한 상태여야 한다.
- `z0`는 현재 하드웨어에서 안전한 기준 높이로 정한다.
  - z reference: A 단계 통과 후 현재 안전 home pose의 기준 z로 기록한다.
  - status: A 단계 수행 후 작성.

Test displacement:
- initial: `±3 mm` in x/y direction.
- expand to `±5 mm` only if initial check passes.

Target sequence:
```text
home position
target: (0, 0, z0)

+x direction check
target: (+3, 0, z0)
target: (0, 0, z0)

-x direction check
target: (-3, 0, z0)
target: (0, 0, z0)

+y direction check
target: (0, +3, z0)
target: (0, 0, z0)

-y direction check
target: (0, -3, z0)
target: (0, 0, z0)
```

Expansion sequence:
```text
target: (+5, 0, z0)
target: (0, 0, z0)
target: (-5, 0, z0)
target: (0, 0, z0)
target: (0, +5, z0)
target: (0, 0, z0)
target: (0, -5, z0)
target: (0, 0, z0)
```

Success criteria:
- `+x` target에서 platform이 `base_frame` +x 방향으로 이동한다.
- `-x` target에서 platform이 `base_frame` -x 방향으로 이동한다.
- `+y` target에서 platform이 `base_frame` +y 방향으로 이동한다.
- `-y` target에서 platform이 `base_frame` -y 방향으로 이동한다.
- 이동 중 platform이 과도하게 기울거나 비틀리지 않는다.
- link interference, abnormal vibration, servo stalling이 없다.

Fail / stop criteria:
- target direction과 실제 platform 이동 방향이 반대다.
- 움직임 중 platform이 급격히 기울거나 비틀린다.
- 한 방향 이동 후 home position으로 돌아오지 못한다.
- link interference, servo stalling, abnormal vibration, abnormal noise가 발생한다.

### C. Vision Readiness Check
- B 단계와 같은 작은 x/y 방향 이동을 사용한다.
- 목적은 vision system의 위치 정확도 평가가 아니라 marker detection과 좌표 방향 확인이다.
- ArUco marker가 안정적으로 검출되는지 확인한다.
- `vision_x`, `vision_y`가 `base_frame` 기준 mm 단위로 기록되는지 확인한다.
- B에서 육안으로 확인한 +x/+y 이동과 vision log의 +x/+y 증가 방향이 일치하는지 확인한다.
- 실제 좌표 오차는 Run 00에서 평가하지 않는다.

Preconditions:
- B 단계가 pass여야 한다.
- camera, marker, homography/calibration file이 준비되어야 한다.
- vision logger가 main log와 같은 `run_id`를 기록해야 한다.
  - vision calibration/homography file status: pending. 다음 정보 수신 후 작성한다.

Vision checks:
- marker_detected: yes/no.
- valid=true row ratio: TBD.
- vision_x direction match:
  - `+x` movement -> `vision_x` increases: yes/no.
- vision_y direction match:
  - `+y` movement -> `vision_y` increases: yes/no.
- static coordinate noise:
  - TBD mm.
- same run_id as main log:
  - yes/no.

Success criteria:
- marker가 정지 상태와 작은 x/y 이동 중 안정적으로 검출된다.
- `vision_x/y`가 mm 단위로 기록된다.
- `+x` 이동에서 `vision_x` 증가 방향이 맞다.
- `+y` 이동에서 `vision_y` 증가 방향이 맞다.
- 정지 상태 좌표 흔들림이 기록 가능하다.
- vision log와 main log의 `run_id`가 같다.

Fail / stop criteria:
- marker가 `1 s` 이상 연속 미검출된다.
- `vision_x/y` 좌표 방향이 SoT 좌표계와 반대다.
- vision log에 timestamp 또는 `run_id`가 없다.
- C가 실패해도 하드웨어 조립 자체가 실패한 것은 아니지만, Run 01 vision 기반 baseline 데이터 수집으로는 넘어가지 않는다.

## 3. Stage Gate
- A가 통과하지 않으면 B로 진행하지 않는다.
- B가 통과하지 않으면 C로 진행하지 않는다.
- C가 실패해도 하드웨어 조립 자체가 실패한 것은 아니지만, Run 01 vision 기반 baseline 데이터 수집으로는 넘어가지 않는다.
- Run 00에서 위치 정확도, tracking error, baseline error label은 평가하지 않는다.

## 4. Test Trajectory
- trajectory name: `run00_commissioning_small_motion`
- A target or theta range:
  - joint command only.
  - `±3 deg`, then `±5 deg`.
- B/C target range:
  - `x`: initial `±3 mm`, expansion `±5 mm`.
  - `y`: initial `±3 mm`, expansion `±5 mm`.
  - `z`: `z0`, current safe home z, TBD.
- duration [s]: TBD
  - 각 command 후 충분히 정지 상태를 관찰할 수 있도록 천천히 진행한다.
- command rate [Hz]: TBD
- max velocity:
  - controller가 허용하는 최저속 설정으로 시작한다.
- max acceleration:
  - controller가 허용하는 최저가속 설정으로 시작한다.

## 5. Run Procedure
1. Assign `run_id`.
   - 예: `YYYY-MM-DD_run00_commissioning_001`.
2. Confirm base config.
   - `wB=46 mm`, `H=285 mm`, `center_cmd_i=84/86/88 deg`.
   - `STOP` command 미구현, 물리 전원 차단 우선.
3. Assign roles.
   - Y는 power cutoff operator로 참석한다.
4. Clear workspace.
   - link, cable, frame 주변 간섭 가능성을 제거한다.
5. Power on sequence.
   - Arduino USB 5 V.
   - servo 2S Li-Po power.
   - pump power는 Run 00에서 필요할 때만 켠다.
6. Start Arduino/controller.
   - firmware path/status는 Y 확인 전까지 pending으로 둔다.
   - baud rate `9600 bps`를 확인한다.
7. Move to zero.
   - `ALL 0 0 0` 또는 `CENTER`.
   - `theta_i=0 deg` 자세와 `center_cmd_i` 기준을 확인한다.
8. Start main logger if available.
   - main log path: `data/real/raw/main_<run_id>.csv`.
   - vision log path if used: `data/vision/raw/vision_<run_id>.csv`.
   - file path와 `run_id`를 기록한다.
9. Execute A.
   - assembled joint small-angle check.
10. Execute B only if A passes.
    - Cartesian direction / parallel motion check.
11. Start vision logger and execute C only if B passes.
    - vision readiness check.
12. Stop loggers.
    - 파일 저장 여부를 확인한다.
13. Power down sequence.
    - servo Li-Po power를 먼저 차단한다.
    - pump power를 차단한다.
    - Arduino USB를 종료한다.
14. Save run metadata.
    - pass/fail, issue, operator note를 기록한다.

## 6. Stop Conditions
- use base stop conditions: yes.
- emergency stop / power cutoff:
  - 현재 software `STOP` command는 미구현이다.
  - 이상 동작 시 Y가 Li-Po servo power를 물리적으로 차단한다.
- stage-specific stop:
  - A/B/C 각 단계의 fail / stop criteria 중 하나라도 발생하면 즉시 중지한다.
- theta range exceeded:
  - A에서는 `±5 deg`를 초과하지 않는다.
  - absolute no-go는 `theta_i <= -65 deg` 또는 `theta_i >= +90 deg`다.
- target range exceeded:
  - B/C에서는 승인된 `±3 mm`, 확장 후 `±5 mm` x/y 이동을 초과하지 않는다.
- operator judgment:
  - 실험 참여자 중 누구든 위험하다고 판단하면 즉시 중지한다.

## 7. Post-Run Validation
- A result:
  - passed: yes.
  - basis: 사용자 보고 기준.
  - maximum checked joint range: `±5 deg`.
  - motor direction verified: yes.
  - zero return verified: yes.
  - interference/vibration/stalling: no issue reported.
- B result:
  - passed: yes.
  - basis: 사용자 보고 기준.
  - tested displacement: `±5 mm`.
  - x direction match: yes.
  - y direction match: yes.
  - parallel motion acceptable by visual check: yes.
- C result:
  - passed: pending.
  - marker_detected: pending.
  - valid=true row ratio: TBD.
  - vision_x direction match: pending.
  - vision_y direction match: pending.
  - static coordinate noise: TBD mm.
  - same run_id as main log: pending.
- main log valid:
  - required command/state fields recorded: TBD.
  - timestamp present: TBD.
- Run 01 readiness:
  - ready for vision-based baseline data collection: no.
  - reason if no: C 단계 vision readiness check가 아직 완료되지 않았다.
- issues found:
  - A/B 단계에서 사용자 보고 기준 issue 없음.
  - C 단계는 pending.

## 8. Run Metadata
- run_id: TBD
- operator: TBD
- date/time: TBD
- hardware configuration version: `docs/hardware_experiment_base_config.md`, 2026-06-04 기준
- firmware version or commit:
  - status: pending Y confirmation.
  - note: repo 추가 여부와 실제 uploaded sketch 정보를 확인한 뒤 기록한다.
- z reference `z0`:
  - status: A 단계 수행 후 작성.
  - note: A 단계 통과 후 현재 안전 home pose의 기준 z를 기록한다.
- main log path: `data/real/raw/main_<run_id>.csv`
- vision log path: `data/vision/raw/vision_<run_id>.csv`
- vision calibration file:
  - status: pending.
  - note: camera calibration/homography file 정보 수신 후 작성한다.
- notes:
  - 2026-06-05: A/B gate는 사용자 보고 기준으로 pass 기록.
  - C gate는 homography 적용 vision logger와 방향 확인 후 별도 기록.
