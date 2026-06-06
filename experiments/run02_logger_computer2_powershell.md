# Run 02 Logger - Computer 2 PowerShell Guide

## 1. Final Matrix

- trajectories:
  `cross_pm30`, `reverse_grid_3x3_pm40`, `diamond_pm35`, `circle_r40`
- correction: `off`, `on`
- repetitions: `r01`, `r02`, `r03`
- total: `4 x 2 x 3 = 24`
- pair order: 같은 repetition/trajectory의 OFF 직후 ON

## 2. Required Files

```text
C:\delta_robot_run02\
  experiments\run02_logger.py
  kinematics\
  virtual_sensor\
  data\simulation\raw\simscape_run02_nominal_<trajectory>.csv
```

ON 실행에는 아래 frozen model이 필요하다.

```text
virtual_sensor\models\ridge_run01_main_2026-06-06.npz
```

## 3. Generate Manifest

실제 실행 날짜로 변경한다.

```powershell
cd C:\delta_robot_run02
py .\experiments\run02_logger.py manifest `
  --date 2026-06-07 `
  --output .\experiments\run02_24_run_manifest.json
```

출력의 `run_count=24`를 확인한다.

## 4. Prepare Nominal Simscape Files

각 trajectory OFF dry-run으로 deterministic main schedule을 먼저 만든다.

```powershell
py .\experiments\run02_logger.py run cross_pm30 `
  --correction off `
  --run-id 2026-06-07_run02_cross_pm30_off_r01 `
  --dry-run
```

동일하게 reverse grid, diamond, circle schedule을 생성하고 Simscape에서
아래 네 파일을 export한다.

```text
data\simulation\raw\simscape_run02_nominal_cross_pm30.csv
data\simulation\raw\simscape_run02_nominal_reverse_grid_3x3_pm40.csv
data\simulation\raw\simscape_run02_nominal_diamond_pm35.csv
data\simulation\raw\simscape_run02_nominal_circle_r40.csv
```

필수 컬럼은 `time,sim_x,sim_y,sim_z`이며 dry-run main CSV와 `time` 값 및
row count가 정확히 같아야 한다.

## 5. Real OFF/ON Pair Example

Arduino IDE Serial Monitor를 닫고 vision logger를 먼저 시작한다.

```powershell
py .\experiments\run02_logger.py run cross_pm30 `
  --correction off `
  --run-id 2026-06-07_run02_cross_pm30_off_r01 `
  --port COM3
```

파일과 robot 상태를 확인한 뒤 바로 ON을 실행한다.

```powershell
py .\experiments\run02_logger.py run cross_pm30 `
  --correction on `
  --run-id 2026-06-07_run02_cross_pm30_on_r01 `
  --simscape-csv .\data\simulation\raw\simscape_run02_nominal_cross_pm30.csv `
  --port COM3
```

다른 trajectory는 positional trajectory와 run ID, Simscape 경로만
manifest에 맞춰 변경한다.

## 6. Frozen Defaults

- target Z: `-263.27731514697575 mm`
- waypoint/home hold: `5 s`
- circle start/end `(40,0)` hold: `2 s`
- circle: `72` points, `30 s`, counterclockwise
- data sample period: `0.1 s`
- command update: phase 전환 시 또는 `0.5 s`
- correction gain: `0.25`
- XY vector clamp: `2 mm`
- Z correction: disabled
- serial: `9600 baud`

실험 중 이 값을 변경하지 않는다. 변경이 필요하면 현재 24-run
comparison을 중단하고 별도 조건으로 다시 시작한다.

## 7. Stop Checks

- fallback 연속 3회 또는 총 5회
- schedule lag `>500 ms`
- correction norm `>2 mm`
- marker 연속 소실 `>1 s`
- servo stall, abnormal noise/vibration, link interference

위 조건이면 즉시 중지하고 해당 run을 rejection 처리한다.
