# Run 02 Presentation Numbers Check

## 검증 범위

- 새 하드웨어 실험: 없음
- 공식 OFF/ON pair: `12`
- Run 02 merged CSV: `24`
- 발표 summary CSV data row: `10`
- 검증한 presentation PNG: `5`
- Raw/processed CSV schema 및 기존 run ID 변경: 없음

## 1. Trajectory Summary 대조

아래 값은
`experiments/results/run02_reanalysis_2026-06-07.json`과
`experiments/results/run02_presentation_summary_2026-06-07.csv`를
대조한 결과다.

### Official Absolute RMSE

| Trajectory | OFF mean (mm) | ON mean (mm) | Mean-based improvement | Improved pairs | 검증 |
|---|---:|---:|---:|---:|---|
| Cross | 5.600339 | 5.985360 | -6.874970% | 1/3 | PASS |
| Reverse grid | 7.984567 | 7.066310 | +11.500402% | 3/3 | PASS |
| Diamond | 5.641018 | 4.870165 | +13.665144% | 3/3 | PASS |
| Circle | 6.206851 | 7.767023 | -25.136287% | 0/3 | PASS |
| **동일가중 전체** | **6.358194** | **6.422214** | **-1.006902%** | **7/12 pair, 2/4 trajectory** | **PASS** |

### Home-Normalized RMSE

| Trajectory | OFF mean (mm) | ON mean (mm) | Mean-based improvement | Improved pairs | 검증 |
|---|---:|---:|---:|---:|---|
| Cross | 4.213837 | 5.172491 | -22.750124% | 1/3 | PASS |
| Reverse grid | 7.146115 | 6.901933 | +3.416990% | 3/3 | PASS |
| Diamond | 4.868019 | 4.139853 | +14.958173% | 3/3 | PASS |
| Circle | 5.486398 | 7.352748 | -34.017761% | 0/3 | PASS |
| **동일가중 전체** | **5.428593** | **5.891756** | **-8.531927%** | **7/12 pair, 2/4 trajectory** | **PASS** |

## 2. Improvement Percent 정의 확인

발표 summary와 figure는 다음 mean-based 정의를 사용한다.

```text
100 * (OFF mean - ON mean) / OFF mean
```

기존 comparison JSON의 `improvement_percent_mean`은 세 pair의 개별
percent를 산술평균한 값이므로 수치가 다르다.

| Trajectory | 발표 mean-based | Comparison pair-percent mean | 차이 원인 |
|---|---:|---:|---|
| Cross | -6.87% | -7.73% | 계산 정의 차이 |
| Reverse grid | +11.50% | +11.05% | 계산 정의 차이 |
| Diamond | +13.67% | +13.67% | 반올림하면 거의 동일 |
| Circle | -25.14% | -25.41% | 계산 정의 차이 |

**판정:** source 불일치가 아니라 aggregate 계산 정의 차이다. 발표 내에서는
mean-based percent로 통일한다.

## 3. Diagnostic Numbers 대조

| 항목 | 발표 수치 | Primary source | 검증 |
|---|---|---|---|
| Cross actual integer command change | `11.1%` | Reanalysis JSON `0.111111...` | PASS |
| Reverse grid actual integer command change | `45.5%` | Reanalysis JSON `0.454545...` | PASS |
| Diamond actual integer command change | `27.1%` | Reanalysis JSON `0.271428...` | PASS |
| Circle actual integer command change | `33.0%` | Reanalysis JSON `0.33` | PASS |
| Circle radial RMSE | `3.319 -> 2.843 mm` | Reanalysis JSON | PASS |
| Circle tangential RMSE | `3.593 -> 4.442 mm` | Reanalysis JSON | PASS |
| Circle phase lag | `2.2 -> 361.7 ms` | Reanalysis JSON | PASS |
| Circle best shift mean | OFF `33.3 ms`, ON `350 ms` | Reanalysis JSON | PASS |

## 4. Correction Sign 근거 확인

- 기록값: predicted error와 OFF tracking error 방향 일치율
  `95.6~100%`.
- 적용식: `corrected_target_xy = target_xy - gain * predicted_error_xy`.
- 해석: predicted error의 반대 방향으로 target을 이동하므로 correction
  sign 자체는 정상으로 판단한다.
- Source:
  - `docs/daily_notes/2026-06-07.md` Entry 003
  - `fulltext.md`
  - 적용식은
    `experiments/results/run02_correction_offline_validation_2026-06-06.json`
    및 Run 02 protocol에 기록

**Source limitation:** `95.6~100%`의 trajectory/pair별 상세 배열은
comparison 또는 reanalysis JSON에 저장돼 있지 않다. 현재 repository의
공식 근거는 당시 읽기 전용 진단 후 작성한 Daily Note와 fulltext
요약이다. 따라서 이 값은 발표에서 범위로 인용할 수 있지만 다른
machine-readable 지표와 같은 수준의 자동 재계산 결과로 표현하지 않는다.

## 5. Figure 대조

| Figure | 포함 수치 | 권장 슬라이드 | 상태 |
|---|---|---|---|
| `run02_rmse_by_trajectory.png` | Trajectory별 official OFF/ON mean | Run 02 핵심 결과 | PASS |
| `run02_improvement_by_trajectory.png` | Official improvement, 0% 기준선 | 개선/악화 trajectory 구분 | PASS |
| `run02_absolute_vs_home_normalized.png` | Absolute 대 home-normalized improvement | Home offset 영향 및 Diamond 일관성 | PASS |
| `run02_actuator_command_change_rate.png` | `11.1%, 45.5%, 27.1%, 33.0%` | Cross actuator resolution 한계 | PASS |
| `run02_circle_error_decomposition.png` | Radial/tangential RMSE와 phase lag | Circle failure mode 분석 | PASS |

## 6. Source Path 확인

| 경로 | 상태 |
|---|---|
| `experiments/results/run02_comparison_2026-06-07.json` | 존재 |
| `experiments/results/run02_reanalysis_2026-06-07.json` | 존재 |
| `experiments/results/run02_presentation_summary_2026-06-07.md` | 존재 |
| `experiments/results/run02_presentation_summary_2026-06-07.csv` | 존재 |
| `data/processed/merged_*run02*.csv` | 24개 존재 |
| 필수 presentation PNG 5개 | 모두 존재 |

## 최종 판정

- Summary JSON/CSV/figure 사이의 핵심 수치 불일치: **없음**
- Source path 누락: **없음**
- 주의할 계산 정의: improvement percent 두 방식
- 재현성 제한이 있는 값: correction sign 방향 일치율 `95.6~100%`
- 발표 결론: 전체 평균 개선이 아닌 **trajectory-dependent conditional
  improvement와 failure mode 분석**
