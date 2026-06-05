# data

실험 및 시뮬레이션에서 수집한 원본/가공 데이터를 관리하는 폴더입니다.

현재 포함 예시:
- `data/fake_pipeline/`: fake pipeline으로 생성한 CSV/JSON 샘플 결과 저장 경로
- `data/real/raw/`: real main logger CSV/JSON/TXT 저장 경로
- `data/real/derived/`: `theta*_meas` 기반 angle-derived measured position CSV 저장 경로
- `data/vision/raw/`: vision raw ground-truth CSV 저장 경로
- `data/vision/calibration/`: vision calibration/homography artifact 저장 경로
- `data/simulation/raw/`: Simscape raw output CSV 저장 경로
- `data/processed/`: 학습/평가용 processed merged dataset 저장 경로

Run 01 processed dataset naming:
- `data/real/raw/main_<run_id>.csv`
- `data/vision/raw/vision_<run_id>.csv`
- `data/simulation/raw/simscape_<run_id>.csv`
- `data/real/derived/measured_position_<run_id>.csv`
- `data/processed/merged_<run_id>.csv`

`data/processed/merged_<run_id>.csv`는 `docs/system_data_flow.md`와 `docs/measured_data_structure.md`의 fixed 16-column contract를 따른다. Run 01-pre 산출물은 pipeline validation용이며 최종 training dataset으로 채택하지 않는다.
