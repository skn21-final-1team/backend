from typing import Annotated

from fastapi import APIRouter, Query, Request

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.notebook import NotebookRequest, NotebookResponse, NotebookSortType, NotebookUpdateBody
from schemas.source import SourceResponse, SourceUpdateBatchRequest
from schemas.response import BaseResponse
from services.notebook import notebook_service

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def create_notebook(req: Request, body: NotebookRequest, db: DbSession) -> BaseResponse[NotebookResponse]:
    user = get_current_user(req)
    return BaseResponse.ok(notebook_service.create_notebook(user.id, body.title, db))


@router.get(
    "/list",
    response_model=BaseResponse[list[NotebookResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_notebooks(
    request: Request,
    db: DbSession,
    sort: Annotated[
        NotebookSortType,
        Query(
            description="정렬 방식 (recent | created_at | name)",
        ),
    ] = NotebookSortType.RECENT_CREATED,
) -> BaseResponse[list[NotebookResponse]]:
    """현재 사용자 노트북 목록을 정렬 기준에 맞춰 반환한다."""
    user = get_current_user(request)
    return BaseResponse.ok(notebook_service.get_notebooks_by_user(user.id, db, sort))


@router.get(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def get_notebook(notebook_id: int, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.get_notebook(notebook_id, db))


@router.patch(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def update_notebook(notebook_id: int, body: NotebookUpdateBody, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.update_notebook(notebook_id, body, db))


@router.delete(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_notebook(notebook_id: int, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.delete_notebook(notebook_id, db))


@router.patch(
    "/{notebook_id}/sources/active",
    response_model=BaseResponse[list[SourceResponse]],
    responses={404: {"model": BaseResponse}},
)
def active_all_sources(
    notebook_id: int, body: SourceUpdateBatchRequest, db: DbSession
) -> BaseResponse[list[SourceResponse]]:
    """주어진 notebook ID에 속한 모든 소스의 활성화 상태를 일괄 변경합니다."""
    return BaseResponse.ok(notebook_service.active_all_sources(notebook_id, body, db))
