---
trigger: always_on
---

# 폴더구조

├── main.py              # 애플리케이션 진입점 (FastAPI 인스턴스 생성)
├── api/                   # API 라우트 레이어
│   └── route.py          # 라우터들을 하나로 묶어주는 곳
│   └── endpoints/       # 실제 엔드포인트 구현 (users.py, items.py 등)
├── core/                # 프로젝트 전반의 설정
│   ├── config.py        # 환경변수(pydantic-settings) 및 설정
│   └── security.py      # JWT, 인증 관련 로직
├── crud/                # Create, Read, Update, Delete (DB 조작 로직)
├── models/              # DB 테이블 정의 (SQLAlchemy, Tortoise 등)
├── schemas/             # DTO (Pydantic 모델)
├── db/                  # DB 연결 설정 및 세션 관리
├── services/            # 비즈니스 로직
├── .env                     # 환경변수 파일
├── pyproject.toml         # 의존성 관리


# 코드 컨벤션
불필요한 주석은 사용하지 마세요.
단일 책임원칙을 우선으로 고려하여 개발합니다.
OOP를 지향하며 개발하세요.
클린코드를 지향하며 개발하세요.
depth가 깊게 코딩하지 마세요. 깊이는 최소한으로 합니다.
코드의 결합도를 최소한으로 작업합니다.
타입 힌팅을 무시하거나 any타입을 사용하지 마세요. 타입은 꼭 작성합니다.
타입을 억지로 맞추기위해 주석으로 숨기지 마세요.
타입을 반드시 맞춰서 생성하세요