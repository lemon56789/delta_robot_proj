# Plan

## Goal
Prepare the trajectory-independent part of Run 02 before the final trajectory
and Simscape files are fixed: implement a reusable XY correction engine, add a
serial-free replay workflow, and validate model interface, clamp, fallback,
and IK safety using the existing Run 01 datasets.

## Files
- `docs/plans/2026-06-06_017_run02_correction_engine_offline_validation.md`
- `virtual_sensor/correction_engine.py`
- `virtual_sensor/test_correction_engine.py`
- `experiments/run02_offline_validate.py`
- `experiments/results/run02_correction_offline_validation_2026-06-06.json`
- `virtual_sensor/README.md`
- `experiments/README.md`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/virtual_sensing_progress.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
1. Add a reusable correction engine that:
   - loads the frozen Ridge model through the existing `RidgeModel` API;
   - accepts model features in the artifact-defined order;
   - computes `target_correction_xy = -gain * predicted_error_xy`;
   - applies an XY vector-norm clamp while leaving Z correction disabled;
   - solves corrected-target IK with the shared `kinematics` module;
   - falls back to the nominal target and nominal theta command when prediction
     is invalid or corrected-target IK is rejected;
   - returns explicit prediction, requested/applied correction, clamp, fallback,
     corrected target, corrected theta, and status fields for logging.
2. Add a generic offline validation CLI that accepts one or more processed
   merged CSV files and candidate gain/clamp values without depending on a
   specific trajectory name.
3. Validate candidate configurations against:
   - Run 01-main data for prediction magnitude, clamp rate, and IK safety;
   - the four complete Run 01-holdout datasets for replay compatibility and IK
     safety only.
4. Do not optimize or select gain/clamp from holdout error metrics. The report
   may describe holdout prediction and safety distributions, but holdout labels
   must not be used to tune the correction configuration.
5. Add standard-library unit tests for correction sign, XY vector clamp, Z-off
   behavior, feature-order validation, invalid-prediction fallback, and IK
   fallback.
6. Record the correction-log field definitions and clarify that this phase
   does not send serial commands or modify Arduino firmware.

## Impact
- Adds the reusable PC-side computation needed before a Run 02 logger can send
  corrected `ALL theta1 theta2 theta3` commands.
- Does not add or change trajectories.
- Does not require new Simscape files.
- Does not change the fixed 16-column processed dataset contract, Arduino
  protocol, firmware, model coefficients, or Run 01 raw data.
- The correction log is a Run 02 auxiliary log, not a replacement for the
  processed merged dataset.

## Risk
- Existing `theta*_meas` values are command echoes, so this remains one-pass
  feedforward correction rather than encoder-based closed-loop feedback.
- Offline replay can verify numerical and workspace safety but cannot prove
  real hardware improvement.
- The current holdout is retrospective after alignment diagnosis. Using it to
  tune gain or clamp would further bias the next evaluation, so configuration
  selection must remain main-only and safety-oriented.
- A correction that passes pointwise IK may still move too aggressively on
  hardware. The later serial-enabled Run 02 phase still requires a low-gain
  staged hardware gate and operator stop conditions.

## Validation
- Run `python3 -m unittest virtual_sensor.test_correction_engine`.
- Run the offline validator twice and confirm deterministic JSON results.
- Confirm the frozen artifact feature/target names are accepted exactly and
  mismatched feature schemas are rejected.
- Confirm every applied XY correction is no larger than its configured clamp.
- Confirm Z target and Z correction remain unchanged/zero.
- Confirm corrected theta values stay within `-45 deg <= theta_i <= 90 deg`.
- Confirm every prediction or corrected-IK failure is logged and falls back to
  the nominal command.
- Confirm the validator reports Run 01-main and holdout separately and does not
  rank candidate configurations using holdout target errors.
- Run `git diff --check`.

## Approval Gate
- This plan authorizes only the common engine and offline validation phase.
- Serial transmission, final trajectory definitions, new Simscape generation,
  and physical Run 02 execution require a later approved plan or an explicit
  extension of this plan after the trajectory is fixed.

## Execution Status
- Implemented frozen-model inference, negative-error XY correction, vector
  clamp, Z-off, corrected-target IK, and nominal-command fallback.
- Added six unit tests for correction sign/Z-off, clamp, feature order,
  non-finite prediction fallback, inference exception fallback, and
  corrected-IK fallback.
- Replayed nine gain/clamp candidates over Run 01-main 15 runs / `5,158` rows
  and complete holdout 4 runs / `1,356` rows.
- All candidates had zero fallback, correction-limit violation, and
  theta-limit violation.
- Main-only provisional hardware start candidate:
  - gain `0.25`
  - XY vector clamp `2 mm`
  - main clamp rate `0.077549%`
  - holdout clamp rate `0%`
- Holdout `error_*` labels were not read or used for configuration selection.
- Physical serial execution remains outside this plan.
