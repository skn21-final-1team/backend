# Backend

```
source .venv/bin/activate
```
## 서버 실행
```bash
uvicorn main:app --reload
```

## ruff 린팅 및 포맷팅 확인
```bash
ruff check .
ruff format --check .
```

Swagger UI 접속: http://localhost:8000/docs  
ReDoc 접속: http://localhost:8000/redoc  
Health check API 호출: GET http://localhost:8000/api/v1/health
