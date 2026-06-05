# Plan

## Goal
Update team role documentation to reflect actual Run 00/Run 01-pre work:
S/T/N performed hardware fabrication and assembly work, S also acted as team
leader, N handled custom profile ordering requests, and Y handled circuit/wiring
work. Keep earlier dynamics/vibration/stress-analysis roles as planning-stage
responsibilities rather than deleting them.

## Files
- `docs/plans/2026-06-06_007_update_team_roles_after_hardware_build.md`
- `README.md`
- `docs/member_profiles/README.md`
- `docs/member_profiles/S.md`
- `docs/member_profiles/T.md`
- `docs/member_profiles/N.md`
- `docs/member_profiles/Y.md`
- `docs/system_data_flow.md`
- `docs/hardware_experiment_base_config.md`
- `docs/hardware_experiment_run_00_commissioning.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Use the concise role table in `README.md`.
- Use the fuller role description in member profiles and owner mapping:
  - S: team lead, hardware fabrication/assembly, experiment support,
    planning-stage dynamics/vibration analysis
  - L: system integration, virtual sensing, data processing/training,
    vision-based measurement
  - Y: Arduino control, circuit/wiring, power/drive connection
  - T: hardware fabrication/assembly, mechanical design, fabrication dimension
    review
  - N: hardware fabrication/assembly, custom profile ordering request,
    planning-stage structural/stress analysis
- Update hardware/common experiment owner references to include S/T/N for
  hardware build and Y for circuit/power/control wiring.
- Update Run 00/Run 01 responsible-member notes where they still had generic
  TBD role entries.

## Impact
- Documentation only.
- No technical interface or data contract changes.

## Risk
- Overstating analysis work would be misleading, so dynamics/vibration/stress
  analysis must remain clearly marked as planning-stage scope.

## Validation
- Search role-related docs for old role-only wording and confirm updated role
  wording is consistent.
