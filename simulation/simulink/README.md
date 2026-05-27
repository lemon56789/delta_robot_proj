# simulink

Simulink 관련 원본 모델과, 해당 모델이 같은 위치 기준으로 참조하는 보조 파일을 함께 보관하는 폴더입니다.

- `.slx`, `.mdl`, `.m`, `.mlx` 등 직접 관리하는 원본 파일을 둡니다.
- 상대경로 의존성이 있는 파일은 필요한 범위에서 같은 하위 폴더에 함께 둡니다.
- `slprj/`, autosave, cache, code generation 산출물은 포함하지 않습니다.
- 현재 기준 모델과 주요 파일 역할은 `model_notes.md`를 기준으로 확인합니다.
