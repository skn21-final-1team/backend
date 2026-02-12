from fastapi import APIRouter

from core.security import CurrentUser
from db.database import DbSession
from schemas.chat import ChatRequest, ChatResponse
from schemas.response import BaseResponse
from services.chat import chat_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[ChatResponse],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def create_chat(req: ChatRequest, db: DbSession, user: CurrentUser) -> BaseResponse[ChatResponse]:
    return BaseResponse.ok(chat_service.create_chat(req.notebook_id, req.role, req.message, db))


@router.get(
    "/{chat_id}",
    response_model=BaseResponse[ChatResponse],
    responses={404: {"model": BaseResponse}},
)
def get_chat(chat_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[ChatResponse]:
    return BaseResponse.ok(chat_service.get_chat(chat_id, db))


@router.get(
    "/notebook/{notebook_id}",
    response_model=BaseResponse[list[ChatResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_chats_by_notebook(notebook_id: int, db: DbSession, user: CurrentUser) -> BaseResponse[list[ChatResponse]]:
    return BaseResponse.ok(chat_service.get_chats_by_notebook(notebook_id, db))