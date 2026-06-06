# Plan

## Goal
Align the Run 01 protocol and PC-side logger with the actual `pm40` training
data collection and use `pm30` for cross/square holdout evaluation.

## Files
- `docs/plans/2026-06-06_010_align_main_pm40_holdout_pm30.md`
- `experiments/run01_main_logger.py`
- `experiments/README.md`
- `experiments/run01_main_logger_computer2_powershell.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Add `cross_pm40` and `square_pm40` as Run 01-main trajectory names.
- Add five explicit Run 01-holdout trajectory names:
  - `static_center_holdout`
  - `cross_pm30_holdout`
  - `square_pm30_holdout`
  - `circle_r40_holdout`
  - `grid_3x3_pm40_holdout`
- Keep the older `pm20` main and `pm15` holdout CLI choices for compatibility,
  but stop using them as the current Run 01 protocol.
- Update the Run 01 protocol to record that the completed main dataset used
  `pm40` cross/square trajectories.
- Update holdout run IDs and Computer 2 execution examples to use `pm30`.

## Impact
- PC-side logger trajectory choices and experiment documentation change.
- Arduino serial protocol and raw/processed CSV contracts do not change.
- Existing main and vision data files are not renamed or modified.

## Risk
- Holdout `pm30` is inside the `pm40` training range, so it tests independent-run
  generalization at a different amplitude, not extrapolation outside the
  training workspace.
- Static and grid holdout runs must remain excluded from fitting and tuning.

## Validation
- Run `python -m py_compile experiments/run01_main_logger.py`.
- Dry-run all five current holdout trajectories.
- Verify the cross/square holdout targets use exactly `+/-30 mm`.
- Run `git diff --check`.
