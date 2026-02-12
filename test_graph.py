from agent.graph import graph

while True:
    question = input("\n질문을 입력하세요 (종료: q): ")
    if question.strip().lower() == "q":
        break

    result = graph.invoke(
        {
            "notebook_id": 1,
            "question": question,
            "chat_history": [],
        }
    )
    print(f"\n답변: {result['answer']}")
