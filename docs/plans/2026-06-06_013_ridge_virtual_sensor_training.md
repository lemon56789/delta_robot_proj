# Plan

## Goal
Implement and execute the first virtual sensor baseline using standardized
Linear/Ridge regression, run-level 3-fold cross-validation, final retraining on
all Run 01-main data, and isolated Run 01-holdout evaluation.

## Files
- `docs/plans/2026-06-06_013_ridge_virtual_sensor_training.md`
- `virtual_sensor/train_ridge.py`
- `virtual_sensor/evaluate_ridge.py`
- `virtual_sensor/ridge_model.py`
- `virtual_sensor/README.md`
- `experiments/run01_preprocess.py`
- `data/real/derived/measured_position_2026-06-06_run01_holdout_*.csv`
- `data/processed/merged_2026-06-06_run01_holdout_*.csv`
- `data/processed/alignment_2026-06-06_run01_holdout_*.json`
- `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`
- `experiments/results/ridge_run01_main_cv_2026-06-06.json`
- `experiments/results/ridge_run01_holdout_2026-06-06.json`
- `docs/daily_notes/2026-06-06.md`

## Changes
1. Dataset discovery and grouping
   - Load the 15 processed Run 01-main CSVs from
     `data/processed/merged_2026-06-06_run01_main_*.csv`.
   - Extract trajectory and repetition IDs from each run ID.
   - Keep every complete run together; never randomly split adjacent rows.
   - Use the fixed feature columns:
     - `theta1_cmd`, `theta2_cmd`, `theta3_cmd`
     - `theta1_meas`, `theta2_meas`, `theta3_meas`
     - `sim_x`, `sim_y`, `sim_z`
   - Use `error_x`, `error_y`, `error_z` as model targets, while treating
     `error_x/y` as primary and `error_z` as diagnostic.

2. Run-level 3-fold validation
   - Fold 1: validate on all `r01` main runs; train on `r02+r03`.
   - Fold 2: validate on all `r02` main runs; train on `r01+r03`.
   - Fold 3: validate on all `r03` main runs; train on `r01+r02`.
   - Fit feature standardization using only each fold's training rows.
   - Apply the training mean/scale to that fold's validation rows.
   - Test a deterministic, documented alpha grid spanning weak to strong
     regularization.
   - Compute per-run and per-trajectory metrics before fold aggregation so runs
     with more rows do not dominate alpha selection.

3. Metrics and alpha selection
   - Primary selection metric: mean XY RMSE across runs and all three folds.
   - Supporting metrics:
     - X/Y RMSE
     - XY Euclidean RMSE
     - X/Y MAE
     - XY Euclidean MAE
     - XY maximum Euclidean error
     - diagnostic Z RMSE/MAE
   - Select the alpha with the lowest mean XY RMSE.
   - Use a deterministic tie-break: lower mean XY MAE, then smaller alpha.
   - Save every alpha/fold/run result and the selected alpha to the CV report.

4. Final model
   - Refit the feature scaler on all 15 Run 01-main datasets.
   - Retrain one final Ridge model on all Run 01-main rows using the selected
     alpha.
   - Save a portable NumPy `.npz` artifact containing coefficients, intercept,
     feature mean/scale, feature/target names, selected alpha, and training run
     IDs.
   - Do not select or ship one of the three fold models as the final model.

5. Holdout preprocessing and evaluation
   - Generate derived, merged, and alignment files for the five Run 01-holdout
     runs using the same preprocessing policy as Run 01-main.
   - If the circle Simscape input is not yet available, evaluate the four
     complete holdouts first and label that report
     `preliminary_complete_only`.
   - Re-run the same evaluator after circle preprocessing; the report then
     becomes `final_with_partial_circle`.
   - Evaluate the final frozen model on:
     - `static_center_holdout`
     - `cross_pm30_holdout`
     - `square_pm30_holdout`
     - `grid_3x3_pm40_holdout`
   - Treat `circle_r40_holdout_r01` as partial/diagnostic only because its final
     circle and home-return vision coverage is incomplete.
   - For the partial circle, use only the valid observed circle interval and
     clearly label its metrics as non-final.
   - Do not use any holdout result to change alpha, features, scaling, or model
     fitting.

6. Reproducibility and reporting
   - Record exact input run IDs, row counts, alpha grid, selected alpha, feature
     columns, target columns, commands, and code version when available.
   - Write machine-readable JSON reports for CV and holdout evaluation.
   - Update `virtual_sensor/README.md` with execution commands and artifact
     paths.
   - Record all changes and outcomes in the daily note.

## Impact
- Adds the first trained virtual sensor model and its reproducible evaluation
  workflow.
- Does not change the fixed 16-column processed CSV contract.
- Does not change Arduino firmware, hardware control, or correction feedback.
- Produces an offline error estimator only; applying correction in Run 02 is a
  separate approved task.

## Risk
- `theta*_meas` is still `command_echo_no_encoder`, so motor measurement
  features do not contain independent encoder information.
- `error_z` is derived from command-echo FK and must not be presented as
  external 3D ground-truth performance.
- Static data can dominate row-weighted fitting. Inspect trajectory-level
  metrics and, if necessary, define an explicit run/trajectory weighting policy
  before changing the baseline.
- Phase/motion alignment has frame-level uncertainty that can inflate errors
  near transitions.
- The partial circle holdout is unsuitable as the sole final circle comparison
  baseline.
- If an additional Python dependency is required, installation needs separate
  approval; prefer the existing NumPy-based environment where practical.

## Validation
- Confirm all 15 main merged datasets load with the fixed feature/target schema,
  finite values, and monotonic timestamps.
- Confirm every validation run ID is absent from its fold's training run IDs.
- Confirm scalers are fitted only on fold training data.
- Confirm all alpha candidates produce finite fold metrics.
- Confirm alpha selection is reproducible across repeated executions.
- Confirm the final model artifact reproduces in-memory predictions within
  floating-point tolerance after reload.
- Confirm holdout run IDs are absent from all fitting and tuning records.
- Confirm normal holdout reports cover four complete runs and label circle as
  partial/diagnostic.
- Run `git diff --check`.

## Execution Order
1. Inspect available numerical dependencies and existing dataset helpers.
2. Implement reusable Ridge/scaler/model serialization logic.
3. Implement run discovery, 3-fold CV, metric aggregation, and final training.
4. Extend/execute holdout preprocessing without changing raw data.
5. Implement frozen-model holdout evaluation.
6. Run CV and select alpha.
7. Retrain and save the final model.
8. Evaluate complete holdouts and the partial circle separately.
9. Verify artifacts and document the results.

## Execution Status
- The original results below were superseded by the phase-boundary
  realignment and retraining in plan 015.
- Completed: NumPy Ridge/scaler/model serialization, run-level 3-fold CV,
  alpha selection, final retraining, model artifact, CV JSON report, reload and
  deterministic repeat validation.
- Selected result: `alpha=1`, Run 01-main run-macro mean XY RMSE
  `10.007230 mm`.
- Completed for holdout policy: frozen-model evaluator and partial-circle
  observed angular coverage alignment.
- Four complete holdout Simscape inputs are now available. Their preliminary
  evaluation is complete with status `preliminary_complete_only`.
- Preliminary complete-run macro XY RMSE changed from `11.945516 mm` with zero
  correction prediction to `11.033113 mm` with the frozen Ridge model, a
  `7.638%` improvement.
- Circle evaluation remains pending and must be added with the same frozen
  model; no retraining or tuning is allowed.
- Current post-plan-015 model uses `alpha=100`; see
  `2026-06-06_015_phase_boundary_realignment_retrain.md`.
