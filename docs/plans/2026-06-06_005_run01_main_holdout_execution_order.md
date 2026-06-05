# Plan

## Goal
Record the Run 01-main and Run 01-holdout execution order in today's daily note
so it can be used for immediate reporting.

## Files
- `docs/plans/2026-06-06_005_run01_main_holdout_execution_order.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Summarize which existing scripts are reused.
- List the next execution order from trajectory support through data collection,
  Simscape export, processed merge generation, validation, Ridge training, and
  holdout evaluation.
- Clarify that Run 01-holdout must not be used for fitting or tuning.

## Impact
- Documentation only.
- No CSV contract, code interface, or data flow change.

## Risk
- The current `run01_main_logger.py` still needs main/holdout trajectory support
  before the listed run commands can be executed.

## Validation
- Confirm the daily note includes a concise action sequence suitable for team
  reporting.
