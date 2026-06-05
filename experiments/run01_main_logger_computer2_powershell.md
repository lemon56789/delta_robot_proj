# Run 01-pre Main Logger - Computer 2 PowerShell Guide

이 문서는 컴퓨터 2(Y)에서 Arduino serial을 열어 Run 01-pre main log를 저장하기 위한 실행 안내다.

## 1. 전달받을 파일
- `run01_main_logger.py`
- 이 안내 파일: `run01_main_logger_computer2_powershell.md`

두 파일을 같은 폴더에 둔다.

예:
```text
C:\delta_robot_run01\
  run01_main_logger.py
  run01_main_logger_computer2_powershell.md
```

## 2. 실행 전 확인
1. Arduino가 컴퓨터 2에 USB로 연결되어 있어야 한다.
2. Arduino IDE의 Serial Monitor를 닫는다.
   - Serial Monitor가 열려 있으면 Python이 COM port를 열 수 없다.
3. 장치 관리자에서 Arduino COM port를 확인한다.
   - 예: `COM3`, `COM4`.
4. PowerShell을 연다.
5. script가 있는 폴더로 이동한다.

```powershell
cd C:\delta_robot_run01
```

## 3. pyserial 설치
아래 명령으로 설치한다.

```powershell
python -m pip install pyserial
```

`python` 명령이 동작하지 않으면 아래를 사용한다.

```powershell
py -m pip install pyserial
```

## 4. Dry-run 확인
serial 연결 없이 CSV 형식만 확인한다.

```powershell
python .\run01_main_logger.py static_center_pre --run-id 2026-06-05_run01_pre_static_center_r01 --dry-run
```

정상 출력 예:
```text
main_csv=data\real\raw\main_2026-06-05_run01_pre_static_center_r01.csv
metadata_json=data\real\raw\main_2026-06-05_run01_pre_static_center_r01.json
serial_log=data\real\raw\serial_2026-06-05_run01_pre_static_center_r01.txt
row_count=...
theta_meas_source=command_echo_no_encoder
time_source=pc_elapsed_ms
```

## 5. 실제 static run 실행
`COM3`는 실제 Arduino port로 바꾼다.

```powershell
python .\run01_main_logger.py static_center_pre `
  --run-id 2026-06-05_run01_pre_static_center_r01 `
  --port COM3 `
  --output-csv .\main_2026-06-05_run01_pre_static_center_r01.csv `
  --metadata-json .\main_2026-06-05_run01_pre_static_center_r01.json `
  --serial-log .\serial_2026-06-05_run01_pre_static_center_r01.txt
```

## 6. Run 01-pre 나머지 실행
static run이 정상 저장된 뒤 실행한다.

### cross `±40 mm`
```powershell
python .\run01_main_logger.py cross_pm40_pre `
  --run-id 2026-06-05_run01_pre_cross_pm40_r01 `
  --port COM3 `
  --output-csv .\main_2026-06-05_run01_pre_cross_pm40_r01.csv `
  --metadata-json .\main_2026-06-05_run01_pre_cross_pm40_r01.json `
  --serial-log .\serial_2026-06-05_run01_pre_cross_pm40_r01.txt
```

### square `±40 mm`
```powershell
python .\run01_main_logger.py square_pm40_pre `
  --run-id 2026-06-05_run01_pre_square_pm40_r01 `
  --port COM3 `
  --output-csv .\main_2026-06-05_run01_pre_square_pm40_r01.csv `
  --metadata-json .\main_2026-06-05_run01_pre_square_pm40_r01.json `
  --serial-log .\serial_2026-06-05_run01_pre_square_pm40_r01.txt
```

## 7. 생성 파일 전달
각 run마다 아래 3개 파일을 컴퓨터 1(L)로 전달한다.

```text
main_<run_id>.csv
main_<run_id>.json
serial_<run_id>.txt
```

컴퓨터 1 repo에서는 main CSV를 아래 위치에 둔다.

```text
data/real/raw/main_<run_id>.csv
```

metadata JSON과 serial text log도 같은 run 근거로 보관한다.

## 8. 주의사항
- vision logger의 `run_id`와 main logger의 `run_id`가 정확히 같아야 한다.
- `theta*_meas`는 encoder 측정값이 아니다.
  - 현재 값은 `theta*_cmd`를 그대로 기록한 `command_echo_no_encoder`다.
- `time`은 Arduino `millis()`가 아니다.
  - 현재 값은 PC logger 기준 elapsed ms이며 `time_source=pc_elapsed_ms`로 기록된다.
- 이 logger의 목적은 Run 01-pre pipeline validation이다.
- 이 단계의 `error_z`는 pipeline 확인용 diagnostic으로만 사용하고, 외부 3D ground-truth 성능으로 해석하지 않는다.
- Arduino/controller에 position gain `1.25`를 적용한 경우 main metadata 또는 별도 run note에 반드시 기록한다.

## 9. 문제 발생 시
- `Access denied` 또는 port open 실패:
  - Arduino IDE Serial Monitor를 닫는다.
  - COM port 번호를 다시 확인한다.
- `No module named serial`:
  - `python -m pip install pyserial`을 실행한다.
- `python` 명령이 없음:
  - `py .\run01_main_logger.py ...` 형태로 실행한다.
