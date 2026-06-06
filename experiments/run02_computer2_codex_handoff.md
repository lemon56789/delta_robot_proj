# Computer 2 Codex Run 02 인수인계

이 문서는 Git 저장소를 사용하지 않는 Computer 2에서 Codex가 Run 02 실행 환경을
직접 구성하고, Simscape 준비와 실제 24회 실험을 수행하기 위한 독립형 지시서다.

## 1. 목표와 금지 사항

- 실험 구성: 궤적 4종 × 반복 3회 × 보정 OFF/ON 2종 = 총 24회
- 각 쌍은 반드시 같은 궤적과 반복 번호로 `OFF → ON` 순서로 수행한다.
- 전달받은 Python 파일과 학습 모델을 임의로 수정하거나 다시 학습하지 않는다.
- CSV 컬럼, 파일명 규칙, gain, clamp, Z, 궤적 및 시간 파라미터를 변경하지 않는다.
- 명목 Simscape CSV가 없거나 시간축이 맞지 않으면 ON 실험을 강행하지 않는다.
- 누락된 데이터나 파일을 임의로 생성하거나 placeholder로 대체하지 않는다.
- Computer 2에서는 Git 명령을 사용할 필요가 없다.

문제가 생기면 다음 형식으로 작업자에게 보고하고 해당 실행을 중단한다.

```text
[BLOCKER]
문제:
필요:
대안:
```

## 2. 전달받아야 할 파일

아래 상대 경로를 유지해서 전달받는다.

```text
experiments/
  run02_logger.py
  test_run02_logger.py
  run02_logger_computer2_powershell.md
  run02_computer2_codex_handoff.md
kinematics/
  geometry.py
  inverse_kinematics.py
virtual_sensor/
  correction_engine.py
  ridge_model.py
  models/
    ridge_run01_main_2026-06-06.npz
```

PowerShell에서 핵심 파일 무결성을 확인한다.

```powershell
Get-FileHash .\experiments\run02_logger.py -Algorithm SHA256
Get-FileHash .\kinematics\geometry.py -Algorithm SHA256
Get-FileHash .\kinematics\inverse_kinematics.py -Algorithm SHA256
Get-FileHash .\virtual_sensor\correction_engine.py -Algorithm SHA256
Get-FileHash .\virtual_sensor\ridge_model.py -Algorithm SHA256
Get-FileHash .\virtual_sensor\models\ridge_run01_main_2026-06-06.npz -Algorithm SHA256
```

예상 SHA-256:

```text
c20ecb0ae73d94bed848efad5e5de7bcc74e52f3842eeef7c3fa153edc7c496e  experiments/run02_logger.py
98a4ca272a7127ecc17b23082f5581da3d93b0ce05c00a4730a7b28d2ea5b97f  kinematics/geometry.py
3e62e5b0a6d6773c1533eaa0c671644cf5343da86fc93af0bc0a94449f4ea0ae  kinematics/inverse_kinematics.py
6bb8ff4e6d274ec2a1b44c239b1ccba0df1a90eeb5c89a0962bd7ac98423ceb9  virtual_sensor/correction_engine.py
a1db230fc518c24a201a587a1bb7a485546dd1546426ae837c9a996b0ef5866d  virtual_sensor/ridge_model.py
538695943a5096d4f2890104fc04af5978c3635fb8196baaac346e9cb1cf26d6  virtual_sensor/models/ridge_run01_main_2026-06-06.npz
```

해시가 다르면 전송 중 변경 여부를 확인하기 전까지 실험을 시작하지 않는다.

## 3. 작업 폴더 생성

기준 폴더는 `C:\delta_robot_run02`다. 다른 위치를 사용하면 모든 명령을 그 위치에
맞게 일관되게 바꾼다.

```powershell
New-Item -ItemType Directory -Force C:\delta_robot_run02 | Out-Null
Set-Location C:\delta_robot_run02

$dirs = @(
  ".\experiments",
  ".\kinematics",
  ".\virtual_sensor\models",
  ".\data\real\raw",
  ".\data\simulation\raw",
  ".\schedule_exports"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force $_ | Out-Null }
```

전달받은 파일을 2절의 상대 경로에 배치한다. `run02_logger.py`만 복사하면
kinematics와 virtual sensor import가 실패하므로 필수 파일 전체를 배치한다.

## 4. Python 및 코드 검증

Python 3.12 계열을 우선 사용한다.

```powershell
py --version
py -m pip install numpy pyserial
py -m py_compile `
  .\experiments\run02_logger.py `
  .\kinematics\geometry.py `
  .\kinematics\inverse_kinematics.py `
  .\virtual_sensor\correction_engine.py `
  .\virtual_sensor\ridge_model.py
py -m unittest experiments.test_run02_logger
```

테스트가 실패하면 코드를 현장에서 수정하지 말고 오류 전문을 원래 컴퓨터에 전달한다.

Arduino IDE의 Serial Monitor와 다른 시리얼 프로그램은 닫아 COM 포트 독점을 해제한다.

```powershell
[System.IO.Ports.SerialPort]::GetPortNames()
```

## 5. 고정 실험 조건

다음 값은 변경하지 않는다.

```text
Z = -263.27731514697575 mm
waypoint/home hold = 5.0 s
circle start/end hold = 2.0 s
circle = radius 40 mm, 72 points, 30.0 s, CCW
data schedule interval = 0.1 s
serial command interval = phase transition 또는 최대 0.5 s
correction gain = 0.25
correction clamp = 2.0 mm
Z correction = OFF
baud rate = 9600
```

궤적 이름과 예상 행 수:

```text
cross_pm30             450 rows
reverse_grid_3x3_pm40  550 rows
diamond_pm35           350 rows
circle_r40             500 rows
```

## 6. 24회 매니페스트 생성

`YYYY-MM-DD`는 실제 실험 날짜로 바꾼다. vision, main, metadata의 run ID 날짜를
모두 동일하게 사용한다.

```powershell
py .\experiments\run02_logger.py manifest `
  --date YYYY-MM-DD `
  --output .\experiments\run02_24_run_manifest.json
```

출력에서 `run_count=24`를 확인한다. 실행 순서는 다음과 같다.

```text
01 cross_pm30 off r01
02 cross_pm30 on  r01
03 cross_pm30 off r02
04 cross_pm30 on  r02
05 cross_pm30 off r03
06 cross_pm30 on  r03
07 reverse_grid_3x3_pm40 off r01
08 reverse_grid_3x3_pm40 on  r01
09 reverse_grid_3x3_pm40 off r02
10 reverse_grid_3x3_pm40 on  r02
11 reverse_grid_3x3_pm40 off r03
12 reverse_grid_3x3_pm40 on  r03
13 diamond_pm35 off r01
14 diamond_pm35 on  r01
15 diamond_pm35 off r02
16 diamond_pm35 on  r02
17 diamond_pm35 off r03
18 diamond_pm35 on  r03
19 circle_r40 off r01
20 circle_r40 on  r01
21 circle_r40 off r02
22 circle_r40 on  r02
23 circle_r40 off r03
24 circle_r40 on  r03
```

## 7. Simscape용 OFF dry-run 스케줄 생성

실제 실험 파일과 혼동하지 않도록 dry-run 결과는 `schedule_exports`에 저장한다.
아래 명령은 실제 로봇이나 Arduino로 명령을 보내지 않는다.

```powershell
$date = "YYYY-MM-DD"
$trajectories = @(
  "cross_pm30",
  "reverse_grid_3x3_pm40",
  "diamond_pm35",
  "circle_r40"
)

foreach ($trajectory in $trajectories) {
  $runId = "${date}_run02_${trajectory}_off_r01"
  py .\experiments\run02_logger.py run $trajectory `
    --correction off `
    --run-id $runId `
    --dry-run `
    --output-csv ".\schedule_exports\main_schedule_${trajectory}.csv" `
    --metadata-json ".\schedule_exports\metadata_schedule_${trajectory}.json" `
    --serial-log ".\schedule_exports\serial_schedule_${trajectory}.txt" `
    --correction-csv ".\schedule_exports\correction_schedule_${trajectory}.csv"
  if ($LASTEXITCODE -ne 0) { throw "dry-run failed: $trajectory" }
}
```

각 `main_schedule_*.csv`의 `time`, target 좌표 및 nominal motor angle을 Simscape 입력에
사용한다. 이전 Run 01처럼 임의 보간하거나 시간을 다시 생성하지 않는다.

Simscape는 다음 네 파일을 생성해야 한다.

```text
data/simulation/raw/simscape_run02_nominal_cross_pm30.csv
data/simulation/raw/simscape_run02_nominal_reverse_grid_3x3_pm40.csv
data/simulation/raw/simscape_run02_nominal_diamond_pm35.csv
data/simulation/raw/simscape_run02_nominal_circle_r40.csv
```

각 Simscape CSV 필수 컬럼:

```text
time,sim_x,sim_y,sim_z
```

`time`은 대응하는 dry-run CSV와 행 수 및 각 시각이 정확히 같아야 한다. ON 실행기는
이 조건을 검사하며 불일치 시 중단한다. 실험 전에 네 ON dry-run을 실행해서 시간축과
보정 로딩을 검증한다.

```powershell
$date = "YYYY-MM-DD"
$trajectories = @(
  "cross_pm30",
  "reverse_grid_3x3_pm40",
  "diamond_pm35",
  "circle_r40"
)

foreach ($trajectory in $trajectories) {
  $runId = "${date}_run02_${trajectory}_on_r01"
  py .\experiments\run02_logger.py run $trajectory `
    --correction on `
    --run-id $runId `
    --simscape-csv ".\data\simulation\raw\simscape_run02_nominal_${trajectory}.csv" `
    --dry-run `
    --output-csv ".\schedule_exports\main_on_check_${trajectory}.csv" `
    --metadata-json ".\schedule_exports\metadata_on_check_${trajectory}.json" `
    --serial-log ".\schedule_exports\serial_on_check_${trajectory}.txt" `
    --correction-csv ".\schedule_exports\correction_on_check_${trajectory}.csv"
  if ($LASTEXITCODE -ne 0) { throw "ON validation failed: $trajectory" }
}
```

## 8. 실제 OFF/ON 실행

각 실행 전에 vision 기록을 먼저 시작한다. vision과 main에 같은 run ID를 사용한다.
`COM3`은 실제 Arduino 포트로 바꾼다.

OFF 예시:

```powershell
py .\experiments\run02_logger.py run cross_pm30 `
  --correction off `
  --run-id YYYY-MM-DD_run02_cross_pm30_off_r01 `
  --port COM3
```

ON 예시:

```powershell
py .\experiments\run02_logger.py run cross_pm30 `
  --correction on `
  --run-id YYYY-MM-DD_run02_cross_pm30_on_r01 `
  --simscape-csv .\data\simulation\raw\simscape_run02_nominal_cross_pm30.csv `
  --port COM3
```

나머지는 매니페스트의 run ID, trajectory, correction을 그대로 대입한다. OFF/ON 한 쌍
사이에 카메라, 로봇 원점, 조명, Simscape 파일 및 실험 파라미터를 바꾸지 않는다.

## 9. 매 실행 후 확인 및 중단 기준

- 프로세스 종료 코드가 0인지 확인한다.
- `data\real\raw` 아래 main CSV, metadata JSON, serial TXT, correction CSV가 생성됐는지 확인한다.
- main CSV 행 수가 5절의 예상값과 같은지 확인한다.
- vision CSV가 같은 run ID로 정상 종료됐는지 확인한다.
- ON에서 fallback, clamp, correction norm과 schedule lag를 기록한다.
- 실패한 run ID의 파일을 성공 데이터로 사용하지 않는다.

다음 중 하나면 즉시 중지하고 해당 run을 rejection 처리한다.

- fallback 연속 3회 또는 총 5회
- schedule lag `>500 ms`
- correction norm `>2 mm`
- marker 연속 소실 `>1 s`
- servo stall, 비정상 소음/진동, link interference 또는 충돌 위험
- Arduino 포트 연결 또는 명령 전송 실패
- 역기구학 실패
- ON의 Simscape CSV, 필수 컬럼 또는 모델 파일 누락
- 명령 스케줄과 Simscape 시간축 불일치

## 10. 실험 종료 후 회수 파일

다음 항목을 폴더 구조를 유지한 채 원래 컴퓨터로 전달한다.

```text
experiments/run02_24_run_manifest.json
data/real/raw/main_*.csv
data/real/raw/metadata_*.json
data/real/raw/serial_*.txt
data/real/raw/correction_*.csv
data/simulation/raw/simscape_run02_nominal_*.csv
schedule_exports/*
vision 측에서 생성한 동일 run ID의 raw CSV 전체
실행 중 작성한 오류 및 실험 메모
```

원본 파일은 전달 완료와 백업 확인 전까지 삭제하거나 덮어쓰지 않는다.

## 11. 추가 명령 참고

개별 명령의 상세 옵션과 고정값은
`experiments/run02_logger_computer2_powershell.md`를 함께 참고한다. 두 문서가 충돌하면
이 문서의 안전 조건을 우선 적용하고, 파라미터 차이는 원래 컴퓨터에 확인한다.
