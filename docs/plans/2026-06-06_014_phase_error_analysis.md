# Plan

## Goal
Analyze the existing frozen Ridge baseline by phase and time since phase start,
identify where the large grid/square errors occur, and distinguish likely
alignment-transition effects from persistent model error before changing
features or introducing a neural network.

## Files
- `docs/plans/2026-06-06_014_phase_error_analysis.md`
- `virtual_sensor/analyze_phase_errors.py`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.json`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.md`
- `virtual_sensor/README.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
1. Reconstruct out-of-fold predictions for all 15 Run 01-main runs using the
   selected alpha and the original `r01/r02/r03` fold policy.
2. Use the frozen final model for the four currently available complete
   holdouts. Do not refit, tune, or select features from holdout results.
3. Join each merged row to the corresponding raw main-log phase by exact
   timestamp. Fail if any merged timestamp cannot be mapped.
4. Compute zero-prediction baseline and Ridge metrics for:
   - each run
   - each phase
   - each trajectory/normalized phase category
   - phase-age windows `0-0.5 s`, `0.5-1.5 s`, and `1.5 s+`
   - phase-edge windows: first `0.5 s`, interior, and final `0.5 s`
5. Record the largest row-level XY residuals with run ID, phase, phase age,
   target, true error, prediction, and before/after residual.
6. Classify evidence conservatively:
   - error concentrated in the first `0.5 s`: likely transition/alignment or
     settling sensitivity
   - error concentrated in the final `0.5 s`, with vision already moving to
     the next setpoint: likely phase-boundary alignment contamination
   - error remaining after `1.5 s`: persistent model/data limitation
   - Ridge worse than zero prediction: harmful correction region
7. Produce machine-readable JSON and a concise Markdown diagnosis with the
   recommended next modeling step. Do not implement new features or an MLP in
   this task.

## Impact
- Adds offline diagnostic tooling and reports only.
- Does not change the 16-column processed CSV contract.
- Does not change the trained model, alpha, preprocessing outputs, controller,
  or Run 02 behavior.

## Risk
- Phase labels describe commanded setpoint intervals, not measured settling.
- Vision/main piecewise alignment can move apparent transition timing.
- `theta*_meas` remains command echo, so motor dynamics are not independently
  observed.
- Holdout findings are diagnostic only and must not be used for model tuning.

## Validation
- Confirm every analyzed merged row maps to one raw phase timestamp.
- Confirm main predictions are strictly out-of-fold.
- Confirm holdout run IDs are absent from fitting records.
- Confirm phase and phase-age row counts sum to each analyzed run row count.
- Confirm all metrics and worst-row records are finite.
- Re-run analysis and confirm deterministic output apart from command/version
  metadata.
- Run `git diff --check`.

## Execution Status
- The diagnostic values below describe the pre-plan-015 processed datasets.
- Completed for 15 Run 01-main OOF runs and four complete frozen holdouts.
- Holdout row-weighted XY RMSE improved `6.17%` overall.
- Excluding the first/final `0.5 s`, the interior holdout rows improved
  `16.00%` (`6.068 -> 5.097 mm`).
- Final `0.5 s` rows had `40.304 mm` Ridge XY RMSE versus `5.097 mm` in the
  interior.
- Raw vision inspection confirmed that several phase-labeled segments already
  move toward the next setpoint at their tail. The current piecewise alignment
  maps those samples into the current main phase.
- Next action: correct phase-boundary alignment and regenerate processed data
  before feature changes or MLP comparison.
- Plan 015 completed that action. The regenerated final `0.5 s` holdout Ridge
  RMSE is `2.444 mm`, down from `40.304 mm`.
