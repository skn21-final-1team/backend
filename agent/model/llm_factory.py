from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from agent.model.cumtom_exaone import MyCustomModel
from core.config import get_settings

settings = get_settings()


class LLMModel:
    """모델 이름에 따라 적절한 LLM 인스턴스를 생성하는 팩토리 클래스."""

    GPT_4O_MINI_CONFIG = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "api_key": settings.openai_api_key,
    }

    def get_llm(self, config: RunnableConfig) -> BaseChatModel:
        """RunnableConfig에서 모델 이름을 읽어 대응하는 LLM 인스턴스를 반환합니다.

        Args:
            config: LangGraph RunnableConfig. configurable.model_name으로 모델 선택.

        Returns:
            BaseChatModel: 선택된 LLM 인스턴스.
        """
        model_name: str = config.get("configurable", {}).get("model_name", "gpt-4o-mini")

        if model_name == "exaone":
            return MyCustomModel()
        return ChatOpenAI(**LLMModel.GPT_4O_MINI_CONFIG)


llm_factory = LLMModel()
