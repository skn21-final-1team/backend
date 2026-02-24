from fastapi import APIRouter, Request

from core.auth_guard import get_current_user
from db.database import DbSession
from schemas.notebook import NotebookDeleteRequest, NotebookRequest, NotebookResponse, NotebookUpdateRequest
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
def get_notebooks(request: Request, db: DbSession) -> BaseResponse[list[NotebookResponse]]:
    user = get_current_user(request)
    return BaseResponse.ok(notebook_service.get_notebooks_by_user(user.id, db))


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
def update_notebook(req: NotebookUpdateRequest, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.update_notebook_title(req.notebook_id, req.title, db))


@router.delete(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_notebook(body: NotebookDeleteRequest, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.delete_notebook(body.notebook_id, db))
