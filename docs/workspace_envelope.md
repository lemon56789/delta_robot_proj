# Workspace Envelope Note

이 문서는 2026-05-08 기준 델타 로봇의 설치 높이와 `XY` 작업공간 관계를 정리한 설계 참고 문서다.
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
  - `wB = 24.051 mm`
  - `uP = 27.177 mm`
- current provisional / analysis angle range:
  - `-45 deg <= theta_i <= 90 deg`
- clearance definition:
  - `clearance_mm = H + z_mm`
  - `H` = `base origin -> ground`
  - `z_mm` = `base_frame` 기준 작업점 높이

## 3. Main Findings
### 3.1 Maximum `XY` Area Slice
- `XY` 가동 면적이 가장 넓은 수평 단면은 `z = -175 mm` 근처였다.
- 확인 절차:
  - coarse scan: `x,y=-250..250 mm`, `5 mm` grid, `z=-380..-40 mm`
  - refine scan: `z=-185..-165 mm`, `2 mm` grid, `1 mm` z step
  - final check: `z=-176/-175/-174 mm`, `1 mm` grid
- 최종 확인 결과:
  - best slice: `z = -175 mm`
  - reachable area: `142,774 mm^2`
  - extent: `x = -213..213 mm`, `y = -234..201 mm`

### 3.2 Interpretation
- `z = -175 mm`는 `XY` 면적 최대층이다.
- 이 층은 `pick/place 접근층`보다 `이송층` 또는 `넓은 범위 이동층`으로 보는 편이 자연스럽다.
- 바닥 가까운 pick 작업은 이보다 더 깊은 `z`에서 수행해야 하지만, 그에 따라 `XY` 면적은 줄어든다.

## 4. Area Ratio By Z
아래는 `z`별 `XY` 면적과 최대 대비 비율이다.

| z (mm) | Area (mm^2) | Ratio vs Max |
|---|---:|---:|
| `-240` | `106,868` | `74.88%` |
| `-235` | `110,204` | `77.21%` |
| `-230` | `113,580` | `79.58%` |
| `-225` | `116,760` | `81.81%` |
| `-220` | `119,860` | `83.98%` |
| `-215` | `122,828` | `86.06%` |
| `-210` | `125,756` | `88.11%` |
| `-205` | `128,508` | `90.04%` |
| `-200` | `131,196` | `91.92%` |
| `-195` | `133,724` | `93.69%` |
| `-190` | `136,196` | `95.42%` |
| `-185` | `138,492` | `97.03%` |
| `-180` | `140,652` | `98.55%` |
| `-175` | `142,774` | `100.00%` |

## 5. Recommended Installation Height
### 5.1 Candidate Comparison
`z=-175 mm`를 이송층, `z=-215..-235 mm`를 접근/픽층으로 보고 설치 높이를 비교하면 아래와 같다.

| H = base-ground | Clearance at z=-175 | Clearance at z=-215 | Clearance at z=-235 | Comment |
|---|---:|---:|---:|---|
| `235 mm` | `60 mm` | `20 mm` | `0 mm` | 낮다. 이송 여유와 바닥 여유가 부족하다. |
| `245 mm` | `70 mm` | `30 mm` | `10 mm` | 가능은 하지만 타이트하다. |
| `255 mm` | `80 mm` | `40 mm` | `20 mm` | 균형이 가장 좋다. |
| `265 mm` | `90 mm` | `50 mm` | `30 mm` | 이송 여유가 좋고 보수적이다. |
| `275 mm` | `100 mm` | `60 mm` | `40 mm` | 높다. 바닥 픽업보다 이송 위주에 가깝다. |
| `290 mm` | `115 mm` | `75 mm` | `55 mm` | 바닥면보다 떠 있는 tray/jig 작업에 유리하다. |

### 5.2 Practical Guidance
- 일반적인 pick-and-place:
  - 추천 설치 높이 `H = 255 mm`
- 이송 안정성, 간섭 여유를 더 두고 싶을 때:
  - 대안 `H = 265 mm`
- `H = 290 mm`:
  - 바닥 바로 위 작업공간은 줄지만, 바닥에서 떠 있는 작업면에서는 유리하다.
  - tray, jig, fixture가 바닥에서 어느 정도 떠 있는 경우에 적합하다.

## 6. `H = 290 mm` Workspace By Real Clearance
`H = 290 mm`이면 실제 ground plane은 `z = -290 mm`에 해당한다.
아래 표는 바닥 위 높이별 `XY` 단면을 정리한 것이다.

| Clearance Above Ground | base_frame z | Area (mm^2) | Ratio vs Max | x Range (mm) | y Range (mm) |
|---|---:|---:|---:|---:|---:|
| `0 mm` | `-290` | `67,907` | `47.56%` | `-148..148` | `-166..136` |
| `20 mm` | `-270` | `84,482` | `59.17%` | `-164..164` | `-184..153` |
| `40 mm` | `-250` | `99,747` | `69.86%` | `-178..178` | `-199..167` |
| `60 mm` | `-230` | `113,563` | `79.54%` | `-190..190` | `-211..179` |
| `80 mm` | `-210` | `125,710` | `88.05%` | `-200..200` | `-221..188` |
| `100 mm` | `-190` | `136,117` | `95.34%` | `-208..208` | `-229..197` |
| `115 mm` | `-175` | `142,774` | `100.00%` | `-213..213` | `-234..201` |

해석:
- `H = 290 mm`에서는 바닥면 자체의 `XY` 작업공간이 최대의 절반 이하로 줄어든다.
- 반면 바닥 위 `60..100 mm` 높이에서는 큰 작업공간을 확보할 수 있다.
- 따라서 `H = 290 mm`는 floor pick보다는 elevated work surface에 더 적합하다.

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
    for y in range(-250, 251, 5):
        for x in range(-250, 251, 5):
            if diagnose_delta_ik(x, y, z, theta_min_deg=-45, theta_max_deg=90).result is not None:
                ok += 1
    print(z, ok * 25)
PY
```

추가 refined check:
- `z=-185..-165 mm`, `2 mm` grid
- `z=-176/-175/-174 mm`, `1 mm` grid
- `H=290 mm`일 때 바닥 기준 단면은 `clearance = H + z`로 변환해 평가

## 9. Relation To Other Docs
- 좌표계 및 방향 기준: [system_data_flow.md](/home/lemon56789/delta_robot/docs/system_data_flow.md)
- nominal geometry 반영 상태: [roadmap.md](/home/lemon56789/delta_robot/docs/roadmap.md)
- 본 문서는 설치 높이와 workspace envelope 참고용 메모이며, 인터페이스 계약은 변경하지 않는다.
