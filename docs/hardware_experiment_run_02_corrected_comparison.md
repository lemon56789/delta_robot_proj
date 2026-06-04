# Hardware Experiment Run 02 - Corrected Comparison

이 문서는 가상센싱 보정을 적용한 뒤 baseline 데이터와 비교할 검증 데이터를 수집하기 위한 run protocol이다.

## 1. Experiment Scope
- experiment purpose: (작성: 보정 적용 후 baseline 대비 성능 개선을 확인하는 목적을 적는다)
- expected output: (작성: corrected main CSV, vision CSV, processed dataset, comparison report 등 산출물을 적는다)
- target stage: (작성: Stage 9 폐루프 적용 및 성능 검증 등으로 적는다)
- responsible members: (작성: 실험 진행, virtual sensor, Arduino, vision, data analysis 담당자를 적는다)
- date: (작성: 실험 수행일을 `YYYY-MM-DD`로 적는다)
- run_id: (작성: 이번 run 식별자를 적는다)
- baseline run_id: (작성: 비교 대상 baseline run_id를 적는다)
- correction enabled: (작성: corrected run이므로 원칙적으로 `yes`)

## 2. Correction Setup
- virtual sensor model: (작성: 사용할 모델 파일, 버전, 학습 데이터셋을 적는다)
- correction input fields: (작성: 모델 입력으로 사용할 필드를 적는다)
- correction output fields: (작성: 모델 출력 또는 적용할 correction 필드를 적는다)
- correction injection point: (작성: correction을 target position에 적용하는 위치와 방식을 적는다)
- safety clamp: (작성: correction 최대 허용값과 clamp 방식을 적는다)
- fallback behavior: (작성: 모델 추론 실패 시 uncorrected target 사용 등 fallback을 적는다)

## 3. Trajectory
- trajectory name: (작성: baseline과 동일하거나 대응되는 trajectory 이름을 적는다)
- target range `x` [mm]: (작성: x 목표 범위를 적는다)
- target range `y` [mm]: (작성: y 목표 범위를 적는다)
- target range `z` [mm]: (작성: z 목표 범위를 적는다)
- duration [s]: (작성: 1회 실행 시간을 적는다)
- repeat count: (작성: 반복 횟수를 적는다)
- command rate [Hz]: (작성: command 전송 주파수를 적는다)
- max velocity: (작성: trajectory 최대 속도를 적는다)
- max acceleration: (작성: trajectory 최대 가속도를 적는다)
- expected theta range: (작성: 예상되는 `theta1/2/3` 범위를 적는다)

## 4. Required Logs
- corrected main log: (작성: correction on 상태의 main log 경로를 적는다)
- vision raw log: (작성: corrected run의 vision CSV 경로를 적는다)
- correction log: (작성: model input/output, clamp 여부, fallback 여부를 저장할 로그 경로를 적는다)
- angle-derived position log: (작성: `measured_z_est` 생성 로그 경로를 적는다)
- processed merged dataset: (작성: corrected processed dataset 경로를 적는다)
- comparison report: (작성: baseline 대비 비교 결과 저장 경로를 적는다)

## 5. Run Procedure
1. Assign `run_id`: (작성: corrected run_id를 정한다)
2. Load baseline reference: (작성: 비교 대상 baseline run_id와 dataset을 확인한다)
3. Load virtual sensor model: (작성: 모델 파일과 설정을 로드한다)
4. Power on and zero: (작성: 전원 인가와 zeroing 수행 결과를 적는다)
5. Start main logger: (작성: main logger 시작 명령과 저장 파일을 적는다)
6. Start vision logger: (작성: vision logger 시작 명령과 저장 파일을 적는다)
7. Start correction logger: (작성: correction log 시작 방법을 적는다)
8. Trigger common start event: (작성: 정렬용 공통 시작 이벤트를 적는다)
9. Execute corrected trajectory: (작성: correction on 상태의 trajectory 실행 명령을 적는다)
10. Trigger common stop event: (작성: 정렬용 공통 종료 이벤트를 적는다)
11. Stop loggers: (작성: logger 종료와 파일 저장 확인 방법을 적는다)
12. Generate processed merged dataset: (작성: alignment와 merge 실행 방법을 적는다)
13. Compare against baseline: (작성: RMSE, max error, trajectory error 비교 방법을 적는다)
14. Save run metadata: (작성: metadata 저장 위치를 적는다)

## 6. Run-Specific Stop Conditions
- use base stop conditions: (작성: base config의 공통 중지 조건을 적용하는지 적는다)
- correction clamp exceeded: (작성: correction이 어느 기준을 넘으면 중지할지 적는다)
- model inference failure: (작성: 추론 실패가 몇 번 발생하면 중지할지 적는다)
- tracking error threshold: (작성: vision 기준 오차가 어느 값을 넘으면 중지할지 적는다)

## 7. Post-Run Validation
- required files exist: (작성: 필요한 파일이 모두 생성됐는지 확인한다)
- correction log valid: (작성: correction input/output, clamp, fallback 로그가 정상인지 확인한다)
- processed dataset generated: (작성: corrected processed dataset 생성 여부를 확인한다)
- baseline comparison completed: (작성: baseline 대비 비교가 완료됐는지 확인한다)
- RMSE comparison: (작성: baseline/corrected RMSE를 적는다)
- max error comparison: (작성: baseline/corrected max error를 적는다)
- corrected run accepted: (작성: 성능 비교 데이터로 채택할지 여부와 이유를 적는다)

## 8. Run Metadata
- run_id: (작성: 실험 실행 식별자를 적는다)
- baseline run_id: (작성: 비교 대상 baseline run_id를 적는다)
- operator: (작성: 실험 수행자를 적는다)
- date/time: (작성: 실험 시작/종료 시간을 적는다)
- hardware configuration version: (작성: base config 버전 또는 갱신일을 적는다)
- firmware version or commit: (작성: Arduino 펌웨어 버전 또는 commit을 적는다)
- virtual sensor model version: (작성: 모델 버전과 학습 데이터셋을 적는다)
- trajectory name: (작성: 사용한 trajectory 이름을 적는다)
- calibration file: (작성: vision calibration/homography 파일 경로를 적는다)
- code version or commit: (작성: logger, processing script, model inference 코드 버전 또는 commit을 적는다)
- notes: (작성: 특이사항을 적는다)
