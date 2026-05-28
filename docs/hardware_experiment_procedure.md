# Hardware Experiment Procedure

이 문서는 실제 하드웨어 실험 절차를 확정하기 전에 필요한 장비 스펙, 제어기 설정, 로그 구조, 안전 조건을 수집하기 위한 템플릿이다. 빈칸은 하드웨어/제어/비전 담당자가 실제 장비 기준으로 채운다.

관련 기준 문서:
- `docs/system_data_flow.md`
- `docs/measured_data_structure.md`
- `docs/vision_tracking.md`
- `docs/workspace_envelope.md`

## 1. Experiment Scope
- experiment purpose:
- expected output:
- target stage:
- responsible members:
- date:
- run_id rule:

## 2. Hardware Configuration
### 2.1 Robot Geometry
- measured `L` [mm]:
- measured `l` [mm]:
- measured `wB` [mm]:
- measured `uP` [mm]:
- base/platform measured dimensions:
- installation height `H` [mm]:
- coordinate frame check method:

### 2.2 Motors
- motor model:
- motor type:
- rated voltage [V]:
- rated current [A]:
- max current [A]:
- max speed:
- max torque:
- encoder included:
- encoder resolution:
- gear ratio:
- known backlash:
- known deadband:

### 2.3 Motor Drivers
- driver model:
- supply voltage [V]:
- current limit setting:
- microstep setting:
- control mode:
- enable/disable pin behavior:
- fault output available:
- fault condition notes:

### 2.4 Power
- power supply model:
- voltage [V]:
- current limit [A]:
- fuse/current protection:
- emergency power cutoff method:
- grounding notes:

### 2.5 Mechanical Limits
- hardware-confirmed theta1 range [deg]:
- hardware-confirmed theta2 range [deg]:
- hardware-confirmed theta3 range [deg]:
- interference risk zones:
- safe initial pose:
- homing pose:
- maximum safe velocity:
- maximum safe acceleration:

## 3. Arduino Controller
### 3.1 Board And Firmware
- Arduino board model:
- firmware file/path:
- firmware version or commit:
- control loop period [ms]:
- serial baud rate:
- command input format:
- command unit:
- output log format:

### 3.2 Command Interface
- input command source:
- accepted command fields:
- `theta*_cmd` unit:
- conversion from `theta_cmd` to motor command:
- command rate [Hz]:
- command timeout behavior:
- invalid command behavior:

### 3.3 Measurement Interface
- `theta*_meas` source:
- `theta*_meas` unit:
- encoder calibration method:
- zeroing/homing method:
- startup offset handling:
- dropout handling:
- fault/status fields:

## 4. Vision Measurement Setup
### 4.1 Camera
- camera model:
- connection type:
- resolution:
- FPS:
- exposure setting:
- focus setting:
- mount height:
- mount orientation:
- field of view coverage:

### 4.2 Marker
- marker type:
- marker size [mm]:
- marker ID:
- marker attachment point:
- marker center offset from end-effector center [mm]:
- occlusion risk:

### 4.3 Calibration
- calibration method:
- calibration target:
- calibration date:
- lens distortion correction file/path:
- homography reference point count:
- homography reference coordinates in `base_frame`:
- reprojection error threshold:

### 4.4 Vision Logging
- vision logger file/path:
- `vision_time` source:
- raw video saved:
- raw video path rule:
- vision CSV path rule:
- marker miss handling:

## 5. Data Logging Structure
### 5.1 Real Main Log
- storage path:
- filename rule:
- required fields:
  - `run_id`
  - `time`
  - `target_x`
  - `target_y`
  - `target_z`
  - `theta1_cmd`
  - `theta2_cmd`
  - `theta3_cmd`
  - `theta1_meas`
  - `theta2_meas`
  - `theta3_meas`
  - `valid`
- additional fields:

### 5.2 Vision Raw Log
- storage path: `data/vision/raw/`
- filename rule: `vision_<run_id>.csv`
- required fields:
  - `run_id`
  - `vision_time`
  - `vision_x`
  - `vision_y`
  - `marker_detected`
  - `frame_id`
  - `valid`
- additional fields:

### 5.3 Angle-Derived Position Log
- generation method:
- FK/estimator function:
- estimator_method value:
- storage path:
- filename rule:
- required fields:
  - `run_id`
  - `time`
  - `measured_x_est`
  - `measured_y_est`
  - `measured_z_est`
  - `estimator_method`
  - `valid`

### 5.4 Processed Merged Dataset
- storage path:
- filename rule:
- alignment reference:
- resampling method:
- lag compensation method:
- invalid row exclusion rule:
- `error_x` source:
- `error_y` source:
- `error_z` source:

## 6. Synchronization And Alignment
- PC logger used as reference clock:
- Arduino timestamp source:
- camera timestamp source:
- common start event:
- common stop event:
- expected serial delay:
- expected camera delay:
- lag estimation method:
- alignment validation method:

## 7. Test Trajectories
### 7.1 Initial Safe Test
- trajectory name:
- target range `x` [mm]:
- target range `y` [mm]:
- target range `z` [mm]:
- duration [s]:
- command rate [Hz]:
- max velocity:
- max acceleration:
- expected theta range:

### 7.2 Data Collection Test
- trajectory name:
- target range `x` [mm]:
- target range `y` [mm]:
- target range `z` [mm]:
- duration [s]:
- repeat count:
- random seed if applicable:
- expected output files:

## 8. Pre-Run Checklist
- robot mounted securely:
- links and joints inspected:
- wiring inspected:
- power supply current limit set:
- emergency stop tested:
- Arduino connected:
- serial logger ready:
- camera connected:
- marker visible:
- calibration loaded:
- safe initial pose confirmed:
- output folders prepared:
- run_id assigned:

## 9. Run Procedure
1. Assign `run_id`:
2. Power on sequence:
3. Start Arduino/controller:
4. Run homing/zeroing:
5. Move to safe initial pose:
6. Start main logger:
7. Start vision logger:
8. Trigger common start event:
9. Execute trajectory:
10. Monitor safety/status:
11. Trigger common stop event:
12. Stop loggers:
13. Power down sequence:
14. Save run metadata:

## 10. Stop Conditions
- emergency stop pressed:
- overcurrent:
- motor driver fault:
- abnormal vibration:
- link interference:
- marker lost for longer than threshold:
- serial dropout:
- theta range exceeded:
- target range exceeded:
- operator judgment:

## 11. Post-Run Validation
- main CSV exists:
- vision CSV exists:
- optional raw video exists:
- timestamps monotonic:
- required columns present:
- no unexpected NaN:
- valid row ratio:
- theta range within limit:
- marker detection ratio:
- alignment check completed:
- processed merged dataset generated:
- run metadata saved:

## 12. Run Metadata
- run_id:
- operator:
- date/time:
- hardware configuration version:
- firmware version or commit:
- trajectory name:
- calibration file:
- Simscape model:
- code version or commit:
- notes:

## 13. Open Items
1. real main log storage path:
2. processed merged dataset storage path:
3. actual `theta*_meas` source:
4. `estimator_method` naming rule:
5. hardware-confirmed angle limits:
6. emergency stop implementation:
7. initial safe trajectory:
