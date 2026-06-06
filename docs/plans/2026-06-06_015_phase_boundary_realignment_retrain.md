# Plan

## Goal
Correct the non-circle phase-boundary alignment identified by plan 014,
regenerate Run 01-main and complete holdout processed datasets, retrain the
Ridge baseline, and compare the new frozen holdout result with the previous
`7.638%` macro improvement.

## Files
- `docs/plans/2026-06-06_015_phase_boundary_realignment_retrain.md`
- `experiments/run01_preprocess.py`
- `data/real/derived/measured_position_2026-06-06_run01_main_*.csv`
- `data/real/derived/measured_position_2026-06-06_run01_holdout_*.csv`
- `data/processed/merged_2026-06-06_run01_main_*.csv`
- `data/processed/merged_2026-06-06_run01_holdout_*.csv`
- `data/processed/alignment_2026-06-06_run01_main_*.json`
- `data/processed/alignment_2026-06-06_run01_holdout_*.json`
- `virtual_sensor/models/ridge_run01_main_2026-06-06.npz`
- `experiments/results/ridge_run01_main_cv_2026-06-06.json`
- `experiments/results/ridge_run01_holdout_2026-06-06.json`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.json`
- `experiments/results/ridge_run01_phase_analysis_2026-06-06.md`
- `virtual_sensor/README.md`
- `docs/measured_data_structure.md`
- `docs/plans/2026-06-06_013_ridge_virtual_sensor_training.md`
- `docs/plans/2026-06-06_014_phase_error_analysis.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
1. For cross, square, and grid vision phases, detect departure from the current
   stable position using a `5 mm` displacement threshold and consecutive valid
   samples.
   - If no departure sample exists inside a manually labeled phase, use that
     phase's final valid timestamp as the boundary edge; the transition is then
     represented by the gap to the next phase's first valid sample.
2. Map each detected departure event to the next main command-phase start.
   - Map the final stable sample before a detected departure to the current
     main phase end so an unobserved vision gap cannot spread motion across the
     stable hold interval.
3. Map the first valid sample of the newly labeled vision phase to the
   corresponding Simscape settle event, defined as the first sample within
   `3 mm` XY of that phase target.
4. Preserve the existing static and circle policies.
5. Regenerate all 15 Run 01-main datasets and the four available complete
   holdouts with the corrected event anchors.
6. Re-run the existing 3-fold Ridge CV, select alpha only from main OOF
   results, retrain the final model on all main rows, and evaluate the same four
   frozen holdouts.
7. Re-run phase analysis and compare:
   - previous macro holdout improvement `7.638%`
   - previous row-weighted holdout improvement `6.175%`
   - previous interior improvement `16.003%`
   - new values after realignment

## Impact
- Changes processed labels and alignment metadata, not the fixed 16-column CSV
  contract.
- Replaces the current model and reports because their training labels change.
- Does not change raw logs, Simscape input files, controller behavior, or Run 02
  interfaces.

## Risk
- The `5 mm` departure threshold and `3 mm` Simscape settle threshold are
  analysis policies and may need revision if event detection fails.
- Vision phase labels are manually timed and can still contain ambiguous
  samples.
- Holdout remains evaluation-only and must not influence alpha or thresholds;
  thresholds are fixed from the plan 014 main/holdout boundary diagnosis and
  applied uniformly.
- Because the existing holdout exposed the preprocessing defect, its
  post-realignment score is retrospective and is no longer a pristine final
  generalization estimate. Fresh Run 02 data is required for the next unbiased
  performance gate.

## Validation
- Confirm every non-circle run produces strictly increasing source and target
  anchors.
- Confirm departure anchors occur before the next vision phase start.
- Confirm main/Simscape time axes still match exactly.
- Confirm all regenerated CSVs retain the fixed schema, finite values, and
  strictly increasing timestamps.
- Confirm final `0.5 s` phase error falls substantially relative to the prior
  `40.304 mm` Ridge RMSE.
- Confirm main OOF and holdout fitting isolation.
- Confirm model reload and repeated training are deterministic.
- Run `git diff --check`.

## Execution Status
- Regenerated 15 main and four complete holdout datasets with event anchors.
- Fixed epoch-millisecond anchor comparison to use absolute tolerance; the
  previous relative `math.isclose` check collapsed sub-second event intervals.
- Regenerated main row count: `5,158`.
- Selected alpha changed from `1` to `100`.
- Main OOF macro XY RMSE changed from `10.007230 mm` to `4.886987 mm`.
- Complete holdout macro result changed:
  - zero-prediction XY RMSE: `11.945516 -> 4.533414 mm`
  - Ridge XY RMSE: `11.033113 -> 2.848173 mm`
  - improvement: `7.638% -> 37.174%`
- Phase-analysis final `0.5 s` Ridge RMSE changed from `40.304 mm` to
  `2.444 mm`.
- These corrected holdout values are retrospective because this holdout was
  used to diagnose the alignment defect.
