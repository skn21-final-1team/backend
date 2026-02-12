from langchain_openai import ChatOpenAI

from core.config import get_settings

settings = get_settings()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=settings.openai_api_key,
)
