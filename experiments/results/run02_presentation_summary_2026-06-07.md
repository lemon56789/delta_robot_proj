# Run 02 발표용 요약

## 분석 범위

- 실제 실험일: `2026-06-07`
- artifact에서 유지한 Run ID 날짜: `2026-06-06`
- 데이터: 4개 trajectory, trajectory별 3회 반복, OFF/ON 총 12 pair
- 추가 하드웨어 실험: 없음
- 주 지표: `tracking_xy_rmse`
- 출처:
  - `experiments/results/run02_comparison_2026-06-07.json`
  - `experiments/results/run02_reanalysis_2026-06-07.json`

양의 개선율은 correction ON에서 RMSE가 감소했다는 뜻이다. 이 보고서의
개선율은 표에 표시된 평균값으로 다음과 같이 계산한다.

```text
100 * (OFF 평균 - ON 평균) / OFF 평균
```

공식 comparison JSON에는 세 pair의 개별 개선율을 산술평균한 값도
저장되어 있다. 이 값은 표시된 OFF/ON 평균으로 계산한 개선율과 정의가
다르므로 아래 표에는 사용하지 않는다.

## 1. 공식 절대 RMSE 요약

| Trajectory | OFF 평균 (mm) | ON 평균 (mm) | 개선율 | 개선 pair |
|---|---:|---:|---:|---:|
| Cross `+/-30 mm` | 5.6003 | 5.9854 | -6.87% | 1/3 |
| Reverse grid `3x3 +/-40 mm` | 7.9846 | 7.0663 | +11.50% | 3/3 |
| Diamond `+/-35 mm` | 5.6410 | 4.8702 | +13.67% | 3/3 |
| Circle `r=40 mm` | 6.2069 | 7.7670 | -25.14% | 0/3 |

공식 절대 RMSE는 Reverse grid와 Diamond에서 개선됐고 Cross와
Circle에서는 악화됐다. 전체 12개 OFF/ON pair 중 7개가 개선됐다.

## 2. Home 정규화 RMSE 요약

Home 정규화는 각 run의 초기 home 구간에서 계산한
`median(vision_xy - target_xy)` offset을 제거한다. 원점 및 home drift
영향을 확인하기 위한 진단값이며 절대 위치 정확도를 대체하지 않는다.

| Trajectory | OFF 평균 (mm) | ON 평균 (mm) | 개선율 | 개선 pair |
|---|---:|---:|---:|---:|
| Cross `+/-30 mm` | 4.2138 | 5.1725 | -22.75% | 1/3 |
| Reverse grid `3x3 +/-40 mm` | 7.1461 | 6.9019 | +3.42% | 3/3 |
| Diamond `+/-35 mm` | 4.8680 | 4.1399 | +14.96% | 3/3 |
| Circle `r=40 mm` | 5.4864 | 7.3527 | -34.02% | 0/3 |

Diamond는 home 정규화 후에도 세 pair가 모두 개선됐다. Reverse grid도
개선 pair 수는 유지됐지만 평균 개선율은 11.50%에서 3.42%로 감소했다.
따라서 절대 RMSE 개선의 일부는 초기 home offset에 의존한다.

## 3. Trajectory별 개선 Pair 수

| Trajectory | 공식 절대 RMSE | Home 정규화 RMSE |
|---|---:|---:|
| Cross `+/-30 mm` | 1/3 | 1/3 |
| Reverse grid `3x3 +/-40 mm` | 3/3 | 3/3 |
| Diamond `+/-35 mm` | 3/3 | 3/3 |
| Circle `r=40 mm` | 0/3 | 0/3 |
| **합계** | **7/12** | **7/12** |

## 4. 전체 Trajectory 동일가중 평균

각 trajectory 내부의 세 repetition을 먼저 평균한 뒤, 네 trajectory에
동일한 가중치를 적용했다.

| 분석 기준 | OFF 평균 (mm) | ON 평균 (mm) | 개선율 | 개선 trajectory |
|---|---:|---:|---:|---:|
| 공식 절대 RMSE | 6.3582 | 6.4222 | -1.01% | 2/4 |
| Home 정규화 RMSE | 5.4286 | 5.8918 | -8.53% | 2/4 |

전체 평균은 correction이 보편적으로 개선됐다는 결론을 지지하지 않는다.
Trajectory마다 서로 다른 현상이 나타났으므로 전체 평균은 보조 지표로만
제시한다.

## 5. 발표용 해석

- **Diamond: 일관된 개선.** 절대 RMSE는 13.67%, home 정규화 RMSE는
  14.96% 개선됐고 두 기준 모두 세 pair가 전부 개선됐다. 특정
  trajectory에서 correction이 유효했다는 가장 강한 근거다.
- **Reverse grid: 개선됐지만 일부는 home offset에 의존.** 세 pair가
  모두 개선됐지만 home 정규화 후 평균 개선율이 11.50%에서 3.42%로
  감소했다. Correction 효과와 초기 home 및 zero drift 영향을 완전히
  분리할 수 없다.
- **Cross: actuator 정수 명령 해상도 제한.** ON command event 중 실제
  추정 integer servo command가 달라진 비율은 11.1%였고, fractional
  command 기준 이론 변화율은 33.3%였다. 많은 correction이 구분 가능한
  actuator 명령으로 이어지지 않았으며 세 pair 중 한 pair만 개선됐다.
- **Circle: radial error는 감소했지만 tangential 및 phase lag는 증가.**
  Radial RMSE는 3.319 mm에서 2.843 mm로 감소했지만 tangential RMSE는
  3.593 mm에서 4.442 mm로 증가했다. 평균 equivalent phase lag도 약
  2.2 ms에서 361.7 ms로 증가했다. Correction이 radial geometry는
  개선했지만 tangential/phase error를 유발하거나 증폭해 공식 tracking
  RMSE는 세 pair 모두 악화됐다.

## 결론

Run 02는 trajectory와 무관한 보편적 정확도 향상을 입증하지 못했다.
발표에서 방어 가능한 결론은 trajectory별로 구분해야 한다. Diamond는
일관된 개선을 보였고, Reverse grid는 home offset을 제거하면 개선 폭이
작아졌다. Cross는 actuator 정수 명령 해상도의 제약을 받았으며,
Circle은 radial error 감소와 맞바꿔 tangential 및 phase lag error가
증가했다.
