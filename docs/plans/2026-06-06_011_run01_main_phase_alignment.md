# Plan

## Goal
Replace the provisional first-timestamp vision alignment with trajectory-aware
alignment for the 15 completed Run 01-main runs, then generate measured-position
and merged training datasets.

## Files
- `docs/plans/2026-06-06_011_run01_main_phase_alignment.md`
- `experiments/run01_preprocess.py`
- `docs/measured_data_structure.md`
- `data/real/derived/measured_position_2026-06-06_run01_main_*.csv`
- `data/processed/merged_2026-06-06_run01_main_*.csv`
- `data/processed/alignment_2026-06-06_run01_main_*.json`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Resolve both the contract Simscape filename `simscape_<run_id>.csv` and the
  current exported filename `simscape_2026-06-06_run01_simscape_<suffix>.csv`.
- Verify that Simscape rows use the same timestamp axis as the main log.
- Align cross, square, and grid runs using corresponding internal phase
  boundaries while excluding the leading and trailing home phases as anchors.
- Align circle runs using the first and last vision samples whose distance from
  the initial home position exceeds `10 mm`.
- Align static runs by mapping the full vision duration to the full main
  duration.
- Write one alignment sidecar JSON per run containing the method, source file,
  anchors, valid-row counts, and merged-row counts.

## Impact
- Changes Run 01 post-processing alignment behavior.
- Keeps the fixed 16-column processed CSV contract unchanged.
- Does not modify raw main, vision, or Simscape data.

## Risk
- Vision phase labels were entered independently from the PC logger, so phase
  boundaries have frame-level timing uncertainty.
- Circle motion detection uses a `10 mm` threshold and assumes the run starts
  near home.
- Current `theta*_meas` remains command echo, so `error_z` is diagnostic only.

## Validation
- Process all 15 Run 01-main runs.
- Confirm Simscape/main timestamps match exactly.
- Confirm every merged CSV has the fixed 16 columns, monotonic time, and no NaN.
- Check aligned vision coverage and phase-level median positions.
- Run `virtual_sensor/check_dataset.py` for all generated merged CSVs.
- Run `git diff --check`.
