# Plan

## Goal
Record the optional 24-run Run 02 trajectory candidate so it can be reused
later without relying on conversation history.

## Files
- `docs/plans/2026-06-06_018_document_run02_24_run_trajectory_candidate.md`
- `docs/hardware_experiment_run_02_corrected_comparison.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
1. Add an optional Run 02 candidate consisting of four trajectories:
   - cross `+/-30 mm`, existing holdout order unchanged;
   - reverse grid 3x3 `+/-40 mm`, exact reverse of the existing grid order;
   - diamond `+/-35 mm`, starting at `(35, 0)` and moving
     counterclockwise;
   - circle `r=40 mm`, existing counterclockwise direction unchanged.
2. Define every waypoint explicitly:
   - cross:
     home -> `(30,0)` -> home -> `(-30,0)` -> home -> `(0,30)` ->
     home -> `(0,-30)` -> home
   - reverse grid:
     home -> `(40,40)` -> `(0,40)` -> `(-40,40)` -> `(40,0)` ->
     `(0,0)` -> `(-40,0)` -> `(40,-40)` -> `(0,-40)` ->
     `(-40,-40)` -> home
   - diamond:
     home -> `(35,0)` -> `(0,35)` -> `(-35,0)` -> `(0,-35)` ->
     `(35,0)` -> home
   - circle:
     home -> `(40,0)` -> counterclockwise radius-40 circle -> home
3. Define the experiment matrix as correction OFF/ON, three repetitions each:
   four trajectories x two correction states x three repetitions = 24 runs.
4. Mark this matrix as a documented candidate, not yet the final Run 02
   execution decision.

## Impact
- Documentation only.
- Does not add logger trajectory implementations or generate Simscape files.
- Does not change the correction engine, model, Arduino protocol, or CSV
  contract.

## Risk
- The candidate may be replaced by a time-reduced or holdout-reuse design.
- Reverse-grid transitions include long row-to-row diagonal movements, matching
  the reverse of the existing grid definition rather than a serpentine path.
- Duration, hold time, circle point count, and OFF/ON execution ordering remain
  to be fixed before implementation.

## Validation
- Confirm all four waypoint definitions are unambiguous.
- Confirm reverse grid is the exact reverse of the existing grid waypoint list.
- Confirm diamond order is counterclockwise in `base_frame`.
- Confirm the run count is `4 x 2 x 3 = 24`.
- Confirm the document labels the matrix as optional/not finalized.
- Run `git diff --check`.

## Execution Status
- Added the optional 24-run matrix to the Run 02 protocol.
- Recorded explicit waypoint sequences for cross, reverse grid, diamond, and
  circle.
- Confirmed the matrix is four trajectories x OFF/ON x three repetitions =
  24 runs.
- Marked the matrix as a candidate, not a final execution decision.
- Left duration, hold time, circle discretization, OFF/ON ordering, and run
  naming for the later implementation plan.
