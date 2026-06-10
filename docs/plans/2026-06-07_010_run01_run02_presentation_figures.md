# Plan

## Goal
기존 Run 01/02 결과 artifact만 사용해 PPT에 바로 삽입할 수 있는 발표용
PNG/SVG 그래프를 재현 가능하게 생성한다.

## Files
- `docs/plans/2026-06-07_010_run01_run02_presentation_figures.md`
- `experiments/generate_presentation_figures.py`
- `experiments/figures/run02_rmse_by_trajectory.png`
- `experiments/figures/run02_rmse_by_trajectory.svg`
- `experiments/figures/run02_improvement_by_trajectory.png`
- `experiments/figures/run02_improvement_by_trajectory.svg`
- `experiments/figures/run02_absolute_vs_home_normalized.png`
- `experiments/figures/run02_absolute_vs_home_normalized.svg`
- `experiments/figures/run02_circle_error_decomposition.png`
- `experiments/figures/run02_circle_error_decomposition.svg`
- `experiments/figures/run02_actuator_command_change_rate.png`
- `experiments/figures/run02_actuator_command_change_rate.svg`
- `experiments/figures/run01_holdout_rmse_by_trajectory.png`
- `experiments/figures/run01_holdout_rmse_by_trajectory.svg`
- `experiments/figures/run01_expected_improvement_by_trajectory.png`
- `experiments/figures/run01_expected_improvement_by_trajectory.svg`
- `docs/daily_notes/2026-06-07.md`

## Changes
- Run 02 official absolute OFF/ON RMSE grouped bar를 생성한다.
- Run 02 trajectory별 absolute improvement bar와 absolute 대
  home-normalized improvement grouped bar를 생성한다.
- Circle radial/tangential RMSE와 phase lag를 단위별 두 panel로
  분리해 한 figure에 요약한다.
- Trajectory별 실제 integer servo command 변화율을 bar로 생성한다.
- Run 01 complete holdout zero-prediction 대 Ridge residual RMSE와
  trajectory별 예상 감소율을 별도 figure로 생성한다.
- 모든 figure는 16:9 canvas, 값 label, 범례, 0% 기준선과 발표용 색상을
  사용하고 PNG와 SVG를 함께 저장한다.
- 현재 환경에 plotting package가 없으므로 Python 표준 라이브러리만
  사용하는 최소 SVG/PNG renderer를 구현한다.

## Impact
- 분석 시각화 코드와 생성 figure만 추가한다.
- 기존 Run 01/02 JSON/CSV, 모델, raw/processed 데이터, 데이터 contract,
  제어 코드와 시스템 인터페이스는 변경하지 않는다.

## Risk
- 자체 renderer는 범용 plotting library보다 기능이 제한적이므로 이번
  발표 figure에 필요한 bar, axis, label, legend에 범위를 한정한다.
- SVG text rendering은 PPT와 OS font fallback에 따라 모양이 달라질 수
  있으므로 PNG도 함께 제공한다.
- Run 01 예상 감소율은 offline estimator residual이며 실제 hardware
  correction 결과로 오해하지 않도록 subtitle에 명시한다.

## Validation
- 스크립트를 실행해 7개 base figure의 PNG/SVG 총 14개 파일을 생성한다.
- PNG signature, width, height와 SVG root/viewBox를 확인한다.
- Run 02 수치가 reanalysis JSON과, Run 01 수치가 holdout JSON과
  일치하는지 스크립트 내부에서 검증한다.
- 모든 figure에 요구한 trajectory와 value label이 포함되는지 확인한다.
- 원본 JSON/CSV와 processed 데이터가 변경되지 않았는지 확인한다.
