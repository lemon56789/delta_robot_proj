# Run 02 Failure Mode Table

## 목적

Run 02 결과를 전체 성공 또는 전체 실패로 단순화하지 않고,
trajectory-dependent effect와 실제 적용 단계의 한계를 발표용으로
분리한다. 아래 원인 해석은 기존 artifact에 근거한 진단이며 단일
인과관계를 새 하드웨어 실험으로 확정한 결과는 아니다.

## Trajectory별 결과와 Failure Mode

| Trajectory | 관측 결과 | 핵심 근거 | 주요 failure mode 또는 제한 | 발표용 해석 | 권장 figure |
|---|---|---|---|---|---|
| Cross `+/-30 mm` | 공식 절대 RMSE 악화, home 정규화 후에도 악화 | Absolute `5.600 -> 5.985 mm`, `-6.87%`, `1/3` 개선. Home-normalized `4.214 -> 5.172 mm`, `-22.75%`, `1/3` 개선. 실제 integer command 변화율 `11.1%` | **Actuator integer resolution.** Fractional correction이 실제 구분 가능한 integer servo command로 거의 이어지지 않음 | 모델 방향보다 actuator command 양자화가 correction 전달을 제한한 사례 | `run02_actuator_command_change_rate.png`, `run02_absolute_vs_home_normalized.png` |
| Reverse grid `3x3 +/-40 mm` | 공식 및 home 정규화 모두 `3/3` 개선 | Absolute `7.985 -> 7.066 mm`, `+11.50%`. Home-normalized `7.146 -> 6.902 mm`, `+3.42%`. Integer command 변화율 `45.5%` | **Home-offset sensitivity.** 개선은 반복 일관성이 있지만 home offset 제거 후 효과 크기가 감소 | 모델 기반 보정의 유효 사례지만 절대 개선의 일부는 초기 zero/home 차이에 의존 | `run02_rmse_by_trajectory.png`, `run02_absolute_vs_home_normalized.png` |
| Diamond `+/-35 mm` | 공식 및 home 정규화 모두 `3/3` 개선 | Absolute `5.641 -> 4.870 mm`, `+13.67%`. Home-normalized `4.868 -> 4.140 mm`, `+14.96%`. Integer command 변화율 `27.1%` | 뚜렷한 failure mode보다 **trajectory-specific successful case**. 다만 3 pair 범위의 결과 | Home offset 제거 전후에 모두 일관된 개선을 보여 모델 기반 보정의 가장 강한 유효 사례 | `run02_rmse_by_trajectory.png`, `run02_absolute_vs_home_normalized.png` |
| Circle `r=40 mm` | 공식 및 home 정규화 모두 `0/3`, tracking RMSE 악화 | Absolute `6.207 -> 7.767 mm`, `-25.14%`. Radial RMSE `3.319 -> 2.843 mm` 감소. Tangential RMSE `3.593 -> 4.442 mm` 증가. Phase lag `2.2 -> 361.7 ms` 증가 | **Static correction과 dynamic phase lag 분리 실패.** 정적 위치 오차를 줄이는 방향의 correction이 tangential/phase error를 키움 | Radial geometry는 개선됐지만 동적 tracking은 악화됐다. 모델이 정적 error와 동적 lag를 구분하지 못한 사례 | `run02_circle_error_decomposition.png`, `run02_improvement_by_trajectory.png` |

## System-Level Failure Modes

| Failure mode | Artifact 근거 | 영향 | 결론 범위 |
|---|---|---|---|
| Correction sign 오류 여부 | Predicted error와 OFF tracking error 방향 일치율 `95.6~100%`. Controller는 `target_xy - gain * predicted_error_xy` 적용 | Predicted error 반대 방향으로 target을 이동하므로 sign 자체는 정상 | 전체 악화를 sign 반전 오류로 설명하지 않음 |
| Integer servo command 양자화 | 실제 command 변화율: Cross `11.1%`, Reverse grid `45.5%`, Diamond `27.1%`, Circle `33.0%` | 작은 fractional theta correction이 `servo.write()` 이전 정수화에서 소실 | 특히 Cross failure의 주요 제한 |
| Home/zero 반복성 | Absolute 대비 home-normalized improvement 변화. 기존 진단의 pair별 최대 home shift: Cross `4.34 mm`, Reverse grid `2.80 mm`, Diamond `4.39 mm`, Circle `1.85 mm` | Correction 효과와 run 시작 위치 차이가 섞일 수 있음 | Reverse grid의 개선 크기는 조건부로 해석 |
| Dynamic phase lag | Circle phase lag OFF `2.2 ms`, ON `361.7 ms`; best shift ON 평균 `350 ms` | 시간축 기준 tracking RMSE와 tangential error 증가 | Circle에 static correction policy를 그대로 적용하기 어려움 |
| 전체 평균 상쇄 | Absolute 동일가중 `6.358 -> 6.422 mm`, `-1.01%`; home-normalized `5.429 -> 5.892 mm`, `-8.53%` | 개선 trajectory와 악화 trajectory가 전체 평균에서 상쇄 | 일괄 성공을 주장하지 않고 trajectory-dependent effect로 결론 |

## 발표 결론

- 전체 동일가중 평균은 개선되지 않았으므로 Run 02를 일괄 성공으로
  주장하지 않는다.
- Diamond와 Reverse grid는 모델 기반 보정의 유효 사례로 제시한다.
  Diamond는 absolute와 home-normalized 모두 `3/3` 개선으로 가장
  강하다.
- Cross는 correction sign 실패가 아니라 actuator integer resolution
  때문에 correction 전달률이 낮았던 사례로 설명한다.
- Circle은 radial error 감소와 tangential/phase lag 증가가 동시에
  나타났으므로 static correction과 dynamic lag를 분리하지 못한 사례로
  설명한다.
- 최종 결론은 **조건부 개선과 적용 한계 분석**이다.

## Source

- `experiments/results/run02_comparison_2026-06-07.json`
- `experiments/results/run02_reanalysis_2026-06-07.json`
- `experiments/results/run02_presentation_summary_2026-06-07.csv`
- `docs/daily_notes/2026-06-07.md` Entry 003
- `fulltext.md`
