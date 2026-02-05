---
trigger: always_on
---

# Backend Skills & Tools

## 1. FastAPI Execution
- 환경 변수는 `core/config.py`의 Pydantic Settings를 통해서만 접근합니다.

## 2. Pydantic & Type Hinting
- `backend-code-style.md`의 타입 규칙에 따라, 모든 스키마는 `schemas/` 폴더 내에 정의합니다.
- `Optional` 대신 Python 3.10+ 스타일인 `| None`을 사용합니다.


## 3. Error Handling
- 모든 비즈니스 예외는 `FastAPI.HTTPException`을 사용하여 적절한 상태 코드와 함께 반환합니다.

## 4. Pyproject
- 모든 의존성 관리는 pyproject.toml을 기준으로 하며, 패키지 추가 시 uv add를 사용한다.
- 설치 후에는 항상 uv.lock 파일이 업데이트되었는지 확인한다.