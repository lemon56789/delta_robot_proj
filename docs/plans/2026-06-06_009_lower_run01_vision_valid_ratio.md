# Plan

## Goal
Lower the Run 01 vision valid-row acceptance threshold from `95%` to `90%`
without encouraging longer static holds that would bias the training dataset.

## Files
- `docs/plans/2026-06-06_009_lower_run01_vision_valid_ratio.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Set the Run 01-pre/main/holdout minimum vision valid-row ratio to `>= 90%`.
- Keep the continuous marker-loss limit below `1 s`.
- Add trajectory coverage conditions so a run is rejected when marker loss is
  concentrated at a corner, direction, or continuous circle segment.
- Clarify that increasing static hold time only to improve the ratio is not an
  acceptance strategy because it can bias the dataset toward static rows.
- Update the recorded Run 01-pre interpretation under the new threshold.

## Impact
- Experiment acceptance policy change only.
- No CSV format, logger interface, data-flow, or model interface change.

## Risk
- A ratio-only check can accept poorly distributed data, so segment coverage
  and continuous-loss checks must be applied together with the `90%` threshold.

## Validation
- Confirm the Run 01 protocol consistently states `>= 90%`.
- Confirm the `1 s` marker-loss and trajectory-coverage rules remain explicit.
- Run `git diff --check`.
