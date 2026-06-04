# Hardware Experiment Run 03 - Final Demo

이 문서는 최종 시연용 움직임을 실행하기 위한 run protocol이다. 시연 목적에 따라 최소 로그만 남길 수 있지만, 재현성을 위해 main log와 metadata는 남긴다.

## 1. Experiment Scope
- experiment purpose: (작성: 최종 시연에서 보여줄 기능과 메시지를 적는다)
- expected output: (작성: 시연 영상, main log, optional vision log, metadata 등 산출물을 적는다)
- target stage: (작성: Stage 9 또는 Stage 10 등 시연 위치를 적는다)
- responsible members: (작성: 시연 진행, safety, logging 담당자를 적는다)
- date: (작성: 시연 수행일을 `YYYY-MM-DD`로 적는다)
- run_id: (작성: 이번 demo run 식별자를 적는다)
- correction enabled: (작성: 보정 on/off 여부를 적는다)
- vision used: (작성: vision을 검증용으로 켤지, 운영 모드처럼 끌지 적는다)

## 2. Demo Motion
- demo name: (작성: 시연 움직임 이름을 적는다)
- visual goal: (작성: 관찰자에게 보여줄 동작 목적을 적는다. 예: 반복 위치 추종, 보정 전후 비교)
- target range `x` [mm]: (작성: x 목표 범위를 적는다)
- target range `y` [mm]: (작성: y 목표 범위를 적는다)
- target range `z` [mm]: (작성: z 목표 범위를 적는다)
- duration [s]: (작성: 시연 실행 시간을 적는다)
- repeat count: (작성: 반복 횟수를 적는다)
- command rate [Hz]: (작성: command 전송 주파수를 적는다)
- max velocity: (작성: 시연용 안전 속도 제한을 적는다)
- max acceleration: (작성: 시연용 안전 가속도 제한을 적는다)

## 3. Required Logs
- main log: (작성: 최소 main log 경로를 적는다)
- demo video: (작성: 시연 촬영 영상 경로를 적는다)
- optional vision raw log: (작성: vision을 켠 경우 CSV 경로를 적는다)
- optional processed dataset: (작성: 시연 후 정량 검증을 할 경우 dataset 경로를 적는다)

## 4. Run Procedure
1. Assign `run_id`: (작성: demo run_id를 정한다)
2. Load base config: (작성: 사용할 base config 버전 또는 갱신일을 적는다)
3. Confirm demo safety area: (작성: 주변 정리, 관찰자 거리, emergency stop 위치를 확인한다)
4. Power on and zero: (작성: 전원 인가와 zeroing 수행 결과를 적는다)
5. Start required logger: (작성: main logger와 필요한 선택 logger를 시작한다)
6. Start demo video recording: (작성: 영상 촬영 시작 방법을 적는다)
7. Execute demo motion: (작성: demo trajectory 실행 명령과 파라미터를 적는다)
8. Stop demo motion: (작성: 정상 종료 또는 중지 방법을 적는다)
9. Stop logger and video: (작성: 로그와 영상 저장 확인 방법을 적는다)
10. Power down sequence: (작성: 전원 차단 순서를 적는다)
11. Save run metadata: (작성: metadata 저장 위치를 적는다)

## 5. Run-Specific Stop Conditions
- use base stop conditions: (작성: base config의 공통 중지 조건을 적용하는지 적는다)
- audience safety threshold: (작성: 시연 환경에서 추가할 안전 거리/접근 금지 조건을 적는다)
- demo tracking failure: (작성: 시연 실패로 보고 중지할 동작 기준을 적는다)
- correction fallback if used: (작성: 보정 사용 시 fallback 발생 기준과 중지 여부를 적는다)

## 6. Post-Run Validation
- demo completed: (작성: 시연이 의도한 동작을 완료했는지 적는다)
- main log exists: (작성: main log 파일 존재 여부를 확인한다)
- video exists: (작성: 시연 영상 파일 존재 여부를 확인한다)
- visible issue: (작성: 시연 중 관찰된 흔들림, 충돌 위험, marker loss 등을 적는다)
- optional metric: (작성: 정량 검증을 했다면 RMSE, max error 등 지표를 적는다)
- demo accepted: (작성: 최종 시연 자료로 채택할지 여부와 이유를 적는다)

## 7. Run Metadata
- run_id: (작성: 실험 실행 식별자를 적는다)
- operator: (작성: 시연 수행자를 적는다)
- date/time: (작성: 시연 시작/종료 시간을 적는다)
- hardware configuration version: (작성: base config 버전 또는 갱신일을 적는다)
- firmware version or commit: (작성: Arduino 펌웨어 버전 또는 commit을 적는다)
- virtual sensor model version if used: (작성: 보정 사용 시 모델 버전을 적는다)
- demo name: (작성: demo motion 이름을 적는다)
- code version or commit: (작성: 실행 script, logger, model inference 코드 버전 또는 commit을 적는다)
- notes: (작성: 특이사항을 적는다)
