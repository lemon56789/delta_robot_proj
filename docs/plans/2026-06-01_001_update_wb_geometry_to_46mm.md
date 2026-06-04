# Plan

## Goal
Update the project geometry source of truth from the previous nominal `wB = 24.051 mm` to the hardware-built `wB = 46.0 mm`.

This change aligns Python kinematics, Simscape initialization, and active project documentation with the actual motor/upper-arm joint radial position. The outer base/platform side lengths remain separate measured dimensions and are not used as `wB` or `uP`.

## Files
Planned files to modify:

- `kinematics/geometry.py`
- `kinematics/README.md`
- `simulation/simulink/init_delta_params.m`
- `docs/system_data_flow.md`
- `docs/ik_structure_note.md`
- `docs/hardware_experiment_base_config.md`
- `docs/roadmap.md`
- `docs/workspace_envelope.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-01.md`

Planned generated artifacts to either regenerate or explicitly mark as old-geometry artifacts:

- `data/fake_pipeline/*.csv`
- `data/fake_pipeline/*.json`
- `experiments/kinematics/*.csv`
- `experiments/kinematics/*.json`
- Simscape output files generated from the previous `wB = 24.051 mm` setup

## Changes
1. Change active Python nominal geometry:
   - Set `NOMINAL_DELTA_GEOMETRY.base_center_to_side_mm` from `24.051` to `46.0`.
   - Clarify that this field represents the base-center to motor/upper-arm joint reference distance, not the outer base side-derived distance.

2. Change active Simscape parameter:
   - Set `wB = 46.0e-3` in `simulation/simulink/init_delta_params.m`.
   - Keep units in meters for Simscape.

3. Update Source of Truth documentation:
   - Revise `wB` definition in `docs/system_data_flow.md`.
   - Clarify that outer base side length `199 mm` and platform side length `57.5 mm` are measured external dimensions, while `wB` and `uP` are the kinematic reference distances used by IK/FK.
   - Update `docs/hardware_experiment_base_config.md` wording so `wB = 46 mm` is not confused with the outer base side geometry.

4. Update active documentation references:
   - Replace current nominal `wB = 24.051 mm` references with `wB = 46.0 mm` in current status docs.
   - Keep historical plans and daily notes unchanged unless they are current active status documents.

5. Recompute derived artifacts after approval:
   - Re-run IK/FK validation with the new geometry.
   - Recompute workspace envelope values and update `docs/workspace_envelope.md`.
   - Regenerate fake pipeline data if those files are still treated as active samples.
   - Re-run Simscape export after `init_delta_params.m` is updated.

## Impact
- IK and FK formulas do not need structural changes because both already use `delta_offset = uP - wB`.
- Same target positions will produce different `theta*_cmd` values.
- Existing generated data and workspace summaries based on `wB = 24.051 mm` must not be mixed with new `wB = 46.0 mm` runs.
- Simscape and Python outputs must be regenerated from the same geometry before comparing `sim_*`, `theta_*`, or `error_*`.
- This is a geometry parameter contract change and affects downstream simulation, workspace analysis, controller commands, and generated datasets.

## Risk
- If any document still defines `wB` as the outer base side-derived distance, future calculations may mix physical dimensions and kinematic reference dimensions.
- Existing fake pipeline CSVs may appear valid because target positions remain reachable, but their `theta*_cmd`, `sim_*`, and `error_*` fields are old-geometry values.
- Workspace envelope and installation-height guidance will change numerically after recomputation.
- Simscape model blocks may contain cached or manually duplicated geometry values outside `init_delta_params.m`; this must be checked during validation.

## Validation
1. Run Python IK/FK roundtrip:
   - `python kinematics/validate_roundtrip.py`

2. Run representative target checks with `wB = 46.0 mm`:
   - centerline targets such as `(0, 0, -200)`, `(0, 0, -220)`, `(0, 0, -250)`
   - off-center targets such as `(20, 0, -220)`, `(0, 20, -220)`, `(30, 30, -240)`

3. Re-run workspace sweep:
   - Use the same theta range policy `-45 deg <= theta_i <= 90 deg`.
   - Save new CSV/JSON with filenames that indicate the `wB = 46.0 mm` geometry.

4. Regenerate fake pipeline data if it remains active:
   - Confirm all targets are reachable.
   - Confirm regenerated `theta*_cmd` values use the new geometry.

5. Re-run Simscape initialization/export:
   - Confirm `init_delta_params.m` uses `wB = 46.0e-3`.
   - Confirm Simscape output is generated after parameter reload.

6. Search for stale active references:
   - `rg -n "24\\.051|wB = 24|wB=24|base_center_to_side_mm=24" -g '!venv/**'`

7. Record all changes in `docs/daily_notes/2026-06-01.md`.
