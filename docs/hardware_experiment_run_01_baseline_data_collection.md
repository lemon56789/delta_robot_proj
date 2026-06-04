# Hardware Experiment Run 01 - Baseline Data Collection

이 문서는 오차 학습용 baseline 데이터를 수집하기 위한 run protocol이다. 보정은 끄고, measured/sim/vision 로그를 수집해 processed merged dataset에서 `error_*` label을 생성한다.

## 1. Experiment Scope
- experiment purpose: (작성: 학습용 baseline error dataset 수집 목적을 적는다)
- expected output: (작성: main CSV, vision CSV, angle-derived position log, Simscape output, processed merged dataset 등 산출물을 적는다)
- target stage: (작성: Stage 7 실제 데이터 수집 또는 Stage 8 학습 데이터 준비 등으로 적는다)
- responsible members: (작성: 실험 진행, Arduino, vision, data processing 담당자를 적는다)
- date: (작성: 실험 수행일을 `YYYY-MM-DD`로 적는다)
- run_id: (작성: 이번 run 식별자를 적는다)
- correction enabled: (작성: baseline이므로 원칙적으로 `no`)

## 2. Trajectory
- trajectory name: (작성: baseline 데이터 수집용 trajectory 이름을 적는다)
- target range `x` [mm]: (작성: x 목표 범위를 적는다)
- target range `y` [mm]: (작성: y 목표 범위를 적는다)
- target range `z` [mm]: (작성: z 목표 범위를 적는다)
- duration [s]: (작성: 1회 실행 시간을 적는다)
- repeat count: (작성: 반복 횟수를 적는다)
- command rate [Hz]: (작성: command 전송 주파수를 적는다)
- max velocity: (작성: trajectory 최대 속도를 적는다)
- max acceleration: (작성: trajectory 최대 가속도를 적는다)
- random seed if applicable: (작성: 랜덤 trajectory이면 seed를 적고, 아니면 `N/A`)
- expected theta range: (작성: 예상되는 `theta1/2/3` 범위를 적는다)

## 3. Required Logs
- main log: (작성: main log 저장 경로와 파일명을 적는다)
- vision raw log: (작성: vision CSV 저장 경로와 파일명을 적는다)
- raw video: (작성: 저장 여부와 파일명을 적는다)
- angle-derived position log: (작성: `measured_z_est` 생성 로그 경로를 적는다)
- Simscape output: (작성: 비교에 사용할 Simscape output 파일 또는 생성 방법을 적는다)
- processed merged dataset: (작성: 생성할 processed dataset 경로를 적는다)

## 4. Run Procedure
1. Assign `run_id`: (작성: run_id를 정하고 모든 logger 설정에 반영한다)
2. Load base config: (작성: 사용할 base config 버전 또는 갱신일을 적는다)
3. Power on and zero: (작성: 전원 인가와 zeroing 수행 결과를 적는다)
4. Start main logger: (작성: main logger 시작 명령과 저장 파일을 적는다)
5. Start vision logger: (작성: vision logger 시작 명령과 저장 파일을 적는다)
6. Trigger common start event: (작성: 정렬용 공통 시작 이벤트를 적는다)
7. Execute baseline trajectory: (작성: trajectory 실행 명령과 파라미터를 적는다)
8. Trigger common stop event: (작성: 정렬용 공통 종료 이벤트를 적는다)
9. Stop loggers: (작성: logger 종료와 파일 저장 확인 방법을 적는다)
10. Generate angle-derived position: (작성: `theta*_meas` 기반 FK/estimator 실행 방법을 적는다)
11. Generate processed merged dataset: (작성: alignment와 merge 실행 방법을 적는다)
12. Save run metadata: (작성: metadata 저장 위치를 적는다)

## 5. Run-Specific Stop Conditions
- use base stop conditions: (작성: base config의 공통 중지 조건을 적용하는지 적는다)
- marker loss threshold: (작성: baseline 데이터 품질을 위해 허용할 marker loss 기준을 적는다)
- valid row ratio threshold: (작성: 유효 row 비율이 어느 값보다 낮으면 실패로 볼지 적는다)
- theta range threshold: (작성: baseline trajectory에서 허용할 theta 범위를 적는다)

## 6. Post-Run Validation
- required files exist: (작성: 필요한 파일이 모두 생성됐는지 확인한다)
- timestamp monotonic: (작성: main/vision timestamp가 단조 증가하는지 확인한다)
- required columns present: (작성: 필수 컬럼 존재 여부를 확인한다)
- marker detection ratio: (작성: marker 검출률을 계산한다)
- valid row ratio: (작성: `valid=true` row 비율을 계산한다)
- alignment check completed: (작성: alignment plot 또는 metric 확인 결과를 적는다)
- processed error labels generated: (작성: `error_x/y/z` 생성 여부와 기준을 적는다)
- baseline dataset accepted: (작성: 학습 데이터로 사용할지 여부와 이유를 적는다)

## 7. Run Metadata
- run_id: (작성: 실험 실행 식별자를 적는다)
- operator: (작성: 실험 수행자를 적는다)
- date/time: (작성: 실험 시작/종료 시간을 적는다)
- hardware configuration version: (작성: base config 버전 또는 갱신일을 적는다)
- firmware version or commit: (작성: Arduino 펌웨어 버전 또는 commit을 적는다)
- trajectory name: (작성: 사용한 trajectory 이름을 적는다)
- calibration file: (작성: vision calibration/homography 파일 경로를 적는다)
- Simscape model: (작성: 비교에 사용할 Simscape 모델 이름을 적는다)
- code version or commit: (작성: logger, processing script, IK/FK 코드 버전 또는 commit을 적는다)
- notes: (작성: 특이사항을 적는다)
