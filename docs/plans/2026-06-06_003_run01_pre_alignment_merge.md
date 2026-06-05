# Plan

## Goal
Generate Run 01-pre pipeline-validation artifacts from the current raw main,
vision, and Simscape CSV files:
- angle-derived measured position CSVs
- processed merged datasets
- `error_x/y/z` labels in the fixed 16-column contract

These artifacts are for Run 01-pre end-to-end validation only, not final training
data quality judgment.

## Files
- Add `experiments/run01_preprocess.py`
- Create `data/real/derived/measured_position_<run_id>.csv`
- Create `data/processed/merged_<run_id>.csv`
- Update `docs/daily_notes/2026-06-06.md`

## Changes
- Implement a small preprocessing script that:
  - reads `data/real/raw/main_<run_id>.csv`
  - reads `data/vision/raw/vision_<run_id>.csv`
  - reads `data/simulation/raw/simscape_<run_id>.csv`
  - computes FK-based `measured_x/y/z_est` from `theta*_meas`
  - maps valid vision rows onto the main logger time axis by linear
    interpolation
  - merges main, Simscape, vision-derived XY, and angle-derived Z
  - writes the fixed final 16 columns
  - computes `error_x = measured_x_vision - sim_x`,
    `error_y = measured_y_vision - sim_y`,
    `error_z = measured_z_est - sim_z`

## Impact
- Does not change the public CSV contract.
- Does not change FK/IK interfaces.
- Adds processed artifacts under the already documented storage paths.
- Treats `theta*_meas` as `command_echo_no_encoder` because the current raw
  main logs do not contain real encoder measurements.

## Risk
- Vision timestamp alignment is provisional and only uses valid detected marker
  rows.
- Cross and square include marker misses, so merged row counts may be smaller
  than main row counts.
- `error_z` is based on FK from command-echo theta values, not independent
  measured Z ground truth.

## Validation
- Run the preprocessing script for the three Run 01-pre run IDs.
- Validate each merged CSV with `virtual_sensor/check_dataset.py`.
- Confirm final column order, row counts, monotonic timestamps, and no NaN.
