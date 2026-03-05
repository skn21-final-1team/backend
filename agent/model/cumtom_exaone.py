from typing import Any

import httpx
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, message_to_dict
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable


class MyCustomModel(BaseChatModel):
    """외부 프라이빗 추론 API와 연동하는 커스텀 LangChain 채팅 모델."""

    endpoint_url: str = "https://otojmh2s7brdai-8080.proxy.runpod.net/api/inference/chat"

    @property
    def _llm_type(self) -> str:
        return "custom_private_model"

    def with_structured_output(
        self,
        schema: dict | type,
        *,
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable:
        _ = include_raw, kwargs
        parser = PydanticOutputParser(pydantic_object=schema) if isinstance(schema, type) else JsonOutputParser()
        return self | parser

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """동기 방식으로 외부 모델 API를 호출하여 결과를 LangChain 규격에 맞게 반환합니다.

        Args:
            messages: 사용자 및 시스템 메시지 이력.
            stop: 생성 중단 토큰 리스트.
            run_manager: 콜백 런 매니저.
            kwargs: 기타 추가 파라미터.

        Returns:
            ChatResult: 생성된 답변을 포함한 LangChain 규격 결괏값 객체.
        """
        content = self._call_api(messages)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=content))])

    def _call_api(self, messages: list[BaseMessage]) -> str:
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.endpoint_url,
                    json={"input": [message_to_dict(m) for m in messages]},
                )

                print("ChatResult", response.json())
                data: dict[str, Any] = response.json().get("data", {})
                return str(data.get("content", ""))
        except Exception as e:
            print(f"Model generation error: {e}")
            return ""
