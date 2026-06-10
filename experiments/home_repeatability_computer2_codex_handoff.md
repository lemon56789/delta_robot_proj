# Computer 2 Codex Home Repeatability Experiment Handoff

이 문서는 추가 Run 02 OFF/ON 실험 전에 `+X preload -> home` 접근 방향의
home 반복성을 확인하기 위한 최소 하드웨어 실험 지시서다. Computer 2
Codex는 아래 run ID, 명령, 시간과 중단 조건을 변경하지 않는다.

## 1. Experiment Goal

- `(+40, 0) -> home`과 `(+60, 0) -> home` 접근 후 vision home 위치의
  반복성을 비교한다.
- 관찰된 +X 방향 부하와 진동을 기록한다.
- 이후 Diamond OFF/ON 최소 확인 실험에 사용할 공통 preload 위치를
  결정한다.
- correction, virtual sensor model과 Run 02 logger는 이 실험에서
  사용하지 않는다.

## 2. Frozen Run IDs

실험일과 파일 식별자는 아래 값으로 고정한다.

```text
01 2026-06-07_home_repeat_xp40_r01
02 2026-06-07_home_repeat_xp40_r02
03 2026-06-07_home_repeat_xp40_r03
04 2026-06-07_home_repeat_xp60_r01
05 2026-06-07_home_repeat_xp60_r02
06 2026-06-07_home_repeat_xp60_r03
```

- `xp40`: preload target `(+40, 0, HOME_Z)`
- `xp60`: preload target `(+60, 0, HOME_Z)`
- `r01-r03`: 같은 조건의 독립 반복
- Computer 2 메모와 Windows vision CSV는 반드시 같은 run ID를 쓴다.
- 실패한 run ID를 재사용하지 않는다. 재실행이 필요하면 작업을 중단하고
  새 run ID를 원래 컴퓨터 담당자에게 요청한다.

## 3. Fixed Commands

공통 Z:

```text
HOME_Z = -263.27731514697575 mm
```

Python IK로 계산한 direct theta command:

```text
xp40 preload: ALL 1.391730 -7.272993 9.941871
xp60 preload: ALL 3.129250 -9.819505 15.763535
home:         ALL 0 0 0
```

각 run의 시간:

```text
preload 도착 후 hold: 2 s
home 명령 후 stabilization: 5 s
```

## 4. Preconditions

1. Arduino에 현재 실험용 firmware가 업로드되어 있어야 한다.
2. 전원 차단 담당자가 즉시 대응할 수 있어야 한다.
3. camera, marker, homography, 조명과 로봇 조립 상태를 6회 동안 바꾸지
   않는다.
4. Arduino IDE Serial Monitor 이외의 프로그램은 Arduino COM 포트를
   사용하지 않는다.
5. Serial Monitor 설정:
   - baud rate: `9600`
   - line ending: `Newline`
6. Serial Monitor를 열 때 Arduino가 리셋되고 자동 HOME을 수행할 수
   있다. startup message와 `Servos initialized at HOME.`을 확인한 후
   실험을 시작한다.
7. Serial Monitor는 6개 run 사이에 닫거나 다시 열지 않는다. 다시 열면
   Arduino reset으로 접근 이력이 바뀌므로 해당 실험 세션을 중단한다.

## 5. Vision Handshake

각 run마다 Computer 2와 Windows vision 담당자가 다음 순서를 사용한다.

1. Computer 2가 다음 run ID를 음성 또는 메시지로 읽어준다.
2. Vision 담당자가 같은 run ID로 기록을 시작한다.
3. Vision 담당자가 `VISION READY <run_id>`라고 응답한다.
4. Computer 2는 READY 응답 뒤 preload 명령을 보낸다.
5. home stabilization `5 s`가 끝나면 Computer 2가
   `RUN END <run_id>`라고 알린다.
6. Vision 담당자는 그 이후 기록을 종료하고 파일 존재를 확인한다.

Vision 출력 파일:

```text
vision_<run_id>.csv
```

필수 CSV 컬럼:

```text
run_id,vision_time,vision_x,vision_y,marker_detected,frame_id,valid
```

Vision 기록에는 preload 이동 시작 전 home, +X 이동, `2 s` preload hold,
home 복귀와 `5 s` stabilization 전체가 포함되어야 한다.

## 6. Execution Order

### 6-A. xp40 Runs

아래 절차를 `r01`, `r02`, `r03`에 각각 수행한다.

1. 현재 로봇이 HOME에 있고 vision marker가 검출되는지 확인한다.
2. 5절의 vision handshake를 완료한다.
3. Serial Monitor에 다음 명령을 한 번 보낸다.

```text
ALL 1.391730 -7.272993 9.941871
```

4. 명령 완료 후 `2 s` 기다린다.
5. Serial Monitor에 다음 명령을 한 번 보낸다.

```text
ALL 0 0 0
```

6. home 도착 후 `5 s` 기다린다.
7. vision 기록을 종료한다.
8. run별 진동, 소음, 간섭과 명령 완료 여부를 메모한다.

xp40 세 run이 모두 중단 조건 없이 끝난 경우에만 xp60으로 진행한다.

### 6-B. xp60 Runs

아래 절차를 `r01`, `r02`, `r03`에 각각 수행한다.

1. 현재 로봇이 HOME에 있고 vision marker가 검출되는지 확인한다.
2. 5절의 vision handshake를 완료한다.
3. Serial Monitor에 다음 명령을 한 번 보낸다.

```text
ALL 3.129250 -9.819505 15.763535
```

4. 명령 완료 후 `2 s` 기다린다.
5. Serial Monitor에 다음 명령을 한 번 보낸다.

```text
ALL 0 0 0
```

6. home 도착 후 `5 s` 기다린다.
7. vision 기록을 종료한다.
8. run별 진동, 소음, 간섭과 명령 완료 여부를 메모한다.

## 7. Stop Conditions

다음 중 하나라도 발생하면 즉시 전원을 차단하고 해당 조건의 나머지
run을 진행하지 않는다.

- +X 이동에서 진동이 계속 증가한다.
- servo stall, 비정상 소음 또는 과열 징후가 있다.
- link interference, platform tilt, 충돌 위험이 있다.
- 명령 방향과 실제 이동 방향이 다르다.
- home으로 정상 복귀하지 못한다.
- marker가 `1 s`보다 오래 연속 소실된다.
- Serial Monitor가 닫히거나 Arduino가 예상치 않게 reset된다.

xp40에서 중단 조건이 발생하면 xp60은 수행하지 않는다.

문제 보고 형식:

```text
[BLOCKER]
run_id:
문제:
발생 명령:
관찰:
필요:
```

## 8. Computer 2 Run Memo

각 run에 대해 아래 값을 텍스트 파일 또는 표에 기록한다.

```text
run_id:
preload_command:
preload_command_time:
home_command_time:
vision_ready_confirmed: yes/no
preload_hold_completed: yes/no
home_stabilization_completed: yes/no
vibration: none/weak/strong
abnormal_noise: yes/no
interference_or_stall: yes/no
arduino_reset: yes/no
operator_note:
```

권장 파일명:

```text
home_repeatability_computer2_2026-06-07.txt
```

## 9. Post-Run Checks

각 run 직후 다음을 확인한다.

- vision CSV 파일명이 확정 run ID와 일치한다.
- CSV 내부 모든 `run_id`가 파일명의 run ID와 같다.
- `vision_time`이 단조 증가한다.
- preload와 home 복귀가 vision XY에서 확인된다.
- 마지막 `5 s` home stabilization 구간이 기록되어 있다.
- marker 연속 소실이 `1 s` 이하다.

실험 중 vision 원점, homography 또는 좌표를 run별로 재설정하지 않는다.

## 10. Files To Return

폴더 구조를 유지해 원래 컴퓨터 담당자에게 다음 파일을 전달한다.

```text
home_repeatability_computer2_2026-06-07.txt
vision_2026-06-07_home_repeat_xp40_r01.csv
vision_2026-06-07_home_repeat_xp40_r02.csv
vision_2026-06-07_home_repeat_xp40_r03.csv
vision_2026-06-07_home_repeat_xp60_r01.csv
vision_2026-06-07_home_repeat_xp60_r02.csv
vision_2026-06-07_home_repeat_xp60_r03.csv
```

중단으로 생성되지 않은 파일은 임의로 만들지 않는다. 실패 또는 중단
사유는 Computer 2 run memo에 남긴다.

## 11. Selection Rule

최종 preload 선택은 원래 컴퓨터에서 vision 데이터 분석 후 결정한다.
Computer 2에서 육안 판단만으로 preload 조건을 확정하지 않는다.

- 우선 비교값: 마지막 home stabilization 구간의 XY 중앙값과 반복 간
  최대 거리
- 두 조건의 반복성이 비슷하면 부하가 작은 `xp40`을 선택한다.
- `xp60`이 명확히 더 반복적이어도 strong vibration, abnormal noise 또는
  interference가 있으면 선택하지 않는다.
