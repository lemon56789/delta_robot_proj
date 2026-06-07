# Windows Vision Codex Home Repeatability Experiment Handoff

이 문서는 Windows vision 컴퓨터에서 `+X preload -> home` 반복성 실험
6개 run의 vision ground-truth CSV를 기록하기 위한 독립형 지시서다.
Vision Codex는 기존 vision logger와 calibration을 사용하며 run ID,
파일명, CSV 계약과 실행 순서를 변경하지 않는다.

## 1. Experiment Goal

- `(+40, 0) -> home`과 `(+60, 0) -> home` 접근 후 마지막 home 위치의
  반복성을 vision XY로 측정한다.
- Computer 2의 명령 메모와 동일한 run ID로 pairing 가능한 raw CSV를
  생성한다.
- 이 실험에서는 run별 zero 재설정이나 위치 보정을 적용하지 않는다.

## 2. Frozen Run IDs

아래 순서와 문자열을 그대로 사용한다.

```text
01 2026-06-07_home_repeat_xp40_r01
02 2026-06-07_home_repeat_xp40_r02
03 2026-06-07_home_repeat_xp40_r03
04 2026-06-07_home_repeat_xp60_r01
05 2026-06-07_home_repeat_xp60_r02
06 2026-06-07_home_repeat_xp60_r03
```

- `xp40`: Computer 2가 `(+40, 0)` preload 후 home으로 복귀한다.
- `xp60`: Computer 2가 `(+60, 0)` preload 후 home으로 복귀한다.
- `r01-r03`: 같은 조건의 독립 반복이다.
- 파일명과 CSV 내부 모든 row의 `run_id`는 위 문자열과 정확히 같아야
  한다.
- 실패한 run ID를 다른 실행에 재사용하지 않는다.

## 3. Required Existing Inputs

실험 전에 다음 정보를 확인한다.

```text
vision logger program/path:
camera index or device:
marker ID:
calibration/homography file:
output directory:
```

기존 실험에 사용한 logger 실행 방법이나 calibration 파일을 찾을 수
없으면 임의 logger, dummy calibration 또는 placeholder CSV를 만들지
않는다.

보고 형식:

```text
[BLOCKER]
문제:
확인한 경로:
필요:
대안:
```

## 4. Frozen Vision Configuration

다음 항목은 6개 run 동안 동일하게 유지한다.

- camera 위치, 높이, 각도와 초점
- camera index/device
- frame resolution과 frame rate
- marker와 marker ID
- calibration/homography 파일
- base-frame XY 방향과 mm 변환
- 조명과 노출 설정
- vision logger 코드와 실행 옵션
- output directory

금지 사항:

- run마다 vision 원점을 `(0, 0)`으로 다시 맞추기
- run별 homography 또는 calibration 재계산
- home shift를 제거한 좌표를 raw CSV에 저장
- invalid frame을 이전 위치로 덮어쓰기
- 누락된 frame을 임의 생성하거나 보간하기

## 5. Output Contract

기본 저장 경로:

```text
data/vision/raw/
```

파일명:

```text
vision_<run_id>.csv
```

필수 CSV 컬럼과 순서:

```text
run_id,vision_time,vision_x,vision_y,marker_detected,frame_id,valid
```

필드 의미:

- `run_id`: 2절의 확정 run ID
- `vision_time`: 기존 vision logger가 사용하는 PC capture timestamp
- `vision_x`, `vision_y`: 기존 homography 기준 base-frame millimeter
- `marker_detected`: marker 검출 여부
- `frame_id`: 단조 증가 frame 번호
- `valid`: 해당 XY 값을 분석에 사용할 수 있는지 여부

기존 logger가 선택 진단 컬럼을 이미 출력하면 유지할 수 있다.

```text
marker_id,reprojection_error,confidence,video_file
```

필수 컬럼을 삭제하거나 이름을 바꾸지 않는다.

## 6. Recording Scope

각 vision CSV에는 다음 전체 구간이 포함되어야 한다.

```text
초기 home
-> +X preload 이동
-> preload 위치 hold 2 s
-> home 복귀
-> home stabilization 5 s
```

- Computer 2가 preload 명령을 보내기 전에 기록을 시작한다.
- 마지막 home stabilization `5 s`가 모두 지난 뒤 기록을 종료한다.
- 시작 또는 종료 시점을 맞추기 위해 raw frame을 잘라내지 않는다.
- 분석에서는 마지막 stabilization 구간을 후처리로 선택한다.

## 7. Computer 2 Handshake

각 run마다 다음 순서를 지킨다.

1. Computer 2가 실행할 run ID를 읽어준다.
2. Vision 담당자는 문자열이 2절 목록과 같은지 확인한다.
3. 같은 run ID로 vision logger를 시작한다.
4. CSV가 생성되고 frame 입력이 시작된 것을 확인한다.
5. Computer 2에 다음 형식으로 알린다.

```text
VISION READY <run_id>
```

6. Computer 2는 READY 이후 preload 명령을 보낸다.
7. Computer 2가 home stabilization 완료 후 다음 형식으로 알린다.

```text
RUN END <run_id>
```

8. Vision 담당자는 RUN END 이후 logger를 종료한다.
9. 9절의 post-run check를 즉시 수행한다.

READY 전에 Computer 2가 preload 명령을 보냈다면 해당 run을 정상
데이터로 채택하지 말고 중단 사실을 메모한다.

## 8. Execution Order

### 8-A. xp40

다음 세 run을 먼저 수행한다.

```text
2026-06-07_home_repeat_xp40_r01
2026-06-07_home_repeat_xp40_r02
2026-06-07_home_repeat_xp40_r03
```

xp40 세 run이 모두 끝난 뒤 Computer 2가 안전 상태를 확인해야 xp60으로
진행한다.

### 8-B. xp60

Computer 2가 xp60 진행 가능하다고 확인한 경우에만 수행한다.

```text
2026-06-07_home_repeat_xp60_r01
2026-06-07_home_repeat_xp60_r02
2026-06-07_home_repeat_xp60_r03
```

Computer 2가 진동, 간섭 또는 stall로 xp60을 중단하면 누락 파일을
임의로 생성하지 않는다.

## 9. Post-Run Checks

각 run 직후 다음을 확인한다.

1. 파일명이 `vision_<run_id>.csv`인지 확인한다.
2. CSV가 비어 있지 않은지 확인한다.
3. 필수 컬럼 7개가 모두 존재하고 순서가 맞는지 확인한다.
4. 모든 row의 `run_id`가 파일명의 run ID와 같은지 확인한다.
5. `vision_time`이 단조 증가하는지 확인한다.
6. `frame_id`가 단조 증가하는지 확인한다.
7. 초기 home, +X 이동, preload hold, home 복귀와 마지막 stabilization이
   vision XY에서 확인되는지 점검한다.
8. valid ratio와 가장 긴 연속 marker loss를 기록한다.
9. marker 연속 소실이 `1 s`를 넘으면 invalid 후보로 표시한다.
10. CSV를 열어 저장한 뒤 원본 값을 수정하거나 재저장하지 않는다.

## 10. Stop Conditions

다음 중 하나면 vision 기록을 종료하고 Computer 2에 즉시 알린다.

- camera 연결이 끊기거나 frame 입력이 멈춘다.
- marker가 `1 s` 넘게 연속 소실된다.
- timestamp 또는 frame ID가 증가하지 않는다.
- 잘못된 run ID로 기록을 시작했다.
- calibration/homography가 예상 파일과 다르다.
- camera, marker 또는 조명이 이동했다.
- Computer 2에서 servo stall, 비정상 진동, 간섭 또는 emergency stop을
  알린다.

중단 보고:

```text
[BLOCKER]
run_id:
문제:
마지막 정상 frame_id:
마지막 정상 vision_time:
생성 파일:
필요:
```

## 11. Vision Run Memo

각 run에 대해 다음을 기록한다.

```text
run_id:
vision_start_time:
vision_end_time:
output_file:
calibration_file:
camera_device:
row_count:
valid_ratio:
longest_marker_loss_s:
initial_home_visible: yes/no
preload_motion_visible: yes/no
final_home_stabilization_visible: yes/no
operator_note:
```

권장 파일명:

```text
home_repeatability_vision_2026-06-07.txt
```

## 12. Files To Return

원래 컴퓨터 담당자에게 다음 파일을 전달한다.

```text
home_repeatability_vision_2026-06-07.txt
data/vision/raw/vision_2026-06-07_home_repeat_xp40_r01.csv
data/vision/raw/vision_2026-06-07_home_repeat_xp40_r02.csv
data/vision/raw/vision_2026-06-07_home_repeat_xp40_r03.csv
data/vision/raw/vision_2026-06-07_home_repeat_xp60_r01.csv
data/vision/raw/vision_2026-06-07_home_repeat_xp60_r02.csv
data/vision/raw/vision_2026-06-07_home_repeat_xp60_r03.csv
```

실제로 생성된 원본 파일만 전달한다. 중단 또는 실패로 생성되지 않은
파일은 placeholder로 만들지 않는다.

## 13. Analysis Boundary

Windows vision 컴퓨터에서는 preload 조건의 우열이나 home offset을
확정하지 않는다. Raw CSV와 품질 메모만 반환한다.

원래 컴퓨터에서 다음 값을 동일 정책으로 계산한다.

- 마지막 home stabilization 구간의 XY 중앙값
- 조건별 X/Y 표준편차
- 반복 간 최대 pairwise XY 거리
- 초기 home 대비 최종 home 이동
- xp40/xp60 진동 메모와 반복성의 tradeoff

두 조건의 반복성이 비슷하면 부하가 작은 `xp40`을 우선한다.
