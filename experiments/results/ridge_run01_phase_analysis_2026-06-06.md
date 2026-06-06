# Ridge Run 01 Phase Error Analysis

## Summary
- Holdout zero-prediction XY RMSE: `4.597 mm`
- Holdout Ridge XY RMSE: `2.837 mm`
- Holdout row-weighted improvement: `38.30%`
- Holdout interior XY RMSE: `4.502 -> 2.628 mm` (`41.63%`)
- Holdout final 0.5 s XY RMSE: `4.245 -> 2.444 mm`

## Trajectory Diagnosis

| Trajectory | Improvement | Interior RMSE | Final 0.5 s RMSE | Diagnosis |
|---|---:|---:|---:|---|
| cross_pm30 | 16.93% | 2.887 mm | 2.699 mm | persistent_model_limitation |
| grid_3x3_pm40 | 45.89% | 2.236 mm | 2.157 mm | transition_sensitive |
| square_pm30 | 36.11% | 2.504 mm | 2.438 mm | transition_sensitive |
| static_center_hold | 43.43% | 2.885 mm | 2.971 mm | mixed_or_moderate_improvement |

## Worst Holdout Rows

| Run | Phase | Age | Baseline | Ridge | Change |
|---|---|---:|---:|---:|---:|
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | x_minus_y_plus | 0 ms | 22.172 mm | 21.001 mm | -1.171 mm |
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | x_minus_y_center | 0 ms | 18.714 mm | 18.049 mm | -0.665 mm |
| 2026-06-06_run01_holdout_square_pm30_r01 | q1_x_plus_y_plus_2 | 0 ms | 9.589 mm | 11.780 mm | +2.192 mm |
| 2026-06-06_run01_holdout_square_pm30_r01 | q3_x_minus_y_minus | 0 ms | 13.041 mm | 11.455 mm | -1.586 mm |
| 2026-06-06_run01_holdout_square_pm30_r01 | q2_x_minus_y_plus | 0 ms | 13.323 mm | 10.573 mm | -2.750 mm |
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | x_minus_y_minus | 0 ms | 11.999 mm | 9.114 mm | -2.885 mm |
| 2026-06-06_run01_holdout_square_pm30_r01 | q4_x_plus_y_minus | 0 ms | 8.957 mm | 9.108 mm | +0.151 mm |
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | x_plus_y_plus | 0 ms | 5.041 mm | 7.854 mm | +2.813 mm |
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | x_plus_y_minus | 0 ms | 6.429 mm | 7.067 mm | +0.638 mm |
| 2026-06-06_run01_holdout_grid_3x3_pm40_r01 | home_2 | 0 ms | 9.689 mm | 7.017 mm | -2.672 mm |

## Interpretation Rule

- `transition_sensitive`: early-window RMSE exceeds settled RMSE by 50%.
- `phase_end_alignment_sensitive`: final 0.5 s RMSE exceeds interior by 50%.
- `persistent_model_limitation`: improvement is below 5% or a phase is harmed.
- Holdout findings remain diagnostic and are not used to tune the model.
- Correct phase-boundary alignment before changing model capacity.
