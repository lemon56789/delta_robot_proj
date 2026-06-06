# Plan

## Goal
Define run-level 3-fold cross-validation as the validation policy for the
initial Linear/Ridge virtual sensor baseline.

## Files
- `docs/plans/2026-06-06_012_run_level_three_fold_ridge_validation.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `virtual_sensor/README.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Use repetition IDs `r01`, `r02`, and `r03` as three validation folds.
- Keep complete runs together; do not randomly split adjacent CSV rows.
- For each fold, validate on the same repetition across all five Run 01-main
  trajectories and train on the other two repetitions.
- Select Ridge alpha using the mean validation performance across all three
  folds, with XY RMSE as the primary metric and XY MAE/max error as supporting
  metrics.
- Aggregate metrics by run/trajectory before the fold mean so trajectories with
  more rows do not dominate solely because of row count.
- Retrain one final model on all Run 01-main data after alpha and feature choices
  are fixed.
- Keep Run 01-holdout excluded from fitting, tuning, feature selection, and
  cross-validation.

## Impact
- Modeling and validation policy documentation only.
- No data contract or logger interface change.

## Risk
- Three folds estimate repeat-run variability but do not cover every possible
  workspace or hardware condition.
- Static rows can dominate training if they are not weighted or sampled
  appropriately.

## Validation
- Confirm fold definitions are explicit and run-level.
- Confirm the policy does not select one fold model as the final model.
- Confirm the final model is retrained on all Run 01-main data.
- Confirm holdout isolation remains explicit.
- Run `git diff --check`.
