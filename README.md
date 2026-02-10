# Backend

## 실행 전 필수 사항

1. **Docker Desktop** 실행
2. **PostgreSQL 컨테이너** 실행 (Docker Desktop에서 켜기)
3. `.env` 파일에 `DATABASE_URL` 설정 (본인 환경에 맞게)

## 초기 세팅 (pull 이후)

```bash
uv sync
```

## 서버 실행

```bash
uvicorn main:app --reload
```

- 서버 시작 시 DB 테이블이 자동 생성됩니다.
- Firecrawl 컨테이너는 크롤링 요청 시 자동으로 시작/종료됩니다.

## ruff 린팅 및 포맷팅 확인

```bash
ruff check .
ruff format --check .
```

## API 문서

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check API 호출: GET http://localhost:8000/api/v1/health
