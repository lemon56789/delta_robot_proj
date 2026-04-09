# Vision-Based Position Tracking

이 문서는 델타 로봇의 오차 보정 모델 학습과 성능 검증을 위해 사용하는 외부 비전 기반 위치 측정계를 정의한다.
본 문서의 비전 시스템은 운영 단계의 제어 센서가 아니라 개발 및 실험 단계에서만 사용하는 `XY ground-truth 측정계`다.

## 1. Purpose
- 엔드이펙터의 실제 위치에 대한 외부 기준값을 확보해 가상센서 학습 라벨과 검증 기준으로 사용한다.
- 초기 학습 및 검증 단계에서는 외부 비전 시스템으로 위치를 측정하고, 운영 단계에서는 해당 시스템을 제거한다.
- 최종 운영 경로는 `motor command + measured motor angle + simulation data + virtual sensing` 기준을 유지한다.

## 2. Scope
- 측정 범위는 `base_frame` 기준 `XY` 위치로 한정한다.
- 단일 top-view USB 웹캠 구성에서는 `Z` 위치를 직접 ground-truth로 제공하지 않는다.
- 본 문서는 학습 및 검증용 외부 측정계만 다루며, 운영 제어 루프 입력 장치는 다루지 않는다.

## 3. System Overview
비전 기반 위치 측정 시스템은 다음 요소로 구성한다.

- 상부 카메라: 작업 공간을 위에서 내려다보는 top-view USB 웹캠
- 엔드이펙터 마커: ArUco marker 또는 color marker
- 작업 평면 기준: 실제 좌표 변환용 기준 마킹
- 영상 처리: OpenCV 기반 검출 및 좌표 변환

카메라는 작업 공간 전체가 보이도록 상부에 고정 설치한다.

## 4. System Configuration
### 4.1 Camera
- 일반 USB 웹캠 사용
- 해상도는 최소 `640x480` 이상
- 설치 위치는 로봇 상부이며, 전체 작업 공간이 프레임 안에 포함되어야 한다
- 렌즈 왜곡 보정을 위해 calibration 절차를 수행한다

### 4.2 End-Effector Marker
다음 두 가지 방식 중 하나를 사용한다.

#### Option A. ArUco Marker
- OpenCV `aruco` 모듈 사용 가능
- marker center 추정이 비교적 안정적이다
- orientation 정보까지 함께 얻을 수 있다
- 조명 변화에 color marker보다 상대적으로 강하다

#### Option B. Color Marker
- 빨간색 또는 파란색 marker 부착
- HSV 기반 color segmentation 사용
- 구현은 단순하지만 조명 변화와 배경 영향에 민감하다

실험 초기 기준안은 `ArUco marker`를 우선 선택한다.

### 4.3 Work Plane
- 작업 평면 위에 실제 좌표 기준점을 둔다
- 기준판, A4 용지, 또는 평판 지그를 사용할 수 있다
- 최소 2점 이상이 아니라, 실제 좌표 변환 안정성을 위해 4점 기준 마킹을 권장한다
- 기준점 좌표는 `base_frame` 기준 `mm` 단위로 정의한다

## 5. Coordinate And Data Policy
- 최종 위치 값은 `docs/system_data_flow.md`와 같은 `base_frame` 기준으로 기록한다
- 단위는 `mm`를 사용한다
- 비전 데이터는 현재 메인 CSV 고정 컬럼에 직접 편입하지 않는다
- 비전 측정 결과는 별도 로그 또는 별도 CSV로 저장하고, 후처리에서 메인 데이터와 병합한다
- 비전 시스템은 학습 라벨 생성과 평가용 ground-truth 생성에만 사용한다

## 6. Pipeline
전체 측정 및 기록 순서는 다음과 같다.

1. 목표 위치 `target_x`, `target_y`, `target_z`를 입력한다.
2. 로봇이 IK 기반 제어에 따라 동작한다.
3. 카메라에서 영상 프레임을 획득한다.
4. 엔드이펙터 marker를 검출한다.
5. 렌즈 왜곡 보정과 평면 좌표 변환을 적용한다.
6. pixel 좌표를 `base_frame` 기준 실제 `x`, `y` 좌표로 변환한다.
7. 비전 기반 ground-truth와 메인 로그를 timestamp 기준으로 정렬한다.
8. 학습 라벨 또는 검증용 기준 데이터로 저장한다.

## 7. Calibration And Transform
비전 측정계를 ground-truth로 사용하려면 아래 절차가 필요하다.

- 카메라 내부 파라미터 calibration
- 렌즈 왜곡 보정
- 작업 평면 기준점 추출
- homography 또는 동등한 평면 좌표 변환 계산
- 카메라 좌표계 결과를 `base_frame` 기준 `mm` 단위로 변환

이 절차가 없으면 pixel 좌표는 프로젝트의 위치 기준과 직접 비교할 수 없다.

## 8. Timestamp Alignment
- 카메라 측정 로그는 자체 timestamp를 기록한다
- Arduino와 PC logger는 현재 `docs/system_data_flow.md`의 시간 정책을 따른다
- 비전 로그와 메인 로그의 alignment는 실시간 결합이 아니라 후처리 기준으로 수행한다
- alignment 기준은 공통 이벤트 또는 PC logger 기준 시간축을 사용한다

## 9. Output Definition
비전 시스템의 기본 출력은 다음과 같다.

- `vision_time`
- `vision_x`
- `vision_y`
- `marker_detected`
- `frame_id`

필요 시 품질 진단용 필드를 추가할 수 있다.

- `marker_id`
- `reprojection_error`
- `confidence`

위 출력은 외부 측정계 전용 로그이며, 현재 메인 CSV 계약의 필수 컬럼은 아니다.

## 10. Vision Log Storage Policy
- 비전 로그는 현재 메인 CSV와 분리된 별도 데이터로 저장한다.
- 초기 단계 저장 기준은 `raw` 우선 정책으로 둔다.
- 기본 저장 경로는 `data/vision/raw/`로 정의한다.
- 현재 리포지토리에는 `data/vision/raw/` 디렉터리를 실제 raw 로그 기준 경로로 둔다.
- 한 번의 실험 실행은 하나의 `run_id`로 식별하고, 비전 로그 파일명은 해당 `run_id`를 포함한다.
- 최소 파일명 규칙은 `vision_<run_id>.csv`로 둔다.
- 필요 시 같은 `run_id` 기준으로 원본 영상 또는 프레임 묶음을 함께 저장할 수 있다.
- 가공 데이터 또는 병합 데이터의 저장 구조는 후속 정책에서 별도로 정의한다.
- 비전 로그는 raw 기준 원본 보존 목적이며, 메인 로그와의 결합은 저장 단계가 아니라 후처리 단계에서 수행한다.

예시 경로:
- `data/vision/raw/vision_2026-04-06_run001.csv`
- `data/vision/raw/vision_2026-04-06_run001.mp4`

최소 CSV 필드:
- `vision_time`
- `vision_x`
- `vision_y`
- `marker_detected`
- `frame_id`

선택 필드:
- `marker_id`
- `reprojection_error`
- `confidence`
- `video_file`

## 11. Relation To Current Project Contract
- 메인 시스템 구조는 `Target -> Controller -> Real Robot -> Measured Data -> Virtual Sensor -> Correction` 기준을 유지한다
- 가상센서의 운영 입력 계약은 변경하지 않는다
- 비전 시스템은 운영 단계 센서가 아니라 학습 및 검증용 외부 ground-truth 장치다
- 따라서 본 문서는 현재 시스템 계약을 대체하지 않고, 실험 및 평가 레이어를 보완한다

## 12. Limitations
- 단일 top-view 웹캠만으로는 `Z` 위치를 직접 측정할 수 없다
- marker occlusion이 발생하면 측정이 끊길 수 있다
- 조명 변화가 color marker 검출 정확도에 영향을 줄 수 있다
- webcam frame rate와 exposure 설정에 따라 timestamp jitter가 발생할 수 있다
- camera installation angle 오차가 크면 XY 좌표 변환 오차가 커질 수 있다

## 13. Recommended Initial Setup
- camera: USB webcam, top-view, `640x480` 이상
- marker: ArUco marker
- processing: OpenCV
- coordinate transform: planar homography
- logging: `data/vision/raw/` separate vision log + post-alignment

## 14. Open Questions
1. 카메라 설치 높이와 시야각을 어떤 범위로 고정할 것인가?
2. 기준 평면 마킹 좌표를 `base_frame`에 어떻게 정합할 것인가?
3. 원본 영상과 CSV를 항상 함께 저장할 것인가, 선택 저장으로 둘 것인가?
4. 평가 단계에서 `vision_x`, `vision_y`와 메인 로그를 어떤 기준 이벤트로 정렬할 것인가?
