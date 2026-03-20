from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from core.config import get_settings

settings = get_settings()

DEFAULT_LLM_MODEL_NAME = "gpt-4o-mini"


class LLMModel:
    """모델 이름에 따라 적절한 LLM 인스턴스를 생성하는 팩토리 클래스."""

    OPENAI_MODEL_CONFIGS: dict[str, dict[str, object]] = {
        "gpt-4o-mini": {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "api_key": settings.openai_api_key,
        },
        "gpt-5.4-mini": {
            "model": "gpt-5.4-mini",
            "temperature": 0,
            "api_key": settings.openai_api_key,
        },
    }

    EXAONE_CONFIG = {
        "model": "LGAI-EXAONE/EXAONE-4.0-32B-FP8",
        "base_url": f"{settings.custom_llm_url}/openai/v1",
        "temperature": 0,
        "api_key": settings.runpod_api_key,
    }

    def get_llm(self, config: RunnableConfig) -> BaseChatModel:
        """RunnableConfig에서 모델 이름을 읽어 대응하는 LLM 인스턴스를 반환합니다.

        Args:
            config: LangGraph RunnableConfig. configurable.model_name으로 모델 선택.

        Returns:
            BaseChatModel: 선택된 LLM 인스턴스.
        """
        model_name = config.get("configurable", {}).get("model_name", DEFAULT_LLM_MODEL_NAME)

        if model_name == "exaone":
            return ChatOpenAI(**LLMModel.EXAONE_CONFIG)
        return ChatOpenAI(
            **LLMModel.OPENAI_MODEL_CONFIGS.get(
                model_name,
                LLMModel.OPENAI_MODEL_CONFIGS[DEFAULT_LLM_MODEL_NAME],
            )
        )


llm_factory = LLMModel()
