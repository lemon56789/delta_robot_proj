# Plan

## Goal
Document the initial virtual sensor learning method as a simple linear
regression/Ridge baseline instead of a PyTorch neural network.

## Files
- `docs/plans/2026-06-06_004_linear_ridge_virtual_sensor_baseline.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/roadmap.md`
- `virtual_sensor/README.md`
- `README.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Add the Stage 8 initial modeling policy:
  - primary model: linear regression or Ridge regression
  - target: `error_x`, `error_y`, `error_z`
  - default features: current `virtual_sensor.dataset.FEATURE_COLUMNS`
  - PyTorch neural network: optional future extension only
- Clarify validation/holdout usage:
  - validation can tune Ridge alpha
  - holdout must not be used for fitting or tuning
- Clarify evaluation metrics:
  - `error_x/y` are the primary measured XY labels
  - `error_z` remains secondary/diagnostic when based on angle-derived Z
- Mark PyTorch as a future optional path rather than the first required
  implementation.

## Impact
- No CSV contract change.
- No code/interface change.
- Makes the project feasible under current time constraints by prioritizing an
  explainable baseline model.

## Risk
- Linear/Ridge may underfit nonlinear hardware behavior.
- If hardware error is strongly trajectory-dependent, a later nonlinear model
  may still be needed.

## Validation
- Check that documentation no longer implies PyTorch is required for the first
  virtual sensor baseline.
- Check that Run 01-main/holdout split rules remain unchanged.
