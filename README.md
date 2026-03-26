# Backend

웹 소스를 기반으로 AI가 질문에 답변하는 노트북 서비스의 백엔드입니다.
LangGraph 워크플로우로 구성된 RAG 파이프라인이 의도 분류, 벡터 검색, Reranking, 답변 생성을 오케스트레이션합니다.

**기술 스택**: FastAPI · LangGraph · PostgreSQL + pgvector · OpenAI · RunPod

---

## 시스템 아키텍처

```
Frontend (Next.js / Chrome Extension)
        │  HTTP / SSE
        ▼
┌──────────────────────────────────────────┐
│            FastAPI Backend               │
│                                          │
│  API Routes → Services → LangGraph       │
│                 Agent                    │
│                                          │
│  ┌──────────────────────────────────┐    │
│  │  RAG Agent (LangGraph)           │    │
│  │  classify → retrieve → generate  │    │
│  └──────────────────────────────────┘    │
└───────┬──────────────────────────────────┘
        │
        ├──────────────────┬──────────────────┐
        ▼                  ▼                  ▼
  PostgreSQL           RunPod API         OpenAI API
  + pgvector       ├─ Embedding (bge-m3)  (gpt-4o-mini)
  (벡터 저장소)    ├─ Reranker
                   └─ LLM (EXAONE)
```

---

## RAG 파이프라인

LangGraph 기반 상태 머신으로 구현되어 있으며, 사용자 질문의 성격에 따라 경로가 분기됩니다.

```
사용자 질문
    │
    ▼
[classify_intent]
    ├── casual  ──→ [casual_answer] ──────────────────────┐
    ├── simple  ──→ [retrieve_sources] ◀──[rewrite_query] │
    └── complex ──→ [decompose_query] ──→ [retrieve_sources]
                                               │
                                  ┌── 소스 없음 & 재시도 가능 ──→ [rewrite_query]
                                  └── 소스 있음 or 재시도 초과
                                               │
                                        [generate_answer] ──┐
                                                            │
                                                       [save_chat] → 반환
```

| 노드                 | 역할                                                       |
| -------------------- | ---------------------------------------------------------- |
| `classify_intent`  | 질문을 simple / complex / casual 로 분류 (LLM)             |
| `decompose_query`  | 복합 질문을 2~3개의 하위 질문으로 분해 (LLM)               |
| `retrieve_sources` | pgvector 벡터 검색 후 Reranker로 관련도 재정렬             |
| `rewrite_query`    | 검색 실패 시 질문을 재작성하여 재시도 (LLM, fallback 포함) |
| `generate_answer`  | 검색 소스 + 대화 이력을 컨텍스트로 답변 생성 (LLM)         |
| `save_chat`        | 질문과 답변을 DB에 저장                                    |

---

## 프로젝트 구조

```
backend/
├── agent/                  # LangGraph RAG 에이전트
│   ├── graph.py            # 워크플로우 정의
│   ├── state.py            # QAState 타입
│   ├── nodes/              # 각 처리 노드
│   ├── edges/              # 조건부 라우팅 로직
│   ├── model/              # LLM, Embedding, Reranker 인스턴스
│   └── prompts/            # 프롬프트 템플릿
├── api/
│   └── endpoints/          # chat, notebook, source, auth 등
├── services/               # 비즈니스 로직
├── crud/                   # DB 접근 계층
├── models/                 # SQLAlchemy 모델
├── schemas/                # Pydantic 요청/응답 스키마
├── core/                   # 설정, 인증, 로깅
├── db/                     # DB 엔진 및 세션
├── alembic/                # DB 마이그레이션
└── main.py                 # FastAPI 앱 진입점
```

---

## 환경변수

### 데이터베이스

| 변수                   | 설명                       | 필수 |
| ---------------------- | -------------------------- | :--: |
| `DATABASE_URL`       | PostgreSQL 동기 연결 URL   |  ✅  |
| `ASYNC_DATABASE_URL` | PostgreSQL 비동기 연결 URL |  ✅  |

### LLM & 모델

| 변수                     | 설명                                      | 필수 |
| ------------------------ | ----------------------------------------- | :--: |
| `OPENAI_API_KEY`       | OpenAI API 키                             |  ✅  |
| `RUNPOD_API_KEY`       | RunPod API 키                             |  ✅  |
| `EMBEDDING_MODEL_URL`  | Embedding 모델 엔드포인트 (RunPod)        |  ✅  |
| `RERANKER_MODEL_URL`   | Reranker 모델 엔드포인트 (RunPod)         |  ✅  |
| `CUSTOM_LLM_MODEL_URL` | Custom LLM 엔드포인트 (EXAONE 등, RunPod) |  ✅  |

### 인증

| 변수                     | 설명                       | 필수 |
| ------------------------ | -------------------------- | :--: |
| `SECRET_KEY`           | JWT 서명 시크릿 키         |  ✅  |
| `GOOGLE_CLIENT_ID`     | Google OAuth Client ID     |  ✅  |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret |  ✅  |

### 크롤링 & 기타

| 변수                     | 설명                         | 필수 |
| ------------------------ | ---------------------------- | :--: |
| `CHUNKING_CRAWL_URL`   | 크롤링 서버 URL              |  ✅  |
| `BACKEND_CORS_ORIGINS` | 허용할 CORS 출처 (JSON 배열) |  ✅  |

---

## 실행 방법

### 사전 요구사항

- Docker Desktop 실행
- PostgreSQL 컨테이너 실행
- Python 3.11 이상
- [uv](https://github.com/astral-sh/uv) 패키지 매니저

### 설치 및 실행

```bash
# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 값 입력

# 서버 실행
uvicorn main:app --reload
```

- 서버 시작 시 DB 테이블이 자동 생성됩니다.
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 개발 명령어

```bash
# 린팅 검사
ruff check .

# 포맷 검사
ruff format --check .

# DB 마이그레이션
alembic upgrade head
```
