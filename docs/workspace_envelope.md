# Workspace Envelope Note

이 문서는 2026-06-01 기준 델타 로봇의 설치 높이와 `XY` 작업공간 관계를 정리한 설계 참고 문서다.
좌표계와 nominal geometry는 현재 SoT인 [system_data_flow.md](/home/lemon56789/delta_robot/docs/system_data_flow.md)와 코드 상수에 맞춘다.

## 1. Scope
- 목적: `base origin -> ground` 설치 높이와 실제 작업면 높이에 따른 `XY` reachable area를 빠르게 판단한다.
- 범위: 현재 nominal geometry와 현재 코드 구현 기준의 workspace envelope 추정
- 비범위:
  - CSV 계약 변경
  - 인터페이스 변경
  - 최종 hardware-confirmed angle range 확정

중요:
- 현재 SoT 문서상 angle range는 `-45..90 deg`를 `hardware-safe provisional`과 `nominal-analysis`에 함께 사용한다.
- 다만 `hardware-confirmed` 범위는 아직 별도 확정되지 않았다.
- 따라서 아래 수치는 현재 프로젝트 기준의 설치 검토용 envelope reference이며, 추후 실제 조립 및 반복 구동 결과에 따라 hardware-confirmed 범위는 다시 조정될 수 있다.

## 2. Assumptions
- coordinate frame:
  - origin `O` = `base center`
  - workspace direction = `-z`
- geometry:
  - `L = 125.0 mm`
  - `l = 300.0 mm`
  - `wB = 46.0 mm`
  - `uP = 27.177 mm`
- current provisional / analysis angle range:
  - `-45 deg <= theta_i <= 90 deg`
- clearance definition:
  - `clearance_mm = H + z_mm`
  - `H` = `base origin -> ground`
  - `z_mm` = `base_frame` 기준 작업점 높이

## 3. Main Findings
### 3.1 Maximum `XY` Area Slice
- `XY` 가동 면적이 가장 넓은 수평 단면은 `z = -212 mm` 근처였다.
- 확인 절차:
  - coarse scan: `x,y=-400..400 mm`, `5 mm` grid, `z=-380..-40 mm`
  - refine scan: `z=-217..-210 mm`, `1 mm` grid
- 최종 확인 결과:
  - best checked slice: `z = -212 mm`
  - reachable area: `231,364 mm^2`
  - extent: `x = -270..270 mm`, `y = -277..268 mm`

### 3.2 Interpretation
- `z = -212 mm`는 `XY` 면적 최대층에 가깝다.
- 이 층은 `pick/place 접근층`보다 `이송층` 또는 `넓은 범위 이동층`으로 보는 편이 자연스럽다.
- 바닥 가까운 pick 작업은 이보다 더 깊은 `z`에서 수행해야 하지만, 그에 따라 `XY` 면적은 줄어든다.

## 4. Area Ratio By Z
아래는 `z`별 `XY` 면적과 최대 대비 비율이다.

| z (mm) | Area (mm^2) | Ratio vs Max |
|---|---:|---:|
| `-240` | `214,825` | `92.85%` |
| `-235` | `217,900` | `94.18%` |
| `-230` | `221,025` | `95.53%` |
| `-225` | `224,125` | `96.87%` |
| `-220` | `227,050` | `98.14%` |
| `-215` | `229,675` | `99.27%` |
| `-210` | `223,475` | `96.59%` |
| `-205` | `197,825` | `85.50%` |
| `-200` | `172,850` | `74.71%` |
| `-195` | `149,700` | `64.70%` |
| `-190` | `133,300` | `57.61%` |
| `-185` | `118,150` | `51.07%` |
| `-180` | `105,550` | `45.62%` |
| `-175` | `92,300` | `39.89%` |

## 5. Recommended Installation Height
### 5.1 Candidate Comparison
`z=-212 mm`를 이송층, `z=-250..-270 mm`를 접근/픽층으로 보고 설치 높이를 비교하면 아래와 같다.

| H = base-ground | Clearance at z=-212 | Clearance at z=-250 | Clearance at z=-270 | Comment |
|---|---:|---:|---:|---|
| `255 mm` | `43 mm` | `5 mm` | `-15 mm` | 낮다. 접근/픽층 여유가 부족하다. |
| `275 mm` | `63 mm` | `25 mm` | `5 mm` | 가능은 하지만 타이트하다. |
| `290 mm` | `78 mm` | `40 mm` | `20 mm` | 균형이 가장 좋다. |
| `310 mm` | `98 mm` | `60 mm` | `40 mm` | 이송 여유와 바닥 여유가 좋고 보수적이다. |
| `330 mm` | `118 mm` | `80 mm` | `60 mm` | 높다. 바닥 픽업보다 이송/fixture 작업에 가깝다. |

### 5.2 Practical Guidance
- 일반적인 pick-and-place:
  - 추천 설치 높이 `H = 290 mm`
- 이송 안정성, 간섭 여유를 더 두고 싶을 때:
  - 대안 `H = 310 mm`
- `H = 330 mm`:
  - 바닥 바로 위 작업공간보다 이송 또는 fixture 작업에 더 유리하다.
  - tray, jig, fixture가 바닥에서 어느 정도 떠 있는 경우에 적합하다.

## 6. `H = 290 mm` Workspace By Real Clearance
`H = 290 mm`이면 실제 ground plane은 `z = -290 mm`에 해당한다.
아래 표는 바닥 위 높이별 `XY` 단면을 정리한 것이다.

| Clearance Above Ground | base_frame z | Area (mm^2) | Ratio vs Max | x Range (mm) | y Range (mm) |
|---|---:|---:|---:|---:|---:|
| `0 mm` | `-290` | `173,225` | `74.87%` | `-230..230` | `-240..230` |
| `20 mm` | `-270` | `191,625` | `82.82%` | `-245..245` | `-250..240` |
| `40 mm` | `-250` | `207,525` | `89.69%` | `-255..255` | `-260..250` |
| `60 mm` | `-230` | `221,025` | `95.53%` | `-260..260` | `-270..260` |
| `80 mm` | `-210` | `223,475` | `96.59%` | `-270..270` | `-275..265` |
| `100 mm` | `-190` | `133,300` | `57.61%` | `-275..275` | `-280..270` |
| `115 mm` | `-175` | `92,300` | `39.89%` | `-275..275` | `-285..275` |

해석:
- `H = 290 mm`에서는 바닥면 자체도 최대 면적 대비 약 `75%` 수준의 `XY` 작업공간을 유지한다.
- 바닥 위 `40..80 mm` 높이에서 큰 작업공간을 확보할 수 있다.
- 바닥 위 `100 mm` 이상에서는 angle range 제약 때문에 면적이 다시 줄어든다.

## 7. Cautions
- 여기서 말하는 clearance는 platform 기준점 가정이다.
- 실제 그리퍼 팁이 platform보다 `d mm` 아래에 있으면 실제 팁 clearance는 `clearance_mm - d`가 된다.
- 따라서 실제 조립 설계 시에는:
  - gripper tip offset
  - suction cup length or finger length
  - workpiece height
  - tray/jig height
  - 동적 흔들림 여유
  를 추가로 반영해야 한다.

## 8. Reproducibility
아래 형태의 로컬 계산으로 본 문서 수치를 얻었다.

```bash
python - <<'PY'
from kinematics.inverse_kinematics import diagnose_delta_ik

# z slice별 XY reachable area count
for z in range(-380, -39, 5):
    ok = 0
    for y in range(-400, 401, 5):
        for x in range(-400, 401, 5):
            if diagnose_delta_ik(x, y, z, theta_min_deg=-45, theta_max_deg=90).result is not None:
                ok += 1
    print(z, ok * 25)
PY
```

추가 refined check:
- `z=-217..-210 mm`, `1 mm` grid
- refined check range: `x=-290..290 mm`, `y=-300..290 mm`
- `H=290 mm`일 때 바닥 기준 단면은 `clearance = H + z`로 변환해 평가

## 9. Relation To Other Docs
- 좌표계 및 방향 기준: [system_data_flow.md](/home/lemon56789/delta_robot/docs/system_data_flow.md)
- nominal geometry 반영 상태: [roadmap.md](/home/lemon56789/delta_robot/docs/roadmap.md)
- 본 문서는 설치 높이와 workspace envelope 참고용 메모이며, 인터페이스 계약은 변경하지 않는다.
