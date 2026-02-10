---
trigger: always_on
---

# 폴더구조

agent/ # ✅ LangGraph 전용 최상위 디렉토리
├── __init__.py
├── graph.py          # StateGraph 정의 및 compile
├── state.py          # TypedDict 기반 State 정의
├── nodes/
│   └── __init__.py
├── edges/
│   └── __init__.py
├── tools/
│   └── __init__.py
└── prompts/
    └── __init__.py

# 각 하위 디렉토리의 역할
agent/graph.py
 - LangGraph의 핵심인 StateGraph를 정의하고 노드/엣지를 연결한 뒤 compile()하는 곳입니다. 그래프의 전체 흐름을 한눈에 파악할 수 있습니다.

agent/state.py
- TypedDict 기반의 State 스키마를 정의합니다. 그래프를 통해 흐르는 데이터의 타입을 명확하게 관리합니다.

agent/nodes/
 - 그래프의 각 노드(step) 를 개별 파일로 분리합니다. 각 노드는 State → State 시그니처의 함수로, 단일 책임 원칙을 지킵니다.

agent/edges/
 - conditional_edge에 사용하는 분기 조건 함수를 모아둡니다. 의도 분류 결과에 따라 다른 노드로 라우팅하는 등의 로직입니다.

agent/tools/
 - LLM Agent가 호출할 수 있는 Tool을 정의합니다. LangChain의 @tool 데코레이터를 사용하는 함수들이 위치합니다.

agent/prompts/
 - 프롬프트 템플릿을 관리합니다. 노드 코드에 프롬프트가 하드코딩되는 것을 방지하고, 프롬프트만 독립적으로 수정할 수 있게 합니다.

