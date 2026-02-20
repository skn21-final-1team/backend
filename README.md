# Backend

## 실행 전 필수 사항

1. **PostgreSQL 컨테이너** 실행
2. `.env` 파일에 `DATABASE_URL` 설정 (본인 환경에 맞게)

## 초기 세팅 (pull 이후)

```bash
# 의존성 설치
uv sync

# Playwright 브라우저 설치 (최초 1회만)
uv run playwright install chromium
```

## 서버 실행

```bash
uvicorn main:app --reload
```

- 서버 시작 시 DB 테이블이 자동 생성됩니다.

## ruff 린팅 및 포맷팅 확인

```bash
ruff check .
ruff format --check .
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check API 호출: GET http://localhost:8000/api/v1/health
