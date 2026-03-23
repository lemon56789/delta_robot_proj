# AGENTS.md — Delta Robot Virtual Sensing Project
버전: v1.1-fixed · 갱신: 2026-03-22 · 대상: Codegen AI (Codex 등)

---

# 목적
본 문서는 **저가형 델타 로봇의 가상 센싱 기반 정밀도 향상 프로젝트**에서  
AI 에이전트(Codex 등)가 따라야 할 **작업 규칙, 코드 작성 규약, 데이터 구조,  
변경 워크플로, 연구 수행 기준**을 정의한다.

---

# 0. 최상위 규칙 (Non-negotiables) — 가장 중요

## 0-A Source of Truth (SoT) 우선순위
상충 시 아래 순서를 따른다:
1) docs/* (system_architecture, data_format 등)
2) AGENTS.md
3) README.md
4) 코드 및 주석

---

## 0-B 변경 기록 의무 (Daily Notes)
- 어떤 파일이든 수정/추가/삭제 발생 시 반드시 기록
- 경로:
  docs/daily_notes/YYYY-MM-DD.md
- 파일 없으면 생성

### 필수 포함 항목
- 무엇을
- 왜
- 어떻게
- 결과
- 변경 파일
- 다음 작업

---

## 0-C placeholder/dummy 구현 금지
- 껍데기 코드 생성 금지
- 실제 동작 가능한 수준으로 구현
- 불가능하면 즉시 BLOCKER 보고

---

## 0-D 공개 인터페이스 무단 변경 금지
다음 항목 임의 변경 금지:
- 데이터 포맷 (CSV 구조)
- 함수 입력/출력
- 폴더 구조
- 시스템 데이터 흐름

변경 시 → Contract Change → 승인 필요

---

## 0-E 승인 기반 작업 원칙 (매우 중요)
- 파일 수정 전 반드시 계획서 작성
- 승인 전 어떤 파일도 변경 금지

---

# 1. 변경 정책

## 1-A Doc-only 변경 (승인 필요)
- README.md
- docs/*
- docs/daily_notes/*
- docs/plans/*
- fulltext.md

단, 아래 항목은 Doc-only로 분류하지 않음:
- AGENTS.md
- 데이터 포맷 변경

---

## 1-B Code 변경 (승인 필요)
- Python 코드
- Arduino 코드
- MATLAB/Simscape
- 데이터 처리 코드

---

## 1-C Contract Change (엄격)
다음은 반드시 승인 필요:
- 데이터 포맷 변경
- 시스템 구조 변경
- 인터페이스 변경
- 제어 흐름 변경

---

# 2. 프로젝트 환경

## 사용 기술
- Python 3.12.3
- MATLAB / Simulink / Simscape
- Arduino
- PyTorch (가상센싱)
- GitHub

---

# 3. 리포 구조

docs/
├─ plans/
├─ daily_notes/
├─ templates/

simulation/
hardware/
control/
virtual_sensor/
data/
kinematics/
experiments/
cad/

---

# 4. 시스템 구조 (핵심 개념)

Target Trajectory
↓
Controller (Arduino)
↓
Real Robot
↓
Measured Data
↓
Virtual Sensor (AI / Model)
↓
Correction
↓
Controller Feedback

---

# 5. 인터페이스 계약 (Design by Contract)

## 5-A 역기구학
input:
(x, y, z)

output:
(theta1, theta2, theta3)

---

## 5-B 제어기
input:
target position / trajectory

output:
motor command

---

## 5-C 가상 센서
input:
- motor command
- measured motor angle
- simulation data

output:
- estimated position
- correction value

---

## 5-D 데이터 흐름
Simulation ↔ Real ↔ Virtual Sensor ↔ Control

---

# 6. 데이터 규칙 (매우 중요)

## 기본 포맷 (CSV)

time,
target_x, target_y, target_z,
motor1_cmd, motor2_cmd, motor3_cmd,
motor1_meas, motor2_meas, motor3_meas,
sim_x, sim_y, sim_z,
error_x, error_y, error_z

---

## 규칙
- time 컬럼 필수 (timestamp 의미)
- 컬럼 순서 고정
- 변경 시 Contract Change

---

# 7. 연구 수행 규칙 (Research Ops)

## 7-A 재현성
모든 실험에서 기록:
- 실행 커맨드
- 사용 데이터
- 파라미터
- 코드 버전

---

## 7-B 로그
- CSV + 텍스트 로그 필수
- 최소 하나는 로컬 저장

---

## 7-C 실험 비교
- 동일 조건 유지
- 변경 시 기록 필수

---

# 8. 코딩 규약

## 기본
- Python 3.12.3
- 타입힌트 사용
- config 분리
- 하드코딩 금지

---

## 금지
- global 변수 남용
- 의미 없는 변수명
- 단위 미표기

---

## 권장
- dataclass 사용
- 함수 단위 명확화

---

# 9. 변경 워크플로 (핵심)

## 9-A 작업 절차

1. 계획서 작성
2. 사용자 승인
3. 코드 수정
4. Daily Notes 기록

---

## 9-B 계획서 위치
docs/plans/

파일명:
YYYY-MM-DD_###_title.md

---

## 9-C 계획서 템플릿

위치: docs/templates/plan_template.md

```
# Plan

## Goal
## Files
## Changes
## Impact
## Risk
## Validation
```

---

## 9-D Daily Note 템플릿

위치: docs/templates/daily_note_template.md

# Daily Note

## Entry
- 무엇을:
- 왜:
- 어떻게:
- 결과:
- 다음:

---

# 10. BLOCKER 처리

다음 상황에서 즉시 보고해야 한다:
- 데이터 없음
- 선행 코드 없음
- 구조 불명확

형식:

[BLOCKER]  
문제:  
필요:  
대안:  

---

# 11. 금지 사항

- 승인 없이 코드 수정
- 데이터 구조 임의 변경
- 테스트 없는 기능 추가
- 기록 없는 작업

---

# 12. 권장 사항

- 최소 기능부터 구현
- 모든 변경 이유 기록
- 재현 가능성 확보

---

# 13. 핵심 원칙 요약

- 계획 없이 수정 금지
- 기록 없는 작업 금지
- 인터페이스 임의 변경 금지
- 재현 불가능한 실험 금지

---

# (부록) 템플릿

## Plan Template

    # Plan

    ## Goal
    (작업 목적)

    ## Files
    (수정/생성 파일 목록)

    ## Changes
    (구체적 변경 내용)

    ## Impact
    (영향 범위)

    ## Risk
    (리스크)

    ## Validation
    (검증 방법)

---

## Daily Note Template

    # Daily Note - YYYY-MM-DD

    ## Entry 001
    - 무엇을:
    - 왜:
    - 어떻게:
    - 결과:
    - 다음:

---

# END OF FILE
