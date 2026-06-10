# Run 01 발표용 요약

## 분석 범위

- 데이터 수집일 및 artifact 날짜: `2026-06-06`
- 학습 데이터: Run 01-main 15개 run, `5,158` rows
- 검증 방식: repetition 단위 run-level 3-fold cross-validation
- 최종 모델: standardized Ridge regression, `alpha=100`
- Complete holdout: 4개 trajectory, trajectory별 1개 run
- Partial diagnostic: Circle `r=40 mm` 1개 run
- 주 지표: `error_xy` prediction residual의 XY RMSE
- 출처:
  - `experiments/results/ridge_run01_main_cv_2026-06-06.json`
  - `experiments/results/ridge_run01_holdout_2026-06-06.json`
  - `experiments/results/ridge_run01_phase_analysis_2026-06-06.json`

Run 01의 수치는 correction을 실제 controller에 적용한 tracking 결과가
아니다. `error_xy`를 예측하지 않았을 때의 RMSE와 frozen Ridge 예측 후
남은 residual RMSE를 비교한 offline 예상치다.

```text
예상 RMSE 감소율 =
100 * (zero-prediction RMSE - Ridge residual RMSE)
      / zero-prediction RMSE
```

## 1. Complete Holdout 예상 RMSE 요약

| Trajectory | 오차 예측 없음 (mm) | Ridge 잔차 (mm) | 예상 감소율 | 개선 run |
|---|---:|---:|---:|---:|
| Static center | 5.1045 | 2.8878 | +43.43% | 1/1 |
| Cross `+/-30 mm` | 3.5065 | 2.9127 | +16.93% | 1/1 |
| Square `+/-30 mm` | 4.4961 | 2.8726 | +36.11% | 1/1 |
| Grid `3x3 +/-40 mm` | 5.0265 | 2.7196 | +45.89% | 1/1 |
| **동일가중 macro 평균** | **4.5334** | **2.8482** | **+37.17%** | **4/4** |

Complete holdout 네 run은 모두 Ridge residual RMSE가 감소했다. 가장 큰
예상 감소율은 Grid 45.89%, 가장 작은 감소율은 Cross 16.93%였다.

## 2. Main 3-Fold 검증 결과

| 항목 | 결과 |
|---|---:|
| Main run 수 | 15 |
| Main row 수 | 5,158 |
| 선택 alpha | 100 |
| Main OOF macro XY RMSE | 4.887 mm |

Main OOF RMSE는 repetition별 holdout fold에서 얻은 estimator prediction
residual의 run-macro 평균이다. 최종 모델은 alpha 선택 후 main 15개
전체로 다시 학습했다.

## 3. Row-Weighted Phase 진단

| 분석 구간 | 오차 예측 없음 (mm) | Ridge 잔차 (mm) | 예상 감소율 |
|---|---:|---:|---:|
| Complete holdout 전체 | 4.597 | 2.837 | +38.30% |
| Phase interior | 4.502 | 2.628 | +41.63% |
| Phase 마지막 0.5 s | 4.245 | 2.444 | +42.43% |

Row-weighted 분석에서도 전체적으로 residual이 감소했다. 큰 잔차는 주로
phase 시작 transient에 남아 있었으며 Grid와 Square는
transition-sensitive로 분류됐다.

## 4. Partial Circle 진단

| Trajectory | 오차 예측 없음 (mm) | Ridge 잔차 (mm) | 예상 감소율 | 상태 |
|---|---:|---:|---:|---|
| Circle `r=40 mm` | 6.6649 | 7.8720 | -18.11% | partial diagnostic |

Circle은 전체 궤적과 home return coverage가 완전하지 않아 complete
holdout macro 평균에서 제외했다. 관측된 partial 구간에서는 Ridge
residual이 증가했으므로 원운동 일반화에 한계가 있음을 시사한다.

## 5. Run 02와의 관계

| 구분 | Run 01 | Run 02 |
|---|---|---|
| 평가 대상 | Offline error estimator | 실제 correction OFF/ON tracking |
| 비교값 | Zero prediction 대 Ridge residual | 실제 OFF 대 실제 ON |
| 주요 전체 결과 | Complete holdout 예상 37.17% 감소 | 절대 RMSE 동일가중 1.01% 악화 |
| 해석 | 모델이 기존 오차를 설명할 가능성 | actuator와 동역학을 포함한 실제 효과 |

Run 01의 37.17%는 모델이 holdout error label을 예측한 결과이며, correction
gain, actuator 정수 명령화, backlash, home drift와 phase lag는 포함하지
않는다. 따라서 이는 Run 02에서 기대한 개선 가능성의 근거이지 실제
하드웨어 개선율 보장은 아니다.

## 6. 발표용 해석

- **Offline 모델 가능성:** Complete holdout macro XY RMSE가
  4.533 mm에서 2.848 mm로 감소해 37.17%의 예상 residual 감소를 보였다.
- **Trajectory별 차이:** Grid, Static, Square는 36.11~45.89% 감소했지만
  Cross는 16.93%로 상대적으로 작았다.
- **Circle 일반화 한계:** Partial Circle은 18.11% 악화돼 원운동과 동적
  phase 특성이 학습된 step/static trajectory와 다름을 보여줬다.
- **해석 제한:** Holdout alignment 결함을 수정한 뒤 재평가한
  retrospective 결과이며 trajectory별 complete holdout은 1개 run뿐이다.
- **Run 02 차이의 원인:** Run 01은 estimator residual만 평가했지만 Run
  02는 integer actuator command, 기구 반복성, home offset 및 동적 lag가
  포함된 실제 시스템 평가였다.

## 결론

Run 01에서는 frozen Ridge가 complete holdout error를 설명할 경우 XY
RMSE가 평균 37.17% 감소할 것으로 예상됐다. 그러나 이 수치는 offline
prediction residual 감소이며 실제 위치 보정 성능이 아니다. Run 02
결과와 함께 제시할 때는 “모델 자체는 오차 예측 가능성을 보였지만,
실제 하드웨어 적용에서는 actuator 해상도와 trajectory별 동역학 때문에
동일한 개선이 재현되지 않았다”는 결론이 적절하다.
