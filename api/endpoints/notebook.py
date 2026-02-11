from fastapi import APIRouter, Query

from db.database import DbSession
from schemas.notebook import NotebookRequest, NotebookResponse
from schemas.response import BaseResponse
from services.notebook import notebook_service

router = APIRouter()


@router.post(
    "/",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}, 401: {"model": BaseResponse}},
)
def create_notebook(req: NotebookRequest, db: DbSession, user_id: int = Query(...)) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.create_notebook(user_id, req.title, db))


@router.get(
    "/",
    response_model=BaseResponse[list[NotebookResponse]],
    responses={404: {"model": BaseResponse}},
)
def get_notebooks(db: DbSession, user_id: int = Query(...)) -> BaseResponse[list[NotebookResponse]]:
    return BaseResponse.ok(notebook_service.get_notebooks_by_user(user_id, db))


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
def update_notebook(notebook_id: int, req: NotebookRequest, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.update_notebook_title(notebook_id, req.title, db))


@router.delete(
    "/{notebook_id}",
    response_model=BaseResponse[NotebookResponse],
    responses={404: {"model": BaseResponse}},
)
def delete_notebook(notebook_id: int, db: DbSession) -> BaseResponse[NotebookResponse]:
    return BaseResponse.ok(notebook_service.delete_notebook(notebook_id, db))
