from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from core.config import get_settings

settings = get_settings()


class LLMModel:
    """모델 이름에 따라 적절한 LLM 인스턴스를 생성하는 팩토리 클래스."""

    GPT_4O_MINI_CONFIG = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "api_key": settings.openai_api_key,
    }

    EXAONE_CONFIG = {
        "model": "LGAI-EXAONE/EXAONE-4.0-32B-FP8",
        "base_url": f"{settings.custom_llm_url}/openai/v1",
        "temperature": 0,
        "api_key": settings.runpod_api_key,
    }

    # structured output(function calling)을 지원하는 모델
    _STRUCTURED_OUTPUT_MODELS = {"gpt-4o-mini"}

    def get_llm(self, config: RunnableConfig) -> BaseChatModel:
        """RunnableConfig에서 모델 이름을 읽어 대응하는 LLM 인스턴스를 반환합니다."""
        model_name: str = config.get("configurable", {}).get("model_name", "gpt-4o-mini")

        if model_name == "exaone":
            return ChatOpenAI(**LLMModel.EXAONE_CONFIG)
        return ChatOpenAI(**LLMModel.GPT_4O_MINI_CONFIG)

    def supports_structured_output(self, config: RunnableConfig) -> bool:
        """현재 모델이 with_structured_output(function calling)을 지원하는지 반환합니다."""
        model_name: str = config.get("configurable", {}).get("model_name", "gpt-4o-mini")
        return model_name in self._STRUCTURED_OUTPUT_MODELS


llm_factory = LLMModel()
