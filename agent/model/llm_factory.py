from typing import Literal

from langchain_openai import ChatOpenAI

from core.config import get_settings

settings = get_settings()


class LLMModel:
    GPT_4O_MINI_CONFIG = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "api_key": settings.openai_api_key,
    }

    EXAONE_CONFIG = {
        "model": "exaone",
        "temperature": 0,
        "api_key": settings.openai_api_key,
    }

    def get_llm(self, name: Literal["gpt-4o-mini", "exaone"] = "gpt-4o-mini") -> ChatOpenAI:
        if name == "gpt-4o-mini":
            return ChatOpenAI(LLMModel.GPT_4O_MINI_CONFIG)
        if name == "exaone":
            return ChatOpenAI(LLMModel.EXAONE_CONFIG)
        return ChatOpenAI(LLMModel.GPT_4O_MINI_CONFIG)


llm_factory = LLMModel()
