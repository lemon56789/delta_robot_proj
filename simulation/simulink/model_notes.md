# Simulink Model Notes

## Current Latest Model
- current latest `slx`: `simscape_delta_robot_trajectory.slx`
- not latest: `simscape_delta_robot_trajectory_axisfix.slx`

## Main Files
- `simscape_delta_robot_trajectory.slx`
  - 현재 기준 Simscape trajectory 모델이다.
- `init_delta_params.m`
  - 델타 로봇의 기하 파라미터, base joint 위치, joint frame rotation, platform 관련 초기 파라미터를 workspace에 설정한다.
- `load_fake_pipeline_theta.m`
  - fake pipeline CSV에서 `time`, `theta1_cmd`, `theta2_cmd`, `theta3_cmd`를 읽고 Simulink 입력용 `timeseries`로 변환한다.
  - 현재 스크립트는 `boot_ms -> s`, `deg -> rad` 변환을 수행한다.
- `run_fake_pipeline_simscape.m`
  - 파라미터 초기화와 CSV 로드를 수행한 뒤 `simscape_delta_robot_trajectory.slx`를 실행한다.
  - 시뮬레이션 출력 `sim_x`, `sim_y`, `sim_z`를 CSV 시간축에 맞춰 보간하고 `_simscape.csv` 파일로 저장한다.
  - 현재 `error_* = target_* - sim_*`를 다시 계산하는 부분은 SoT의 correction 의미가 아니라 diagnostic 용도다.
- `check_joint_tips.m`
  - `out` 변수에서 마지막 시점의 `J1`, `J2`, `J3` 좌표를 읽어 테이블로 확인한다.
- `create_theta_trajectory.m`
  - 대칭형 `theta` 테스트 궤적을 생성한다.
- `create_theta_trajectory_asym.m`
  - 비대칭형 `theta` 테스트 궤적을 생성한다.

## Other Models
- `simscape_delta_robot_jointsensor.slx`
  - joint sensor 관련 확인용 보조 모델로 보관한다.
- `simscape_delta_robot_minimal.slx`
  - 단순화된 보조 모델로 보관한다.
- `simscape_delta_robot_platform.slx`
  - platform 관련 보조 모델로 보관한다.
- `simscape_delta_robot_skeleton.slx`
  - skeleton 단계 보조 모델로 보관한다.
- `single_revolute_test.slx`
  - 단일 revolute joint 검사용 테스트 모델로 보관한다.

## Generated Files Policy
- `slprj/`, `*.slxc`, `*.avi`, autosave 파일은 생성물로 보고 버전관리 대상에서 제외한다.
