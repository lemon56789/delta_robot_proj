# Plan

## Goal
Update project documents after Run 01-pre pipeline validation, processed dataset
generation, and the linear/Ridge baseline modeling decision.

## Files
- `docs/plans/2026-06-06_006_update_docs_after_run01_pre.md`
- `docs/roadmap.md`
- `docs/measured_data_structure.md`
- `docs/hardware_experiment_run_01_baseline_data_collection.md`
- `experiments/README.md`
- `data/README.md`
- `fulltext.md`
- `docs/daily_notes/2026-06-06.md`

## Changes
- Update current status snapshots from pre-run preparation to Run 00 passed and
  Run 01-pre pipeline validation completed.
- Record generated Run 01-pre processed artifacts and limitations.
- Clarify that `data/real/raw`, `data/real/derived`, `data/simulation/raw`,
  and `data/processed` paths are now active conventions.
- Add `experiments/run01_preprocess.py` usage to the experiments documentation.
- Update immediate priorities toward Run 01-main/holdout trajectory support,
  data collection, processed merge, and linear/Ridge training.

## Impact
- Documentation only.
- No data contract, folder structure, or code interface changes.
- Keeps `fulltext.md` aligned with current SoT documents and artifacts.

## Risk
- Run 01-pre artifacts are pipeline-validation outputs, not final training data;
  documents must not overstate their quality.
- Run 01-main/holdout logger trajectory support is still pending.

## Validation
- Check that documents consistently mention:
  - Run 01-pre pipeline validation completed
  - pre artifacts are not final training data
  - initial model is linear/Ridge
  - next task is Run 01-main/holdout trajectory support and data collection
