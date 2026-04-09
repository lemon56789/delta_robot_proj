# Plan

## Goal
외부 비전 시스템을 델타 로봇의 운영 센서가 아니라 학습 및 검증 단계에서만 사용하는 `XY ground-truth 측정계`로 정의한다.
현재 프로젝트의 메인 데이터 흐름, 제어 루프, 가상센서 입력 계약은 유지하고, 비전 시스템은 외부 기준 측정 장치로 분리 문서화한다.

## Files
- `docs/plans/2026-04-06_001_vision_tracking_ground_truth.md`
- `docs/vision_tracking.md`
- `docs/daily_notes/2026-04-06.md`

## Changes
- `docs/vision_tracking.md`를 신규 작성한다.
- 비전 시스템의 목적을 `오차 보정 모델 학습 및 검증용 ground-truth 확보`로 명시한다.
- 적용 범위를 `개발/실험 단계 한정`으로 제한하고, 운영 단계에서는 제거된다는 점을 문서에 반영한다.
- 측정 범위를 `XY 위치 측정`으로 한정하고, 단일 top-view 웹캠 구성에서는 `Z ground-truth`를 직접 제공하지 않음을 명시한다.
- 시스템 구성 요소를 상부 USB 웹캠, 엔드이펙터 마커, 작업 평면 기준, OpenCV 기반 처리로 정리한다.
- 데이터 처리 파이프라인을 영상 획득, 마커 검출, 픽셀 좌표의 실제 좌표 변환, 로그 저장 순으로 문서화한다.
- 비전 데이터는 메인 CSV 계약의 필수 컬럼으로 편입하지 않고 별도 로그 또는 후처리 병합 대상으로 정의한다.
- 좌표계는 `docs/system_data_flow.md`의 `base_frame`, `mm` 기준과 정렬하도록 명시한다.
- 카메라 로그와 Arduino/PC logger 데이터는 후처리에서 timestamp alignment 한다는 원칙을 포함한다.
- calibration, homography, lens distortion correction, occlusion, lighting limitation 등 실험상 제약을 문서에 포함한다.

## Impact
- 기존 메인 시스템 구조는 유지된다.
- 기존 가상센서 입력 계약은 변경하지 않는다.
- 기존 CSV 고정 컬럼 계약은 유지된다.
- 비전 시스템은 학습 라벨 생성과 검증용 외부 기준 측정계로만 추가된다.

## Risk
- 단일 top-view 웹캠으로는 `Z` 위치를 직접 ground-truth로 제공할 수 없다.
- 조명 변화, 마커 가림, 렌즈 왜곡, 설치 오차에 따라 XY 정확도가 저하될 수 있다.
- `base_frame`과 카메라 좌표계 간 변환 정의가 불명확하면 데이터 정합성이 무너질 수 있다.
- 메인 CSV와 비전 로그의 timestamp alignment 기준이 불명확하면 학습 라벨 품질이 낮아질 수 있다.
- 문서 표현이 부정확하면 비전 시스템이 운영 제어 루프에 포함되는 것으로 오해될 수 있다.

## Validation
- 문서 목적과 범위가 `학습/검증용 외부 측정계`로 일관되는지 확인한다.
- `XY ground-truth only` 제한이 문서 전반에 명확히 반영되는지 확인한다.
- `docs/system_data_flow.md`, `AGENTS.md`, `README.md`와 충돌 없이 읽히는지 검토한다.
- 메인 CSV 계약을 변경하지 않는다는 점이 분명히 기술되어 있는지 확인한다.
- 좌표계, 단위, timestamp alignment, calibration, limitation 항목이 빠짐없이 포함되었는지 확인한다.
