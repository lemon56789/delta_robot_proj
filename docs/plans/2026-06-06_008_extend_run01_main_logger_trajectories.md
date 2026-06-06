# Plan

## Goal
Extend the Run 01 PC-side main logger so it can execute Run 01-main and
Run 01-holdout trajectories with the updated circle and grid definitions.

## Files
- `docs/plans/2026-06-06_008_extend_run01_main_logger_trajectories.md`
- `experiments/run01_main_logger.py`
- `experiments/README.md`
- `experiments/run01_main_logger_computer2_powershell.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Keep the existing Arduino serial command protocol: `ALL theta1 theta2 theta3`.
- Keep the existing raw main CSV fields so `experiments/run01_preprocess.py`
  remains compatible.
- Add Run 01-main trajectories:
  - `static_center_hold`
  - `cross_pm20`
  - `square_pm20`
  - `circle_r40`
  - `grid_3x3_pm40`
- Add Run 01-holdout trajectories:
  - `cross_pm15_holdout`
  - `square_pm15_holdout`
  - `circle_r40_holdout`
- Define `circle_r40` as home -> `(40, 0)` -> counterclockwise radius `40 mm`
  circle -> home.
- Define `grid_3x3_pm40` as home -> `(-40, -40)` -> `(0, -40)` ->
  `(40, -40)` -> `(-40, 0)` -> `(0, 0)` -> `(40, 0)` ->
  `(-40, 40)` -> `(0, 40)` -> `(40, 40)` -> home.
- Add CLI options for circle point count and circle revolution duration.
- Update Run 01 documentation and the Computer 2 PowerShell guide with the new
  trajectory names and execution notes.

## Impact
- Code change is limited to the PC-side experiment logger.
- No Arduino firmware change.
- No processed CSV contract change.
- Run 01 trajectory naming changes from the previous `circle_r15` and
  `grid_3x3_pm20` draft to `circle_r40` and `grid_3x3_pm40`.

## Risk
- Circle timing is not finalized, so the logger exposes a configurable
  `--circle-duration-s` value and records it in metadata.
- The logger can only send discrete serial setpoints. A slow continuous circle
  is approximated by many small point commands unless the Arduino firmware later
  adds trajectory streaming/interpolation.
- `theta*_meas` remains `command_echo_no_encoder`, not actual encoder feedback.

## Validation
- Run `python -m py_compile experiments/run01_main_logger.py`.
- Run `--dry-run` for representative main and holdout trajectories.
- Confirm generated CSV files have rows and expected headers.
- Run `git diff --check`.
